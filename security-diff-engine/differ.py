#!/usr/bin/env python3
"""Diff-aware security policy scanner for Python, shell, Terraform, and Ansible."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shlex
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SEVERITIES = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
HUNK = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")
SENSITIVE_PATH = re.compile(r"(^|/)(?:\.env(?:\.[^/]+)?|(?:id_rsa|id_ed25519)(?:\.pub)?|[^/]+\.(?:pem|key|p12)|secrets?\.json|credentials)$", re.I)
BINARY_EXTENSIONS = {
    ".7z": "7-zip archive", ".a": "static library", ".apk": "Android package", ".appimage": "AppImage package", ".avro": "Avro data", ".bin": "binary data", ".container": "container image",
    ".bz2": "bzip2 archive", ".cab": "Windows cabinet package", ".class": "Java class", ".deb": "Debian package", ".dmg": "Apple disk image", ".dll": "Windows executable", ".dylib": "Mach-O library",
    ".docker": "container image", ".exe": "Windows executable", ".flac": "FLAC audio", ".gif": "GIF image", ".gz": "gzip archive", ".iso": "ISO disk image",
    ".h5": "HDF5 data", ".hdf5": "HDF5 data", ".ico": "icon image", ".jar": "Java archive",
    ".jpeg": "JPEG image", ".jpg": "JPEG image", ".mkv": "Matroska media", ".mp3": "MP3 audio",
    ".mp4": "MP4 media", ".msi": "Windows installer", ".o": "object file", ".ogg": "Ogg media", ".pkg": "operating system package",
    ".oci": "container image", ".orc": "ORC data", ".parquet": "Parquet data", ".pdf": "PDF document", ".pkl": "Python pickle",
    ".png": "PNG image", ".rar": "RAR archive", ".rpm": "RPM package", ".so": "ELF library", ".sqlite": "SQLite database",
    ".tar": "tar archive", ".tif": "TIFF image", ".tiff": "TIFF image", ".wasm": "WebAssembly module",
    ".wav": "WAV audio", ".webp": "WebP image", ".xz": "XZ archive", ".zip": "ZIP archive", ".zst": "Zstandard archive",
}
MAX_EXACT_BINARY_DIFF = 2 * 1024 * 1024
BINARY_SAMPLE_BYTES = 64 * 1024
TOOL_VERSION = "1.0.0"

@dataclass(frozen=True)
class Rule:
    id: str
    title: str
    description: str
    severity: str
    pattern: re.Pattern[str]
    file_types: tuple[str, ...]
    remediation: str
    kind: str = "vulnerability"

@dataclass(frozen=True)
class DiffLine:
    path: str
    number: int
    text: str

@dataclass(frozen=True)
class Finding:
    rule_id: str
    title: str
    severity: str
    category: str
    description: str
    remediation: str
    path: str
    line: int
    evidence: str

@dataclass(frozen=True)
class BinaryChange:
    path: str
    status: str
    format: str
    executable: bool
    old_size: int | None
    new_size: int | None
    old_sha256: str | None
    new_sha256: str | None
    diff_method: str
    changed_old_bytes: int | None
    changed_new_bytes: int | None
    ranges: list[dict[str, int]]

@dataclass(frozen=True)
class Blob:
    """Bounded binary inspection data; content is retained only when it is safe to diff."""
    size: int
    sha256: str
    sample: bytes
    content: bytes | None

def file_type(path: str) -> str:
    suffix = Path(path).suffix.lower()
    if suffix == ".py": return "python"
    if suffix in {".sh", ".bash", ".zsh", ".ksh"} or Path(path).name in {"bashrc", "profile"}: return "shell"
    if suffix in {".tf", ".tfvars"}: return "terraform"
    if suffix in {".yaml", ".yml"}:
        lowered = path.lower()
        return "ansible" if any(part in lowered for part in ("playbook", "roles/", "tasks/", "handlers/", "ansible")) else "yaml"
    return "generic"

class SecurityDiffer:
    def __init__(self, repo_path: str, rules_path: str | None = None):
        self.repo_path = Path(repo_path).resolve()
        self.rules_path = Path(rules_path or Path(__file__).with_name("security_rules.json")).resolve()
        self.rules = self.load_rules(str(self.rules_path))
        self.policy_sha256 = hashlib.sha256(self.rules_path.read_bytes()).hexdigest()

    @staticmethod
    def load_rules(path: str) -> list[Rule]:
        try:
            source = json.loads(Path(path).read_text(encoding="utf-8"))["rules"]
            result = []
            for item in source:
                severity = item["severity"].lower()
                if severity not in SEVERITIES: raise ValueError("invalid severity %r" % severity)
                result.append(Rule(
                    item["id"], item["title"], item["description"], severity,
                    re.compile(item["pattern"], re.IGNORECASE),
                    tuple(item.get("file_types", ["generic"])), item["remediation"],
                    item.get("kind", "vulnerability"),
                ))
            return result
        except (OSError, KeyError, TypeError, ValueError, re.error, json.JSONDecodeError) as error:
            raise ValueError("cannot load rules from %s: %s" % (path, error)) from error

    def run_git_diff(self, base: str | None, compare: str, cached: bool) -> str:
        command = ["git", "-C", str(self.repo_path), "diff", "--no-ext-diff", "--no-color", "--no-renames", "-U3"]
        command.extend(["--cached"] if cached else ([base, compare] if base else [compare]))
        try:
            return subprocess.run(command, text=True, capture_output=True, check=True).stdout
        except FileNotFoundError as error:
            raise RuntimeError("git is not installed or is not on PATH") from error
        except subprocess.CalledProcessError as error:
            raise RuntimeError("git diff failed: %s" % (error.stderr.strip() or "unknown git error")) from error

    def _git_diff_args(self, base: str | None, compare: str, cached: bool) -> list[str]:
        args = ["git", "-C", str(self.repo_path), "diff", "--no-ext-diff", "--no-renames"]
        args.extend(["--cached"] if cached else ([base, compare] if base else [compare]))
        return args

    def _run_git(self, args: list[str], text: bool = False) -> str | bytes:
        try:
            return subprocess.run(args, text=text, capture_output=True, check=True).stdout
        except FileNotFoundError as error:
            raise RuntimeError("git is not installed or is not on PATH") from error
        except subprocess.CalledProcessError as error:
            detail = error.stderr.decode() if isinstance(error.stderr, bytes) else error.stderr
            raise RuntimeError("git diff failed: %s" % (detail.strip() or "unknown git error")) from error

    @staticmethod
    def binary_format(path: str, content: bytes) -> tuple[str, bool]:
        magic = content[:512]
        if content.startswith(b"version https://git-lfs.github.com/spec/v1\n"): return "Git LFS pointer", False
        if magic.startswith(b"\x7fELF"): return "ELF executable", True
        if magic.startswith(b"MZ"): return "PE executable", True
        # CAFEBABE is shared by Java class files and Mach-O universal binaries;
        # the class-file suffix resolves that otherwise unavoidable ambiguity.
        if Path(path).suffix.lower() == ".class" and magic.startswith(b"\xca\xfe\xba\xbe"): return "Java class", True
        if magic[:4] in {b"\xfe\xed\xfa\xce", b"\xfe\xed\xfa\xcf", b"\xce\xfa\xed\xfe", b"\xcf\xfa\xed\xfe", b"\xca\xfe\xba\xbe", b"\xbe\xba\xfe\xca"}: return "Mach-O executable", True
        if magic.startswith(b"\x00asm"): return "WebAssembly module", True
        signatures = ((b"\x89PNG\r\n\x1a\n", "PNG image"), (b"\xff\xd8\xff", "JPEG image"), (b"GIF87a", "GIF image"), (b"GIF89a", "GIF image"), (b"%PDF-", "PDF document"), (b"!<arch>\n", "ar archive"), (b"\xed\xab\xee\xdb", "RPM package"), (b"MSCF", "Windows cabinet package"), (b"PK\x03\x04", "ZIP archive"), (b"\x1f\x8b", "gzip archive"), (b"BZh", "bzip2 archive"), (b"\xfd7zXZ\x00", "XZ archive"), (b"7z\xbc\xaf\x27\x1c", "7-zip archive"), (b"Rar!\x1a\x07", "RAR archive"), (b"SQLite format 3\x00", "SQLite database"), (b"\x89HDF\r\n\x1a\n", "HDF5 data"), (b"PAR1", "Parquet data"), (b"OggS", "Ogg media"), (b"fLaC", "FLAC audio"), (b"RIFF", "RIFF media"))
        for signature, name in signatures:
            if magic.startswith(signature): return name, False
        if len(content) > 262 and content[257:262] == b"ustar":
            names = SecurityDiffer.tar_member_names(content)
            if {"oci-layout", "index.json"}.issubset(names): return "OCI container image", False
            if {"manifest.json", "repositories"}.issubset(names): return "Docker container image", False
            return "tar archive", False
        if len(content) >= 12 and content[4:8] == b"ftyp": return "ISO media", False
        return BINARY_EXTENSIONS.get(Path(path).suffix.lower(), "binary data"), False

    @staticmethod
    def tar_member_names(content: bytes, limit: int = 10000) -> set[str]:
        """Read tar member names without extracting or decompressing untrusted content."""
        names: set[str] = set(); offset = 0
        for _ in range(limit):
            if offset + 512 > len(content): break
            header = content[offset:offset + 512]
            if header == b"\0" * 512: break
            name = header[:100].split(b"\0", 1)[0].decode("utf-8", "replace")
            prefix = header[345:500].split(b"\0", 1)[0].decode("utf-8", "replace")
            if name: names.add((prefix + "/" if prefix else "") + name)
            try: size = int(header[124:136].split(b"\0", 1)[0].strip() or b"0", 8)
            except ValueError: break
            offset += 512 + ((size + 511) // 512) * 512
        return names

    @staticmethod
    def binary_byte_diff(old: bytes, new: bytes) -> tuple[str, int | None, int | None, list[dict[str, int]]]:
        """Return exact byte spans for modest blobs and safe metadata for large ones."""
        if max(len(old), len(new)) > MAX_EXACT_BINARY_DIFF:
            return "sha256_only", None, None, []
        # A prefix/suffix comparison is deterministic, linear, and describes the changed region
        # without attempting an expensive or misleading binary patch reconstruction.
        prefix = 0
        limit = min(len(old), len(new))
        while prefix < limit and old[prefix] == new[prefix]: prefix += 1
        suffix = 0
        while suffix < limit - prefix and old[-1 - suffix] == new[-1 - suffix]: suffix += 1
        old_changed, new_changed = len(old) - prefix - suffix, len(new) - prefix - suffix
        ranges = [] if not (old_changed or new_changed) else [{"old_offset": prefix, "old_length": old_changed, "new_offset": prefix, "new_length": new_changed}]
        return "byte_range", old_changed, new_changed, ranges

    @staticmethod
    def _digest_stream(stream: Any, size: int) -> Blob:
        digest = hashlib.sha256(); sample = bytearray(); content = bytearray() if size <= MAX_EXACT_BINARY_DIFF else None
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
            if len(sample) < BINARY_SAMPLE_BYTES: sample.extend(chunk[:BINARY_SAMPLE_BYTES - len(sample)])
            if content is not None: content.extend(chunk)
        return Blob(size, digest.hexdigest(), bytes(sample), bytes(content) if content is not None else None)

    def _blob(self, object_id: str, worktree_path: Path | None = None) -> Blob | None:
        if set(object_id) == {"0"}:
            try:
                if not worktree_path or not worktree_path.is_file(): return None
                with worktree_path.open("rb") as source:
                    return self._digest_stream(source, worktree_path.stat().st_size)
            except OSError:
                raise RuntimeError("cannot read worktree file: %s" % worktree_path)
        try:
            size = int(subprocess.run(["git", "-C", str(self.repo_path), "cat-file", "-s", object_id], text=True, capture_output=True, check=True).stdout)
            process = subprocess.Popen(["git", "-C", str(self.repo_path), "cat-file", "-p", object_id], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            assert process.stdout is not None
            result = self._digest_stream(process.stdout, size)
            _, stderr = process.communicate()
            if process.returncode: raise RuntimeError(stderr.decode("utf-8", "replace").strip() or "unknown Git object error")
            return result
        except (OSError, ValueError, subprocess.CalledProcessError) as error:
            raise RuntimeError("cannot read Git object %s: %s" % (object_id, error)) from error

    def binary_changes(self, base: str | None, compare: str, cached: bool) -> list[BinaryChange]:
        raw = self._run_git(self._git_diff_args(base, compare, cached) + ["--raw", "-z"], text=False)
        assert isinstance(raw, bytes)
        changes = []
        # Raw -z records are `:mode mode old new status<TAB>path<NUL>` (and a second path for renames).
        records = raw.split(b"\0")
        index = 0
        while index < len(records):
            record = records[index]; index += 1
            if not record: continue
            # With -z, Git stores the header and pathname in separate NUL records.
            # (Without -z they are separated by a tab.) Support both forms for clarity.
            if b"\t" in record:
                header, path_raw = record.split(b"\t", 1)
            elif record.startswith(b":") and index < len(records):
                header, path_raw = record, records[index]; index += 1
            else:
                continue
            fields = header.decode("ascii", "replace").split()
            if len(fields) < 5: continue
            old_mode, new_mode, old_id, new_id, status = fields[0][1:], fields[1], fields[2], fields[3], fields[4]
            path = path_raw.decode("utf-8", "surrogateescape")
            if status.startswith(("R", "C")) and index < len(records): path = records[index].decode("utf-8", "surrogateescape"); index += 1
            old = self._blob(old_id)
            # Git uses an all-zero object ID for a worktree side of --raw. Read that
            # file directly; committed and staged comparisons always use blob IDs.
            worktree_file = self.repo_path / path if not cached and base is None else None
            new = self._blob(new_id, worktree_file)
            sample = new if new is not None else old
            if sample is None: continue
            fmt, magic_executable = self.binary_format(path, sample.sample)
            if b"\0" not in sample.sample and Path(path).suffix.lower() not in BINARY_EXTENSIONS and fmt == "binary data": continue
            executable = magic_executable or new_mode == "100755" or old_mode == "100755"
            if old is None or new is None or old.content is None or new.content is None:
                method, old_changed, new_changed, ranges = "sha256_only", None, None, []
            else:
                method, old_changed, new_changed, ranges = self.binary_byte_diff(old.content, new.content)
            changes.append(BinaryChange(path, status, fmt, executable, old.size if old is not None else None, new.size if new is not None else None,
                old.sha256 if old is not None else None, new.sha256 if new is not None else None,
                method, old_changed, new_changed, ranges))
        return sorted(changes, key=lambda item: item.path)

    @staticmethod
    def parse_diff(diff: str) -> tuple[list[DiffLine], list[DiffLine], set[str]]:
        """Parse standard unified diff while preserving actual new/old line numbers."""
        added: list[DiffLine] = []; removed: list[DiffLine] = []; paths: set[str] = set()
        old_path = new_path = None; old_number = new_number = 0; in_hunk = False
        def parse_path(header: str) -> str | None:
            value = header[4:].split("\t", 1)[0]
            if value == "/dev/null": return None
            return value[2:] if value.startswith(("a/", "b/")) else value
        for raw in diff.splitlines():
            if raw.startswith("--- "): old_path, in_hunk = parse_path(raw), False
            elif raw.startswith("+++ "):
                new_path, in_hunk = parse_path(raw), False
                paths.update(path for path in (old_path, new_path) if path)
            elif match := HUNK.match(raw):
                old_number, new_number, in_hunk = int(match.group(1)), int(match.group(2)), True
            elif in_hunk and raw.startswith("+") and not raw.startswith("+++") and new_path:
                added.append(DiffLine(new_path, new_number, raw[1:])); new_number += 1
            elif in_hunk and raw.startswith("-") and not raw.startswith("---") and old_path:
                removed.append(DiffLine(old_path, old_number, raw[1:])); old_number += 1
            elif in_hunk and raw.startswith(" "): old_number += 1; new_number += 1
        return added, removed, paths

    def scan_lines(self, lines: Iterable[DiffLine], kind: str) -> list[Finding]:
        findings = []
        for line in lines:
            language = file_type(line.path)
            for rule in self.rules:
                if rule.kind != kind or (language not in rule.file_types and "generic" not in rule.file_types):
                    continue
                if rule.pattern.search(line.text):
                    sensitive = "secret" in rule.id.lower() or "private key" in rule.title.lower()
                    findings.append(Finding(rule.id, rule.title, rule.severity if kind == "vulnerability" else "medium",
                        "removed_protection" if kind == "protection" else language, rule.description,
                        rule.remediation, line.path, line.number,
                        "<redacted: potentially sensitive matched content>" if sensitive else line.text.strip()[:300]))
        return findings

    def analyze_text(self, diff: str) -> list[Finding]:
        added, removed, paths = self.parse_diff(diff)
        findings = [Finding("SENSITIVE_FILE", "Sensitive file changed", "critical", "secrets",
                    "A file conventionally used for credentials or private keys changed.",
                    "Remove it from version control, rotate exposed material, and use a secret manager.",
                    path, 0, path) for path in paths if SENSITIVE_PATH.search(path)]
        findings += self.scan_lines(added, "vulnerability")
        findings += self.scan_lines(removed, "protection")
        unique = {(x.rule_id, x.path, x.line): x for x in findings}
        return sorted(unique.values(), key=lambda x: (-SEVERITIES[x.severity], x.path, x.line, x.rule_id))

    def analyze(self, base: str | None, compare: str, cached: bool) -> dict[str, Any]:
        findings = self.analyze_text(self.run_git_diff(base, compare, cached))
        binary_changes = self.binary_changes(base, compare, cached)
        text_sensitive_paths = {item.path for item in findings if item.rule_id == "SENSITIVE_FILE"}
        for change in binary_changes:
            if SENSITIVE_PATH.search(change.path) and change.path not in text_sensitive_paths:
                findings.append(Finding("SENSITIVE_FILE", "Sensitive file changed", "critical", "secrets",
                    "A file conventionally used for credentials or private keys changed.",
                    "Remove it from version control, rotate exposed material, and use a secret manager.",
                    change.path, 0, change.path))
            container = change.format in {"OCI container image", "Docker container image", "container image"}
            lfs_pointer = change.format == "Git LFS pointer"
            severity = "high" if change.executable or container or lfs_pointer else "low"
            rule_id = "LFS_ARTIFACT_UNAVAILABLE" if lfs_pointer else ("CONTAINER_IMAGE_CHANGED" if container else ("BINARY_EXECUTABLE_CHANGED" if change.executable else "BINARY_DATA_CHANGED"))
            title = "Git LFS artifact unavailable" if lfs_pointer else ("Container image changed" if container else ("Binary executable changed" if change.executable else "Binary data changed"))
            category = "supply_chain" if lfs_pointer else ("container" if container else "binary")
            findings.append(Finding(rule_id, title, severity, category,
                "A %s changed; text security rules cannot inspect its contents." % change.format.lower(),
                "Fetch and scan the LFS artifact before release." if lfs_pointer else "Review the binary provenance, hash, and byte-range metadata; scan untrusted images or executables before deployment.",
                change.path, 0, "%s: %s -> %s (%s)" % (change.format, change.old_sha256 or "new", change.new_sha256 or "deleted", change.diff_method)))
        unique = {(x.rule_id, x.path, x.line): x for x in findings}
        findings = sorted(unique.values(), key=lambda x: (-SEVERITIES[x.severity], x.path, x.line, x.rule_id))
        highest = max((SEVERITIES[item.severity] for item in findings), default=0)
        return {
            "schema_version": 4, "generated_at": datetime.now(timezone.utc).isoformat(),
            "comparison": "HEAD..INDEX" if cached else ("%s..%s" % (base, compare) if base else "%s..WORKTREE" % compare),
            "scan": {"tool_version": TOOL_VERSION, "policy_sha256": self.policy_sha256,
                     "binary_hash": "sha256", "exact_binary_diff_max_bytes": MAX_EXACT_BINARY_DIFF,
                     "binary_sample_bytes": BINARY_SAMPLE_BYTES,
                     "limitations": ["Binary content is not semantically disassembled or vulnerability scanned.", "Git LFS pointers require artifact retrieval and a separate scan.", "Evidence for secret and private-key findings is redacted."]},
            "summary": {"finding_count": len(findings), "highest_severity": next(k for k, v in SEVERITIES.items() if v == highest),
                        "by_severity": {level: sum(x.severity == level for x in findings) for level in SEVERITIES}},
            "binary_changes": [asdict(item) for item in binary_changes],
            "findings": [asdict(item) for item in findings],
        }

    def install_hook(self, force: bool) -> None:
        try:
            raw_path = subprocess.run(["git", "-C", str(self.repo_path), "rev-parse", "--git-path", "hooks/pre-commit"], text=True, capture_output=True, check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError) as error:
            raise RuntimeError("%s is not a supported Git worktree" % self.repo_path) from error
        hook = Path(raw_path)
        if not hook.is_absolute(): hook = self.repo_path / hook
        hook.parent.mkdir(parents=True, exist_ok=True)
        if hook.exists() and not force: raise RuntimeError("refusing to overwrite existing hook: %s (use --force)" % hook)
        hook.write_text("#!/bin/sh\nexec %s %s %s --cached --fail-on high --format json\n" % tuple(shlex.quote(str(item)) for item in (sys.executable, Path(__file__).resolve(), self.repo_path)), encoding="utf-8")
        hook.chmod(0o755)

def render_yaml(value: Any, indent: int = 0) -> str:
    """Small, dependency-free YAML emitter for this report's JSON-shaped data."""
    pad = " " * indent
    if isinstance(value, dict):
        lines = []
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                lines.extend(["%s%s:" % (pad, key), render_yaml(item, indent + 2)])
            else:
                lines.append("%s%s: %s" % (pad, key, json.dumps(item)))
        return "\n".join(lines)
    if isinstance(value, list):
        if not value: return "[]"
        rendered = []
        for item in value:
            if isinstance(item, dict):
                rendered.extend(["%s-" % pad, render_yaml(item, indent + 2)])
            else: rendered.append("%s- %s" % (pad, json.dumps(item)))
        return "\n".join(rendered)
    return json.dumps(value)

