import React from "react";

export const Footer: React.FC = () => {
  return (
    <footer style={{
      borderTop: "1px solid var(--border-default)",
      backgroundColor: "var(--bg-surface)",
      padding: "10px 32px",
      fontSize: "12px",
      color: "var(--text-muted)",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      zIndex: 10
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        <div style={{ width: "7px", height: "7px", borderRadius: "50%", backgroundColor: "var(--status-nominal)" }} />
        <span style={{ fontWeight: 600, color: "var(--text-secondary)" }}>SciData Platform v1.0.0</span>
        <span>&bull;</span>
        <span>AI-Powered Scientific Image Data Management Platform</span>
      </div>

      <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>
        <span>IEEE Benchmark Evidence Architecture &bull; 2026</span>
      </div>
    </footer>
  );
};
