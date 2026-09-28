import React from "react";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: string;
  badge?: string;
  badgeColor?: string;
  icon?: React.ReactNode;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  trend,
  badge,
  badgeColor = "var(--accent-primary)",
  icon
}) => {
  return (
    <div className="card" style={{
      display: "flex",
      flexDirection: "column",
      gap: "10px",
      minWidth: "220px",
      flex: "1 1 220px",
      position: "relative",
      overflow: "hidden"
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          {icon && <span style={{ color: badgeColor }}>{icon}</span>}
          <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "600", textTransform: "uppercase", letterSpacing: "0.5px" }}>
            {title}
          </span>
        </div>
        {badge && (
          <span style={{
            fontSize: "11px",
            backgroundColor: `rgba(59, 130, 246, 0.1)`,
            color: badgeColor,
            border: `1px solid ${badgeColor}33`,
            padding: "2px 6px",
            borderRadius: "var(--radius-sm)",
            fontWeight: "600"
          }}>
            {badge}
          </span>
        )}
      </div>

      <div style={{ fontSize: "28px", fontWeight: "700", color: "var(--text-primary)", letterSpacing: "-0.5px" }}>
        {value}
      </div>

      {(subtitle || trend) && (
        <div style={{ fontSize: "12px", color: "var(--text-secondary)", display: "flex", alignItems: "center", gap: "6px" }}>
          {trend && <span style={{ fontWeight: "600", color: "var(--accent-cyan)" }}>{trend}</span>}
          <span>{subtitle}</span>
        </div>
      )}
    </div>
  );
};
