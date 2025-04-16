import { defineConfig, loadEnv, UserConfig } from "vite"

/**
 * Vite configuration for Streamlit React Component development
 *
 * @see https://vitejs.dev/config/ for complete Vite configuration options
 */
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())

  const port = env.VITE_PORT ? parseInt(env.VITE_PORT) : 3001

  return {
    base: "./",
    server: {
      port,
    },
    build: {
      outDir: "build",
    },
  } satisfies UserConfig
})
