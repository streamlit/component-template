import os
import streamlit.components.v1 as components

_RELEASE = False

__title__ = "Baseweb UI"
__author__ = "Thomas Bouamoud"


if not _RELEASE:
    _base_web_button = components.declare_component(
        "base_web_button", url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "baseweb_components/button/frontend/build")
    _base_web_button = components.declare_component("base_web_button", path=build_dir)


def base_web_button(
    label: str = "you forgot to add a label to your button",
    disabled: bool = False,
    size: str = "default",
    shape: str = "default",
    kind: str = "primary",
    key=None,
) -> None:
    _base_web_button(
        label=label,
        disabled=disabled,
        size=size,
        shape=shape,
        kind=kind,
        key=key,
        default=0,
    )
