# Website Content - PyPI Packages Section

**Add this to your websites to showcase your 12 PyPI packages**

---

## For llmsecurity.dev

### Homepage Section:

```html
<section id="packages" class="py-20 bg-gray-50 dark:bg-gray-900">
  <div class="container mx-auto px-4">
    <div class="text-center mb-12">
      <h2 class="text-4xl font-bold text-gray-900 dark:text-white mb-4">
        Production-Ready Python Packages
      </h2>
      <p class="text-xl text-gray-600 dark:text-gray-300">
        12 open-source packages published on PyPI, installable worldwide via <code>pip install</code>
      </p>
      <div class="mt-4">
        <a href="https://pypi.org/user/afterdarksys/"
           class="text-blue-600 hover:text-blue-800 dark:text-blue-400 font-semibold">
          Browse all packages on PyPI →
        </a>
      </div>
    </div>

    <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- Security & AI Packages -->
      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
        <div class="flex items-center mb-4">
          <span class="text-3xl mr-3">🔒</span>
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">afterdark-llm-firewall</h3>
        </div>
        <p class="text-gray-600 dark:text-gray-300 mb-4">
          Production-ready security layer for AI applications
        </p>
        <code class="text-sm bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded">
          pip install afterdark-llm-firewall
        </code>
        <div class="mt-4">
          <a href="https://pypi.org/project/afterdark-llm-firewall/"
             class="text-blue-600 hover:text-blue-800 text-sm">View on PyPI</a>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
        <div class="flex items-center mb-4">
          <span class="text-3xl mr-3">🤖</span>
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">afterdark-prompt-generator</h3>
        </div>
        <p class="text-gray-600 dark:text-gray-300 mb-4">
          Enterprise-grade prompt generator for ChatGPT and Claude Code
        </p>
        <code class="text-sm bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded">
          pip install afterdark-prompt-generator
        </code>
        <div class="mt-4">
          <a href="https://pypi.org/project/afterdark-prompt-generator/"
             class="text-blue-600 hover:text-blue-800 text-sm">View on PyPI</a>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
        <div class="flex items-center mb-4">
          <span class="text-3xl mr-3">🔐</span>
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">gpg-key-tracker</h3>
        </div>
        <p class="text-gray-600 dark:text-gray-300 mb-4">
          Comprehensive PGP/GPG key management with metadata tracking
        </p>
        <code class="text-sm bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded">
          pip install gpg-key-tracker
        </code>
        <div class="mt-4">
          <a href="https://pypi.org/project/gpg-key-tracker/"
             class="text-blue-600 hover:text-blue-800 text-sm">View on PyPI</a>
        </div>
      </div>

      <!-- DNS & Networking -->
      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
        <div class="flex items-center mb-4">
          <span class="text-3xl mr-3">🌐</span>
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">dnsscience-dnsnet</h3>
        </div>
        <p class="text-gray-600 dark:text-gray-300 mb-4">
          DNS networking and analysis toolkit
        </p>
        <code class="text-sm bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded">
          pip install dnsscience-dnsnet
        </code>
        <div class="mt-4">
          <a href="https://pypi.org/project/dnsscience-dnsnet/"
             class="text-blue-600 hover:text-blue-800 text-sm">View on PyPI</a>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
        <div class="flex items-center mb-4">
          <span class="text-3xl mr-3">⚙️</span>
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">dnsscience-coredns-manager</h3>
        </div>
        <p class="text-gray-600 dark:text-gray-300 mb-4">
          CoreDNS management and automation tool
        </p>
        <code class="text-sm bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded">
          pip install dnsscience-coredns-manager
        </code>
        <div class="mt-4">
          <a href="https://pypi.org/project/dnsscience-coredns-manager/"
             class="text-blue-600 hover:text-blue-800 text-sm">View on PyPI</a>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
        <div class="flex items-center mb-4">
          <span class="text-3xl mr-3">🔧</span>
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">rancid-ng</h3>
        </div>
        <p class="text-gray-600 dark:text-gray-300 mb-4">
          Next-generation network configuration management
        </p>
        <code class="text-sm bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded">
          pip install rancid-ng
        </code>
        <div class="mt-4">
          <a href="https://pypi.org/project/rancid-ng/"
             class="text-blue-600 hover:text-blue-800 text-sm">View on PyPI</a>
        </div>
      </div>

      <!-- Cloud & Infrastructure -->
      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
        <div class="flex items-center mb-4">
          <span class="text-3xl mr-3">☁️</span>
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">aws2oci</h3>
        </div>
        <p class="text-gray-600 dark:text-gray-300 mb-4">
          AWS to Oracle Cloud Infrastructure migration toolkit
        </p>
        <code class="text-sm bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded">
          pip install aws2oci
        </code>
        <div class="mt-4">
          <a href="https://pypi.org/project/aws2oci/"
             class="text-blue-600 hover:text-blue-800 text-sm">View on PyPI</a>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
        <div class="flex items-center mb-4">
          <span class="text-3xl mr-3">🐰</span>
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">bunny-cli</h3>
        </div>
        <p class="text-gray-600 dark:text-gray-300 mb-4">
          Bunny CDN command-line interface
        </p>
        <code class="text-sm bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded">
          pip install bunny-cli
        </code>
        <div class="mt-4">
          <a href="https://pypi.org/project/bunny-cli/"
             class="text-blue-600 hover:text-blue-800 text-sm">View on PyPI</a>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
        <div class="flex items-center mb-4">
          <span class="text-3xl mr-3">🔏</span>
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">linux-codesign-toolkit</h3>
        </div>
        <p class="text-gray-600 dark:text-gray-300 mb-4">
          Linux code signing and verification toolkit
        </p>
        <code class="text-sm bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded">
          pip install linux-codesign-toolkit
        </code>
        <div class="mt-4">
          <a href="https://pypi.org/project/linux-codesign-toolkit/"
             class="text-blue-600 hover:text-blue-800 text-sm">View on PyPI</a>
        </div>
      </div>

      <!-- Additional Tools -->
      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
        <div class="flex items-center mb-4">
          <span class="text-3xl mr-3">🤖</span>
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">autonomousbm</h3>
        </div>
        <p class="text-gray-600 dark:text-gray-300 mb-4">
          Autonomous business management and automation
        </p>
        <code class="text-sm bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded">
          pip install autonomousbm
        </code>
        <div class="mt-4">
          <a href="https://pypi.org/project/autonomousbm/"
             class="text-blue-600 hover:text-blue-800 text-sm">View on PyPI</a>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
        <div class="flex items-center mb-4">
          <span class="text-3xl mr-3">💕</span>
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">nerdycupid</h3>
        </div>
        <p class="text-gray-600 dark:text-gray-300 mb-4">
          AI-powered dating and matchmaking assistant
        </p>
        <code class="text-sm bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded">
          pip install nerdycupid
        </code>
        <div class="mt-4">
          <a href="https://pypi.org/project/nerdycupid/"
             class="text-blue-600 hover:text-blue-800 text-sm">View on PyPI</a>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
        <div class="flex items-center mb-4">
          <span class="text-3xl mr-3">🌍</span>
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">dnsscience-globalconnect</h3>
        </div>
        <p class="text-gray-600 dark:text-gray-300 mb-4">
          Global connectivity and network detection tool
        </p>
        <code class="text-sm bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded">
          pip install dnsscience-globalconnect
        </code>
        <div class="mt-4">
          <a href="https://pypi.org/project/dnsscience-globalconnect/"
             class="text-blue-600 hover:text-blue-800 text-sm">View on PyPI</a>
        </div>
      </div>
    </div>

    <div class="text-center mt-12">
      <div class="inline-flex items-center space-x-4 bg-blue-50 dark:bg-blue-900 px-8 py-4 rounded-lg">
        <span class="text-lg font-semibold text-gray-900 dark:text-white">
          All packages are MIT licensed and production-ready
        </span>
        <a href="https://github.com/straticus1"
           class="text-blue-600 hover:text-blue-800 dark:text-blue-400 font-semibold">
          View on GitHub →
        </a>
      </div>
    </div>
  </div>
</section>
```

