# VeriBits Phase 2 - Deployment Guide
**Created:** January 12, 2026
**Status:** Ready for deployment (SSH access required)

---

## 📋 Deployment Summary

### What's Been Completed

✅ **Phase 1: Quick Wins**
- PyPI packages published (afterdark-llm-firewall, afterdark-prompt-generator)
- GitHub releases created
- llmsecurity.dev website deployed to OCI

✅ **Phase 2: VeriBits Expansion (8 Features)**
- All controllers created and committed to git
- Database migration created (030_threat_intelligence_tables.sql)
- SDKs built (Python + TypeScript)
- CI/CD integrations created (GitHub Actions, GitLab CI)
- All code pushed to GitHub: https://github.com/afterdarksys/veribits.com

✅ **Phase 3: General Security Tools (7 Tools)**
- All standalone Python tools created
- Code committed to afterdark-enhancements repository

✅ **Phase 4: Deployment Preparation**
- OCI deployment script updated with new migration
- Deployment archive created: `/tmp/veribits-deploy.tar.gz` (546KB)
- Deployment script pushed to GitHub

✅ **Phase 5: Documentation**
- Master documentation created: `MASTER_DOCUMENTATION.md` (500+ lines)

---

## 🚀 Deployment Instructions

### Prerequisites

Before deploying, ensure you have:

1. **SSH Access to OCI Instances:**
   - Main Server: `129.80.158.147`
   - API Server: `129.153.158.177`
   - SSH Key configured: `~/.ssh/id_rsa` (or set `OCI_SSH_KEY` env var)
   - SSH User: `opc` (or set `OCI_SSH_USER` env var)

2. **Network Access:**
   - VPN connection if required
   - Port 22 (SSH) accessible to OCI instances

3. **Database Access:**
   - PostgreSQL credentials in `.env` file on server
   - Database: veribits (production)

### Deployment Steps

#### 1. Verify SSH Access

```bash
# Test SSH connection to main server
ssh -i ~/.ssh/id_rsa opc@129.80.158.147

# Test SSH connection to API server
ssh -i ~/.ssh/id_rsa opc@129.153.158.177
```

#### 2. Run Deployment Script

```bash
cd ~/development/veribits.com

# Full deployment (includes migrations)
bash scripts/deploy-to-oci.sh

# Or skip migrations if already applied
bash scripts/deploy-to-oci.sh --skip-migrations

# Or dry run to test without deploying
bash scripts/deploy-to-oci.sh --dry-run
```

#### 3. Verify Deployment

The script automatically verifies:
- Main site: https://veribits.com/
- API health: https://veribits.com/api/v1/health
- API docs: https://veribits.com/api/docs

You can also manually test:

```bash
# Test threat intelligence endpoint
curl -X POST https://veribits.com/api/v1/threat-intel/lookup \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"hash": "test_hash", "sources": ["virustotal"]}'

# Test sandbox endpoint
curl -X POST https://veribits.com/api/v1/sandbox/submit \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@test.txt"

# Test SBOM generation
curl -X POST https://veribits.com/api/v1/ci/sbom/generate \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"format": "cyclonedx"}'
```

---

## 📦 What Gets Deployed

### New Controllers (8 total)

1. **ThreatIntelController.php** (550+ lines)
   - `/api/v1/threat-intel/lookup` - Hash lookups
   - `/api/v1/threat-intel/fingerprint` - File fingerprinting
   - `/api/v1/threat-intel/yara-scan` - YARA scanning
   - `/api/v1/threat-intel/ioc-feed` - IOC feeds

2. **CICDController.php** (400+ lines)
   - `/api/v1/ci/sbom/generate` - SBOM generation
   - `/api/v1/ci/sbom/validate` - SBOM validation
   - `/api/v1/ci/artifacts/scan` - Artifact scanning
   - `/api/v1/ci/webhook` - CI/CD webhooks
   - `/api/v1/ci/stats` - CI/CD statistics

3. **SandboxController.php** (400+ lines)
   - `/api/v1/sandbox/submit` - Submit files
   - `/api/v1/sandbox/status/{id}` - Check status
   - `/api/v1/sandbox/report/{id}` - Get reports
   - `/api/v1/sandbox/static-analysis` - Static analysis

