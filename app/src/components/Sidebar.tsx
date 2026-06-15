import { NavLink } from "react-router-dom";
import {
  LayoutDashboard, Upload, Stamp, ArrowRightLeft, Search,
  Users, DollarSign, Wallet
} from "lucide-react";

const links = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard", end: true },
  { to: "/deploy", icon: Upload, label: "Deploy Collection" },
  { to: "/mint", icon: Stamp, label: "Mint Tokens" },
  { to: "/transfer", icon: ArrowRightLeft, label: "Transfer & Approve" },
  { to: "/query", icon: Search, label: "Query Collection" },
  { to: "/batch", icon: Users, label: "Batch Operations" },
  { to: "/royalty", icon: DollarSign, label: "Royalty Management" },
];

export default function Sidebar() {
  return (
    <aside className="w-64 min-h-screen bg-[#0d0a1e] border-r border-[#2A1A5A] flex flex-col">
      <div className="p-5 border-b border-[#2A1A5A]">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#6C5CE7] to-[#00D2FF] flex items-center justify-center">
            <Wallet size={16} className="text-white" />
          </div>
          <div>
            <p className="text-white font-bold text-sm">PHAROS NFT</p>
            <p className="text-[#6666AA] text-[10px]">Collection Manager</p>
          </div>
        </div>
      </div>
      <nav className="flex-1 p-3 space-y-1">
        {links.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            end={l.end}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all ${
                isActive
                  ? "bg-[#6C5CE7]/15 text-[#8B7CF7] border border-[#6C5CE7]/30"
                  : "text-[#9999CC] hover:text-white hover:bg-[#ffffff08]"
              }`
            }
          >
            <l.icon size={16} />
            {l.label}
          </NavLink>
        ))}
      </nav>
      <div className="p-4 border-t border-[#2A1A5A]">
        <p className="text-[10px] text-[#6666AA]">Skill-to-Agent Hackathon</p>
        <p className="text-[10px] text-[#6666AA]">Phase 1 · June 17</p>
      </div>
    </aside>
  );
}
