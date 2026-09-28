import React from "react";
import { Link, useLocation } from "react-router-dom";

export const Sidebar: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { label: "Dashboard", path: "/dashboard" },
    { label: "Projects", path: "/projects" },
    { label: "Upload Images", path: "/upload" },
    { label: "Search & Retrieval", path: "/search" },
    { label: "Curation & Deduplication", path: "/curation" },
    { label: "Review Queue", path: "/reviews" },
    { label: "Model Registry", path: "/models" },
    { label: "System Health & Audit", path: "/settings" },
  ];

  return (
    <aside style={{
      width: "240px",
      backgroundColor: "#1e293b",
      color: "#f8fafc",
      display: "flex",
      flexDirection: "column",
      padding: "20px 0",
      borderRight: "1px solid #334155",
      minHeight: "calc(100vh - 60px)"
    }}>
      <div style={{ padding: "0 20px 16px 20px", fontSize: "12px", textTransform: "uppercase", letterSpacing: "1px", color: "#64748b" }}>
        Navigation
      </div>
      <nav style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
        {navItems.map((item) => {
          const isActive = location.pathname === item.path || (item.path !== "/dashboard" && location.pathname.startsWith(item.path));
          return (
            <Link
              key={item.path}
              to={item.path}
              style={{
                display: "block",
                padding: "10px 20px",
                color: isActive ? "#ffffff" : "#94a3b8",
                backgroundColor: isActive ? "#334155" : "transparent",
                textDecoration: "none",
                fontSize: "14px",
                fontWeight: isActive ? "600" : "400",
                borderLeft: isActive ? "3px solid #38bdf8" : "3px solid transparent"
              }}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
};
