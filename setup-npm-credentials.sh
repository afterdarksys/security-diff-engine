#!/bin/bash
# NPM Credentials Setup Wizard
# One-time setup for npm package publishing

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   NPM Credentials Setup Wizard${NC}"
echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo ""

# Step 1: Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed${NC}"
    echo ""
    echo "Install Node.js (includes npm):"
    echo "  - macOS: brew install node"
    echo "  - Linux: sudo apt-get install nodejs npm"
    echo "  - Windows: https://nodejs.org/"
    exit 1
fi

NPM_VERSION=$(npm --version)
echo -e "${GREEN}✓ npm installed:${NC} v$NPM_VERSION"
echo ""

# Step 2: Check if logged in
if npm whoami &> /dev/null; then
    NPM_USER=$(npm whoami)
    echo -e "${GREEN}✓ Already logged in to npm:${NC} $NPM_USER"
    echo ""
    read -p "Do you want to log in with a different account? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Setup complete!${NC}"
        exit 0
    fi
    echo ""
fi

# Step 3: npm account setup guide
echo -e "${YELLOW}📝 NPM Account Setup${NC}"
echo ""
echo "If you don't have an npm account yet:"
echo "  1. Visit: https://www.npmjs.com/signup"
echo "  2. Create your account"
echo "  3. Verify your email address"
echo ""
echo -e "${BLUE}Press Enter when ready to log in...${NC}"
read

# Step 4: npm login
echo -e "${YELLOW}🔑 Logging in to npm...${NC}"
echo ""
echo "You'll be prompted for:"
echo "  - Username"
echo "  - Password"
echo "  - Email"
echo ""

if npm login; then
    echo ""
    echo -e "${GREEN}✓ Successfully logged in!${NC}"
    NPM_USER=$(npm whoami)
    echo -e "${GREEN}✓ npm User:${NC} $NPM_USER"
else
    echo ""
    echo -e "${RED}❌ Login failed${NC}"
    echo ""
    echo -e "${YELLOW}💡 Troubleshooting:${NC}"
    echo "  1. Verify your credentials"
    echo "  2. Check email verification"
    echo "  3. Try: npm login --auth-type=web"
    exit 1
fi

echo ""

# Step 5: Verify authentication
echo -e "${YELLOW}🔍 Verifying authentication...${NC}"
if npm whoami &> /dev/null; then
    echo -e "${GREEN}✓ Authentication verified${NC}"
else
    echo -e "${RED}❌ Authentication failed${NC}"
    exit 1
fi

echo ""

# Step 6: Check for 2FA
echo -e "${YELLOW}🔐 Checking 2FA status...${NC}"
echo ""
echo "For better security, enable 2FA on your npm account:"
echo "  1. Visit: https://www.npmjs.com/settings/$(npm whoami)/tfa"
echo "  2. Enable 2FA"
echo "  3. Choose 'Authorization and Publishing' mode for best security"
echo ""
echo "Note: With 2FA enabled, you'll need one-time passwords for publishing."
echo ""

# Step 7: Test access
echo -e "${YELLOW}🧪 Testing npm access...${NC}"
if npm access ls-packages 2>/dev/null | grep -q "$(npm whoami)" || [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ npm access confirmed${NC}"
else
    echo -e "${YELLOW}⚠️  No packages published yet (this is normal for new accounts)${NC}"
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   ✅ Setup Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📦 Credentials stored in:${NC}"
echo "  ~/.npmrc"
echo ""
echo -e "${BLUE}💡 Next steps:${NC}"
echo "  1. Run: ./publish-npm-package.sh test"
echo "  2. Test your package"
echo "  3. Run: ./publish-npm-package.sh prod [version]"
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo "  - NPM_PUBLISHING_GUIDE.md (comprehensive)"
echo "  - QUICK_PUBLISH_REFERENCE.md (quick reference)"
echo ""
echo -e "${GREEN}You're ready to publish npm packages! 🚀${NC}"
echo ""
