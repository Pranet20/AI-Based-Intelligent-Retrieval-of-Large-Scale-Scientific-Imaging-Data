import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  UploadCloud,
  FileCheck,
  AlertTriangle,
  Microscope,
  Cpu,
  Layers,
  CheckCircle2,
  ShieldCheck,
  Sparkles,
  ArrowRight,
  Database,
  Eye,
  Sliders,
  Activity,
  FileSpreadsheet
} from "lucide-react";
import { Project } from "../types";
import { ApiClient, ImageDetailResponse } from "../api/client";

interface SampleItem {
  filename: string;
  channel: string;
  size_bytes: number;
  size_mb: number;
}

export const Upload: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"file" | "samples">("file");
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<number | "">("");
  const [file, setFile] = useState<File | null>(null);
  const [filePreview, setFilePreview] = useState<string | null>(null);

  // Available Samples from dataset
  const [samples, setSamples] = useState<SampleItem[]>([]);
  const [loadingSamples, setLoadingSamples] = useState(false);

  // Scientific Metadata Fields
  const [microscope, setMicroscope] = useState("Widefield Fluorescence (IXM)");
  const [detector, setDetector] = useState("sCMOS High-QE");
  const [acceleratingVoltage, setAcceleratingVoltage] = useState("0.0");
  const [magnification, setMagnification] = useState("200");
  const [pixelSizeNm, setPixelSizeNm] = useState("325.0");

  const [uploading, setUploading] = useState(false);
  const [pipelineStep, setPipelineStep] = useState<string>("");
  const [result, setResult] = useState<(ImageDetailResponse & { message?: string }) | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    ApiClient.getProjects()
      .then((data) => {
        setProjects(data);
        if (data.length > 0) setSelectedProject(data[0].id);
      })
      .catch((e) => console.error(e));

    loadSamples();
  }, []);

  const loadSamples = async () => {
    setLoadingSamples(true);
    try {
      const res = await ApiClient.getAvailableSamples();
      if (res && res.samples) {
        setSamples(res.samples);
      }
    } catch (e) {
      console.warn("Could not load samples:", e);
    } finally {
      setLoadingSamples(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      setError(null);
      if (selected.type.startsWith("image/") && !selected.name.toLowerCase().endsWith(".tif") && !selected.name.toLowerCase().endsWith(".tiff")) {
        const url = URL.createObjectURL(selected);
        setFilePreview(url);
      } else {
        setFilePreview(null);
      }
    }
  };

  const applyPreset = (presetType: "bbbc021" | "sem" | "tem") => {
    if (presetType === "bbbc021") {
      setMicroscope("Widefield Fluorescence (IXM)");
      setDetector("sCMOS High-QE");
      setAcceleratingVoltage("0.0");
      setMagnification("200");
      setPixelSizeNm("325.0");
    } else if (presetType === "sem") {
      setMicroscope("FEI Helios NanoLab 600 SEM");
      setDetector("SE / In-Lens");
      setAcceleratingVoltage("15.0");
      setMagnification("5000");
      setPixelSizeNm("10.5");
    } else if (presetType === "tem") {
      setMicroscope("ThermoFisher Titan Cryo-TEM");
      setDetector("Gatan K3 Direct Detector");
      setAcceleratingVoltage("300.0");
      setMagnification("65000");
      setPixelSizeNm("0.85");
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a valid micrograph image file.");
      return;
    }

    setUploading(true);
    setPipelineStep("Validating file integrity & SHA-256...");
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);
    if (selectedProject) formData.append("project_id", selectedProject.toString());
    if (microscope) formData.append("microscope", microscope);
    if (detector) formData.append("detector", detector);
    if (acceleratingVoltage) formData.append("accelerating_voltage_kv", acceleratingVoltage);
    if (magnification) formData.append("magnification", magnification);
    if (pixelSizeNm) formData.append("pixel_size_nm", pixelSizeNm);

    const stepTimer = setTimeout(() => {
      setPipelineStep("16-Bit Dynamic Range Contrast Stretching & Quality Profiling...");
    }, 1200);

    const stepTimer2 = setTimeout(() => {
      setPipelineStep("Extracting DINOv2 ViT-S/14 384-D Vector & FAISS Indexing...");
    }, 2800);

    try {
      const res = await ApiClient.uploadImage(formData);
      setResult(res as any);
    } catch (err: any) {
      setError(err.message || "Micrograph ingestion pipeline failure.");
    } finally {
      clearTimeout(stepTimer);
      clearTimeout(stepTimer2);
      setUploading(false);
      setPipelineStep("");
    }
  };

  const handleIngestSample = async (sampleFilename: string) => {
    setUploading(true);
    setPipelineStep(`Ingesting sample '${sampleFilename}' via automated pipeline...`);
    setError(null);
    setResult(null);

    try {
      const res = await ApiClient.ingestSample(sampleFilename, selectedProject ? Number(selectedProject) : undefined);
      setResult(res);
    } catch (err: any) {
      setError(err.message || "Sample micrograph ingestion failure.");
    } finally {
      setUploading(false);
      setPipelineStep("");
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px", maxWidth: "980px" }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: "22px", fontWeight: "700", color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "10px" }}>
          <UploadCloud size={22} color="var(--accent-primary)" />
          <span>Scientific Micrograph Ingestion Pipeline</span>
        </h1>
        <p style={{ fontSize: "14px", color: "var(--text-secondary)", marginTop: "4px" }}>
          Automated 14-step ingestion pipeline: 16-bit TIFF percentile contrast-stretching, SHA-256 fingerprinting,
          6-indicator quality risk assessment, 6-stage redundancy cascade, DINOv2 ViT-S/14 384-D neural embedding, and FAISS indexing.
        </p>
      </div>

      {/* Mode Navigation Tabs */}
      <div style={{ display: "flex", gap: "8px", borderBottom: "1px solid var(--border-default)", paddingBottom: "8px" }}>
        <button
          onClick={() => setActiveTab("file")}
          className={`btn ${activeTab === "file" ? "btn-primary" : "btn-secondary"} btn-sm`}
          style={{ display: "flex", alignItems: "center", gap: "6px" }}
        >
          <UploadCloud size={15} />
          <span>Upload File from Computer</span>
        </button>
        <button
          onClick={() => setActiveTab("samples")}
          className={`btn ${activeTab === "samples" ? "btn-primary" : "btn-secondary"} btn-sm`}
          style={{ display: "flex", alignItems: "center", gap: "6px" }}
        >
          <Database size={15} />
          <span>BBBC021 Benchmark Sample Datasets ({samples.length})</span>
        </button>
      </div>

      {/* Main Content Body */}
      {activeTab === "file" ? (
        <div className="card">
          <form onSubmit={handleUpload} style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            {/* File Picker Zone */}
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                <label style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)" }}>
                  Micrograph Image File (.tif, .tiff, .png, .jpg, .jpeg) *
                </label>
                <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>Supports 16-bit uncompressed scientific TIFFs</span>
              </div>
              <div style={{
                border: file ? "2px solid var(--accent-primary)" : "2px dashed var(--border-default)",
                borderRadius: "var(--radius-md)",
                padding: "24px",
                textAlign: "center",
                backgroundColor: "var(--bg-canvas)",
                transition: "all var(--transition-fast)"
              }}>
                <input
                  type="file"
                  id="file-input"
                  accept=".png,.tif,.tiff,.jpg,.jpeg"
                  onChange={handleFileChange}
                  style={{ display: "none" }}
                />
                <label htmlFor="file-input" style={{ cursor: "pointer", display: "flex", flexDirection: "column", alignItems: "center", gap: "10px" }}>
                  {filePreview ? (
                    <img
                      src={filePreview}
                      alt="Local Preview"
                      style={{ maxHeight: "140px", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-default)" }}
                    />
                  ) : (
                    <UploadCloud size={36} color="var(--accent-primary)" />
                  )}
                  <div style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)" }}>
                    {file ? file.name : "Drag & Drop or Click to Select Micrograph File"}
                  </div>
                  <div style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                    {file
                      ? `${(file.size / (1024 * 1024)).toFixed(2)} MB • ${file.name.toLowerCase().endsWith(".tif") || file.name.toLowerCase().endsWith(".tiff") ? "16-Bit Scientific TIFF (Will be contrast-stretched)" : file.type || "Image"}`
                      : "Supported formats: 16-bit/8-bit TIFF, PNG, JPEG up to 50 MB"}
                  </div>
                </label>
              </div>
            </div>

            {/* Quick Metadata Presets */}
            <div style={{ display: "flex", alignItems: "center", gap: "10px", padding: "10px 14px", backgroundColor: "var(--bg-canvas)", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-default)" }}>
              <Sparkles size={16} color="var(--accent-primary)" />
              <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)" }}>Quick Instrument Presets:</span>
              <div style={{ display: "flex", gap: "8px" }}>
                <button type="button" onClick={() => applyPreset("bbbc021")} className="btn btn-secondary btn-sm" style={{ fontSize: "11px", padding: "3px 8px" }}>
                  Fluorescence (BBBC021)
                </button>
                <button type="button" onClick={() => applyPreset("sem")} className="btn btn-secondary btn-sm" style={{ fontSize: "11px", padding: "3px 8px" }}>
                  FEI SEM (15 kV)
                </button>
                <button type="button" onClick={() => applyPreset("tem")} className="btn btn-secondary btn-sm" style={{ fontSize: "11px", padding: "3px 8px" }}>
                  Cryo-TEM (300 kV)
                </button>
              </div>
            </div>

            {/* Project & Acquisition Parameters */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "6px" }}>
                  Target Scientific Project / Dataset
                </label>
                <select
                  value={selectedProject}
                  onChange={(e) => setSelectedProject(e.target.value ? Number(e.target.value) : "")}
                  className="input-field"
                >
                  <option value="">No Project Assigned (Default Pool)</option>
                  {projects.map((p) => (
                    <option key={p.id} value={p.id}>{p.name} (#{p.id})</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "6px" }}>
                  Microscope Instrument
                </label>
                <input
                  type="text"
                  value={microscope}
                  onChange={(e) => setMicroscope(e.target.value)}
                  placeholder="e.g. Widefield Fluorescence (IXM)"
                  className="input-field"
                />
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: "14px" }}>
              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "6px" }}>
                  Detector
                </label>
                <input
                  type="text"
                  value={detector}
                  onChange={(e) => setDetector(e.target.value)}
                  placeholder="e.g. sCMOS High-QE"
                  className="input-field"
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "6px" }}>
                  Voltage (kV)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={acceleratingVoltage}
                  onChange={(e) => setAcceleratingVoltage(e.target.value)}
                  placeholder="0.0"
                  className="input-field"
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "6px" }}>
                  Magnification (x)
                </label>
                <input
                  type="number"
                  value={magnification}
                  onChange={(e) => setMagnification(e.target.value)}
                  placeholder="200"
                  className="input-field"
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "6px" }}>
                  Pixel Size (nm)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={pixelSizeNm}
                  onChange={(e) => setPixelSizeNm(e.target.value)}
                  placeholder="325.0"
                  className="input-field"
                />
              </div>
            </div>

            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: "6px" }}>
              <button
                type="submit"
                disabled={uploading || !file}
                className="btn btn-primary"
                style={{ height: "42px", padding: "0 22px" }}
              >
                {uploading ? (
                  <>
                    <Cpu size={16} className="animate-spin" />
                    <span>Executing Pipeline...</span>
                  </>
                ) : (
                  <>
                    <UploadCloud size={16} />
                    <span>Ingest & Index Micrograph</span>
                  </>
                )}
              </button>

              {uploading && (
                <div style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "13px", color: "var(--accent-primary)" }}>
                  <Activity size={16} className="animate-pulse" />
                  <span>{pipelineStep}</span>
                </div>
              )}
            </div>
          </form>
        </div>
      ) : (
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <div>
              <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)" }}>
                BBBC021 Benchmark Dataset Micrographs
              </h3>
              <p style={{ fontSize: "13px", color: "var(--text-secondary)" }}>
                Select a real multi-channel scientific micrograph from the local BBBC021 repository to ingest through the 14-stage pipeline.
              </p>
            </div>
            <button onClick={loadSamples} disabled={loadingSamples} className="btn btn-secondary btn-sm">
              Refresh Disk Samples
            </button>
          </div>

          {loadingSamples ? (
            <div style={{ padding: "40px", textAlign: "center", color: "var(--text-muted)" }}>
              <Cpu size={24} className="animate-spin" style={{ margin: "0 auto 8px" }} />
              <div>Scanning BBBC021 dataset repository...</div>
            </div>
          ) : samples.length === 0 ? (
            <div style={{ padding: "30px", textAlign: "center", color: "var(--text-muted)", backgroundColor: "var(--bg-canvas)", borderRadius: "var(--radius-sm)" }}>
              No raw TIFF files found in the dataset directory. You can use the "Upload File from Computer" tab to upload micrographs.
            </div>
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "10px" }}>
              {samples.slice(0, 10).map((sample, idx) => (
                <div
                  key={sample.filename}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "12px 16px",
                    backgroundColor: "var(--bg-canvas)",
                    borderRadius: "var(--radius-sm)",
                    border: "1px solid var(--border-default)",
                    transition: "border-color var(--transition-fast)"
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                    <div style={{
                      width: "36px",
                      height: "36px",
                      borderRadius: "var(--radius-sm)",
                      backgroundColor: sample.channel.includes("DAPI") ? "rgba(59, 130, 246, 0.15)" : sample.channel.includes("Tubulin") ? "rgba(16, 185, 129, 0.15)" : "rgba(245, 158, 11, 0.15)",
                      color: sample.channel.includes("DAPI") ? "#3b82f6" : sample.channel.includes("Tubulin") ? "#10b981" : "#f59e0b",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontWeight: 700,
                      fontSize: "12px"
                    }}>
                      #{idx + 1}
                    </div>
                    <div>
                      <div style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)", wordBreak: "break-all" }}>
                        {sample.filename}
                      </div>
                      <div style={{ fontSize: "11px", color: "var(--text-secondary)", display: "flex", gap: "12px", marginTop: "2px" }}>
                        <span><strong>Channel:</strong> {sample.channel}</span>
                        <span><strong>Size:</strong> {sample.size_mb} MB (16-bit)</span>
                        <span><strong>Format:</strong> Uncompressed TIFF</span>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => handleIngestSample(sample.filename)}
                    disabled={uploading}
                    className="btn btn-secondary btn-sm"
                    style={{ flexShrink: 0, display: "flex", alignItems: "center", gap: "6px" }}
                  >
                    <UploadCloud size={14} />
                    <span>Ingest Sample</span>
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Ingestion Error Alert */}
      {error && (
        <div className="card" style={{ borderLeft: "4px solid var(--status-risk)", color: "var(--status-risk)" }}>
          <div style={{ fontWeight: 600, display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
            <AlertTriangle size={18} />
            <span>Ingestion Pipeline Error</span>
          </div>
          <div style={{ fontSize: "13px" }}>{error}</div>
        </div>
      )}

      {/* Comprehensive Ingestion Results & Inspection Gateway */}
      {result && (
        <div className="card" style={{ borderLeft: "4px solid var(--status-nominal)", padding: "20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "var(--status-nominal)", fontWeight: 700, fontSize: "16px" }}>
                <CheckCircle2 size={20} />
                <span>Micrograph Ingestion & Indexing Succeeded</span>
              </div>
              <div style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "2px" }}>
                Assigned Database Catalog ID: <strong>#{result.id}</strong> &bull; Status: <span className="badge badge-nominal">{result.processing_status}</span>
              </div>
            </div>

            <div style={{ display: "flex", gap: "8px" }}>
              <button
                onClick={() => navigate(`/images/${result.id}`)}
                className="btn btn-primary btn-sm"
                style={{ display: "flex", alignItems: "center", gap: "6px", backgroundColor: "var(--accent-primary)" }}
              >
                <Eye size={15} />
                <span>Inspect Micrograph Bit-by-Bit</span>
                <ArrowRight size={14} />
              </button>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "180px 1fr", gap: "20px", alignItems: "start" }}>
            {/* Visual Micrograph Display Preview */}
            <div style={{ textAlign: "center" }}>
              <div style={{
                position: "relative",
                width: "180px",
                height: "180px",
                borderRadius: "var(--radius-md)",
                overflow: "hidden",
                border: "1px solid var(--border-default)",
                backgroundColor: "#05070a",
                cursor: "pointer"
              }}
              onClick={() => navigate(`/images/${result.id}`)}
              title="Click to open Deep Interactive Micrograph Viewport"
              >
                <img
                  src={ApiClient.getImageDisplayUrl(result.id)}
                  alt={result.original_filename}
                  style={{ width: "100%", height: "100%", objectFit: "cover" }}
                  onError={(e: any) => {
                    e.currentTarget.src = ApiClient.getImageThumbnailUrl(result.id);
                  }}
                />
                <div style={{
                  position: "absolute",
                  bottom: "6px",
                  right: "6px",
                  backgroundColor: "rgba(0,0,0,0.75)",
                  color: "#fff",
                  fontSize: "10px",
                  padding: "2px 6px",
                  borderRadius: "4px",
                  display: "flex",
                  alignItems: "center",
                  gap: "4px"
                }}>
                  <Eye size={10} />
                  <span>Inspect</span>
                </div>
              </div>
              <div style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "6px" }}>
                {result.width} × {result.height} px
              </div>
            </div>

            {/* Core Identification & Quality Summary */}
            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              <div style={{ fontSize: "13px", color: "var(--text-primary)", display: "flex", flexDirection: "column", gap: "4px" }}>
                <div><strong>Filename:</strong> <span className="font-mono">{result.original_filename}</span></div>
                <div><strong>SHA-256:</strong> <span className="font-mono" style={{ fontSize: "11px", color: "var(--text-muted)" }}>{result.sha256}</span></div>
                <div><strong>Redundancy Cascade:</strong> <span className="badge badge-info">{result.duplicate?.duplicate_status || "NO_DECLARED_REDUNDANCY_DETECTED"}</span></div>
              </div>

              {/* 6-Indicator Quality Risk Dashboard */}
              {result.quality && (
                <div style={{
                  backgroundColor: "var(--bg-canvas)",
                  padding: "12px",
                  borderRadius: "var(--radius-sm)",
                  border: "1px solid var(--border-default)"
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                    <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "6px" }}>
                      <Activity size={14} color="var(--accent-primary)" />
                      <span>Image-Derived Quality-Risk Indicators</span>
                    </span>
                    <span className={`badge ${result.quality.quality_label === "NOMINAL" ? "badge-nominal" : "badge-warning"}`}>
                      {result.quality.quality_label} (Risk: {(result.quality.composite_quality_risk * 100).toFixed(1)}%)
                    </span>
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "8px", fontSize: "12px" }}>
                    <div style={{ padding: "6px 8px", backgroundColor: "var(--bg-surface)", borderRadius: "var(--radius-sm)" }}>
                      <div style={{ color: "var(--text-muted)", fontSize: "10px" }}>Shannon Entropy</div>
                      <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>{result.quality.shannon_entropy?.toFixed(3) || "N/A"} bits</div>
                    </div>
                    <div style={{ padding: "6px 8px", backgroundColor: "var(--bg-surface)", borderRadius: "var(--radius-sm)" }}>
                      <div style={{ color: "var(--text-muted)", fontSize: "10px" }}>Laplacian Focus</div>
                      <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>{result.quality.laplacian_variance?.toFixed(2) || "N/A"}</div>
                    </div>
                    <div style={{ padding: "6px 8px", backgroundColor: "var(--bg-surface)", borderRadius: "var(--radius-sm)" }}>
                      <div style={{ color: "var(--text-muted)", fontSize: "10px" }}>Dynamic Range</div>
                      <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>{result.quality.dynamic_range || "N/A"}</div>
                    </div>
                    <div style={{ padding: "6px 8px", backgroundColor: "var(--bg-surface)", borderRadius: "var(--radius-sm)" }}>
                      <div style={{ color: "var(--text-muted)", fontSize: "10px" }}>Edge Density</div>
                      <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>{result.quality.edge_density ? (result.quality.edge_density * 100).toFixed(2) + "%" : "N/A"}</div>
                    </div>
                    <div style={{ padding: "6px 8px", backgroundColor: "var(--bg-surface)", borderRadius: "var(--radius-sm)" }}>
                      <div style={{ color: "var(--text-muted)", fontSize: "10px" }}>Clipping Ratio</div>
                      <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>{result.quality.clipping_ratio ? (result.quality.clipping_ratio * 100).toFixed(2) + "%" : "0.00%"}</div>
                    </div>
                    <div style={{ padding: "6px 8px", backgroundColor: "var(--bg-surface)", borderRadius: "var(--radius-sm)" }}>
                      <div style={{ color: "var(--text-muted)", fontSize: "10px" }}>High-Freq FFT</div>
                      <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>{result.quality.high_freq_fft_ratio ? (result.quality.high_freq_fft_ratio * 100).toFixed(2) + "%" : "N/A"}</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div style={{ display: "flex", gap: "10px", marginTop: "4px" }}>
                <button
                  onClick={() => navigate(`/images/${result.id}`)}
                  className="btn btn-primary btn-sm"
                  style={{ display: "flex", alignItems: "center", gap: "6px" }}
                >
                  <Eye size={14} />
                  <span>Bit-by-Bit Micrograph Inspector</span>
                </button>
                <button
                  onClick={() => navigate(`/search?query_id=${result.id}`)}
                  className="btn btn-secondary btn-sm"
                  style={{ display: "flex", alignItems: "center", gap: "6px" }}
                >
                  <Sparkles size={14} />
                  <span>Execute Vector Retrieval</span>
                </button>
                <button
                  onClick={() => navigate(`/models`)}
                  className="btn btn-secondary btn-sm"
                  style={{ display: "flex", alignItems: "center", gap: "6px" }}
                >
                  <Cpu size={14} />
                  <span>Model Feature Probe</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
