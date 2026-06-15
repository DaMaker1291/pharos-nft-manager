import { useState } from "react";

export default function TransferApprove() {
  const [contract, setContract] = useState("");
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [tokenId, setTokenId] = useState("");
  const [mode, setMode] = useState<"transfer" | "approve">("transfer");
  const [processing, setProcessing] = useState(false);

  const handleAction = async () => {
    setProcessing(true);
    await new Promise((r) => setTimeout(r, 1500));
    alert(`${mode === "transfer" ? "Transfer" : "Approval"} successful! (simulated)`);
    setProcessing(false);
  };

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Transfer & Approve</h1>
        <p className="text-sm text-[#9999CC]">Transfer NFTs or approve operators</p>
      </div>

      <div className="rounded-xl bg-[#1a1040] border border-[#2A1A5A] p-6 space-y-4">
        <div>
          <label className="block text-xs text-[#9999CC] mb-1.5">Contract Address</label>
          <input value={contract} onChange={(e) => setContract(e.target.value)} placeholder="0x..." className="w-full px-3 py-2 rounded-lg bg-[#12102A] border border-[#3A2A6A] text-white text-sm font-mono focus:outline-none focus:border-[#6C5CE7]" />
        </div>

        <div className="flex gap-2 p-1 rounded-lg bg-[#0a0a1a] w-fit">
          <button onClick={() => setMode("transfer")} className={`px-4 py-1.5 rounded-md text-xs font-medium transition-all ${mode === "transfer" ? "bg-[#6C5CE7] text-white" : "text-[#9999CC]"}`}>Transfer</button>
          <button onClick={() => setMode("approve")} className={`px-4 py-1.5 rounded-md text-xs font-medium transition-all ${mode === "approve" ? "bg-[#6C5CE7] text-white" : "text-[#9999CC]"}`}>Approve</button>
        </div>

        {mode === "transfer" ? (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-[#9999CC] mb-1.5">From Address</label>
              <input value={from} onChange={(e) => setFrom(e.target.value)} placeholder="0x..." className="w-full px-3 py-2 rounded-lg bg-[#12102A] border border-[#3A2A6A] text-white text-sm font-mono focus:outline-none focus:border-[#6C5CE7]" />
            </div>
            <div>
              <label className="block text-xs text-[#9999CC] mb-1.5">To Address</label>
              <input value={to} onChange={(e) => setTo(e.target.value)} placeholder="0x..." className="w-full px-3 py-2 rounded-lg bg-[#12102A] border border-[#3A2A6A] text-white text-sm font-mono focus:outline-none focus:border-[#6C5CE7]" />
            </div>
          </div>
        ) : (
          <div>
            <label className="block text-xs text-[#9999CC] mb-1.5">Operator Address</label>
            <input value={to} onChange={(e) => setTo(e.target.value)} placeholder="0x..." className="w-full px-3 py-2 rounded-lg bg-[#12102A] border border-[#3A2A6A] text-white text-sm font-mono focus:outline-none focus:border-[#6C5CE7]" />
          </div>
        )}

        <div>
          <label className="block text-xs text-[#9999CC] mb-1.5">Token ID</label>
          <input type="number" value={tokenId} onChange={(e) => setTokenId(e.target.value)} placeholder="1" className="w-full px-3 py-2 rounded-lg bg-[#12102A] border border-[#3A2A6A] text-white text-sm focus:outline-none focus:border-[#6C5CE7]" />
        </div>

        <button
          onClick={handleAction}
          disabled={processing || !contract || !to || !tokenId}
          className="w-full py-3 rounded-xl bg-gradient-to-r from-[#6C5CE7] to-[#00D2FF] text-white font-semibold hover:opacity-90 disabled:opacity-40 transition-all shadow-lg shadow-purple-600/20"
        >
          {processing ? "Processing..." : mode === "transfer" ? "Transfer Token" : "Approve Operator"}
        </button>
      </div>
    </div>
  );
}
