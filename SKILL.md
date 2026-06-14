---
name: pharos-nft-manager
description: |
  Complete NFT collection management on Pharos — deploy ERC-721 contracts,
  mint tokens with metadata, batch transfer, manage royalties, and query
  collection state. Use when the user wants to create, mint, transfer, or
  manage NFT collections on Pharos Network. Triggers on "nft", "erc721",
  "collectible", "token uri", "metadata", "mint nft", "deploy nft",
  "nft collection", "pharos nft", "royalty".
version: 1.0.0
license: MIT
author: pharos-builder
metadata:
  network: Pharos Atlantic Testnet
  chain_id: 688689
requires:
  anyBins:
    - cast
    - forge
    - jq
---

# Pharos NFT Collection Manager

Comprehensive skill for deploying and managing ERC-721 NFT collections on Pharos Network. Enables AI agents to create full NFT collections, mint tokens with metadata, manage royalties, batch operations, and query on-chain state.

## Prerequisites

### 1. Install Foundry (MANDATORY)

The Agent MUST first run `which cast` to check if Foundry is installed.
If `cast` is NOT found, run:

```bash
curl -L https://foundry.paradigm.xyz | bash
source ~/.zshenv && foundryup
```

Verify: `cast --version && forge --version`

### 2. Configure Private Key

Write operations require a private key via:
- `--private-key $PRIVATE_KEY` (recommended)
- Environment variable `$PRIVATE_KEY`

### 3. Network Configuration

All RPC URLs, chain IDs, and explorer URLs are in `assets/networks.json`.

Default: **Pharos Atlantic Testnet**
- RPC: `https://atlantic.dplabs-internal.com`
- Chain ID: `688689`
- Explorer: `https://atlantic.pacific-explorer.pharos.network`

---

## Capability Index

| Capability | Tool / Method | Reference |
|---|---|---|
| Deploy NFT collection (ERC-721 with royalty support) | `forge script` | → `references/deploy-nft.md` |
| Mint NFT to address with metadata URI | `cast send` | → `references/mint-nft.md` |
| Transfer NFT from one address to another | `cast send` | → `references/transfer-nft.md` |
| Safe transfer with data payload | `cast send` | → `references/transfer-nft.md#safe-transfer-from-with-data` |
| Query token owner of an NFT | `cast call` | → `references/query-nft.md#token-owner` |
| Query token URI / metadata | `cast call` | → `references/query-nft.md#token-uri` |
| Query collection name & symbol | `cast call` | → `references/query-nft.md#collection-info` |
| Check NFT balance of an address | `cast call` | → `references/query-nft.md#balance-of` |
| Query total supply minted | `cast call` | → `references/query-nft.md#total-supply` |
| Check royalty info for a token | `cast call` | → `references/query-nft.md#royalty-info` |
| Query all tokens owned by address | `cast call` loop | → `references/query-nft.md#tokens-of-owner` |
| Batch mint NFTs to multiple addresses | `cast send` loop | → `references/batch-nft.md#batch-mint` |
| Batch transfer NFTs | `cast send` loop | → `references/batch-nft.md#batch-transfer` |
| Generate metadata JSON for IPFS | `echo` + `jq` | → `references/query-nft.md#metadata-generation` |
| Update token metadata URI | `cast send` | → `references/mint-nft.md#update-token-uri` |
| Set royalty percentage for collection | `cast send` | → `references/deploy-nft.md#set-royalty` |
| Burn NFT token | `cast send` | → `references/transfer-nft.md#burn-token` |

---

## Quick Start

```bash
# Export your private key
export PRIVATE_KEY=0xYourPrivateKey

# Deploy an NFT collection
# Agent reads: references/deploy-nft.md

# Mint an NFT
# Agent reads: references/mint-nft.md

# Check collection
# Agent reads: references/query-nft.md
```

---

## Folder Structure

```
pharos-nft-manager/
├── SKILL.md                      ← Entry point (this file)
├── assets/
│   ├── networks.json             ← Pharos network configuration
│   ├── nft/
│   │   └── PharosNFT.sol         ← ERC-721 contract with royalty
│   └── metadata/
│       └── template.json         ← Metadata JSON template
└── references/
    ├── deploy-nft.md             ← Deploy NFT collection
    ├── mint-nft.md               ← Mint tokens
    ├── transfer-nft.md           ← Transfer & burn tokens
    ├── query-nft.md              ← Query collection state
    └── batch-nft.md              ← Batch operations
```

---

## Error Handling Reference

| Error | Cause | Fix |
|---|---|---|
| `execution reverted: ERC721: token already minted` | Token ID already exists | Use a different token ID |
| `execution reverted: ERC721: invalid token ID` | Token does not exist | Query `totalSupply()` first |
| `execution reverted: ERC721: transfer from incorrect owner` | Wrong sender | Check `ownerOf(tokenId)` |
| `execution reverted: ERC721: operator not approved` | Missing approval | Run `approve()` first |
| `insufficient funds` | Not enough PHRS for gas | Check `cast balance` |
| `connection refused` | Missing `--rpc-url` | Confirm `--rpc-url` is passed |
| `compiler error` | Solidity compilation failed | Run `foundryup` to update |

---

## Security Notes

- Never commit private keys to git
- Always use `$PRIVATE_KEY` environment variable
- Validate all addresses (must be `0x` + 40 hex chars)
- Confirm gas estimates before broadcast
- Metadata URIs should use `ipfs://` or `https://` for production
