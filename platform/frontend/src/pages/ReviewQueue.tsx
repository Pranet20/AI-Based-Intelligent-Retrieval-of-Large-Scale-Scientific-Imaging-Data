import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

interface ReviewQueueItem {
  image_id: number;
  original_filename: string;
  duplicate_status: string;
  composite_quality_risk: number;
  quality_label: string;
  novelty_score: number;
  novelty_percentile: number;
  priority: number;
  algorithmic_recommendation: string;
  microscope?: string;
}

export const ReviewQueue: React.FC = () => {
  const [queue, setQueue] = useState<ReviewQueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedImage, setSelectedImage] = useState<ReviewQueueItem | null>(null);
  const [decision, setDecision] = useState("KEEP");
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const fetchQueue = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/curation/review-queue");
      if (res.ok) {
        const data = await res.json();
        setQueue(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, []);

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedImage) return;

    setSubmitting(true);
    try {
      const token = localStorage.getItem("scidata_token");
      const res = await fetch("http://localhost:8000/api/v1/curation/reviews", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : "",
        },
        body: JSON.stringify({
          image_id: selectedImage.image_id,
          decision,
          comment,
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Review submission failed");
      }

      setSelectedImage(null);
      setComment("");
      fetchQueue();
    } catch (err: any) {
      alert("Error submitting review: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <div>
        <h1 style={{ fontSize: "24px", fontWeight: "700", color: "#0f172a" }}>Curation Review Queue</h1>
        <p style={{ fontSize: "14px", color: "#64748b" }}>
          Human-in-the-loop triage prioritized by composite diagnostic risk: quality defects, redundancy alerts, and high-novelty micrographs.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: selectedImage ? "1fr 400px" : "1fr", gap: "24px" }}>
        {/* Table */}
        <div style={{ backgroundColor: "#ffffff", borderRadius: "8px", border: "1px solid #e2e8f0", overflow: "hidden" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "14px" }}>
            <thead>
              <tr style={{ backgroundColor: "#f8fafc", borderBottom: "1px solid #e2e8f0", textAlign: "left", color: "#64748b" }}>
                <th style={{ padding: "10px 14px" }}>Priority</th>
                <th style={{ padding: "10px 14px" }}>Image ID</th>
                <th style={{ padding: "10px 14px" }}>Filename</th>
                <th style={{ padding: "10px 14px" }}>Quality Risk</th>
                <th style={{ padding: "10px 14px" }}>Redundancy</th>
                <th style={{ padding: "10px 14px" }}>Novelty %</th>
                <th style={{ padding: "10px 14px" }}>Recommendation</th>
                <th style={{ padding: "10px 14px" }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={8} style={{ padding: "24px", textAlign: "center", color: "#64748b" }}>Loading review queue...</td></tr>
              ) : queue.length === 0 ? (
                <tr><td colSpan={8} style={{ padding: "24px", textAlign: "center", color: "#16a34a" }}>All micrographs reviewed! No items pending.</td></tr>
              ) : (
                queue.map((item) => (
                  <tr key={item.image_id} style={{ borderBottom: "1px solid #f1f5f9" }}>
                    <td style={{ padding: "10px 14px", fontWeight: "700", color: "#ea580c" }}>
                      {item.priority.toFixed(3)}
                    </td>
                    <td style={{ padding: "10px 14px" }}>
                      <Link to={`/images/${item.image_id}`} style={{ color: "#2563eb", fontWeight: "600" }}>
                        #{item.image_id}
                      </Link>
                    </td>
                    <td style={{ padding: "10px 14px" }}>{item.original_filename}</td>
                    <td style={{ padding: "10px 14px" }}>
                      <span style={{
                        fontSize: "12px",
                        padding: "2px 6px",
                        borderRadius: "4px",
                        backgroundColor: item.quality_label === "NOMINAL" ? "#dcfce7" : "#fee2e2",
                        color: item.quality_label === "NOMINAL" ? "#166534" : "#991b1b"
                      }}>
                        {item.composite_quality_risk.toFixed(3)}
                      </span>
                    </td>
                    <td style={{ padding: "10px 14px", fontSize: "12px" }}>
                      {item.duplicate_status === "NO_DECLARED_REDUNDANCY_DETECTED" ? "None" : item.duplicate_status}
                    </td>
                    <td style={{ padding: "10px 14px" }}>{item.novelty_percentile.toFixed(1)}%</td>
                    <td style={{ padding: "10px 14px", fontWeight: "600" }}>
                      <span style={{
                        fontSize: "12px",
                        padding: "2px 8px",
                        borderRadius: "4px",
                        backgroundColor: item.algorithmic_recommendation === "KEEP" ? "#f1f5f9" : "#fef3c7",
                        color: item.algorithmic_recommendation === "KEEP" ? "#475569" : "#92400e"
                      }}>
                        {item.algorithmic_recommendation}
                      </span>
                    </td>
                    <td style={{ padding: "10px 14px" }}>
                      <button
                        onClick={() => {
                          setSelectedImage(item);
                          setDecision(item.algorithmic_recommendation);
                        }}
                        style={{
                          padding: "4px 10px",
                          backgroundColor: "#3b82f6",
                          color: "#ffffff",
                          border: "none",
                          borderRadius: "4px",
                          fontSize: "12px",
                          cursor: "pointer"
                        }}
                      >
                        Review
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Modal / Sidebar Review Panel */}
        {selectedImage && (
          <div style={{
            backgroundColor: "#ffffff",
            padding: "20px",
            borderRadius: "8px",
            border: "1px solid #cbd5e1",
            boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)"
          }}>
            <h3 style={{ fontSize: "16px", fontWeight: "700", marginBottom: "8px", color: "#0f172a" }}>
              Submit Review: #{selectedImage.image_id}
            </h3>
            <p style={{ fontSize: "12px", color: "#64748b", marginBottom: "16px" }}>
              File: {selectedImage.original_filename}
            </p>

            <form onSubmit={handleSubmitReview} style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "#334155", marginBottom: "4px" }}>
                  Curator Decision
                </label>
                <select
                  value={decision}
                  onChange={(e) => setDecision(e.target.value)}
                  style={{ width: "100%", padding: "8px", border: "1px solid #cbd5e1", borderRadius: "4px", fontSize: "13px" }}
                >
                  <option value="KEEP">KEEP (Retain in active repository)</option>
                  <option value="REVIEW_LATER">REVIEW_LATER (Defer decision)</option>
                  <option value="DUPLICATE">DUPLICATE (Flag redundant record)</option>
                  <option value="LOW_QUALITY">LOW_QUALITY (Quality risk verified)</option>
                  <option value="INTERESTING_NOVEL">INTERESTING_NOVEL (Novel microstructure)</option>
                  <option value="INCORRECT_METADATA">INCORRECT_METADATA (Metadata audit needed)</option>
                </select>
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "#334155", marginBottom: "4px" }}>
                  Curator Rationale / Notes
                </label>
                <textarea
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  rows={4}
                  placeholder="Document specific physical reasons for the decision..."
                  style={{ width: "100%", padding: "8px", border: "1px solid #cbd5e1", borderRadius: "4px", fontSize: "13px" }}
                />
              </div>

              <div style={{ display: "flex", gap: "8px", marginTop: "8px" }}>
                <button
                  type="submit"
                  disabled={submitting}
                  style={{
                    flex: 1,
                    padding: "8px 16px",
                    backgroundColor: "#16a34a",
                    color: "#ffffff",
                    border: "none",
                    borderRadius: "4px",
                    fontWeight: "600",
                    cursor: submitting ? "not-allowed" : "pointer",
                    fontSize: "13px"
                  }}
                >
                  {submitting ? "Saving..." : "Commit Decision"}
                </button>
                <button
                  type="button"
                  onClick={() => setSelectedImage(null)}
                  style={{
                    padding: "8px 14px",
                    backgroundColor: "#f1f5f9",
                    color: "#475569",
                    border: "1px solid #cbd5e1",
                    borderRadius: "4px",
                    cursor: "pointer",
                    fontSize: "13px"
                  }}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};
