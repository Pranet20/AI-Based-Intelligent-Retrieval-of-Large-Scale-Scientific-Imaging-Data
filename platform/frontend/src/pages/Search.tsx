import React, { useState, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  Search as SearchIcon,
  Sliders,
  Columns,
  Eye,
  Microscope,
  CheckCircle2,
  AlertTriangle,
  ArrowRightLeft,
  X,
  Zap
} from "lucide-react";
import { SearchResult } from "../types";
import { ApiClient, ImageDetailResponse } from "../api/client";

export const Search: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [queryImageId, setQueryImageId] = useState(searchParams.get("query_id") || "1");
  const [topK, setTopK] = useState(10);
  const [modality, setModality] = useState("");
  const [useHybrid, setUseHybrid] = useState(false);
  const [instrumentFilter, setInstrumentFilter] = useState("");

  const [representation, setRepresentation] = useState<"dinov2_base" | "phase4_adapted">("dinov2_base");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [latencyMs, setLatencyMs] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Side-by-Side Comparison State
  const [comparisonTargetId, setComparisonTargetId] = useState<number | null>(null);
  const [queryDetail, setQueryDetail] = useState<ImageDetailResponse | null>(null);
  const [targetDetail, setTargetDetail] = useState<ImageDetailResponse | null>(null);
  const [loadingComparison, setLoadingComparison] = useState(false);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!queryImageId) return;

    setLoading(true);
    setError(null);
    const start = performance.now();
    try {
      const qId = parseInt(queryImageId, 10);
      let data: SearchResult[];
      if (useHybrid) {
        const metaQuery: Record<string, any> = {};
        if (modality) metaQuery["modality"] = modality;
        if (instrumentFilter) metaQuery["instrument"] = instrumentFilter;
        data = await ApiClient.searchHybrid(qId, metaQuery, topK, representation);
      } else {
        data = await ApiClient.searchByVector(qId, topK, modality || undefined, representation);
      }
      setLatencyMs(performance.now() - start);
      setResults(data);
    } catch (err: any) {
      setError(err.message || "Vector search failed");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (searchParams.get("query_id")) {
      handleSearch();
    }
  }, [searchParams]);

  // Load details for comparison
  const openComparison = async (targetId: number) => {
    setComparisonTargetId(targetId);
    setLoadingComparison(true);
    try {
      const qId = parseInt(queryImageId, 10);
      const [qData, tData] = await Promise.all([
        ApiClient.getImage(qId),
        ApiClient.getImage(targetId),
      ]);
      setQueryDetail(qData);
      setTargetDetail(tData);
    } catch (err) {
      console.error("Comparison load error:", err);
    } finally {
      setLoadingComparison(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: "22px", fontWeight: "700", color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "10px" }}>
          <SearchIcon size={22} color="var(--accent-primary)" />
          <span>Vector & Hybrid Retrieval Engine</span>
        </h1>
        <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
          Exact 384-D FAISS Inner-Product similarity search powered by frozen DINOv2 ViT-S/14 representation and Phase 4 acquisition adapter.
        </p>
      </div>

      {/* Query Formulation Form */}
      <div className="card">
        <form onSubmit={handleSearch} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 220px 120px auto", gap: "16px", alignItems: "end" }}>
            <div>
              <label style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "6px" }}>
                Query Micrograph ID *
              </label>
              <input
                type="number"
                value={queryImageId}
                onChange={(e) => setQueryImageId(e.target.value)}
                placeholder="e.g. 1"
                required
                className="input-field"
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "6px" }}>
                Representation Architecture
              </label>
              <select
                value={representation}
                onChange={(e) => setRepresentation(e.target.value as any)}
                className="input-field"
                style={{ height: "40px" }}
              >
                <option value="dinov2_base">DINOv2 Foundation (Visual Quality)</option>
                <option value="phase4_adapted">Phase 4 Adapter (Acquisition-Aware)</option>
              </select>
            </div>

            <div>
              <label style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "6px" }}>
                Top-K Returns
              </label>
              <input
                type="number"
                min="1"
                max="50"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="input-field"
                style={{ height: "40px" }}
              />
            </div>

            <button
              type="submit"
              disabled={loading || !queryImageId}
              className="btn btn-primary"
              style={{ height: "40px" }}
            >
              <SearchIcon size={16} />
              <span>{loading ? "Searching..." : "Execute Search"}</span>
            </button>
          </div>

          {/* Hybrid Metadata Filter Toggle */}
          <div style={{ paddingTop: "12px", borderTop: "1px solid var(--border-subtle)" }}>
            <label style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "13px", cursor: "pointer", color: "var(--text-secondary)" }}>
              <input
                type="checkbox"
                checked={useHybrid}
                onChange={(e) => setUseHybrid(e.target.checked)}
              />
              <span style={{ fontWeight: 500 }}>Enable Hybrid Visual + Scientific Metadata Filtering (Phase 5 Protocol)</span>
            </label>

            {useHybrid && (
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginTop: "12px", padding: "12px", backgroundColor: "var(--bg-canvas)", borderRadius: "var(--radius-md)" }}>
                <div>
                  <label style={{ display: "block", fontSize: "11px", color: "var(--text-muted)", marginBottom: "4px" }}>
                    Modality Filter
                  </label>
                  <input
                    type="text"
                    value={modality}
                    onChange={(e) => setModality(e.target.value)}
                    placeholder="e.g. SEM, BSE, SE"
                    className="input-field"
                  />
                </div>
                <div>
                  <label style={{ display: "block", fontSize: "11px", color: "var(--text-muted)", marginBottom: "4px" }}>
                    Instrument / Microscope Filter
                  </label>
                  <input
                    type="text"
                    value={instrumentFilter}
                    onChange={(e) => setInstrumentFilter(e.target.value)}
                    placeholder="e.g. Helios, Zeiss"
                    className="input-field"
                  />
                </div>
              </div>
            )}
          </div>
        </form>
      </div>

      {error && (
        <div className="card" style={{ borderLeft: "4px solid var(--status-risk)", color: "var(--status-risk)" }}>
          {error}
        </div>
      )}

      {/* Side-by-Side Comparison Modal */}
      {comparisonTargetId && (
        <div style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: "rgba(0, 0, 0, 0.85)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 100,
          backdropFilter: "blur(6px)",
          padding: "20px"
        }}>
          <div className="card" style={{ width: "960px", maxWidth: "95vw", maxHeight: "90vh", overflowY: "auto", padding: "24px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "10px" }}>
                <ArrowRightLeft size={20} color="var(--accent-primary)" />
                <span>Side-by-Side Micrograph Comparison</span>
              </h2>
              <button onClick={() => setComparisonTargetId(null)} className="btn btn-secondary btn-sm">
                <X size={16} />
              </button>
            </div>

            {loadingComparison || !queryDetail || !targetDetail ? (
              <div style={{ padding: "40px", textAlign: "center", color: "var(--text-muted)" }}>
                Loading dual micrograph comparison spectra...
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
                {/* Dual Image Preview */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                  <div style={{ textAlign: "center" }}>
                    <div style={{ fontSize: "12px", fontWeight: 600, color: "var(--accent-primary)", marginBottom: "6px" }}>
                      Query Micrograph #{queryDetail.id}
                    </div>
                    <div style={{ height: "240px", backgroundColor: "#000", borderRadius: "var(--radius-md)", overflow: "hidden" }}>
                      <img
                        src={ApiClient.getImageUrl(queryDetail.id)}
                        alt="Query"
                        style={{ width: "100%", height: "100%", objectFit: "contain" }}
                      />
                    </div>
                    <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "4px" }}>
                      {queryDetail.original_filename}
                    </div>
                  </div>

                  <div style={{ textAlign: "center" }}>
                    <div style={{ fontSize: "12px", fontWeight: 600, color: "var(--status-nominal)", marginBottom: "6px" }}>
                      Retrieved Match #{targetDetail.id}
                    </div>
                    <div style={{ height: "240px", backgroundColor: "#000", borderRadius: "var(--radius-md)", overflow: "hidden" }}>
                      <img
                        src={ApiClient.getImageUrl(targetDetail.id)}
                        alt="Match"
                        style={{ width: "100%", height: "100%", objectFit: "contain" }}
                      />
                    </div>
                    <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "4px" }}>
                      {targetDetail.original_filename}
                    </div>
                  </div>
                </div>

                {/* Metric Diff Comparison Table */}
                <div className="table-container">
                  <table className="scientific-table">
                    <thead>
                      <tr>
                        <th>Metric / Parameter</th>
                        <th>Query #{queryDetail.id}</th>
                        <th>Match #{targetDetail.id}</th>
                        <th>Comparison Insight</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td style={{ fontWeight: 600 }}>Accelerating Voltage</td>
                        <td className="font-mono">{queryDetail.metadata?.accelerating_voltage_kv ? `${queryDetail.metadata.accelerating_voltage_kv} kV` : "—"}</td>
                        <td className="font-mono">{targetDetail.metadata?.accelerating_voltage_kv ? `${targetDetail.metadata.accelerating_voltage_kv} kV` : "—"}</td>
                        <td>
                          {queryDetail.metadata?.accelerating_voltage_kv === targetDetail.metadata?.accelerating_voltage_kv
                            ? "Identical Acquisition Setting"
                            : "Cross-Acquisition Geometry Gap Handled by Adapter"}
                        </td>
                      </tr>
                      <tr>
                        <td style={{ fontWeight: 600 }}>Detector Type</td>
                        <td className="font-mono">{queryDetail.metadata?.detector || "—"}</td>
                        <td className="font-mono">{targetDetail.metadata?.detector || "—"}</td>
                        <td>{queryDetail.metadata?.detector === targetDetail.metadata?.detector ? "Matching Detector" : "Cross-Detector Match"}</td>
                      </tr>
                      <tr>
                        <td style={{ fontWeight: 600 }}>Composite Quality Risk</td>
                        <td className="font-mono">{queryDetail.quality ? `${(queryDetail.quality.composite_quality_risk * 100).toFixed(1)}%` : "—"}</td>
                        <td className="font-mono">{targetDetail.quality ? `${(targetDetail.quality.composite_quality_risk * 100).toFixed(1)}%` : "—"}</td>
                        <td>
                          {Math.abs((queryDetail.quality?.composite_quality_risk || 0) - (targetDetail.quality?.composite_quality_risk || 0)) < 0.1
                            ? "Consistent Image-Derived Quality Risk"
                            : "Varying Signal Degradation"}
                        </td>
                      </tr>
                      <tr>
                        <td style={{ fontWeight: 600 }}>Resolution</td>
                        <td className="font-mono">{queryDetail.width} × {queryDetail.height}</td>
                        <td className="font-mono">{targetDetail.width} × {targetDetail.height}</td>
                        <td>Preprocessed to uniform 224 × 224 DINOv2 input</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Search Results Display */}
      {results.length > 0 && (
        <div className="card" style={{ padding: "0", overflow: "hidden" }}>
          <div style={{
            padding: "16px 20px",
            backgroundColor: "var(--bg-surface-elevated)",
            borderBottom: "1px solid var(--border-default)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center"
          }}>
            <div>
              <h2 style={{ fontSize: "15px", fontWeight: 600, color: "var(--text-primary)" }}>
                Retrieval Matches ({results.length})
              </h2>
              {latencyMs !== null && (
                <div style={{ fontSize: "11px", color: "var(--accent-cyan)", marginTop: "2px" }}>
                  Query executed in {latencyMs.toFixed(2)} ms via exact FAISS IndexFlatIP
                </div>
              )}
            </div>

            <span className="badge badge-nominal">Normalized Cosine Distance</span>
          </div>

          <div className="table-container">
            <table className="scientific-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Image ID</th>
                  <th>Filename</th>
                  <th>Cosine Similarity</th>
                  <th>Modality</th>
                  <th>Quality Risk</th>
                  <th>Redundancy Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {results.map((res, i) => (
                  <tr key={res.image_id}>
                    <td className="font-mono" style={{ color: "var(--text-muted)", fontWeight: 600 }}>#{i + 1}</td>
                    <td className="font-mono">
                      <Link to={`/images/${res.image_id}`} style={{ fontWeight: 600 }}>
                        #{res.image_id}
                      </Link>
                    </td>
                    <td style={{ fontWeight: 600 }}>{res.filename}</td>
                    <td>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <div style={{ width: "60px", height: "6px", backgroundColor: "var(--bg-canvas)", borderRadius: "var(--radius-full)", overflow: "hidden" }}>
                          <div style={{
                            width: `${Math.max(0, Math.min(100, res.similarity * 100))}%`,
                            height: "100%",
                            backgroundColor: res.similarity >= 0.8 ? "var(--status-nominal)" : "var(--accent-primary)"
                          }} />
                        </div>
                        <span className="font-mono" style={{ fontWeight: 700, color: "var(--text-primary)" }}>
                          {res.similarity.toFixed(4)}
                        </span>
                      </div>
                    </td>
                    <td>{res.modality || "SEM"}</td>
                    <td>
                      <span className={`badge ${res.quality_label === "NOMINAL" ? "badge-nominal" : "badge-risk"}`}>
                        {(res.quality_risk * 100).toFixed(1)}% ({res.quality_label})
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${res.duplicate_status === "NO_DECLARED_REDUNDANCY_DETECTED" ? "badge-nominal" : "badge-warning"}`}>
                        {res.duplicate_status === "NO_DECLARED_REDUNDANCY_DETECTED" ? "UNIQUE" : "REDUNDANT"}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: "flex", gap: "6px" }}>
                        <button
                          onClick={() => openComparison(res.image_id)}
                          className="btn btn-secondary btn-sm"
                          title="Side-by-Side Comparison"
                        >
                          <Columns size={12} />
                          <span>Compare</span>
                        </button>
                        <Link to={`/images/${res.image_id}`} className="btn btn-secondary btn-sm">
                          <Eye size={12} />
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
