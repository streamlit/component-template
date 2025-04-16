import React, { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import MaterialLogin from "./MaterialLogin"

const rootElement = document.getElementById("root")

if (!rootElement) {
  throw new Error("Root element not found")
}

const root = createRoot(rootElement)

root.render(
  <StrictMode>
    <MaterialLogin />
  </StrictMode>
)
