export type Theme = "dark" | "light";

export const getStoredTheme = (): Theme => {
  if (typeof window === "undefined") return "dark";
  const stored = localStorage.getItem("scidata_theme");
  if (stored === "light" || stored === "dark") return stored;
  if (window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches) {
    return "light";
  }
  return "dark";
};

export const applyTheme = (theme: Theme) => {
  if (typeof document === "undefined") return;
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("scidata_theme", theme);
};

export const toggleTheme = (): Theme => {
  const current = getStoredTheme();
  const next: Theme = current === "dark" ? "light" : "dark";
  applyTheme(next);
  return next;
};

