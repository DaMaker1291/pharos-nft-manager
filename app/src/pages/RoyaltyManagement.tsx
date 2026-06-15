import { useState } from "react";

export default function RoyaltyManagement() {
  const [contract, setContract] = useState("");
  const [fee, setFee] = useState("250");
  const [receiver, setReceiver] = useState("");
  const [processing, setProcessing] = useState(false);

  const handleSetRoyalty = async () => {
    setProcessing(true);
    await new Promise((r) => setTimeout(r, 1500));
    alert("Royalty updated! (simulated)");
    setProcessing(false);
  };

  const handleQueryRoyalty = async () => {
    await new Promise((r) => setTimeout(r, 500));
    setReceiver("0x7F9...3E2B");
    alert("Current royalty: 2.5% to 0x7F9...3E2B (simulated)");
  };

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Royalty Management</h1>
        <p className="text-sm text-[#9999CC]">Configure EIP-2981 creator fees on your NFT collections</p>
      </div>

      <div className="rounded-xl bg-[#1a1040] border border-[#2A1A5A] p-6 space-y-4">
        <div>
          <label className="block text-xs text-[#9999CC] mb-1.5">Contract Address</label>
          <input value={contract} onChange={(e) => setContract(e.target.value)} placeholder="0x..." className="w-full px-3 py-2 rounded-lg bg-[#12102A] border border-[#3A2A6A] text-white text-sm font-mono focus:outline-none focus:border-[#6C5CE7]" />
        </div>

        <button
          onClick={handleQueryRoyalty}
          disabled={!contract}
          className="w-full py-2 rounded-lg bg-[#12102A] border border-[#3A2A6A] text-[#00D2FF] text-sm hover:border-[#00D2FF] transition-all disabled:opacity-40"
        >
          Query Current Royalty
        </button>

        <div className="border-t border-[#2A1A5A] pt-4">
          <h3 className="text-sm font-semibold text-white mb-4">Set Royalty</h3>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-xs text-[#9999CC] mb-1.5">Royalty Fee (basis points)</label>
              <input type="number" value={fee} onChange={(e) => setFee(e.target.value)} className="w-full px-3 py-2 rounded-lg bg-[#12102A] border border-[#3A2A6A] text-white text-sm focus:outline-none focus:border-[#6C5CE7]" />
              <p className="text-[10px] text-[#6666AA] mt-0.5">100 = 1% · 250 = 2.5% · 1000 = 10%</p>
            </div>
            <div>
              <label className="block text-xs text-[#9999CC] mb-1.5">Receiver Address</label>
              <input value={receiver} onChange={(e) => setReceiver(e.target.value)} placeholder="0x..." className="w-full px-3 py-2 rounded-lg bg-[#12102A] border border-[#3A2A6A] text-white text-sm font-mono focus:outline-none focus:border-[#6C5CE7]" />
            </div>
          </div>

          <div className="rounded-lg bg-[#0a0a1a] border border-[#2A1A5A] p-3">
            <div className="flex justify-between text-sm">
              <span className="text-[#9999CC]">EIP-2981 Royalty Info</span>
              <span className="text-[#FFD700] font-mono text-xs">{Number(fee) / 100}% → {receiver || "0x..."}</span>
            </div>
          </div>

          <button
            onClick={handleSetRoyalty}
            disabled={processing || !contract || !receiver}
            className="w-full mt-4 py-3 rounded-xl bg-gradient-to-r from-[#6C5CE7] to-[#00D2FF] text-white font-semibold hover:opacity-90 disabled:opacity-40 transition-all shadow-lg shadow-purple-600/20"
          >
            {processing ? "Updating..." : "Set Royalty"}
          </button>
        </div>
      </div>
    </div>
  );
}
