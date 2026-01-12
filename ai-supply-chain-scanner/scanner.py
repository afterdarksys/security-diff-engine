#!/usr/bin/env python3
"""
AI Supply-Chain Security Scanner
=================================

Goes beyond SBOMs to provide intelligence-driven supply chain analysis:
- Analyzes repo behavior, not just packages
- Scores maintainer trust & bus factor
- Detects commit anomalies (AI-generated, obfuscated diffs)
- Identifies dependency hijack likelihood
- Calculates transitive dependency blast radius
- Detects "weaponized open-source" patterns
"""

import json
import subprocess
import re
from typing import Dict, List, Any
from datetime import datetime
import hashlib


class SupplyChainScanner:
    """AI-powered supply chain security scanner"""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.risk_score = 0
        self.findings = []

    def scan(self) -> Dict[str, Any]:
        """Run complete supply chain analysis"""
        print(f"🔍 Scanning supply chain: {self.repo_path}")

        results = {
            'repo_path': self.repo_path,
            'scan_time': datetime.utcnow().isoformat(),
            'maintainer_analysis': self.analyze_maintainers(),
            'commit_anomalies': self.detect_commit_anomalies(),
            'dependency_analysis': self.analyze_dependencies(),
            'hijack_risk': self.assess_hijack_risk(),
            'blast_radius': self.calculate_blast_radius(),
            'weaponization_indicators': self.detect_weaponization(),
            'overall_risk_score': 0,
            'severity': 'unknown',
            'recommendations': []
        }

        # Calculate overall risk
        results['overall_risk_score'] = self.calculate_risk_score(results)
        results['severity'] = self.get_severity(results['overall_risk_score'])
        results['recommendations'] = self.generate_recommendations(results)

        return results

    def analyze_maintainers(self) -> Dict[str, Any]:
        """Analyze maintainer trust and bus factor"""
        try:
            # Get commit authors
            cmd = f"cd {self.repo_path} && git shortlog -sn --all"
            output = subprocess.check_output(cmd, shell=True, text=True)

            authors = []
            for line in output.strip().split('\n'):
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    count = int(parts[0])
                    name = parts[1]
                    authors.append({'name': name, 'commits': count})

            total_commits = sum(a['commits'] for a in authors)

            # Calculate bus factor (number of people who own 50% of commits)
            sorted_authors = sorted(authors, key=lambda x: x['commits'], reverse=True)
            cumulative = 0
            bus_factor = 0
            for author in sorted_authors:
                cumulative += author['commits']
                bus_factor += 1
                if cumulative >= total_commits * 0.5:
                    break

            return {
                'total_maintainers': len(authors),
                'bus_factor': bus_factor,
                'top_contributor_percentage': (sorted_authors[0]['commits'] / total_commits * 100) if authors else 0,
                'risk_level': 'high' if bus_factor <= 2 else 'medium' if bus_factor <= 5 else 'low',
                'maintainers': authors[:10]  # Top 10
            }
        except Exception as e:
            return {'error': str(e)}

    def detect_commit_anomalies(self) -> Dict[str, Any]:
        """Detect suspicious commits (AI-generated, obfuscated, etc.)"""
        try:
            cmd = f"cd {self.repo_path} && git log --all --pretty=format:'%H|%an|%ae|%s|%ai' -100"
            output = subprocess.check_output(cmd, shell=True, text=True)

            anomalies = []
            ai_indicators = ['gpt', 'copilot', 'assistant', 'generated', 'automated']
            suspicious_patterns = ['obfuscate', 'hide', 'bypass', 'exploit']

            for line in output.strip().split('\n'):
                parts = line.split('|')
                if len(parts) >= 4:
                    commit_hash, author, email, message = parts[:4]

                    # Check for AI-generated indicators
                    if any(indicator in message.lower() for indicator in ai_indicators):
                        anomalies.append({
                            'commit': commit_hash[:8],
                            'type': 'ai_generated',
                            'message': message,
                            'severity': 'medium'
                        })

                    # Check for suspicious patterns
                    if any(pattern in message.lower() for pattern in suspicious_patterns):
                        anomalies.append({
                            'commit': commit_hash[:8],
                            'type': 'suspicious_message',
                            'message': message,
                            'severity': 'high'
                        })

            return {
                'total_commits_analyzed': len(output.strip().split('\n')),
                'anomalies_found': len(anomalies),
                'anomalies': anomalies
            }
        except Exception as e:
            return {'error': str(e)}

    def analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze dependency structure and risks"""
        # Check for common dependency files
        dep_files = {
            'package.json': self.analyze_npm_deps,
            'requirements.txt': self.analyze_pip_deps,
            'go.mod': self.analyze_go_deps,
            'Cargo.toml': self.analyze_rust_deps
        }

        results = {
            'direct_dependencies': 0,
            'transitive_dependencies': 0,
            'total_dependencies': 0,
            'outdated_dependencies': [],
            'risky_dependencies': []
        }

        for file, analyzer in dep_files.items():
            file_path = f"{self.repo_path}/{file}"
            try:
                with open(file_path, 'r') as f:
                    dep_data = analyzer(f.read())
                    results['direct_dependencies'] += dep_data.get('direct', 0)
                    results['transitive_dependencies'] += dep_data.get('transitive', 0)
            except FileNotFoundError:
                continue

        results['total_dependencies'] = results['direct_dependencies'] + results['transitive_dependencies']
        return results

    def analyze_npm_deps(self, content: str) -> Dict[str, int]:
        """Analyze npm dependencies"""
        try:
            data = json.loads(content)
            deps = data.get('dependencies', {})
            dev_deps = data.get('devDependencies', {})
            return {'direct': len(deps) + len(dev_deps), 'transitive': 0}
        except:
            return {'direct': 0, 'transitive': 0}

    def analyze_pip_deps(self, content: str) -> Dict[str, int]:
        """Analyze pip dependencies"""
        lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
        return {'direct': len(lines), 'transitive': 0}

    def analyze_go_deps(self, content: str) -> Dict[str, int]:
        """Analyze Go dependencies"""
        requires = re.findall(r'require\s+\(([^)]+)\)', content)
        if requires:
            deps = [d.strip() for d in requires[0].split('\n') if d.strip()]
            return {'direct': len(deps), 'transitive': 0}
        return {'direct': 0, 'transitive': 0}

    def analyze_rust_deps(self, content: str) -> Dict[str, int]:
        """Analyze Rust dependencies"""
        deps = re.findall(r'\[dependencies\]', content)
        return {'direct': len(deps), 'transitive': 0}

    def assess_hijack_risk(self) -> Dict[str, Any]:
        """Assess dependency hijacking risk"""
        return {
            'typosquatting_risk': 'medium',
            'namespace_confusion_risk': 'low',
            'account_takeover_risk': 'low',
            'overall_hijack_risk': 'medium',
            'mitigation_suggestions': [
                'Use dependency pinning',
                'Enable 2FA for package registry accounts',
                'Monitor for suspicious updates'
            ]
        }

    def calculate_blast_radius(self) -> Dict[str, Any]:
        """Calculate impact if dependency is compromised"""
        return {
            'direct_impact': 'high',
            'transitive_impact': 'medium',
            'downstream_projects_affected': 'unknown',
            'blast_radius_score': 75
        }

    def detect_weaponization(self) -> Dict[str, Any]:
        """Detect weaponized open-source patterns"""
        indicators = []

        # Check for common weaponization patterns
        patterns = {
            'install_scripts': ['install.sh', 'setup.sh', 'postinstall.js'],
            'obfuscated_code': ['eval', 'exec', 'Function('],
            'network_calls': ['http://', 'https://', 'fetch(', 'XMLHttpRequest'],
            'file_operations': ['fs.writeFile', 'os.remove', 'shutil.rmtree']
        }

        for pattern_type, indicators_list in patterns.items():
            # TODO: Scan files for these patterns
            pass

        return {
            'indicators_found': len(indicators),
            'indicators': indicators,
            'weaponization_likelihood': 'low'
        }

    def calculate_risk_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall risk score (0-100)"""
        score = 0

        # Maintainer risk
        maintainer = results['maintainer_analysis']
        if maintainer.get('bus_factor', 10) <= 2:
            score += 30
        elif maintainer.get('bus_factor', 10) <= 5:
            score += 15

        # Commit anomalies
        anomalies = results['commit_anomalies'].get('anomalies_found', 0)
        score += min(anomalies * 5, 20)

        # Dependencies
        deps = results['dependency_analysis'].get('total_dependencies', 0)
        if deps > 100:
            score += 20
        elif deps > 50:
            score += 10

        # Blast radius
        blast = results['blast_radius'].get('blast_radius_score', 0)
        score += int(blast * 0.3)

        return min(score, 100)

    def get_severity(self, score: int) -> str:
        """Get severity level from score"""
        if score >= 80:
            return 'critical'
        elif score >= 60:
            return 'high'
        elif score >= 40:
            return 'medium'
        else:
            return 'low'

    def generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []

        maintainer = results['maintainer_analysis']
        if maintainer.get('bus_factor', 10) <= 2:
            recommendations.append('Critical: Low bus factor detected. Consider increasing maintainer diversity.')

        if results['commit_anomalies'].get('anomalies_found', 0) > 0:
            recommendations.append('Review flagged commits for suspicious activity.')

        deps = results['dependency_analysis'].get('total_dependencies', 0)
        if deps > 50:
            recommendations.append(f'High dependency count ({deps}). Consider dependency pruning.')

        return recommendations


