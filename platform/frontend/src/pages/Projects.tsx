import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Layers,
  LayoutGrid,
  List,
  Search,
  Plus,
  Filter,
  Eye,
  Microscope,
  CheckCircle2,
  AlertTriangle,
  FileDown
} from "lucide-react";
import { Project } from "../types";
import { ApiClient } from "../api/client";

export const Projects: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<number | undefined>(undefined);
  const [images, setImages] = useState<any[]>([]);
  const [totalImages, setTotalImages] = useState(0);
  const [viewMode, setViewMode] = useState<"grid" | "table">("grid");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);

  // New Project Form State
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newName, setNewName] = useState("");
  const [newDescription, setNewDescription] = useState("");

  const loadData = async () => {
    setLoading(true);
    try {
      const projData = await ApiClient.getProjects();
      setProjects(projData);

      const imgData = await ApiClient.getImages(selectedProjectId, statusFilter || undefined, 100, 0);
      setImages(imgData.items || []);
      setTotalImages(imgData.total || 0);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedProjectId, statusFilter]);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName) return;
    try {
      await ApiClient.createProject({ name: newName, description: newDescription });
      setNewName("");
      setNewDescription("");
      setShowCreateModal(false);
      loadData();
    } catch (err: any) {
      alert("Failed to create project: " + err.message);
    }
  };

  const filteredImages = images.filter((img) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      img.original_filename?.toLowerCase().includes(q) ||
      img.id.toString().includes(q) ||
      img.microscope?.toLowerCase().includes(q)
    );
  });

  const exportMetadataJson = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(filteredImages, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `scidata_micrographs_export_${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Top Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "16px" }}>
        <div>
          <h1 style={{ fontSize: "22px", fontWeight: "700", color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "10px" }}>
            <Layers size={22} color="var(--accent-primary)" />
            <span>Dataset & Micrograph Explorer</span>
          </h1>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
            Explore scientific imaging collections, inspect acquisition metadata, and filter by diagnostic risk indicators.
          </p>
        </div>

        <div style={{ display: "flex", gap: "10px" }}>
          <button onClick={exportMetadataJson} className="btn btn-secondary btn-sm">
            <FileDown size={14} />
            <span>Export Metadata JSON</span>
          </button>
          <button onClick={() => setShowCreateModal(true)} className="btn btn-primary btn-sm">
            <Plus size={14} />
            <span>New Project</span>
          </button>
        </div>
      </div>

      {/* Control Bar: Filters, Search, and View Mode Toggle */}
      <div className="card" style={{ padding: "16px", display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "12px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap", flex: 1 }}>
          {/* Project Selector */}
          <select
            value={selectedProjectId || ""}
            onChange={(e) => setSelectedProjectId(e.target.value ? Number(e.target.value) : undefined)}
            className="input-field"
            style={{ width: "auto", minWidth: "180px" }}
          >
            <option value="">All Projects ({projects.length})</option>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.image_count} imgs)
              </option>
            ))}
          </select>

          {/* Processing Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input-field"
            style={{ width: "auto", minWidth: "160px" }}
          >
            <option value="">All Statuses</option>
            <option value="VERIFIED">VERIFIED</option>
            <option value="READY">READY</option>
            <option value="FLAGGED">FLAGGED</option>
            <option value="REVIEWED">REVIEWED</option>
          </select>

          {/* Search Box */}
          <div style={{ position: "relative", minWidth: "220px", flex: 1, maxWidth: "360px" }}>
            <Search size={14} color="var(--text-muted)" style={{ position: "absolute", left: "10px", top: "11px" }} />
            <input
              type="text"
              placeholder="Search filename or ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input-field"
              style={{ paddingLeft: "32px" }}
            />
          </div>
        </div>

        {/* View Mode Toggle */}
        <div style={{ display: "flex", alignItems: "center", gap: "4px", backgroundColor: "var(--bg-canvas)", padding: "4px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-default)" }}>
          <button
            onClick={() => setViewMode("grid")}
            className="btn btn-sm"
            style={{
              backgroundColor: viewMode === "grid" ? "var(--bg-surface-elevated)" : "transparent",
              color: viewMode === "grid" ? "var(--accent-primary)" : "var(--text-muted)",
              padding: "6px 10px"
            }}
            title="Grid View"
          >
            <LayoutGrid size={16} />
          </button>
          <button
            onClick={() => setViewMode("table")}
            className="btn btn-sm"
            style={{
              backgroundColor: viewMode === "table" ? "var(--bg-surface-elevated)" : "transparent",
              color: viewMode === "table" ? "var(--accent-primary)" : "var(--text-muted)",
              padding: "6px 10px"
            }}
            title="Table View"
          >
            <List size={16} />
          </button>
        </div>
      </div>

      {/* Image Content Container */}
      {loading ? (
        <div style={{ padding: "40px", textAlign: "center", color: "var(--text-muted)" }}>
          Loading micrographs...
        </div>
      ) : filteredImages.length === 0 ? (
        <div className="card" style={{ padding: "40px", textAlign: "center" }}>
          <Microscope size={40} color="var(--text-muted)" style={{ margin: "0 auto 12px auto" }} />
          <h3 style={{ fontSize: "16px", color: "var(--text-primary)", marginBottom: "4px" }}>No Micrographs Found</h3>
          <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginBottom: "16px" }}>
            No images match your active filters or search query.
          </p>
          <Link to="/upload" className="btn btn-primary btn-sm">
            Ingest New Images
          </Link>
        </div>
      ) : viewMode === "grid" ? (
        /* Grid View */
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))",
          gap: "16px"
        }}>
          {filteredImages.map((img) => (
            <div key={img.id} className="card" style={{ padding: "0", overflow: "hidden", display: "flex", flexDirection: "column" }}>
              <div style={{
                height: "170px",
                backgroundColor: "#000000",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                position: "relative",
                overflow: "hidden"
              }}>
                <img
                  src={ApiClient.getImageThumbnailUrl(img.id)}
                  alt={img.original_filename}
                  style={{ width: "100%", height: "100%", objectFit: "contain" }}
                  onError={(e: any) => {
                    e.target.style.display = "none";
                    if (e.target.nextSibling) e.target.nextSibling.style.display = "flex";
                  }}
                />
                <div style={{
                  display: "none",
                  alignItems: "center",
                  justifyContent: "center",
                  width: "100%",
                  height: "100%",
                  color: "var(--text-muted)",
                  fontSize: "12px",
                  gap: "6px"
                }}>
                  <Microscope size={24} />
                  <span>Micrograph Preview</span>
                </div>

                {/* Status Badges Overlay */}
                <div style={{ position: "absolute", top: "8px", right: "8px", display: "flex", gap: "6px" }}>
                  {img.quality_label === "RISK_FLAGGED" && (
                    <span className="badge badge-risk">Risk Flagged</span>
                  )}
                  {img.duplicate_status !== "NO_DECLARED_REDUNDANCY_DETECTED" && (
                    <span className="badge badge-warning">Redundant</span>
                  )}
                </div>
              </div>

              <div style={{ padding: "14px", display: "flex", flexDirection: "column", gap: "8px", flex: 1 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>ID #{img.id}</span>
                  <span className="badge badge-info">{img.processing_status}</span>
                </div>

                <div style={{
                  fontSize: "13px",
                  fontWeight: 600,
                  color: "var(--text-primary)",
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis"
                }} title={img.original_filename}>
                  {img.original_filename}
                </div>

                <div style={{ fontSize: "11px", color: "var(--text-secondary)", display: "flex", justifyContent: "space-between" }}>
                  <span>Resolution:</span>
                  <span className="font-mono">{img.width} × {img.height}</span>
                </div>

                <div style={{ fontSize: "11px", color: "var(--text-secondary)", display: "flex", justifyContent: "space-between" }}>
                  <span>Quality Risk:</span>
                  <span className="font-mono" style={{
                    color: img.composite_quality_risk >= 0.60 ? "var(--status-risk)" : "var(--status-nominal)"
                  }}>
                    {(img.composite_quality_risk * 100).toFixed(1)}%
                  </span>
                </div>

                <div style={{ marginTop: "auto", paddingTop: "10px", borderTop: "1px solid var(--border-subtle)", display: "flex", justifyContent: "space-between" }}>
                  <Link to={`/images/${img.id}`} className="btn btn-secondary btn-sm" style={{ flex: 1, marginRight: "6px" }}>
                    <Eye size={12} />
                    <span>Inspect</span>
                  </Link>
                  <Link to={`/search?query_id=${img.id}`} className="btn btn-primary btn-sm" style={{ flex: 1 }}>
                    <Search size={12} />
                    <span>Find Similar</span>
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* Table View */
        <div className="table-container">
          <table className="scientific-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Filename</th>
                <th>Resolution</th>
                <th>Status</th>
                <th>Quality Risk</th>
                <th>Redundancy Status</th>
                <th>Microscope</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredImages.map((img) => (
                <tr key={img.id}>
                  <td className="font-mono" style={{ color: "var(--text-muted)" }}>#{img.id}</td>
                  <td style={{ fontWeight: 600 }}>{img.original_filename}</td>
                  <td className="font-mono">{img.width} × {img.height}</td>
                  <td>
                    <span className={`badge ${
                      img.processing_status === "VERIFIED" ? "badge-nominal" :
                      img.processing_status === "FLAGGED" ? "badge-risk" : "badge-info"
                    }`}>
                      {img.processing_status}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${img.composite_quality_risk >= 0.60 ? "badge-risk" : "badge-nominal"}`}>
                      {(img.composite_quality_risk * 100).toFixed(1)}% ({img.quality_label})
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${
                      img.duplicate_status === "NO_DECLARED_REDUNDANCY_DETECTED" ? "badge-nominal" : "badge-warning"
                    }`}>
                      {img.duplicate_status === "NO_DECLARED_REDUNDANCY_DETECTED" ? "UNIQUE" : "REDUNDANT"}
                    </span>
                  </td>
                  <td>{img.microscope || "—"}</td>
                  <td>
                    <div style={{ display: "flex", gap: "6px" }}>
                      <Link to={`/images/${img.id}`} className="btn btn-secondary btn-sm">
                        <Eye size={12} />
                        <span>Inspect</span>
                      </Link>
                      <Link to={`/search?query_id=${img.id}`} className="btn btn-primary btn-sm">
                        <Search size={12} />
                        <span>Search</span>
                      </Link>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal for Creating New Project */}
      {showCreateModal && (
        <div style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: "rgba(0, 0, 0, 0.75)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 100,
          backdropFilter: "blur(4px)"
        }}>
          <div className="card" style={{ width: "460px", maxWidth: "90%", padding: "24px" }}>
            <h2 style={{ fontSize: "18px", fontWeight: "700", color: "var(--text-primary)", marginBottom: "16px" }}>
              Create New Research Project
            </h2>
            <form onSubmit={handleCreateProject} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              <div>
                <label style={{ display: "block", fontSize: "12px", color: "var(--text-secondary)", marginBottom: "6px" }}>
                  Project Name *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. HCCI Alloy Heat-Treatment Series"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="input-field"
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "12px", color: "var(--text-secondary)", marginBottom: "6px" }}>
                  Description
                </label>
                <textarea
                  rows={3}
                  placeholder="Acquisition instrument, accelerating voltages, or study notes..."
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  className="input-field"
                  style={{ resize: "vertical" }}
                />
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "8px" }}>
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="btn btn-secondary btn-sm"
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary btn-sm">
                  Create Project
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
