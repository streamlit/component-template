import os
import streamlit.components.v1 as components

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
_RELEASE = False

if not _RELEASE:
    _selectable_data_table = components.declare_component(
        "selectable_data_table",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _selectable_data_table = components.declare_component("selectable_data_table", path=build_dir)


def selectable_data_table(data, key=None):
    return _selectable_data_table(data=data, default=[], key=key)
