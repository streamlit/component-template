import streamlit as st
import streamlit.components.v1 as components

_material_login = components.declare_component(
    "material_login", url="http://localhost:3001",
)


def material_login(title, key=None):
    return _material_login(title=title, key=key)


USERNAME = "a@a.com"
PASSWORD = "test"

logged_in_data = material_login("Insert your account")

st.write(logged_in_data)

if bool(logged_in_data) and logged_in_data['username'] == USERNAME and logged_in_data['password'] == PASSWORD:
    st.balloons()
