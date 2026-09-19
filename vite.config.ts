import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig({
  root: "web",
  resolve: { alias: { "/src": new URL("./src", import.meta.url).pathname } },
  publicDir: "../public",
  plugins: [react()],
  base: "./",
  build: { outDir: "../dist", emptyOutDir: true },
});
