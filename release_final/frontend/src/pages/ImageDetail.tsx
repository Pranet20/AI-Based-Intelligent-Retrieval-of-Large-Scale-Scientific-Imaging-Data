import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ScientificImage } from "../types";
import { ApiClient } from "../api/client";

export const ImageDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [image, setImage] = useState<ScientificImage | null>(null);
  const [provenance, setProvenance] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    const imgId = parseInt(id, 10);
    Promise.all([
      ApiClient.getImage(imgId),
      ApiClient.getProvenance(imgId).catch(() => []),
    ])
      .then(([imgData, provData]) => {
        setImage(imgData);
        setProvenance(provData);
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div style={{ padding: "32px", color: "#64748b" }}>Loading micrograph profile...</div>;
  if (!image) return <div style={{ padding: "32px", color: "#ef4444" }}>Micrograph not found.</div>;

  const q = image.quality;
  const d = image.duplicate;
  const n = image.novelty;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px", maxWidth: "1000px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ fontSize: "22px", fontWeight: "700", color: "#0f172a" }}>
            Micrograph Profile #{image.id}: {image.filename}
          </h1>
          <p style={{ fontSize: "13px", color: "#64748b" }}>
            Project #{image.project_id} &bull; Uploaded {new Date(image.uploaded_at).toLocaleString()}
          </p>
        </div>
        <div style={{
          padding: "6px 12px",
          borderRadius: "4px",
          fontSize: "13px",
          fontWeight: "600",
          backgroundColor: image.status === "READY" ? "#dcfce7" : "#fef3c7",
          color: image.status === "READY" ? "#166534" : "#92400e"
        }}>
          Status: {image.status}
        </div>
      </div>

      {/* Grid: Metadata & Integrity */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
        {/* Physical & Acquisition Metadata */}
        <div style={{ backgroundColor: "#ffffff", padding: "20px", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
          <h2 style={{ fontSize: "15px", fontWeight: "600", color: "#0f172a", marginBottom: "12px" }}>
            Acquisition & Format Metadata
          </h2>
          <div style={{ display: "flex", flexDirection: "column", gap: "8px", fontSize: "13px" }}>
            <div><strong>Modality:</strong> {image.modality}</div>
            <div><strong>Instrument:</strong> {image.instrument || "N/A"}</div>
            <div><strong>Specimen ID:</strong> {image.specimen_id || "N/A"}</div>
            <div><strong>ROI ID:</strong> {image.roi_id || "N/A"}</div>
            <div><strong>Acquisition Run:</strong> {image.acquisition_id || "N/A"}</div>
            <div><strong>Dimensions:</strong> {image.width} × {image.height} px</div>
            <div><strong>Channels:</strong> {image.channels} ({image.bit_depth})</div>
            <div><strong>Format:</strong> {image.format}</div>
            <div style={{ wordBreak: "break-all" }}>
              <strong>SHA-256:</strong> <code>{image.sha256}</code>
            </div>
          </div>
        </div>

        {/* Quality Risk Breakdown */}
        <div style={{ backgroundColor: "#ffffff", padding: "20px", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
            <h2 style={{ fontSize: "15px", fontWeight: "600", color: "#0f172a" }}>
              Image-Derived Quality Risk
            </h2>
            <span style={{
              fontSize: "12px",
              padding: "2px 8px",
              borderRadius: "4px",
              fontWeight: "600",
              backgroundColor: q?.quality_label === "NOMINAL" ? "#dcfce7" : "#fee2e2",
              color: q?.quality_label === "NOMINAL" ? "#166534" : "#991b1b"
            }}>
              {q?.quality_label || "NOT COMPUTED"}
            </span>
          </div>
          {q ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "6px", fontSize: "13px" }}>
              <div><strong>Composite Quality Risk:</strong> {q.composite_quality_risk.toFixed(4)}</div>
              <div><strong>Laplacian Variance:</strong> {q.laplacian_variance.toFixed(2)}</div>
              <div><strong>Edge Density:</strong> {q.edge_density.toFixed(4)}</div>
              <div><strong>Shannon Entropy:</strong> {q.shannon_entropy.toFixed(3)} bits</div>
              <div><strong>Dynamic Range:</strong> {q.dynamic_range.toFixed(3)}</div>
              <div><strong>Clipping Ratio:</strong> {(q.clipping_ratio * 100).toFixed(2)}%</div>
              <div><strong>High-Freq FFT Ratio:</strong> {q.high_freq_fft_ratio.toFixed(4)}</div>
            </div>
          ) : (
            <div style={{ fontSize: "13px", color: "#64748b" }}>No quality metrics computed.</div>
          )}
        </div>
      </div>

      {/* Redundancy & Novelty Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
        {/* Redundancy */}
        <div style={{ backgroundColor: "#ffffff", padding: "20px", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
          <h2 style={{ fontSize: "15px", fontWeight: "600", color: "#0f172a", marginBottom: "12px" }}>
            Multi-Stage Duplicate Cascade
          </h2>
          {d ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "6px", fontSize: "13px" }}>
              <div><strong>Status:</strong> {d.duplicate_status}</div>
              <div><strong>Action Recommendation:</strong> {d.action}</div>
              <div><strong>Matching Stage:</strong> {d.match_stage || "None"}</div>
              {d.matched_image_id && (
                <div>
                  <strong>Matched Image:</strong>{" "}
                  <Link to={`/images/${d.matched_image_id}`} style={{ color: "#2563eb", fontWeight: "600" }}>
                    Image #{d.matched_image_id}
                  </Link>{" "}
                  (Sim: {d.similarity_score?.toFixed(4)})
                </div>
              )}
            </div>
          ) : (
            <div style={{ fontSize: "13px", color: "#64748b" }}>Redundancy analysis pending.</div>
          )}
        </div>

        {/* Novelty */}
        <div style={{ backgroundColor: "#ffffff", padding: "20px", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
          <h2 style={{ fontSize: "15px", fontWeight: "600", color: "#0f172a", marginBottom: "12px" }}>
            Relative Embedding-Space Novelty
          </h2>
          {n ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "6px", fontSize: "13px" }}>
              <div><strong>Novelty Score:</strong> {n.novelty_score.toFixed(4)} (Mean k-NN Cosine Dist)</div>
              <div><strong>Novelty Percentile:</strong> {n.novelty_percentile.toFixed(1)}%</div>
              <div><strong>Reference Corpus:</strong> {n.reference_corpus}</div>
              <div style={{ color: "#64748b", fontSize: "12px", marginTop: "4px" }}>
                <em>{n.interpretation}</em>
              </div>
            </div>
          ) : (
            <div style={{ fontSize: "13px", color: "#64748b" }}>Novelty evaluation pending.</div>
          )}
        </div>
      </div>

      {/* Provenance History */}
      <div style={{ backgroundColor: "#ffffff", padding: "20px", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
        <h2 style={{ fontSize: "15px", fontWeight: "600", color: "#0f172a", marginBottom: "12px" }}>
          Cryptographic Provenance Trail
        </h2>
        {provenance.length === 0 ? (
          <div style={{ fontSize: "13px", color: "#64748b" }}>No provenance events recorded.</div>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
            <thead>
              <tr style={{ backgroundColor: "#f8fafc", textAlign: "left", color: "#64748b" }}>
                <th style={{ padding: "8px" }}>Event Type</th>
                <th style={{ padding: "8px" }}>Actor</th>
                <th style={{ padding: "8px" }}>Timestamp</th>
                <th style={{ padding: "8px" }}>Details</th>
              </tr>
            </thead>
            <tbody>
              {provenance.map((ev, i) => (
                <tr key={i} style={{ borderBottom: "1px solid #f1f5f9" }}>
                  <td style={{ padding: "8px", fontWeight: "600" }}>{ev.event_type}</td>
                  <td style={{ padding: "8px" }}>{ev.actor || "SYSTEM"}</td>
                  <td style={{ padding: "8px", color: "#64748b" }}>{new Date(ev.timestamp).toLocaleString()}</td>
                  <td style={{ padding: "8px", color: "#475569" }}>{JSON.stringify(ev.details || {})}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
