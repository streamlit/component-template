import streamlit as st
from my_component import my_component

# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run example.py`

st.subheader("Component with constant args")

# Create an instance of our component with a constant `name` arg, and
# print its output value.
result = my_component("World")
st.markdown("You've clicked %s times!" % int(result["num_clicks"]))

st.markdown("---")
st.subheader("Component with variable args")

# `key` keeps this instance stable while `name` changes. The wrapper sends
# `name` to the frontend in `data`.
name_input = st.text_input("Enter a name", value="Streamlit")
result = my_component(name_input, key="foo")
st.markdown("You've clicked %s times!" % int(result["num_clicks"]))
