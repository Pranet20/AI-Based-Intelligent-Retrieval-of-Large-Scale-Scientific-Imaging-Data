import React from "react";
import { Link, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Layers,
  Search,
  CheckSquare,
  UploadCloud,
  Cpu,
  Activity,
  FileText
} from "lucide-react";

export const Sidebar: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { label: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
    { label: "Dataset Explorer", path: "/explorer", icon: Layers, aliases: ["/projects"] },
    { label: "Vector Search", path: "/search", icon: Search },
    { label: "Curator Workbench", path: "/reviews", icon: CheckSquare, aliases: ["/curation"] },
    { label: "Ingest Micrographs", path: "/upload", icon: UploadCloud },
    { label: "Model Registry", path: "/models", icon: Cpu },
    { label: "System Health & Audit", path: "/health", icon: Activity, aliases: ["/settings"] },
  ];

  return (
    <aside style={{
      width: "var(--sidebar-width)",
      backgroundColor: "var(--bg-surface)",
      borderRight: "1px solid var(--border-default)",
      display: "flex",
      flexDirection: "column",
      padding: "24px 0",
      minHeight: "calc(100vh - var(--header-height))"
    }}>
      <div style={{
        padding: "0 20px 12px 20px",
        fontSize: "11px",
        fontWeight: 700,
        textTransform: "uppercase",
        letterSpacing: "0.8px",
        color: "var(--text-muted)"
      }}>
        Scientific Platform
      </div>

      <nav style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
        {navItems.map((item) => {
          const isCurrent =
            location.pathname === item.path ||
            (item.aliases && item.aliases.some((a) => location.pathname.startsWith(a))) ||
            (item.path !== "/dashboard" && location.pathname.startsWith(item.path));

          const Icon = item.icon;

          return (
            <Link
              key={item.path}
              to={item.path}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "12px",
                padding: "10px 20px",
                color: isCurrent ? "var(--text-primary)" : "var(--text-secondary)",
                backgroundColor: isCurrent ? "var(--bg-surface-elevated)" : "transparent",
                borderLeft: isCurrent ? "3px solid var(--accent-primary)" : "3px solid transparent",
                fontSize: "13px",
                fontWeight: isCurrent ? 600 : 500,
                transition: "all var(--transition-fast)"
              }}
            >
              <Icon size={18} color={isCurrent ? "var(--accent-primary)" : "var(--text-muted)"} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div style={{
        marginTop: "auto",
        padding: "16px 20px",
        borderTop: "1px solid var(--border-subtle)",
        display: "flex",
        flexDirection: "column",
        gap: "6px"
      }}>
        <div style={{ fontSize: "11px", color: "var(--text-muted)", display: "flex", justifyContent: "space-between" }}>
          <span>Protocol:</span>
          <span className="font-mono" style={{ color: "var(--accent-cyan)" }}>HCCI + Carinthia</span>
        </div>
        <div style={{ fontSize: "11px", color: "var(--text-muted)", display: "flex", justifyContent: "space-between" }}>
          <span>Architecture:</span>
          <span className="font-mono">DINOv2 ViT-S/14</span>
        </div>
        <div style={{ fontSize: "11px", color: "var(--text-muted)", display: "flex", justifyContent: "space-between" }}>
          <span>State:</span>
          <span style={{ color: "var(--status-nominal)", fontWeight: 600 }}>Frozen v1.0.0</span>
        </div>
      </div>
    </aside>
  );
};
