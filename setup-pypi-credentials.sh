#!/bin/bash
# PyPI Credentials Setup Helper

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   PyPI Credentials Setup${NC}"
echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo ""

# Check if keyring is available
if ! python3 -c "import keyring" 2>/dev/null; then
    echo -e "${YELLOW}Installing keyring...${NC}"
    pip3 install --user keyring
    echo ""
fi

echo -e "${GREEN}This script will help you store your PyPI API tokens securely.${NC}"
echo ""
echo -e "${YELLOW}Step 1: Create PyPI Accounts (if you haven't)${NC}"
echo "  - TestPyPI: https://test.pypi.org/account/register/"
echo "  - PyPI: https://pypi.org/account/register/"
echo ""

read -p "Press ENTER when you have your accounts ready..."

echo ""
echo -e "${YELLOW}Step 2: Generate API Tokens${NC}"
echo "  - TestPyPI token: https://test.pypi.org/manage/account/token/"
echo "  - PyPI token: https://pypi.org/manage/account/token/"
echo ""
echo "Create tokens with 'Entire account' scope"
echo ""

read -p "Press ENTER when you have your tokens ready..."

echo ""
echo -e "${BLUE}═══ TestPyPI Token ═══${NC}"
echo "Paste your TestPyPI token (starts with 'pypi-'):"
python3 -m keyring set https://test.pypi.org/legacy/ __token__

echo ""
echo -e "${BLUE}═══ PyPI Token ═══${NC}"
echo "Paste your PyPI token (starts with 'pypi-'):"
python3 -m keyring set https://upload.pypi.org/legacy/ __token__

echo ""
echo -e "${GREEN}✅ Credentials stored securely!${NC}"
echo ""
echo -e "${BLUE}You can now publish packages:${NC}"
echo "  ./publish-python-package.sh test      # Test on TestPyPI"
echo "  ./publish-python-package.sh prod 1.0.0  # Publish to PyPI"
echo ""
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   Setup Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
