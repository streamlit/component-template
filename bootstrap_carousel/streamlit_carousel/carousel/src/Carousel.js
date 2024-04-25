import "bootstrap/dist/css/bootstrap.min.css";
import React from "react";
import { Carousel } from "react-bootstrap";
import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib";

class BootstrapCarousel extends StreamlitComponentBase {
  componentDidMount() {
    Streamlit.setFrameHeight(this.props.args["height"]);
  }

  render = () => {
    return (
      <Carousel
        slide={this.props.args["slide"]}
        fade={this.props.args["fade"]}
        controls={this.props.args["controls"]}
        indicators={this.props.args["indicators"]}
        interval={this.props.args["interval"]}
        pause={this.props.args["pause"]}
        wrap={this.props.args["wrap"]}
        style={{ height: "100%" }}
        variant={this.props.theme["base"] !== "dark" && "dark"}
      >
        {Object.values(this.props.args["items"]).map((item, i) => (
          <Carousel.Item
            style={{ height: "100%" }}
            key={`${this.props.args["key"]}_item_${i}`}
          >
            <a href={item.link} target="_blank" rel="noreferrer">
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-around",
                  height: "100%",
                }}
              >
                <img
                  style={{
                    width: `${this.props.args["width"] * 100}%`,
                    height: "100%",
                  }}
                  src={item.img}
                  alt={"slide_" + i}
                />
              </div>
              <Carousel.Caption>
                <h3>{item.title}</h3>
                <p>{item.text}</p>
              </Carousel.Caption>
            </a>
          </Carousel.Item>
        ))}
      </Carousel>
    );
  };
}

export default withStreamlitConnection(BootstrapCarousel);
