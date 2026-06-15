import { BrowserProvider, Contract, formatEther, parseEther, JsonRpcSigner, JsonRpcProvider } from "ethers";
import { PHAROS_NFT_ABI, PHAROS_CHAIN_ID, PHAROS_RPC_URLS, CHAIN_INFO } from "./contract";

let provider: BrowserProvider | null = null;
let signer: JsonRpcSigner | null = null;

export async function connectWallet(): Promise<string> {
  if (!window.ethereum) throw new Error("MetaMask not installed");
  const bp = new BrowserProvider(window.ethereum);
  const accounts = await bp.send("eth_requestAccounts", []);
  provider = bp;
  signer = await bp.getSigner();
  return accounts[0];
}

export async function switchChain(chainId: number = PHAROS_CHAIN_ID): Promise<void> {
  if (!window.ethereum) throw new Error("MetaMask not installed");
  try {
    await window.ethereum.request({ method: "wallet_switchEthereumChain", params: [{ chainId: `0x${chainId.toString(16)}` }] });
  } catch (e: any) {
    if (e.code === 4902) {
      const info = CHAIN_INFO[chainId];
      await window.ethereum.request({
        method: "wallet_addEthereumChain",
        params: [{ chainId: `0x${chainId.toString(16)}`, rpcUrls: [PHAROS_RPC_URLS[chainId]], chainName: info?.name || "Pharos", nativeCurrency: { name: info?.symbol || "PHAROS", symbol: info?.symbol || "PHAROS", decimals: 18 } }],
      });
    } else throw e;
  }
}

export function getProvider() { return provider; }
export function getSigner() { return signer; }

export async function getContract(address: string): Promise<Contract> {
  if (!signer) throw new Error("Wallet not connected");
  return new Contract(address, PHAROS_NFT_ABI, signer);
}

export async function getReadContract(address: string): Promise<Contract> {
  if (!provider) throw new Error("Provider not initialized");
  const rp = new JsonRpcProvider(PHAROS_RPC_URLS[PHAROS_CHAIN_ID]);
  return new Contract(address, PHAROS_NFT_ABI, rp);
}

export async function getAccount(): Promise<string | null> {
  if (!provider) return null;
  const acc = await provider.listAccounts();
  return acc.length > 0 ? acc[0].address : null;
}

export async function getBalance(address: string): Promise<string> {
  if (!provider) throw new Error("Provider not initialized");
  const bal = await provider.getBalance(address);
  return formatEther(bal);
}

export { formatEther, parseEther };
