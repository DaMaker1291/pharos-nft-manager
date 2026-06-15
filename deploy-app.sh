#!/bin/bash
set -e
echo "🚀 Building Pharos NFT Manager App..."
cd "$(dirname "$0")/app"
npm run build
echo "✅ Build complete! (app/dist)"
echo ""
echo "To deploy to GitHub Pages:"
echo "  1. Push to main branch (auto-deploys via Actions)"
echo "  2. Or manually: npx gh-pages -d dist"
echo ""
echo "📎 Live URL once deployed:"
echo "   https://DaMaker1291.github.io/pharos-nft-manager/"
