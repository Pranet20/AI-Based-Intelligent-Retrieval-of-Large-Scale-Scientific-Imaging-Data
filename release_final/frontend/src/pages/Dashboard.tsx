import React, { useEffect, useState } from "react";
import { MetricCard } from "../components/MetricCard";

interface DashboardStats {
  total_images: number;
  total_projects: number;
  potential_redundancies: number;
  quality_risk_items: number;
  pending_reviews: number;
  completed_reviews: number;
  faiss_indexed_vectors: number;
}

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/v1/dashboard/stats")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load dashboard metrics");
        return res.json();
      })
      .then((data) => {
        setStats(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div style={{ padding: "32px", color: "#64748b" }}>Loading platform statistics...</div>;
  }

  if (error || !stats) {
    return (
      <div style={{ padding: "32px", color: "#ef4444" }}>
        Failed to load database metrics: {error || "Unknown error"}
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <div>
        <h1 style={{ fontSize: "24px", fontWeight: "700", color: "#0f172a" }}>Research Platform Overview</h1>
        <p style={{ fontSize: "14px", color: "#64748b" }}>
          Live metrics dynamically aggregated from relational metadata and exact FAISS vector index.
        </p>
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "16px" }}>
        <MetricCard
          title="Indexed Micrographs"
          value={stats.total_images.toLocaleString()}
          subtitle="Managed in storage"
          badge="Live"
          badgeColor="#0284c7"
        />
        <MetricCard
          title="FAISS Vectors"
          value={stats.faiss_indexed_vectors.toLocaleString()}
          subtitle="384-D Exact IndexFlatIP"
          badge="Vector DB"
          badgeColor="#16a34a"
        />
        <MetricCard
          title="Active Projects"
          value={stats.total_projects.toLocaleString()}
          subtitle="Registered repositories"
        />
        <MetricCard
          title="Redundancies Detected"
          value={stats.potential_redundancies.toLocaleString()}
          subtitle="Exact & near duplicates"
          badge={stats.potential_redundancies > 0 ? "Review Needed" : "Clean"}
          badgeColor={stats.potential_redundancies > 0 ? "#ea580c" : "#16a34a"}
        />
        <MetricCard
          title="Quality Risk Items"
          value={stats.quality_risk_items.toLocaleString()}
          subtitle="Composite risk score >= 0.50"
          badge="Physical Metrics"
          badgeColor={stats.quality_risk_items > 0 ? "#dc2626" : "#16a34a"}
        />
        <MetricCard
          title="Pending Reviews"
          value={stats.pending_reviews.toLocaleString()}
          subtitle="Awaiting human curator"
          badge="Review Queue"
          badgeColor="#8b5cf6"
        />
      </div>

      <div style={{
        backgroundColor: "#ffffff",
        padding: "24px",
        borderRadius: "8px",
        border: "1px solid #e2e8f0"
      }}>
        <h2 style={{ fontSize: "16px", fontWeight: "600", marginBottom: "12px", color: "#0f172a" }}>
          Pipeline Architecture Status
        </h2>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "14px" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid #e2e8f0", textAlign: "left", color: "#64748b" }}>
              <th style={{ padding: "8px 0" }}>Component</th>
              <th style={{ padding: "8px 0" }}>Authoritative Baseline</th>
              <th style={{ padding: "8px 0" }}>Dimensionality / Target</th>
              <th style={{ padding: "8px 0" }}>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr style={{ borderBottom: "1px solid #f1f5f9" }}>
              <td style={{ padding: "10px 0", fontWeight: "500" }}>Visual Backbone</td>
              <td style={{ padding: "10px 0", color: "#475569" }}>Meta DINOv2 ViT-S/14</td>
              <td style={{ padding: "10px 0", color: "#475569" }}>384 (L2 Normalized)</td>
              <td style={{ padding: "10px 0", color: "#16a34a", fontWeight: "600" }}>Active & Frozen</td>
            </tr>
            <tr style={{ borderBottom: "1px solid #f1f5f9" }}>
              <td style={{ padding: "10px 0", fontWeight: "500" }}>Acquisition Adapter</td>
              <td style={{ padding: "10px 0", color: "#475569" }}>Phase 4 Linear Projection (Seed 42)</td>
              <td style={{ padding: "10px 0", color: "#475569" }}>384 -> 384</td>
              <td style={{ padding: "10px 0", color: "#16a34a", fontWeight: "600" }}>SHA-256 Verified</td>
            </tr>
            <tr style={{ borderBottom: "1px solid #f1f5f9" }}>
              <td style={{ padding: "10px 0", fontWeight: "500" }}>Vector Search Index</td>
              <td style={{ padding: "10px 0", color: "#475569" }}>Exact FAISS IndexFlatIP</td>
              <td style={{ padding: "10px 0", color: "#475569" }}>Inner Product / Cosine</td>
              <td style={{ padding: "10px 0", color: "#16a34a", fontWeight: "600" }}>Operational</td>
            </tr>
            <tr>
              <td style={{ padding: "10px 0", fontWeight: "500" }}>Integrity Cascade</td>
              <td style={{ padding: "10px 0", color: "#475569" }}>6-Stage Scientific Redundancy & Risk</td>
              <td style={{ padding: "10px 0", color: "#475569" }}>Exact + Near-Duplicate + SSIM</td>
              <td style={{ padding: "10px 0", color: "#16a34a", fontWeight: "600" }}>Enabled</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};
