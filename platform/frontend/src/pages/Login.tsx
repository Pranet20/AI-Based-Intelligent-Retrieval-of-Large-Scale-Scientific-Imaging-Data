import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  LogIn,
  UserPlus,
  Microscope,
  Lock,
  User as UserIcon,
  Mail,
  Shield,
  Eye,
  EyeOff,
  Sun,
  Moon,
  AlertCircle,
  CheckCircle2,
  Cpu,
  Layers,
  Sparkles
} from "lucide-react";
import { ApiClient } from "../api/client";
import { Theme, getStoredTheme, applyTheme } from "../utils/theme";

interface LoginProps {
  onLoginSuccess: (user: any) => void;
}

export const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [theme, setTheme] = useState<Theme>("dark");
  const navigate = useNavigate();

  // Sign In Form State
  const [loginIdentifier, setLoginIdentifier] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [showLoginPassword, setShowLoginPassword] = useState(false);

  // Sign Up Form State
  const [regUsername, setRegUsername] = useState("");
  const [regEmail, setRegEmail] = useState("");
  const [regPassword, setRegPassword] = useState("");
  const [regConfirmPassword, setRegConfirmPassword] = useState("");
  const [regRole, setRegRole] = useState<string>("RESEARCHER");
  const [showRegPassword, setShowRegPassword] = useState(false);

  // Status & Feedback
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Initialize theme
  useEffect(() => {
    const active = getStoredTheme();
    setTheme(active);
    applyTheme(active);
  }, []);

  const toggleTheme = () => {
    const nextTheme: Theme = theme === "dark" ? "light" : "dark";
    setTheme(nextTheme);
    applyTheme(nextTheme);
  };

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMsg(null);
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("username", loginIdentifier.trim());
      formData.append("password", loginPassword);

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

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMsg(null);

    if (regPassword !== regConfirmPassword) {
      setError("Passwords do not match. Please verify.");
      return;
    }

    if (regPassword.length < 6) {
      setError("Password must contain at least 6 characters.");
      return;
    }

    setLoading(true);
    try {
      await ApiClient.register({
        username: regUsername.trim(),
        email: regEmail.trim(),
        password: regPassword,
        role: regRole,
      });

      setSuccessMsg("Account successfully provisioned! Logging into platform...");
      const user = await ApiClient.getCurrentUser();
      setTimeout(() => {
        onLoginSuccess(user);
        navigate("/dashboard");
      }, 500);
    } catch (err: any) {
      setError(err.message || "Registration failed. Username or email may already be in use.");
    } finally {
      setLoading(false);
    }
  };

  const handleFillDemo = (username: string, pass: string) => {
    setMode("signin");
    setLoginIdentifier(username);
    setLoginPassword(pass);
    setError(null);
  };

  return (
    <div style={{
      minHeight: "100vh",
      width: "100vw",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      backgroundColor: "var(--bg-canvas)",
      backgroundImage: theme === "dark" 
        ? "radial-gradient(ellipse at 50% -20%, rgba(59, 130, 246, 0.15), transparent 70%), radial-gradient(ellipse at 80% 80%, rgba(6, 182, 212, 0.08), transparent 50%)"
        : "radial-gradient(ellipse at 50% -20%, rgba(37, 99, 235, 0.08), transparent 70%), radial-gradient(ellipse at 80% 80%, rgba(8, 145, 178, 0.06), transparent 50%)",
      padding: "24px",
      position: "relative",
      boxSizing: "border-box"
    }}>
      {/* Top Bar Floating Controls */}
      <div style={{
        position: "absolute",
        top: "24px",
        left: "28px",
        right: "28px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between"
      }}>
        {/* Brand identity pill */}
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "10px",
          color: "var(--text-primary)",
          fontWeight: 700,
          fontSize: "15px",
          letterSpacing: "0.3px"
        }}>
          <div style={{
            width: "32px",
            height: "32px",
            borderRadius: "var(--radius-md)",
            background: "linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-cyan) 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#ffffff",
            boxShadow: "0 2px 10px rgba(59, 130, 246, 0.35)"
          }}>
            <Microscope size={18} />
          </div>
          <span>SciData Platform</span>
        </div>

        {/* Theme Toggle & Engine Status */}
        <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
          <div style={{
            display: "none",
            alignItems: "center",
            gap: "6px",
            padding: "5px 12px",
            borderRadius: "var(--radius-full)",
            backgroundColor: "var(--status-nominal-bg)",
            border: "1px solid rgba(16, 185, 129, 0.3)",
            fontSize: "11px",
            fontWeight: 600,
            color: "var(--status-nominal)"
          }}>
            <span style={{
              width: "6px",
              height: "6px",
              borderRadius: "50%",
              backgroundColor: "var(--status-nominal)",
              boxShadow: "0 0 6px var(--status-nominal)"
            }} />
            <span>DINOv2 + FAISS Ready</span>
          </div>

          <button
            onClick={toggleTheme}
            className="btn btn-secondary btn-sm"
            title={`Switch to ${theme === "dark" ? "Light" : "Dark"} Mode`}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              padding: "6px 14px",
              borderRadius: "var(--radius-full)",
              fontSize: "12px",
              fontWeight: 600
            }}
          >
            {theme === "dark" ? <Sun size={15} color="#f59e0b" /> : <Moon size={15} color="#6366f1" />}
            <span>{theme === "dark" ? "Light Mode" : "Dark Mode"}</span>
          </button>
        </div>
      </div>

      {/* Main Authentication Container */}
      <div className="card" style={{
        width: "100%",
        maxWidth: "460px",
        padding: "36px",
        borderRadius: "var(--radius-lg)",
        boxShadow: "var(--shadow-lg)",
        backgroundColor: "var(--bg-surface)",
        border: "1px solid var(--border-default)",
        position: "relative",
        zIndex: 10
      }}>
        {/* Header Branding */}
        <div style={{ textAlign: "center", marginBottom: "26px" }}>
          <div style={{
            width: "56px",
            height: "56px",
            borderRadius: "16px",
            background: "linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-cyan) 100%)",
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#ffffff",
            marginBottom: "14px",
            boxShadow: "0 6px 20px rgba(59, 130, 246, 0.4)"
          }}>
            <Microscope size={30} />
          </div>
          <h1 style={{
            fontSize: "22px",
            fontWeight: 800,
            color: "var(--text-primary)",
            letterSpacing: "-0.3px",
            margin: 0
          }}>
            Scientific Portal Gateway
          </h1>
          <p style={{
            fontSize: "13px",
            color: "var(--text-muted)",
            marginTop: "6px",
            lineHeight: 1.4
          }}>
            Metadata-Aware Retrieval, Quality Assessment & Curation Platform
          </p>
        </div>

        {/* Tab Toggle Header */}
        <div style={{
          display: "flex",
          backgroundColor: "var(--bg-canvas)",
          padding: "4px",
          borderRadius: "var(--radius-md)",
          border: "1px solid var(--border-subtle)",
          marginBottom: "24px"
        }}>
          <button
            type="button"
            onClick={() => { setMode("signin"); setError(null); setSuccessMsg(null); }}
            style={{
              flex: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "8px",
              padding: "10px 0",
              borderRadius: "calc(var(--radius-md) - 2px)",
              border: "none",
              fontSize: "13px",
              fontWeight: 600,
              cursor: "pointer",
              transition: "all var(--transition-fast)",
              backgroundColor: mode === "signin" ? "var(--bg-surface-elevated)" : "transparent",
              color: mode === "signin" ? "var(--text-primary)" : "var(--text-muted)",
              boxShadow: mode === "signin" ? "var(--shadow-sm)" : "none"
            }}
          >
            <LogIn size={15} color={mode === "signin" ? "var(--accent-primary)" : "currentColor"} />
            <span>Sign In</span>
          </button>

          <button
            type="button"
            onClick={() => { setMode("signup"); setError(null); setSuccessMsg(null); }}
            style={{
              flex: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "8px",
              padding: "10px 0",
              borderRadius: "calc(var(--radius-md) - 2px)",
              border: "none",
              fontSize: "13px",
              fontWeight: 600,
              cursor: "pointer",
              transition: "all var(--transition-fast)",
              backgroundColor: mode === "signup" ? "var(--bg-surface-elevated)" : "transparent",
              color: mode === "signup" ? "var(--text-primary)" : "var(--text-muted)",
              boxShadow: mode === "signup" ? "var(--shadow-sm)" : "none"
            }}
          >
            <UserPlus size={15} color={mode === "signup" ? "var(--accent-cyan)" : "currentColor"} />
            <span>Create Account</span>
          </button>
        </div>

        {/* Feedback Alerts */}
        {error && (
          <div style={{
            backgroundColor: "var(--status-risk-bg)",
            border: "1px solid rgba(239, 68, 68, 0.3)",
            color: "var(--status-risk)",
            padding: "12px 14px",
            borderRadius: "var(--radius-md)",
            fontSize: "13px",
            marginBottom: "20px",
            display: "flex",
            alignItems: "flex-start",
            gap: "10px",
            lineHeight: 1.4
          }}>
            <AlertCircle size={17} style={{ flexShrink: 0, marginTop: "2px" }} />
            <span>{error}</span>
          </div>
        )}

        {successMsg && (
          <div style={{
            backgroundColor: "var(--status-nominal-bg)",
            border: "1px solid rgba(16, 185, 129, 0.3)",
            color: "var(--status-nominal)",
            padding: "12px 14px",
            borderRadius: "var(--radius-md)",
            fontSize: "13px",
            marginBottom: "20px",
            display: "flex",
            alignItems: "center",
            gap: "10px"
          }}>
            <CheckCircle2 size={17} style={{ flexShrink: 0 }} />
            <span>{successMsg}</span>
          </div>
        )}

        {/* SIGN IN FORM */}
        {mode === "signin" && (
          <form onSubmit={handleSignIn} style={{ display: "flex", flexDirection: "column", gap: "18px" }}>
            <div>
              <label style={{
                display: "block",
                fontSize: "12px",
                fontWeight: 600,
                color: "var(--text-secondary)",
                marginBottom: "6px"
              }}>
                Username or Institutional Email *
              </label>
              <div style={{ position: "relative" }}>
                <UserIcon
                  size={15}
                  color="var(--text-muted)"
                  style={{ position: "absolute", left: "12px", top: "13px" }}
                />
                <input
                  type="text"
                  value={loginIdentifier}
                  onChange={(e) => setLoginIdentifier(e.target.value)}
                  required
                  placeholder="e.g. admin or curator"
                  className="input-field"
                  style={{ paddingLeft: "36px", height: "40px" }}
                />
              </div>
            </div>

            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                <label style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)" }}>
                  Password *
                </label>
              </div>
              <div style={{ position: "relative" }}>
                <Lock
                  size={15}
                  color="var(--text-muted)"
                  style={{ position: "absolute", left: "12px", top: "13px" }}
                />
                <input
                  type={showLoginPassword ? "text" : "password"}
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  required
                  placeholder="Enter your security credential"
                  className="input-field"
                  style={{ paddingLeft: "36px", paddingRight: "36px", height: "40px" }}
                />
                <button
                  type="button"
                  onClick={() => setShowLoginPassword(!showLoginPassword)}
                  style={{
                    position: "absolute",
                    right: "10px",
                    top: "11px",
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    color: "var(--text-muted)",
                    padding: 0
                  }}
                  title={showLoginPassword ? "Hide password" : "Show password"}
                >
                  {showLoginPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
              style={{
                width: "100%",
                height: "44px",
                marginTop: "6px",
                fontSize: "14px",
                fontWeight: 600,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px"
              }}
            >
              <LogIn size={16} />
              <span>{loading ? "Authenticating Session..." : "Sign In to Platform"}</span>
            </button>
          </form>
        )}

        {/* SIGN UP FORM */}
        {mode === "signup" && (
          <form onSubmit={handleSignUp} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div>
              <label style={{
                display: "block",
                fontSize: "12px",
                fontWeight: 600,
                color: "var(--text-secondary)",
                marginBottom: "5px"
              }}>
                Full Username *
              </label>
              <div style={{ position: "relative" }}>
                <UserIcon
                  size={15}
                  color="var(--text-muted)"
                  style={{ position: "absolute", left: "12px", top: "12px" }}
                />
                <input
                  type="text"
                  value={regUsername}
                  onChange={(e) => setRegUsername(e.target.value)}
                  required
                  placeholder="e.g. dr_alex_smith"
                  className="input-field"
                  style={{ paddingLeft: "36px", height: "38px" }}
                />
              </div>
            </div>

            <div>
              <label style={{
                display: "block",
                fontSize: "12px",
                fontWeight: 600,
                color: "var(--text-secondary)",
                marginBottom: "5px"
              }}>
                Institutional Email *
              </label>
              <div style={{ position: "relative" }}>
                <Mail
                  size={15}
                  color="var(--text-muted)"
                  style={{ position: "absolute", left: "12px", top: "12px" }}
                />
                <input
                  type="email"
                  value={regEmail}
                  onChange={(e) => setRegEmail(e.target.value)}
                  required
                  placeholder="e.g. alex@institute.edu"
                  className="input-field"
                  style={{ paddingLeft: "36px", height: "38px" }}
                />
              </div>
            </div>

            <div>
              <label style={{
                display: "block",
                fontSize: "12px",
                fontWeight: 600,
                color: "var(--text-secondary)",
                marginBottom: "5px"
              }}>
                Primary Platform Role *
              </label>
              <div style={{ position: "relative" }}>
                <Shield
                  size={15}
                  color="var(--text-muted)"
                  style={{ position: "absolute", left: "12px", top: "12px" }}
                />
                <select
                  value={regRole}
                  onChange={(e) => setRegRole(e.target.value)}
                  className="input-field"
                  style={{ paddingLeft: "36px", height: "38px", cursor: "pointer" }}
                >
                  <option value="RESEARCHER">Scientist / Researcher (Retrieval & Ingestion)</option>
                  <option value="CURATOR">Curator / Reviewer (Workbench & Quality Review)</option>
                  <option value="ADMIN">System Administrator (Registry & Auditing)</option>
                </select>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
              <div>
                <label style={{
                  display: "block",
                  fontSize: "12px",
                  fontWeight: 600,
                  color: "var(--text-secondary)",
                  marginBottom: "5px"
                }}>
                  Password *
                </label>
                <div style={{ position: "relative" }}>
                  <input
                    type={showRegPassword ? "text" : "password"}
                    value={regPassword}
                    onChange={(e) => setRegPassword(e.target.value)}
                    required
                    placeholder="Min 6 chars"
                    className="input-field"
                    style={{ height: "38px", paddingRight: "30px" }}
                  />
                  <button
                    type="button"
                    onClick={() => setShowRegPassword(!showRegPassword)}
                    style={{
                      position: "absolute",
                      right: "8px",
                      top: "10px",
                      background: "none",
                      border: "none",
                      cursor: "pointer",
                      color: "var(--text-muted)",
                      padding: 0
                    }}
                  >
                    {showRegPassword ? <EyeOff size={14} /> : <Eye size={14} />}
                  </button>
                </div>
              </div>

              <div>
                <label style={{
                  display: "block",
                  fontSize: "12px",
                  fontWeight: 600,
                  color: "var(--text-secondary)",
                  marginBottom: "5px"
                }}>
                  Confirm Password *
                </label>
                <input
                  type={showRegPassword ? "text" : "password"}
                  value={regConfirmPassword}
                  onChange={(e) => setRegConfirmPassword(e.target.value)}
                  required
                  placeholder="Repeat password"
                  className="input-field"
                  style={{ height: "38px" }}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
              style={{
                width: "100%",
                height: "42px",
                marginTop: "6px",
                fontSize: "14px",
                fontWeight: 600,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px"
              }}
            >
              <UserPlus size={16} />
              <span>{loading ? "Provisioning Identity..." : "Register & Enter Platform"}</span>
            </button>
          </form>
        )}

        {/* Demo Fast-Fill Helper */}
        <div style={{
          marginTop: "24px",
          paddingTop: "18px",
          borderTop: "1px solid var(--border-subtle)",
          textAlign: "center"
        }}>
          <div style={{
            fontSize: "11px",
            fontWeight: 600,
            textTransform: "uppercase",
            letterSpacing: "0.6px",
            color: "var(--text-muted)",
            marginBottom: "10px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "6px"
          }}>
            <Sparkles size={13} color="var(--accent-cyan)" />
            <span>Instant Demo Access</span>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "8px" }}>
            <button
              type="button"
              onClick={() => handleFillDemo("admin", "admin123")}
              className="btn btn-secondary btn-sm"
              style={{ fontSize: "11px", padding: "6px 8px" }}
              title="Full system administrative credentials"
            >
              Admin
            </button>
            <button
              type="button"
              onClick={() => handleFillDemo("curator", "curator123")}
              className="btn btn-secondary btn-sm"
              style={{ fontSize: "11px", padding: "6px 8px" }}
              title="Curator workbench credentials"
            >
              Curator
            </button>
            <button
              type="button"
              onClick={() => handleFillDemo("scientist", "scientist123")}
              className="btn btn-secondary btn-sm"
              style={{ fontSize: "11px", padding: "6px 8px" }}
              title="Researcher credentials"
            >
              Scientist
            </button>
          </div>
        </div>

        {/* Protocol Footer Badges */}
        <div style={{
          marginTop: "20px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "12px",
          fontSize: "11px",
          color: "var(--text-muted)"
        }}>
          <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
            <Cpu size={12} /> DINOv2 ViT-S/14
          </span>
          <span>•</span>
          <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
            <Layers size={12} /> HNSW Index
          </span>
          <span>•</span>
          <span style={{ color: "var(--status-nominal)", fontWeight: 600 }}>
            v1.0.0 Stable
          </span>
        </div>
      </div>
    </div>
  );
};
