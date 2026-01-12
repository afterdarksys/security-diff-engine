# Python Package Publishing Guide

Complete guide to publishing your Python libraries to PyPI with automation.

---

## Quick Start

### 1. One-Time Setup (5 minutes)

#### A. Create PyPI Accounts

1. **TestPyPI** (for testing):
   - Visit: https://test.pypi.org/account/register/
   - Create account and verify email

2. **PyPI** (production):
   - Visit: https://pypi.org/account/register/
   - Create account and verify email

#### B. Generate API Tokens

**TestPyPI:**
1. Go to: https://test.pypi.org/manage/account/token/
2. Click "Add API token"
3. Name: "Local Publishing" (or any name)
4. Scope: "Entire account"
5. Copy the token (starts with `pypi-`)

**PyPI:**
1. Go to: https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Name: "Local Publishing"
4. Scope: "Entire account"
5. Copy the token

#### C. Store Tokens Securely (MacOS)

```bash
# Store TestPyPI token
python3 -m keyring set https://test.pypi.org/legacy/ __token__
# Paste your TestPyPI token when prompted

# Store PyPI token
python3 -m keyring set https://upload.pypi.org/legacy/ __token__
# Paste your PyPI token when prompted
```

**Alternative: Use ~/.pypirc file**

```bash
cat > ~/.pypirc <<EOF
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_PYPI_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TESTPYPI_TOKEN_HERE
EOF

chmod 600 ~/.pypirc
```

---

## Publishing Methods

### Method 1: Quick Publish Script (Recommended)

Use the universal publish script for any Python package:

```bash
# Copy the script to your package directory
cp /path/to/publish-python-package.sh .

# Make it executable
chmod +x publish-python-package.sh

# Test publish (to TestPyPI)
./publish-python-package.sh test

# Production publish (to PyPI)
./publish-python-package.sh prod 1.0.0
```

**What it does:**
- ✅ Cleans old builds
- ✅ Runs tests (if available)
- ✅ Updates version numbers
- ✅ Builds package
- ✅ Validates package
- ✅ Publishes to PyPI
- ✅ Creates git tags

### Method 2: Manual Publishing

```bash
# 1. Clean previous builds
rm -rf dist/ build/ *.egg-info/

# 2. Build package
python3 -m build

# 3. Check package
python3 -m twine check dist/*

# 4. Upload to TestPyPI (test first!)
python3 -m twine upload --repository testpypi dist/*

# 5. Test install
pip install --index-url https://test.pypi.org/simple/ your-package-name

# 6. Upload to PyPI (production)
python3 -m twine upload dist/*
```

### Method 3: GitHub Actions (Automated)

Set up automated publishing on release:

```bash
# 1. Copy workflow template
mkdir -p .github/workflows
cp /path/to/publish-template.yml .github/workflows/publish.yml

# 2. Add secrets to GitHub repo
# Go to: Settings → Secrets and variables → Actions
# Add:
#   - PYPI_API_TOKEN (your PyPI token)
#   - TEST_PYPI_API_TOKEN (your TestPyPI token)

# 3. Create a release
git tag v1.0.0
git push --tags
# Or create release via GitHub UI
```

**Triggers:**
- ✅ Automatically publishes on GitHub release
- ✅ Manual trigger via Actions tab
- ✅ Choose test or production environment

---

## Package Requirements

### Minimum Required Files

Your package needs these files:

```
your-package/
├── pyproject.toml          # Package metadata
├── your_package/           # Source code directory
│   ├── __init__.py        # Package initialization
│   └── ...                # Your modules
├── README.md              # Documentation
├── LICENSE               # License file
└── tests/                # Tests (optional but recommended)
```

### Sample pyproject.toml

```toml
[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "your-package-name"
version = "0.1.0"
description = "Your package description"
authors = ["Your Name <you@example.com>"]
license = "MIT"
readme = "README.md"
homepage = "https://yourpackage.dev"
repository = "https://github.com/yourusername/your-package"
packages = [{include = "your_package"}]  # Important!

keywords = ["keyword1", "keyword2"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]

[tool.poetry.dependencies]
python = "^3.10"
# your dependencies here

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
black = "^23.11.0"
```

**Important:** The `packages = [{include = "your_package"}]` line is crucial!

---

## Publishing Workflow

### For New Packages

1. **Prepare package**
   ```bash
   # Ensure pyproject.toml is correct
   # Add README.md
   # Add LICENSE file
   ```

2. **Test locally**
   ```bash
   python3 -m build
   python3 -m twine check dist/*
   ```

3. **Publish to TestPyPI first**
   ```bash
   ./publish-python-package.sh test
   ```

4. **Test installation**
   ```bash
   pip install --index-url https://test.pypi.org/simple/ your-package
   python -c "import your_package; print(your_package.__version__)"
   ```

5. **Publish to production**
   ```bash
   ./publish-python-package.sh prod 0.1.0
   ```

### For Updates

1. **Update version**
   - In `pyproject.toml`: `version = "0.2.0"`
   - In `__init__.py`: `__version__ = "0.2.0"`