def render_toml(report: dict[str, Any]) -> str:
    def scalar(value: Any) -> str: return json.dumps(value)
    lines = ["schema_version = %s" % report["schema_version"], "generated_at = %s" % scalar(report["generated_at"]), "comparison = %s" % scalar(report["comparison"]), "", "[summary]"]
    lines += ["%s = %s" % (key, scalar(value)) for key, value in report["summary"].items() if key != "by_severity"]
    lines += ["", "[summary.by_severity]"] + ["%s = %s" % (key, value) for key, value in report["summary"]["by_severity"].items()]
    if "scan" in report:
        lines += ["", "[scan]"] + ["%s = %s" % (key, scalar(value)) for key, value in report["scan"].items()]
    for change in report.get("binary_changes", []):
        lines += ["", "[[binary_changes]]"] + ["%s = %s" % (key, scalar(value)) for key, value in change.items()]
    for finding in report["findings"]:
        lines += ["", "[[findings]]"] + ["%s = %s" % (key, scalar(value)) for key, value in finding.items()]
    return "\n".join(lines) + "\n"

def render(report: dict[str, Any], output_format: str) -> str:
    if output_format == "json": return json.dumps(report, indent=2, sort_keys=True) + "\n"
    if output_format == "yaml": return render_yaml(report) + "\n"
    return render_toml(report)

