import React, { useEffect, useState } from "react";
import { SystemHealth } from "../types";
import { ApiClient } from "../api/client";

export const SettingsView: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [version, setVersion] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      ApiClient.getHealth(),
      fetch("http://localhost:8000/api/v1/version").then((r) => r.json()).catch(() => null),
    ])
      .then(([hData, vData]) => {
        setHealth(hData);
        setVersion(vData);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px", maxWidth: "900px" }}>
      <div>
        <h1 style={{ fontSize: "24px", fontWeight: "700", color: "#0f172a" }}>System Health & Configuration</h1>
        <p style={{ fontSize: "14px", color: "#64748b" }}>
          Production platform diagnostics, cryptographic checksums, and storage configurations.
        </p>
      </div>

      <div style={{ backgroundColor: "#ffffff", padding: "20px", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
        <h2 style={{ fontSize: "16px", fontWeight: "600", marginBottom: "16px", color: "#0f172a" }}>
          Runtime Health Status
        </h2>
        {loading ? (
          <div style={{ color: "#64748b" }}>Querying system status...</div>
        ) : health ? (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", fontSize: "14px" }}>
            <div><strong>Overall Status:</strong> <span style={{ color: "#16a34a", fontWeight: "600" }}>{health.status}</span></div>
            <div><strong>Database Connection:</strong> <span style={{ color: "#16a34a", fontWeight: "600" }}>{health.database}</span></div>
            <div><strong>Exact FAISS Vector Count:</strong> {health.faiss_index_count}</div>
            <div><strong>Platform Version:</strong> {health.version}</div>
          </div>
        ) : (
          <div style={{ color: "#dc2626" }}>Unable to reach backend API.</div>
        )}
      </div>

      {version && (
        <div style={{ backgroundColor: "#ffffff", padding: "20px", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
          <h2 style={{ fontSize: "16px", fontWeight: "600", marginBottom: "16px", color: "#0f172a" }}>
            Cryptographic Pinned Artifacts
          </h2>
          <div style={{ display: "flex", flexDirection: "column", gap: "8px", fontSize: "13px" }}>
            <div><strong>Backbone Model:</strong> {version.dinov2_model} ({version.embedding_dimension}-D)</div>
            <div><strong>Preprocessing Version:</strong> {version.preprocessing_version}</div>
            <div style={{ wordBreak: "break-all" }}>
              <strong>Phase 4 Checkpoint SHA-256:</strong> <code>{version.phase4_checkpoint_hash}</code>
            </div>
            <div><strong>Database Schema Version:</strong> {version.schema_version}</div>
          </div>
        </div>
      )}

      <div style={{ backgroundColor: "#ffffff", padding: "20px", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
        <h2 style={{ fontSize: "16px", fontWeight: "600", marginBottom: "16px", color: "#0f172a" }}>
          Storage Architecture
        </h2>
        <div style={{ display: "flex", flexDirection: "column", gap: "8px", fontSize: "13px", color: "#475569" }}>
          <div><strong>Immutable Originals:</strong> <code>platform/storage/originals/</code></div>
          <div><strong>Web Thumbnails:</strong> <code>platform/storage/thumbnails/</code></div>
          <div><strong>Vector Indices:</strong> <code>platform/storage/indexes/</code></div>
          <div><strong>Audit Trail:</strong> Table <code>audit_logs</code> (append-only, immutable)</div>
        </div>
      </div>
    </div>
  );
};
