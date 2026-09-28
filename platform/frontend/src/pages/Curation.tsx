import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  ShieldAlert,
  CheckSquare,
  AlertTriangle,
  Layers,
  Eye,
  CheckCircle2
} from "lucide-react";
import { ApiClient } from "../api/client";

export const Curation: React.FC = () => {
  const [images, setImages] = useState<any[]>([]);
  const [filter, setFilter] = useState<"ALL" | "REDUNDANT" | "QUALITY_RISK">("ALL");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    ApiClient.getImages(undefined, undefined, 100, 0)
      .then((res) => setImages(res.items || []))
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  }, []);

  const redundantCount = images.filter(
    (img) => img.duplicate_status && img.duplicate_status !== "NO_DECLARED_REDUNDANCY_DETECTED"
  ).length;

  const qualityRiskCount = images.filter(
    (img) => img.quality_label === "RISK_FLAGGED" || img.composite_quality_risk >= 0.60
  ).length;

  const filteredImages = images.filter((img) => {
    if (filter === "REDUNDANT") {
      return img.duplicate_status && img.duplicate_status !== "NO_DECLARED_REDUNDANCY_DETECTED";
    }
    if (filter === "QUALITY_RISK") {
      return img.quality_label === "RISK_FLAGGED" || img.composite_quality_risk >= 0.60;
    }
    return true;
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Top Banner */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "16px" }}>
        <div>
          <h1 style={{ fontSize: "22px", fontWeight: "700", color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "10px" }}>
            <Layers size={22} color="var(--accent-primary)" />
            <span>Data Integrity, Redundancy & Curation</span>
          </h1>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
            Multi-stage cascade results, physical quality-risk flagging, and active triage status.
          </p>
        </div>

        <Link to="/reviews" className="btn btn-primary btn-sm">
          <CheckSquare size={14} />
          <span>Launch Curator Workbench</span>
        </Link>
      </div>

      {/* Filter Tabs */}
      <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
        <button
          onClick={() => setFilter("ALL")}
          className={`btn btn-sm ${filter === "ALL" ? "btn-primary" : "btn-secondary"}`}
        >
          All Micrographs ({images.length})
        </button>
        <button
          onClick={() => setFilter("REDUNDANT")}
          className={`btn btn-sm ${filter === "REDUNDANT" ? "btn-primary" : "btn-secondary"}`}
          style={filter === "REDUNDANT" ? { backgroundColor: "var(--status-warning)", borderColor: "var(--status-warning)" } : {}}
        >
          <AlertTriangle size={14} />
          <span>Redundancies Detected ({redundantCount})</span>
        </button>
        <button
          onClick={() => setFilter("QUALITY_RISK")}
          className={`btn btn-sm ${filter === "QUALITY_RISK" ? "btn-primary" : "btn-secondary"}`}
          style={filter === "QUALITY_RISK" ? { backgroundColor: "var(--status-risk)", borderColor: "var(--status-risk)" } : {}}
        >
          <ShieldAlert size={14} />
          <span>Quality-Risk Flagged ({qualityRiskCount})</span>
        </button>
      </div>

      {/* Data Table */}
      <div className="card" style={{ padding: "0", overflow: "hidden" }}>
        <div className="table-container">
          <table className="scientific-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Filename</th>
                <th>Resolution</th>
                <th>Composite Risk</th>
                <th>Quality Label</th>
                <th>Redundancy Status</th>
                <th>Processing Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={8} style={{ padding: "30px", textAlign: "center", color: "var(--text-muted)" }}>Loading records...</td></tr>
              ) : filteredImages.length === 0 ? (
                <tr><td colSpan={8} style={{ padding: "30px", textAlign: "center", color: "var(--text-muted)" }}>No micrographs matching filter criteria.</td></tr>
              ) : (
                filteredImages.map((img) => (
                  <tr key={img.id}>
                    <td className="font-mono">#{img.id}</td>
                    <td style={{ fontWeight: 600 }}>{img.original_filename}</td>
                    <td className="font-mono">{img.width} × {img.height}</td>
                    <td className="font-mono" style={{ color: img.composite_quality_risk >= 0.60 ? "var(--status-risk)" : "var(--status-nominal)" }}>
                      {(img.composite_quality_risk * 100).toFixed(1)}%
                    </td>
                    <td>
                      <span className={`badge ${img.quality_label === "NOMINAL" ? "badge-nominal" : "badge-risk"}`}>
                        {img.quality_label}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${img.duplicate_status === "NO_DECLARED_REDUNDANCY_DETECTED" ? "badge-nominal" : "badge-warning"}`}>
                        {img.duplicate_status === "NO_DECLARED_REDUNDANCY_DETECTED" ? "UNIQUE" : "REDUNDANT"}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-info">{img.processing_status}</span>
                    </td>
                    <td>
                      <div style={{ display: "flex", gap: "6px" }}>
                        <Link to={`/images/${img.id}`} className="btn btn-secondary btn-sm">
                          <Eye size={12} />
                          <span>Inspect</span>
                        </Link>
                        <Link to={`/reviews?image_id=${img.id}`} className="btn btn-primary btn-sm">
                          <CheckSquare size={12} />
                          <span>Curate</span>
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
