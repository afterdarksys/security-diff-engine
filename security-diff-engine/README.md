# Security Diff Review

A dependency-free, diff-aware security scanner for Python, shell, Terraform, Ansible, and binary Git blobs. This is a heuristic tool, not a claim that it can prove exploitability: each result contains a rule ID, severity, changed file, exact line, evidence, and remediation.

    python3 differ.py /path/to/repo
    python3 differ.py /path/to/repo main HEAD --fail-on high
    python3 differ.py /path/to/repo --cached --fail-on high
    python3 differ.py /path/to/repo --cached --format yaml --output report.yaml
    python3 differ.py /path/to/repo main HEAD --format toml

It prints JSON and creates no files unless an output path is supplied. Exit status: 0 for success, 1 for a matched fail threshold, and 2 for operational/configuration errors.

Requirements: Python 3.9+ and Git. It runs without a Docker daemon or third-party Python package. Every report includes the scanner version, policy SHA-256, scan limits, and limitations so CI systems can retain auditable evidence.

To avoid duplicating credentials in CI artifacts, evidence is redacted for secret and private-key findings. Protect reports as internal security records because other evidence may still identify sensitive code paths.

Install a staged-change hook with the install-hook option. Existing hooks are never replaced without the force option.

The default policy detects common dangerous patterns: Python dynamic execution, deserialization and disabled TLS verification; shell eval, remote pipe-to-shell, recursive root deletion and broad permissions; Terraform public CIDRs/ACLs, disabled TLS and inline secrets; and Ansible shell tasks, ignored failures, disabled validation and broad modes. It detects private-key and AWS-key material in every text file.

Binary changes are compared directly from Git blobs and appear in the `binary_changes` report field. The scanner identifies ELF, PE, Mach-O, WebAssembly, Java classes, libraries, archives, operating-system packages (DEB, RPM, APK, MSI, DMG, PKG, AppImage, CAB, and ISO), Docker/OCI image archives, databases, PDFs, images, audio/video, and common scientific/columnar data formats by magic bytes or extension. Docker and OCI image tar layouts are identified from their manifest members without extracting them. SHA-256 is streamed for every binary, avoiding whole-image buffering; blobs up to 2 MiB additionally report an exact changed byte range. Changed executables and container images produce a high-severity review finding; other binary data changes produce a low-severity finding. Git LFS pointers produce a high-severity finding because the actual artifact must be retrieved and scanned separately. This is provenance-aware binary review, not disassembly, vulnerability analysis of archive contents, malware detection, or semantic reverse engineering.

Rules scan only added lines; deleted authentication protection is reported for review and never offsets vulnerability findings. JSON is the default. YAML and TOML are dependency-free renderings of the same schema, intended for CI artifacts and pipeline adapters. Use dedicated SAST, IaC, and secret scanners alongside this utility for production enforcement.

    PYTHONPYCACHEPREFIX=/tmp/security-diff-pycache python3 -m unittest -v
