import React from "react";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: string;
  badge?: string;
  badgeColor?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  trend,
  badge,
  badgeColor = "#3b82f6"
}) => {
  return (
    <div style={{
      backgroundColor: "#ffffff",
      padding: "20px",
      borderRadius: "8px",
      border: "1px solid #e2e8f0",
      boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
      display: "flex",
      flexDirection: "column",
      gap: "8px",
      minWidth: "220px",
      flex: 1
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: "13px", color: "#64748b", fontWeight: "500", textTransform: "uppercase" }}>
          {title}
        </span>
        {badge && (
          <span style={{
            fontSize: "11px",
            backgroundColor: `${badgeColor}15`,
            color: badgeColor,
            padding: "2px 6px",
            borderRadius: "4px",
            fontWeight: "600"
          }}>
            {badge}
          </span>
        )}
      </div>
      <div style={{ fontSize: "28px", fontWeight: "700", color: "#0f172a" }}>
        {value}
      </div>
      {(subtitle || trend) && (
        <div style={{ fontSize: "12px", color: "#64748b" }}>
          {trend && <span style={{ fontWeight: "600", marginRight: "4px" }}>{trend}</span>}
          {subtitle}
        </div>
      )}
    </div>
  );
};
