import { defineConfig, UserConfig } from "vite"
import react from "@vitejs/plugin-react-swc"

/** @see https://vitejs.dev/config/ */
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
