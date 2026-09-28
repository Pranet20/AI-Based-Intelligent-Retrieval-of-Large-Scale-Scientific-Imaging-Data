import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Navbar } from "./components/Navbar";
import { Sidebar } from "./components/Sidebar";
import { Dashboard } from "./pages/Dashboard";
import { Projects } from "./pages/Projects";
import { Upload } from "./pages/Upload";
import { ImageDetail } from "./pages/ImageDetail";
import { Search } from "./pages/Search";
import { Curation } from "./pages/Curation";
import { ReviewQueue } from "./pages/ReviewQueue";
import { ModelsView } from "./pages/ModelsView";
import { SettingsView } from "./pages/SettingsView";
import { Login } from "./pages/Login";
import { ApiClient } from "./api/client";

export const App: React.FC = () => {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    ApiClient.getCurrentUser()
      .then((u) => setUser(u))
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  const handleLogout = () => {
    ApiClient.clearToken();
    setUser(null);
  };

  if (loading) {
    return <div style={{ padding: "40px", color: "#64748b" }}>Initializing SciData Platform...</div>;
  }

  return (
    <BrowserRouter>
      <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
        <Navbar user={user} onLogout={handleLogout} />
        <div style={{ display: "flex", flex: 1 }}>
          <Sidebar />
          <main style={{ flex: 1, padding: "24px", backgroundColor: "#f8fafc", overflowY: "auto" }}>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/login" element={<Login onLoginSuccess={setUser} />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/projects" element={<Projects />} />
              <Route path="/upload" element={<Upload />} />
              <Route path="/images/:id" element={<ImageDetail />} />
              <Route path="/search" element={<Search />} />
              <Route path="/curation" element={<Curation />} />
              <Route path="/reviews" element={<ReviewQueue />} />
              <Route path="/models" element={<ModelsView />} />
              <Route path="/settings" element={<SettingsView />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
};

export default App;
