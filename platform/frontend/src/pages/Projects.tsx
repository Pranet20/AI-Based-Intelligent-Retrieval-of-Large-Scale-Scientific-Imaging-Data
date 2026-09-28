import React, { useEffect, useState } from "react";
import { Project } from "../types";
import { ApiClient } from "../api/client";

export const Projects: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchProjects = async () => {
    try {
      const data = await ApiClient.getProjects();
      setProjects(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name) return;
    try {
      await ApiClient.createProject({ name, description });
      setName("");
      setDescription("");
      fetchProjects();
    } catch (e: any) {
      alert("Error creating project: " + e.message);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <div>
        <h1 style={{ fontSize: "24px", fontWeight: "700", color: "#0f172a" }}>Research Projects</h1>
        <p style={{ fontSize: "14px", color: "#64748b" }}>
          Isolate micrographs by dataset, microscope instrument, or research campaign.
        </p>
      </div>

      <div style={{
        backgroundColor: "#ffffff",
        padding: "20px",
        borderRadius: "8px",
        border: "1px solid #e2e8f0"
      }}>
        <h3 style={{ fontSize: "15px", fontWeight: "600", marginBottom: "12px", color: "#0f172a" }}>
          Create New Project
        </h3>
        <form onSubmit={handleCreate} style={{ display: "flex", gap: "12px", alignItems: "flex-end" }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: "block", fontSize: "12px", fontWeight: "500", color: "#475569", marginBottom: "4px" }}>
              Project Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. HCCI Steel Inclusions"
              required
              style={{ width: "100%", padding: "8px 12px", border: "1px solid #cbd5e1", borderRadius: "4px", fontSize: "14px" }}
            />
          </div>
          <div style={{ flex: 2 }}>
            <label style={{ display: "block", fontSize: "12px", fontWeight: "500", color: "#475569", marginBottom: "4px" }}>
              Description
            </label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional description of dataset & instrument configuration"
              style={{ width: "100%", padding: "8px 12px", border: "1px solid #cbd5e1", borderRadius: "4px", fontSize: "14px" }}
            />
          </div>
          <button
            type="submit"
            style={{
              padding: "9px 18px",
              backgroundColor: "#2563eb",
              color: "#ffffff",
              border: "none",
              borderRadius: "4px",
              fontWeight: "600",
              cursor: "pointer",
              fontSize: "14px"
            }}
          >
            Create
          </button>
        </form>
      </div>

      <div style={{
        backgroundColor: "#ffffff",
        borderRadius: "8px",
        border: "1px solid #e2e8f0",
        overflow: "hidden"
      }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "14px" }}>
          <thead>
            <tr style={{ backgroundColor: "#f8fafc", borderBottom: "1px solid #e2e8f0", textAlign: "left", color: "#64748b" }}>
              <th style={{ padding: "12px 16px" }}>Project ID</th>
              <th style={{ padding: "12px 16px" }}>Name</th>
              <th style={{ padding: "12px 16px" }}>Description</th>
              <th style={{ padding: "12px 16px" }}>Images</th>
              <th style={{ padding: "12px 16px" }}>Created</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={5} style={{ padding: "24px", textAlign: "center", color: "#64748b" }}>Loading projects...</td></tr>
            ) : projects.length === 0 ? (
              <tr><td colSpan={5} style={{ padding: "24px", textAlign: "center", color: "#64748b" }}>No projects registered yet.</td></tr>
            ) : (
              projects.map((p) => (
                <tr key={p.id} style={{ borderBottom: "1px solid #f1f5f9" }}>
                  <td style={{ padding: "12px 16px", color: "#64748b" }}>#{p.id}</td>
                  <td style={{ padding: "12px 16px", fontWeight: "600", color: "#0f172a" }}>{p.name}</td>
                  <td style={{ padding: "12px 16px", color: "#475569" }}>{p.description || "—"}</td>
                  <td style={{ padding: "12px 16px", color: "#0284c7", fontWeight: "600" }}>{p.image_count}</td>
                  <td style={{ padding: "12px 16px", color: "#64748b" }}>{new Date(p.created_at).toLocaleDateString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
