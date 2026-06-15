#!/bin/bash

# Pharos NFT Manager — Demo Video Recording Script
# Records screen + mic via ffmpeg, stages the demo step by step

set -e

OUTPUT_FILE="${1:-pharos-nft-demo.mp4}"
DURATION="${2:-300}"  # 5 min default
TIMESTAMP=$(date +%s)

echo "============================================"
echo "  Pharos NFT Manager — Demo Recorder"
echo "============================================"
echo ""
echo "Output: $OUTPUT_FILE"
echo "Max duration: ${DURATION}s"
echo ""
echo "We'll stage each step — you explain as we go."
echo ""

# 1. Open VS Code at the project
echo ">>> Opening VS Code with project..."
open -a "Visual Studio Code" /Users/shaurjeshbasu/Downloads/HACK\ IN/pharos-nft-manager
sleep 3

# 2. Open GitHub repo in browser
echo ">>> Opening GitHub repo..."
open https://github.com/DaMaker1291/pharos-nft-manager
sleep 2

# 3. Print demo script in a separate terminal
echo ""
echo "============================================"
echo "  DEMO SCRIPT — Follow these steps:"
echo "============================================"
echo ""
echo "STAGE 1 — GitHub Repo (0:00 - 0:45)"
echo "  - Browser shows the repo"
echo "  - README: explain what the skill does"
echo "  - Point out: SKILL.md, assets/, references/"
echo ""
echo "STAGE 2 — SKILL.md Entry Point (0:45 - 1:30)"
echo "  - VS Code open at SKILL.md"
echo "  - Show YAML frontmatter (name, description, triggers)"
echo "  - Show Capability Index table"
echo "  - Explain: this is what the AI agent reads first"
echo ""
echo "STAGE 3 — Smart Contract (1:30 - 2:30)"
echo "  - Open assets/nft/PharosNFT.sol"
echo "  - Explain: ERC-721 + EIP-2981 royalty + batch mint"
echo "  - Highlight: safeMint, mintBatch, royaltyInfo"
echo "  - Show OpenZeppelin inheritance"
echo ""
echo "STAGE 4 — Reference Files (2:30 - 3:30)"
echo "  - Open references/deploy-nft.md"
echo "  - Show: command template, parameters, error handling"
echo "  - Open references/mint-nft.md"
echo "  - Open references/query-nft.md"
echo "  - Explain: agent guidelines for each operation"
echo ""
echo "STAGE 5 — Network Config (3:30 - 3:50)"
echo "  - Open assets/networks.json"
echo "  - Show: testnet + mainnet RPC, chain IDs"
echo ""
echo "STAGE 6 — Wrap Up (3:50 - 4:30)"
echo "  - Show README features table"
echo "  - Summarize why this wins:"
echo "    - Original: no NFT skill exists"
echo "    - Complete: full lifecycle"
echo "    - Composable: works with skill engine"
echo "    - Practical: NFTs for AI Agent economy"
echo ""
echo "============================================"
echo ""

# 4. Start recording
echo ">>> Starting screen recording in 5 seconds..."
echo "    Speak clearly and walk through each stage."
echo "    Press CTRL+C to stop recording early."
sleep 5

echo ">>> Recording... (max ${DURATION}s)"

ffmpeg -f avfoundation -capture_cursor 1 -i "1:0" \
  -t "$DURATION" \
  -c:v libx264 -preset ultrafast -crf 28 \
  -c:a aac -b:a 128k \
  -pix_fmt yuv420p \
  "$OUTPUT_FILE" 2>&1 | tail -5

echo ""
echo "============================================"
echo "  Recording saved: $OUTPUT_FILE"
echo "============================================"
echo ""
echo "Now upload to YouTube (unlisted) or directly"
echo "to DoraHacks submission."
echo ""
echo "File size:"
ls -lh "$OUTPUT_FILE"
