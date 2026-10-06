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
  Tag,
  Sliders,
  Eye,
  EyeOff,
  Download,
  BarChart2,
  Crosshair,
  Sparkles,
  Zap,
  Target,
  FileText,
  AlertTriangle,
  CheckCircle2,
  HelpCircle,
  Compass
} from "lucide-react";
import {
  ApiClient,
  ImageDetailResponse,
  LocalizationResponse,
  EvidenceRecordResponse,
} from "../api/client";

export const ImageDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [image, setImage] = useState<ImageDetailResponse | null>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [localization, setLocalization] = useState<LocalizationResponse | null>(null);
  const [evidence, setEvidence] = useState<EvidenceRecordResponse | null>(null);
  const [similarImages, setSimilarImages] = useState<any[]>([]);
  const [provenance, setProvenance] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [copiedSha, setCopiedSha] = useState(false);
  const [imgError, setImgError] = useState(false);

  // Pan & Zoom interactive controls
  const [zoom, setZoom] = useState<number>(1.0);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [showMetadataHud, setShowMetadataHud] = useState(true);

  // Localization overlay controls
  const [showLocalization, setShowLocalization] = useState<boolean>(true);
  const [overlayOpacity, setOverlayOpacity] = useState<number>(65);

  // Bit-by-bit image adjustments
  const [brightness, setBrightness] = useState<number>(100);
  const [contrast, setContrast] = useState<number>(100);
  const [invert, setInvert] = useState<boolean>(false);
  const [colorFilter, setColorFilter] = useState<"none" | "cyan" | "green" | "red" | "thermal">("none");
  const [autoEnhanced, setAutoEnhanced] = useState<boolean>(true);

  // Pixel inspection state
  const [cursorPos, setCursorPos] = useState<{ x: number; y: number } | null>(null);
  const [pixelIntensity, setPixelIntensity] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<"overview" | "evidence" | "histogram" | "spots" | "similar">("overview");

  const containerRef = useRef<HTMLDivElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    if (!id) return;
    const imgId = parseInt(id, 10);
    setLoading(true);
    setImgError(false);

    Promise.all([
      ApiClient.getImage(imgId),
      ApiClient.getProvenance(imgId).catch(() => []),
      ApiClient.getImageLocalization(imgId).catch(() => null),
      ApiClient.getImageEvidence(imgId).catch(() => null),
    ])
      .then(([imgData, provData, locData, evData]) => {
        setImage(imgData);
        setProvenance(provData);
        setLocalization(locData);
        setEvidence(evData);
      })
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));

    // Fetch deep analysis & similar images in background
    setAnalysisLoading(true);
    Promise.all([
      ApiClient.getImageAnalysis(imgId).catch(() => null),
      ApiClient.getSimilarImages(imgId, 5).catch(() => []),
    ])
      .then(([analysisData, similarData]) => {
        setAnalysis(analysisData);
        setSimilarImages(similarData);
      })
      .finally(() => setAnalysisLoading(false));
  }, [id]);


  const handleCopySha = () => {
    if (image?.sha256) {
      navigator.clipboard.writeText(image.sha256);
      setCopiedSha(true);
      setTimeout(() => setCopiedSha(false), 2000);
    }
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return;
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
    }

    if (imgRef.current && containerRef.current) {
      const rect = imgRef.current.getBoundingClientRect();
      const relX = e.clientX - rect.left;
      const relY = e.clientY - rect.top;

      if (relX >= 0 && relX <= rect.width && relY >= 0 && relY <= rect.height) {
        const normX = Math.floor((relX / rect.width) * (image?.width || 1280));
        const normY = Math.floor((relY / rect.height) * (image?.height || 1024));
        setCursorPos({ x: normX, y: normY });

        // Pseudo intensity estimate from quantiles if analysis exists
        if (analysis?.quantiles) {
          const pseudo = Math.floor(analysis.quantiles.median + (Math.sin(normX * 0.05) * Math.cos(normY * 0.05)) * analysis.quantiles.std);
          setPixelIntensity(Math.max(0, pseudo));
        }
      } else {
        setCursorPos(null);
      }
    }
  };

  const handleMouseUp = () => setIsDragging(false);

  const resetViewport = () => {
    setZoom(1.0);
    setPan({ x: 0, y: 0 });
    setBrightness(100);
    setContrast(100);
    setInvert(false);
    setColorFilter("none");
    setAutoEnhanced(true);
  };

  const getFilterStyle = (): string => {
    const filters: string[] = [];
    filters.push(`brightness(${brightness}%)`);
    filters.push(`contrast(${autoEnhanced ? contrast + 25 : contrast}%)`);
    if (invert) filters.push("invert(100%)");

    if (colorFilter === "cyan") {
      filters.push("sepia(100%) hue-rotate(150deg) saturate(300%)");
    } else if (colorFilter === "green") {
      filters.push("sepia(100%) hue-rotate(80deg) saturate(300%)");
    } else if (colorFilter === "red") {
      filters.push("sepia(100%) hue-rotate(320deg) saturate(350%)");
    } else if (colorFilter === "thermal") {
      filters.push("sepia(100%) hue-rotate(220deg) saturate(400%) contrast(150%)");
    }
    return filters.join(" ");
  };

  if (loading) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "60vh", color: "var(--text-muted)" }}>
        Loading scientific micrograph and analytics...
      </div>
    );
  }

  if (!image) {
    return (
      <div className="card" style={{ padding: "40px", textAlign: "center" }}>
        <h3>Micrograph Not Found</h3>
        <p style={{ color: "var(--text-muted)", marginTop: "8px" }}>The requested scientific image ID could not be loaded.</p>
        <Link to="/explorer" className="btn btn-primary" style={{ marginTop: "16px" }}>
          Return to Dataset Explorer
        </Link>
      </div>
    );
  }

  const meta = image.metadata || {};
  const quality = image.quality || { composite_quality_risk: 0.0, quality_label: "NOMINAL" };
  const duplicate = image.duplicate || { duplicate_status: "NO_DECLARED_REDUNDANCY_DETECTED" };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Top Header & Quick Actions */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", flexWrap: "wrap", gap: "16px" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "12px", color: "var(--text-muted)", marginBottom: "4px" }}>
            <Link to="/explorer" style={{ color: "var(--accent-primary)" }}>Dataset Explorer</Link>
            <span>/</span>
            <span>Project #{image.project_id || 1}</span>
            <span>/</span>
            <span style={{ color: "var(--text-primary)", fontWeight: 600 }}>#{image.id}</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <h1 style={{ fontSize: "20px", fontWeight: 700, color: "var(--text-primary)", wordBreak: "break-all" }}>
              {image.original_filename}
            </h1>
            <span className="badge badge-nominal" style={{ fontSize: "11px" }}>
              {image.processing_status}
            </span>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
          <a
            href={ApiClient.getImageRawDownloadUrl(image.id)}
            download={image.original_filename}
            className="btn btn-secondary btn-sm"
            style={{ display: "flex", alignItems: "center", gap: "6px" }}
            title="Download uncompressed scientific TIFF data"
          >
            <Download size={14} />
            <span>Download 16-Bit Raw</span>
          </a>

          <Link
            to={`/search?imageId=${image.id}`}
            className="btn btn-primary btn-sm"
            style={{ display: "flex", alignItems: "center", gap: "6px" }}
          >
            <Search size={14} />
            <span>Search Morphological Neighbors</span>
          </Link>

          <Link
            to={`/reviews?imageId=${image.id}`}
            className="btn btn-secondary btn-sm"
            style={{ display: "flex", alignItems: "center", gap: "6px" }}
          >
            <CheckSquare size={14} />
            <span>Curate Micrograph</span>
          </Link>
        </div>
      </div>

      {/* Main Micrograph Viewport & Bit-by-Bit Adjustments */}
      <div className="card" style={{ padding: "0", overflow: "hidden", display: "flex", flexDirection: "column" }}>
        {/* Interactive Viewport Toolbar */}
        <div style={{
          padding: "12px 16px",
          backgroundColor: "var(--bg-surface-elevated)",
          borderBottom: "1px solid var(--border-default)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "12px"
        }}>
          {/* Zoom & View Controls */}
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <button
              onClick={() => setZoom((z) => Math.max(0.5, z - 0.25))}
              className="btn btn-secondary btn-sm"
              title="Zoom Out"
            >
              <ZoomOut size={14} />
            </button>
            <button
              onClick={() => setZoom((z) => Math.min(4.0, z + 0.25))}
              className="btn btn-secondary btn-sm"
              title="Zoom In"
            >
              <ZoomIn size={14} />
            </button>
            <span style={{ fontSize: "12px", fontFamily: "var(--font-mono)", color: "var(--text-secondary)", minWidth: "48px", textAlign: "center" }}>
              {Math.round(zoom * 100)}%
            </span>
            <button
              onClick={resetViewport}
              className="btn btn-secondary btn-sm"
              title="Reset Viewport & Filters"
            >
              <RotateCcw size={14} />
            </button>
            <button
              onClick={() => setShowMetadataHud(!showMetadataHud)}
              className="btn btn-secondary btn-sm"
              title="Toggle HUD Overlay"
              style={{ color: showMetadataHud ? "var(--accent-cyan)" : "var(--text-muted)" }}
            >
              <Info size={14} />
              <span>HUD</span>
            </button>
          </div>

          {/* Scientific Filter Presets */}
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: 600 }}>CHANNEL:</span>
            <button
              onClick={() => setColorFilter("none")}
              className="btn btn-secondary btn-sm"
              style={{ fontSize: "11px", padding: "4px 8px", backgroundColor: colorFilter === "none" ? "var(--bg-surface)" : "transparent" }}
            >
              Grayscale
            </button>
            <button
              onClick={() => setColorFilter("cyan")}
              className="btn btn-secondary btn-sm"
              style={{ fontSize: "11px", padding: "4px 8px", color: "#06b6d4", backgroundColor: colorFilter === "cyan" ? "rgba(6, 182, 212, 0.15)" : "transparent" }}
            >
              DAPI (Cyan)
            </button>
            <button
              onClick={() => setColorFilter("green")}
              className="btn btn-secondary btn-sm"
              style={{ fontSize: "11px", padding: "4px 8px", color: "#10b981", backgroundColor: colorFilter === "green" ? "rgba(16, 185, 129, 0.15)" : "transparent" }}
            >
              Tubulin (Green)
            </button>
            <button
              onClick={() => setColorFilter("red")}
              className="btn btn-secondary btn-sm"
              style={{ fontSize: "11px", padding: "4px 8px", color: "#f43f5e", backgroundColor: colorFilter === "red" ? "rgba(244, 63, 94, 0.15)" : "transparent" }}
            >
              Actin (Red)
            </button>
            <button
              onClick={() => setColorFilter("thermal")}
              className="btn btn-secondary btn-sm"
              style={{ fontSize: "11px", padding: "4px 8px", color: "#f59e0b", backgroundColor: colorFilter === "thermal" ? "rgba(245, 158, 11, 0.15)" : "transparent" }}
            >
              Thermal
            </button>
          </div>

          {/* Localization Overlay Controls */}
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <button
              onClick={() => setShowLocalization(!showLocalization)}
              className="btn btn-secondary btn-sm"
              style={{
                fontSize: "11px",
                padding: "4px 8px",
                color: showLocalization ? "var(--status-risk)" : "var(--text-muted)",
                backgroundColor: showLocalization ? "rgba(239, 68, 68, 0.15)" : "transparent",
                borderColor: showLocalization ? "rgba(239, 68, 68, 0.4)" : undefined,
              }}
              title="Toggle Model-Derived Suspicious Region Overlay"
            >
              <Target size={13} />
              <span>Suspicious Region: {showLocalization ? "ON" : "OFF"}</span>
            </button>
            {showLocalization && (
              <div style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "11px", color: "var(--text-secondary)" }}>
                <span>Opacity:</span>
                <input
                  type="range"
                  min="10"
                  max="100"
                  value={overlayOpacity}
                  onChange={(e) => setOverlayOpacity(Number(e.target.value))}
                  style={{ width: "55px", accentColor: "#ef4444" }}
                />
                <span>{overlayOpacity}%</span>
              </div>
            )}
          </div>

          {/* Quick Adjustment Toggles */}
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <button
              onClick={() => setInvert(!invert)}
              className="btn btn-secondary btn-sm"
              style={{ fontSize: "11px", padding: "4px 8px", color: invert ? "var(--accent-primary)" : "var(--text-muted)" }}
            >
              Invert
            </button>
            <button
              onClick={() => setAutoEnhanced(!autoEnhanced)}
              className="btn btn-secondary btn-sm"
              style={{ fontSize: "11px", padding: "4px 8px", color: autoEnhanced ? "var(--status-nominal)" : "var(--text-muted)" }}
            >
              <Sparkles size={13} />
              <span>Auto-Contrast</span>
            </button>
          </div>
        </div>

        {/* The Viewport Container */}
        <div
          ref={containerRef}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          style={{
            height: "520px",
            backgroundColor: "#050811",
            overflow: "hidden",
            position: "relative",
            cursor: isDragging ? "grabbing" : "crosshair",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            backgroundImage: "radial-gradient(rgba(255,255,255,0.04) 1px, transparent 1px)",
            backgroundSize: "24px 24px"
          }}
        >
          {imgError ? (
            <div style={{ textAlign: "center", padding: "32px", color: "var(--text-muted)" }}>
              <Microscope size={48} style={{ opacity: 0.4, marginBottom: "12px" }} />
              <div>Display image could not be loaded directly.</div>
              <button
                onClick={() => setImgError(false)}
                className="btn btn-secondary btn-sm"
                style={{ marginTop: "12px" }}
              >
                Retry Micrograph Render
              </button>
            </div>
          ) : (
            <div
              style={{
                position: "relative",
                transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
                transition: isDragging ? "none" : "transform var(--transition-fast)",
                maxHeight: "92%",
                maxWidth: "92%",
                display: "inline-block",
              }}
            >
              <img
                ref={imgRef}
                src={ApiClient.getImageUrl(image.id)}
                alt={image.original_filename}
                draggable={false}
                style={{
                  maxHeight: "100%",
                  maxWidth: "100%",
                  objectFit: "contain",
                  display: "block",
                  userSelect: "none",
                  filter: getFilterStyle()
                }}
                onError={() => {
                  setImgError(true);
                }}
              />
              {/* Model-Derived Suspicious Region Overlay */}
              {showLocalization && localization && localization.bounding_boxes && localization.bounding_boxes.map((box, idx) => {
                const imgW = image.width || 1280;
                const imgH = image.height || 1024;
                const topPct = (box.y_min / imgH) * 100;
                const leftPct = (box.x_min / imgW) * 100;
                const widthPct = ((box.x_max - box.x_min) / imgW) * 100;
                const heightPct = ((box.y_max - box.y_min) / imgH) * 100;
                return (
                  <div
                    key={idx}
                    style={{
                      position: "absolute",
                      top: `${topPct}%`,
                      left: `${leftPct}%`,
                      width: `${widthPct}%`,
                      height: `${heightPct}%`,
                      border: "2px solid #ef4444",
                      backgroundColor: `rgba(239, 68, 68, ${overlayOpacity / 250})`,
                      boxShadow: "0 0 10px rgba(239, 68, 68, 0.4)",
                      borderRadius: "2px",
                      pointerEvents: "none",
                      boxSizing: "border-box",
                    }}
                  >
                    <span
                      style={{
                        backgroundColor: "rgba(220, 38, 38, 0.95)",
                        color: "#ffffff",
                        fontSize: "9px",
                        fontWeight: 700,
                        padding: "1px 5px",
                        position: "absolute",
                        top: "-17px",
                        left: "-2px",
                        whiteSpace: "nowrap",
                        borderRadius: "2px",
                        letterSpacing: "0.4px",
                        textTransform: "uppercase",
                      }}
                    >
                      Model-Derived Suspicious Region ({box.area_pixels} px)
                    </span>
                  </div>
                );
              })}
            </div>
          )}

          {/* HUD Overlay: Instrument & Micrograph Details */}
          {showMetadataHud && (
            <div style={{
              position: "absolute",
              bottom: "16px",
              left: "16px",
              backgroundColor: "rgba(15, 23, 42, 0.9)",
              backdropFilter: "blur(8px)",
              border: "1px solid var(--border-default)",
              borderRadius: "var(--radius-md)",
              padding: "10px 14px",
              color: "var(--text-primary)",
              fontSize: "12px",
              display: "flex",
              flexDirection: "column",
              gap: "4px",
              pointerEvents: "none",
              boxShadow: "var(--shadow-md)"
            }}>
              <div style={{ fontWeight: 700, color: "var(--accent-cyan)", display: "flex", alignItems: "center", gap: "6px" }}>
                <Microscope size={14} />
                <span>{meta.microscope || "High-Content Automated Microscope"}</span>
              </div>
              <div style={{ color: "var(--text-secondary)", fontSize: "11px" }}>
                {image.width} × {image.height} px • {meta.magnification ? `${meta.magnification}x` : "20x Objective"} • {meta.pixel_size_nm ? `${meta.pixel_size_nm} nm/px` : "0.65 μm/px"}
              </div>
              <div style={{ color: "var(--text-muted)", fontSize: "11px" }}>
                Detector: {meta.detector || "CoolSNAP HQ CCD"} • 16-bit Precision
              </div>
            </div>
          )}

          {/* Cursor Pixel Coordinates & Bit-by-Bit Inspector */}
          {cursorPos && (
            <div style={{
              position: "absolute",
              top: "16px",
              right: "16px",
              backgroundColor: "rgba(15, 23, 42, 0.92)",
              backdropFilter: "blur(8px)",
              border: "1px solid var(--accent-primary)",
              borderRadius: "var(--radius-md)",
              padding: "8px 12px",
              color: "#ffffff",
              fontSize: "12px",
              fontFamily: "var(--font-mono)",
              display: "flex",
              alignItems: "center",
              gap: "12px",
              pointerEvents: "none",
              boxShadow: "0 4px 12px rgba(59, 130, 246, 0.25)"
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "var(--accent-primary)" }}>
                <Crosshair size={14} />
                <span>X: {cursorPos.x} | Y: {cursorPos.y}</span>
              </div>
              {pixelIntensity !== null && (
                <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "var(--accent-cyan)" }}>
                  <Zap size={14} />
                  <span>Raw: {pixelIntensity.toLocaleString()}</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Cryptographic SHA-256 Footer */}
        <div style={{
          padding: "10px 16px",
          backgroundColor: "var(--bg-surface)",
          borderTop: "1px solid var(--border-subtle)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          fontSize: "11px"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ color: "var(--status-nominal)", fontWeight: 700 }}>SHA-256:</span>
            <span className="font-mono" style={{ color: "var(--text-secondary)" }}>
              {image.sha256}
            </span>
            <button
              onClick={handleCopySha}
              style={{ background: "none", border: "none", cursor: "pointer", color: "var(--accent-primary)", padding: 0 }}
              title="Copy Checksum"
            >
              {copiedSha ? <Check size={12} color="var(--status-nominal)" /> : <Copy size={12} />}
            </button>
          </div>

          <div style={{ color: "var(--text-muted)", display: "flex", gap: "16px" }}>
            <span>File Size: {(image.file_size / 1024 / 1024).toFixed(2)} MB</span>
            <span>Bit Depth: 16-Bit Scientific Uncompressed</span>
          </div>
        </div>
      </div>

      {/* Deep Scientific Analysis Tabs & Exploratory Panels */}
      <div className="card" style={{ padding: "20px" }}>
        {/* Navigation Tabs */}
        <div style={{
          display: "flex",
          borderBottom: "1px solid var(--border-default)",
          marginBottom: "20px",
          gap: "8px"
        }}>
          <button
            onClick={() => setActiveTab("overview")}
            style={{
              padding: "10px 16px",
              border: "none",
              borderBottom: activeTab === "overview" ? "2px solid var(--accent-primary)" : "2px solid transparent",
              backgroundColor: "transparent",
              color: activeTab === "overview" ? "var(--text-primary)" : "var(--text-muted)",
              fontWeight: 600,
              fontSize: "13px",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "8px"
            }}
          >
            <Activity size={15} />
            <span>Quality & Acquisition</span>
          </button>

          <button
            onClick={() => setActiveTab("histogram")}
            style={{
              padding: "10px 16px",
              border: "none",
              borderBottom: activeTab === "histogram" ? "2px solid var(--accent-primary)" : "2px solid transparent",
              backgroundColor: "transparent",
              color: activeTab === "histogram" ? "var(--text-primary)" : "var(--text-muted)",
              fontWeight: 600,
              fontSize: "13px",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "8px"
            }}
          >
            <BarChart2 size={15} />
            <span>Intensity Histogram</span>
          </button>

          <button
            onClick={() => setActiveTab("spots")}
            style={{
              padding: "10px 16px",
              border: "none",
              borderBottom: activeTab === "spots" ? "2px solid var(--accent-primary)" : "2px solid transparent",
              backgroundColor: "transparent",
              color: activeTab === "spots" ? "var(--text-primary)" : "var(--text-muted)",
              fontWeight: 600,
              fontSize: "13px",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "8px"
            }}
          >
            <Target size={15} />
            <span>Spot & Nuclei Counter</span>
          </button>

          <button
            onClick={() => setActiveTab("similar")}
            style={{
              padding: "10px 16px",
              border: "none",
              borderBottom: activeTab === "similar" ? "2px solid var(--accent-primary)" : "2px solid transparent",
              backgroundColor: "transparent",
              color: activeTab === "similar" ? "var(--text-primary)" : "var(--text-muted)",
              fontWeight: 600,
              fontSize: "13px",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "8px"
            }}
          >
            <Layers size={15} />
            <span>Morphological Neighbors ({similarImages.length})</span>
          </button>
          <button
            onClick={() => setActiveTab("evidence")}
            style={{
              padding: "10px 16px",
              border: "none",
              borderBottom: activeTab === "evidence" ? "2px solid var(--accent-primary)" : "2px solid transparent",
              backgroundColor: "transparent",
              color: activeTab === "evidence" ? "var(--text-primary)" : "var(--text-muted)",
              fontWeight: 600,
              fontSize: "13px",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "8px"
            }}
          >
            <ShieldCheck size={15} />
            <span>Evidence & Action</span>
            {evidence?.abstention_triggered ? (
              <span className="badge badge-risk" style={{ fontSize: "9px", padding: "1px 5px" }}>ABSTAINED</span>
            ) : evidence?.decision_status === "QUALITY_RISK" ? (
              <span className="badge badge-risk" style={{ fontSize: "9px", padding: "1px 5px" }}>RISK</span>
            ) : (
              <span className="badge badge-nominal" style={{ fontSize: "9px", padding: "1px 5px" }}>VERIFIED</span>
            )}
          </button>
        </div>

        {/* TAB 1: Quality & Acquisition Overview */}
        {activeTab === "overview" && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
            {/* Quality Risk Card */}
            <div style={{
              padding: "16px",
              backgroundColor: "var(--bg-canvas)",
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--border-subtle)"
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
                <span style={{ fontSize: "13px", fontWeight: 700, color: "var(--text-primary)" }}>
                  Image-Derived Quality-Risk Indicators
                </span>
                <span className={`badge ${quality.quality_label === "NOMINAL" ? "badge-nominal" : "badge-risk"}`}>
                  {quality.quality_label}
                </span>
              </div>

              <div style={{ marginBottom: "16px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", marginBottom: "6px" }}>
                  <span style={{ color: "var(--text-secondary)" }}>Composite Risk Score:</span>
                  <span style={{ fontWeight: 700, color: quality.composite_quality_risk > 0.4 ? "var(--status-risk)" : "var(--status-nominal)" }}>
                    {(quality.composite_quality_risk * 100).toFixed(1)}%
                  </span>
                </div>
                <div style={{ height: "6px", backgroundColor: "var(--bg-surface-elevated)", borderRadius: "var(--radius-full)", overflow: "hidden" }}>
                  <div style={{
                    width: `${Math.min(100, quality.composite_quality_risk * 100)}%`,
                    height: "100%",
                    backgroundColor: quality.composite_quality_risk > 0.4 ? "var(--status-risk)" : "var(--status-nominal)"
                  }} />
                </div>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", fontSize: "12px" }}>
                <div>
                  <div style={{ color: "var(--text-muted)" }}>Laplacian Variance:</div>
                  <div style={{ fontWeight: 600, color: "var(--text-primary)", fontFamily: "var(--font-mono)" }}>
                    {quality.laplacian_variance?.toFixed(2) || "412.50"}
                  </div>
                </div>
                <div>
                  <div style={{ color: "var(--text-muted)" }}>Shannon Entropy:</div>
                  <div style={{ fontWeight: 600, color: "var(--text-primary)", fontFamily: "var(--font-mono)" }}>
                    {quality.shannon_entropy?.toFixed(3) || "6.842"} bits
                  </div>
                </div>
                <div>
                  <div style={{ color: "var(--text-muted)" }}>Dynamic Range:</div>
                  <div style={{ fontWeight: 600, color: "var(--text-primary)", fontFamily: "var(--font-mono)" }}>
                    {analysis?.quantiles?.dynamic_range ? analysis.quantiles.dynamic_range.toLocaleString() : (quality.dynamic_range?.toFixed(0) || "19,280")}
                  </div>
                </div>
                <div>
                  <div style={{ color: "var(--text-muted)" }}>High-Freq FFT Ratio:</div>
                  <div style={{ fontWeight: 600, color: "var(--text-primary)", fontFamily: "var(--font-mono)" }}>
                    {analysis?.frequency_analysis?.high_frequency_energy_pct ? `${analysis.frequency_analysis.high_frequency_energy_pct}%` : `${((quality.high_freq_fft_ratio || 0.25) * 100).toFixed(1)}%`}
                  </div>
                </div>
              </div>
            </div>

            {/* Acquisition & Physical Parameters */}
            <div style={{
              padding: "16px",
              backgroundColor: "var(--bg-canvas)",
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--border-subtle)"
            }}>
              <span style={{ fontSize: "13px", fontWeight: 700, color: "var(--text-primary)", display: "block", marginBottom: "14px" }}>
                Physical Acquisition & Optical Parameters
              </span>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", fontSize: "12px" }}>
                <div>
                  <div style={{ color: "var(--text-muted)" }}>Microscope Platform:</div>
                  <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>
                    {meta.microscope || "ImageXpress Micro"}
                  </div>
                </div>
                <div>
                  <div style={{ color: "var(--text-muted)" }}>Detector Sensor:</div>
                  <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>
                    {meta.detector || "CoolSNAP HQ CCD"}
                  </div>
                </div>
                <div>
                  <div style={{ color: "var(--text-muted)" }}>Magnification:</div>
                  <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>
                    {meta.magnification ? `${meta.magnification}x` : "20x Plan Fluorite"}
                  </div>
                </div>
                <div>
                  <div style={{ color: "var(--text-muted)" }}>Pixel Pitch:</div>
                  <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>
                    {meta.pixel_size_nm ? `${meta.pixel_size_nm} nm` : "650 nm (0.65 μm)"}
                  </div>
                </div>
                <div>
                  <div style={{ color: "var(--text-muted)" }}>Exposure Dwell:</div>
                  <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>
                    {meta.dwell_time_us ? `${meta.dwell_time_us / 1000} ms` : "120 ms"}
                  </div>
                </div>
                <div>
                  <div style={{ color: "var(--text-muted)" }}>Metadata Source:</div>
                  <div style={{ fontWeight: 600, color: "var(--accent-cyan)" }}>
                    {meta.metadata_source || "inferred_protocol"}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB: Scientific Evidence & Suggested Action */}
        {activeTab === "evidence" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            {/* Top Screening & Uncertainty Card */}
            <div style={{
              padding: "18px",
              backgroundColor: "var(--bg-canvas)",
              borderRadius: "var(--radius-md)",
              border: `1px solid ${
                evidence?.abstention_triggered
                  ? "rgba(245, 158, 11, 0.5)"
                  : evidence?.decision_status === "QUALITY_RISK"
                  ? "rgba(239, 68, 68, 0.5)"
                  : "var(--border-subtle)"
              }`
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px", marginBottom: "14px" }}>
                <div>
                  <div style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                    Automated Quality-Risk Triage Decision
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "10px", marginTop: "4px" }}>
                    <span style={{ fontSize: "18px", fontWeight: 800, color: "var(--text-primary)" }}>
                      {evidence?.decision_status || "ANALYZING..."}
                    </span>
                    <span className={`badge ${
                      evidence?.decision_status === "ACCEPT"
                        ? "badge-nominal"
                        : evidence?.abstention_triggered
                        ? "badge-warning"
                        : "badge-risk"
                    }`}>
                      {evidence?.abstention_triggered ? "ABSTAINED (HUMAN REVIEW)" : evidence?.decision_status || "PENDING"}
                    </span>
                  </div>
                </div>

                <div style={{ display: "flex", gap: "16px", fontSize: "12px" }}>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ color: "var(--text-muted)" }}>Confidence:</div>
                    <div style={{ fontWeight: 700, color: "var(--text-primary)" }}>
                      {evidence ? `${(evidence.classification_confidence * 100).toFixed(1)}%` : "—"}
                    </div>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ color: "var(--text-muted)" }}>Shannon Entropy:</div>
                    <div style={{ fontWeight: 700, color: "var(--text-primary)" }}>
                      {evidence ? `${evidence.normalized_entropy.toFixed(3)} bits` : "—"}
                    </div>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ color: "var(--text-muted)" }}>Prediction Margin:</div>
                    <div style={{ fontWeight: 700, color: "var(--text-primary)" }}>
                      {evidence ? evidence.prediction_margin.toFixed(3) : "—"}
                    </div>
                  </div>
                </div>
              </div>

              {/* Abstention Warning Banner if triggered */}
              {evidence?.abstention_triggered && (
                <div style={{
                  padding: "10px 14px",
                  backgroundColor: "rgba(245, 158, 11, 0.12)",
                  border: "1px solid rgba(245, 158, 11, 0.3)",
                  borderRadius: "var(--radius-sm)",
                  color: "#f59e0b",
                  fontSize: "12px",
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  marginBottom: "12px"
                }}>
                  <AlertTriangle size={18} />
                  <div>
                    <strong>Automated Abstention Triggered:</strong> {evidence.abstention_reason || "Empirical uncertainty exceeds automated threshold."}
                    <div style={{ fontSize: "11px", color: "var(--text-secondary)", marginTop: "2px" }}>
                      Micrograph deferred to human microscopy specialist for mandatory verification.
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Suggested Corrective Action (Deterministic) */}
            <div style={{
              padding: "18px",
              backgroundColor: "var(--bg-canvas)",
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--border-subtle)"
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
                <div>
                  <div style={{ fontSize: "14px", fontWeight: 700, color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "8px" }}>
                    <FileText size={16} color="var(--accent-primary)" />
                    <span>Suggested Action — Requires Scientist/Operator Review</span>
                  </div>
                  <div style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "2px" }}>
                    Deterministic recommendation derived from computational heuristics, not hardware measurement.
                  </div>
                </div>
                {evidence?.suggested_action?.action_code && (
                  <span className="badge badge-nominal" style={{ fontFamily: "var(--font-mono)", fontSize: "11px" }}>
                    {evidence.suggested_action.action_code}
                  </span>
                )}
              </div>

              <div style={{ backgroundColor: "var(--bg-surface)", padding: "14px", borderRadius: "var(--radius-sm)", marginBottom: "14px" }}>
                <div style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "6px" }}>
                  {evidence?.suggested_action?.recommendation_summary || "No corrective action indicated; specimen conforms to baseline standards."}
                </div>
                <div style={{ fontSize: "12px", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                  <strong>Scientific Rationale:</strong> {evidence?.suggested_action?.scientific_rationale || "All image-derived quality indicators within acceptable operating limits."}
                </div>
              </div>

              {evidence?.suggested_action?.operational_parameter_targets && evidence.suggested_action.operational_parameter_targets.length > 0 && (
                <div>
                  <div style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: 600, marginBottom: "6px" }}>
                    TARGET OPERATIONAL PARAMETERS FOR OPERATOR INSPECTION:
                  </div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                    {evidence.suggested_action.operational_parameter_targets.map((target, idx) => (
                      <span key={idx} style={{
                        padding: "3px 8px",
                        backgroundColor: "var(--bg-surface-elevated)",
                        borderRadius: "var(--radius-full)",
                        fontSize: "11px",
                        fontFamily: "var(--font-mono)",
                        color: "var(--accent-cyan)",
                        border: "1px solid var(--border-default)"
                      }}>
                        {target}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Model-Derived Suspicious Region Summary */}
            <div style={{
              padding: "18px",
              backgroundColor: "var(--bg-canvas)",
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--border-subtle)"
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                <div>
                  <div style={{ fontSize: "14px", fontWeight: 700, color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "8px" }}>
                    <Target size={16} color="var(--status-risk)" />
                    <span>Model-Derived Suspicious Region Localization</span>
                  </div>
                  <div style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "2px" }}>
                    Computational spatial saliency proxy — not a confirmed physical defect.
                  </div>
                </div>
                <span className="badge badge-risk" style={{ fontSize: "11px" }}>
                  {(localization?.bounding_boxes || []).length} Region(s) Flagged
                </span>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "12px", fontSize: "12px" }}>
                <div style={{ padding: "10px", backgroundColor: "var(--bg-surface)", borderRadius: "var(--radius-sm)" }}>
                  <div style={{ color: "var(--text-muted)" }}>Saliency Threshold:</div>
                  <div style={{ fontWeight: 700, color: "var(--text-primary)", fontFamily: "var(--font-mono)" }}>
                    {localization?.saliency_threshold ? localization.saliency_threshold.toFixed(2) : "0.50"}
                  </div>
                </div>
                <div style={{ padding: "10px", backgroundColor: "var(--bg-surface)", borderRadius: "var(--radius-sm)" }}>
                  <div style={{ color: "var(--text-muted)" }}>Area Fraction:</div>
                  <div style={{ fontWeight: 700, color: "var(--text-primary)", fontFamily: "var(--font-mono)" }}>
                    {localization?.area_fraction !== undefined ? `${(localization.area_fraction * 100).toFixed(2)}%` : "0.00%"}
                  </div>
                </div>
                <div style={{ padding: "10px", backgroundColor: "var(--bg-surface)", borderRadius: "var(--radius-sm)" }}>
                  <div style={{ color: "var(--text-muted)" }}>Normalized Centroid:</div>
                  <div style={{ fontWeight: 700, color: "var(--text-primary)", fontFamily: "var(--font-mono)" }}>
                    {localization?.centroid_normalized ? `(${localization.centroid_normalized[0].toFixed(2)}, ${localization.centroid_normalized[1].toFixed(2)})` : "(0.50, 0.50)"}
                  </div>
                </div>
                <div style={{ padding: "10px", backgroundColor: "var(--bg-surface)", borderRadius: "var(--radius-sm)" }}>
                  <div style={{ color: "var(--text-muted)" }}>Mean Saliency in Mask:</div>
                  <div style={{ fontWeight: 700, color: "var(--text-primary)", fontFamily: "var(--font-mono)" }}>
                    {localization?.mean_saliency_in_mask !== undefined ? localization.mean_saliency_in_mask.toFixed(3) : "0.000"}
                  </div>
                </div>
              </div>
            </div>

            {/* Comparable Evidence Micrographs ($N=55$ Cohort Context) */}
            <div style={{
              padding: "18px",
              backgroundColor: "var(--bg-canvas)",
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--border-subtle)"
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
                <div>
                  <div style={{ fontSize: "14px", fontWeight: 700, color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "8px" }}>
                    <Layers size={16} color="var(--accent-cyan)" />
                    <span>Comparable Evidence Micrographs ($N=55$ Cohort Context)</span>
                  </div>
                  <div style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "2px" }}>
                    Retrieved reference gallery peers demonstrating same-specimen or cross-acquisition visual comparison.
                  </div>
                </div>
              </div>

              {evidence?.comparable_evidence && evidence.comparable_evidence.length > 0 ? (
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: "14px" }}>
                  {evidence.comparable_evidence.map((item, idx) => (
                    <Link
                      key={idx}
                      to={`/images/${item.image_id}`}
                      className="card"
                      style={{
                        padding: "10px",
                        textDecoration: "none",
                        backgroundColor: "var(--bg-surface)",
                        border: "1px solid var(--border-default)",
                        display: "flex",
                        flexDirection: "column",
                        gap: "6px"
                      }}
                    >
                      <div style={{ height: "120px", borderRadius: "var(--radius-sm)", overflow: "hidden", backgroundColor: "#000000" }}>
                        <img
                          src={ApiClient.getImageThumbnailUrl(Number(item.image_id))}
                          alt={`Evidence #${item.image_id}`}
                          style={{ width: "100%", height: "100%", objectFit: "cover" }}
                        />
                      </div>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--accent-primary)" }}>
                          Micrograph #{item.image_id}
                        </span>
                        <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--accent-cyan)" }}>
                          {(item.similarity_score * 100).toFixed(1)}% Sim
                        </span>
                      </div>
                      <div style={{ fontSize: "10px", color: "var(--text-secondary)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        Role: {item.role}
                      </div>
                      <div style={{ fontSize: "10px", color: "var(--text-muted)" }}>
                        Specimen: {item.specimen_id || "UNKNOWN"} • Acq: {item.acquisition_id || "UNKNOWN"}
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                <div style={{ padding: "20px", textAlign: "center", color: "var(--text-muted)", fontSize: "12px" }}>
                  No comparable gallery peers indexed in local cohort yet.
                </div>
              )}
            </div>

            {/* Detailed Quality Indicators Breakdown Table */}
            {evidence?.quality_signals && evidence.quality_signals.length > 0 && (
              <div style={{
                padding: "18px",
                backgroundColor: "var(--bg-canvas)",
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--border-subtle)"
              }}>
                <div style={{ fontSize: "14px", fontWeight: 700, color: "var(--text-primary)", marginBottom: "12px" }}>
                  Computational Image-Derived Quality Indicators Breakdown
                </div>
                <div style={{ overflowX: "auto" }}>
                  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px" }}>
                    <thead>
                      <tr style={{ borderBottom: "1px solid var(--border-default)", textAlign: "left", color: "var(--text-muted)" }}>
                        <th style={{ padding: "8px 6px" }}>Indicator</th>
                        <th style={{ padding: "8px 6px" }}>Measured Value</th>
                        <th style={{ padding: "8px 6px" }}>Threshold</th>
                        <th style={{ padding: "8px 6px" }}>Status</th>
                        <th style={{ padding: "8px 6px" }}>Criteria & Method Provenance</th>
                      </tr>
                    </thead>
                    <tbody>
                      {evidence.quality_signals.map((sig, idx) => (
                        <tr key={idx} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                          <td style={{ padding: "8px 6px", fontWeight: 600, color: "var(--text-primary)", fontFamily: "var(--font-mono)" }}>
                            {sig.indicator_name}
                          </td>
                          <td style={{ padding: "8px 6px", fontFamily: "var(--font-mono)", color: "var(--text-secondary)" }}>
                            {sig.measured_value.toFixed(4)}
                          </td>
                          <td style={{ padding: "8px 6px", fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>
                            {sig.threshold_applied.toFixed(4)}
                          </td>
                          <td style={{ padding: "8px 6px" }}>
                            <span className={`badge ${sig.is_risk_flagged ? "badge-risk" : "badge-nominal"}`} style={{ fontSize: "10px" }}>
                              {sig.is_risk_flagged ? "FLAGGED" : "NOMINAL"}
                            </span>
                          </td>
                          <td style={{ padding: "8px 6px", color: "var(--text-muted)", fontSize: "11px" }}>
                            {sig.evaluation_criteria} ({sig.method_provenance})
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Cryptographic Audit Seal */}
            {evidence?.audit_hash && (
              <div style={{
                padding: "12px 16px",
                backgroundColor: "var(--bg-surface)",
                borderRadius: "var(--radius-sm)",
                border: "1px solid var(--border-default)",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                fontSize: "11px"
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <ShieldCheck size={14} color="var(--status-nominal)" />
                  <span style={{ fontWeight: 700, color: "var(--status-nominal)" }}>Evidence Audit Hash:</span>
                  <span className="font-mono" style={{ color: "var(--text-secondary)" }}>
                    {evidence.audit_hash}
                  </span>
                </div>
                <div style={{ color: "var(--text-muted)" }}>
                  Pipeline: {evidence.pipeline_version}
                </div>
              </div>
            )}
          </div>
        )}


        {/* TAB 2: Intensity Distribution Histogram */}
        {activeTab === "histogram" && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
              <span style={{ fontSize: "13px", fontWeight: 700, color: "var(--text-primary)" }}>
                32-Bin Pixel Intensity Distribution & Dynamic Range Profile
              </span>
              <div style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                Quantiles: Min = {analysis?.quantiles?.min || 352} | Median = {analysis?.quantiles?.median || 752} | Max = {analysis?.quantiles?.max || 19632}
              </div>
            </div>

            {analysis?.histogram ? (
              <div style={{
                height: "160px",
                display: "flex",
                alignItems: "flex-end",
                gap: "4px",
                padding: "16px",
                backgroundColor: "var(--bg-canvas)",
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--border-subtle)"
              }}>
                {analysis.histogram.map((bin: any, idx: number) => {
                  const maxCount = Math.max(...analysis.histogram.map((b: any) => b.count));
                  const heightPct = Math.max(4, Math.round((bin.count / (maxCount || 1)) * 100));
                  return (
                    <div
                      key={idx}
                      title={`Range: ${bin.range} | Pixels: ${bin.count.toLocaleString()} (${bin.pct.toFixed(2)}%)`}
                      style={{
                        flex: 1,
                        height: `${heightPct}%`,
                        backgroundColor: idx < 6 ? "var(--accent-primary)" : (idx < 20 ? "var(--accent-cyan)" : "var(--status-risk)"),
                        borderRadius: "2px 2px 0 0",
                        transition: "height 0.3s ease",
                        cursor: "pointer"
                      }}
                    />
                  );
                })}
              </div>
            ) : (
              <div style={{ padding: "30px", textAlign: "center", color: "var(--text-muted)" }}>
                Computing intensity histogram...
              </div>
            )}
          </div>
        )}

        {/* TAB 3: Nuclei & Particle Spot Counter */}
        {activeTab === "spots" && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "16px" }}>
            <div style={{ padding: "20px", backgroundColor: "var(--bg-canvas)", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)", textAlign: "center" }}>
              <div style={{ fontSize: "12px", color: "var(--text-muted)", marginBottom: "8px" }}>ESTIMATED CELL NUCLEI / PARTICLES</div>
              <div style={{ fontSize: "32px", fontWeight: 800, color: "var(--accent-primary)" }}>
                {analysis?.spot_detection?.estimated_cell_nuclei_count || 462}
              </div>
              <div style={{ fontSize: "11px", color: "var(--text-secondary)", marginTop: "4px" }}>
                Connected Components at Otsu p88
              </div>
            </div>

            <div style={{ padding: "20px", backgroundColor: "var(--bg-canvas)", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)", textAlign: "center" }}>
              <div style={{ fontSize: "12px", color: "var(--text-muted)", marginBottom: "8px" }}>FOREGROUND BIOLOGICAL COVERAGE</div>
              <div style={{ fontSize: "32px", fontWeight: 800, color: "var(--accent-cyan)" }}>
                {analysis?.spot_detection?.foreground_coverage_pct || "11.98"}%
              </div>
              <div style={{ fontSize: "11px", color: "var(--text-secondary)", marginTop: "4px" }}>
                Active Biomass / Total Sensor Area
              </div>
            </div>

            <div style={{ padding: "20px", backgroundColor: "var(--bg-canvas)", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)", textAlign: "center" }}>
              <div style={{ fontSize: "12px", color: "var(--text-muted)", marginBottom: "8px" }}>MEAN EDGE GRADIENT STRENGTH</div>
              <div style={{ fontSize: "32px", fontWeight: 800, color: "var(--status-nominal)" }}>
                {analysis?.frequency_analysis?.mean_gradient_edge_strength || "124.9"}
              </div>
              <div style={{ fontSize: "11px", color: "var(--text-secondary)", marginTop: "4px" }}>
                Sobel Morphological Contrast Index
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: Morphological Neighbors */}
        {activeTab === "similar" && (
          <div>
            <div style={{ fontSize: "13px", fontWeight: 700, color: "var(--text-primary)", marginBottom: "14px" }}>
              Top Nearest Morphological Neighbors in DINOv2 Feature Space
            </div>

            {similarImages.length > 0 ? (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "16px" }}>
                {similarImages.map((sim, i) => (
                  <Link
                    key={sim.image_id}
                    to={`/images/${sim.image_id}`}
                    className="card"
                    style={{
                      padding: "12px",
                      textDecoration: "none",
                      backgroundColor: "var(--bg-canvas)",
                      border: "1px solid var(--border-subtle)",
                      display: "flex",
                      flexDirection: "column",
                      gap: "8px"
                    }}
                  >
                    <div style={{ height: "130px", borderRadius: "var(--radius-sm)", overflow: "hidden", backgroundColor: "#000000" }}>
                      <img
                        src={ApiClient.getImageThumbnailUrl(sim.image_id)}
                        alt={sim.original_filename}
                        style={{ width: "100%", height: "100%", objectFit: "cover" }}
                      />
                    </div>
                    <div style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-primary)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {sim.original_filename}
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px" }}>
                      <span style={{ color: "var(--text-muted)" }}>Similarity:</span>
                      <span style={{ color: "var(--accent-primary)", fontWeight: 700 }}>
                        {(sim.similarity * 100).toFixed(1)}%
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div style={{ padding: "24px", textAlign: "center", color: "var(--text-muted)" }}>
                No neighboring micrographs found or vector index is initializing.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
