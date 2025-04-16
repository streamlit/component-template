import { defineConfig, UserConfig } from "vite"
import react from "@vitejs/plugin-react-swc"

/**
 * Vite configuration for Streamlit React Component development
 *
 * @see https://vitejs.dev/config/ for complete Vite configuration options
 */
export default defineConfig({
  base: "./",
  plugins: [react()],
  server: {
    port: process.env.PORT ? parseInt(process.env.PORT) : 3001,
  },
  build: {
    outDir: "build",
  },
}) satisfies UserConfig
