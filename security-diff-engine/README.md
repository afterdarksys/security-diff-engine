# Security Diff Review

A dependency-free, diff-aware security scanner for Python, shell, Terraform, and Ansible. This is a heuristic tool, not a claim that it can prove exploitability: each result contains a rule ID, severity, changed file, exact line, evidence, and remediation.

    python3 differ.py /path/to/repo
    python3 differ.py /path/to/repo main HEAD --fail-on high
    python3 differ.py /path/to/repo --cached --fail-on high
    python3 differ.py /path/to/repo --cached --format yaml --output report.yaml
    python3 differ.py /path/to/repo main HEAD --format toml

It prints JSON and creates no files unless an output path is supplied. Exit status: 0 for success, 1 for a matched fail threshold, and 2 for operational/configuration errors.

Install a staged-change hook with the install-hook option. Existing hooks are never replaced without the force option.

The default policy detects common dangerous patterns: Python dynamic execution, deserialization and disabled TLS verification; shell eval, remote pipe-to-shell, recursive root deletion and broad permissions; Terraform public CIDRs/ACLs, disabled TLS and inline secrets; and Ansible shell tasks, ignored failures, disabled validation and broad modes. It detects private-key and AWS-key material in every text file.

Rules scan only added lines; deleted authentication protection is reported for review and never offsets vulnerability findings. JSON is the default. YAML and TOML are dependency-free renderings of the same schema, intended for CI artifacts and pipeline adapters. Use dedicated SAST, IaC, and secret scanners alongside this utility for production enforcement.

    PYTHONPYCACHEPREFIX=/tmp/security-diff-pycache python3 -m unittest -v
