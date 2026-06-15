import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import DeployCollection from "./pages/DeployCollection";
import MintTokens from "./pages/MintTokens";
import TransferApprove from "./pages/TransferApprove";
import QueryCollection from "./pages/QueryCollection";
import BatchOperations from "./pages/BatchOperations";
import RoyaltyManagement from "./pages/RoyaltyManagement";

export default function App() {
  return (
    <BrowserRouter basename="/pharos-nft-manager">
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/deploy" element={<DeployCollection />} />
          <Route path="/mint" element={<MintTokens />} />
          <Route path="/transfer" element={<TransferApprove />} />
          <Route path="/query" element={<QueryCollection />} />
          <Route path="/batch" element={<BatchOperations />} />
          <Route path="/royalty" element={<RoyaltyManagement />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
