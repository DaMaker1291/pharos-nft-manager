# Query NFT Collection Instructions

Teaches the AI agent how to query NFT collection state on Pharos.

---

## Collection Info

### Name & Symbol

```bash
cast call <contract_address> "name()(string)" --rpc-url <rpc_url>
cast call <contract_address> "symbol()(string)" --rpc-url <rpc_url>
```

### Total Supply & Max Supply

```bash
cast call <contract_address> "totalSupply()(uint256)" --rpc-url <rpc_url>
cast call <contract_address> "maxSupply()(uint256)" --rpc-url <rpc_url>
```

### Mint Price

```bash
cast call <contract_address> "mintPrice()(uint256)" --rpc-url <rpc_url>
```

Human-readable: `cast --from-wei <mint_price>`

### Owner (Contract Admin)

```bash
cast call <contract_address> "owner()(address)" --rpc-url <rpc_url>
```

### Contract URI

```bash
cast call <contract_address> "contractURI()(string)" --rpc-url <rpc_url>
```

---

## Token Queries

### Token Owner

```bash
cast call <contract_address> "ownerOf(uint256)(address)" <token_id> --rpc-url <rpc_url>
```

### Token URI (Metadata)

```bash
cast call <contract_address> "tokenURI(uint256)(string)" <token_id> --rpc-url <rpc_url>
```

### Fetch Remote Metadata

If token URI is HTTP(S), fetch and display:

```bash
curl -s <token_uri> | jq .
```

---

## Wallet Queries

### Balance Of (Number of NFTs owned)

```bash
cast call <contract_address> "balanceOf(address)(uint256)" <wallet_address> --rpc-url <rpc_url>
```

### Tokens of Owner

The contract uses sequential token IDs (1 to totalSupply). Iterate to find all tokens for an address:

```bash
# Set variables
export CONTRACT=<contract_address>
export OWNER=<wallet_address>
export RPC=<rpc_url>

# Loop through tokens (bash)
for id in $(seq 1 $(cast call $CONTRACT "totalSupply()(uint256)" --rpc-url $RPC)); do
  owner=$(cast call $CONTRACT "ownerOf(uint256)(address)" $id --rpc-url $RPC)
  if [[ "${owner,,}" == "${OWNER,,}" ]]; then
    uri=$(cast call $CONTRACT "tokenURI(uint256)(string)" $id --rpc-url $RPC)
    echo "Token #$id | URI: $uri"
  fi
done
```

---

## Royalty Info

### Royalty Receiver

```bash
cast call <contract_address> "royaltyReceiver()(address)" --rpc-url <rpc_url>
```

### Royalty Fraction

```bash
cast call <contract_address> "royaltyFraction()(uint96)" --rpc-url <rpc_url>
```

Fraction is in basis points (250 = 2.5%).

### Calculate Royalty

```bash
cast call <contract_address> "royaltyInfo(uint256,uint256)(address,uint256)" \
  <token_id> \
  <sale_price_wei> \
  --rpc-url <rpc_url>
```

---

## Event Queries

### Transfer Events (All)

```bash
cast logs \
  --rpc-url <rpc_url> \
  --address <contract_address> \
  "Transfer(address indexed from, address indexed to, uint256 indexed tokenId)"
```

### Transfers From/To Specific Address

```bash
# Transfers FROM an address
cast logs \
  --rpc-url <rpc_url> \
  --address <contract_address> \
  --topic2 <address_padded_hex> \
  "Transfer(address indexed from, address indexed to, uint256 indexed tokenId)"

# Transfers TO an address
cast logs \
  --rpc-url <rpc_url> \
  --address <contract_address> \
  --topic3 <address_padded_hex> \
  "Transfer(address indexed from, address indexed to, uint256 indexed tokenId)"
```

For topic filtering, pad address to 64 hex chars (no `0x`): `000000000000000000000000<address_without_0x>`.

---

## Metadata Generation

### Generate JSON Metadata File

```bash
cat > metadata.json << 'EOF'
{
  "name": "<token_name>",
  "description": "<token_description>",
  "image": "<image_url>",
  "attributes": [
    {
      "trait_type": "<trait_name>",
      "value": "<trait_value>"
    }
  ]
}
EOF

cat metadata.json | jq .
```

### Upload to IPFS (via CLI)

```bash
# Requires ipfs CLI or curl to pinning service
curl -X POST -F "file=@metadata.json" https://api.pinata.cloud/pinning/pinFileToIPFS \
  -H "pinata_api_key: <key>" \
  -H "pinata_secret_api_key: <secret>"
```

Or use a local gateway:

```bash
ipfs add metadata.json
# Returns: QmHash...
```

---

## Aggregate Collection Report

For a full collection overview, the Agent should run all checks and format a report:

```
=== NFT Collection Report ===
Contract: 0x...
Name: Pharos Punks
Symbol: PPUNK
Owner: 0x... (deployer)
Total Minted: 42 / 10000
Mint Price: 0.01 PHRS
Royalty: 2.5% → 0x...

Recent Activity:
- Last 5 mints: Token #42 to 0x...
- Floor tracking: N/A (no marketplace)
```

---

## Agent Guidelines

1. Always check `totalSupply()` first to know collection size
2. For wallet queries, show human-readable PHRS values (use `cast --from-wei`)
3. When displaying addresses, show truncated form: `0x1234...5678`
4. Format URIs as clickable links when possible
5. For event queries, limit results and show newest first
6. Convert timestamps to human-readable dates
7. Offer to mint or transfer after showing collection status
