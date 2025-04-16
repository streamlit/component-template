import { defineConfig, UserConfig } from "vite"

/**
 * Vite configuration for Streamlit Component development
 *
 * @see https://vitejs.dev/config/ for complete Vite configuration options
 */
export default defineConfig({
  base: "./",
  server: {
    port: process.env.PORT ? parseInt(process.env.PORT) : 3001,
  },
  build: {
    outDir: "build",
  },
}) satisfies UserConfig
