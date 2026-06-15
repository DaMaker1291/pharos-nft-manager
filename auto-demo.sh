#!/bin/bash
# Automated demo video generator — captures full screen
set -e

export TERM=xterm-256color
PROJECT="/Users/shaurjeshbasu/Downloads/HACK IN/pharos-nft-manager"
OUTPUT_DIR="/tmp/pharos-demo-$(date +%s)"
FRAMES_DIR="$OUTPUT_DIR/frames"
VIDEO="$PROJECT/pharos-nft-demo.mp4"
mkdir -p "$FRAMES_DIR"

frame=0

next_frame() {
  frame=$((frame + 1))
  local filepath="$1"
  local label="$2"

  clear
  echo ""
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║           PHAROS NFT COLLECTION MANAGER                     ║"
  printf "║  Stage %-2s  %-45s  ║\n" "$frame" "$label"
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo ""

  if [ -f "$filepath" ]; then
    local total=$(wc -l < "$filepath")
    local show=$((total > 55 ? 55 : total))
    head -$show "$filepath"
    if [ "$total" -gt 55 ]; then
      echo ""
      echo "  ... ($((total - 55)) more lines)"
    fi
  elif [ -d "$filepath" ]; then
    ls -la "$filepath"
  fi

  sleep 2
  local padded=$(printf "frame-%03d" $frame)
  screencapture -x "$FRAMES_DIR/$padded.png"
  echo "  >> Frame $frame: $label"
  sleep 0.5
}

cd "$PROJECT"

echo "Starting automated demo video capture..."
echo "Total frames: ~15 | Duration: ~1 min"
sleep 2

next_frame "." "Project Structure Overview"
next_frame "SKILL.md" "Entry Point — AI Agent Instructions"
grep -B2 -A 35 "^| Capability\|^| ---" SKILL.md > /tmp/st3.txt
next_frame "/tmp/st3.txt" "Capability Index — 15 Operations"
next_frame "assets/nft/PharosNFT.sol" "Smart Contract — ERC-721 + EIP-2981"
grep -B1 -A 20 "^    constructor" assets/nft/PharosNFT.sol > /tmp/st5.txt
next_frame "/tmp/st5.txt" "Constructor — Collection Configuration"
grep -B1 -A 22 "function mintBatch" assets/nft/PharosNFT.sol > /tmp/st6.txt
next_frame "/tmp/st6.txt" "Batch Mint — Multi-Recipient in One TX"
grep -B1 -A 15 "function royaltyInfo" assets/nft/PharosNFT.sol > /tmp/st7.txt
next_frame "/tmp/st7.txt" "EIP-2981 Royalty — Automated Creator Fees"
head -60 references/deploy-nft.md > /tmp/st8.txt
next_frame "/tmp/st8.txt" "Deploy Reference — Agent Instructions"
head -50 references/mint-nft.md > /tmp/st9.txt
next_frame "/tmp/st9.txt" "Mint Reference — Token Creation"
head -50 references/transfer-nft.md > /tmp/st10.txt
next_frame "/tmp/st10.txt" "Transfer Reference — Safe Transfer & Approve"
head -50 references/query-nft.md > /tmp/st11.txt
next_frame "/tmp/st11.txt" "Query Reference — Collection & Token State"
head -50 references/batch-nft.md > /tmp/st12.txt
next_frame "/tmp/st12.txt" "Batch Ops — Airdrops & Bulk Transfers"
next_frame "assets/networks.json" "Network Config — Testnet & Mainnet"
head -50 README.md > /tmp/st14.txt
next_frame "/tmp/st14.txt" "README — Full Documentation"

# Final summary
clear
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        PHAROS NFT COLLECTION MANAGER                         ║"
echo "║                                                              ║"
echo "║        ✓ SKILL.md — YAML frontmatter + 15 capabilities       ║"
echo "║        ✓ PharosNFT.sol — ERC-721 + Royalty + Batch          ║"
echo "║        ✓ 5 reference files for AI agent instructions         ║"
echo "║        ✓ Error handling in every command template            ║"
echo "║        ✓ Network config (Atlantic + Pacific)                 ║"
echo "║        ✓ Metadata templates + full README                    ║"
echo "║                                                              ║"
echo "║        WHY THIS WINS:                                        ║"
echo "║        • ORIGINAL — No existing NFT skill on Pharos          ║"
echo "║        • COMPLETE — Full lifecycle: deploy→mint→query        ║"
echo "║        • COMPOSABLE — Importable by Pharos Skill Engine      ║"
echo "║        • PRACTICAL — NFTs for AI Agent economy               ║"
echo "║        • EXCELLENT DOCS — Templates, errors, guidelines      ║"
echo "║                                                              ║"
echo "║     GitHub: DaMaker1291/pharos-nft-manager                   ║"
echo "║     Phase 1: Skill Hackathon | 500 PROS prize                ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
sleep 3
frame=$((frame + 1))
spadded=$(printf "frame-%03d" $frame)
screencapture -x "$FRAMES_DIR/$spadded.png"

echo ""
echo ">>> Frames captured: $frame"

echo ""
echo ">>> Generating video..."
ffmpeg -y -framerate 1/3 -pattern_type glob -i "$FRAMES_DIR/frame-*.png" \
  -c:v libx264 -preset medium -crf 22 \
  -pix_fmt yuv420p -r 30 \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black" \
  "$VIDEO" 2>&1 | tail -5

echo ""
echo "======================================="
echo "  Video: $VIDEO"
ls -lh "$VIDEO"
echo "======================================="