4. **CryptoServicesController.php** (150+ lines)
   - `/api/v1/crypto/keys/publish` - Publish keys
   - `/api/v1/crypto/ct-monitor/add` - CT monitoring
   - `/api/v1/crypto/alerts/expiry` - Expiry alerts

5. **SteganoScaleController.php** (120+ lines)
   - `/api/v1/stegano/batch-scan` - Batch scanning
   - `/api/v1/stegano/cloud-scan` - Cloud scanning

6. **NotificationsController.php** (180+ lines)
   - `/api/v1/notifications/webhooks` - Configure webhooks
   - `/api/v1/notifications/slack` - Slack integration
   - `/api/v1/notifications/siem` - SIEM export
   - `/api/v1/notifications/test` - Test notifications

7. **SecurityPostureController.php** (250+ lines)
   - `/api/v1/posture/dashboard` - Security dashboard
   - `/api/v1/posture/supply-chain-report` - Assurance reports
   - `/api/v1/posture/artifact-integrity` - Integrity status

8. **SDKs**
   - Python SDK: `sdks/python/veribits/`
   - TypeScript SDK: `sdks/typescript/src/`

### Database Migration

**Migration 030: Threat Intelligence Tables** (7 new tables)
- `threat_lookups` - Hash lookup history
- `yara_scans` - YARA scan results
- `iocs` - Indicators of compromise
- `file_fingerprints` - File analysis cache
- `yara_rules` - YARA rules library
- `threat_intel_sources` - API source configuration
- `threat_intel_quotas` - Usage quotas

### CI/CD Integrations

- **GitHub Action:** `.github/actions/veribits-scan/`
  - `action.yml` - Action definition
  - `entrypoint.sh` - Execution script
  - `Dockerfile` - Container definition

- **GitLab CI:** `integrations/gitlab-ci/.gitlab-ci.yml`
  - Security scan job
  - SBOM generation job
  - Artifact scanning job

---

## 🔧 Manual Deployment (If Script Fails)

If the automated script fails, you can deploy manually:

### 1. Create Deployment Archive

```bash
cd ~/development/veribits.com

tar --exclude='.git' \
    --exclude='node_modules' \
    --exclude='vendor' \
    --exclude='.env.local' \
    --exclude='*.log' \
    -czf /tmp/veribits-deploy.tar.gz \
    app/ docker/ db/migrations/ composer.json composer.lock
```

### 2. Upload to Server

```bash
scp -i ~/.ssh/id_rsa /tmp/veribits-deploy.tar.gz opc@129.80.158.147:/tmp/
```

### 3. Extract on Server

```bash
ssh -i ~/.ssh/id_rsa opc@129.80.158.147

# Backup current deployment
sudo cp -r /var/www/veribits /var/www/veribits.backup.$(date +%Y%m%d-%H%M%S)

# Extract new deployment
cd /var/www/veribits
sudo tar -xzf /tmp/veribits-deploy.tar.gz

# Set permissions
sudo chown -R apache:apache /var/www/veribits

# Install dependencies
cd /var/www/veribits
sudo composer install --no-dev --optimize-autoloader

# Restart web server
sudo systemctl restart httpd
```

### 4. Run Database Migration

```bash
# On the server, run the migration
cd /var/www/veribits

# Source environment variables
export $(grep -v '^#' app/config/.env | xargs)

# Run migration
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USERNAME" -d "$DB_DATABASE" \
    -f db/migrations/030_threat_intelligence_tables.sql
```

### 5. Verify

```bash
# Check web server status
sudo systemctl status httpd

# Test health endpoint
curl -sf http://localhost/api/v1/health

# Check logs
sudo tail -f /var/www/logs/app.log
```

---

## 🧪 Post-Deployment Testing

### Test All New Endpoints

