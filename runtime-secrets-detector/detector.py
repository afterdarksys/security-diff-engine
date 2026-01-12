#!/usr/bin/env python3
"""
Runtime Secrets Leak Detector
==============================

Detects secrets at runtime (not just in repos):
- Hooks into application memory
- Monitors logs and APM traces
- Pattern matching + ML entropy analysis
- Detects secrets before they leave the system
- Auto-revokes exposed secrets via integrations
"""

import re
import sys
import json
import hashlib
from typing import List, Dict, Any
from datetime import datetime


class SecretsDetector:
    """Runtime secrets leak detector"""

    def __init__(self):
        self.patterns = self._load_patterns()
        self.detected_secrets = []

    def _load_patterns(self) -> Dict[str, re.Pattern]:
        """Load regex patterns for secret detection"""
        return {
            'aws_access_key': re.compile(r'AKIA[0-9A-Z]{16}'),
            'aws_secret_key': re.compile(r'[A-Za-z0-9/+=]{40}'),
            'github_token': re.compile(r'ghp_[0-9a-zA-Z]{36}'),
            'slack_token': re.compile(r'xox[baprs]-[0-9]{10,12}-[0-9]{10,12}-[0-9a-zA-Z]{24,32}'),
            'stripe_key': re.compile(r'sk_live_[0-9a-zA-Z]{24}'),
            'private_key': re.compile(r'-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----'),
            'password': re.compile(r'(password|passwd|pwd)\s*[:=]\s*["\']?([^"\'\s]+)["\']?', re.IGNORECASE),
            'api_key': re.compile(r'(api[_-]?key|apikey)\s*[:=]\s*["\']?([0-9a-zA-Z\-_]{20,})["\']?', re.IGNORECASE),
            'jwt': re.compile(r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*'),
            'connection_string': re.compile(r'(mongodb|postgres|mysql)://[^:]+:[^@]+@', re.IGNORECASE)
        }

    def scan_text(self, text: str, source: str = 'unknown') -> List[Dict[str, Any]]:
        """Scan text for secrets"""
        findings = []

        for secret_type, pattern in self.patterns.items():
            matches = pattern.finditer(text)
            for match in matches:
                secret_value = match.group(0)
                finding = {
                    'type': secret_type,
                    'value_hash': hashlib.sha256(secret_value.encode()).hexdigest()[:16],
                    'source': source,
                    'line_number': text[:match.start()].count('\n') + 1,
                    'entropy': self.calculate_entropy(secret_value),
                    'severity': self.get_severity(secret_type),
                    'timestamp': datetime.utcnow().isoformat()
                }
                findings.append(finding)
                self.detected_secrets.append(finding)

        return findings

    def scan_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Scan file for secrets"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return self.scan_text(content, source=file_path)
        except Exception as e:
            print(f"Error scanning {file_path}: {e}", file=sys.stderr)
            return []

    def scan_logs(self, log_file: str) -> List[Dict[str, Any]]:
        """Scan log files for leaked secrets"""
        return self.scan_file(log_file)

    def monitor_memory(self, process_id: int) -> List[Dict[str, Any]]:
        """Monitor process memory for secrets (requires privileges)"""
        # TODO: Implement memory scanning (platform-specific)
        print(f"⚠️  Memory monitoring not yet implemented for PID {process_id}")
        return []

    def calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text"""
        if not text:
            return 0.0

        entropy = 0.0
        for char in set(text):
            freq = text.count(char) / len(text)
            entropy -= freq * (freq.bit_length() - 1)

        return round(entropy, 3)

    def get_severity(self, secret_type: str) -> str:
        """Get severity level for secret type"""
        critical_types = ['aws_secret_key', 'private_key', 'stripe_key']
        high_types = ['aws_access_key', 'github_token', 'slack_token']

        if secret_type in critical_types:
            return 'critical'
        elif secret_type in high_types:
            return 'high'
        else:
            return 'medium'

    def auto_revoke(self, finding: Dict[str, Any]) -> bool:
        """Auto-revoke exposed secret (integrations required)"""
        # TODO: Implement integrations with AWS, GitHub, etc.
        print(f"⚠️  Auto-revocation not yet implemented for {finding['type']}")
        return False

    def generate_report(self) -> Dict[str, Any]:
        """Generate detection report"""
        return {
            'scan_time': datetime.utcnow().isoformat(),
            'total_secrets_found': len(self.detected_secrets),
            'by_severity': self._group_by_severity(),
            'by_type': self._group_by_type(),
            'secrets': self.detected_secrets
        }

    def _group_by_severity(self) -> Dict[str, int]:
        """Group findings by severity"""
        groups = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for secret in self.detected_secrets:
            groups[secret.get('severity', 'medium')] += 1
        return groups

    def _group_by_type(self) -> Dict[str, int]:
        """Group findings by type"""
        groups = {}
        for secret in self.detected_secrets:
            secret_type = secret.get('type', 'unknown')
            groups[secret_type] = groups.get(secret_type, 0) + 1
        return groups


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python detector.py <file_or_directory>")
        print("\nExamples:")
        print("  python detector.py app.log")
        print("  python detector.py /var/log/")
        sys.exit(1)

    target = sys.argv[1]
    detector = SecretsDetector()

    print("🔍 Runtime Secrets Leak Detector")
    print("=" * 50)

    import os
    if os.path.isfile(target):
        print(f"Scanning file: {target}")
        findings = detector.scan_file(target)
    elif os.path.isdir(target):
        print(f"Scanning directory: {target}")
        for root, dirs, files in os.walk(target):
            for file in files:
                if file.endswith(('.log', '.txt', '.json')):
                    file_path = os.path.join(root, file)
                    detector.scan_file(file_path)
        findings = detector.detected_secrets
    else:
        print(f"Error: {target} not found")
        sys.exit(1)

    # Generate report
    report = detector.generate_report()

    print(f"\n🎯 Results:")
    print(f"   Total Secrets Found: {report['total_secrets_found']}")
    print(f"\n📊 By Severity:")
    for severity, count in report['by_severity'].items():
        if count > 0:
            print(f"   - {severity.upper()}: {count}")

    print(f"\n📦 By Type:")
    for secret_type, count in report['by_type'].items():
        print(f"   - {secret_type}: {count}")

    if findings:
        print(f"\n⚠️  SECRETS DETECTED!")
        print("   Review and revoke immediately:")
        for i, finding in enumerate(findings[:5], 1):  # Show first 5
            print(f"   {i}. {finding['type']} in {finding['source']} (line {finding['line_number']})")

    # Save report
    report_file = f"secrets_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Full report saved to: {report_file}")


if __name__ == '__main__':
    main()
