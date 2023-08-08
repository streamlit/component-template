import streamlit as st
from my_component import my_component

num_clicks = my_component("World")
st.markdown("You've clicked %s times!" % int(num_clicks))
