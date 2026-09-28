import React, { useState } from "react";
import { Link } from "react-router-dom";
import { SearchResult } from "../types";
import { ApiClient } from "../api/client";

export const Search: React.FC = () => {
  const [queryImageId, setQueryImageId] = useState("");
  const [topK, setTopK] = useState(10);
  const [modality, setModality] = useState("");
  const [useHybrid, setUseHybrid] = useState(false);
  const [instrumentFilter, setInstrumentFilter] = useState("");

  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!queryImageId) return;

    setLoading(true);
    setError(null);
    try {
      const qId = parseInt(queryImageId, 10);
      let data: SearchResult[];
      if (useHybrid) {
        const metaQuery: Record<string, any> = {};
        if (modality) metaQuery["modality"] = modality;
        if (instrumentFilter) metaQuery["instrument"] = instrumentFilter;
        data = await ApiClient.searchHybrid(qId, metaQuery, topK);
      } else {
        data = await ApiClient.searchByVector(qId, topK, modality || undefined);
      }
      setResults(data);
    } catch (err: any) {
      setError(err.message || "Search failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px", maxWidth: "900px" }}>
      <div>
        <h1 style={{ fontSize: "24px", fontWeight: "700", color: "#0f172a" }}>Vector & Hybrid Retrieval</h1>
        <p style={{ fontSize: "14px", color: "#64748b" }}>
          Query the exact FAISS IndexFlatIP index (384-D) with optional scientific metadata constraints.
        </p>
      </div>

      <div style={{ backgroundColor: "#ffffff", padding: "20px", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
        <form onSubmit={handleSearch} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div style={{ display: "flex", gap: "16px" }}>
            <div style={{ flex: 1 }}>
              <label style={{ display: "block", fontSize: "13px", fontWeight: "500", color: "#334155", marginBottom: "6px" }}>
                Query Micrograph ID
              </label>
              <input
                type="number"
                value={queryImageId}
                onChange={(e) => setQueryImageId(e.target.value)}
                placeholder="e.g. 1"
                required
                style={{ width: "100%", padding: "8px 12px", border: "1px solid #cbd5e1", borderRadius: "4px", fontSize: "14px" }}
              />
            </div>
            <div style={{ width: "120px" }}>
              <label style={{ display: "block", fontSize: "13px", fontWeight: "500", color: "#334155", marginBottom: "6px" }}>
                Top-K
              </label>
              <input
                type="number"
                min="1"
                max="100"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                style={{ width: "100%", padding: "8px 12px", border: "1px solid #cbd5e1", borderRadius: "4px", fontSize: "14px" }}
              />
            </div>
          </div>

          <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
            <label style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "13px", cursor: "pointer", fontWeight: "500" }}>
              <input
                type="checkbox"
                checked={useHybrid}
                onChange={(e) => setUseHybrid(e.target.checked)}
              />
              Enable Hybrid Visual + Scientific Metadata Filtering (Phase 5 Protocol)
            </label>
          </div>

          {useHybrid && (
            <div style={{ display: "flex", gap: "16px", backgroundColor: "#f8fafc", padding: "12px", borderRadius: "6px" }}>
              <div style={{ flex: 1 }}>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "500", color: "#475569", marginBottom: "4px" }}>
                  Modality Filter
                </label>
                <input
                  type="text"
                  value={modality}
                  onChange={(e) => setModality(e.target.value)}
                  placeholder="e.g. SEM"
                  style={{ width: "100%", padding: "6px 10px", border: "1px solid #cbd5e1", borderRadius: "4px", fontSize: "13px" }}
                />
              </div>
              <div style={{ flex: 1 }}>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "500", color: "#475569", marginBottom: "4px" }}>
                  Instrument Filter
                </label>
                <input
                  type="text"
                  value={instrumentFilter}
                  onChange={(e) => setInstrumentFilter(e.target.value)}
                  placeholder="e.g. Helios NanoLab"
                  style={{ width: "100%", padding: "6px 10px", border: "1px solid #cbd5e1", borderRadius: "4px", fontSize: "13px" }}
                />
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !queryImageId}
            style={{
              padding: "10px 20px",
              backgroundColor: "#2563eb",
              color: "#ffffff",
              border: "none",
              borderRadius: "4px",
              fontSize: "14px",
              fontWeight: "600",
              cursor: loading ? "not-allowed" : "pointer",
              alignSelf: "flex-start"
            }}
          >
            {loading ? "Searching Exact FAISS Index..." : "Execute Retrieval"}
          </button>
        </form>
      </div>

      {error && (
        <div style={{ padding: "12px 16px", backgroundColor: "#fef2f2", color: "#991b1b", borderRadius: "4px", fontSize: "14px" }}>
          {error}
        </div>
      )}

      {results.length > 0 && (
        <div style={{ backgroundColor: "#ffffff", borderRadius: "8px", border: "1px solid #e2e8f0", overflow: "hidden" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "14px" }}>
            <thead>
              <tr style={{ backgroundColor: "#f8fafc", borderBottom: "1px solid #e2e8f0", textAlign: "left", color: "#64748b" }}>
                <th style={{ padding: "10px 14px" }}>Rank</th>
                <th style={{ padding: "10px 14px" }}>Image ID</th>
                <th style={{ padding: "10px 14px" }}>Filename</th>
                <th style={{ padding: "10px 14px" }}>Cosine Similarity</th>
                <th style={{ padding: "10px 14px" }}>Modality</th>
                <th style={{ padding: "10px 14px" }}>Quality Risk</th>
                <th style={{ padding: "10px 14px" }}>Duplicate Status</th>
              </tr>
            </thead>
            <tbody>
              {results.map((res, i) => (
                <tr key={res.image_id} style={{ borderBottom: "1px solid #f1f5f9" }}>
                  <td style={{ padding: "10px 14px", fontWeight: "600", color: "#64748b" }}>#{i + 1}</td>
                  <td style={{ padding: "10px 14px" }}>
                    <Link to={`/images/${res.image_id}`} style={{ color: "#2563eb", fontWeight: "600" }}>
                      #{res.image_id}
                    </Link>
                  </td>
                  <td style={{ padding: "10px 14px" }}>{res.filename}</td>
                  <td style={{ padding: "10px 14px", fontWeight: "700", color: "#0f172a" }}>
                    {res.similarity.toFixed(4)}
                  </td>
                  <td style={{ padding: "10px 14px", color: "#475569" }}>{res.modality}</td>
                  <td style={{ padding: "10px 14px" }}>
                    <span style={{
                      fontSize: "12px",
                      padding: "2px 6px",
                      borderRadius: "4px",
                      backgroundColor: res.quality_label === "NOMINAL" ? "#dcfce7" : "#fee2e2",
                      color: res.quality_label === "NOMINAL" ? "#166534" : "#991b1b"
                    }}>
                      {res.quality_label} ({res.quality_risk.toFixed(3)})
                    </span>
                  </td>
                  <td style={{ padding: "10px 14px", fontSize: "12px", color: "#475569" }}>
                    {res.duplicate_status}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
