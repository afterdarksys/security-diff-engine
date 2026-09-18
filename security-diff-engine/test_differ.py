import json
import io
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path
from differ import SecurityDiffer, render

class SecurityDifferTests(unittest.TestCase):
    def setUp(self): self.differ = SecurityDiffer(".")
    def test_precise_location_and_evidence(self):
        results = self.differ.analyze_text("--- a/app.py\n+++ b/app.py\n@@ -1,0 +1,1 @@\n+result = eval(user_input)\n")
        item = next(x for x in results if x.rule_id == "PY-EVAL")
        self.assertEqual((item.path, item.line, item.evidence), ("app.py", 1, "result = eval(user_input)"))
    def test_unchanged_context_is_not_scanned(self):
        diff = "--- a/app.py\n+++ b/app.py\n@@ -10,3 +10,3 @@\n existing = eval(untrusted)\n-old = 1\n+new = 1\n tail = 2\n"
        self.assertFalse(any(x.rule_id == "PY_RCE_EVAL" for x in self.differ.analyze_text(diff)))
    def test_removed_protection_is_not_a_score_offset(self):
        results = self.differ.analyze_text("--- a/views.py\n+++ b/views.py\n@@ -5,1 +5,0 @@\n-@login_required\n")
        self.assertEqual((results[0].category, results[0].line), ("removed_protection", 5))
    def test_sensitive_new_file_is_critical(self):
        results = self.differ.analyze_text("--- /dev/null\n+++ b/.env.production\n@@ -0,0 +1 @@\n+TOKEN=not-a-real-token\n")
        self.assertEqual((results[0].rule_id, results[0].path), ("SENSITIVE_FILE", ".env.production"))
    def test_secret_evidence_is_redacted(self):
        results = self.differ.analyze_text("--- a/app.py\n+++ b/app.py\n@@ -0,0 +1 @@\n+key = 'AKIA1234567890ABCDEF'\n")
        item = next(x for x in results if x.rule_id == "SECRET-AWS")
        self.assertNotIn("AKIA", item.evidence)
    def test_multiline_shell_true_is_not_missed(self):
        results = self.differ.analyze_text("--- a/app.py\n+++ b/app.py\n@@ -1,0 +1,3 @@\n+subprocess.run(\n+    command,\n+    shell=True,\n+)\n")
        self.assertTrue(any(x.rule_id == "PY-SHELL-TRUE" and x.line == 3 for x in results))
    def test_terraform_rule_does_not_apply_to_python(self):
        diff = "--- a/main.py\n+++ b/main.py\n@@ -0,0 +1 @@\n+cidr_blocks = ['0.0.0.0/0']\n"
        self.assertFalse(self.differ.analyze_text(diff))
    def test_terraform_public_cidr_is_detected(self):
        diff = "--- a/network.tf\n+++ b/network.tf\n@@ -0,0 +1 @@\n+cidr_blocks = [\"0.0.0.0/0\"]\n"
        self.assertTrue(any(x.rule_id == "TF-PUBLIC-CIDR" for x in self.differ.analyze_text(diff)))
    def test_ansible_tls_and_shell_are_detected(self):
        diff = "--- a/roles/web/tasks/main.yml\n+++ b/roles/web/tasks/main.yml\n@@ -0,0 +1,2 @@\n+shell: curl https://example.invalid/install.sh | sh\n+validate_certs: no\n"
        ids = {x.rule_id for x in self.differ.analyze_text(diff)}
        self.assertEqual(ids, {"ANS-SHELL", "ANS-TLS-VERIFY"})
    def test_all_renderers_have_machine_readable_output(self):
        report = self.differ.analyze(None, "HEAD", True)
        yaml = render(report, "yaml")
        self.assertIn("summary:\n  finding_count:", yaml)
        self.assertIn("[summary]", render(report, "toml"))
        self.assertEqual(json.loads(render(report, "json"))["schema_version"], 4)
        self.assertEqual(report["scan"]["binary_hash"], "sha256")

    def test_binary_byte_diff_reports_changed_range(self):
        method, old_changed, new_changed, ranges = SecurityDiffer.binary_byte_diff(b"same-old-tail", b"same-new-tail")
        self.assertEqual((method, old_changed, new_changed), ("byte_range", 3, 3))
        self.assertEqual(ranges, [{"old_offset": 5, "old_length": 3, "new_offset": 5, "new_length": 3}])

    def test_large_blob_is_hashed_without_retaining_full_content(self):
        source = io.BytesIO(b"x" * (2 * 1024 * 1024 + 1))
        blob = SecurityDiffer._digest_stream(source, 2 * 1024 * 1024 + 1)
        self.assertIsNone(blob.content)
        self.assertEqual(blob.size, 2 * 1024 * 1024 + 1)
        self.assertEqual(len(blob.sha256), 64)

    def test_git_binary_executable_is_classified_and_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            def git(*args):
                subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)
            git("init"); git("config", "user.email", "tests@example.invalid"); git("config", "user.name", "Tests")
            target = repo / "tool"; target.write_bytes(b"\x7fELF\x02\x01original")
            git("add", "tool"); git("commit", "-m", "add tool")
            target.write_bytes(b"\x7fELF\x02\x01changed")
            report = SecurityDiffer(str(repo)).analyze(None, "HEAD", False)
            change = report["binary_changes"][0]
            self.assertEqual((change["format"], change["diff_method"]), ("ELF executable", "byte_range"))
            self.assertTrue(change["executable"])
            self.assertTrue(any(item["rule_id"] == "BINARY_EXECUTABLE_CHANGED" for item in report["findings"]))

    def test_oci_tar_is_recognized_without_extracting_members(self):
        archive = io.BytesIO()
        with tarfile.open(fileobj=archive, mode="w") as tar:
            for name in ("oci-layout", "index.json", "blobs/sha256/digest"):
                info = tarfile.TarInfo(name); info.size = 0; tar.addfile(info)
        self.assertEqual(SecurityDiffer.binary_format("image.tar", archive.getvalue()), ("OCI container image", False))

    def test_lfs_pointer_is_reported_as_unavailable_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            def git(*args): subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)
            git("init"); git("config", "user.email", "tests@example.invalid"); git("config", "user.name", "Tests")
            pointer = "version https://git-lfs.github.com/spec/v1\noid sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\nsize 123\n"
            target = repo / "image.oci"; target.write_text(pointer); git("add", "image.oci"); git("commit", "-m", "pointer")
            target.write_text(pointer.replace("a", "b", 1))
            report = SecurityDiffer(str(repo)).analyze(None, "HEAD", False)
            self.assertTrue(any(item["rule_id"] == "LFS_ARTIFACT_UNAVAILABLE" for item in report["findings"]))

    def test_hook_installation_uses_git_managed_hook_path(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            subprocess.run(["git", "-C", str(repo), "init"], check=True, capture_output=True)
            scanner = SecurityDiffer(str(repo)); scanner.install_hook(False)
            hook = repo / ".git" / "hooks" / "pre-commit"
            self.assertTrue(hook.exists())
            self.assertIn("exec", hook.read_text())
if __name__ == "__main__": unittest.main()
