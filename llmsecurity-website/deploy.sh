#!/bin/bash

# llmsecurity.dev Quick Deploy Script
# Choose your deployment method

echo "🚀 llmsecurity.dev Deployment Script"
echo "====================================="
echo ""
echo "Choose deployment method:"
echo "1) Vercel (Recommended - Fast & Free)"
echo "2) Netlify (Easy & Free)"
echo "3) Test Locally Only"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
  1)
    echo "📦 Deploying to Vercel..."

    # Check if vercel CLI is installed
    if ! command -v vercel &> /dev/null; then
        echo "❌ Vercel CLI not installed"
        echo "📥 Installing Vercel CLI..."
        npm install -g vercel
    fi

    echo "🚀 Deploying..."
    vercel --prod

    echo ""
    echo "✅ Deployed to Vercel!"
    echo "📝 Next steps:"
    echo "   1. Go to Vercel Dashboard"
    echo "   2. Settings → Domains"
    echo "   3. Add custom domain: llmsecurity.dev"
    ;;

  2)
    echo "📦 Deploying to Netlify..."

    # Check if netlify CLI is installed
    if ! command -v netlify &> /dev/null; then
        echo "❌ Netlify CLI not installed"
        echo "📥 Installing Netlify CLI..."
        npm install -g netlify-cli
    fi

    echo "🚀 Deploying..."
    netlify deploy --prod

    echo ""
    echo "✅ Deployed to Netlify!"
    echo "📝 Next steps:"
    echo "   1. Go to Netlify Dashboard"
    echo "   2. Domain settings"
    echo "   3. Add custom domain: llmsecurity.dev"
    ;;

  3)
    echo "🌐 Starting local server..."
    echo ""
    echo "✅ Server running at: http://localhost:8000"
    echo "📱 Network access at: http://$(ipconfig getifaddr en0):8000"
    echo ""
    echo "Press Ctrl+C to stop"
    echo ""
    python3 -m http.server 8000
    ;;

  *)
    echo "❌ Invalid choice"
    exit 1
    ;;
esac
