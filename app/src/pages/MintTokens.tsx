import { useState } from "react";

export default function MintTokens() {
  const [contract, setContract] = useState("");
  const [to, setTo] = useState("");
  const [uri, setUri] = useState("ipfs://bafybeigdyrzt5sfp7udm7hu76uh7y26nf4c4j3wk5f7x7j5k5k5k5k5k5i/metadata.json");
  const [minting, setMinting] = useState(false);
  const [mode, setMode] = useState<"single" | "batch">("single");
  const [batchUris, setBatchUris] = useState("");

  const handleMint = async () => {
    setMinting(true);
    await new Promise((r) => setTimeout(r, 1500));
    alert("NFT minted! (simulated — connect wallet for real mint)");
    setMinting(false);
  };

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Mint Tokens</h1>
        <p className="text-sm text-[#9999CC]">Mint single or batch NFTs to any address</p>
      </div>

      <div className="rounded-xl bg-[#1a1040] border border-[#2A1A5A] p-6 space-y-4">
        <div>
          <label className="block text-xs text-[#9999CC] mb-1.5">Contract Address</label>
          <input value={contract} onChange={(e) => setContract(e.target.value)} placeholder="0x..." className="w-full px-3 py-2 rounded-lg bg-[#12102A] border border-[#3A2A6A] text-white text-sm font-mono focus:outline-none focus:border-[#6C5CE7]" />
        </div>

        <div>
          <label className="block text-xs text-[#9999CC] mb-1.5">Recipient Address</label>
          <input value={to} onChange={(e) => setTo(e.target.value)} placeholder="0x..." className="w-full px-3 py-2 rounded-lg bg-[#12102A] border border-[#3A2A6A] text-white text-sm font-mono focus:outline-none focus:border-[#6C5CE7]" />
        </div>

        <div className="flex gap-2 p-1 rounded-lg bg-[#0a0a1a] w-fit">
          <button onClick={() => setMode("single")} className={`px-4 py-1.5 rounded-md text-xs font-medium transition-all ${mode === "single" ? "bg-[#6C5CE7] text-white" : "text-[#9999CC]"}`}>Single Mint</button>
          <button onClick={() => setMode("batch")} className={`px-4 py-1.5 rounded-md text-xs font-medium transition-all ${mode === "batch" ? "bg-[#6C5CE7] text-white" : "text-[#9999CC]"}`}>Batch Mint</button>
        </div>

        {mode === "single" ? (
          <div>
            <label className="block text-xs text-[#9999CC] mb-1.5">Token URI (metadata)</label>
            <input value={uri} onChange={(e) => setUri(e.target.value)} className="w-full px-3 py-2 rounded-lg bg-[#12102A] border border-[#3A2A6A] text-white text-sm font-mono focus:outline-none focus:border-[#6C5CE7]" />
          </div>
        ) : (
          <div>
            <label className="block text-xs text-[#9999CC] mb-1.5">URIs (one per line)</label>
            <textarea value={batchUris} onChange={(e) => setBatchUris(e.target.value)} rows={4} placeholder="ipfs://.../1.json&#10;ipfs://.../2.json&#10;ipfs://.../3.json" className="w-full px-3 py-2 rounded-lg bg-[#12102A] border border-[#3A2A6A] text-white text-sm font-mono focus:outline-none focus:border-[#6C5CE7] placeholder:text-[#6666AA] resize-none" />
          </div>
        )}

        <button
          onClick={handleMint}
          disabled={minting || !contract || !to}
          className="w-full py-3 rounded-xl bg-gradient-to-r from-[#6C5CE7] to-[#00D2FF] text-white font-semibold hover:opacity-90 disabled:opacity-40 transition-all shadow-lg shadow-purple-600/20"
        >
          {minting ? "Minting..." : mode === "single" ? "Mint Token" : "Batch Mint Tokens"}
        </button>
      </div>
    </div>
  );
}
