import { useState } from "react";
import { Plus, Trash2 } from "lucide-react";

export default function BatchOperations() {
  const [contract, setContract] = useState("");
  const [entries, setEntries] = useState([{ address: "", uri: "ipfs://.../metadata.json" }]);
  const [processing, setProcessing] = useState(false);

  const addRow = () => setEntries([...entries, { address: "", uri: "ipfs://.../metadata.json" }]);
  const removeRow = (i: number) => entries.length > 1 && setEntries(entries.filter((_, j) => j !== i));
  const update = (i: number, k: "address" | "uri", v: string) => {
    const copy = [...entries];
    copy[i] = { ...copy[i], [k]: v };
    setEntries(copy);
  };

  const handleAirdrop = async () => {
    setProcessing(true);
    await new Promise((r) => setTimeout(r, 2000));
    alert(`Airdropped ${entries.length} NFTs! (simulated)`);
    setProcessing(false);
  };

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Batch Operations</h1>
        <p className="text-sm text-[#9999CC]">Airdrop NFTs to multiple addresses in one transaction</p>
      </div>

      <div className="rounded-xl bg-[#1a1040] border border-[#2A1A5A] p-6 space-y-4">
        <div>
          <label className="block text-xs text-[#9999CC] mb-1.5">Contract Address</label>
          <input value={contract} onChange={(e) => setContract(e.target.value)} placeholder="0x..." className="w-full px-3 py-2 rounded-lg bg-[#12102A] border border-[#3A2A6A] text-white text-sm font-mono focus:outline-none focus:border-[#6C5CE7]" />
        </div>

        <div className="flex items-center justify-between">
          <span className="text-xs text-[#9999CC]">Recipients ({entries.length})</span>
          <button onClick={addRow} className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-[#6C5CE7]/20 text-[#8B7CF7] text-xs hover:bg-[#6C5CE7]/30 transition-all">
            <Plus size={14} /> Add Row
          </button>
        </div>

        <div className="space-y-2 max-h-64 overflow-y-auto">
          {entries.map((e, i) => (
            <div key={i} className="flex gap-2 items-center">
              <input value={e.address} onChange={(v) => update(i, "address", v.target.value)} placeholder="0x..." className="flex-1 px-3 py-2 rounded-lg bg-[#12102A] border border-[#3A2A6A] text-white text-xs font-mono focus:outline-none focus:border-[#6C5CE7]" />
              <input value={e.uri} onChange={(v) => update(i, "uri", v.target.value)} placeholder="ipfs://..." className="flex-1 px-3 py-2 rounded-lg bg-[#12102A] border border-[#3A2A6A] text-white text-xs font-mono focus:outline-none focus:border-[#6C5CE7]" />
              <button onClick={() => removeRow(i)} className="p-2 rounded-lg hover:bg-red-500/10 text-red-400 transition-all">
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>

        <div className="rounded-lg bg-[#0a0a1a] border border-[#2A1A5A] p-3">
          <p className="text-xs text-[#6666AA]">Batch size: {entries.length} NFTs · Estimated gas: {entries.length * 50000} gas</p>
        </div>

        <button
          onClick={handleAirdrop}
          disabled={processing || !contract || entries.some((e) => !e.address)}
          className="w-full py-3 rounded-xl bg-gradient-to-r from-[#6C5CE7] to-[#00D2FF] text-white font-semibold hover:opacity-90 disabled:opacity-40 transition-all shadow-lg shadow-purple-600/20"
        >
          {processing ? "Processing Airdrop..." : `Airdrop to ${entries.length} Addresses`}
        </button>
      </div>
    </div>
  );
}
