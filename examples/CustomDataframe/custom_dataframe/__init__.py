import os

import pandas as pd

import streamlit.components.v1 as components

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
_RELEASE = False

if not _RELEASE:
    _custom_dataframe = components.declare_component(
        "custom_dataframe",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _custom_dataframe = components.declare_component("custom_dataframe", path=build_dir)


def custom_dataframe(data, key=None):
    return _custom_dataframe(data=data, key=key, default=pd.DataFrame())
