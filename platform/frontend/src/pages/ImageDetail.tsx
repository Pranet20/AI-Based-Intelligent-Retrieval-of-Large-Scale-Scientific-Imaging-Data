import React, { useEffect, useState, useRef } from "react";
import { useParams, Link } from "react-router-dom";
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  RotateCcw,
  Copy,
  Check,
  Search,
  CheckSquare,
  Layers,
  Activity,
  ShieldCheck,
  Microscope,
  Info,
  Calendar,
  Tag
} from "lucide-react";
import { ApiClient, ImageDetailResponse } from "../api/client";

export const ImageDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [image, setImage] = useState<ImageDetailResponse | null>(null);
  const [provenance, setProvenance] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [copiedSha, setCopiedSha] = useState(false);

  // Pan & Zoom interactive controls
  const [zoom, setZoom] = useState<number>(1.0);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [showMetadataHud, setShowMetadataHud] = useState(true);

  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!id) return;
    const imgId = parseInt(id, 10);
    setLoading(true);
    Promise.all([
      ApiClient.getImage(imgId),
      ApiClient.getProvenance(imgId).catch(() => []),
    ])
      .then(([imgData, provData]) => {
        setImage(imgData);
        setProvenance(provData);
      })
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  }, [id]);

  const handleCopySha = () => {
    if (!image?.sha256) return;
    navigator.clipboard.writeText(image.sha256);
    setCopiedSha(true);
    setTimeout(() => setCopiedSha(false), 2000);
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleZoom = (delta: number) => {
    setZoom((prev) => Math.min(Math.max(0.2, prev + delta), 5.0));
  };

  const handleResetView = () => {
    setZoom(1.0);
    setPan({ x: 0, y: 0 });
  };

  if (loading) {
    return (
      <div style={{ padding: "40px", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: "10px" }}>
        <Activity size={20} className="animate-spin" />
        <span>Loading scientific micrograph and physical metadata...</span>
      </div>
    );
  }

  if (!image) {
    return (
      <div className="card" style={{ borderLeft: "4px solid var(--status-risk)", padding: "24px" }}>
        <div style={{ color: "var(--status-risk)", fontWeight: 600 }}>Micrograph Not Found</div>
        <p style={{ color: "var(--text-secondary)", fontSize: "14px", marginTop: "4px" }}>
          The requested micrograph #{id} could not be retrieved from platform storage.
        </p>
        <Link to="/explorer" className="btn btn-secondary btn-sm" style={{ marginTop: "16px" }}>
          Return to Explorer
        </Link>
      </div>
    );
  }

  const q = image.quality;
  const d = image.duplicate;
  const m = image.metadata;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      {/* Top Header & Breadcrumbs */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "12px", color: "var(--text-muted)", marginBottom: "4px" }}>
            <Link to="/explorer">Explorer</Link>
            <span>/</span>
            <span>Project #{image.project_id}</span>
            <span>/</span>
            <span style={{ color: "var(--text-primary)" }}>#{image.id}</span>
          </div>
          <h1 style={{ fontSize: "20px", fontWeight: "700", color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "10px" }}>
            <span>{image.original_filename}</span>
            <span className={`badge ${image.processing_status === "VERIFIED" ? "badge-nominal" : image.processing_status === "FLAGGED" ? "badge-risk" : "badge-info"}`}>
              {image.processing_status}
            </span>
          </h1>
        </div>

        <div style={{ display: "flex", gap: "10px" }}>
          <Link to={`/search?query_id=${image.id}`} className="btn btn-primary btn-sm">
            <Search size={14} />
            <span>Search Similar</span>
          </Link>
          <Link to={`/reviews?image_id=${image.id}`} className="btn btn-secondary btn-sm">
            <CheckSquare size={14} />
            <span>Curate Image</span>
          </Link>
        </div>
      </div>

      {/* Main Two-Column Layout: Left Viewport (Interactive Pan/Zoom), Right Metadata Inspector */}
      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "20px", alignItems: "start" }}>
        {/* Left: Scientific Viewport */}
        <div className="card" style={{ padding: "0", overflow: "hidden", display: "flex", flexDirection: "column" }}>
          {/* Viewer Toolbar */}
          <div style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "10px 16px",
            backgroundColor: "var(--bg-surface-elevated)",
            borderBottom: "1px solid var(--border-default)"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <button onClick={() => handleZoom(0.25)} className="btn btn-secondary btn-sm" title="Zoom In">
                <ZoomIn size={14} />
              </button>
              <button onClick={() => handleZoom(-0.25)} className="btn btn-secondary btn-sm" title="Zoom Out">
                <ZoomOut size={14} />
              </button>
              <button onClick={handleResetView} className="btn btn-secondary btn-sm" title="Reset (100%)">
                <RotateCcw size={14} />
                <span className="font-mono">{Math.round(zoom * 100)}%</span>
              </button>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <button
                onClick={() => setShowMetadataHud(!showMetadataHud)}
                className="btn btn-secondary btn-sm"
                title="Toggle HUD Overlay"
              >
                <Info size={14} />
                <span>HUD</span>
              </button>
              <a
                href={ApiClient.getImageUrl(image.id)}
                target="_blank"
                rel="noreferrer"
                className="btn btn-secondary btn-sm"
                title="Open Raw File"
              >
                <Maximize2 size={14} />
              </a>
            </div>
          </div>

          {/* Interactive Micrograph Canvas */}
          <div
            ref={containerRef}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            style={{
              height: "480px",
              backgroundColor: "#000000",
              overflow: "hidden",
              position: "relative",
              cursor: isDragging ? "grabbing" : "grab",
              display: "flex",
              alignItems: "center",
              justifyContent: "center"
            }}
          >
            <img
              src={ApiClient.getImageUrl(image.id)}
              alt={image.original_filename}
              draggable={false}
              style={{
                transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
                transition: isDragging ? "none" : "transform var(--transition-fast)",
                maxHeight: "90%",
                maxWidth: "90%",
                objectFit: "contain",
                userSelect: "none"
              }}
              onError={(e: any) => {
                e.target.src = ApiClient.getImageThumbnailUrl(image.id);
              }}
            />

            {/* Scientific HUD Overlay */}
            {showMetadataHud && (
              <div style={{
                position: "absolute",
                bottom: "12px",
                left: "12px",
                backgroundColor: "rgba(15, 23, 42, 0.85)",
                backdropFilter: "blur(6px)",
                border: "1px solid var(--border-default)",
                borderRadius: "var(--radius-md)",
                padding: "8px 12px",
                fontSize: "11px",
                color: "var(--text-secondary)",
                display: "flex",
                flexDirection: "column",
                gap: "3px",
                pointerEvents: "none"
              }}>
                <div style={{ color: "var(--text-primary)", fontWeight: 600, display: "flex", alignItems: "center", gap: "6px" }}>
                  <Microscope size={12} color="var(--accent-cyan)" />
                  <span>{m?.microscope || "Scanning Electron Microscope"}</span>
                </div>
                <div className="font-mono">
                  {image.width} × {image.height} px &bull; {m?.accelerating_voltage_kv ? `${m.accelerating_voltage_kv} kV` : "KV Unset"}
                  {m?.magnification ? ` &bull; ${m.magnification.toLocaleString()}x` : ""}
                </div>
                <div className="font-mono" style={{ color: "var(--text-muted)" }}>
                  Detector: {m?.detector || "SE/BSE"} &bull; Scale: {m?.pixel_size_nm ? `${m.pixel_size_nm.toFixed(2)} nm/px` : "N/A"}
                </div>
              </div>
            )}
          </div>

          {/* Cryptographic SHA-256 Fingerprint */}
          <div style={{
            padding: "10px 16px",
            backgroundColor: "var(--bg-canvas)",
            borderTop: "1px solid var(--border-subtle)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            fontSize: "11px"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", overflow: "hidden" }}>
              <ShieldCheck size={14} color="var(--status-nominal)" />
              <span style={{ color: "var(--text-muted)" }}>SHA-256:</span>
              <span className="font-mono" style={{ color: "var(--text-primary)", textOverflow: "ellipsis", overflow: "hidden", whiteSpace: "nowrap" }}>
                {image.sha256}
              </span>
            </div>
            <button
              onClick={handleCopySha}
              className="btn btn-secondary btn-sm"
              style={{ padding: "2px 8px", fontSize: "11px" }}
              title="Copy Checksum"
            >
              {copiedSha ? <Check size={12} color="var(--status-nominal)" /> : <Copy size={12} />}
              <span>{copiedSha ? "Copied" : "Copy"}</span>
            </button>
          </div>
        </div>

        {/* Right: Scientific Metadata & Physical Integrity Inspector */}
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {/* Physical Quality Indicators */}
          <div className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
              <h2 style={{ fontSize: "14px", fontWeight: "600", color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "8px" }}>
                <Activity size={16} color="var(--accent-primary)" />
                <span>Image-Derived Quality-Risk Indicators</span>
              </h2>
              <span className={`badge ${q?.quality_label === "NOMINAL" ? "badge-nominal" : "badge-risk"}`}>
                {q?.quality_label || "COMPUTED"}
              </span>
            </div>

            {q ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                {/* Composite Risk Bar */}
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", marginBottom: "4px" }}>
                    <span style={{ color: "var(--text-secondary)" }}>Composite Quality Risk Score</span>
                    <span className="font-mono" style={{
                      fontWeight: 600,
                      color: q.composite_quality_risk >= 0.60 ? "var(--status-risk)" : "var(--status-nominal)"
                    }}>
                      {(q.composite_quality_risk * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div style={{ height: "6px", backgroundColor: "var(--bg-canvas)", borderRadius: "var(--radius-full)", overflow: "hidden" }}>
                    <div style={{
                      height: "100%",
                      width: `${Math.min(100, q.composite_quality_risk * 100)}%`,
                      backgroundColor: q.composite_quality_risk >= 0.60 ? "var(--status-risk)" : "var(--status-nominal)",
                      transition: "width var(--transition-base)"
                    }} />
                  </div>
                </div>

                {/* Sub-indicator Metric Grid */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", fontSize: "12px", marginTop: "4px" }}>
                  <div style={{ padding: "8px", backgroundColor: "var(--bg-canvas)", borderRadius: "var(--radius-sm)" }}>
                    <span style={{ color: "var(--text-muted)", display: "block" }}>Laplacian Variance:</span>
                    <span className="font-mono" style={{ fontWeight: 600 }}>{q.laplacian_variance?.toFixed(2) ?? "—"}</span>
                  </div>
                  <div style={{ padding: "8px", backgroundColor: "var(--bg-canvas)", borderRadius: "var(--radius-sm)" }}>
                    <span style={{ color: "var(--text-muted)", display: "block" }}>Edge Density:</span>
                    <span className="font-mono" style={{ fontWeight: 600 }}>{q.edge_density?.toFixed(4) ?? "—"}</span>
                  </div>
                  <div style={{ padding: "8px", backgroundColor: "var(--bg-canvas)", borderRadius: "var(--radius-sm)" }}>
                    <span style={{ color: "var(--text-muted)", display: "block" }}>Shannon Entropy:</span>
                    <span className="font-mono" style={{ fontWeight: 600 }}>{q.shannon_entropy?.toFixed(3) ?? "—"} bits</span>
                  </div>
                  <div style={{ padding: "8px", backgroundColor: "var(--bg-canvas)", borderRadius: "var(--radius-sm)" }}>
                    <span style={{ color: "var(--text-muted)", display: "block" }}>Dynamic Range:</span>
                    <span className="font-mono" style={{ fontWeight: 600 }}>{q.dynamic_range?.toFixed(3) ?? "—"}</span>
                  </div>
                  <div style={{ padding: "8px", backgroundColor: "var(--bg-canvas)", borderRadius: "var(--radius-sm)" }}>
                    <span style={{ color: "var(--text-muted)", display: "block" }}>Clipping Ratio:</span>
                    <span className="font-mono" style={{ fontWeight: 600 }}>
                      {q.clipping_ratio !== undefined ? `${(q.clipping_ratio * 100).toFixed(2)}%` : "—"}
                    </span>
                  </div>
                  <div style={{ padding: "8px", backgroundColor: "var(--bg-canvas)", borderRadius: "var(--radius-sm)" }}>
                    <span style={{ color: "var(--text-muted)", display: "block" }}>High-Freq FFT Ratio:</span>
                    <span className="font-mono" style={{ fontWeight: 600 }}>{q.high_freq_fft_ratio?.toFixed(4) ?? "—"}</span>
                  </div>
                </div>
              </div>
            ) : (
              <p style={{ fontSize: "12px", color: "var(--text-muted)" }}>No physical quality indicators recorded.</p>
            )}
          </div>

          {/* Acquisition & Physical Parameters */}
          <div className="card">
            <h2 style={{ fontSize: "14px", fontWeight: "600", color: "var(--text-primary)", marginBottom: "12px", display: "flex", alignItems: "center", gap: "8px" }}>
              <Microscope size={16} color="var(--accent-cyan)" />
              <span>Acquisition & Physical Parameters</span>
            </h2>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", fontSize: "12px" }}>
              <div>
                <span style={{ color: "var(--text-muted)", display: "block" }}>Accelerating Voltage:</span>
                <span className="font-mono" style={{ fontWeight: 600 }}>
                  {m?.accelerating_voltage_kv ? `${m.accelerating_voltage_kv} kV` : "—"}
                </span>
              </div>
              <div>
                <span style={{ color: "var(--text-muted)", display: "block" }}>Detector:</span>
                <span className="font-mono" style={{ fontWeight: 600 }}>{m?.detector || "—"}</span>
              </div>
              <div>
                <span style={{ color: "var(--text-muted)", display: "block" }}>Magnification:</span>
                <span className="font-mono" style={{ fontWeight: 600 }}>
                  {m?.magnification ? `${m.magnification.toLocaleString()}x` : "—"}
                </span>
              </div>
              <div>
                <span style={{ color: "var(--text-muted)", display: "block" }}>Pixel Size:</span>
                <span className="font-mono" style={{ fontWeight: 600 }}>
                  {m?.pixel_size_nm ? `${m.pixel_size_nm.toFixed(2)} nm` : "—"}
                </span>
              </div>
              <div>
                <span style={{ color: "var(--text-muted)", display: "block" }}>Working Distance:</span>
                <span className="font-mono" style={{ fontWeight: 600 }}>
                  {m?.working_distance_mm ? `${m.working_distance_mm} mm` : "—"}
                </span>
              </div>
              <div>
                <span style={{ color: "var(--text-muted)", display: "block" }}>Dwell Time:</span>
                <span className="font-mono" style={{ fontWeight: 600 }}>
                  {m?.dwell_time_us ? `${m.dwell_time_us} µs` : "—"}
                </span>
              </div>
            </div>
          </div>

          {/* Redundancy & Novelty Assessment */}
          <div className="card">
            <h2 style={{ fontSize: "14px", fontWeight: "600", color: "var(--text-primary)", marginBottom: "12px", display: "flex", alignItems: "center", gap: "8px" }}>
              <Layers size={16} color="var(--accent-indigo)" />
              <span>Multi-Stage Redundancy & Novelty</span>
            </h2>

            <div style={{ display: "flex", flexDirection: "column", gap: "8px", fontSize: "12px" }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-secondary)" }}>Redundancy Cascade:</span>
                <span className={`badge ${
                  d?.duplicate_status === "NO_DECLARED_REDUNDANCY_DETECTED" ? "badge-nominal" : "badge-warning"
                }`}>
                  {d?.duplicate_status || "ANALYZED"}
                </span>
              </div>

              {d?.matched_image_id && (
                <div style={{ padding: "8px", backgroundColor: "var(--bg-canvas)", borderRadius: "var(--radius-sm)", display: "flex", justifyContent: "space-between" }}>
                  <span style={{ color: "var(--text-muted)" }}>Matched Micrograph:</span>
                  <Link to={`/images/${d.matched_image_id}`} style={{ fontWeight: 600 }}>
                    #{d.matched_image_id} (Sim: {d.similarity_score?.toFixed(4)})
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Cryptographic Provenance Timeline */}
      <div className="card">
        <h2 style={{ fontSize: "14px", fontWeight: "600", color: "var(--text-primary)", marginBottom: "12px", display: "flex", alignItems: "center", gap: "8px" }}>
          <ShieldCheck size={16} color="var(--status-nominal)" />
          <span>Cryptographic Provenance & Audit Trail</span>
        </h2>

        {provenance.length === 0 ? (
          <p style={{ fontSize: "12px", color: "var(--text-muted)" }}>
            Initial ingestion event recorded at {new Date(image.created_at).toLocaleString()}.
          </p>
        ) : (
          <div className="table-container">
            <table className="scientific-table">
              <thead>
                <tr>
                  <th>Event Type</th>
                  <th>Actor / System</th>
                  <th>Timestamp</th>
                  <th>Execution Parameters</th>
                </tr>
              </thead>
              <tbody>
                {provenance.map((ev, idx) => (
                  <tr key={idx}>
                    <td>
                      <span className="badge badge-info">{ev.event_type}</span>
                    </td>
                    <td style={{ fontWeight: 600 }}>{ev.actor || "PIPELINE_ENGINE"}</td>
                    <td className="font-mono" style={{ color: "var(--text-secondary)" }}>
                      {new Date(ev.timestamp).toLocaleString()}
                    </td>
                    <td className="font-mono" style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                      {JSON.stringify(ev.details || ev.parameters || {})}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
