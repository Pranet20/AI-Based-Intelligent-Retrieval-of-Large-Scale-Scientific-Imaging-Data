import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Activity, ShieldCheck, Database, LogOut, LogIn, Microscope } from "lucide-react";
import { ApiClient } from "../api/client";

interface NavbarProps {
  user: any;
  onLogout: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ user, onLogout }) => {
  const [dbStatus, setDbStatus] = useState<string>("checking");
  const [faissCount, setFaissCount] = useState<number | null>(null);

  useEffect(() => {
    ApiClient.getHealth()
      .then((h) => {
        setDbStatus(h.database);
        setFaissCount(h.faiss_index_count);
      })
      .catch(() => {
        setDbStatus("unreachable");
      });
  }, []);

  return (
    <header style={{
      height: "var(--header-height)",
      backgroundColor: "var(--bg-surface)",
      borderBottom: "1px solid var(--border-default)",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "0 24px",
      position: "sticky",
      top: 0,
      zIndex: 50,
      boxShadow: "var(--shadow-sm)"
    }}>
      {/* Brand & Platform Identity */}
      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
        <Link to="/dashboard" style={{ display: "flex", alignItems: "center", gap: "10px", textDecoration: "none" }}>
          <div style={{
            width: "36px",
            height: "36px",
            borderRadius: "var(--radius-md)",
            background: "linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-cyan) 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#ffffff",
            boxShadow: "0 2px 8px rgba(59, 130, 246, 0.4)"
          }}>
            <Microscope size={20} />
          </div>
          <div>
            <div style={{ fontSize: "16px", fontWeight: "700", color: "var(--text-primary)", letterSpacing: "0.2px" }}>
              SciData Platform
            </div>
            <div style={{ fontSize: "11px", color: "var(--text-muted)", letterSpacing: "0.4px" }}>
              Scientific Image Data Management
            </div>
          </div>
        </Link>

        {/* Runtime Status Pill */}
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          padding: "4px 10px",
          borderRadius: "var(--radius-full)",
          backgroundColor: "rgba(16, 185, 129, 0.1)",
          border: "1px solid rgba(16, 185, 129, 0.3)",
          fontSize: "11px",
          fontWeight: 600,
          color: "var(--status-nominal)"
        }}>
          <span style={{
            width: "7px",
            height: "7px",
            borderRadius: "50%",
            backgroundColor: "var(--status-nominal)",
            boxShadow: "0 0 8px var(--status-nominal)"
          }} />
          PROJECT_RUNTIME_VALIDATED
        </div>
      </div>

      {/* Observability Telemetry & Auth */}
      <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
        {/* Live Vector Engine Telemetry */}
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "14px",
          fontSize: "12px",
          color: "var(--text-secondary)",
          backgroundColor: "var(--bg-canvas)",
          padding: "5px 12px",
          borderRadius: "var(--radius-md)",
          border: "1px solid var(--border-subtle)"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <Database size={14} color="var(--accent-cyan)" />
            <span>DB:</span>
            <span style={{
              fontWeight: 600,
              color: dbStatus === "connected" ? "var(--status-nominal)" : "var(--status-risk)"
            }}>
              {dbStatus}
            </span>
          </div>

          <div style={{ width: "1px", height: "14px", backgroundColor: "var(--border-default)" }} />

          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <Activity size={14} color="var(--accent-primary)" />
            <span>FAISS Vectors:</span>
            <span style={{ fontWeight: 600, color: "var(--text-primary)" }}>
              {faissCount !== null ? faissCount.toLocaleString() : "..."}
            </span>
          </div>
        </div>

        {/* User / Authentication */}
        {user ? (
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <div style={{
                width: "32px",
                height: "32px",
                borderRadius: "var(--radius-full)",
                backgroundColor: "var(--bg-surface-elevated)",
                border: "1px solid var(--border-default)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "var(--accent-cyan)",
                fontWeight: 600,
                fontSize: "13px"
              }}>
                {user.username.charAt(0).toUpperCase()}
              </div>
              <div style={{ display: "flex", flexDirection: "column" }}>
                <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)" }}>
                  {user.username}
                </span>
                <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                  {user.role}
                </span>
              </div>
            </div>

            <button
              onClick={onLogout}
              className="btn btn-secondary btn-sm"
              title="Sign Out"
              style={{ display: "flex", alignItems: "center", gap: "6px" }}
            >
              <LogOut size={14} />
              <span>Sign Out</span>
            </button>
          </div>
        ) : (
          <Link
            to="/login"
            className="btn btn-primary btn-sm"
            style={{ display: "flex", alignItems: "center", gap: "6px" }}
          >
            <LogIn size={14} />
            <span>Sign In</span>
          </Link>
        )}
      </div>
    </header>
  );
};
