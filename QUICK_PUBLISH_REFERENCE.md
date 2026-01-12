# Package Publishing - Quick Reference Card

Keep this handy for quick publishing Python and npm packages!

---

## 🐍 Python (PyPI) Publishing

### First Time Setup (Once)

```bash
# 1. Install tools
pip3 install --user build twine keyring

# 2. Run setup wizard
cd /Users/ryan/development/afterdark-enhancements
./setup-pypi-credentials.sh
```

**You'll need:**
- TestPyPI account: https://test.pypi.org/account/register/
- PyPI account: https://pypi.org/account/register/
- API tokens from both (create at /manage/account/token/)

### Publishing Any Python Package (3 Commands)

```bash
# 1. Go to your package directory
cd /path/to/your-package

# 2. Copy the publish script (first time only)
cp /Users/ryan/development/afterdark-enhancements/publish-python-package.sh .

# 3. Publish!
./publish-python-package.sh test          # Test on TestPyPI first
./publish-python-package.sh prod 1.0.0    # Production release
```

### Common Python Commands

**Test First (Always!):**
```bash
./publish-python-package.sh test
```

**Publish New Package:**
```bash
./publish-python-package.sh prod 0.1.0
```

**Publish Update:**
```bash
./publish-python-package.sh prod 0.2.0
```

**Manual Build Only:**
```bash
python3 -m build
python3 -m twine check dist/*
```

---

## 📦 npm (Node.js) Publishing

### First Time Setup (Once)

```bash
# 1. Install Node.js (if not installed)
brew install node  # macOS
# OR: Download from https://nodejs.org/

# 2. Run setup wizard
cd /Users/ryan/development/afterdark-enhancements
./setup-npm-credentials.sh
```

**You'll need:**
- npm account: https://www.npmjs.com/signup
- Verify your email

### Publishing Any npm Package (3 Commands)

```bash
# 1. Go to your package directory
cd /path/to/your-package

# 2. Copy the publish script (first time only)
cp /Users/ryan/development/afterdark-enhancements/publish-npm-package.sh .

# 3. Publish!
./publish-npm-package.sh test          # Test with 'next' tag
./publish-npm-package.sh prod 1.0.0    # Production release
```

### Common npm Commands

**Test First (Always!):**
```bash
./publish-npm-package.sh test
```

**Publish New Package:**
```bash
./publish-npm-package.sh prod 1.0.0
```

**Publish Update:**
```bash
./publish-npm-package.sh prod 1.1.0
```

**Manual Build Only:**
```bash
npm run build
npm pack
npm publish --dry-run
```

---

## ✅ Checklist Before Publishing

### Python Packages
- [ ] Tests pass (`pytest` or similar)
- [ ] Version updated in `pyproject.toml`
- [ ] Version updated in `__init__.py`
- [ ] README updated
- [ ] Changes committed to git
- [ ] Test on TestPyPI first!

### npm Packages
- [ ] Tests pass (`npm test`)
- [ ] Version updated in `package.json`
- [ ] README updated
- [ ] Changes committed to git
- [ ] `npm pack` reviewed
- [ ] `npm publish --dry-run` successful

---

## 📁 Package Requirements

### Python Package Structure
```
your-package/
├── pyproject.toml      # With: packages = [{include = "your_pkg"}]
├── your_pkg/
│   ├── __init__.py    # With: __version__ = "0.1.0"
│   └── ...
├── README.md
└── LICENSE
```

### npm Package Structure
```
your-package/
├── package.json        # With: name, version, main, files
├── dist/              # Built files
│   └── index.js
├── src/               # Source (excluded from package)
├── README.md
└── LICENSE
```

---

## 🔧 Troubleshooting

### Python Issues

**"No file/folder found for package"**
→ Add to pyproject.toml: `packages = [{include = "your_package"}]`

**"Invalid authentication"**
→ Run: `./setup-pypi-credentials.sh`

**"Package already exists"**
→ Increment version number

**"File already exists on PyPI"**
→ Can't overwrite - must increment version

### npm Issues

**"Not logged in"**
→ Run: `npm login` or `./setup-npm-credentials.sh`

**"Package name taken"**
→ Use scope: `@yourusername/package-name` or choose different name

**"Version already published"**
→ Increment version: `npm version patch`

**"Missing files in package"**
→ Check `package.json` `files` field and `.npmignore`

---

## 🔗 URLs

### Python
- **TestPyPI**: https://test.pypi.org/
- **PyPI**: https://pypi.org/
- **Full Guide**: PYTHON_PUBLISHING_GUIDE.md

### npm
- **npm Registry**: https://www.npmjs.com/
- **npm Docs**: https://docs.npmjs.com/
- **Full Guide**: NPM_PUBLISHING_GUIDE.md

---

## 📝 Examples

### Python: afterdark-llm-firewall

```bash
cd /Users/ryan/development/afterdark-enhancements/llm-security-firewall
./publish-python-package.sh test
pip install --index-url https://test.pypi.org/simple/ afterdark-llm-firewall
./publish-python-package.sh prod 0.1.0
git push --tags
```

### npm: Your npm Package

```bash
cd /path/to/your-npm-package
./publish-npm-package.sh test
npm install your-package@next  # Test the next tag version
./publish-npm-package.sh prod 1.0.0
git push --tags
```

---

## 🚀 Quick Start Commands

### Python
```bash
# Copy script
cp /Users/ryan/development/afterdark-enhancements/publish-python-package.sh .

# Test
./publish-python-package.sh test

# Publish
./publish-python-package.sh prod 0.1.0
```

### npm
```bash
# Copy script
cp /Users/ryan/development/afterdark-enhancements/publish-npm-package.sh .

# Test
./publish-npm-package.sh test

# Publish
./publish-npm-package.sh prod 1.0.0
```

---

## 💡 Pro Tips

**Python:**
- Always test on TestPyPI first - it's free practice!
- Use semantic versioning: MAJOR.MINOR.PATCH
- Keep dependencies minimal

**npm:**
- Use `npm pack` to inspect package contents
- Test with `npm publish --dry-run` first
- Enable 2FA for security
- Use `--tag next` for beta releases

---

**One system, infinite packages!** 🎸🔥

📚 **Full Documentation:**
- Python: `PYTHON_PUBLISHING_GUIDE.md`
- npm: `NPM_PUBLISHING_GUIDE.md`
- System Overview: `PUBLISHING_SYSTEM_README.md`