2. **Update changelog**
   ```bash
   # Add to CHANGELOG.md or README.md
   ```

3. **Test and publish**
   ```bash
   ./publish-python-package.sh test 0.2.0  # Test first
   ./publish-python-package.sh prod 0.2.0  # Then production
   ```

4. **Push to git**
   ```bash
   git push
   git push --tags
   ```

---

## Common Issues & Solutions

### Issue: "No file/folder found for package"

**Problem:** Poetry can't find your package.

**Solution:** Add to `pyproject.toml`:
```toml
packages = [{include = "your_package_name"}]
```

### Issue: "Invalid or non-existent authentication"

**Problem:** API token not configured.

**Solution:** Run keyring setup again:
```bash
python3 -m keyring set https://upload.pypi.org/legacy/ __token__
# Paste your token
```

### Issue: "Package name already taken"

**Problem:** Someone else owns that name on PyPI.

**Solution:** Choose a unique name. Common patterns:
- `yourcompany-packagename`
- `packagename-extension`
- Check availability: https://pypi.org/project/your-name/

### Issue: "Upload failed - file already exists"

**Problem:** Version already published (can't overwrite).

**Solution:** Increment version number and publish again.

### Issue: Package builds but dependencies missing

**Problem:** Dependencies not specified correctly.

**Solution:** Ensure all dependencies in `[tool.poetry.dependencies]` section.

---

## Best Practices

### Versioning

Use Semantic Versioning (SemVer):
- `MAJOR.MINOR.PATCH`
- `1.0.0` → First stable release
- `1.0.1` → Bug fixes
- `1.1.0` → New features (backward compatible)
- `2.0.0` → Breaking changes

### Pre-releases

For alpha/beta versions:
- `0.1.0a1` - Alpha
- `0.1.0b1` - Beta
- `0.1.0rc1` - Release candidate

### Testing

Always test before production:

```bash
# 1. Test locally
pytest

# 2. Test build
python3 -m build
python3 -m twine check dist/*

# 3. Test on TestPyPI
./publish-python-package.sh test

# 4. Install and test
pip install --index-url https://test.pypi.org/simple/ your-package
```

### Documentation

Include in every package:
- ✅ Clear README.md with usage examples
- ✅ CHANGELOG.md tracking all changes
- ✅ LICENSE file
- ✅ API documentation (docstrings)

### Security

- ✅ Use API tokens (never passwords)
- ✅ Store tokens in keyring or secrets
- ✅ Never commit tokens to git
- ✅ Use `.gitignore` for sensitive files

---

## Automation Templates

### Makefile for Publishing

```makefile
.PHONY: clean build check test-publish publish

clean:
	rm -rf dist/ build/ *.egg-info/

build: clean
	python3 -m build

check: build
	python3 -m twine check dist/*

test-publish: check
	python3 -m twine upload --repository testpypi dist/*

publish: check
	@echo "⚠️  Publishing to PRODUCTION PyPI"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		python3 -m twine upload dist/*; \
	fi
```

Usage:
```bash
make test-publish  # Test on TestPyPI
make publish       # Publish to PyPI
```

### Pre-commit Hook

`.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Ensure version is updated before commit

VERSION_FILE="pyproject.toml"
if git diff --cached --name-only | grep -q "$VERSION_FILE"; then
    echo "✓ Version file updated"
else
    echo "⚠️  Remember to update version in pyproject.toml"
fi
```

---

## Publishing Checklist

Before every release:

- [ ] Tests passing (`pytest`)
- [ ] Version bumped in `pyproject.toml`
- [ ] Version bumped in `__init__.py`
- [ ] CHANGELOG.md updated
- [ ] README.md up to date
- [ ] All changes committed
- [ ] Build succeeds (`python3 -m build`)
- [ ] Package check passes (`twine check dist/*`)
- [ ] Tested on TestPyPI
- [ ] Ready for production

---

## Resources

### Official Documentation
- PyPI: https://pypi.org/
- TestPyPI: https://test.pypi.org/
- Packaging Guide: https://packaging.python.org/
- Twine: https://twine.readthedocs.io/

### Tools
- Poetry: https://python-poetry.org/
- Build: https://pypa-build.readthedocs.io/
- Twine: https://twine.readthedocs.io/

### Community
- Python Packaging Discord: https://discord.gg/python-packaging
- PyPA Discussion: https://discuss.python.org/c/packaging/

---

## Quick Reference

```bash
# Setup (one time)
pip install --user build twine
python3 -m keyring set https://upload.pypi.org/legacy/ __token__

# Publish workflow
./publish-python-package.sh test     # Test first
./publish-python-package.sh prod 1.0.0  # Production

# Manual commands
python3 -m build                     # Build
python3 -m twine check dist/*        # Check
python3 -m twine upload dist/*       # Upload

# GitHub Actions
git tag v1.0.0                       # Tag release
git push --tags                      # Push tag
```

---

**Need help?** Check the [Python Packaging User Guide](https://packaging.python.org/) or open an issue.

**Ready to publish?** Run `./publish-python-package.sh test` to get started!
