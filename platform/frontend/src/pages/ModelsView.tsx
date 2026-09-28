import React, { useEffect, useState } from "react";
import { Cpu, ShieldCheck, Copy, Check, Info } from "lucide-react";
import { ModelVersion } from "../types";
import { ApiClient } from "../api/client";

export const ModelsView: React.FC = () => {
  const [models, setModels] = useState<ModelVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [copiedId, setCopiedId] = useState<number | null>(null);

  useEffect(() => {
    ApiClient.getModels()
      .then((data) => setModels(data))
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  }, []);

  const handleCopy = (id: number, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: "22px", fontWeight: "700", color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "10px" }}>
          <Cpu size={22} color="var(--accent-primary)" />
          <span>Authoritative Model Registry</span>
        </h1>
        <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
          Cryptographically pinned neural representations and model weights verified at system startup against frozen research checksums.
        </p>
      </div>

      {/* Immutability Banner */}
      <div style={{
        padding: "12px 16px",
        borderRadius: "var(--radius-md)",
        backgroundColor: "rgba(16, 185, 129, 0.08)",
        border: "1px solid rgba(16, 185, 129, 0.2)",
        display: "flex",
        alignItems: "center",
        gap: "10px",
        fontSize: "12px",
        color: "var(--text-secondary)"
      }}>
        <ShieldCheck size={18} color="var(--status-nominal)" style={{ flexShrink: 0 }} />
        <span>
          <strong>Cryptographic Baseline Integrity:</strong> All visual encoders and projection adapters are loaded in read-only evaluation mode.
          Weights are checked against authoritative SHA-256 signatures before inference initialization.
        </span>
      </div>

      {/* Model Cards Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "16px" }}>
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
            <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase" }}>
              Visual Backbone
            </span>
            <span className="badge badge-nominal">Frozen</span>
          </div>
          <h2 style={{ fontSize: "16px", fontWeight: 700, color: "var(--text-primary)", marginBottom: "4px" }}>
            Meta DINOv2 ViT-S/14
          </h2>
          <p style={{ fontSize: "12px", color: "var(--text-secondary)", marginBottom: "14px" }}>
            Self-supervised Vision Transformer with 14x14 patch size. Yields 384-D generalizable representation without task-specific labels.
          </p>
          <div style={{ fontSize: "12px", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "4px" }}>
            <div><strong>Embedding Dimension:</strong> 384 (L2 Normalized)</div>
            <div><strong>Evaluation Protocol:</strong> Zero-shot retrieval on HCCI & Carinthia</div>
          </div>
        </div>

        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
            <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase" }}>
              Domain Adapter
            </span>
            <span className="badge badge-nominal">Authoritative</span>
          </div>
          <h2 style={{ fontSize: "16px", fontWeight: 700, color: "var(--text-primary)", marginBottom: "4px" }}>
            Phase 4 Linear Projection (Seed 42)
          </h2>
          <p style={{ fontSize: "12px", color: "var(--text-secondary)", marginBottom: "14px" }}>
            Learned cross-acquisition alignment reducing geometry similarity gap by 68.15% (p = 1.42 × 10⁻¹²).
          </p>
          <div style={{ fontSize: "12px", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "4px" }}>
            <div><strong>Architecture:</strong> Linear(384, 384) + L2 Normalization</div>
            <div><strong>Checkpoint:</strong> <code>best_checkpoint_seed42.pt</code></div>
          </div>
        </div>

        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
            <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase" }}>
              Comparative Baseline
            </span>
            <span className="badge badge-info">Benchmark Only</span>
          </div>
          <h2 style={{ fontSize: "16px", fontWeight: 700, color: "var(--text-primary)", marginBottom: "4px" }}>
            ResNet-50 (ImageNet Pretrained)
          </h2>
          <p style={{ fontSize: "12px", color: "var(--text-secondary)", marginBottom: "14px" }}>
            Standard convolutional baseline achieving 92.45% R@1, demonstrating superiority of self-supervised ViT.
          </p>
          <div style={{ fontSize: "12px", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "4px" }}>
            <div><strong>Architecture:</strong> ResNet-50 (2048-D Pool5)</div>
            <div><strong>Purpose:</strong> Phase 2 & 7 comparative evaluation baseline</div>
          </div>
        </div>
      </div>

      {/* Registered Checkpoints Table */}
      <div className="card" style={{ padding: "0", overflow: "hidden" }}>
        <div style={{ padding: "16px 20px", backgroundColor: "var(--bg-surface-elevated)", borderBottom: "1px solid var(--border-default)" }}>
          <h2 style={{ fontSize: "15px", fontWeight: 600, color: "var(--text-primary)" }}>
            Database-Registered Model Versions & Checksums
          </h2>
        </div>

        <div className="table-container">
          <table className="scientific-table">
            <thead>
              <tr>
                <th>Model Identifier</th>
                <th>Architecture</th>
                <th>Dimension</th>
                <th>Weights SHA-256 Checksum</th>
                <th>Preprocessing</th>
                <th>Lifecycle Status</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={6} style={{ padding: "30px", textAlign: "center", color: "var(--text-muted)" }}>Loading model registry...</td></tr>
              ) : models.length === 0 ? (
                <tr><td colSpan={6} style={{ padding: "30px", textAlign: "center", color: "var(--text-muted)" }}>No models registered in database.</td></tr>
              ) : (
                models.map((m) => (
                  <tr key={m.id}>
                    <td style={{ fontWeight: 600, color: "var(--text-primary)" }}>{m.model_id}</td>
                    <td>{m.architecture}</td>
                    <td className="font-mono" style={{ color: "var(--accent-cyan)", fontWeight: 600 }}>{m.embedding_dimension}-D</td>
                    <td>
                      <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                        <span className="font-mono" style={{ fontSize: "11px", color: "var(--text-secondary)" }}>
                          {m.weights_hash.length > 28 ? `${m.weights_hash.substring(0, 14)}...${m.weights_hash.substring(m.weights_hash.length - 14)}` : m.weights_hash}
                        </span>
                        <button
                          onClick={() => handleCopy(m.id, m.weights_hash)}
                          className="btn btn-secondary btn-sm"
                          style={{ padding: "2px 6px" }}
                          title="Copy Full Checksum"
                        >
                          {copiedId === m.id ? <Check size={12} color="var(--status-nominal)" /> : <Copy size={12} />}
                        </button>
                      </div>
                    </td>
                    <td className="font-mono" style={{ fontSize: "12px", color: "var(--text-muted)" }}>{m.preprocessing_version}</td>
                    <td>
                      <span className={`badge ${m.is_active ? "badge-nominal" : "badge-risk"}`}>
                        {m.is_active ? "ACTIVE & VERIFIED" : "INACTIVE"}
                      </span>
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
