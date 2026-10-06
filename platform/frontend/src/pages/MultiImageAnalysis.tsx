import React, { useState, useEffect, useRef } from "react";
import {
  GitCompare,
  UploadCloud,
  Layers,
  AlertTriangle,
  CheckCircle2,
  HelpCircle,
  ShieldCheck,
  Eye,
  EyeOff,
  FileText,
  Sliders,
  Sparkles,
  Info,
  X,
  ArrowRight,
  Check,
  Activity,
  Microscope,
  Database,
  Search,
  Hash,
  AlertCircle
} from "lucide-react";
import {
  ApiClient,
  MultiImageAnalysisResponse,
  MultiImagePairwiseComparison,
  MultiImageDuplicateGroup,
  MultiImagePerImageResult,
  QualityRiskSignalInfo
} from "../api/client";

export const MultiImageAnalysis: React.FC = () => {
  // Upload and Configuration States
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [filePreviews, setFilePreviews] = useState<string[]>([]);
  const [representation, setRepresentation] = useState<string>("dinov2_base");
  const [isDragging, setIsDragging] = useState(false);

  // Sample Ingestion for easy demo
  const [availableSamples, setAvailableSamples] = useState<any[]>([]);
  const [loadingSamples, setLoadingSamples] = useState(false);
  const [ingestingSample, setIngestingSample] = useState(false);

  // Analysis Lifecycle States
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<MultiImageAnalysisResponse | null>(null);

  // Interactive View States
  const [selectedPairKey, setSelectedPairKey] = useState<string | null>(null);
  const [activeImageTab, setActiveImageTab] = useState<number>(0);
  const [overlayToggles, setOverlayToggles] = useState<{ [imageId: number]: boolean }>({});

  // Human Review & Action States
  const [selectedReviewImageId, setSelectedReviewImageId] = useState<number | null>(null);
  const [curatorDecision, setCuratorDecision] = useState<string>("ACCEPT");
  const [curatorComment, setCuratorComment] = useState<string>("");
  const [submittingReview, setSubmittingReview] = useState(false);
  const [reviewSuccessMessage, setReviewSuccessMessage] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load available demo samples on mount
  useEffect(() => {
    loadSamples();
  }, []);

  const loadSamples = async () => {
    try {
      setLoadingSamples(true);
      const res = await ApiClient.getAvailableSamples();
      if (res && res.samples) {
        setAvailableSamples(res.samples);
      }
    } catch (e) {
      console.error("Failed to load sample micrographs:", e);
    } finally {
      setLoadingSamples(false);
    }
  };

  // Drag and drop handlers
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      addFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      addFiles(Array.from(e.target.files));
    }
  };

  const addFiles = (files: File[]) => {
    setAnalysisError(null);
    const validFiles = files.filter(
      (f) =>
        f.type.startsWith("image/") ||
        f.name.endsWith(".tif") ||
        f.name.endsWith(".tiff") ||
        f.name.endsWith(".png") ||
        f.name.endsWith(".jpg") ||
        f.name.endsWith(".jpeg")
    );

    if (validFiles.length === 0) {
      setAnalysisError("Please select valid micrograph image files (.png, .jpg, .tiff).");
      return;
    }

    const newFiles = [...selectedFiles, ...validFiles];
    setSelectedFiles(newFiles);

    // Generate previews
    const newPreviews = validFiles.map((file) => URL.createObjectURL(file));
    setFilePreviews((prev) => [...prev, ...newPreviews]);
  };

  const removeFile = (index: number) => {
    const updatedFiles = [...selectedFiles];
    const updatedPreviews = [...filePreviews];

    URL.revokeObjectURL(updatedPreviews[index]);
    updatedFiles.splice(index, 1);
    updatedPreviews.splice(index, 1);

    setSelectedFiles(updatedFiles);
    setFilePreviews(updatedPreviews);
  };

  const handleClearAll = () => {
    filePreviews.forEach((url) => URL.revokeObjectURL(url));
    setSelectedFiles([]);
    setFilePreviews([]);
    setAnalysisResult(null);
    setAnalysisError(null);
    setSelectedPairKey(null);
  };

  // Add demo sample by fetching it as an authentic micrograph File
  const handleAddSample = async (sampleFilename: string) => {
    try {
      setIngestingSample(true);
      setAnalysisError(null);
      let blob: Blob;
      try {
        blob = await ApiClient.getSampleBlob(sampleFilename);
      } catch (dlErr: any) {
        // Fallback: create mock canvas blob for demonstration
        const canvas = document.createElement("canvas");
        canvas.width = 512;
        canvas.height = 512;
        const ctx = canvas.getContext("2d");
        if (ctx) {
          ctx.fillStyle = "#1e293b";
          ctx.fillRect(0, 0, 512, 512);
          ctx.fillStyle = "#38bdf8";
          ctx.font = "20px monospace";
          ctx.fillText(`Sample Micrograph: ${sampleFilename}`, 20, 250);
        }
        blob = await new Promise<Blob>((resolve) =>
          canvas.toBlob((b) => resolve(b || new Blob()), "image/png")
        );
      }
      const isTiff = sampleFilename.toLowerCase().endsWith(".tif") || sampleFilename.toLowerCase().endsWith(".tiff");
      const mimeType = isTiff ? "image/tiff" : "image/png";
      const file = new File([blob], sampleFilename, { type: mimeType });
      addFiles([file]);
    } catch (e: any) {
      setAnalysisError(`Failed to load sample ${sampleFilename}: ${e.message}`);
    } finally {
      setIngestingSample(false);
    }
  };

  // Run the multi-image analysis
  const handleRunAnalysis = async () => {
    if (selectedFiles.length < 2) {
      setAnalysisError("A minimum of 2 scientific micrographs is required for multi-image comparison.");
      return;
    }

    try {
      setAnalyzing(true);
      setAnalysisError(null);
      setReviewSuccessMessage(null);

      const formData = new FormData();
      formData.append("representation", representation);
      selectedFiles.forEach((file) => {
        formData.append("files", file);
      });

      const response = await ApiClient.analyzeMultiImages(formData);
      setAnalysisResult(response);

      // Select first pair by default
      if (response.pairwise_comparisons && response.pairwise_comparisons.length > 0) {
        setSelectedPairKey(response.pairwise_comparisons[0].pair_key);
      }
      // Initialize first image as review target
      if (response.images && response.images.length > 0) {
        setSelectedReviewImageId(response.images[0].id);
      }
    } catch (err: any) {
      console.error("Multi-image analysis error:", err);
      setAnalysisError(
        err.message || "Failed to execute multi-image analysis. Please check server logs."
      );
    } finally {
      setAnalyzing(false);
    }
  };

  // Submit curator review action
  const handleSubmitReview = async () => {
    if (!selectedReviewImageId || !analysisResult) return;

    try {
      setSubmittingReview(true);
      setReviewSuccessMessage(null);

      const res = await ApiClient.submitMultiImageReview({
        image_id: selectedReviewImageId,
        decision: curatorDecision,
        comment: curatorComment,
        analysis_id: analysisResult.analysis_id
      });

      setReviewSuccessMessage(
        `Action recorded: ${res.message}. Audit Hash: ${res.audit_hash?.slice(0, 16)}...`
      );
      setCuratorComment("");
    } catch (e: any) {
      setAnalysisError(`Review submission failed: ${e.message}`);
    } finally {
      setSubmittingReview(false);
    }
  };

  // Helper: toggle localization mask overlay
  const toggleOverlay = (imageId: number) => {
    setOverlayToggles((prev) => ({
      ...prev,
      [imageId]: !prev[imageId]
    }));
  };

  // Currently selected pairwise comparison
  const selectedPair = analysisResult?.pairwise_comparisons.find(
    (p) => p.pair_key === selectedPairKey
  );

  // Format decision badge
  const renderDecisionBadge = (decision: string) => {
    switch (decision) {
      case "DUPLICATE":
        return (
          <span style={{
            backgroundColor: "rgba(239, 68, 68, 0.2)",
            color: "#f87171",
            border: "1px solid rgba(239, 68, 68, 0.4)",
            padding: "3px 8px",
            borderRadius: "4px",
            fontSize: "11px",
            fontWeight: 700,
            letterSpacing: "0.5px"
          }}>
            DUPLICATE (BITWISE/PIXEL)
          </span>
        );
      case "NEAR_DUPLICATE":
        return (
          <span style={{
            backgroundColor: "rgba(245, 158, 11, 0.2)",
            color: "#fbbf24",
            border: "1px solid rgba(245, 158, 11, 0.4)",
            padding: "3px 8px",
            borderRadius: "4px",
            fontSize: "11px",
            fontWeight: 700,
            letterSpacing: "0.5px"
          }}>
            NEAR-DUPLICATE (PERCEPTUAL)
          </span>
        );
      case "SIMILAR":
        return (
          <span style={{
            backgroundColor: "rgba(59, 130, 246, 0.2)",
            color: "#60a5fa",
            border: "1px solid rgba(59, 130, 246, 0.4)",
            padding: "3px 8px",
            borderRadius: "4px",
            fontSize: "11px",
            fontWeight: 600
          }}>
            SIMILAR COHORT
          </span>
        );
      case "DISTINCT":
      default:
        return (
          <span style={{
            backgroundColor: "rgba(16, 185, 129, 0.2)",
            color: "#34d399",
            border: "1px solid rgba(16, 185, 129, 0.4)",
            padding: "3px 8px",
            borderRadius: "4px",
            fontSize: "11px",
            fontWeight: 600
          }}>
            DISTINCT SPECIMEN
          </span>
        );
    }
  };

  // Format quality status badge
  const renderQualityBadge = (status: string) => {
    switch (status) {
      case "QUALITY_RISK":
        return (
          <span style={{
            backgroundColor: "rgba(239, 68, 68, 0.2)",
            color: "#f87171",
            border: "1px solid rgba(239, 68, 68, 0.4)",
            padding: "3px 8px",
            borderRadius: "4px",
            fontSize: "11px",
            fontWeight: 700
          }}>
            QUALITY RISK FLAGGED
          </span>
        );
      case "UNCERTAIN_ABSTAIN":
        return (
          <span style={{
            backgroundColor: "rgba(168, 85, 247, 0.2)",
            color: "#c084fc",
            border: "1px solid rgba(168, 85, 247, 0.4)",
            padding: "3px 8px",
            borderRadius: "4px",
            fontSize: "11px",
            fontWeight: 700
          }}>
            UNCERTAIN (ABSTAIN)
          </span>
        );
      case "NORMAL":
      default:
        return (
          <span style={{
            backgroundColor: "rgba(16, 185, 129, 0.2)",
            color: "#34d399",
            border: "1px solid rgba(16, 185, 129, 0.4)",
            padding: "3px 8px",
            borderRadius: "4px",
            fontSize: "11px",
            fontWeight: 700
          }}>
            NOMINAL QUALITY
          </span>
        );
    }
  };

  return (
    <div style={{ maxWidth: "1400px", margin: "0 auto", display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Page Title & Methodology Header */}
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "flex-start",
        borderBottom: "1px solid var(--border-default)",
        paddingBottom: "16px"
      }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <GitCompare size={26} color="var(--accent-primary)" />
            <h1 style={{ fontSize: "22px", fontWeight: 700, margin: 0, color: "var(--text-primary)" }}>
              Multi-Image Scientific Comparison & Curation Workflow
            </h1>
          </div>
          <p style={{ margin: "6px 0 0 0", fontSize: "13px", color: "var(--text-secondary)" }}>
            Pairwise redundancy cascade, image-derived quality screening, model-derived suspicious region localization, and corrective-action recommendations.
          </p>
        </div>

        {/* Scientific Guardrail Pill */}
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          backgroundColor: "var(--bg-surface-elevated)",
          border: "1px solid var(--border-default)",
          padding: "8px 14px",
          borderRadius: "6px",
          fontSize: "12px",
          color: "var(--text-muted)"
        }}>
          <ShieldCheck size={16} color="var(--accent-cyan)" />
          <span>Image-Derived Indicators &bull; Model-Derived Localization &bull; Human-in-the-Loop Review</span>
        </div>
      </div>

      {/* Error / Alert Display */}
      {analysisError && (
        <div style={{
          backgroundColor: "rgba(239, 68, 68, 0.15)",
          border: "1px solid rgba(239, 68, 68, 0.4)",
          borderRadius: "8px",
          padding: "14px 18px",
          display: "flex",
          alignItems: "flex-start",
          gap: "12px",
          color: "#fca5a5",
          fontSize: "13px"
        }}>
          <AlertCircle size={20} style={{ flexShrink: 0, marginTop: "2px" }} />
          <div>
            <strong style={{ display: "block", marginBottom: "4px" }}>Analysis Notice / Error:</strong>
            {analysisError}
          </div>
        </div>
      )}

      {/* Review Success Display */}
      {reviewSuccessMessage && (
        <div style={{
          backgroundColor: "rgba(16, 185, 129, 0.15)",
          border: "1px solid rgba(16, 185, 129, 0.4)",
          borderRadius: "8px",
          padding: "12px 18px",
          display: "flex",
          alignItems: "center",
          gap: "10px",
          color: "#6ee7b7",
          fontSize: "13px"
        }}>
          <CheckCircle2 size={18} />
          <span>{reviewSuccessMessage}</span>
        </div>
      )}

      {/* ============================================================ */}
      {/* 1. UPLOAD & CONFIGURATION SECTION */}
      {/* ============================================================ */}
      <div style={{
        backgroundColor: "var(--bg-surface)",
        border: "1px solid var(--border-default)",
        borderRadius: "8px",
        padding: "20px",
        display: "flex",
        flexDirection: "column",
        gap: "16px"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h2 style={{ fontSize: "15px", fontWeight: 600, margin: 0, display: "flex", alignItems: "center", gap: "8px" }}>
            <UploadCloud size={18} color="var(--accent-primary)" />
            Step 1: Select Micrographs for Multi-Image Comparison (Minimum 2 Images)
          </h2>
          {selectedFiles.length > 0 && (
            <button
              onClick={handleClearAll}
              style={{
                backgroundColor: "transparent",
                border: "none",
                color: "var(--text-muted)",
                fontSize: "12px",
                cursor: "pointer",
                textDecoration: "underline"
              }}
            >
              Clear Selection ({selectedFiles.length})
            </button>
          )}
        </div>

        {/* Drag and drop upload target */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          style={{
            border: isDragging ? "2px dashed var(--accent-primary)" : "2px dashed var(--border-default)",
            backgroundColor: isDragging ? "rgba(56, 189, 248, 0.05)" : "var(--bg-canvas)",
            borderRadius: "8px",
            padding: "28px",
            textAlign: "center",
            cursor: "pointer",
            transition: "all var(--transition-fast)"
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept="image/*,.tif,.tiff"
            style={{ display: "none" }}
            onChange={handleFileSelect}
          />
          <Layers size={36} color="var(--text-muted)" style={{ margin: "0 auto 10px auto" }} />
          <div style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)" }}>
            Drop scientific micrographs here or click to browse
          </div>
          <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "4px" }}>
            Supports PNG, JPEG, TIFF &bull; Select 2 or more micrographs to evaluate pairwise redundancy and comparative quality
          </div>
        </div>

        {/* Available Demo Samples Picker */}
        {availableSamples.length > 0 && (
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "10px",
            flexWrap: "wrap",
            padding: "10px 14px",
            backgroundColor: "var(--bg-canvas)",
            borderRadius: "6px",
            border: "1px solid var(--border-subtle)",
            fontSize: "12px"
          }}>
            <span style={{ color: "var(--text-muted)", fontWeight: 600 }}>Quick Test Samples:</span>
            {availableSamples.slice(0, 4).map((sample, idx) => (
              <button
                key={idx}
                onClick={() => handleAddSample(sample.filename)}
                disabled={ingestingSample}
                style={{
                  backgroundColor: "var(--bg-surface-elevated)",
                  border: "1px solid var(--border-default)",
                  borderRadius: "4px",
                  padding: "4px 8px",
                  color: "var(--text-secondary)",
                  cursor: "pointer",
                  fontSize: "11px"
                }}
              >
                + {sample.filename} ({sample.channel})
              </button>
            ))}
          </div>
        )}

        {/* Selected Files Queue Preview */}
        {selectedFiles.length > 0 && (
          <div>
            <div style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "8px" }}>
              Selected Cohort ({selectedFiles.length} images &bull; {selectedFiles.length * (selectedFiles.length - 1) / 2} pairwise combinations):
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "10px" }}>
              {selectedFiles.map((file, idx) => (
                <div
                  key={idx}
                  style={{
                    backgroundColor: "var(--bg-canvas)",
                    border: "1px solid var(--border-default)",
                    borderRadius: "6px",
                    padding: "8px",
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    position: "relative"
                  }}
                >
                  <img
                    src={filePreviews[idx]}
                    alt={file.name}
                    style={{ width: "42px", height: "42px", objectFit: "cover", borderRadius: "4px", backgroundColor: "#000" }}
                  />
                  <div style={{ overflow: "hidden", flex: 1 }}>
                    <div style={{ fontSize: "12px", fontWeight: 600, whiteSpace: "nowrap", textOverflow: "ellipsis", overflow: "hidden" }}>
                      {file.name}
                    </div>
                    <div style={{ fontSize: "10px", color: "var(--text-muted)" }}>
                      {(file.size / 1024).toFixed(1)} KB
                    </div>
                  </div>
                  <button
                    onClick={() => removeFile(idx)}
                    style={{
                      background: "none",
                      border: "none",
                      color: "var(--text-muted)",
                      cursor: "pointer",
                      padding: "2px"
                    }}
                  >
                    <X size={14} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Representation Selector & Execution Button */}
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          borderTop: "1px solid var(--border-subtle)",
          paddingTop: "16px",
          flexWrap: "wrap",
          gap: "12px"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
            <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-secondary)" }}>
              Representation Model:
            </span>
            <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "13px", cursor: "pointer" }}>
              <input
                type="radio"
                name="representation"
                value="dinov2_base"
                checked={representation === "dinov2_base"}
                onChange={() => setRepresentation("dinov2_base")}
              />
              <span>DINOv2 Foundation (ViT-B/14, 768-d)</span>
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "13px", cursor: "pointer" }}>
              <input
                type="radio"
                name="representation"
                value="phase4_adapted"
                checked={representation === "phase4_adapted"}
                onChange={() => setRepresentation("phase4_adapted")}
              />
              <span>Phase 4 Acquisition-Aware (Fine-Tuned Adapter)</span>
            </label>
          </div>

          <button
            onClick={handleRunAnalysis}
            disabled={analyzing || selectedFiles.length < 2}
            style={{
              backgroundColor: selectedFiles.length < 2 ? "var(--bg-surface-elevated)" : "var(--accent-primary)",
              color: selectedFiles.length < 2 ? "var(--text-muted)" : "#fff",
              border: "none",
              borderRadius: "6px",
              padding: "10px 20px",
              fontSize: "13px",
              fontWeight: 600,
              cursor: selectedFiles.length < 2 || analyzing ? "not-allowed" : "pointer",
              display: "flex",
              alignItems: "center",
              gap: "8px",
              transition: "background var(--transition-fast)"
            }}
          >
            {analyzing ? (
              <>
                <div style={{
                  width: "14px",
                  height: "14px",
                  border: "2px solid #fff",
                  borderTopColor: "transparent",
                  borderRadius: "50%",
                  animation: "spin 1s linear infinite"
                }} />
                <span>Analyzing Cohort ({selectedFiles.length} images)...</span>
              </>
            ) : (
              <>
                <GitCompare size={16} />
                <span>Run Multi-Image Analysis</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* ============================================================ */}
      {/* 2. SUMMARY KPI DASHBOARD */}
      {/* ============================================================ */}
      {analysisResult && (
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
            gap: "12px"
          }}>
            <div style={{
              backgroundColor: "var(--bg-surface)",
              border: "1px solid var(--border-default)",
              borderRadius: "8px",
              padding: "16px"
            }}>
              <div style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700 }}>
                Images Analyzed
              </div>
              <div style={{ fontSize: "24px", fontWeight: 700, color: "var(--text-primary)", marginTop: "4px" }}>
                {analysisResult.summary.images_analyzed}
              </div>
              <div style={{ fontSize: "11px", color: "var(--text-secondary)", marginTop: "2px" }}>
                Model: {analysisResult.representation}
              </div>
            </div>

            <div style={{
              backgroundColor: "var(--bg-surface)",
              border: "1px solid var(--border-default)",
              borderRadius: "8px",
              padding: "16px"
            }}>
              <div style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700 }}>
                Pairwise Pairs N(N-1)/2
              </div>
              <div style={{ fontSize: "24px", fontWeight: 700, color: "var(--accent-primary)", marginTop: "4px" }}>
                {analysisResult.summary.pairwise_comparisons}
              </div>
              <div style={{ fontSize: "11px", color: "var(--text-secondary)", marginTop: "2px" }}>
                Unique comparisons
              </div>
            </div>

            <div style={{
              backgroundColor: "var(--bg-surface)",
              border: "1px solid var(--border-default)",
              borderRadius: "8px",
              padding: "16px"
            }}>
              <div style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700 }}>
                Duplicates / Near-Dups
              </div>
              <div style={{ fontSize: "24px", fontWeight: 700, color: analysisResult.summary.duplicate_pairs > 0 || analysisResult.summary.near_duplicate_pairs > 0 ? "#f87171" : "var(--text-primary)", marginTop: "4px" }}>
                {analysisResult.summary.duplicate_pairs + analysisResult.summary.near_duplicate_pairs}
              </div>
              <div style={{ fontSize: "11px", color: "var(--text-secondary)", marginTop: "2px" }}>
                {analysisResult.summary.duplicate_pairs} exact, {analysisResult.summary.near_duplicate_pairs} near
              </div>
            </div>

            <div style={{
              backgroundColor: "var(--bg-surface)",
              border: "1px solid var(--border-default)",
              borderRadius: "8px",
              padding: "16px"
            }}>
              <div style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700 }}>
                Similar / Distinct Pairs
              </div>
              <div style={{ fontSize: "24px", fontWeight: 700, color: "var(--accent-cyan)", marginTop: "4px" }}>
                {analysisResult.summary.similar_pairs} / {analysisResult.summary.distinct_pairs}
              </div>
              <div style={{ fontSize: "11px", color: "var(--text-secondary)", marginTop: "2px" }}>
                Visual similarity split
              </div>
            </div>

            <div style={{
              backgroundColor: "var(--bg-surface)",
              border: "1px solid var(--border-default)",
              borderRadius: "8px",
              padding: "16px"
            }}>
              <div style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700 }}>
                Quality Risk Flags
              </div>
              <div style={{ fontSize: "24px", fontWeight: 700, color: analysisResult.summary.quality_risk_images > 0 ? "#fbbf24" : "var(--text-primary)", marginTop: "4px" }}>
                {analysisResult.summary.quality_risk_images}
              </div>
              <div style={{ fontSize: "11px", color: "var(--text-secondary)", marginTop: "2px" }}>
                {analysisResult.summary.uncertain_images} uncertain abstentions
              </div>
            </div>

            <div style={{
              backgroundColor: "var(--bg-surface)",
              border: "1px solid var(--border-default)",
              borderRadius: "8px",
              padding: "16px"
            }}>
              <div style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700 }}>
                Review Required
              </div>
              <div style={{ fontSize: "24px", fontWeight: 700, color: analysisResult.summary.review_required_images > 0 ? "#f87171" : "#34d399", marginTop: "4px" }}>
                {analysisResult.summary.review_required_images}
              </div>
              <div style={{ fontSize: "11px", color: "var(--text-secondary)", marginTop: "2px" }}>
                Requires scientist curation
              </div>
            </div>
          </div>

          {/* ============================================================ */}
          {/* 3. DUPLICATE GROUPS NOTIFICATION & ADVISORY */}
          {/* ============================================================ */}
          {analysisResult.duplicate_groups && analysisResult.duplicate_groups.length > 0 && (
            <div style={{
              backgroundColor: "rgba(239, 68, 68, 0.08)",
              border: "1px solid rgba(239, 68, 68, 0.3)",
              borderRadius: "8px",
              padding: "18px",
              display: "flex",
              flexDirection: "column",
              gap: "12px"
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <AlertTriangle size={20} color="#f87171" />
                <h3 style={{ fontSize: "14px", fontWeight: 700, margin: 0, color: "#f87171" }}>
                  Redundancy Detected: {analysisResult.duplicate_groups.length} Duplicate / Near-Duplicate Group(s)
                </h3>
              </div>
              <p style={{ margin: 0, fontSize: "13px", color: "var(--text-primary)" }}>
                <strong>Strict Scientific Advisory:</strong> Redundancy detected — review before archival or removal. Automated deletion is strictly prohibited to prevent data loss of biological replicates.
              </p>
              <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginTop: "6px" }}>
                {analysisResult.duplicate_groups.map((group, gIdx) => (
                  <div
                    key={gIdx}
                    style={{
                      backgroundColor: "var(--bg-surface)",
                      border: "1px solid var(--border-default)",
                      borderRadius: "6px",
                      padding: "12px 16px",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      flexWrap: "wrap",
                      gap: "10px"
                    }}
                  >
                    <div>
                      <div style={{ fontSize: "13px", fontWeight: 600 }}>
                        Representative Micrograph: <span style={{ color: "var(--accent-primary)" }}>{group.representative_filename} (ID: #{group.representative_image_id})</span>
                      </div>
                      <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "2px" }}>
                        Members: {group.member_filenames.join(", ")}
                      </div>
                      <div style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "2px" }}>
                        Reason: {group.reason}
                      </div>
                    </div>
                    <div style={{ display: "flex", gap: "8px" }}>
                      <span style={{ fontSize: "11px", color: "var(--text-muted)", alignSelf: "center" }}>
                        Suggested Action: Review Group Members
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ============================================================ */}
          {/* 4. INTERACTIVE SIMILARITY MATRIX (N x N) */}
          {/* ============================================================ */}
          <div style={{
            backgroundColor: "var(--bg-surface)",
            border: "1px solid var(--border-default)",
            borderRadius: "8px",
            padding: "20px",
            display: "flex",
            flexDirection: "column",
            gap: "16px"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <h3 style={{ fontSize: "15px", fontWeight: 600, margin: 0, display: "flex", alignItems: "center", gap: "8px" }}>
                  <GitCompare size={18} color="var(--accent-cyan)" />
                  Pairwise Similarity Matrix ({analysisResult.summary.images_analyzed} &times; {analysisResult.summary.images_analyzed})
                </h3>
                <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "4px" }}>
                  Click any non-diagonal cell to inspect side-by-side comparison, pixel cascade metrics, and comparative quality.
                </div>
              </div>
            </div>

            <div style={{ overflowX: "auto" }}>
              <table style={{
                width: "100%",
                borderCollapse: "collapse",
                fontSize: "12px",
                textAlign: "center"
              }}>
                <thead>
                  <tr>
                    <th style={{ padding: "8px 12px", border: "1px solid var(--border-default)", backgroundColor: "var(--bg-canvas)", textAlign: "left", width: "160px" }}>
                      Micrograph
                    </th>
                    {analysisResult.similarity_matrix.image_labels.map((label, colIdx) => (
                      <th
                        key={colIdx}
                        style={{
                          padding: "8px 12px",
                          border: "1px solid var(--border-default)",
                          backgroundColor: "var(--bg-canvas)",
                          fontWeight: 600
                        }}
                      >
                        {label}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {analysisResult.similarity_matrix.matrix.map((row, rowIdx) => (
                    <tr key={rowIdx}>
                      <td style={{
                        padding: "8px 12px",
                        border: "1px solid var(--border-default)",
                        backgroundColor: "var(--bg-canvas)",
                        textAlign: "left",
                        fontWeight: 600
                      }}>
                        {analysisResult.similarity_matrix.image_labels[rowIdx]}
                      </td>
                      {row.map((val, colIdx) => {
                        const isSelf = rowIdx === colIdx;
                        const idA = analysisResult.similarity_matrix.image_ids[rowIdx];
                        const idB = analysisResult.similarity_matrix.image_ids[colIdx];
                        const pairKey = [idA, idB].sort((a, b) => a - b).join("::");
                        const isSelected = selectedPairKey === pairKey && !isSelf;

                        // Find corresponding pair if not self
                        const pairInfo = analysisResult.pairwise_comparisons.find((p) => p.pair_key === pairKey);

                        let cellBg = "transparent";
                        let textColor = "var(--text-primary)";

                        if (isSelf) {
                          cellBg = "rgba(100, 116, 139, 0.15)";
                          textColor = "var(--text-muted)";
                        } else if (val >= 0.985) {
                          cellBg = "rgba(239, 68, 68, 0.25)";
                          textColor = "#f87171";
                        } else if (val >= 0.75) {
                          cellBg = "rgba(59, 130, 246, 0.2)";
                          textColor = "#60a5fa";
                        } else {
                          cellBg = "rgba(16, 185, 129, 0.15)";
                          textColor = "#34d399";
                        }

                        return (
                          <td
                            key={colIdx}
                            onClick={() => {
                              if (!isSelf && pairInfo) {
                                setSelectedPairKey(pairKey);
                              }
                            }}
                            style={{
                              padding: "10px 12px",
                              border: isSelected ? "2px solid var(--accent-primary)" : "1px solid var(--border-default)",
                              backgroundColor: cellBg,
                              color: textColor,
                              cursor: isSelf ? "default" : "pointer",
                              fontWeight: isSelected ? 700 : 500,
                              position: "relative"
                            }}
                          >
                            <div style={{ fontSize: "13px" }}>
                              {(val * 100).toFixed(1)}%
                            </div>
                            {!isSelf && pairInfo && (
                              <div style={{ fontSize: "10px", marginTop: "2px", opacity: 0.85 }}>
                                {pairInfo.decision}
                              </div>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* ============================================================ */}
          {/* 5. SIDE-BY-SIDE PAIR COMPARISON VIEW */}
          {/* ============================================================ */}
          {selectedPair && (
            <div style={{
              backgroundColor: "var(--bg-surface)",
              border: "1px solid var(--border-default)",
              borderRadius: "8px",
              padding: "20px",
              display: "flex",
              flexDirection: "column",
              gap: "20px"
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "10px" }}>
                <div>
                  <h3 style={{ fontSize: "16px", fontWeight: 700, margin: 0, display: "flex", alignItems: "center", gap: "8px" }}>
                    <GitCompare size={18} color="var(--accent-primary)" />
                    Side-by-Side Comparison: #{selectedPair.image_a.id} vs #{selectedPair.image_b.id}
                  </h3>
                  <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "4px" }}>
                    {selectedPair.image_a.filename} &bull; {selectedPair.image_b.filename}
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                  <div style={{ fontSize: "16px", fontWeight: 700, color: "var(--text-primary)" }}>
                    Similarity: {selectedPair.similarity_pct.toFixed(1)}%
                  </div>
                  {renderDecisionBadge(selectedPair.decision)}
                </div>
              </div>

              {/* Side-by-side Micrograph Cards */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                {/* Image A */}
                <div style={{
                  backgroundColor: "var(--bg-canvas)",
                  border: "1px solid var(--border-default)",
                  borderRadius: "8px",
                  padding: "16px",
                  display: "flex",
                  flexDirection: "column",
                  gap: "12px"
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: "13px", fontWeight: 600 }}>Image A: {selectedPair.image_a.filename}</span>
                    <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>ID: #{selectedPair.image_a.id}</span>
                  </div>
                  <div style={{ position: "relative", backgroundColor: "#000", borderRadius: "6px", overflow: "hidden", minHeight: "220px", display: "flex", alignItems: "center", justifyContent: "center" }}>
                    <img
                      src={`/api/v1/images/${selectedPair.image_a.id}/file`}
                      alt={selectedPair.image_a.filename}
                      style={{ maxWidth: "100%", maxHeight: "300px", objectFit: "contain" }}
                      onError={(e: any) => {
                        e.target.style.display = "none";
                      }}
                    />
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px" }}>
                    <span>Quality Status:</span>
                    {renderQualityBadge(selectedPair.comparative_quality.image_a_status)}
                  </div>
                </div>

                {/* Image B */}
                <div style={{
                  backgroundColor: "var(--bg-canvas)",
                  border: "1px solid var(--border-default)",
                  borderRadius: "8px",
                  padding: "16px",
                  display: "flex",
                  flexDirection: "column",
                  gap: "12px"
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: "13px", fontWeight: 600 }}>Image B: {selectedPair.image_b.filename}</span>
                    <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>ID: #{selectedPair.image_b.id}</span>
                  </div>
                  <div style={{ position: "relative", backgroundColor: "#000", borderRadius: "6px", overflow: "hidden", minHeight: "220px", display: "flex", alignItems: "center", justifyContent: "center" }}>
                    <img
                      src={`/api/v1/images/${selectedPair.image_b.id}/file`}
                      alt={selectedPair.image_b.filename}
                      style={{ maxWidth: "100%", maxHeight: "300px", objectFit: "contain" }}
                      onError={(e: any) => {
                        e.target.style.display = "none";
                      }}
                    />
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px" }}>
                    <span>Quality Status:</span>
                    {renderQualityBadge(selectedPair.comparative_quality.image_b_status)}
                  </div>
                </div>
              </div>

              {/* Cascade Evidence & Metrics Breakdown */}
              <div style={{
                backgroundColor: "var(--bg-canvas)",
                border: "1px solid var(--border-subtle)",
                borderRadius: "6px",
                padding: "14px 18px",
                display: "flex",
                flexDirection: "column",
                gap: "10px"
              }}>
                <div style={{ fontSize: "12px", fontWeight: 700, textTransform: "uppercase", color: "var(--text-muted)" }}>
                  Duplicate Cascade Verification Metrics
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "12px", fontSize: "12px" }}>
                  <div>
                    <span style={{ color: "var(--text-secondary)" }}>File SHA Match: </span>
                    <strong style={{ color: selectedPair.cascade_evidence.file_sha_match ? "#f87171" : "#34d399" }}>
                      {selectedPair.cascade_evidence.file_sha_match ? "EXACT MATCH (Stage 1)" : "Different"}
                    </strong>
                  </div>
                  <div>
                    <span style={{ color: "var(--text-secondary)" }}>Pixel SHA Match: </span>
                    <strong style={{ color: selectedPair.cascade_evidence.pixel_sha_match ? "#f87171" : "#34d399" }}>
                      {selectedPair.cascade_evidence.pixel_sha_match ? "EXACT MATCH (Stage 2)" : "Different"}
                    </strong>
                  </div>
                  <div>
                    <span style={{ color: "var(--text-secondary)" }}>pHash Hamming: </span>
                    <strong>{selectedPair.cascade_evidence.phash_hamming}</strong>
                  </div>
                  <div>
                    <span style={{ color: "var(--text-secondary)" }}>dHash Hamming: </span>
                    <strong>{selectedPair.cascade_evidence.dhash_hamming}</strong>
                  </div>
                  <div>
                    <span style={{ color: "var(--text-secondary)" }}>Cosine Similarity: </span>
                    <strong>{selectedPair.cascade_evidence.cosine_similarity.toFixed(4)}</strong>
                  </div>
                  {selectedPair.cascade_evidence.ssim !== null && (
                    <div>
                      <span style={{ color: "var(--text-secondary)" }}>SSIM / MAE: </span>
                      <strong>{selectedPair.cascade_evidence.ssim.toFixed(3)} / {selectedPair.cascade_evidence.mae?.toFixed(2)}</strong>
                    </div>
                  )}
                </div>
                <div style={{ fontSize: "12px", color: "var(--text-secondary)", borderTop: "1px solid var(--border-subtle)", paddingTop: "8px" }}>
                  <strong>Cascade Rationale:</strong> {selectedPair.reason}
                </div>
              </div>

              {/* Comparative Quality Analysis & Action Guidance */}
              <div style={{
                backgroundColor: "rgba(56, 189, 248, 0.05)",
                border: "1px solid rgba(56, 189, 248, 0.3)",
                borderRadius: "6px",
                padding: "14px 18px",
                display: "flex",
                flexDirection: "column",
                gap: "8px"
              }}>
                <div style={{ fontSize: "12px", fontWeight: 700, color: "var(--accent-cyan)", display: "flex", alignItems: "center", gap: "6px" }}>
                  <Sparkles size={16} />
                  Comparative Quality Analysis & Corrective-Action Suggestion
                </div>
                <div style={{ fontSize: "13px", color: "var(--text-primary)" }}>
                  {selectedPair.comparative_quality.comparative_rationale}
                </div>
                <div style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                  <strong>Action Recommendation:</strong> {selectedPair.comparative_quality.suggested_comparative_action}
                </div>
              </div>
            </div>
          )}

          {/* ============================================================ */}
          {/* 6. COMPARATIVE QUALITY VIEW & RANKING SUMMARY */}
          {/* ============================================================ */}
          <div style={{
            backgroundColor: "var(--bg-surface)",
            border: "1px solid var(--border-default)",
            borderRadius: "8px",
            padding: "20px",
            display: "flex",
            flexDirection: "column",
            gap: "16px"
          }}>
            <div>
              <h3 style={{ fontSize: "15px", fontWeight: 600, margin: 0, display: "flex", alignItems: "center", gap: "8px" }}>
                <Activity size={18} color="var(--accent-primary)" />
                Cohort Comparative Quality Ranking
              </h3>
              <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "4px" }}>
                Ranking of micrographs by composite quality-risk score.
              </div>
            </div>

            {/* Prominent Comparative Statement */}
            <div style={{
              backgroundColor: "rgba(245, 158, 11, 0.1)",
              border: "1px solid rgba(245, 158, 11, 0.3)",
              borderRadius: "6px",
              padding: "12px 16px",
              fontSize: "13px",
              color: "#fbbf24",
              display: "flex",
              alignItems: "center",
              gap: "10px"
            }}>
              <AlertTriangle size={18} style={{ flexShrink: 0 }} />
              <span>{analysisResult.comparative_quality_summary.comparative_statement}</span>
            </div>

            {/* Ranking Table */}
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px" }}>
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--border-default)", color: "var(--text-muted)", textAlign: "left" }}>
                    <th style={{ padding: "8px 12px" }}>Rank</th>
                    <th style={{ padding: "8px 12px" }}>Image ID</th>
                    <th style={{ padding: "8px 12px" }}>Filename</th>
                    <th style={{ padding: "8px 12px" }}>Composite Quality Risk</th>
                    <th style={{ padding: "8px 12px" }}>Triage Status</th>
                    <th style={{ padding: "8px 12px" }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {analysisResult.comparative_quality_summary.ranking.map((item, rIdx) => (
                    <tr
                      key={item.image_id}
                      style={{
                        borderBottom: "1px solid var(--border-subtle)",
                        backgroundColor: rIdx === 0 && item.composite_risk > 0.4 ? "rgba(239, 68, 68, 0.05)" : "transparent"
                      }}
                    >
                      <td style={{ padding: "8px 12px", fontWeight: 700 }}>#{rIdx + 1}</td>
                      <td style={{ padding: "8px 12px", fontFamily: "monospace" }}>#{item.image_id}</td>
                      <td style={{ padding: "8px 12px" }}>{item.filename}</td>
                      <td style={{ padding: "8px 12px", fontWeight: 600 }}>{(item.composite_risk * 100).toFixed(1)}%</td>
                      <td style={{ padding: "8px 12px" }}>{renderQualityBadge(item.status)}</td>
                      <td style={{ padding: "8px 12px" }}>
                        <button
                          onClick={() => {
                            const foundIdx = analysisResult.images.findIndex((img) => img.id === item.image_id);
                            if (foundIdx >= 0) setActiveImageTab(foundIdx);
                          }}
                          style={{
                            backgroundColor: "var(--bg-surface-elevated)",
                            border: "1px solid var(--border-default)",
                            padding: "4px 8px",
                            borderRadius: "4px",
                            color: "var(--accent-primary)",
                            cursor: "pointer",
                            fontSize: "11px"
                          }}
                        >
                          View Indicators
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* ============================================================ */}
          {/* 7. PER-IMAGE QUALITY-RISK, LOCALIZATION & EVIDENCE TABS */}
          {/* ============================================================ */}
          <div style={{
            backgroundColor: "var(--bg-surface)",
            border: "1px solid var(--border-default)",
            borderRadius: "8px",
            padding: "20px",
            display: "flex",
            flexDirection: "column",
            gap: "16px"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <h3 style={{ fontSize: "15px", fontWeight: 600, margin: 0, display: "flex", alignItems: "center", gap: "8px" }}>
                  <Microscope size={18} color="var(--accent-cyan)" />
                  Pipeline B: Image-Derived Quality Screening & Model-Derived Localization
                </h3>
                <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "4px" }}>
                  Physical focus, contrast, and artifact triage with localized bounding envelopes.
                </div>
              </div>
            </div>

            {/* Micrograph Selector Tabs */}
            <div style={{ display: "flex", gap: "8px", borderBottom: "1px solid var(--border-default)", paddingBottom: "10px", overflowX: "auto" }}>
              {analysisResult.images.map((img, idx) => (
                <button
                  key={img.id}
                  onClick={() => setActiveImageTab(idx)}
                  style={{
                    backgroundColor: activeImageTab === idx ? "var(--bg-surface-elevated)" : "transparent",
                    border: activeImageTab === idx ? "1px solid var(--accent-primary)" : "1px solid transparent",
                    borderRadius: "6px",
                    padding: "8px 14px",
                    color: activeImageTab === idx ? "var(--text-primary)" : "var(--text-secondary)",
                    cursor: "pointer",
                    fontSize: "12px",
                    fontWeight: activeImageTab === idx ? 600 : 400,
                    display: "flex",
                    alignItems: "center",
                    gap: "8px"
                  }}
                >
                  <span>{img.original_filename}</span>
                  <span style={{ fontSize: "10px", padding: "2px 6px", borderRadius: "4px", backgroundColor: "rgba(255,255,255,0.06)" }}>
                    #{img.id}
                  </span>
                </button>
              ))}
            </div>

            {/* Active Micrograph Deep Analytics Panel */}
            {analysisResult.images[activeImageTab] && (() => {
              const curImg = analysisResult.images[activeImageTab];
              const overlayActive = overlayToggles[curImg.id] ?? true;

              return (
                <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                    {/* Micrograph View with Localization Bounding Box Overlay */}
                    <div style={{
                      backgroundColor: "var(--bg-canvas)",
                      border: "1px solid var(--border-default)",
                      borderRadius: "8px",
                      padding: "16px",
                      display: "flex",
                      flexDirection: "column",
                      gap: "12px"
                    }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span style={{ fontSize: "13px", fontWeight: 600 }}>Micrograph & Suspicious Region Envelope</span>
                        <button
                          onClick={() => toggleOverlay(curImg.id)}
                          style={{
                            backgroundColor: overlayActive ? "var(--accent-primary)" : "var(--bg-surface-elevated)",
                            color: overlayActive ? "#fff" : "var(--text-secondary)",
                            border: "1px solid var(--border-default)",
                            borderRadius: "4px",
                            padding: "4px 8px",
                            fontSize: "11px",
                            cursor: "pointer",
                            display: "flex",
                            alignItems: "center",
                            gap: "6px"
                          }}
                        >
                          {overlayActive ? <Eye size={13} /> : <EyeOff size={13} />}
                          <span>{overlayActive ? "Overlay: Active" : "Overlay: Off"}</span>
                        </button>
                      </div>

                      <div style={{
                        position: "relative",
                        backgroundColor: "#000",
                        borderRadius: "6px",
                        overflow: "hidden",
                        minHeight: "260px",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center"
                      }}>
                        <img
                          src={`/api/v1/images/${curImg.id}/file`}
                          alt={curImg.original_filename}
                          style={{ maxWidth: "100%", maxHeight: "320px", objectFit: "contain" }}
                          onError={(e: any) => {
                            e.target.style.display = "none";
                          }}
                        />

                        {/* Model-Derived Suspicious Region Bounding Envelope */}
                        {overlayActive && curImg.localization && curImg.localization.bounding_boxes && curImg.localization.bounding_boxes.map((box, bIdx) => (
                          <div
                            key={bIdx}
                            style={{
                              position: "absolute",
                              top: `${(box.y_min / (curImg.height || 512)) * 100}%`,
                              left: `${(box.x_min / (curImg.width || 512)) * 100}%`,
                              width: `${((box.x_max - box.x_min) / (curImg.width || 512)) * 100}%`,
                              height: `${((box.y_max - box.y_min) / (curImg.height || 512)) * 100}%`,
                              border: "2px solid #ef4444",
                              backgroundColor: "rgba(239, 68, 68, 0.2)",
                              pointerEvents: "none"
                            }}
                          >
                            <span style={{
                              position: "absolute",
                              top: "-18px",
                              left: "0",
                              backgroundColor: "#ef4444",
                              color: "#fff",
                              fontSize: "9px",
                              fontWeight: 700,
                              padding: "1px 4px",
                              borderRadius: "2px"
                            }}>
                              Model-Derived Suspicious Region
                            </span>
                          </div>
                        ))}
                      </div>

                      {/* Scientific Guardrail Caption */}
                      <div style={{ fontSize: "11px", color: "var(--text-muted)", fontStyle: "italic" }}>
                        Note: Model-derived suspicious region envelopes indicate localized quality anomaly signals. They do not constitute confirmed physical defects.
                      </div>
                    </div>

                    {/* Image-Derived Quality Indicators & Metrics */}
                    <div style={{
                      backgroundColor: "var(--bg-canvas)",
                      border: "1px solid var(--border-default)",
                      borderRadius: "8px",
                      padding: "16px",
                      display: "flex",
                      flexDirection: "column",
                      gap: "12px"
                    }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span style={{ fontSize: "13px", fontWeight: 600 }}>Image-Derived Quality-Risk Indicators</span>
                        {renderQualityBadge(curImg.quality.decision_status)}
                      </div>

                      <div style={{ overflowX: "auto" }}>
                        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "11px" }}>
                          <thead>
                            <tr style={{ borderBottom: "1px solid var(--border-default)", color: "var(--text-muted)", textAlign: "left" }}>
                              <th style={{ padding: "6px" }}>Indicator Name</th>
                              <th style={{ padding: "6px" }}>Value</th>
                              <th style={{ padding: "6px" }}>Threshold</th>
                              <th style={{ padding: "6px" }}>Risk Signal</th>
                            </tr>
                          </thead>
                          <tbody>
                            {curImg.quality.indicators.map((ind, iIdx) => (
                              <tr key={iIdx} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                                <td style={{ padding: "6px", fontWeight: 600 }}>{ind.indicator_name}</td>
                                <td style={{ padding: "6px", fontFamily: "monospace" }}>{ind.measured_value.toFixed(2)}</td>
                                <td style={{ padding: "6px", fontFamily: "monospace" }}>{ind.threshold_applied.toFixed(2)}</td>
                                <td style={{ padding: "6px" }}>
                                  {ind.is_risk_flagged ? (
                                    <span style={{ color: "#f87171", fontWeight: 700 }}>FLAGGED</span>
                                  ) : (
                                    <span style={{ color: "#34d399" }}>NOMINAL</span>
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>

                      {/* Suggested Action — Requires Scientist Review */}
                      <div style={{
                        marginTop: "auto",
                        backgroundColor: "var(--bg-surface)",
                        border: "1px solid var(--border-default)",
                        borderRadius: "6px",
                        padding: "12px"
                      }}>
                        <div style={{ fontSize: "12px", fontWeight: 700, color: "var(--accent-primary)" }}>
                          Suggested Action — Requires Scientist Review ({curImg.explanation.action_code})
                        </div>
                        <div style={{ fontSize: "12px", color: "var(--text-primary)", marginTop: "4px" }}>
                          {curImg.explanation.recommendation_summary}
                        </div>
                        {curImg.explanation.operational_parameter_targets.length > 0 && (
                          <div style={{ marginTop: "6px" }}>
                            <span style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-secondary)" }}>Operational Targets:</span>
                            <ul style={{ margin: "4px 0 0 16px", padding: 0, fontSize: "11px", color: "var(--text-secondary)" }}>
                              {curImg.explanation.operational_parameter_targets.map((tgt, tIdx) => (
                                <li key={tIdx}>{tgt}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Comparable Evidence Cohort (N=55 Cohort Context) */}
                  {curImg.evidence && curImg.evidence.comparable_items.length > 0 && (
                    <div style={{
                      backgroundColor: "var(--bg-canvas)",
                      border: "1px solid var(--border-subtle)",
                      borderRadius: "6px",
                      padding: "14px 18px",
                      display: "flex",
                      flexDirection: "column",
                      gap: "10px"
                    }}>
                      <div style={{ fontSize: "12px", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase" }}>
                        Comparable Scientific Evidence (N=55 Benchmark Cohort Context)
                      </div>
                      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "10px" }}>
                        {curImg.evidence.comparable_items.map((item, cIdx) => (
                          <div
                            key={cIdx}
                            style={{
                              backgroundColor: "var(--bg-surface)",
                              border: "1px solid var(--border-default)",
                              borderRadius: "4px",
                              padding: "10px",
                              fontSize: "11px"
                            }}
                          >
                            <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>Micrograph #{item.image_id}</div>
                            <div style={{ color: "var(--accent-cyan)", marginTop: "2px" }}>Role: {item.role}</div>
                            <div style={{ color: "var(--text-muted)", marginTop: "2px" }}>
                              Similarity: {(item.similarity_score * 100).toFixed(1)}%
                            </div>
                            {item.instrument && (
                              <div style={{ color: "var(--text-muted)", marginTop: "2px" }}>
                                {item.instrument} &bull; {item.accelerating_voltage_kv} kV
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })()}
          </div>

          {/* ============================================================ */}
          {/* 8. SCIENTIST REVIEW & CURATION ACTION TOOLBAR */}
          {/* ============================================================ */}
          <div style={{
            backgroundColor: "var(--bg-surface)",
            border: "1px solid var(--border-default)",
            borderRadius: "8px",
            padding: "20px",
            display: "flex",
            flexDirection: "column",
            gap: "16px"
          }}>
            <div>
              <h3 style={{ fontSize: "15px", fontWeight: 600, margin: 0, display: "flex", alignItems: "center", gap: "8px" }}>
                <CheckCircle2 size={18} color="var(--accent-primary)" />
                Human-in-the-Loop Curator Review & Corrective Action Routing
              </h3>
              <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "4px" }}>
                Record authoritative scientist decision into the cryptographic provenance audit trail.
              </div>
            </div>

            <div style={{ display: "flex", gap: "16px", flexWrap: "wrap", alignItems: "center" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)" }}>Target Micrograph:</span>
                <select
                  value={selectedReviewImageId || ""}
                  onChange={(e) => setSelectedReviewImageId(Number(e.target.value))}
                  style={{
                    backgroundColor: "var(--bg-canvas)",
                    border: "1px solid var(--border-default)",
                    borderRadius: "4px",
                    padding: "6px 10px",
                    color: "var(--text-primary)",
                    fontSize: "12px"
                  }}
                >
                  {analysisResult.images.map((img) => (
                    <option key={img.id} value={img.id}>
                      #{img.id} - {img.original_filename}
                    </option>
                  ))}
                </select>
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)" }}>Curator Action:</span>
                <select
                  value={curatorDecision}
                  onChange={(e) => setCuratorDecision(e.target.value)}
                  style={{
                    backgroundColor: "var(--bg-canvas)",
                    border: "1px solid var(--border-default)",
                    borderRadius: "4px",
                    padding: "6px 10px",
                    color: "var(--text-primary)",
                    fontSize: "12px",
                    fontWeight: 600
                  }}
                >
                  <option value="ACCEPT">ACCEPT (Nominal Micrograph)</option>
                  <option value="FLAG">FLAG (Flag for Quality Investigation)</option>
                  <option value="REQUEST_REACQUISITION">REQUEST_REACQUISITION (Requires Re-Scan)</option>
                  <option value="MARK_DUPLICATE">MARK_DUPLICATE (Confirm Redundant Micrograph)</option>
                  <option value="MARK_NOT_DUPLICATE">MARK_NOT_DUPLICATE (Distinct Biological Sample)</option>
                  <option value="ADD_NOTE">ADD_NOTE (Curation Note)</option>
                </select>
              </div>

              <div style={{ flex: 1, minWidth: "240px" }}>
                <input
                  type="text"
                  placeholder="Optional scientist rationale / comments..."
                  value={curatorComment}
                  onChange={(e) => setCuratorComment(e.target.value)}
                  style={{
                    width: "100%",
                    backgroundColor: "var(--bg-canvas)",
                    border: "1px solid var(--border-default)",
                    borderRadius: "4px",
                    padding: "6px 12px",
                    color: "var(--text-primary)",
                    fontSize: "12px",
                    boxSizing: "border-box"
                  }}
                />
              </div>

              <button
                onClick={handleSubmitReview}
                disabled={submittingReview || !selectedReviewImageId}
                style={{
                  backgroundColor: "var(--accent-primary)",
                  color: "#fff",
                  border: "none",
                  borderRadius: "6px",
                  padding: "8px 18px",
                  fontSize: "12px",
                  fontWeight: 600,
                  cursor: submittingReview ? "not-allowed" : "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "6px"
                }}
              >
                {submittingReview ? (
                  <span>Recording...</span>
                ) : (
                  <>
                    <Check size={14} />
                    <span>Commit Review Action</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* ============================================================ */}
          {/* 9. PROVENANCE & CRYPTOGRAPHIC AUDIT HASH PANEL */}
          {/* ============================================================ */}
          <div style={{
            backgroundColor: "var(--bg-canvas)",
            border: "1px solid var(--border-default)",
            borderRadius: "6px",
            padding: "14px 18px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "10px",
            fontSize: "11px",
            color: "var(--text-muted)"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <Hash size={14} color="var(--accent-cyan)" />
              <span>Analysis ID: <strong style={{ color: "var(--text-primary)" }}>{analysisResult.analysis_id}</strong></span>
              <span>&bull;</span>
              <span>Timestamp: {analysisResult.timestamp_utc}</span>
              <span>&bull;</span>
              <span>Representation: {analysisResult.representation}</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <ShieldCheck size={14} color="var(--accent-primary)" />
              <span>Provenance Master Seal:</span>
              <span style={{ fontFamily: "monospace", color: "var(--accent-cyan)" }}>
                {analysisResult.provenance.audit_hash}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
