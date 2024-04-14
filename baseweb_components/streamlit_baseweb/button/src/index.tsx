import React from "react";
import ReactDOM from "react-dom";
import BaseWebButton from "./Button";
import { Provider as StyletronProvider } from "styletron-react";
import { Client as Styletron } from "styletron-engine-atomic";

const engine = new Styletron();

ReactDOM.render(
  <React.StrictMode>
    <StyletronProvider value={engine}>
      <BaseWebButton />
    </StyletronProvider>
  </React.StrictMode>,
  document.getElementById("root"),
);
