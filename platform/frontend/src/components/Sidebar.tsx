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
  LogOut,
  User as UserIcon,
  Shield,
  GitCompare
} from "lucide-react";

interface SidebarProps {
  user?: any;
  onLogout?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ user, onLogout }) => {
  const location = useLocation();

  const navItems = [
    { label: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
    { label: "Dataset Explorer", path: "/explorer", icon: Layers, aliases: ["/projects"] },
    { label: "Vector Search", path: "/search", icon: Search },
    { label: "Multi-Image Analysis", path: "/multi-image", icon: GitCompare },
    { label: "Curator Workbench", path: "/reviews", icon: CheckSquare, aliases: ["/curation", "/workbench"] },
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
      padding: "20px 0 16px 0",
      minHeight: "calc(100vh - var(--header-height))",
      boxSizing: "border-box"
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

      <nav style={{ display: "flex", flexDirection: "column", gap: "3px" }}>
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

      {/* Platform Specification Metadata */}
      <div style={{
        marginTop: "auto",
        padding: "14px 20px",
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

      {/* Sidebar Bottom Footer: Active User & Sign Out Section */}
      <div style={{
        padding: "16px 20px 8px 20px",
        borderTop: "1px solid var(--border-default)",
        backgroundColor: "var(--bg-canvas)",
        margin: "0 10px 4px 10px",
        borderRadius: "var(--radius-md)"
      }}>
        {user ? (
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "12px" }}>
              <div style={{
                position: "relative",
                width: "34px",
                height: "34px",
                borderRadius: "var(--radius-full)",
                background: "linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-cyan) 100%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#ffffff",
                fontWeight: 700,
                fontSize: "14px",
                flexShrink: 0
              }}>
                {user.username ? user.username.charAt(0).toUpperCase() : "U"}
                <span style={{
                  position: "absolute",
                  bottom: "0",
                  right: "0",
                  width: "9px",
                  height: "9px",
                  borderRadius: "50%",
                  backgroundColor: "var(--status-nominal)",
                  border: "2px solid var(--bg-canvas)"
                }} />
              </div>

              <div style={{ overflow: "hidden", flex: 1 }}>
                <div style={{
                  fontSize: "13px",
                  fontWeight: 600,
                  color: "var(--text-primary)",
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis"
                }}>
                  {user.username}
                </div>
                <div style={{
                  fontSize: "11px",
                  color: "var(--accent-cyan)",
                  fontWeight: 600,
                  textTransform: "uppercase"
                }}>
                  {user.role || "MEMBER"}
                </div>
              </div>
            </div>

            {onLogout && (
              <button
                type="button"
                onClick={onLogout}
                className="btn btn-secondary btn-sm"
                style={{
                  width: "100%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "8px",
                  padding: "7px 12px",
                  color: "var(--status-risk)",
                  backgroundColor: "var(--status-risk-bg)",
                  borderColor: "rgba(239, 68, 68, 0.3)",
                  fontSize: "12px",
                  fontWeight: 600
                }}
                title="Sign out of current scientific session"
              >
                <LogOut size={14} />
                <span>Sign Out</span>
              </button>
            )}
          </div>
        ) : (
          <div style={{ textAlign: "center", padding: "4px 0" }}>
            <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>Guest Mode</span>
          </div>
        )}
      </div>
    </aside>
  );
};
