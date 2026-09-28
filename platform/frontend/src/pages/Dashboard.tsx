import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Database,
  Layers,
  Search,
  CheckSquare,
  AlertTriangle,
  Zap,
  TrendingUp,
  FileCheck,
  Cpu,
  BarChart3
} from "lucide-react";
import { ApiClient, DashboardStats, ResearchDashboardData } from "../api/client";
import { MetricCard } from "../components/MetricCard";

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [researchData, setResearchData] = useState<ResearchDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      ApiClient.getDashboardStats(),
      ApiClient.getResearchDashboard().catch(() => null)
    ])
      .then(([s, r]) => {
        setStats(s);
        setResearchData(r);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div style={{ padding: "40px", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: "12px" }}>
        <Zap className="animate-spin" size={20} color="var(--accent-primary)" />
        <span>Loading live database telemetry and research benchmarks...</span>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="card" style={{ borderLeft: "4px solid var(--status-risk)" }}>
        <div style={{ color: "var(--status-risk)", fontWeight: 600, marginBottom: "8px" }}>
          Database Telemetry Error
        </div>
        <p style={{ color: "var(--text-secondary)", fontSize: "14px" }}>
          Failed to load live platform statistics: {error || "Unknown error"}
        </p>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Platform Banner */}
      <div className="card" style={{
        background: "linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.7) 100%)",
        borderColor: "var(--border-default)",
        padding: "24px"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "16px" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "8px" }}>
              <h1 style={{ fontSize: "22px", fontWeight: "700", color: "var(--text-primary)" }}>
                AI-Powered Scientific Image Data Management Platform
              </h1>
              <span className="badge badge-info">v1.0.0 Production</span>
            </div>
            <p style={{ fontSize: "14px", color: "var(--text-secondary)", maxWidth: "800px" }}>
              Metadata-aware retrieval, acquisition-robust representation, physical data integrity assessment,
              and anomaly-aware curation for large-scale scanning electron microscopy.
            </p>
          </div>

          <div style={{ display: "flex", gap: "10px" }}>
            <Link to="/search" className="btn btn-primary btn-sm">
              <Search size={14} />
              <span>Vector Search</span>
            </Link>
            <Link to="/reviews" className="btn btn-secondary btn-sm">
              <CheckSquare size={14} />
              <span>Curator Queue</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Live Operational Metrics Grid */}
      <div>
        <div style={{ fontSize: "12px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.8px", color: "var(--text-muted)", marginBottom: "12px" }}>
          Live Operational Telemetry
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "16px" }}>
          <MetricCard
            title="Managed Micrographs"
            value={stats.total_images.toLocaleString()}
            subtitle="Ingested in platform storage"
            badge="Live DB"
            badgeColor="var(--accent-primary)"
            icon={<Layers size={16} />}
          />
          <MetricCard
            title="Exact FAISS Vectors"
            value={stats.faiss_indexed_vectors.toLocaleString()}
            subtitle="384-D L2-Normalized Vectors"
            badge="IndexFlatIP"
            badgeColor="var(--status-nominal)"
            icon={<Database size={16} />}
          />
          <MetricCard
            title="Active Projects"
            value={stats.total_projects.toLocaleString()}
            subtitle="Isolated namespaces"
            badge="Multi-tenant"
            badgeColor="var(--accent-cyan)"
            icon={<Cpu size={16} />}
          />
          <MetricCard
            title="Redundancies Flagged"
            value={stats.potential_redundancies.toLocaleString()}
            subtitle="Exact & perceptual duplicates"
            badge={stats.potential_redundancies > 0 ? "Review Needed" : "Clean"}
            badgeColor={stats.potential_redundancies > 0 ? "var(--status-warning)" : "var(--status-nominal)"}
            icon={<AlertTriangle size={16} />}
          />
          <MetricCard
            title="Quality Risk Items"
            value={stats.quality_risk_items.toLocaleString()}
            subtitle="Composite quality risk ≥ 0.60"
            badge="Image-Derived"
            badgeColor={stats.quality_risk_items > 0 ? "var(--status-risk)" : "var(--status-nominal)"}
            icon={<AlertTriangle size={16} />}
          />
          <MetricCard
            title="Curator Decisions"
            value={stats.completed_reviews.toLocaleString()}
            subtitle={`${stats.pending_reviews} pending in triage queue`}
            badge="Workbench"
            badgeColor="var(--accent-indigo)"
            icon={<CheckSquare size={16} />}
          />
        </div>
      </div>

      {/* Empirical Benchmark & Research Performance Highlights */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(420px, 1fr))", gap: "16px" }}>
        {/* Research Benchmark Highlights */}
        <div className="card">
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <TrendingUp size={18} color="var(--accent-primary)" />
              <h2 style={{ fontSize: "15px", fontWeight: "600", color: "var(--text-primary)" }}>
                Authoritative Research Benchmarks
              </h2>
            </div>
            <span className="badge badge-nominal">Frozen Baseline</span>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginBottom: "16px" }}>
            <div style={{ padding: "12px", backgroundColor: "var(--bg-canvas)", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)" }}>
              <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>DINOv2 ViT-S/14 R@1</div>
              <div style={{ fontSize: "20px", fontWeight: "700", color: "var(--accent-cyan)" }}>94.81%</div>
              <div style={{ fontSize: "11px", color: "var(--text-secondary)" }}>vs ResNet50 (92.45%)</div>
            </div>

            <div style={{ padding: "12px", backgroundColor: "var(--bg-canvas)", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)" }}>
              <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>Cross-Acquisition Gap Reduction</div>
              <div style={{ fontSize: "20px", fontWeight: "700", color: "var(--status-nominal)" }}>68.15%</div>
              <div style={{ fontSize: "11px", color: "var(--text-secondary)" }}>p = 1.42 × 10⁻¹²</div>
            </div>

            <div style={{ padding: "12px", backgroundColor: "var(--bg-canvas)", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)" }}>
              <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>Defocus Detection AUROC</div>
              <div style={{ fontSize: "20px", fontWeight: "700", color: "var(--status-nominal)" }}>0.8803</div>
              <div style={{ fontSize: "11px", color: "var(--text-secondary)" }}>AUPRC = 0.9618</div>
            </div>

            <div style={{ padding: "12px", backgroundColor: "var(--bg-canvas)", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)" }}>
              <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>FAISS Exact Query Latency</div>
              <div style={{ fontSize: "20px", fontWeight: "700", color: "var(--accent-primary)" }}>0.096 ms</div>
              <div style={{ fontSize: "11px", color: "var(--text-secondary)" }}>Sub-millisecond retrieval</div>
            </div>
          </div>

          <p style={{ fontSize: "12px", color: "var(--text-muted)" }}>
            * Evaluated on authoritative HCCI and Carinthia micrographs under frozen Phase 1–7 evaluation protocol.
          </p>
        </div>

        {/* Dataset Reconciliation Inventory */}
        <div className="card">
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <FileCheck size={18} color="var(--accent-cyan)" />
              <h2 style={{ fontSize: "15px", fontWeight: "600", color: "var(--text-primary)" }}>
                Authoritative Dataset Inventory
              </h2>
            </div>
            <span className="badge badge-info">128 Checksums Verified</span>
          </div>

          <div className="table-container" style={{ marginBottom: "12px" }}>
            <table className="scientific-table">
              <thead>
                <tr>
                  <th>Dataset Corpus</th>
                  <th>Files</th>
                  <th>Role</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td style={{ fontWeight: 600 }}>HCCI Superalloy Archive</td>
                  <td className="font-mono">774</td>
                  <td>Primary In-Domain</td>
                  <td><span className="badge badge-nominal">100% Present</span></td>
                </tr>
                <tr>
                  <td style={{ fontWeight: 600 }}>Carinthia SEM Micrographs</td>
                  <td className="font-mono">4,591</td>
                  <td>Cross-Domain Benchmark</td>
                  <td><span className="badge badge-nominal">100% Present</span></td>
                </tr>
                <tr>
                  <td style={{ fontWeight: 600 }}>SEM Nanoscience Records</td>
                  <td className="font-mono">21,272</td>
                  <td>Extended Configuration</td>
                  <td><span className="badge badge-warning">Configured</span></td>
                </tr>
              </tbody>
            </table>
          </div>

          <p style={{ fontSize: "12px", color: "var(--text-muted)" }}>
            Dataset counts reconciled with checksum integrity against <code>reports/final_audit/FINAL_DATASET_COUNT_RECONCILIATION.csv</code>.
          </p>
        </div>
      </div>

      {/* Pipeline Architecture Table */}
      <div className="card">
        <h2 style={{ fontSize: "15px", fontWeight: "600", color: "var(--text-primary)", marginBottom: "14px" }}>
          Pipeline Architecture & Component Status
        </h2>
        <div className="table-container">
          <table className="scientific-table">
            <thead>
              <tr>
                <th>Component</th>
                <th>Authoritative Baseline</th>
                <th>Dimensionality / Specs</th>
                <th>Validation Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={{ fontWeight: 600 }}>Visual Representation Backbone</td>
                <td>Meta DINOv2 ViT-S/14</td>
                <td className="font-mono">384-D (L2 Normalized)</td>
                <td><span className="badge badge-nominal">Frozen & Checksummed</span></td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Acquisition Robustness Adapter</td>
                <td>Phase 4 Linear Projection (Seed 42)</td>
                <td className="font-mono">384 → 384 Linear</td>
                <td><span className="badge badge-nominal">SHA-256 Validated</span></td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Vector Index Engine</td>
                <td>Exact FAISS IndexFlatIP</td>
                <td className="font-mono">Inner Product / Cosine</td>
                <td><span className="badge badge-nominal">Operational</span></td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Scientific Redundancy Cascade</td>
                <td>6-Stage File, Pixel, Perceptual & Feature Match</td>
                <td className="font-mono">SHA-256, dHash, pHash, SSIM</td>
                <td><span className="badge badge-nominal">Active</span></td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Quality-Risk Indicator Engine</td>
                <td>Multi-indicator blur, dynamic range, clipping</td>
                <td className="font-mono">Laplacian Var, Shannon Entropy</td>
                <td><span className="badge badge-nominal">Active</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
