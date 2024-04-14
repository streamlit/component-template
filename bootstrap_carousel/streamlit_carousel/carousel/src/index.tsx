import React from "react";
import ReactDOM from "react-dom";
import { Container } from "react-bootstrap";
import BootstrapCarousel from "./Carousel";

ReactDOM.render(
  <Container className="vh-100 d-flex flex-column ">
    <BootstrapCarousel />
  </Container>,
  document.getElementById("root"),
);
