import { useState } from "react";
import UploadSection from "./components/UploadSection";
import Dashboard from "./components/Dashboard";
import "./index.css";

export default function App() {
  const [datasetId, setDatasetId] = useState(null);
  const [datasetName, setDatasetName] = useState("");

  return (
    <div className="app-wrapper">
      <header className="app-header">
        <div className="header-inner">
          <span className="logo-text">DataLens</span>
          <span className="logo-sub">Airline Analytics Dashboard</span>
        </div>
      </header>

      <main className="app-main">
        {!datasetId ? (
          <UploadSection onUploadSuccess={(id, name) => { setDatasetId(id); setDatasetName(name); }} />
        ) : (
          <Dashboard datasetId={datasetId} datasetName={datasetName} onReset={() => setDatasetId(null)} />
        )}
      </main>
    </div>
  );
}