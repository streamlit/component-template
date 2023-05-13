import os
import streamlit.components.v1 as components

_RELEASE = False

if not _RELEASE:
    _base_web_button = components.declare_component(
        "base_web_button",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _base_web_button = components.declare_component("base_web_button", path=build_dir)


def base_web_button(key=None):
    _base_web_button(key=key, default=0)
