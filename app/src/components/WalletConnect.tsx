import { useState } from "react";
import { connectWallet, switchChain, getAccount, getBalance } from "../lib/web3";
import { PHAROS_CHAIN_ID } from "../lib/contract";

export default function WalletConnect() {
  const [account, setAccount] = useState<string | null>(null);
  const [bal, setBal] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const handleConnect = async () => {
    setLoading(true);
    try {
      await switchChain(PHAROS_CHAIN_ID);
      const addr = await connectWallet();
      setAccount(addr);
      const b = await getBalance(addr);
      setBal(Number(b).toFixed(4));
    } catch (e: any) {
      alert(e.message);
    }
    setLoading(false);
  };

  if (account) {
    return (
      <div className="flex items-center gap-3 px-4 py-2 rounded-xl bg-[#12102A] border border-[#3A2A6A]">
        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
        <div>
          <p className="text-xs text-[#9999CC]">{account.slice(0, 6)}...{account.slice(-4)}</p>
          <p className="text-xs text-[#00FF88]">{bal} PHAROS</p>
        </div>
      </div>
    );
  }

  return (
    <button
      onClick={handleConnect}
      disabled={loading}
      className="px-5 py-2 rounded-xl bg-gradient-to-r from-[#6C5CE7] to-[#00D2FF] text-white font-semibold text-sm hover:opacity-90 disabled:opacity-50 transition-all shadow-lg shadow-purple-600/20"
    >
      {loading ? "Connecting..." : "Connect Wallet"}
    </button>
  );
}
