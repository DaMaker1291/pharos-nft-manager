import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area } from "recharts";
import { getAccount, getBalance } from "../lib/web3";
import { Wallet, Upload, Stamp, ArrowRightLeft, Search, DollarSign } from "lucide-react";

const stats = [
  { label: "Collections Deployed", value: "3", change: "+2 this week", icon: Upload, color: "#6C5CE7" },
  { label: "Total NFTs Minted", value: "1,247", change: "+89 today", icon: Stamp, color: "#00D2FF" },
  { label: "Active Holders", value: "342", change: "+12.5%", icon: Wallet, color: "#00FF88" },
  { label: "Royalty Revenue", value: "4.8 ETH", change: "+0.3 ETH", icon: DollarSign, color: "#FFD700" },
];

const chartData = [
  { day: "Mon", mints: 12, transfers: 5 },
  { day: "Tue", mints: 19, transfers: 8 },
  { day: "Wed", mints: 25, transfers: 14 },
  { day: "Thu", mints: 18, transfers: 10 },
  { day: "Fri", mints: 30, transfers: 22 },
  { day: "Sat", mints: 42, transfers: 28 },
  { day: "Sun", mints: 35, transfers: 19 },
];

const recentActivity = [
  { action: "Mint", token: "#142", to: "0x7F9...3E2B", time: "2 min ago", status: "success" },
  { action: "Transfer", token: "#089", to: "0x3A1...8D4F", time: "15 min ago", status: "success" },
  { action: "Mint", token: "#141", to: "0xB8E...6C1A", time: "1 hour ago", status: "success" },
  { action: "Approval", token: "#133", to: "0xDeF...9A2B", time: "3 hours ago", status: "success" },
  { action: "Royalty Set", token: "-", to: "0x4C2...7E3F", time: "5 hours ago", status: "success" },
];

export default function Dashboard() {
  const [account, setAccount] = useState<string | null>(null);
  const [balance, setBalance] = useState("");

  useEffect(() => {
    getAccount().then(async (a) => {
      if (a) { setAccount(a); setBalance(await getBalance(a)); }
    });
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-sm text-[#9999CC]">Overview of your NFT ecosystem</p>
        </div>
        {account && (
          <div className="text-right text-sm">
            <p className="text-[#9999CC]">{account.slice(0, 8)}...{account.slice(-6)}</p>
            <p className="text-[#00FF88]">{Number(balance).toFixed(4)} PHAROS</p>
          </div>
        )}
      </div>

      <div className="grid grid-cols-4 gap-4">
        {stats.map((s) => (
          <div key={s.label} className="rounded-xl bg-[#1a1040] border border-[#2A1A5A] p-4 hover:border-[#6C5CE7]/50 transition-all">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: `${s.color}20` }}>
                <s.icon size={16} style={{ color: s.color }} />
              </div>
              <span className="text-xs text-[#9999CC]">{s.label}</span>
            </div>
            <p className="text-2xl font-bold text-white">{s.value}</p>
            <p className="text-xs text-[#00FF88]">{s.change}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2 rounded-xl bg-[#1a1040] border border-[#2A1A5A] p-5">
          <h3 className="text-sm font-semibold text-white mb-4">Network Activity (7 Days)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="mintsGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#6C5CE7" stopOpacity={0.3}/><stop offset="100%" stopColor="#6C5CE7" stopOpacity={0}/></linearGradient>
                <linearGradient id="xferGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#00D2FF" stopOpacity={0.3}/><stop offset="100%" stopColor="#00D2FF" stopOpacity={0}/></linearGradient>
              </defs>
              <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: "#6666AA", fontSize: 12 }} />
              <YAxis axisLine={false} tickLine={false} tick={{ fill: "#6666AA", fontSize: 12 }} />
              <Tooltip contentStyle={{ background: "#12102A", border: "1px solid #2A1A5A", borderRadius: 8, color: "#E8E8FF" }} />
              <Area type="monotone" dataKey="mints" stroke="#6C5CE7" fill="url(#mintsGrad)" strokeWidth={2} />
              <Area type="monotone" dataKey="transfers" stroke="#00D2FF" fill="url(#xferGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-xl bg-[#1a1040] border border-[#2A1A5A] p-5">
          <h3 className="text-sm font-semibold text-white mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {recentActivity.map((a, i) => (
              <div key={i} className="flex items-center gap-2 text-xs">
                <div className={`w-1.5 h-1.5 rounded-full ${a.status === "success" ? "bg-green-500" : "bg-yellow-500"}`} />
                <span className="text-[#6C5CE7] font-mono">{a.action}</span>
                <span className="text-[#9999CC]">{a.token}</span>
                <span className="text-[#6666AA] ml-auto">{a.time}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
