# Security and regulated-use boundary

Security Diff Review is a change-review control. It identifies risky text patterns and records binary or container artifact provenance; it is not an endpoint-protection, malware-analysis, container-vulnerability, SBOM, signing, or compliance-certification product.

For a regulated release process, run it in CI against a protected branch and retain the JSON report with the associated commit SHA, build record, reviewer decision, and policy file. Treat high and critical findings as release gates. The report's `scan` section records the scanner version, SHA-256 of the policy, limits, and known limitations for that evidence trail.

Use defense in depth for deployable artifacts:

- Retrieve and inspect Git LFS artifacts separately; an LFS pointer is intentionally a high-severity finding because it is not the artifact.
- Verify container/image signatures and attestations, generate and review an SBOM, and use an approved vulnerability scanner before deployment.
- Restrict CI credentials, protect policy changes with code review, and store reports in access-controlled, retention-managed systems.
- Do not place PHI, credentials, private keys, or unencrypted regulated data in source control or scan reports.

The project does not claim HIPAA, FedRAMP, PCI DSS, SOC 2, or any other certification. Each organization remains responsible for its risk assessment, control implementation, evidence retention, and legal/compliance review.
