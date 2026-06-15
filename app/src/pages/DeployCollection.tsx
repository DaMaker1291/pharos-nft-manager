import { useState } from "react";

export default function DeployCollection() {
  const [name, setName] = useState("");
  const [symbol, setSymbol] = useState("");
  const [maxSupply, setMaxSupply] = useState("10000");
  const [mintPrice, setMintPrice] = useState("0.001");
  const [royaltyFee, setRoyaltyFee] = useState("250");
  const [deploying, setDeploying] = useState(false);

  const handleDeploy = async () => {
    setDeploying(true);
    await new Promise((r) => setTimeout(r, 2000));
    alert("Collection deployed! (simulated — connect wallet for real deploy)");
    setDeploying(false);
  };

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Deploy Collection</h1>
        <p className="text-sm text-[#9999CC]">Launch a new ERC-721 NFT collection in one transaction</p>
      </div>

      <div className="rounded-xl bg-[#1a1040] border border-[#2A1A5A] p-6 space-y-5">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-[#9999CC] mb-1.5">Collection Name</label>
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Pharos Punks" className="w-full px-3 py-2 rounded-lg bg-[#12102A] border border-[#3A2A6A] text-white text-sm focus:outline-none focus:border-[#6C5CE7] placeholder:text-[#6666AA]" />
          </div>
          <div>
            <label className="block text-xs text-[#9999CC] mb-1.5">Symbol</label>
            <input value={symbol} onChange={(e) => setSymbol(e.target.value)} placeholder="PPUNK" className="w-full px-3 py-2 rounded-lg bg-[#12102A] border border-[#3A2A6A] text-white text-sm focus:outline-none focus:border-[#6C5CE7] placeholder:text-[#6666AA]" />
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-xs text-[#9999CC] mb-1.5">Max Supply</label>
            <input type="number" value={maxSupply} onChange={(e) => setMaxSupply(e.target.value)} className="w-full px-3 py-2 rounded-lg bg-[#12102A] border border-[#3A2A6A] text-white text-sm focus:outline-none focus:border-[#6C5CE7]" />
          </div>
          <div>
            <label className="block text-xs text-[#9999CC] mb-1.5">Mint Price (ETH)</label>
            <input type="number" step="0.001" value={mintPrice} onChange={(e) => setMintPrice(e.target.value)} className="w-full px-3 py-2 rounded-lg bg-[#12102A] border border-[#3A2A6A] text-white text-sm focus:outline-none focus:border-[#6C5CE7]" />
          </div>
          <div>
            <label className="block text-xs text-[#9999CC] mb-1.5">Royalty Fee (basis pts)</label>
            <input type="number" value={royaltyFee} onChange={(e) => setRoyaltyFee(e.target.value)} className="w-full px-3 py-2 rounded-lg bg-[#12102A] border border-[#3A2A6A] text-white text-sm focus:outline-none focus:border-[#6C5CE7]" />
            <p className="text-[10px] text-[#6666AA] mt-0.5">250 = 2.5%</p>
          </div>
        </div>

        <div className="rounded-lg bg-[#0a0a1a] p-3 border border-[#2A1A5A]">
          <p className="text-xs text-[#9999CC] mb-1">Deploy Script</p>
          <pre className="text-xs text-[#00FF88] font-mono">$ forge script DeployNFT.s.sol --broadcast --rpc-url &lt;rpc&gt;</pre>
        </div>

        <button
          onClick={handleDeploy}
          disabled={deploying || !name || !symbol}
          className="w-full py-3 rounded-xl bg-gradient-to-r from-[#6C5CE7] to-[#00D2FF] text-white font-semibold hover:opacity-90 disabled:opacity-40 transition-all shadow-lg shadow-purple-600/20"
        >
          {deploying ? "Deploying..." : "Deploy Collection"}
        </button>
      </div>
    </div>
  );
}
