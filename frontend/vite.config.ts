import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "node:path";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  // Base public path for assets. Default "/" (served at domain root). For a
  // subdirectory deploy set VITE_BASE, e.g. "/app/". Client-side routing needs
  // an absolute base so assets resolve from the same place on every route.
  base: process.env.VITE_BASE || "/",
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    outDir: "dist",
    sourcemap: false,
    chunkSizeWarningLimit: 900,
  },
  server: {
    port: 5173,
    strictPort: true,
    // Proxy API calls to the FastAPI backend during development so the app can
    // use same-origin relative URLs and avoid CORS entirely.
    proxy: {
      "/api": {
        target: process.env.VITE_API_PROXY_TARGET || "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
