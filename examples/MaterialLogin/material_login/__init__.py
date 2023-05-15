import os

import streamlit as st
import streamlit.components.v1 as components

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
_RELEASE = False

if not _RELEASE:
    _material_login = components.declare_component(
        "material_login",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _material_login = components.declare_component("material_login", path=build_dir)


def material_login(title, key=None):
    return _material_login(title=title, key=key)

# Test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run material_login/__init__.py`
if not _RELEASE:
    USERNAME = "a@a.com"
    PASSWORD = "test"

    logged_in_data = material_login("Insert your account")

    st.write(logged_in_data)

    if bool(logged_in_data) and logged_in_data['username'] == USERNAME and logged_in_data['password'] == PASSWORD:
        st.balloons()
