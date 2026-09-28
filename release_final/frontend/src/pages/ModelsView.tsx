import React, { useEffect, useState } from "react";
import { ModelVersion } from "../types";
import { ApiClient } from "../api/client";

export const ModelsView: React.FC = () => {
  const [models, setModels] = useState<ModelVersion[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    ApiClient.getModels()
      .then((data) => setModels(data))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <div>
        <h1 style={{ fontSize: "24px", fontWeight: "700", color: "#0f172a" }}>Authoritative Model Registry</h1>
        <p style={{ fontSize: "14px", color: "#64748b" }}>
          Cryptographically pinned neural representations and checkpoints verified at system startup.
        </p>
      </div>

      <div style={{ backgroundColor: "#ffffff", borderRadius: "8px", border: "1px solid #e2e8f0", overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "14px" }}>
          <thead>
            <tr style={{ backgroundColor: "#f8fafc", borderBottom: "1px solid #e2e8f0", textAlign: "left", color: "#64748b" }}>
              <th style={{ padding: "12px 16px" }}>Model Identifier</th>
              <th style={{ padding: "12px 16px" }}>Architecture</th>
              <th style={{ padding: "12px 16px" }}>Dimension</th>
              <th style={{ padding: "12px 16px" }}>Weights / Checkpoint SHA-256</th>
              <th style={{ padding: "12px 16px" }}>Preprocessing</th>
              <th style={{ padding: "12px 16px" }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={6} style={{ padding: "24px", textAlign: "center", color: "#64748b" }}>Loading model registry...</td></tr>
            ) : models.length === 0 ? (
              <tr><td colSpan={6} style={{ padding: "24px", textAlign: "center", color: "#64748b" }}>No models registered.</td></tr>
            ) : (
              models.map((m) => (
                <tr key={m.id} style={{ borderBottom: "1px solid #f1f5f9" }}>
                  <td style={{ padding: "12px 16px", fontWeight: "600", color: "#0f172a" }}>{m.model_id}</td>
                  <td style={{ padding: "12px 16px", color: "#334155" }}>{m.architecture}</td>
                  <td style={{ padding: "12px 16px", color: "#0284c7", fontWeight: "600" }}>{m.embedding_dimension}-D</td>
                  <td style={{ padding: "12px 16px", fontFamily: "monospace", fontSize: "12px", color: "#475569" }}>
                    {m.weights_hash.length > 32 ? `${m.weights_hash.substring(0, 16)}...${m.weights_hash.substring(48)}` : m.weights_hash}
                  </td>
                  <td style={{ padding: "12px 16px", color: "#64748b" }}>{m.preprocessing_version}</td>
                  <td style={{ padding: "12px 16px" }}>
                    <span style={{
                      fontSize: "12px",
                      padding: "2px 8px",
                      borderRadius: "4px",
                      backgroundColor: m.is_active ? "#dcfce7" : "#fee2e2",
                      color: m.is_active ? "#166534" : "#991b1b",
                      fontWeight: "600"
                    }}>
                      {m.is_active ? "VERIFIED & ACTIVE" : "INACTIVE"}
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
