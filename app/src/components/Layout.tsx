import { ReactNode } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import WalletConnect from "./WalletConnect";

export default function Layout() {
  return (
    <div className="flex min-h-screen bg-[#0a0a1a]">
      <Sidebar />
      <main className="flex-1 flex flex-col">
        <header className="h-16 border-b border-[#2A1A5A] flex items-center justify-end px-6 bg-[#0d0a1e]/80 backdrop-blur-sm">
          <WalletConnect />
        </header>
        <div className="flex-1 p-6 overflow-y-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