---

## For AfterDark.tech (or Company Site)

### Markdown Version:

```markdown
## 🚀 Open Source Python Packages

AfterDark has published **12 production-ready Python packages** to PyPI, available worldwide via `pip install`.

### Security & AI Tools

- **[afterdark-llm-firewall](https://pypi.org/project/afterdark-llm-firewall/)** - AI application security layer
  ```bash
  pip install afterdark-llm-firewall
  ```

- **[afterdark-prompt-generator](https://pypi.org/project/afterdark-prompt-generator/)** - Enterprise prompt engineering
  ```bash
  pip install afterdark-prompt-generator
  ```

- **[gpg-key-tracker](https://pypi.org/project/gpg-key-tracker/)** - PGP/GPG key management
  ```bash
  pip install gpg-key-tracker
  ```

### DNS & Networking

- **[dnsscience-dnsnet](https://pypi.org/project/dnsscience-dnsnet/)** - DNS networking toolkit
- **[dnsscience-coredns-manager](https://pypi.org/project/dnsscience-coredns-manager/)** - CoreDNS automation
- **[dnsscience-globalconnect](https://pypi.org/project/dnsscience-globalconnect/)** - Global connectivity tools
- **[rancid-ng](https://pypi.org/project/rancid-ng/)** - Network configuration management

### Cloud & Infrastructure

- **[aws2oci](https://pypi.org/project/aws2oci/)** - AWS to OCI migration
- **[bunny-cli](https://pypi.org/project/bunny-cli/)** - Bunny CDN management
- **[linux-codesign-toolkit](https://pypi.org/project/linux-codesign-toolkit/)** - Code signing tools

### AI & Automation

- **[autonomousbm](https://pypi.org/project/autonomousbm/)** - Business automation
- **[nerdycupid](https://pypi.org/project/nerdycupid/)** - AI matchmaking

---

**Browse all packages:** [PyPI Profile](https://pypi.org/user/afterdarksys/)
```

