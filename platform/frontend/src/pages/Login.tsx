import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { LogIn, Microscope, Lock, User as UserIcon, ShieldAlert } from "lucide-react";
import { ApiClient } from "../api/client";

interface LoginProps {
  onLoginSuccess: (user: any) => void;
}

export const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("username", username);
      formData.append("password", password);

      await ApiClient.login(formData);
      const user = await ApiClient.getCurrentUser();
      onLoginSuccess(user);
      navigate("/dashboard");
    } catch (err: any) {
      setError(err.message || "Failed to authenticate. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  const handleFillDemo = (user: string, pass: string) => {
    setUsername(user);
    setPassword(pass);
  };

  return (
    <div style={{
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      minHeight: "75vh",
      padding: "20px"
    }}>
      <div className="card" style={{
        width: "100%",
        maxWidth: "420px",
        padding: "32px",
        boxShadow: "var(--shadow-lg)"
      }}>
        {/* Brand Icon & Heading */}
        <div style={{ textAlign: "center", marginBottom: "24px" }}>
          <div style={{
            width: "48px",
            height: "48px",
            borderRadius: "var(--radius-lg)",
            background: "linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-cyan) 100%)",
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#ffffff",
            marginBottom: "12px",
            boxShadow: "0 4px 12px rgba(59, 130, 246, 0.4)"
          }}>
            <Microscope size={26} />
          </div>
          <h2 style={{ fontSize: "20px", fontWeight: "700", color: "var(--text-primary)" }}>
            SciData Authentication
          </h2>
          <p style={{ fontSize: "13px", color: "var(--text-muted)", marginTop: "4px" }}>
            Sign in to access scientific image repositories, vector indices, and curator workbench.
          </p>
        </div>

        {error && (
          <div style={{
            backgroundColor: "var(--status-risk-bg)",
            border: "1px solid rgba(239, 68, 68, 0.3)",
            color: "var(--status-risk)",
            padding: "10px 14px",
            borderRadius: "var(--radius-md)",
            fontSize: "13px",
            marginBottom: "16px",
            display: "flex",
            alignItems: "center",
            gap: "8px"
          }}>
            <ShieldAlert size={16} style={{ flexShrink: 0 }} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)", marginBottom: "6px" }}>
              Username or Email *
            </label>
            <div style={{ position: "relative" }}>
              <UserIcon size={14} color="var(--text-muted)" style={{ position: "absolute", left: "10px", top: "12px" }} />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                placeholder="curator or admin"
                className="input-field"
                style={{ paddingLeft: "32px" }}
              />
            </div>
          </div>

          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)", marginBottom: "6px" }}>
              Password *
            </label>
            <div style={{ position: "relative" }}>
              <Lock size={14} color="var(--text-muted)" style={{ position: "absolute", left: "10px", top: "12px" }} />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="••••••••••••"
                className="input-field"
                style={{ paddingLeft: "32px" }}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{ width: "100%", height: "42px", marginTop: "4px" }}
          >
            <LogIn size={16} />
            <span>{loading ? "Authenticating Session..." : "Sign In to Platform"}</span>
          </button>
        </form>

        {/* Demo Fast-Fill Helper */}
        <div style={{
          marginTop: "24px",
          paddingTop: "16px",
          borderTop: "1px solid var(--border-subtle)",
          textAlign: "center"
        }}>
          <span style={{ fontSize: "11px", color: "var(--text-muted)", display: "block", marginBottom: "8px" }}>
            Platform Demo Role Credentials:
          </span>
          <div style={{ display: "flex", justifyContent: "center", gap: "8px" }}>
            <button
              type="button"
              onClick={() => handleFillDemo("admin", "admin_secure_pass_2026")}
              className="btn btn-secondary btn-sm"
              style={{ fontSize: "11px" }}
            >
              Fill Admin
            </button>
            <button
              type="button"
              onClick={() => handleFillDemo("curator", "curator_pass_2026")}
              className="btn btn-secondary btn-sm"
              style={{ fontSize: "11px" }}
            >
              Fill Curator
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
