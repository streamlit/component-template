import os
import base64
from typing import TypedDict, List, NotRequired

import streamlit as st
import streamlit.components.v1 as components

# TODO:
#  - fix overflow issue when item's text is too long

_RELEASE = True

__title__ = "Bootstrap Carousel"
__author__ = "Thomas Bouamoud"

if not _RELEASE:
    _bootstrap_carousel = components.declare_component(
        "streamlit_carousel",
        url="http://localhost:3000",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    modal_dir = os.path.join(parent_dir, "carousel/build")
    _bootstrap_carousel = components.declare_component(
        "streamlit_carousel", path=modal_dir
    )


class Item(TypedDict):
    title: str
    text: str
    img: str
    link: NotRequired[str | None]
    interval: NotRequired[int | None]


def get_image_data_url(file_path: str) -> str:
    """Convert a local image file to a data URL."""
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded_string}"


def validate_items(items: List[Item]) -> List[Item]:
    for item in items:
        if "img" not in item:
            raise ValueError(
                "Each item should include an 'img' key referring to an image url"
            )
        if "title" not in item:
            raise ValueError(
                "Each item should include a 'title' key referring to a string variable"
            )
        if "text" not in item:
            raise ValueError(
                "Each item should include a 'text' key referring to a string variable"
            )
        if "interval" not in item:
            item["interval"] = None
        if "link" not in item:
            item["link"] = None
        if os.path.isfile(item["img"]):
            item["img"] = get_image_data_url(item["img"])
    return items


def carousel(
    items: List[Item],
    slide: bool = True,
    fade: bool = False,
    controls: bool = True,
    indicators: bool = True,
    interval: int = 5000,
    pause: str = None,
    wrap: bool = True,
    container_height: int = 400,
    width: float = 1,
    key=None,
) -> None:
    """
    Defines a Carousel component in the React Bootstrap framework.

    Parameters:
    -------
    - items (List[Item]): A list of items to be displayed in the carousel.
        Each item is represented by a dictionary containing the necessary information for the carousel slide.
        Items should be defined in the below format ('link' and 'interval' are optional):

    carousel([
    {"img": "image1.jpg", "title": "Slide 1", "text": "Description for Slide 1", "link": "https://discuss.streamlit.io/t/new-component-react-bootstrap-carousel/46819", interval=2000},
    {"img": "image2.jpg", "title": "Slide 2", "text": "Description for Slide 2", "link": "https://discuss.streamlit.io/t/new-component-react-bootstrap-carousel/46819", interval=3000},
    {"img": "image3.jpg", "title": "Slide 3", "text": "Description for Slide 3", "link": "https://discuss.streamlit.io/t/new-component-react-bootstrap-carousel/46819", interval=4000}

    - slide (bool, optional): Add sliding animation between items.
        Defaults to True.
    - fade (bool, optional): Determines whether the carousel should use a fading effect during slide transitions.
        Defaults to False.
    - controls (bool, optional): Determines whether navigation controls (previous/next buttons) should be displayed.
        Defaults to True.
    - indicators (bool, optional): Determines whether slide indicators (dots indicating the current slide) should be displayed.
        Defaults to True.
    - interval (int, optional): The duration (in milliseconds) between slide transitions. Defaults to 5000 (5 seconds).
    - pause (str, optional): If set to "hover", pauses the cycling of the carousel on mouseenter and resumes the cycling
                            of the carousel on mouseleave. If set to false, hovering over the carousel won't pause it.
                            On touch-enabled devices, when set to "hover", cycling will pause on touchend (once the user
                            finished interacting with the carousel) for two intervals, before automatically resuming.
                            Note that this is in addition to the above mouse behavior.
        Allowed values are "hover" or None. Defaults to None.
    - wrap (bool, optional): Whether the carousel should cycle continuously or have hard stops.
        Defaults to False.
    - container_height (int, optional): The height (in pixels) of the Streamlit container holding the carousel component.
        Defaults to 400.
    - width (float, optional): The width of the carousel component as a percentage of the container width.
        Defaults to 100%.
    - key (any, optional): An optional key to uniquely identify the carousel component.
        Defaults to None.

    Returns:
    -------
    None
    """
    items = validate_items(items)
    _bootstrap_carousel(
        items=items,
        slide=slide,
        fade=fade,
        controls=controls,
        indicators=indicators,
        interval=interval,
        validation_button_label=pause,
        wrap=wrap,
        key=key,
        width=width,
        height=container_height,
        default=0,
    )
    width = 100
    width_css = (
        """
    div[data-stale="false"]>iframe[title="streamlit_carousel.streamlit_carousel"] {
        width: """
        + str(width)
        + """%;
    }
    """
    )
    st.markdown(f"<style>{width_css}</style>", unsafe_allow_html=True)
