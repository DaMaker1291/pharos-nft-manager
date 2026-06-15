import { useState } from "react";
import { Search, ExternalLink } from "lucide-react";

export default function QueryCollection() {
  const [contract, setContract] = useState("");
  const [tokenId, setTokenId] = useState("");
  const [owner, setOwner] = useState("");
  const [query, setQuery] = useState<"info" | "owner" | "uri" | "balance">("info");
  const [results, setResults] = useState<Record<string, string> | null>(null);
  const [loading, setLoading] = useState(false);

  const handleQuery = async () => {
    setLoading(true);
    await new Promise((r) => setTimeout(r, 800));
    if (query === "info") setResults({ name: "Pharos Punks", symbol: "PPUNK", totalSupply: "1,247", maxSupply: "10,000", mintPrice: "0.001 ETH", royaltyFee: "2.5%", royaltyReceiver: "0x7F9...3E2B" });
    else if (query === "owner") setResults({ owner: "0x4C2...7E3F" });
    else if (query === "uri") setResults({ uri: "ipfs://bafybeig...metadata.json" });
    else setResults({ balance: "5 NFTs" });
    setLoading(false);
  };

  const queries = [
    { key: "info", label: "Collection Info" },
    { key: "owner", label: "Token Owner" },
    { key: "uri", label: "Token URI" },
    { key: "balance", label: "Owner Balance" },
  ];

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Query Collection</h1>
        <p className="text-sm text-[#9999CC]">Read on-chain state of any NFT collection</p>
      </div>

      <div className="rounded-xl bg-[#1a1040] border border-[#2A1A5A] p-6 space-y-4">
        <div>
          <label className="block text-xs text-[#9999CC] mb-1.5">Contract Address</label>
          <input value={contract} onChange={(e) => setContract(e.target.value)} placeholder="0x..." className="w-full px-3 py-2 rounded-lg bg-[#12102A] border border-[#3A2A6A] text-white text-sm font-mono focus:outline-none focus:border-[#6C5CE7]" />
        </div>

        <div className="flex gap-2 p-1 rounded-lg bg-[#0a0a1a] w-fit flex-wrap">
          {queries.map((q) => (
            <button key={q.key} onClick={() => setQuery(q.key as typeof query)} className={`px-4 py-1.5 rounded-md text-xs font-medium transition-all ${query === q.key ? "bg-[#6C5CE7] text-white" : "text-[#9999CC]"}`}>{q.label}</button>
          ))}
        </div>

        {(query === "owner" || query === "uri") && (
          <div>
            <label className="block text-xs text-[#9999CC] mb-1.5">Token ID</label>
            <input type="number" value={tokenId} onChange={(e) => setTokenId(e.target.value)} placeholder="1" className="w-full px-3 py-2 rounded-lg bg-[#12102A] border border-[#3A2A6A] text-white text-sm focus:outline-none focus:border-[#6C5CE7]" />
          </div>
        )}

        {query === "balance" && (
          <div>
            <label className="block text-xs text-[#9999CC] mb-1.5">Owner Address</label>
            <input value={owner} onChange={(e) => setOwner(e.target.value)} placeholder="0x..." className="w-full px-3 py-2 rounded-lg bg-[#12102A] border border-[#3A2A6A] text-white text-sm font-mono focus:outline-none focus:border-[#6C5CE7]" />
          </div>
        )}

        <button
          onClick={handleQuery}
          disabled={loading || !contract}
          className="w-full py-3 rounded-xl bg-gradient-to-r from-[#6C5CE7] to-[#00D2FF] text-white font-semibold hover:opacity-90 disabled:opacity-40 transition-all shadow-lg shadow-purple-600/20"
        >
          {loading ? "Querying..." : "Query"}
        </button>

        {results && (
          <div className="rounded-lg bg-[#0a0a1a] border border-[#2A1A5A] p-4">
            <div className="flex items-center gap-2 mb-3">
              <Search size={14} className="text-[#00FF88]" />
              <span className="text-xs text-[#00FF88] font-semibold">Results</span>
            </div>
            <div className="space-y-2">
              {Object.entries(results).map(([k, v]) => (
                <div key={k} className="flex justify-between text-sm">
                  <span className="text-[#9999CC] capitalize">{k.replace(/([A-Z])/g, ' $1').trim()}</span>
                  <span className="text-white font-mono text-xs">{v}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
