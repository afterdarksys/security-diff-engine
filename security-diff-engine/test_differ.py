import json
import unittest
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
        self.assertEqual(json.loads(render(report, "json"))["schema_version"], 2)
if __name__ == "__main__": unittest.main()
