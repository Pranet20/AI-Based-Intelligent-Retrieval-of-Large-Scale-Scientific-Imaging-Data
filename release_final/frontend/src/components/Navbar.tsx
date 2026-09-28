import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { ApiClient } from "../api/client";

interface NavbarProps {
  user: any;
  onLogout: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ user, onLogout }) => {
  const navigate = useNavigate();

  return (
    <header style={{
      height: "60px",
      backgroundColor: "#0f172a",
      color: "#f8fafc",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "0 24px",
      borderBottom: "1px solid #334155"
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        <span style={{ fontSize: "18px", fontWeight: "bold", letterSpacing: "0.5px" }}>
          SciData Platform
        </span>
        <span style={{
          fontSize: "11px",
          backgroundColor: "#1e293b",
          color: "#94a3b8",
          padding: "2px 8px",
          borderRadius: "4px",
          border: "1px solid #475569"
        }}>
          Phase 8 Production
        </span>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
        {user ? (
          <>
            <span style={{ fontSize: "14px", color: "#cbd5e1" }}>
              {user.username} ({user.role})
            </span>
            <button
              onClick={onLogout}
              style={{
                backgroundColor: "#334155",
                color: "#f8fafc",
                border: "none",
                padding: "6px 12px",
                borderRadius: "4px",
                cursor: "pointer",
                fontSize: "13px"
              }}
            >
              Sign Out
            </button>
          </>
        ) : (
          <Link
            to="/login"
            style={{
              backgroundColor: "#2563eb",
              color: "#ffffff",
              padding: "6px 14px",
              borderRadius: "4px",
              fontSize: "13px"
            }}
          >
            Sign In
          </Link>
        )}
      </div>
    </header>
  );
};
