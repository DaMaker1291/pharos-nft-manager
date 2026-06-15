export const PHAROS_NFT_ABI = [
  "function name() view returns (string)",
  "function symbol() view returns (string)",
  "function totalSupply() view returns (uint256)",
  "function balanceOf(address owner) view returns (uint256)",
  "function ownerOf(uint256 tokenId) view returns (address)",
  "function tokenURI(uint256 tokenId) view returns (string)",
  "function maxSupply() view returns (uint256)",
  "function mintPrice() view returns (uint256)",
  "function royaltyFee() view returns (uint256)",
  "function royaltyReceiver() view returns (address)",
  "function safeMint(address to, string calldata uri) payable returns (uint256)",
  "function safeTransferFrom(address from, address to, uint256 tokenId)",
  "function approve(address to, uint256 tokenId)",
  "function getApproved(uint256 tokenId) view returns (address)",
  "function isApprovedForAll(address owner, address operator) view returns (bool)",
  "function setApprovalForAll(address operator, bool approved)",
  "function batchMint(address to, string[] calldata uris) payable returns (uint256[])",
  "function setRoyaltyFee(uint256 fee)",
  "function royaltyInfo(uint256 tokenId, uint256 salePrice) external view returns (address, uint256)",
  "function supportsInterface(bytes4 interfaceId) view returns (bool)",
  "event Transfer(address indexed from, address indexed to, uint256 indexed tokenId)",
  "event Minted(address indexed to, uint256 indexed tokenId, string uri)",
  "event RoyaltySet(uint256 fee, address receiver)",
];

export const ERC721_ABI = [
  "function name() view returns (string)",
  "function symbol() view returns (string)",
  "function totalSupply() view returns (uint256)",
  "function balanceOf(address owner) view returns (uint256)",
  "function ownerOf(uint256 tokenId) view returns (address)",
  "function tokenURI(uint256 tokenId) view returns (string)",
  "function safeTransferFrom(address from, address to, uint256 tokenId)",
  "function transferFrom(address from, address to, uint256 tokenId)",
  "function approve(address to, uint256 tokenId)",
  "function getApproved(uint256 tokenId) view returns (address)",
  "function isApprovedForAll(address owner, address operator) view returns (bool)",
  "function setApprovalForAll(address operator, bool approved)",
  "function supportsInterface(bytes4 interfaceId) view returns (bool)",
];

export const PHAROS_NFT_BYTECODE = "0x";

export const PHAROS_CHAIN_ID = 1089;

export const PHAROS_RPC_URLS: Record<number, string> = {
  1089: "https://rpc.pharos.network",
};

export const PHAROS_EXPLORER_URLS: Record<number, string> = {
  1089: "https://explorer.pharos.network",
};

export const CHAIN_INFO: Record<number, { name: string; symbol: string }> = {
  1089: { name: "Pharos Network", symbol: "PHAROS" },
};

export const DEFAULT_IPFS_GATEWAY = "https://ipfs.io/ipfs/";
export const DEFAULT_METADATA_URI = "ipfs://bafybeigdyrzt5sfp7udm7hu76uh7y26nf4c4j3wk5f7x7j5k5k5k5k5k5i/metadata.json";
