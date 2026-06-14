# Transfer & Burn NFT Instructions

Teaches the AI agent how to transfer and burn NFTs on Pharos.

---

## Transfer NFT

### Step 1 — Verify Ownership

```bash
cast call <contract_address> "ownerOf(uint256)(address)" <token_id> --rpc-url <rpc_url>
```

If the caller is NOT the owner, check approval:

```bash
cast call <contract_address> "getApproved(uint256)(address)" <token_id> --rpc-url <rpc_url>
```

### Step 2 — Transfer From

#### Standard Transfer

```bash
cast send <contract_address> \
  "transferFrom(address,address,uint256)" \
  <from_address> \
  <to_address> \
  <token_id> \
  --private-key $PRIVATE_KEY \
  --rpc-url <rpc_url>
```

#### Safe Transfer From (Recommended — checks recipient can receive ERC-721)

```bash
cast send <contract_address> \
  "safeTransferFrom(address,address,uint256)" \
  <from_address> \
  <to_address> \
  <token_id> \
  --private-key $PRIVATE_KEY \
  --rpc-url <rpc_url>
```

#### Safe Transfer From With Data

```bash
cast send <contract_address> \
  "safeTransferFrom(address,address,uint256,bytes)" \
  <from_address> \
  <to_address> \
  <token_id> \
  <data_hex> \
  --private-key $PRIVATE_KEY \
  --rpc-url <rpc_url>
```

### Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `<contract_address>` | address | Yes | NFT contract address |
| `<from_address>` | address | Yes | Current owner of the token |
| `<to_address>` | address | Yes | Recipient address |
| `<token_id>` | uint256 | Yes | Token ID to transfer |
| `<data_hex>` | bytes | No | Additional data (hex-encoded) |

### Output Parsing

| Field | Description |
|---|---|
| `status` | `1` = success |
| `transactionHash` | TX hash for explorer |

### Error Handling

| Error | Cause | Fix |
|---|---|---|
| `ERC721: transfer from incorrect owner` | `from_address` is not the owner | Check `ownerOf(tokenId)` |
| `ERC721: operator not approved` | Sender not approved to transfer | Run `approve()` or use owner's key |
| `ERC721: transfer to non ERC721Receiver implementer` | Recipient contract can't receive NFTs | Use `transferFrom` instead of `safeTransferFrom` |
| `ERC721: invalid token ID` | Token does not exist | Check `totalSupply()` |

---

## Approve Operator

### Approve Single Token

```bash
cast send <contract_address> \
  "approve(address,uint256)" \
  <operator_address> \
  <token_id> \
  --private-key $PRIVATE_KEY \
  --rpc-url <rpc_url>
```

### Set Approval For All (Marketplace Pattern)

```bash
cast send <contract_address> \
  "setApprovalForAll(address,bool)" \
  <operator_address> \
  true \
  --private-key $PRIVATE_KEY \
  --rpc-url <rpc_url>
```

### Check Approval

```bash
cast call <contract_address> "getApproved(uint256)(address)" <token_id> --rpc-url <rpc_url>
```

```bash
cast call <contract_address> "isApprovedForAll(address,address)(bool)" <owner> <operator> --rpc-url <rpc_url>
```

---

## Burn Token

### Command Template

The PharosNFT contract does not include a public burn function by default.
For burning, transfer the token to a burn address (`0x000000000000000000000000000000000000dEaD`):

```bash
cast send <contract_address> \
  "transferFrom(address,address,uint256)" \
  <owner_address> \
  0x000000000000000000000000000000000000dEaD \
  <token_id> \
  --private-key $PRIVATE_KEY \
  --rpc-url <rpc_url>
```

---

## Agent Guidelines

1. Always verify ownership first: `ownerOf(tokenId)`
2. If caller is not owner, check if caller is approved
3. If neither, inform user they don't have permission
4. Prefer `safeTransferFrom` over `transferFrom` (prevents lost NFTs)
5. After transfer, confirm new owner: `ownerOf(tokenId)`
6. Show explorer link for the transaction
7. Always confirm with user before executing write operations
