import React from "react";
import ReactDOM from "react-dom/client";
import Container from "react-bootstrap/Container";
import BootstrapCarousel from "./Carousel";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <>
    <Container className="vh-100 d-flex flex-column ">
      <BootstrapCarousel />
    </Container>
  </>,
);