---

## Simple Hero Banner

Add this to any page for quick visibility:

```html
<div class="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-12 px-4 text-center">
  <h2 class="text-3xl font-bold mb-4">12 Python Packages on PyPI</h2>
  <p class="text-xl mb-6">Production-ready tools for security, networking, and cloud infrastructure</p>
  <a href="https://pypi.org/user/afterdarksys/"
     class="bg-white text-blue-600 px-8 py-3 rounded-full font-semibold hover:bg-gray-100 inline-block">
    Browse Packages →
  </a>
</div>
```

---

## Footer Addition

Add to your site footer:

```html
<div class="text-center py-4 border-t border-gray-200 dark:border-gray-700">
  <p class="text-gray-600 dark:text-gray-400">
    <strong>12 Python packages</strong> published on PyPI |
    <a href="https://pypi.org/user/afterdarksys/" class="text-blue-600 hover:text-blue-800">
      View on PyPI
    </a>
  </p>
</div>
```

---

## README Badge for GitHub Org

Add to your GitHub organization profile README:

```markdown
## 📦 PyPI Packages

We maintain 12 production-ready Python packages on PyPI:

[![PyPI Packages](https://img.shields.io/badge/PyPI-12%20packages-blue)](https://pypi.org/user/afterdarksys/)

Browse all: **[pypi.org/user/afterdarksys](https://pypi.org/user/afterdarksys/)**
```

---

**Save this file and use these snippets to update your sites!**
