#!/usr/bin/env python3
"""Diff-aware security policy scanner for Python, shell, Terraform, and Ansible."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SEVERITIES = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
HUNK = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")
SENSITIVE_PATH = re.compile(r"(^|/)(?:\.env(?:\.[^/]+)?|(?:id_rsa|id_ed25519)(?:\.pub)?|[^/]+\.(?:pem|key|p12)|secrets?\.json|credentials)$", re.I)

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
        rules_path = rules_path or str(Path(__file__).with_name("security_rules.json"))
        self.rules = self.load_rules(rules_path)

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
                    findings.append(Finding(rule.id, rule.title, rule.severity if kind == "vulnerability" else "medium",
                        "removed_protection" if kind == "protection" else language, rule.description,
                        rule.remediation, line.path, line.number, line.text.strip()[:300]))
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
        highest = max((SEVERITIES[item.severity] for item in findings), default=0)
        return {
            "schema_version": 2, "generated_at": datetime.now(timezone.utc).isoformat(),
            "comparison": "HEAD..INDEX" if cached else ("%s..%s" % (base, compare) if base else "%s..WORKTREE" % compare),
            "summary": {"finding_count": len(findings), "highest_severity": next(k for k, v in SEVERITIES.items() if v == highest),
                        "by_severity": {level: sum(x.severity == level for x in findings) for level in SEVERITIES}},
            "findings": [asdict(item) for item in findings],
        }

    def install_hook(self, force: bool) -> None:
        hook = self.repo_path / ".git" / "hooks" / "pre-commit"
        if not hook.parent.is_dir(): raise RuntimeError("%s is not a supported Git worktree" % self.repo_path)
        if hook.exists() and not force: raise RuntimeError("refusing to overwrite existing hook: %s (use --force)" % hook)
        hook.write_text('#!/bin/sh\n"%s" "%s" "%s" --cached --fail-on high --format json\n' % (sys.executable, Path(__file__).resolve(), self.repo_path), encoding="utf-8")
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
