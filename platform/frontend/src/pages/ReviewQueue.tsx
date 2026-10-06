import React, { useEffect, useState, useCallback } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  CheckSquare,
  Keyboard,
  Eye,
  AlertTriangle,
  Info,
  CheckCircle2,
  XCircle,
  Sparkles,
  ArrowRight,
  ArrowLeft
} from "lucide-react";
import { ApiClient, ReviewQueueItem } from "../api/client";

export const ReviewQueue: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [queue, setQueue] = useState<ReviewQueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedIndex, setSelectedIndex] = useState<number>(-1);
  const [decision, setDecision] = useState<string>("KEEP");
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<{ text: string; type: "success" | "error" } | null>(null);

  const fetchQueue = async () => {
    try {
      setLoading(true);
      const data = await ApiClient.getReviewQueue(100);
      setQueue(data);

      // Pre-select if URL param image_id provided
      const targetId = searchParams.get("image_id");
      if (targetId) {
        const idx = data.findIndex((item) => item.image_id === Number(targetId));
        if (idx !== -1) {
          setSelectedIndex(idx);
          setDecision(data[idx].algorithmic_recommendation);
        }
      } else if (data.length > 0 && selectedIndex === -1) {
        setSelectedIndex(0);
        setDecision(data[0].algorithmic_recommendation);
      }
    } catch (e: any) {
      console.error(e);
      setMessage({ text: e.message || "Failed to load triage queue", type: "error" });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, []);

  const currentItem: ReviewQueueItem | null =
    selectedIndex >= 0 && selectedIndex < queue.length ? queue[selectedIndex] : null;

  const handleSubmitReview = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!currentItem) return;

    setSubmitting(true);
    setMessage(null);
    try {
      await ApiClient.submitReview({
        image_id: currentItem.image_id,
        decision: decision as any,
        comment: comment || undefined,
      });

      setMessage({ text: `Review committed for micrograph #${currentItem.image_id} (${decision})`, type: "success" });
      setComment("");

      // Remove from queue locally and advance
      const nextQueue = queue.filter((_, i) => i !== selectedIndex);
      setQueue(nextQueue);
      if (nextQueue.length > 0) {
        const nextIdx = Math.min(selectedIndex, nextQueue.length - 1);
        setSelectedIndex(nextIdx);
        setDecision(nextQueue[nextIdx].algorithmic_recommendation);
      } else {
        setSelectedIndex(-1);
      }
    } catch (err: any) {
      setMessage({ text: "Review submission error: " + err.message, type: "error" });
    } finally {
      setSubmitting(false);
    }
  };

  // Keyboard Shortcuts Handler
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    // Only handle if not focused in textarea/input
    if (["INPUT", "TEXTAREA", "SELECT"].includes((e.target as HTMLElement).tagName)) {
      return;
    }

    if (e.key === "j" || e.key === "J") {
      // Next image
      if (queue.length > 0) {
        setSelectedIndex((prev) => {
          const next = Math.min(queue.length - 1, prev + 1);
          setDecision(queue[next].algorithmic_recommendation);
          return next;
        });
      }
    } else if (e.key === "k" || e.key === "K") {
      // Previous image
      if (queue.length > 0) {
        setSelectedIndex((prev) => {
          const next = Math.max(0, prev - 1);
          setDecision(queue[next].algorithmic_recommendation);
          return next;
        });
      }
    } else if (e.key === "d" || e.key === "D") {
      setDecision("DUPLICATE");
    } else if (e.key === "l" || e.key === "L") {
      setDecision("LOW_QUALITY");
    } else if (e.key === "n" || e.key === "N") {
      setDecision("INTERESTING_NOVEL");
    } else if (e.key === "m" || e.key === "M") {
      setDecision("KEEP");
    } else if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      handleSubmitReview();
    }
  }, [queue, selectedIndex, currentItem, decision, comment]);

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "12px" }}>
        <div>
          <h1 style={{ fontSize: "22px", fontWeight: "700", color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "10px" }}>
            <CheckSquare size={22} color="var(--accent-primary)" />
            <span>Curator Workbench & Triage Queue</span>
          </h1>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
            Diagnostic-risk prioritized operational triage queue. Rapid keyboard-assisted curation for defect inspection and anomaly validation.
          </p>
        </div>

        {/* Keyboard Shortcuts Pill */}
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          backgroundColor: "var(--bg-surface)",
          border: "1px solid var(--border-default)",
          padding: "6px 12px",
          borderRadius: "var(--radius-md)",
          fontSize: "12px",
          color: "var(--text-secondary)"
        }}>
          <Keyboard size={14} color="var(--accent-cyan)" />
          <span>Hotkeys:</span>
          <span className="font-mono" style={{ color: "var(--text-primary)" }}>[J/K] Nav</span>
          <span className="font-mono" style={{ color: "var(--text-primary)" }}>[M] Keep</span>
          <span className="font-mono" style={{ color: "var(--text-primary)" }}>[D] Dup</span>
          <span className="font-mono" style={{ color: "var(--text-primary)" }}>[L] LowQ</span>
          <span className="font-mono" style={{ color: "var(--text-primary)" }}>[N] Novel</span>
        </div>
      </div>

      {/* Scientific Limitation Disclaimer */}
      <div style={{
        padding: "10px 16px",
        borderRadius: "var(--radius-md)",
        backgroundColor: "rgba(2, 132, 199, 0.08)",
        border: "1px solid rgba(2, 132, 199, 0.2)",
        display: "flex",
        alignItems: "center",
        gap: "10px",
        fontSize: "12px",
        color: "var(--text-secondary)"
      }}>
        <Info size={16} color="var(--accent-cyan)" style={{ flexShrink: 0 }} />
        <span>
          <strong>Operational Triage Notice:</strong> Triage priority is calculated by algorithmic composite diagnostic risk
          (<code>priority = 0.5 × quality_risk + 0.3 × novelty_pct + 0.2 × redundancy_weight</code>).
          Rankings are descriptive algorithmic triage outputs and not claimed as confirmed clinical/metallurgical diagnostic labels.
        </span>
      </div>

      {message && (
        <div className={`card`} style={{
          padding: "12px 16px",
          borderLeft: `4px solid ${message.type === "success" ? "var(--status-nominal)" : "var(--status-risk)"}`,
          color: message.type === "success" ? "var(--status-nominal)" : "var(--status-risk)",
          fontSize: "13px"
        }}>
          {message.text}
        </div>
      )}

      {/* Main Two-Column Workbench Layout */}
      <div style={{ display: "grid", gridTemplateColumns: currentItem ? "1.1fr 0.9fr" : "1fr", gap: "20px" }}>
        {/* Left: Triage Table */}
        <div className="card" style={{ padding: "0", overflow: "hidden" }}>
          <div style={{ padding: "14px 16px", backgroundColor: "var(--bg-surface-elevated)", borderBottom: "1px solid var(--border-default)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)" }}>
              Active Queue ({queue.length} pending)
            </span>
            <button onClick={fetchQueue} className="btn btn-secondary btn-sm">
              Refresh Queue
            </button>
          </div>

          <div className="table-container">
            <table className="scientific-table">
              <thead>
                <tr>
                  <th>Priority</th>
                  <th>ID</th>
                  <th>Filename</th>
                  <th>Quality Risk</th>
                  <th>Redundancy</th>
                  <th>Novelty %</th>
                  <th>Algorithmic Rec</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan={8} style={{ padding: "30px", textAlign: "center", color: "var(--text-muted)" }}>Loading queue...</td></tr>
                ) : queue.length === 0 ? (
                  <tr>
                    <td colSpan={8} style={{ padding: "40px", textAlign: "center", color: "var(--status-nominal)" }}>
                      <CheckCircle2 size={32} style={{ margin: "0 auto 8px auto", display: "block" }} />
                      All triage candidates reviewed! No pending items in operational queue.
                    </td>
                  </tr>
                ) : (
                  queue.map((item, idx) => {
                    const isSelected = idx === selectedIndex;
                    return (
                      <tr
                        key={item.image_id}
                        onClick={() => {
                          setSelectedIndex(idx);
                          setDecision(item.algorithmic_recommendation);
                        }}
                        style={{
                          backgroundColor: isSelected ? "var(--bg-surface-active)" : undefined,
                          cursor: "pointer"
                        }}
                      >
                        <td className="font-mono" style={{ fontWeight: 700, color: "var(--accent-primary)" }}>
                          {item.priority.toFixed(3)}
                        </td>
                        <td className="font-mono">#{item.image_id}</td>
                        <td style={{ fontWeight: 600, maxWidth: "160px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }} title={item.original_filename}>
                          {item.original_filename}
                        </td>
                        <td>
                          <span className={`badge ${item.composite_quality_risk >= 0.60 ? "badge-risk" : "badge-nominal"}`}>
                            {(item.composite_quality_risk * 100).toFixed(1)}%
                          </span>
                        </td>
                        <td>
                          <span className={`badge ${item.duplicate_status === "NO_DECLARED_REDUNDANCY_DETECTED" ? "badge-nominal" : "badge-warning"}`}>
                            {item.duplicate_status === "NO_DECLARED_REDUNDANCY_DETECTED" ? "UNIQUE" : "REDUNDANT"}
                          </span>
                        </td>
                        <td className="font-mono">{item.novelty_percentile.toFixed(1)}%</td>
                        <td>
                          <span className={`badge ${item.algorithmic_recommendation === "KEEP" ? "badge-nominal" : "badge-warning"}`}>
                            {item.algorithmic_recommendation}
                          </span>
                        </td>
                        <td>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedIndex(idx);
                              setDecision(item.algorithmic_recommendation);
                            }}
                            className="btn btn-secondary btn-sm"
                          >
                            Inspect
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right: Inspection & Decision Panel */}
        {currentItem && (
          <div className="card" style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h2 style={{ fontSize: "16px", fontWeight: 700, color: "var(--text-primary)" }}>
                Curate Micrograph #{currentItem.image_id}
              </h2>
              <div style={{ display: "flex", gap: "6px" }}>
                <button
                  disabled={selectedIndex <= 0}
                  onClick={() => {
                    const prev = Math.max(0, selectedIndex - 1);
                    setSelectedIndex(prev);
                    setDecision(queue[prev].algorithmic_recommendation);
                  }}
                  className="btn btn-secondary btn-sm"
                  title="Previous (K)"
                >
                  <ArrowLeft size={14} />
                </button>
                <button
                  disabled={selectedIndex >= queue.length - 1}
                  onClick={() => {
                    const next = Math.min(queue.length - 1, selectedIndex + 1);
                    setSelectedIndex(next);
                    setDecision(queue[next].algorithmic_recommendation);
                  }}
                  className="btn btn-secondary btn-sm"
                  title="Next (J)"
                >
                  <ArrowRight size={14} />
                </button>
              </div>
            </div>

            {/* Micrograph Preview */}
            <div style={{ height: "220px", backgroundColor: "#000", borderRadius: "var(--radius-md)", overflow: "hidden", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <img
                src={ApiClient.getImageThumbnailUrl(currentItem.image_id)}
                alt={currentItem.original_filename}
                style={{ width: "100%", height: "100%", objectFit: "contain" }}
                onError={(e: any) => {
                  e.target.src = ApiClient.getImageUrl(currentItem.image_id);
                }}
              />
            </div>

            <div style={{ fontSize: "12px", color: "var(--text-secondary)", display: "flex", justifyContent: "space-between" }}>
              <span className="font-mono">{currentItem.original_filename}</span>
              <Link to={`/images/${currentItem.image_id}`} target="_blank" className="btn btn-secondary btn-sm" style={{ padding: "2px 8px" }}>
                <Eye size={12} /> Full Profile
              </Link>
            </div>

            {/* Diagnostics Summary Card */}
            <div style={{ padding: "12px", backgroundColor: "var(--bg-canvas)", borderRadius: "var(--radius-md)", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", fontSize: "12px" }}>
              <div>
                <span style={{ color: "var(--text-muted)", display: "block" }}>Composite Risk:</span>
                <span className="font-mono" style={{ fontWeight: 600, color: currentItem.composite_quality_risk >= 0.60 ? "var(--status-risk)" : "var(--status-nominal)" }}>
                  {(currentItem.composite_quality_risk * 100).toFixed(1)}% ({currentItem.quality_label})
                </span>
              </div>
              <div>
                <span style={{ color: "var(--text-muted)", display: "block" }}>Redundancy:</span>
                <span className="font-mono" style={{ fontWeight: 600 }}>{currentItem.duplicate_status}</span>
              </div>
              <div>
                <span style={{ color: "var(--text-muted)", display: "block" }}>Relative Novelty:</span>
                <span className="font-mono" style={{ fontWeight: 600, color: "var(--accent-cyan)" }}>
                  {currentItem.novelty_percentile.toFixed(1)}th percentile
                </span>
              </div>
              <div>
                <span style={{ color: "var(--text-muted)", display: "block" }}>Algorithmic Rec:</span>
                <span className="badge badge-info">{currentItem.algorithmic_recommendation}</span>
              </div>
            </div>

            {/* Decision Submission Form */}
            <form onSubmit={handleSubmitReview} style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "6px" }}>
                  Curator Verdict *
                </label>
                <select
                  value={decision}
                  onChange={(e) => setDecision(e.target.value)}
                  className="input-field"
                >
                  <option value="KEEP">KEEP — Retain verified micrograph in repository</option>
                  <option value="REVIEW_LATER">REVIEW_LATER — Defer for specialist panel</option>
                  <option value="DUPLICATE">DUPLICATE — Mark as redundant acquisition</option>
                  <option value="LOW_QUALITY">LOW_QUALITY — Mark as severe quality defect</option>
                  <option value="INTERESTING_NOVEL">INTERESTING_NOVEL — Flag novel microstructure</option>
                  <option value="INCORRECT_METADATA">INCORRECT_METADATA — Flag metadata discrepancy</option>
                </select>
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "6px" }}>
                  Curator Rationale / Observation Notes
                </label>
                <textarea
                  rows={3}
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  placeholder="Document curator rationale / evidence-based justification (e.g. defocus blur verified, identical inclusion cluster)..."
                  className="input-field"
                  style={{ resize: "vertical" }}
                />
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="btn btn-primary"
                style={{ width: "100%", height: "40px" }}
              >
                {submitting ? "Committing Verdict..." : `Commit Decision (${decision})`}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};
