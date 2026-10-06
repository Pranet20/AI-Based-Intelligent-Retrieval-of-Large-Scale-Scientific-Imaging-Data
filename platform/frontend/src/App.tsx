import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Navbar } from "./components/Navbar";
import { Sidebar } from "./components/Sidebar";
import { Footer } from "./components/Footer";
import { Dashboard } from "./pages/Dashboard";
import { Projects } from "./pages/Projects";
import { Upload } from "./pages/Upload";
import { ImageDetail } from "./pages/ImageDetail";
import { Search } from "./pages/Search";
import { Curation } from "./pages/Curation";
import { ReviewQueue } from "./pages/ReviewQueue";
import { ModelsView } from "./pages/ModelsView";
import { SettingsView } from "./pages/SettingsView";
import { MultiImageAnalysis } from "./pages/MultiImageAnalysis";
import { Login } from "./pages/Login";
import { ApiClient } from "./api/client";
import { getStoredTheme, applyTheme } from "./utils/theme";

export const App: React.FC = () => {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Initialize theme
    const currentTheme = getStoredTheme();
    applyTheme(currentTheme);

    // Verify session
    const token = ApiClient.getToken();
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }

    ApiClient.getCurrentUser()
      .then((u) => setUser(u))
      .catch(() => {
        ApiClient.clearToken();
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleLogout = () => {
    ApiClient.clearToken();
    setUser(null);
  };

  if (loading) {
    return (
      <div style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "100vh",
        backgroundColor: "var(--bg-canvas)",
        color: "var(--text-muted)",
        fontSize: "14px",
        gap: "12px"
      }}>
        <div style={{
          width: "36px",
          height: "36px",
          border: "3px solid var(--border-default)",
          borderTopColor: "var(--accent-primary)",
          borderRadius: "50%",
          animation: "spin 1s linear infinite"
        }} />
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        <span>Initializing SciData Research Platform...</span>
      </div>
    );
  }

  // Gateway Protection: If unauthenticated, render ONLY the authentication interface
  if (!user) {
    return (
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login onLoginSuccess={setUser} />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    );
  }

  // Authenticated Platform Shell
  return (
    <BrowserRouter>
      <div style={{
        display: "flex",
        flexDirection: "column",
        minHeight: "100vh",
        backgroundColor: "var(--bg-canvas)",
        color: "var(--text-primary)"
      }}>
        <Navbar user={user} onLogout={handleLogout} />
        <div style={{ display: "flex", flex: 1 }}>
          <Sidebar user={user} onLogout={handleLogout} />
          <main style={{
            flex: 1,
            padding: "28px 32px",
            backgroundColor: "var(--bg-canvas)",
            overflowY: "auto",
            minHeight: "calc(100vh - var(--header-height))"
          }}>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/login" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/explorer" element={<Projects />} />
              <Route path="/projects" element={<Projects />} />
              <Route path="/upload" element={<Upload />} />
              <Route path="/images/:id" element={<ImageDetail />} />
              <Route path="/search" element={<Search />} />
              <Route path="/multi-image" element={<MultiImageAnalysis />} />
              <Route path="/curation" element={<Curation />} />
              <Route path="/reviews" element={<ReviewQueue />} />
              <Route path="/workbench" element={<ReviewQueue />} />
              <Route path="/models" element={<ModelsView />} />
              <Route path="/health" element={<SettingsView />} />
              <Route path="/settings" element={<SettingsView />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </main>
        </div>
        <Footer />
      </div>
    </BrowserRouter>
  );
};

export default App;
