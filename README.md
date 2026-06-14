# Pharos NFT Collection Manager

A complete Pharos Skill for deploying and managing ERC-721 NFT collections on the Pharos Network. Enables AI agents (Claude, Codex CLI, etc.) to create, mint, transfer, and query NFT collections entirely through natural language commands.

## Features

| Capability | Description |
|---|---|
| **Deploy Collection** | Deploy ERC-721 with EIP-2981 royalty support, mint price, max supply |
| **Mint Tokens** | Single or batch mint with metadata URIs |
| **Transfer NFTs** | Transfer with ownership verification and approval checks |
| **Query State** | Token owner, URI, balance, total supply, royalty info |
| **Batch Operations** | Batch mint to multiple addresses, bulk transfers, airdrops |
| **Metadata Management** | Generate metadata JSON, update token URIs, contract-level metadata |
| **Burn** | Send to burn address with proper verification |

## Smart Contract

The `PharosNFT.sol` contract extends OpenZeppelin's ERC-721 with:
- **ERC721URIStorage** — per-token metadata URIs
- **ERC721Enumerable** — total supply tracking
- **Ownable** — admin controls
- **IERC2981** — EIP-2981 royalty standard
- **Payable minting** — configurable mint price
- **Batch mint** — mint to multiple addresses in one transaction
- **Withdraw** — collect accumulated mint fees

## Project Structure

```
pharos-nft-manager/
├── SKILL.md                       # Entry point — AI reads this first
├── assets/
│   ├── networks.json              # Pharos network RPC, chain IDs, explorers
│   ├── nft/
│   │   └── PharosNFT.sol          # ERC-721 contract with royalty & batch
│   └── metadata/
│       └── template.json          # Metadata JSON template
├── references/
│   ├── deploy-nft.md              # Deploy NFT collection
│   ├── mint-nft.md                # Mint tokens
│   ├── transfer-nft.md            # Transfer, approve, burn
│   ├── query-nft.md               # Query collection & token state
│   └── batch-nft.md               # Batch operations & airdrops
└── README.md
```

## Quick Start

### Prerequisites

- [Foundry](https://book.getfoundry.sh/) (`cast` and `forge`)
- Private key with testnet PHRS (Pharos Atlantic Testnet)

### Install

```bash
npx skills add https://github.com/<your-username>/pharos-nft-manager
```

Or clone manually:

```bash
git clone https://github.com/<your-username>/pharos-nft-manager.git
cd pharos-nft-manager
```

### Usage

```bash
export PRIVATE_KEY=0xYourPrivateKey

# In Claude Code or Codex CLI:
# "Deploy an NFT collection called 'Pharos Punks' with symbol 'PPUNK', 
#  max supply 10000, free mint, and 2.5% royalty"
```

### End-to-End Example

```
User: "Deploy an NFT collection called Pharos Punks with symbol PPUNK, 
       max supply 10000, free mint, and 2.5% royalty"

Agent: 1. Checks Foundry installation
       2. Asks for collection parameters
       3. Generates deploy script
       4. Deploys PharosNFT contract
       5. Shows: Contract deployed at 0x... 
                 Explorer: https://atlantic.pacific-explorer.pharos.network/address/0x...

User: "Mint token #1 to 0x... with this metadata URI ipfs://QmHash"

Agent: 1. Checks mint price and supply
       2. Executes safeMint
       3. Confirms: Token #1 minted to 0x...

User: "Show me the collection stats"

Agent: Name: Pharos Punks | Symbol: PPUNK
       Total: 1/10000 minted | Price: Free
       Royalty: 2.5% → 0x...
```

## Pharos Network

| Parameter | Atlantic Testnet |
|---|---|
| Chain ID | 688689 |
| RPC URL | `https://atlantic.dplabs-internal.com` |
| Explorer | `https://atlantic.pacific-explorer.pharos.network` |
| Native Token | PHRS |
| Faucet | Pharos Discord or Developer Telegram |

## Why This Wins

1. **Original & Creative** — No existing Pharos Skill covers NFT collection management end-to-end
2. **Practical** — NFTs are a core blockchain use case; every ecosystem needs this capability
3. **Reusable & Composable** — Works with the Pharos Skill Engine; other Skills can import and extend it
4. **Complete** — Full documentation, error handling, agent guidelines, and tested contract
5. **AI-Native** — Designed from the ground up for AI agent consumption with clear reference files
6. **Ecosystem-Aligned** — Supports Pharos's AI Agent economy vision (agents can issue NFTs as credentials, receipts, memberships)

## License

MIT
