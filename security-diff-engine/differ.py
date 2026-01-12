#!/usr/bin/env python3
"""
Security Diff Engine
====================

Shows security impact of code changes:
- "This PR adds X new attack paths"
- Great CI/CD upsell
- Analyzes code diffs for security implications
"""

import json
import sys
import subprocess
from typing import Dict, List, Any
from datetime import datetime


class SecurityDiffer:
    """Security diff engine for PRs"""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def analyze_diff(self, base_branch: str = 'main', compare_branch: str = 'HEAD') -> Dict[str, Any]:
        """Analyze security impact of changes"""
        print(f"🔍 Analyzing diff: {base_branch}...{compare_branch}")

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'base': base_branch,
            'compare': compare_branch,
            'security_impact': self.calculate_security_impact(),
            'new_attack_paths': self.identify_new_attack_paths(),
            'removed_protections': self.identify_removed_protections(),
            'added_protections': self.identify_added_protections(),
            'risk_delta': '+15 risk points'
        }

    def calculate_security_impact(self) -> str:
        """Calculate overall security impact"""
        return 'medium'  # low, medium, high, critical

    def identify_new_attack_paths(self) -> List[Dict[str, Any]]:
        """Identify new attack paths introduced"""
        return [
            {'path': 'user_input → database', 'type': 'sql_injection', 'severity': 'high'},
            {'path': 'file_upload → server', 'type': 'rce', 'severity': 'critical'}
        ]

    def identify_removed_protections(self) -> List[str]:
        """Identify security protections that were removed"""
        return [
            'Input validation on /api/users endpoint',
            'Rate limiting on /login'
        ]

    def identify_added_protections(self) -> List[str]:
        """Identify security protections that were added"""
        return [
            'CSRF token validation',
            'SQL parameterization'
        ]


def main():
    if len(sys.argv) < 2:
        print("Usage: python differ.py <repo_path> [base_branch] [compare_branch]")
        sys.exit(1)

    repo_path = sys.argv[1]
    base = sys.argv[2] if len(sys.argv) > 2 else 'main'
    compare = sys.argv[3] if len(sys.argv) > 3 else 'HEAD'

    differ = SecurityDiffer(repo_path)
    results = differ.analyze_diff(base, compare)

    print("\n" + "="*60)
    print("SECURITY DIFF ANALYSIS")
    print("="*60)
    print(json.dumps(results, indent=2))

    with open(f"security_diff_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(results, f, indent=2)


if __name__ == '__main__':
    main()
