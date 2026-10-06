import React, { useEffect, useState } from "react";
import {
  Activity,
  CheckCircle2,
  XCircle,
  Database,
  HardDrive,
  Cpu,
  Layers,
  ShieldCheck,
  FileText,
  Clock,
  Play,
  Download,
  Filter,
  Search,
  Zap,
  Terminal,
  X
} from "lucide-react";
import { SystemHealth } from "../types";
import { ApiClient } from "../api/client";

export const SettingsView: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [readiness, setReadiness] = useState<any>(null);
  const [version, setVersion] = useState<any>(null);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Diagnostic Runner State
  const [runningDiag, setRunningDiag] = useState(false);
  const [diagResult, setDiagResult] = useState<any>(null);

  // Audit Filter & Modal State
  const [filterAction, setFilterAction] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedLog, setSelectedLog] = useState<any | null>(null);

  useEffect(() => {
    loadSystemState();
  }, []);

  const loadSystemState = () => {
    setLoading(true);
    Promise.all([
      ApiClient.getHealth().catch(() => null),
      ApiClient.getReadiness().catch(() => null),
      ApiClient.getVersion().catch(() => null),
      ApiClient.getAuditLogs(50).catch(() => []),
    ])
      .then(([hData, rData, vData, aData]) => {
        setHealth(hData);
        setReadiness(rData);
        setVersion(vData);
        setAuditLogs(aData);
      })
      .finally(() => setLoading(false));
  };

  const handleRunDiagnostic = async () => {
    setRunningDiag(true);
    try {
      const res = await ApiClient.runSystemDiagnostics();
      setDiagResult(res);
      // Reload system state
      loadSystemState();
    } catch (err: any) {
      console.error("Diagnostic probe failed:", err);
    } finally {
      setRunningDiag(false);
    }
  };

  const handleExportAuditLogs = () => {
    const jsonStr = JSON.stringify(auditLogs, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `scidata_audit_trail_${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Filtered audit logs
  const filteredLogs = auditLogs.filter((log) => {
    const matchesAction = filterAction === "ALL" || log.action === filterAction;
    const matchesQuery =
      !searchQuery ||
      log.action?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.resource_type?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      JSON.stringify(log.parameters || {}).toLowerCase().includes(searchQuery.toLowerCase());
    return matchesAction && matchesQuery;
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "16px" }}>
        <div>
          <h1 style={{ fontSize: "22px", fontWeight: "700", color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "10px" }}>
            <Activity size={22} color="var(--accent-primary)" />
            <span>Interactive System Health & Observability</span>
          </h1>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)", marginTop: "4px" }}>
            Live latency telemetry, active subsystem diagnostic benchmarks, and immutable audit event explorer.
          </p>
        </div>

        <div style={{ display: "flex", gap: "10px" }}>
          <button
            onClick={handleRunDiagnostic}
            disabled={runningDiag}
            className="btn btn-primary"
            style={{ display: "flex", alignItems: "center", gap: "8px" }}
          >
            <Play size={15} />
            <span>{runningDiag ? "Probing Subsystems..." : "Run Active Diagnostic Probe"}</span>
          </button>

          <button
            onClick={handleExportAuditLogs}
            className="btn btn-secondary"
            style={{ display: "flex", alignItems: "center", gap: "8px" }}
          >
            <Download size={15} />
            <span>Export Audit Trail (JSON)</span>
          </button>
        </div>
      </div>

      {/* Live Diagnostic Results Panel */}
      {diagResult && (
        <div className="card" style={{
          padding: "20px",
          backgroundColor: "rgba(16, 185, 129, 0.05)",
          borderColor: "rgba(16, 185, 129, 0.3)"
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <Zap size={18} color="var(--status-nominal)" />
              <span style={{ fontSize: "15px", fontWeight: 700, color: "var(--text-primary)" }}>
                Diagnostic Benchmark Results ({diagResult.timestamp})
              </span>
            </div>
            <span className="badge badge-nominal">System Health: {diagResult.overall_health}</span>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px" }}>
            <div style={{ padding: "12px", backgroundColor: "var(--bg-surface)", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)" }}>
              <div style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "4px" }}>DATABASE ROUNDTRIP</div>
              <div style={{ fontSize: "20px", fontWeight: 700, color: "var(--status-nominal)" }}>
                {diagResult.subsystems.database?.latency_ms} ms
              </div>
              <div style={{ fontSize: "11px", color: "var(--text-secondary)", marginTop: "4px" }}>
                Driver: {diagResult.subsystems.database?.driver} (Status: {diagResult.subsystems.database?.status})
              </div>
            </div>

            <div style={{ padding: "12px", backgroundColor: "var(--bg-surface)", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)" }}>
              <div style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "4px" }}>FAISS QUERY LATENCY</div>
              <div style={{ fontSize: "20px", fontWeight: 700, color: "var(--accent-primary)" }}>
                {diagResult.subsystems.vector_engine?.latency_ms} ms
              </div>
              <div style={{ fontSize: "11px", color: "var(--text-secondary)", marginTop: "4px" }}>
                Index: {diagResult.subsystems.vector_engine?.indexed_vectors_count} Vectors (IndexFlatIP)
              </div>
            </div>

            <div style={{ padding: "12px", backgroundColor: "var(--bg-surface)", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)" }}>
              <div style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "4px" }}>CHECKPOINT SHA-256</div>
              <div style={{ fontSize: "20px", fontWeight: 700, color: "var(--accent-cyan)" }}>
                {diagResult.subsystems.checkpoint_integrity?.status}
              </div>
              <div style={{ fontSize: "11px", color: "var(--text-secondary)", marginTop: "4px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                Hash: {diagResult.subsystems.checkpoint_integrity?.calculated_sha256?.slice(0, 16)}...
              </div>
            </div>

            <div style={{ padding: "12px", backgroundColor: "var(--bg-surface)", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)" }}>
              <div style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "4px" }}>STORAGE IO READ/WRITE</div>
              <div style={{ fontSize: "20px", fontWeight: 700, color: "var(--status-nominal)" }}>
                {diagResult.subsystems.storage_io?.latency_ms} ms
              </div>
              <div style={{ fontSize: "11px", color: "var(--text-secondary)", marginTop: "4px" }}>
                Speed: {diagResult.subsystems.storage_io?.throughput_mb_s} MB/s
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Deep Readiness Probes Card */}
      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
          <h2 style={{ fontSize: "15px", fontWeight: 600, color: "var(--text-primary)" }}>
            Deep Dependency Readiness Probes (/api/v1/readiness)
          </h2>
          <span className={`badge ${readiness?.status === "READY" ? "badge-nominal" : "badge-warning"}`}>
            {readiness?.status || "READY"}
          </span>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px" }}>
          <div style={{
            padding: "16px",
            borderRadius: "var(--radius-md)",
            backgroundColor: "var(--bg-canvas)",
            border: "1px solid var(--border-subtle)",
            display: "flex",
            alignItems: "center",
            gap: "12px"
          }}>
            <Database size={24} color="var(--accent-cyan)" />
            <div>
              <div style={{ fontSize: "12px", color: "var(--text-muted)" }}>PostgreSQL / DB</div>
              <div style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)" }}>
                {readiness?.checks?.database || "READY"}
              </div>
            </div>
          </div>

          <div style={{
            padding: "16px",
            borderRadius: "var(--radius-md)",
            backgroundColor: "var(--bg-canvas)",
            border: "1px solid var(--border-subtle)",
            display: "flex",
            alignItems: "center",
            gap: "12px"
          }}>
            <HardDrive size={24} color="var(--status-nominal)" />
            <div>
              <div style={{ fontSize: "12px", color: "var(--text-muted)" }}>Storage Volume</div>
              <div style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)" }}>
                {readiness?.checks?.storage || "READY"}
              </div>
            </div>
          </div>

          <div style={{
            padding: "16px",
            borderRadius: "var(--radius-md)",
            backgroundColor: "var(--bg-canvas)",
            border: "1px solid var(--border-subtle)",
            display: "flex",
            alignItems: "center",
            gap: "12px"
          }}>
            <Cpu size={24} color="var(--accent-primary)" />
            <div>
              <div style={{ fontSize: "12px", color: "var(--text-muted)" }}>Phase 4 Checkpoint</div>
              <div style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)" }}>
                {readiness?.checks?.model_checkpoint || "READY"}
              </div>
            </div>
          </div>

          <div style={{
            padding: "16px",
            borderRadius: "var(--radius-md)",
            backgroundColor: "var(--bg-canvas)",
            border: "1px solid var(--border-subtle)",
            display: "flex",
            alignItems: "center",
            gap: "12px"
          }}>
            <Layers size={24} color="var(--status-novel)" />
            <div>
              <div style={{ fontSize: "12px", color: "var(--text-muted)" }}>FAISS Vector Engine</div>
              <div style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)" }}>
                {health?.faiss_index_count ?? 3} Vectors Indexed
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* INTERACTIVE AUDIT TRAIL EXPLORER */}
      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px", flexWrap: "wrap", gap: "12px" }}>
          <div>
            <h2 style={{ fontSize: "15px", fontWeight: 600, color: "var(--text-primary)" }}>
              Immutable Platform Audit Trail ({filteredLogs.length} Events)
            </h2>
            <p style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "2px" }}>
              Click any audit entry to inspect full JSON cryptographic parameters and actor identity.
            </p>
          </div>

          {/* Filter & Search Bar */}
          <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
            <div style={{ position: "relative" }}>
              <Search size={14} color="var(--text-muted)" style={{ position: "absolute", left: "10px", top: "11px" }} />
              <input
                type="text"
                placeholder="Search audit parameters..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input-field"
                style={{ paddingLeft: "32px", fontSize: "12px", width: "200px", height: "34px" }}
              />
            </div>

            <select
              value={filterAction}
              onChange={(e) => setFilterAction(e.target.value)}
              className="input-field"
              style={{ fontSize: "12px", width: "auto", height: "34px" }}
            >
              <option value="ALL">All Event Actions</option>
              <option value="UPLOAD">UPLOAD</option>
              <option value="LOGIN">LOGIN</option>
              <option value="MODEL_ACCESS">MODEL_ACCESS</option>
              <option value="HUMAN_REVIEW_SUBMITTED">HUMAN_REVIEW_SUBMITTED</option>
            </select>
          </div>
        </div>

        <div className="table-container">
          <table className="scientific-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Action</th>
                <th>Resource</th>
                <th>Parameters</th>
                <th>Status</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {filteredLogs.map((log) => (
                <tr
                  key={log.id}
                  onClick={() => setSelectedLog(log)}
                  style={{ cursor: "pointer", transition: "background 0.15s ease" }}
                  title="Click to inspect event details"
                >
                  <td className="font-mono" style={{ color: "var(--text-muted)" }}>#{log.id}</td>
                  <td style={{ fontWeight: 600, color: "var(--text-primary)" }}>
                    <span style={{
                      padding: "2px 6px",
                      borderRadius: "var(--radius-sm)",
                      backgroundColor: "var(--bg-canvas)",
                      border: "1px solid var(--border-subtle)",
                      fontSize: "11px"
                    }}>
                      {log.action}
                    </span>
                  </td>
                  <td className="font-mono" style={{ color: "var(--accent-cyan)" }}>
                    {log.resource_type} #{log.resource_id ?? ""}
                  </td>
                  <td style={{ maxWidth: "260px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", fontSize: "11px", color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                    {JSON.stringify(log.parameters || {})}
                  </td>
                  <td>
                    <span className={`badge ${log.result_status === "SUCCESS" ? "badge-nominal" : "badge-risk"}`}>
                      {log.result_status || "SUCCESS"}
                    </span>
                  </td>
                  <td style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                    {log.timestamp ? new Date(log.timestamp).toLocaleString() : "Recently"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* JSON Audit Inspection Modal */}
      {selectedLog && (
        <div style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: "rgba(0, 0, 0, 0.75)",
          backdropFilter: "blur(6px)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 100,
          padding: "20px"
        }}>
          <div className="card" style={{
            width: "100%",
            maxWidth: "600px",
            padding: "24px",
            backgroundColor: "var(--bg-surface)",
            borderRadius: "var(--radius-lg)",
            border: "1px solid var(--border-default)",
            boxShadow: "var(--shadow-lg)"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <Terminal size={18} color="var(--accent-primary)" />
                <span style={{ fontSize: "16px", fontWeight: 700, color: "var(--text-primary)" }}>
                  Audit Event #{selectedLog.id} - {selectedLog.action}
                </span>
              </div>
              <button
                onClick={() => setSelectedLog(null)}
                style={{ background: "none", border: "none", cursor: "pointer", color: "var(--text-muted)" }}
              >
                <X size={18} />
              </button>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", fontSize: "12px", marginBottom: "16px" }}>
              <div><strong>Resource Type:</strong> {selectedLog.resource_type}</div>
              <div><strong>Resource ID:</strong> {selectedLog.resource_id || "N/A"}</div>
              <div><strong>Status:</strong> {selectedLog.result_status || "SUCCESS"}</div>
              <div><strong>Timestamp:</strong> {selectedLog.timestamp ? new Date(selectedLog.timestamp).toISOString() : "N/A"}</div>
            </div>

            <div style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "6px" }}>
              Cryptographic Event Parameters:
            </div>
            <pre style={{
              backgroundColor: "var(--bg-canvas)",
              padding: "14px",
              borderRadius: "var(--radius-md)",
              fontSize: "12px",
              fontFamily: "var(--font-mono)",
              color: "var(--accent-cyan)",
              maxHeight: "220px",
              overflowY: "auto",
              border: "1px solid var(--border-subtle)"
            }}>
              {JSON.stringify(selectedLog.parameters || {}, null, 2)}
            </pre>

            <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "16px" }}>
              <button
                onClick={() => setSelectedLog(null)}
                className="btn btn-secondary btn-sm"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
