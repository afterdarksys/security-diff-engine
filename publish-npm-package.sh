#!/bin/bash
# Universal NPM Package Publisher
# Usage: ./publish-npm-package.sh [test|prod] [version]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MODE="${1:-test}"
VERSION="${2:-}"

echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   NPM Package Publisher${NC}"
echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo ""

# Step 1: Verify we're in an npm package directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Error: No package.json found${NC}"
    echo "   Run this script from the root of an npm package"
    exit 1
fi

PACKAGE_NAME=$(node -p "require('./package.json').name" 2>/dev/null || echo "unknown")
CURRENT_VERSION=$(node -p "require('./package.json').version" 2>/dev/null || echo "0.0.0")

echo -e "${GREEN}📦 Package:${NC} $PACKAGE_NAME"
echo -e "${GREEN}📌 Current Version:${NC} $CURRENT_VERSION"
echo ""

# Step 2: Check if logged in to npm
if ! npm whoami &> /dev/null; then
    echo -e "${RED}❌ Not logged in to npm${NC}"
    echo -e "${YELLOW}💡 Run: npm login${NC}"
    exit 1
fi

NPM_USER=$(npm whoami)
echo -e "${GREEN}👤 npm User:${NC} $NPM_USER"
echo ""

# Step 3: Clean previous builds
echo -e "${YELLOW}🧹 Cleaning previous builds...${NC}"
rm -rf dist/ build/ *.tgz
echo -e "${GREEN}✓ Clean complete${NC}"
echo ""

# Step 4: Run tests (if they exist)
if [ -f "package.json" ] && grep -q "\"test\"" package.json; then
    echo -e "${YELLOW}🧪 Running tests...${NC}"
    if npm test 2>/dev/null; then
        echo -e "${GREEN}✓ Tests passed${NC}"
    else
        echo -e "${RED}❌ Tests failed${NC}"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    echo ""
fi

# Step 5: Update version (if provided)
if [ -n "$VERSION" ]; then
    echo -e "${YELLOW}📝 Updating version to $VERSION...${NC}"
    npm version "$VERSION" --no-git-tag-version
    echo -e "${GREEN}✓ Version updated${NC}"
    echo ""
fi

# Step 6: Run build (if build script exists)
if grep -q "\"build\"" package.json; then
    echo -e "${YELLOW}🔨 Building package...${NC}"
    npm run build
    echo -e "${GREEN}✓ Build complete${NC}"
    echo ""
fi

# Step 7: Create package tarball
echo -e "${YELLOW}📦 Creating package...${NC}"
npm pack
TARBALL=$(ls -t *.tgz | head -1)
echo -e "${GREEN}✓ Package created: $TARBALL${NC}"
echo ""

# Step 8: Show package contents
echo -e "${BLUE}📋 Package contents:${NC}"
tar -tzf "$TARBALL" | head -20
if [ $(tar -tzf "$TARBALL" | wc -l) -gt 20 ]; then
    echo "   ... and $(($(tar -tzf "$TARBALL" | wc -l) - 20)) more files"
fi
echo ""

# Step 9: Dry run check
echo -e "${YELLOW}🔍 Running publish dry-run...${NC}"
if npm publish --dry-run "$TARBALL"; then
    echo -e "${GREEN}✓ Dry-run passed${NC}"
else
    echo -e "${RED}❌ Dry-run failed${NC}"
    exit 1
fi
echo ""

# Step 10: Publish
if [ "$MODE" = "test" ]; then
    echo -e "${YELLOW}🚀 Publishing to npm with 'next' tag (beta)...${NC}"
    echo -e "${YELLOW}   (Test mode - users must explicitly install @next)${NC}"
    echo ""

    npm publish "$TARBALL" --tag next || {
        echo ""
        echo -e "${RED}❌ Upload failed${NC}"
        echo -e "${YELLOW}💡 Common issues:${NC}"
        echo "   1. Package name already taken"
        echo "   2. Version already published"
        echo "   3. Not logged in: npm login"
        echo "   4. No publish access"
        exit 1
    }

    echo ""
    echo -e "${GREEN}✓ Published to npm (next tag)${NC}"
    echo -e "${BLUE}📦 Test install:${NC}"
    echo "   npm install $PACKAGE_NAME@next"

elif [ "$MODE" = "prod" ]; then
    echo -e "${RED}⚠️  PRODUCTION MODE${NC}"
    echo -e "${YELLOW}   This will publish to npm as 'latest'${NC}"
    echo ""
    read -p "Are you sure? (yes/no) " -r
    echo
    if [[ ! $REPLY = "yes" ]]; then
        echo "Cancelled."
        rm -f "$TARBALL"
        exit 1
    fi

    echo -e "${YELLOW}🚀 Publishing to npm...${NC}"
    npm publish "$TARBALL" || {
        echo ""
        echo -e "${RED}❌ Upload failed${NC}"
        echo -e "${YELLOW}💡 Common issues:${NC}"
        echo "   1. Package name already taken"
        echo "   2. Version already published (can't overwrite)"
        echo "   3. Not logged in: npm login"
        echo "   4. No publish access"
        exit 1
    }

    echo ""
    echo -e "${GREEN}✓ Published to npm${NC}"
    echo -e "${BLUE}📦 Install:${NC}"
    echo "   npm install $PACKAGE_NAME"

    # Step 11: Create git tag
    if [ -n "$VERSION" ]; then
        echo ""
        echo -e "${YELLOW}🏷️  Creating git tag v$VERSION...${NC}"
        git add package.json package-lock.json 2>/dev/null || true
        git commit -m "Release v$VERSION" 2>/dev/null || echo "No changes to commit"
        git tag -a "v$VERSION" -m "Release version $VERSION"
        echo -e "${GREEN}✓ Tag created${NC}"
        echo ""
        echo -e "${BLUE}💡 Push tag:${NC}"
        echo "   git push && git push --tags"
    fi

    # Cleanup
    rm -f "$TARBALL"
else
    echo -e "${RED}❌ Invalid mode: $MODE${NC}"
    echo "Usage: $0 [test|prod] [version]"
    rm -f "$TARBALL"
    exit 1
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   ✅ Done!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
