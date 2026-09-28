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
  ShieldCheck
} from "lucide-react";
import { Project } from "../types";
import { ApiClient } from "../api/client";

export const Upload: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<number | "">("");
  const [file, setFile] = useState<File | null>(null);

  // Scientific Metadata Fields matching backend API
  const [microscope, setMicroscope] = useState("Scanning Electron Microscope");
  const [detector, setDetector] = useState("SE");
  const [acceleratingVoltage, setAcceleratingVoltage] = useState("15.0");
  const [magnification, setMagnification] = useState("5000");
  const [pixelSizeNm, setPixelSizeNm] = useState("10.5");

  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    ApiClient.getProjects()
      .then((data) => {
        setProjects(data);
        if (data.length > 0) setSelectedProject(data[0].id);
      })
      .catch((e) => console.error(e));
  }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a valid micrograph image file.");
      return;
    }

    setUploading(true);
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

    try {
      const res = await ApiClient.uploadImage(formData);
      setResult(res);
    } catch (err: any) {
      setError(err.message || "Micrograph ingestion pipeline failure.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px", maxWidth: "860px" }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: "22px", fontWeight: "700", color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "10px" }}>
          <UploadCloud size={22} color="var(--accent-primary)" />
          <span>Scientific Micrograph Ingestion Pipeline</span>
        </h1>
        <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
          Executes the 14-step automated ingestion pipeline: validation, cryptographic SHA-256 fingerprinting,
          6-indicator quality risk profiling, 6-stage redundancy cascade, DINOv2 ViT-S/14 384-D embedding, and exact FAISS indexing.
        </p>
      </div>

      <div className="card">
        <form onSubmit={handleUpload} style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          {/* File Picker Zone */}
          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "8px" }}>
              Micrograph File * (.png, .tif, .tiff, .jpg)
            </label>
            <div style={{
              border: "2px dashed var(--border-default)",
              borderRadius: "var(--radius-md)",
              padding: "24px",
              textAlign: "center",
              backgroundColor: "var(--bg-canvas)",
              transition: "border-color var(--transition-fast)"
            }}>
              <input
                type="file"
                id="file-input"
                accept=".png,.tif,.tiff,.jpg,.jpeg"
                onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
                style={{ display: "none" }}
              />
              <label htmlFor="file-input" style={{ cursor: "pointer", display: "flex", flexDirection: "column", alignItems: "center", gap: "8px" }}>
                <UploadCloud size={32} color="var(--accent-primary)" />
                <div style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)" }}>
                  {file ? file.name : "Click to select micrograph image file"}
                </div>
                <div style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                  {file ? `${(file.size / (1024 * 1024)).toFixed(2)} MB &bull; ${file.type || "image"}` : "Supported formats: TIFF, PNG, JPEG (up to 50 MB)"}
                </div>
              </label>
            </div>
          </div>

          {/* Project & Acquisition Parameters */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
            <div>
              <label style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "6px" }}>
                Target Project / Dataset
              </label>
              <select
                value={selectedProject}
                onChange={(e) => setSelectedProject(e.target.value ? Number(e.target.value) : "")}
                className="input-field"
              >
                <option value="">No Project Assigned</option>
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>{p.name} (#{p.id})</option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "6px" }}>
                Microscope Instrument Model
              </label>
              <input
                type="text"
                value={microscope}
                onChange={(e) => setMicroscope(e.target.value)}
                placeholder="e.g. FEI Helios NanoLab 600"
                className="input-field"
              />
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "16px" }}>
            <div>
              <label style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "6px" }}>
                Detector
              </label>
              <input
                type="text"
                value={detector}
                onChange={(e) => setDetector(e.target.value)}
                placeholder="e.g. SE, BSE, TLD"
                className="input-field"
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "6px" }}>
                Accelerating Voltage (kV)
              </label>
              <input
                type="number"
                step="0.1"
                value={acceleratingVoltage}
                onChange={(e) => setAcceleratingVoltage(e.target.value)}
                placeholder="e.g. 15.0"
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
                placeholder="e.g. 5000"
                className="input-field"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={uploading || !file}
            className="btn btn-primary"
            style={{ height: "42px", alignSelf: "flex-start" }}
          >
            {uploading ? (
              <>
                <Cpu size={16} className="animate-spin" />
                <span>Executing Ingestion Pipeline...</span>
              </>
            ) : (
              <>
                <UploadCloud size={16} />
                <span>Ingest & Index Micrograph</span>
              </>
            )}
          </button>
        </form>

        {error && (
          <div className="card" style={{ marginTop: "20px", borderLeft: "4px solid var(--status-risk)", color: "var(--status-risk)" }}>
            <div style={{ fontWeight: 600, marginBottom: "4px" }}>Ingestion Error</div>
            <div style={{ fontSize: "13px" }}>{error}</div>
          </div>
        )}

        {result && (
          <div className="card" style={{ marginTop: "20px", borderLeft: "4px solid var(--status-nominal)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "var(--status-nominal)", fontWeight: 700 }}>
                <CheckCircle2 size={18} />
                <span>Ingestion Succeeded (Micrograph #{result.id})</span>
              </div>
              <span className="badge badge-nominal">{result.processing_status}</span>
            </div>

            <div style={{ fontSize: "13px", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "6px" }}>
              <div><strong>Original File:</strong> {result.original_filename}</div>
              <div className="font-mono"><strong>SHA-256:</strong> {result.sha256}</div>
              <div>{result.message}</div>
            </div>

            <div style={{ marginTop: "14px", display: "flex", gap: "10px" }}>
              <button
                onClick={() => navigate(`/images/${result.id}`)}
                className="btn btn-primary btn-sm"
              >
                Inspect Micrograph & Provenance
              </button>
              <button
                onClick={() => navigate(`/search?query_id=${result.id}`)}
                className="btn btn-secondary btn-sm"
              >
                Execute Vector Retrieval
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
