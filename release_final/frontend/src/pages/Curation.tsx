import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ScientificImage } from "../types";
import { ApiClient } from "../api/client";

export const Curation: React.FC = () => {
  const [images, setImages] = useState<ScientificImage[]>([]);
  const [filter, setFilter] = useState<"ALL" | "REDUNDANT" | "QUALITY_RISK">("ALL");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    ApiClient.getImages()
      .then((data) => setImages(data))
      .finally(() => setLoading(false));
  }, []);

  const redundantCount = images.filter(
    (img) => img.duplicate && img.duplicate.duplicate_status !== "NO_DECLARED_REDUNDANCY_DETECTED"
  ).length;

  const qualityRiskCount = images.filter(
    (img) => img.quality && img.quality.quality_label === "RISK_FLAGGED"
  ).length;

  const filteredImages = images.filter((img) => {
    if (filter === "REDUNDANT") {
      return img.duplicate && img.duplicate.duplicate_status !== "NO_DECLARED_REDUNDANCY_DETECTED";
    }
    if (filter === "QUALITY_RISK") {
      return img.quality && img.quality.quality_label === "RISK_FLAGGED";
    }
    return true;
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <div>
        <h1 style={{ fontSize: "24px", fontWeight: "700", color: "#0f172a" }}>Data Integrity & Curation</h1>
        <p style={{ fontSize: "14px", color: "#64748b" }}>
          Explore redundancy clusters, physical quality risks, and curate datasets for downstream ML model training.
        </p>
      </div>

      <div style={{ display: "flex", gap: "16px" }}>
        <button
          onClick={() => setFilter("ALL")}
          style={{
            padding: "8px 16px",
            borderRadius: "6px",
            border: "1px solid #cbd5e1",
            backgroundColor: filter === "ALL" ? "#0f172a" : "#ffffff",
            color: filter === "ALL" ? "#ffffff" : "#475569",
            fontWeight: "600",
            cursor: "pointer",
            fontSize: "13px"
          }}
        >
          All Micrographs ({images.length})
        </button>
        <button
          onClick={() => setFilter("REDUNDANT")}
          style={{
            padding: "8px 16px",
            borderRadius: "6px",
            border: "1px solid #ea580c",
            backgroundColor: filter === "REDUNDANT" ? "#ea580c" : "#ffffff",
            color: filter === "REDUNDANT" ? "#ffffff" : "#ea580c",
            fontWeight: "600",
            cursor: "pointer",
            fontSize: "13px"
          }}
        >
          Redundant Micrographs ({redundantCount})
        </button>
        <button
          onClick={() => setFilter("QUALITY_RISK")}
          style={{
            padding: "8px 16px",
            borderRadius: "6px",
            border: "1px solid #dc2626",
            backgroundColor: filter === "QUALITY_RISK" ? "#dc2626" : "#ffffff",
            color: filter === "QUALITY_RISK" ? "#ffffff" : "#dc2626",
            fontWeight: "600",
            cursor: "pointer",
            fontSize: "13px"
          }}
        >
          Quality-Risk Flagged ({qualityRiskCount})
        </button>
      </div>

      <div style={{ backgroundColor: "#ffffff", borderRadius: "8px", border: "1px solid #e2e8f0", overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "14px" }}>
          <thead>
            <tr style={{ backgroundColor: "#f8fafc", borderBottom: "1px solid #e2e8f0", textAlign: "left", color: "#64748b" }}>
              <th style={{ padding: "10px 14px" }}>ID</th>
              <th style={{ padding: "10px 14px" }}>Filename</th>
              <th style={{ padding: "10px 14px" }}>Modality</th>
              <th style={{ padding: "10px 14px" }}>Composite Risk</th>
              <th style={{ padding: "10px 14px" }}>Redundancy Status</th>
              <th style={{ padding: "10px 14px" }}>Action</th>
              <th style={{ padding: "10px 14px" }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={7} style={{ padding: "24px", textAlign: "center", color: "#64748b" }}>Loading micrographs...</td></tr>
            ) : filteredImages.length === 0 ? (
              <tr><td colSpan={7} style={{ padding: "24px", textAlign: "center", color: "#64748b" }}>No micrographs matching filter criteria.</td></tr>
            ) : (
              filteredImages.map((img) => (
                <tr key={img.id} style={{ borderBottom: "1px solid #f1f5f9" }}>
                  <td style={{ padding: "10px 14px" }}>
                    <Link to={`/images/${img.id}`} style={{ color: "#2563eb", fontWeight: "600" }}>
                      #{img.id}
                    </Link>
                  </td>
                  <td style={{ padding: "10px 14px", fontWeight: "500" }}>{img.filename}</td>
                  <td style={{ padding: "10px 14px", color: "#475569" }}>{img.modality}</td>
                  <td style={{ padding: "10px 14px" }}>
                    <span style={{
                      fontSize: "12px",
                      padding: "2px 6px",
                      borderRadius: "4px",
                      backgroundColor: img.quality?.quality_label === "NOMINAL" ? "#dcfce7" : "#fee2e2",
                      color: img.quality?.quality_label === "NOMINAL" ? "#166534" : "#991b1b"
                    }}>
                      {img.quality?.composite_quality_risk.toFixed(3) || "0.000"}
                    </span>
                  </td>
                  <td style={{ padding: "10px 14px", fontSize: "12px" }}>
                    {img.duplicate?.duplicate_status || "N/A"}
                  </td>
                  <td style={{ padding: "10px 14px", fontWeight: "600" }}>
                    {img.duplicate?.action || "KEEP"}
                  </td>
                  <td style={{ padding: "10px 14px" }}>
                    <span style={{
                      fontSize: "12px",
                      padding: "2px 8px",
                      borderRadius: "4px",
                      backgroundColor: img.status === "READY" ? "#dcfce7" : "#fef3c7",
                      color: img.status === "READY" ? "#166534" : "#92400e"
                    }}>
                      {img.status}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
