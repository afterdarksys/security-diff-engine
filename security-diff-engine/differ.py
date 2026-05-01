#!/usr/bin/env python3
"""
Security Diff Engine
====================

Multi-language engine that analyzes code diffs for security implications using heuristic rules.
"""

import json
import sys
import os
import subprocess
import re
from typing import Dict, List, Any, Tuple
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Rule:
    id: str
    description: str
    pattern: re.Pattern
    type: str  # 'vulnerability', 'protection'
    risk_points: int
    severity: str
    languages: List[str]

    def applies_to(self, filename: str) -> bool:
        if not self.languages:
            return True
        ext = os.path.splitext(filename)[1]
        return ext in self.languages

# Sensitive files that should never be modified or added to public repo
SENSITIVE_FILES_PATTERN = re.compile(r"(\.env|.*\.pem|id_rsa|secrets\.json|\.aws/credentials)$", re.IGNORECASE)

class SecurityDiffer:
    def __init__(self, repo_path: str, rules_path: str = "security_rules.json"):
        self.repo_path = os.path.abspath(repo_path)
        self.rules = self._load_rules(rules_path)
        
    def _load_rules(self, rules_path: str) -> List[Rule]:
        # Try to resolve relative to this script if not absolute
        if not os.path.isabs(rules_path):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            rules_path = os.path.join(script_dir, rules_path)
            
        try:
            with open(rules_path, 'r') as f:
                data = json.load(f)
                
            rules = []
            for r in data.get('rules', []):
                rules.append(Rule(
                    id=r['id'],
                    description=r['description'],
                    pattern=re.compile(r['pattern']),
                    type=r['type'],
                    risk_points=r['risk_points'],
                    severity=r['severity'],
                    languages=r.get('languages', [])
                ))
            return rules
        except Exception as e:
            print(f"Error loading rules from {rules_path}: {e}", file=sys.stderr)
            sys.exit(1)

    def run_git_diff(self, base_branch: str, compare_branch: str, cached: bool = False) -> str:
        """Run git diff and return the output"""
        try:
            cmd = ["git", "-C", self.repo_path, "diff", "-U0"]
            if cached:
                cmd.append("--cached")
            else:
                cmd.append(f"{base_branch}..{compare_branch}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error running git diff: {e.stderr}", file=sys.stderr)
            sys.exit(1)

    def parse_diff(self, diff_text: str) -> Dict[str, Dict[str, Any]]:
        """Parse unified diff text into added and removed lines per file.
           Returns { 'filename': {'added': [...], 'removed': [...] } }
        """
        files = {}
        current_file = None
        
        for line in diff_text.splitlines():
            if line.startswith("diff --git"):
                parts = line.split(" ")
                if len(parts) >= 3:
                    current_file = parts[2][2:] # strip a/
                if current_file not in files:
                    files[current_file] = {'added': [], 'removed': []}
            elif line.startswith("+++ ") or line.startswith("--- "):
                pass # skip these headers
            elif line.startswith("+") and not line.startswith("+++"):
                if current_file:
                    files[current_file]['added'].append(line[1:])
            elif line.startswith("-") and not line.startswith("---"):
                if current_file:
                    files[current_file]['removed'].append(line[1:])
                    
        return files

    def install_precommit_hook(self):
        """Install differ.py as a git pre-commit hook."""
        hooks_dir = os.path.join(self.repo_path, '.git', 'hooks')
        if not os.path.exists(hooks_dir):
            print("Error: .git/hooks directory not found. Is this a git repository?")
            sys.exit(1)
            
        hook_path = os.path.join(hooks_dir, 'pre-commit')
        script_path = os.path.abspath(__file__)
        
        hook_script = f"""#!/bin/sh
# Security Diff Engine pre-commit hook
python3 "{script_path}" "{self.repo_path}" --cached
if [ $? -ne 0 ]; then
    echo "Security Diff Engine: Commit blocked due to high/critical security impact."
    exit 1
fi
"""
        with open(hook_path, 'w') as f:
            f.write(hook_script)
        os.chmod(hook_path, 0o755)
        print(f"✅ Successfully installed pre-commit hook at {hook_path}")

    def analyze_diff(self, base_branch: str = 'main', compare_branch: str = 'HEAD', cached: bool = False) -> Tuple[Dict[str, Any], int]:
        """Analyze security impact of changes"""
        diff_text = self.run_git_diff(base_branch, compare_branch, cached)
        parsed_files = self.parse_diff(diff_text)
        
        new_attack_paths = []
        added_protections = []
        removed_protections = []
        total_risk_delta = 0
        total_lines_changed = 0
        
        # 1. Check Diff Size
        for filename, changes in parsed_files.items():
            lines_in_file = len(changes['added']) + len(changes['removed'])
            total_lines_changed += lines_in_file
            
        if total_lines_changed > 500 or len(parsed_files) > 15:
            new_attack_paths.append({
                'path': "global (DIFF_TOO_LARGE)",
                'type': "DIFF_TOO_LARGE",
                'severity': "medium",
                'description': f"Diff is too large to effectively review ({total_lines_changed} lines, {len(parsed_files)} files)"
            })
            total_risk_delta += 15

        # 2. Analyze per file
        for filename, changes in parsed_files.items():
            if SENSITIVE_FILES_PATTERN.search(filename):
                new_attack_paths.append({
                    'path': filename,
                    'type': "SENSITIVE_FILE_EXPOSURE",
                    'severity': "critical",
                    'description': "Modification or exposure of a sensitive file."
                })
                total_risk_delta += 50
                
            for line in changes['added']:
                for rule in self.rules:
                    if rule.applies_to(filename) and rule.pattern.search(line):
                        if rule.type == "vulnerability":
                            new_attack_paths.append({
                                'path': f"{filename} (Added: {rule.id})",
                                'type': rule.id,
                                'severity': rule.severity,
                                'description': rule.description
                            })
                            total_risk_delta += rule.risk_points
                        elif rule.type == "protection":
                            added_protections.append(f"{filename}: {rule.description}")
                            total_risk_delta += rule.risk_points # negative risk points
                            
            for line in changes['removed']:
                for rule in self.rules:
                    if rule.applies_to(filename) and rule.pattern.search(line):
                        if rule.type == "protection":
                            removed_protections.append(f"{filename}: Removed {rule.description}")
                            total_risk_delta += abs(rule.risk_points) * 2
        
        impact = 'low'
        if total_risk_delta > 50:
            impact = 'critical'
        elif total_risk_delta > 20:
            impact = 'high'
        elif total_risk_delta > 0:
            impact = 'medium'
        else:
            impact = 'low'

        sign = "+" if total_risk_delta >= 0 else ""
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'base': base_branch if not cached else "INDEX",
            'compare': compare_branch if not cached else "WORKING_TREE",
            'security_impact': impact,
            'new_attack_paths': new_attack_paths,
            'removed_protections': removed_protections,
            'added_protections': added_protections,
            'risk_delta': f'{sign}{total_risk_delta} risk points'
        }
        
        return results, total_risk_delta

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Security Diff Engine")
    parser.add_argument("repo_path", help="Path to the repository")
    parser.add_argument("base", nargs="?", default="main", help="Base branch")
    parser.add_argument("compare", nargs="?", default="HEAD", help="Compare branch")
    parser.add_argument("--cached", action="store_true", help="Run against git diff --cached (used for pre-commit hooks)")
    parser.add_argument("--install-hook", action="store_true", help="Install as a pre-commit hook in the target repo")

    args = parser.parse_args()

    differ = SecurityDiffer(args.repo_path)
    
    if args.install_hook:
        differ.install_precommit_hook()
        sys.exit(0)

    print("🔍 Analyzing diff...")
    results, risk_points = differ.analyze_diff(args.base, args.compare, args.cached)

    print("\n" + "="*60)
    print("SECURITY DIFF ANALYSIS")
    print("="*60)
    print(json.dumps(results, indent=2))

    with open(f"security_diff_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(results, f, indent=2)

    # For pre-commit hooks, exit with error code if impact is high or critical
    if args.cached and risk_points > 20:
        sys.exit(1)
    
    sys.exit(0)

if __name__ == '__main__':
    main()
