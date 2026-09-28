import React, { useEffect, useState } from "react";
import { Project, ScientificImage } from "../types";
import { ApiClient } from "../api/client";
import { useNavigate } from "react-router-dom";

export const Upload: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<number | "">("");
  const [file, setFile] = useState<File | null>(null);
  const [modality, setModality] = useState("SEM");
  const [instrument, setInstrument] = useState("Helios NanoLab");
  const [specimenId, setSpecimenId] = useState("");
  const [roiId, setRoiId] = useState("");
  const [acquisitionId, setAcquisitionId] = useState("");

  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<ScientificImage | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    ApiClient.getProjects().then((data) => {
      setProjects(data);
      if (data.length > 0) setSelectedProject(data[0].id);
    });
  }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !selectedProject) return;

    setUploading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("project_id", selectedProject.toString());
    formData.append("modality", modality);
    formData.append("instrument", instrument);
    if (specimenId) formData.append("specimen_id", specimenId);
    if (roiId) formData.append("roi_id", roiId);
    if (acquisitionId) formData.append("acquisition_id", acquisitionId);

    try {
      const img = await ApiClient.uploadImage(formData);
      setResult(img);
    } catch (err: any) {
      setError(err.message || "Ingestion pipeline failure");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px", maxWidth: "800px" }}>
      <div>
        <h1 style={{ fontSize: "24px", fontWeight: "700", color: "#0f172a" }}>Scientific Image Ingestion</h1>
        <p style={{ fontSize: "14px", color: "#64748b" }}>
          Executes the 14-step idempotent pipeline: validation, cryptographic hashing, immutable storage,
          6-indicator quality profiling, 6-stage duplicate cascade, 384-D DINOv2 embedding, Phase 4 projection,
          FAISS indexing, and relative novelty calculation.
        </p>
      </div>

      <div style={{
        backgroundColor: "#ffffff",
        padding: "24px",
        borderRadius: "8px",
        border: "1px solid #e2e8f0"
      }}>
        <form onSubmit={handleUpload} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div style={{ display: "flex", gap: "16px" }}>
            <div style={{ flex: 1 }}>
              <label style={{ display: "block", fontSize: "13px", fontWeight: "500", color: "#334155", marginBottom: "6px" }}>
                Target Project
              </label>
              <select
                value={selectedProject}
                onChange={(e) => setSelectedProject(Number(e.target.value))}
                required
                style={{ width: "100%", padding: "8px 12px", border: "1px solid #cbd5e1", borderRadius: "4px", fontSize: "14px" }}
              >
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>{p.name} (#{p.id})</option>
                ))}
              </select>
            </div>
            <div style={{ flex: 1 }}>
              <label style={{ display: "block", fontSize: "13px", fontWeight: "500", color: "#334155", marginBottom: "6px" }}>
                Scientific Image File (.png, .tif, .tiff)
              </label>
              <input
                type="file"
                accept=".png,.tif,.tiff,.jpg,.jpeg"
                onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
                required
                style={{ width: "100%", padding: "6px", fontSize: "13px" }}
              />
            </div>
          </div>

          <div style={{ display: "flex", gap: "16px" }}>
            <div style={{ flex: 1 }}>
              <label style={{ display: "block", fontSize: "13px", fontWeight: "500", color: "#334155", marginBottom: "6px" }}>
                Imaging Modality
              </label>
              <input
                type="text"
                value={modality}
                onChange={(e) => setModality(e.target.value)}
                placeholder="SEM, TEM, Confocal, Optical"
                required
                style={{ width: "100%", padding: "8px 12px", border: "1px solid #cbd5e1", borderRadius: "4px", fontSize: "14px" }}
              />
            </div>
            <div style={{ flex: 1 }}>
              <label style={{ display: "block", fontSize: "13px", fontWeight: "500", color: "#334155", marginBottom: "6px" }}>
                Instrument Model
              </label>
              <input
                type="text"
                value={instrument}
                onChange={(e) => setInstrument(e.target.value)}
                placeholder="Helios NanoLab, VEGA3 XMH, Zeiss Gemini"
                style={{ width: "100%", padding: "8px 12px", border: "1px solid #cbd5e1", borderRadius: "4px", fontSize: "14px" }}
              />
            </div>
          </div>

          <div style={{ display: "flex", gap: "16px" }}>
            <div style={{ flex: 1 }}>
              <label style={{ display: "block", fontSize: "13px", fontWeight: "500", color: "#334155", marginBottom: "6px" }}>
                Specimen ID
              </label>
              <input
                type="text"
                value={specimenId}
                onChange={(e) => setSpecimenId(e.target.value)}
                placeholder="e.g. SPEC-441-A"
                style={{ width: "100%", padding: "8px 12px", border: "1px solid #cbd5e1", borderRadius: "4px", fontSize: "14px" }}
              />
            </div>
            <div style={{ flex: 1 }}>
              <label style={{ display: "block", fontSize: "13px", fontWeight: "500", color: "#334155", marginBottom: "6px" }}>
                Region of Interest (ROI) ID
              </label>
              <input
                type="text"
                value={roiId}
                onChange={(e) => setRoiId(e.target.value)}
                placeholder="e.g. ROI-02"
                style={{ width: "100%", padding: "8px 12px", border: "1px solid #cbd5e1", borderRadius: "4px", fontSize: "14px" }}
              />
            </div>
            <div style={{ flex: 1 }}>
              <label style={{ display: "block", fontSize: "13px", fontWeight: "500", color: "#334155", marginBottom: "6px" }}>
                Acquisition Run ID
              </label>
              <input
                type="text"
                value={acquisitionId}
                onChange={(e) => setAcquisitionId(e.target.value)}
                placeholder="e.g. RUN-2026-09"
                style={{ width: "100%", padding: "8px 12px", border: "1px solid #cbd5e1", borderRadius: "4px", fontSize: "14px" }}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={uploading || !file}
            style={{
              padding: "10px 20px",
              backgroundColor: "#2563eb",
              color: "#ffffff",
              border: "none",
              borderRadius: "4px",
              fontSize: "14px",
              fontWeight: "600",
              cursor: uploading || !file ? "not-allowed" : "pointer",
              alignSelf: "flex-start",
              marginTop: "8px"
            }}
          >
            {uploading ? "Executing 14-Step Ingestion Pipeline..." : "Ingest & Index Micrograph"}
          </button>
        </form>

        {error && (
          <div style={{
            marginTop: "20px",
            padding: "12px 16px",
            backgroundColor: "#fef2f2",
            border: "1px solid #f87171",
            color: "#991b1b",
            borderRadius: "4px",
            fontSize: "14px"
          }}>
            <strong>Ingestion Error:</strong> {error}
          </div>
        )}

        {result && (
          <div style={{
            marginTop: "20px",
            padding: "16px 20px",
            backgroundColor: "#f0fdf4",
            border: "1px solid #86efac",
            borderRadius: "6px"
          }}>
            <h3 style={{ fontSize: "16px", color: "#166534", fontWeight: "700", marginBottom: "8px" }}>
              Ingestion Succeeded (Image #{result.id})
            </h3>
            <div style={{ fontSize: "13px", color: "#14532d", display: "flex", flexDirection: "column", gap: "4px" }}>
              <div><strong>SHA-256:</strong> <code>{result.sha256}</code></div>
              <div><strong>Resolution:</strong> {result.width} × {result.height} ({result.channels} ch, {result.bit_depth})</div>
              <div><strong>Quality Status:</strong> {result.quality?.quality_label} (Composite Risk: {result.quality?.composite_quality_risk.toFixed(4)})</div>
              <div><strong>Redundancy Status:</strong> {result.duplicate?.duplicate_status} (Action: {result.duplicate?.action})</div>
              <div><strong>Relative Novelty:</strong> {result.novelty?.novelty_score.toFixed(4)} (Percentile: {result.novelty?.novelty_percentile.toFixed(1)}%)</div>
            </div>
            <button
              onClick={() => navigate(`/images/${result.id}`)}
              style={{
                marginTop: "12px",
                padding: "6px 12px",
                backgroundColor: "#16a34a",
                color: "#ffffff",
                border: "none",
                borderRadius: "4px",
                fontSize: "13px",
                cursor: "pointer"
              }}
            >
              View Full Image Profile & Provenance
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