def main() -> int:
    parser = argparse.ArgumentParser(description="Diff-aware security policy scanner")
    parser.add_argument("repo_path"); parser.add_argument("base", nargs="?", default=None); parser.add_argument("compare", nargs="?", default="HEAD")
    parser.add_argument("--cached", action="store_true", help="scan HEAD..INDEX")
    parser.add_argument("--rules", help="custom JSON policy file")
    parser.add_argument("--format", choices=("json", "yaml", "toml"), default="json")
    parser.add_argument("--output", help="write report to this path as well as stdout")
    parser.add_argument("--fail-on", choices=SEVERITIES, help="exit 1 at or above this severity")
    parser.add_argument("--install-hook", action="store_true"); parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        scanner = SecurityDiffer(args.repo_path, args.rules)
        if args.install_hook: scanner.install_hook(args.force); print("Installed security-diff pre-commit hook."); return 0
        report = scanner.analyze(args.base, args.compare, args.cached)
    except (RuntimeError, ValueError) as error:
        print("security-diff: %s" % error, file=sys.stderr); return 2
    body = render(report, args.format); print(body, end="")
    if args.output: Path(args.output).write_text(body, encoding="utf-8")
    return int(bool(args.fail_on and any(SEVERITIES[x["severity"]] >= SEVERITIES[args.fail_on] for x in report["findings"])))

if __name__ == "__main__": raise SystemExit(main())
