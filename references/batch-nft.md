# Batch NFT Operations Instructions

Teaches the AI agent how to perform batch operations on Pharos NFT collections.

---

## Batch Mint

### Overview

Mint multiple NFTs to multiple addresses in a single transaction using `mintBatch()`.

### Step 1 — Prepare Recipients and URIs

Create a JSON file with recipient addresses and metadata URIs:

```json
{
  "mints": [
    {"to": "0xAddress1", "uri": "ipfs://QmHash1"},
    {"to": "0xAddress2", "uri": "ipfs://QmHash2"},
    {"to": "0xAddress3", "uri": "ipfs://QmHash3"}
  ]
}
```

### Step 2 — Calculate Total Cost

```bash
cast call <contract_address> "mintPrice()(uint256)" --rpc-url <rpc_url>
```

Total = `mintPrice * numberOfRecipients`.

### Step 3 — Execute Batch Mint

```bash
cast send <contract_address> \
  "mintBatch(address[],string[])" \
  "[<addr1>,<addr2>,<addr3>]" \
  "[<uri1>,<uri2>,<uri3>]" \
  --value <total_mint_price_wei> \
  --private-key $PRIVATE_KEY \
  --rpc-url <rpc_url>
```

### Array Encoding

For `forge script`, encode arrays properly:

```solidity
address[] memory recipients = new address[](3);
recipients[0] = 0xAddr1;
recipients[1] = 0xAddr2;
recipients[2] = 0xAddr3;

string[] memory uris = new string[](3);
uris[0] = "ipfs://hash1";
uris[1] = "ipfs://hash2";
uris[2] = "ipfs://hash3";
```

For `cast send`, use array literal syntax:

```bash
cast send <addr> "mintBatch(address[],string[])" \
  "[0xAddr1,0xAddr2,0xAddr3]" \
  "[uri1,uri2,uri3]" \
  --value <total> \
  --private-key $PRIVATE_KEY \
  --rpc-url <rpc_url>
```

### Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `<contract_address>` | address | Yes | NFT contract address |
| Recipients array | address[] | Yes | Array of recipient addresses |
| URIs array | string[] | Yes | Array of metadata URIs (must match length) |
| `<total_mint_price_wei>` | uint256 | Yes | `mintPrice * recipients.length` |

### Error Handling

| Error | Cause | Fix |
|---|---|---|
| `Array length mismatch` | Recipients and URIs have different lengths | Ensure both arrays have same length |
| `Empty arrays` | One or both arrays are empty | Provide at least 1 recipient and URI |
| `Insufficient payment` | `--value` < `mintPrice * count` | Calculate total correctly |
| `Max supply would be exceeded` | Not enough supply for batch | Reduce batch size |

---

## Batch Transfer

### Overview

Transfer multiple NFTs to one or multiple recipients in sequence.

### Single Recipient, Multiple Tokens

```bash
cast send <contract_address> \
  "safeTransferFrom(address,address,uint256)" \
  <from_address> \
  <to_address> \
  <token_id_1> \
  --private-key $PRIVATE_KEY \
  --rpc-url <rpc_url>

cast send <contract_address> \
  "safeTransferFrom(address,address,uint256)" \
  <from_address> \
  <to_address> \
  <token_id_2> \
  --private-key $PRIVATE_KEY \
  --rpc-url <rpc_url>
```

### Multiple Recipients (Airdrop Pattern)

```bash
# Set up arrays
RECIPIENTS=("0xAddr1" "0xAddr2" "0xAddr3")
TOKEN_IDS=(1 2 3)

# Loop through transfers
for i in "${!RECIPIENTS[@]}"; do
  cast send <contract_address> \
    "safeTransferFrom(address,address,uint256)" \
    <from_address> \
    "${RECIPIENTS[$i]}" \
    "${TOKEN_IDS[$i]}" \
    --private-key $PRIVATE_KEY \
    --rpc-url <rpc_url>
  echo "Transferred token ${TOKEN_IDS[$i]} to ${RECIPIENTS[$i]}"
done
```

---

## Batch Airdrop (NFT Distribution)

Distribute newly minted NFTs to multiple addresses:

### Generate Deploy Script

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import "../src/PharosNFT.sol";

contract AirdropScript is Script {
    function run() external {
        address contractAddr = <contract_address>;
        PharosNFT nft = PharosNFT(contractAddr);

        address[] memory recipients = new address[](3);
        recipients[0] = 0xAddr1;
        recipients[1] = 0xAddr2;
        recipients[2] = 0xAddr3;

        string[] memory uris = new string[](3);
        uris[0] = "ipfs://hash1";
        uris[1] = "ipfs://hash2";
        uris[2] = "ipfs://hash3";

        vm.startBroadcast();
        nft.mintBatch(recipients, uris);
        vm.stopBroadcast();

        for (uint i = 0; i < recipients.length; i++) {
            console.log("Minted token %s to %s", uris[i], recipients[i]);
        }
    }
}
```

### Execute Airdrop

```bash
forge script script/Airdrop.s.sol:AirdropScript \
  --rpc-url <rpc_url> \
  --private-key $PRIVATE_KEY \
  --broadcast
```

---

## Batch Approval for Marketplace

### Approve Operator for All Tokens (Once)

```bash
cast send <contract_address> \
  "setApprovalForAll(address,bool)" \
  <marketplace_address> \
  true \
  --private-key $PRIVATE_KEY \
  --rpc-url <rpc_url>
```

---

## Batch Token Query

Query multiple token owners:

```bash
for id in 1 2 3 4 5; do
  owner=$(cast call <contract_address> "ownerOf(uint256)(address)" $id --rpc-url <rpc_url>)
  uri=$(cast call <contract_address> "tokenURI(uint256)(string)" $id --rpc-url <rpc_url>)
  echo "Token #$id | Owner: $owner | URI: $uri"
done
```

---

## Agent Guidelines

1. For batch mint: always calculate total price = `mintPrice * count`
2. Verify sender has enough balance for total price + gas
3. Confirm arrays have matching lengths before execution
4. For batch transfer: check each token ownership first
5. Show progress for each operation in batch
6. After batch complete, show summary: "Minted/transferred X tokens"
7. Offer to verify with `ownerOf()` for a sample of tokens
8. Keep batch sizes reasonable (recommend max 50 per batch for gas limits)
