# Complete NPM Package Publishing Guide

**Your Universal npm Publishing System**

This guide covers everything you need to publish npm packages professionally.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [System Overview](#system-overview)
3. [Prerequisites](#prerequisites)
4. [Initial Setup (One-Time)](#initial-setup-one-time)
5. [Publishing Methods](#publishing-methods)
6. [Package Configuration](#package-configuration)
7. [Version Management](#version-management)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)
10. [Security](#security)
11. [CI/CD Integration](#cicd-integration)

---

## Quick Start

**Never published before?**
```bash
# 1. One-time setup
./setup-npm-credentials.sh

# 2. Test publish (with 'next' tag)
./publish-npm-package.sh test

# 3. Production publish
./publish-npm-package.sh prod 1.0.0
```

**Already set up?**
```bash
./publish-npm-package.sh prod 1.0.0
```

---

## System Overview

### What You Have

This publishing system includes:

1. **`publish-npm-package.sh`** - Universal publishing script
   - Works with ANY npm package
   - Handles versioning, testing, building
   - Supports test (next tag) and prod (latest tag) modes
   - Creates tarballs and validates before publishing

2. **`setup-npm-credentials.sh`** - One-time setup wizard
   - Guides through npm account setup
   - Handles npm login
   - Verifies authentication

3. **`.github/workflows/npm-publish-template.yml`** - CI/CD automation
   - Auto-publishes on GitHub releases
   - Manual workflow dispatch
   - Integrated with GitHub Actions

4. **This guide** - Complete documentation

### How It Works

```
┌─────────────────────────────────────────────────┐
│  1. Run publish script                          │
│     ./publish-npm-package.sh prod 1.0.0        │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  2. Script validates environment                │
│     - Checks npm login                          │
│     - Verifies package.json exists              │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  3. Updates version (if specified)              │
│     npm version 1.0.0 --no-git-tag-version     │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  4. Runs tests and builds                       │
│     npm test && npm run build                   │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  5. Creates and validates tarball               │
│     npm pack && npm publish --dry-run           │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  6. Publishes to npm                            │
│     npm publish (with appropriate tag)          │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  7. Creates git tag (prod mode only)            │
│     git tag -a v1.0.0                           │
└─────────────────────────────────────────────────┘
```

---

## Prerequisites

### Required Software

1. **Node.js and npm** (v16+ recommended)
   ```bash
   # Check if installed
   node --version
   npm --version

   # Install (macOS)
   brew install node

   # Install (Linux)
   sudo apt-get install nodejs npm
   ```

2. **Git** (for version tagging)
   ```bash
   git --version
   ```

3. **npm Account**
   - Create at: https://www.npmjs.com/signup
   - Verify your email

### Optional But Recommended

1. **Two-Factor Authentication** (2FA)
   - Visit: https://www.npmjs.com/settings/YOUR_USERNAME/tfa
   - Enable for better security

2. **Automation Token** (for CI/CD)
   - Visit: https://www.npmjs.com/settings/YOUR_USERNAME/tokens
   - Create "Automation" token

---

## Initial Setup (One-Time)

### Method 1: Automated Setup (Recommended)

Run the setup wizard:
```bash
./setup-npm-credentials.sh
```

This will:
- ✓ Check npm installation
- ✓ Guide through account setup
- ✓ Handle npm login
- ✓ Verify authentication
- ✓ Provide 2FA setup instructions

### Method 2: Manual Setup

1. **Install Node.js/npm** (if not already installed)
   ```bash
   # macOS
   brew install node

   # Linux
   sudo apt-get install nodejs npm

   # Verify
   node --version
   npm --version
   ```

2. **Create npm Account**
   - Visit: https://www.npmjs.com/signup
   - Complete registration
   - Verify email

3. **Login to npm**
   ```bash
   npm login
   # Enter: username, password, email

   # Verify
   npm whoami
   ```

4. **Enable 2FA** (optional but recommended)
   - Visit: https://www.npmjs.com/settings/YOUR_USERNAME/tfa
   - Follow setup instructions

---

## Publishing Methods

You have three ways to publish:

### Method 1: Using the Publish Script (Recommended)

**Test Publish** (with 'next' tag - users must explicitly install):
```bash
./publish-npm-package.sh test
```

**Production Publish** (with 'latest' tag - default install):
```bash
./publish-npm-package.sh prod 1.0.0
```

The script automatically:
- ✓ Cleans old builds
- ✓ Runs tests (if available)
- ✓ Updates version
- ✓ Builds package
- ✓ Creates tarball
- ✓ Validates with dry-run
- ✓ Publishes to npm
- ✓ Creates git tags (prod mode)

### Method 2: Manual Publishing

**Step-by-step manual process:**

```bash
# 1. Clean previous builds
rm -rf dist/ build/ *.tgz

# 2. Run tests
npm test

# 3. Update version
npm version 1.0.0 --no-git-tag-version

# 4. Build
npm run build

# 5. Create tarball
npm pack

# 6. Dry run
npm publish --dry-run

# 7. Publish (test mode with 'next' tag)
npm publish --tag next

# OR: Publish (prod mode with 'latest' tag)
npm publish

# 8. Create git tag (optional)
git tag -a v1.0.0 -m "Release version 1.0.0"
git push && git push --tags
```

### Method 3: CI/CD (GitHub Actions)

**Automatic on release:**
1. Create a GitHub release
2. Workflow runs automatically
3. Publishes with 'latest' tag

**Manual trigger:**
1. Go to Actions → "Publish NPM Package"
2. Click "Run workflow"
3. Choose mode (test/prod) and version
4. Click "Run workflow"

See [CI/CD Integration](#cicd-integration) section for setup.

---

## Package Configuration

### package.json Requirements

Your `package.json` must include:

```json
{
  "name": "your-package-name",
  "version": "1.0.0",
  "description": "Your package description",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "files": [
    "dist/",
    "README.md",
    "LICENSE"
  ],
  "scripts": {
    "build": "tsc",
    "test": "jest",
    "prepublishOnly": "npm run build"
  },
  "keywords": ["keyword1", "keyword2"],
  "author": "Your Name <email@example.com>",
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/username/repo"
  },
  "bugs": {
    "url": "https://github.com/username/repo/issues"
  },
  "homepage": "https://github.com/username/repo#readme"
}
```

### Key Fields Explained

1. **`name`** - Package name on npm
   - Must be unique
   - Use scope for namespacing: `@yourscope/package-name`
   - Check availability: `npm search package-name`

2. **`version`** - Semantic version (semver)
   - Format: MAJOR.MINOR.PATCH
   - Example: `1.0.0`

3. **`files`** - Files to include in package
   - Only listed files/directories are published
   - Always include: dist/, README.md, LICENSE
   - Exclude dev files

4. **`main`** - Entry point for CommonJS
   - Usually: `dist/index.js`

5. **`types`** (TypeScript) - Type definitions
   - Usually: `dist/index.d.ts`

6. **`module`** (optional) - Entry point for ES modules
   - Usually: `dist/index.mjs`

7. **`exports`** (optional) - Modern entry points
   ```json
   "exports": {
     ".": {
       "require": "./dist/index.js",
       "import": "./dist/index.mjs",
       "types": "./dist/index.d.ts"
     }
   }
   ```

### .npmignore File

Create `.npmignore` to exclude files from package:

```
# Source files (if you ship dist/ only)
src/
*.ts
!*.d.ts

# Tests
tests/
__tests__/
*.test.js
*.spec.js

# Development
.git/
.github/
.vscode/
node_modules/

# Build artifacts
*.log
*.tgz

# Config files
.env
.env.*
tsconfig.json
jest.config.js
.eslintrc
.prettierrc
```

**Note:** Files in `.gitignore` are automatically excluded unless overridden in `.npmignore`.

### README.md

Your README should include:

```markdown
# Package Name

Brief description of your package.

## Installation

\`\`\`bash
npm install your-package-name
\`\`\`

## Usage

\`\`\`javascript
const yourPackage = require('your-package-name');

// Example usage
yourPackage.doSomething();
\`\`\`

## API

### functionName(param)

Description of function...

## License

MIT
```

### LICENSE File

Include a LICENSE file (MIT example):

```
MIT License

Copyright (c) 2026 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Version Management

### Semantic Versioning (semver)

Format: **MAJOR.MINOR.PATCH**

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes
- **MINOR** (1.0.0 → 1.1.0): New features (backward compatible)
- **PATCH** (1.0.0 → 1.0.1): Bug fixes

### Updating Versions

**Using npm version:**
```bash
# Patch (1.0.0 → 1.0.1)
npm version patch

# Minor (1.0.0 → 1.1.0)
npm version minor

# Major (1.0.0 → 2.0.0)
npm version major

# Specific version
npm version 1.2.3

# Pre-release versions
npm version 1.0.0-beta.1
npm version 1.0.0-alpha.2
```

**Using the publish script:**
```bash
# Specify version directly
./publish-npm-package.sh prod 1.2.3

# Or update manually first, then publish
npm version 1.2.3 --no-git-tag-version
./publish-npm-package.sh prod
```

### Pre-release Versions

For beta/alpha releases:

```bash
# Publish beta version
npm version 1.0.0-beta.1 --no-git-tag-version
./publish-npm-package.sh test

# Users install with:
npm install your-package@beta
# or
npm install your-package@1.0.0-beta.1
```

### Version Tags

npm uses tags to manage versions:

- **`latest`** - Default tag (prod releases)
- **`next`** - Beta/test releases
- **`beta`**, **`alpha`** - Pre-release versions
- Custom tags as needed

```bash
# Publish with specific tag
npm publish --tag beta

# Move tag to different version
npm dist-tag add your-package@1.0.1 latest

# View all tags
npm dist-tag ls your-package
```

---

## Troubleshooting

### Common Errors

#### 1. Not Logged In

**Error:**
```
npm ERR! need auth This command requires you to be logged in.
```

**Fix:**
```bash
npm login
# or
./setup-npm-credentials.sh
```

#### 2. Package Name Taken

**Error:**
```
npm ERR! 403 Forbidden - PUT https://registry.npmjs.org/package-name
npm ERR! 403 You do not have permission to publish "package-name".
```

**Fix:**
- Choose a different name
- Use a scope: `@yourusername/package-name`
- Check availability: `npm search package-name`

#### 3. Version Already Published

**Error:**
```
npm ERR! 403 Forbidden - PUT https://registry.npmjs.org/package-name
npm ERR! 403 You cannot publish over the previously published versions
```

**Fix:**
```bash
# Increment version
npm version patch  # or minor, or major
./publish-npm-package.sh prod
```

**Note:** You cannot overwrite published versions on npm.

#### 4. 2FA Token Required

**Error:**
```
npm ERR! code EOTP
npm ERR! This operation requires a one-time password.
```

**Fix:**
```bash
# Add OTP to publish command
npm publish --otp=123456

# Or temporarily disable 2FA for automation
# (not recommended for security)
```

#### 5. Missing Files in Package

**Error:**
Package installs but files are missing.

**Fix:**
1. Check `package.json` `files` field:
   ```json
   "files": ["dist/", "README.md", "LICENSE"]
   ```

2. Check `.npmignore` - make sure not excluding needed files

3. Test locally:
   ```bash
   npm pack
   tar -tzf your-package-1.0.0.tgz
   ```

#### 6. Build Fails

**Error:**
```
npm ERR! Failed at the build script
```

**Fix:**
```bash
# Run build manually to see full error
npm run build

# Check dependencies installed
npm install

# Verify Node version matches requirement
node --version
```

#### 7. Tests Fail

**Error:**
```
npm ERR! Test failed
```

**Fix:**
```bash
# Run tests manually
npm test

# Continue publishing anyway (if safe)
# Answer 'y' when script prompts
```

### Debug Commands

```bash
# Check npm configuration
npm config list

# Verify login
npm whoami

# Check package name availability
npm search package-name

# View package details
npm view your-package

# View package versions
npm view your-package versions

# Test package locally
npm pack
tar -tzf your-package-1.0.0.tgz

# Dry run publish
npm publish --dry-run

# View registry
npm config get registry
```

---

## Best Practices

### 1. Version Management

- ✓ Use semantic versioning
- ✓ Never delete published versions
- ✓ Use pre-release versions for testing
- ✓ Keep CHANGELOG.md updated

### 2. Package Quality

- ✓ Include comprehensive README
- ✓ Add LICENSE file
- ✓ Provide TypeScript types
- ✓ Include examples
- ✓ Write tests
- ✓ Document API

### 3. Package Size

- ✓ Exclude source files (ship only dist/)
- ✓ Exclude tests
- ✓ Exclude dev config files
- ✓ Use `.npmignore`
- ✓ Check size: `npm pack && ls -lh *.tgz`

### 4. Dependencies

- ✓ Minimize dependencies
- ✓ Use `dependencies` for runtime deps
- ✓ Use `devDependencies` for build/test tools
- ✓ Use `peerDependencies` for plugins
- ✓ Keep dependencies updated

### 5. Publishing

- ✓ Test locally before publishing
- ✓ Use `--tag next` for beta releases
- ✓ Never publish secrets or credentials
- ✓ Review `npm pack` contents
- ✓ Use `--dry-run` first
- ✓ Create git tags for releases

### 6. Security

- ✓ Enable 2FA on npm account
- ✓ Use automation tokens for CI/CD
- ✓ Never commit tokens to git
- ✓ Run `npm audit` regularly
- ✓ Keep dependencies updated
- ✓ Review package contents before publishing

### 7. Documentation

- ✓ Maintain comprehensive README
- ✓ Document all public APIs
- ✓ Provide usage examples
- ✓ Keep CHANGELOG.md
- ✓ Link to repository and issues

---

## Security

### Protecting npm Tokens

**For local development:**

npm stores credentials in `~/.npmrc`:
```
//registry.npmjs.org/:_authToken=npm_...
```

**For CI/CD:**

Use GitHub Secrets:
```yaml
# .github/workflows/publish.yml
env:
  NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

### Never Commit:

```bash
# Add to .gitignore
.npmrc
*.tgz
npm-debug.log
```

### Token Types

1. **Legacy Token** (avoid)
   - Never expires
   - Full access
   - Not recommended

2. **Granular Access Token** (recommended)
   - Limited scope
   - Expiration date
   - Can be revoked

3. **Automation Token** (for CI/CD)
   - Bypasses 2FA
   - Use only in CI/CD
   - Rotate regularly

### Enable 2FA

Visit: https://www.npmjs.com/settings/YOUR_USERNAME/tfa

Two modes:
1. **Authorization only** - 2FA for login only
2. **Authorization and Publishing** - 2FA for login and publishing (recommended)

### Security Checklist

Before publishing:

- [ ] No secrets in code
- [ ] No `.env` files in package
- [ ] No API keys or tokens
- [ ] No credentials
- [ ] Review all files in tarball
- [ ] Run `npm audit`
- [ ] Check for vulnerable dependencies

### Audit Commands

```bash
# Check for vulnerabilities
npm audit

# Fix vulnerabilities
npm audit fix

# Force fix (may break)
npm audit fix --force

# View package contents
npm pack
tar -tzf your-package-1.0.0.tgz
```

---

## CI/CD Integration

### GitHub Actions Setup

**1. Get npm Token:**

Visit: https://www.npmjs.com/settings/YOUR_USERNAME/tokens

- Click "Generate New Token"
- Choose "Automation" type
- Copy token (starts with `npm_...`)

**2. Add to GitHub Secrets:**

- Go to repo Settings → Secrets and variables → Actions
- Click "New repository secret"
- Name: `NPM_TOKEN`
- Value: [paste token]

**3. Copy workflow file:**

```bash
# Copy template to your package
cp .github/workflows/npm-publish-template.yml YOUR_PACKAGE/.github/workflows/publish.yml

# Commit and push
git add .github/
git commit -m "Add npm publishing workflow"
git push
```

**4. Usage:**

**Option A - Automatic (on release):**
```bash
# Create and push tag
git tag v1.0.0
git push --tags

# Create GitHub release
gh release create v1.0.0 --title "v1.0.0" --notes "Release notes"

# Workflow runs automatically
```

**Option B - Manual:**
1. Go to Actions → "Publish NPM Package"
2. Click "Run workflow"
3. Choose mode (test/prod)
4. Enter version (optional)
5. Click "Run workflow"

### Workflow Features

The workflow automatically:
- ✓ Sets up Node.js
- ✓ Installs dependencies
- ✓ Runs tests
- ✓ Builds package
- ✓ Updates version (if specified)
- ✓ Publishes to npm
- ✓ Provides summary

### Custom Workflows

Modify the workflow for your needs:

```yaml
# Use different Node version
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '20'  # Change version

# Add custom build steps
- name: Custom build
  run: |
    npm run lint
    npm run type-check
    npm run build

# Publish to multiple registries
- name: Publish to GitHub Packages
  run: npm publish --registry=https://npm.pkg.github.com
  env:
    NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Quick Reference

### Common Commands

```bash
# Setup (one-time)
./setup-npm-credentials.sh

# Publish to test (next tag)
./publish-npm-package.sh test

# Publish to prod (latest tag)
./publish-npm-package.sh prod 1.0.0

# Check login
npm whoami

# Update version
npm version patch|minor|major

# View package info
npm view your-package

# Local test
npm pack
tar -tzf your-package-1.0.0.tgz

# Dry run
npm publish --dry-run
```

### File Checklist

Before publishing, ensure you have:

- [ ] `package.json` (with all required fields)
- [ ] `README.md` (with usage examples)
- [ ] `LICENSE` (MIT, Apache, etc.)
- [ ] `.npmignore` (exclude dev files)
- [ ] Built files (in `dist/` or similar)
- [ ] TypeScript types (if applicable)
- [ ] Tests (passing)

### Publishing Checklist

- [ ] Code is tested and working
- [ ] Version number updated
- [ ] CHANGELOG updated
- [ ] README updated
- [ ] No secrets in code
- [ ] Dependencies up to date
- [ ] `npm pack` contents reviewed
- [ ] `npm publish --dry-run` successful

---

## Additional Resources

### npm Documentation

- **npm docs:** https://docs.npmjs.com/
- **Publishing packages:** https://docs.npmjs.com/packages-and-modules/contributing-packages-to-the-registry
- **package.json:** https://docs.npmjs.com/cli/v10/configuring-npm/package-json
- **semver:** https://semver.org/

### Tools

- **npm Package Cost:** https://packagephobia.com/
- **Bundlephobia:** https://bundlephobia.com/
- **npm Trends:** https://npmtrends.com/

### Community

- **npm Status:** https://status.npmjs.org/
- **npm Support:** https://www.npmjs.com/support
- **GitHub:** https://github.com/npm/cli

---

## Summary

You now have a complete npm publishing system:

1. ✓ Universal publish script (`publish-npm-package.sh`)
2. ✓ Credential setup wizard (`setup-npm-credentials.sh`)
3. ✓ GitHub Actions integration (`.github/workflows/npm-publish-template.yml`)
4. ✓ Comprehensive documentation (this guide)

**To publish any npm package:**

```bash
# 1. Setup (one-time)
./setup-npm-credentials.sh

# 2. Test publish
./publish-npm-package.sh test

# 3. Production publish
./publish-npm-package.sh prod 1.0.0
```

**Everything else is automatic!** 🚀

---

**Created:** January 2026
**Maintained by:** AfterDark Security
**License:** MIT
