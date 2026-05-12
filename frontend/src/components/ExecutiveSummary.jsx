import { useState, useEffect } from "react";
import axios from "axios";

const API = "http://localhost:8000/api";

export default function ExecutiveSummary({ datasetId }) {
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [generated, setGenerated] = useState(false);

  const generateSummary = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/summary/${datasetId}`);
      setSummary(res.data.summary);
      setGenerated(true);
    } catch {
      setSummary("Failed to generate summary. Please try again.");
      setGenerated(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="summary-panel">
      <div className="summary-title">📊 Executive Summary</div>
      {!generated && !loading && (
        <div className="summary-generate">
          <p>Generate an AI-powered summary of key insights from your data.</p>
          <button className="summary-btn" onClick={generateSummary}>
            Generate Summary
          </button>
        </div>
      )}
      {loading && (
        <div className="summary-loading">
          ⏳ Analyzing your data, please wait...
        </div>
      )}
      {generated && !loading && (
        <div className="summary-content">
          <p>{summary}</p>
          <button className="summary-btn" onClick={generateSummary}>
            Regenerate
          </button>
        </div>
      )}
    </div>
  );
}
