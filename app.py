import streamlit as st
from streamlit_p5 import sketch

st.title("Hello")

p5_sketch = sketch("""
function setup() {
   createCanvas(700, 500);
}

// The background function is a statement that tells the computer
// which color (or gray value) to make the background of the display window 
function draw() {
   background(204, 153, 0);
}
""", width=700, height=500)