# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A grab-bag incubator of After Dark Systems security tool prototypes — not a single application. There is no repo-wide build system, package manifest, or test runner; each tool is a standalone Python script (stdlib-only in the cases inspected) run directly with `python3`. `PROJECT_BUILD_STATUS.md` is the honest inventory: it distinguishes shipped products from partial tools and stubs — read it before assuming anything here is production-ready.

## Current state (per PROJECT_BUILD_STATUS.md and inspection)

- **Partial/working prototypes** (single-file Python, ~200-450 lines each):
  - `ai-supply-chain-scanner/` — endpoint SCRM/vulnerability scanner (`scanner.py`): SBOM analysis, EOL tracking, SQLite-backed (`local.db`); sample SBOMs and report JSON included
  - `api-misuse-detector/` — `detector.py` plus a Flask middleware (`middleware.py`, `flask_example.py`, `test_flask_middleware.py`) and sample-traffic generator
  - `cloud-attack-simulator/` — the most structured tool: `simulator.py` entry point, `core/` (engine, models, compliance, darkapi), `providers/` (aws, azure, gcp, oci, kubernetes), `policies/` (YAML attack policies)
  - `runtime-secrets-detector/`, `security-diff-engine/`, `threat-modeling-engine/`, `forensics-automation/` — smaller stubs/skeletons
- **Empty/ideas-only**: `models2go/`, `elastio-clone/`, `for-pm-portal/`
- **Shipped products** referenced by the status doc (llm-security-firewall, macos-supply-chain-monitor, ads-prompt-generator) were published to PyPI/GitHub and are not present as source directories here.

## Commands

There are no Makefiles, package.json, or requirements.txt anywhere in the repo. Run tools directly, e.g. `python3 ai-supply-chain-scanner/scanner.py --help`. Repo-root helper scripts exist for publishing/credentials (`publish-npm-package.sh`, `publish-python-package.sh`, `setup-npm-credentials.sh`, `setup-pypi-credentials.sh`) and diagram generation (`generate_diagram.py`).

## Architecture notes

`ADS_OSX_SECURITY_SUITE.md` documents the intended macOS security suite architecture that these tools feed into: standalone CLI tools that each also run as local HTTP/JSON servers (ports 9001+) implementing a standard interface (`/health`, `/info`, `/data`, `/scan`, `/stream` SSE), unified by a native Wails/Go GUI console. Tools are language-agnostic; the JSON API is the contract. New tools added here should follow that pattern.

Other planning/idea material: `mdfiles/`, `patches/`, `updated_*_product_ideas*.txt`, `DIAGRAM_PROMPTS.md`, `OSX_GO_GUI.md`.
