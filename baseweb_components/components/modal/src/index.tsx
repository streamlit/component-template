import React from "react"
import ReactDOM from "react-dom"
import BaseWebModal from "./Modal"
import { Provider as StyletronProvider } from "styletron-react";
import { Client as Styletron } from "styletron-engine-atomic";


const engine = new Styletron();

ReactDOM.render(
  <React.StrictMode>
    <StyletronProvider value={engine}>
      <BaseWebModal />
    </StyletronProvider>
  </React.StrictMode>,
  document.getElementById("root")
)
