# Mint NFT Instructions

Teaches the AI agent how to mint NFTs to addresses on Pharos.

---

## Overview

Mint new tokens from a deployed PharosNFT collection. Supports:
- Single mint to one address
- Mint with metadata URI
- Check mint price and payment
- Update token URI after minting

---

## Step 1 — Check Collection State

Before minting, check the collection configuration:

### Get Mint Price

```bash
cast call <contract_address> "mintPrice()(uint256)" --rpc-url <rpc_url>
```

### Check Total Supply

```bash
cast call <contract_address> "totalSupply()(uint256)" --rpc-url <rpc_url>
```

### Check Max Supply

```bash
cast call <contract_address> "maxSupply()(uint256)" --rpc-url <rpc_url>
```

---

## Step 2 — Mint Single Token

### Command Template

```bash
cast send <contract_address> \
  "safeMint(address,string)" \
  <recipient_address> \
  "<token_uri>" \
  --value <mint_price_wei> \
  --private-key $PRIVATE_KEY \
  --rpc-url <rpc_url>
```

### Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `<contract_address>` | address | Yes | Deployed NFT contract address |
| `<recipient_address>` | address | Yes | Address that will receive the NFT |
| `<token_uri>` | string | Yes | URI pointing to token metadata (IPFS or HTTPS) |
| `<mint_price_wei>` | uint256 | Yes | Must equal `mintPrice()` exactly |
| `--value` | flag | Yes | Sends PHRS with the call (must match mint price) |

### Output Parsing

| Field | Description |
|---|---|
| `status` | `1` = success |
| `transactionHash` | TX hash for explorer lookup |
| Token ID | Auto-incremented, starting from 1 |

### Error Handling

| Error | Cause | Fix |
|---|---|---|
| `Insufficient payment` | `--value` < `mintPrice()` | Check `mintPrice()` and send exact amount |
| `Max supply reached` | `totalSupply()` >= `maxSupply()` | Collection is full, cannot mint more |
| `execution reverted` | Contract call failed | Verify contract address and parameters |
| `insufficient funds` | Not enough PHRS for gas + mint price | Check wallet balance |

---

## Step 3 — Prepare Metadata URI

### Option A: Generate Metadata File Locally

Create a `metadata.json` file:

```json
{
  "name": "Pharos NFT #1",
  "description": "My first Pharos NFT",
  "image": "ipfs://QmPlaceholderImageHash",
  "attributes": [
    { "trait_type": "Rarity", "value": "Common" },
    { "trait_type": "Color", "value": "Blue" }
  ]
}
```

For local testing, use a placeholder URI:

```bash
echo "ipfs://placeholder-metadata-$(date +%s)" > /tmp/nft-uri.txt
```

### Option B: Use HTTP URI

Provide a publicly accessible metadata JSON URL (must return valid JSON with `name`, `description`, `image` fields).

---

## Step 4 — Update Token URI

### Command Template

```bash
cast send <contract_address> \
  "setTokenURI(uint256,string)" \
  <token_id> \
  "<new_uri>" \
  --private-key $PRIVATE_KEY \
  --rpc-url <rpc_url>
```

### Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `<contract_address>` | address | Yes | NFT contract address |
| `<token_id>` | uint256 | Yes | Token ID to update (must exist) |
| `<new_uri>` | string | Yes | New metadata URI |

### Error Handling

| Error | Cause | Fix |
|---|---|---|
| `execution reverted: ERC721: invalid token ID` | Token does not exist | Query `totalSupply()` first |
| `execution reverted: Ownable: caller is not the owner` | Not contract owner | Must use owner's private key |

---

## Free Mint (Mint Price = 0)

If `mintPrice()` returns 0, omit the `--value` flag:

```bash
cast send <contract_address> \
  "safeMint(address,string)" \
  <recipient_address> \
  "<token_uri>" \
  --private-key $PRIVATE_KEY \
  --rpc-url <rpc_url>
```

---

## Agent Guidelines

1. Read `mintPrice()` from the contract — if > 0, user must send PHRS
2. Read `totalSupply()` and `maxSupply()` — confirm supply is available
3. Ask user for:
   - Recipient address
   - Metadata URI (or offer to generate a placeholder)
4. If `mintPrice() > 0`, check sender balance has enough for price + gas
5. Execute `cast send` with correct parameters
6. Parse transaction hash and token ID from events
7. Show result: `<explorer_url>/tx/<txHash>`
8. Confirm the mint by checking `ownerOf(tokenId)`
9. Ask: "Mint another? Or check the collection?"