```bash
# Set your API key
API_KEY="your_api_key_here"
BASE_URL="https://veribits.com"

# Test threat intelligence
curl -X POST $BASE_URL/api/v1/threat-intel/lookup \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"hash": "abc123", "sources": ["virustotal"]}'

# Test sandbox
curl -X POST $BASE_URL/api/v1/sandbox/submit \
  -H "Authorization: Bearer $API_KEY" \
  -F "file=@test.txt" \
  -F "analysis_type=static"

# Test SBOM generation
curl -X POST $BASE_URL/api/v1/ci/sbom/generate \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"format": "cyclonedx", "components": []}'

# Test crypto services
curl -X POST $BASE_URL/api/v1/crypto/keys/publish \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"key_type": "rsa", "public_key": "..."}'

# Test notifications
curl -X POST $BASE_URL/api/v1/notifications/test \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"channel": "webhook", "config": {}}'

# Test security posture
curl -X GET $BASE_URL/api/v1/posture/dashboard \
  -H "Authorization: Bearer $API_KEY"
```

---

## 📊 Deployment Checklist

### Pre-Deployment
- [ ] SSH access to OCI instances verified
- [ ] Database credentials in `.env` file confirmed
- [ ] Backup of current deployment taken
- [ ] All code pushed to GitHub

### Deployment
- [ ] Deployment script executed successfully
- [ ] Database migration 030 applied
- [ ] Web server restarted
- [ ] No errors in deployment logs

### Post-Deployment
- [ ] Main site accessible (https://veribits.com)
- [ ] API health endpoint returns 200 OK
- [ ] All 25+ new API endpoints tested
- [ ] Database tables created (7 new tables)
- [ ] GitHub Action tested in a repository
- [ ] GitLab CI integration tested
- [ ] Python SDK import tested
- [ ] TypeScript SDK import tested

### Monitoring
- [ ] Check error logs: `/var/www/logs/app.log`
- [ ] Monitor API response times
- [ ] Verify database connections
- [ ] Check Redis cache status
- [ ] Monitor disk space usage

---

## 🐛 Troubleshooting

### SSH Connection Timeout

```bash
# Check if servers are running
oci compute instance list --compartment-id <COMPARTMENT_ID>

# Check security groups allow SSH (port 22)
oci network security-list list --compartment-id <COMPARTMENT_ID>

# Try alternative SSH key
ssh -i ~/.ssh/another_key opc@129.80.158.147
```

### Database Migration Fails

```bash
# Check if tables already exist
psql -h <DB_HOST> -U <DB_USER> -d veribits -c "\dt threat_*"

# Run migration manually with verbose output
psql -h <DB_HOST> -U <DB_USER> -d veribits -f db/migrations/030_threat_intelligence_tables.sql -v ON_ERROR_STOP=1
```

### Web Server Won't Start

```bash
# Check Apache config
sudo apachectl configtest

# Check error logs
sudo tail -f /var/log/httpd/error_log

# Check permissions
ls -la /var/www/veribits/app/public
```

### API Returns 500 Errors

```bash
# Check PHP error logs
sudo tail -f /var/www/logs/app.log

# Check composer dependencies
cd /var/www/veribits
composer install --no-dev

# Check .env file exists
ls -la /var/www/veribits/app/config/.env
```

---

## 📚 Additional Resources

- **Master Documentation:** `MASTER_DOCUMENTATION.md`
- **GitHub Repository:** https://github.com/afterdarksys/veribits.com
- **Deployment Script:** `scripts/deploy-to-oci.sh`
- **Docker Compose:** `docker/docker-compose.production.yml`

---

## 🎯 Next Steps After Deployment

1. **Test All Endpoints** - Use the testing script above
2. **Publish SDKs**
   - Python: `pip install veribits` (publish to PyPI)
   - TypeScript: `npm install veribits` (publish to NPM)
3. **Update API Documentation** - Add OpenAPI/Swagger specs
4. **Set Up Monitoring** - Configure Prometheus/Grafana
5. **Configure Billing** - Set up Stripe integration
6. **Launch Marketing** - Product Hunt, social media
7. **Build Enterprise Features** - Custom tiers, SSO, audit logs

---

**Deployment Prepared By:** Claude Code
**Date:** January 12, 2026
**Status:** ✅ Ready for deployment (requires SSH access)