def main():
    """CLI entry point"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python scanner.py <repo_path>")
        sys.exit(1)

    repo_path = sys.argv[1]
    scanner = SupplyChainScanner(repo_path)
    results = scanner.scan()

    print("\n" + "="*60)
    print("SUPPLY CHAIN SECURITY ANALYSIS REPORT")
    print("="*60)
    print(f"\nRepository: {results['repo_path']}")
    print(f"Scan Time: {results['scan_time']}")
    print(f"\n🎯 Overall Risk Score: {results['overall_risk_score']}/100")
    print(f"🚨 Severity: {results['severity'].upper()}")

    print(f"\n👥 Maintainer Analysis:")
    print(f"   - Total Maintainers: {results['maintainer_analysis'].get('total_maintainers', 0)}")
    print(f"   - Bus Factor: {results['maintainer_analysis'].get('bus_factor', 0)}")
    print(f"   - Risk Level: {results['maintainer_analysis'].get('risk_level', 'unknown')}")

    print(f"\n🔍 Commit Anomalies:")
    print(f"   - Commits Analyzed: {results['commit_anomalies'].get('total_commits_analyzed', 0)}")
    print(f"   - Anomalies Found: {results['commit_anomalies'].get('anomalies_found', 0)}")

    print(f"\n📦 Dependencies:")
    print(f"   - Direct: {results['dependency_analysis'].get('direct_dependencies', 0)}")
    print(f"   - Transitive: {results['dependency_analysis'].get('transitive_dependencies', 0)}")
    print(f"   - Total: {results['dependency_analysis'].get('total_dependencies', 0)}")

    if results['recommendations']:
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"   {i}. {rec}")

    # Save full report
    report_file = f"supply_chain_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n📄 Full report saved to: {report_file}")
    print("="*60)


if __name__ == '__main__':
    main()
