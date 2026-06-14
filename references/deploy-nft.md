# Deploy NFT Collection Instructions

Teaches the AI agent how to deploy a PharosNFT collection contract on Pharos.

> **Network Configuration**: `<rpc_url>` is read from `assets/networks.json` (default: `atlantic-testnet`).
> **Private Key**: Must be passed via `--private-key $PRIVATE_KEY`.

---

## Overview

Deploys a full ERC-721 NFT collection with:
- EIP-2981 royalty support (configurable percentage)
- Mint price (payable minting)
- Max supply cap
- Token URI metadata
- Contract-level metadata
- Ownable (deployer is owner)
- Withdraw function for collected mint fees

---

## Step 1: Generate Deployment Script

The Agent generates `script/DeployNFT.s.sol` in the user's project:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import "../src/PharosNFT.sol";

contract DeployNFTScript is Script {
    function run() external {
        string memory name = "<collection_name>";
        string memory symbol = "<collection_symbol>";
        uint256 maxSupply = <max_supply>;
        uint256 mintPrice = <mint_price_in_wei>;
        address royaltyReceiver = <royalty_receiver_address>;
        uint96 royaltyFraction = <royalty_basis_points>;
        string memory contractURI = "<contract_metadata_uri>";

        vm.startBroadcast();
        PharosNFT nft = new PharosNFT(
            name,
            symbol,
            maxSupply,
            mintPrice,
            royaltyReceiver,
            royaltyFraction,
            contractURI
        );
        console.log("=== NFT Collection Deployed ===");
        console.log("Contract address:", address(nft));
        console.log("Name:", name);
        console.log("Symbol:", symbol);
        console.log("Max supply:", maxSupply);
        console.log("Mint price (wei):", mintPrice);
        console.log("Royalty receiver:", royaltyReceiver);
        console.log("Royalty fraction (bps):", royaltyFraction);
        vm.stopBroadcast();
    }
}
```

---

## Step 2: Set Up Project and Execute

### Command Template

```bash
# Initialize Foundry project (if not exists)
forge init nft-collection --no-commit
cd nft-collection

# Copy contract
cp <skill_path>/assets/nft/PharosNFT.sol src/PharosNFT.sol

# Install OpenZeppelin dependency
forge install OpenZeppelin/openzeppelin-contracts --no-commit

# Generate deploy script
# (Agent fills in the template above)

# Execute deployment
forge script script/DeployNFT.s.sol:DeployNFTScript \
  --rpc-url <rpc_url> \
  --private-key $PRIVATE_KEY \
  --broadcast
```

---

## Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `<collection_name>` | string | Yes | Name of the NFT collection (e.g. "Pharos Punks") |
| `<collection_symbol>` | string | Yes | Ticker symbol (e.g. "PPUNK") |
| `<max_supply>` | uint256 | Yes | Maximum number of tokens (e.g. 10000) |
| `<mint_price_in_wei>` | uint256 | Yes | Price per mint in wei (0 = free mint) |
| `<royalty_receiver_address>` | address | Yes | Wallet that receives royalty fees |
| `<royalty_basis_points>` | uint96 | Yes | Royalty in basis points (250 = 2.5%) |
| `<contract_metadata_uri>` | string | Yes | URI for contract-level metadata |

### Mint Price Conversion

| Human Readable | Wei |
|---|---|
| 0 (free mint) | 0 |
| 0.01 PHRS | 10000000000000000 |
| 0.1 PHRS | 100000000000000000 |
| 1 PHRS | 1000000000000000000 |

---

## Output Parsing

| Field | Description |
|---|---|
| `Contract address:` | Deployed NFT contract address — save this |
| `Name:` | Collection name (confirm matches input) |
| `Symbol:` | Collection symbol (confirm matches input) |
| `Max supply:` | Maximum token supply cap |
| `Mint price (wei):` | Price per mint in wei |
| `Royalty receiver:` | Address receiving royalties |
| `Royalty fraction (bps):` | Royalty percentage in basis points |

---

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| `compiler error` | Solidity compilation failed | Check Foundry version (`foundryup`), verify OpenZeppelin dependency |
| `insufficient funds` | Not enough PHRS for gas | Check balance: `cast balance <addr> --rpc-url <rpc> --ether` |
| `connection refused` | Missing or wrong `--rpc-url` | Read rpcUrl from `assets/networks.json` |
| `constructor args mismatch` | Wrong parameter count/types | Verify all 7 constructor parameters match |
| `execution reverted` | Contract logic revert | Check maxSupply > 0, royalty fraction <= 10000 |

---

## Post-Deployment

After successful deployment, the Agent should:

1. **Show explorer link**: `<explorer_url>/address/<contract_address>`
2. **Verify contract** (optional):

```bash
forge verify-contract <contract_address> src/PharosNFT.sol:PharosNFT \
  --chain-id <chain_id> \
  --verifier-url <explorer_api_url>/v1/explorer/command_api/contract \
  --verifier blockscout \
  --constructor-args $(cast abi-encode "constructor(string,string,uint256,uint256,address,uint96,string)" \
    "<name>" "<symbol>" <maxSupply> <mintPrice> <royaltyReceiver> <royaltyFraction> "<contractURI>")
```

3. **Ask user**: "What would you like to do next? Mint tokens, check collection info, or deploy another collection?"

---

## Agent Guidelines

1. Verify Foundry is installed (`which cast && which forge`)
2. Ask user for collection parameters (name, symbol, max supply, mint price, royalty)
3. Compute mint price in wei using `cast --to-wei <amount>` if user provides in PHRS
4. Generate deploy script with user's parameters filled in
5. Copy `assets/nft/PharosNFT.sol` to user project at `src/PharosNFT.sol`
6. Install OpenZeppelin dependency via forge
7. Read RPC URL from `assets/networks.json`
8. Check deployer balance: `cast balance <deployer> --rpc-url <rpc> --ether`
9. Run `forge build` to verify compilation
10. Execute `forge script` with `--broadcast`
11. Parse output for contract address
12. Show block explorer link
13. Offer to verify contract
