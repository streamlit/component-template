import React from "react"
import { createRoot } from "react-dom/client"
import MyComponent from "./MyComponent"

const root = createRoot(document.getElementById("root") as HTMLElement)
root.render(
  <React.StrictMode>
    <MyComponent />
  </React.StrictMode>
)
