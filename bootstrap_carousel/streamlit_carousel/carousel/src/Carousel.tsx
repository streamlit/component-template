import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib";
import React, { ReactNode } from "react";
import { Carousel } from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";

interface CarouselItem {
  interval: number;
  img: string;
  title: string;
  text: string;
}

class BootstrapCarousel extends StreamlitComponentBase {
  public componentDidMount() {
    Streamlit.setFrameHeight(this.props.args["height"]);
  }

  public render = (): ReactNode => {
    return (
      <Carousel
        slide={this.props.args["slide"]}
        fade={this.props.args["fade"]}
        controls={this.props.args["controls"]}
        indicators={this.props.args["indicators"]}
        interval={this.props.args["interval"]}
        pause={this.props.args["pause"]}
        wrap={this.props.args["wrap"]}
      >
        {Object.values(this.props.args["items"]).map((item, i) => (
          <Carousel.Item interval={(item as CarouselItem).interval} key={i}>
            <img
              className="d-block w-100"
              src={(item as CarouselItem).img}
              alt={"slide_" + i}
            />
            <Carousel.Caption>
              <h3>{(item as CarouselItem).title}</h3>
              <p>{(item as CarouselItem).text}</p>
            </Carousel.Caption>
          </Carousel.Item>
        ))}
      </Carousel>
    );
  };
}

export default withStreamlitConnection(BootstrapCarousel);
