import os

import streamlit as st
import streamlit.components.v1 as components


# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
_RELEASE = False

if not _RELEASE:
    _radio_button = components.declare_component(
        "radio_button",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _radio_button = components.declare_component("radio_button", path=build_dir)


def custom_radio_button(label, options, default, key=None):
    return _radio_button(label=label, options=options, default=default, key=key)

# Test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run radio_button/__init__.py`
if not _RELEASE:
    result = custom_radio_button(
        "How many bats?",
        options=["one bat", "TWO bats", "THREE bats", "FOUR BATS! ah ah ah!"],
        default="one bat",
    )
    st.write("This many: %s" % result)
