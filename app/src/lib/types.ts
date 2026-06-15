export interface CollectionInfo {
  address: string;
  name: string;
  symbol: string;
  totalSupply: number;
  maxSupply: number;
  mintPrice: string;
  royaltyFee: number;
  royaltyReceiver: string;
  owner: string;
}

export interface TokenInfo {
  id: number;
  uri: string;
  owner: string;
}

export interface DeployParams {
  name: string;
  symbol: string;
  maxSupply: number;
  mintPrice: string;
  royaltyFee: number;
}

export interface MintParams {
  to: string;
  uri: string;
}

export interface TransferParams {
  from: string;
  to: string;
  tokenId: number;
}

export interface AirdropEntry {
  address: string;
  uri: string;
}
