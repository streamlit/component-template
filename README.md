# streamlit_sp5

Embed your processing sketches in Streamlit!

## Installation instructions

```sh
pip install streamlit streamlit_p5
```

## Quickstart

```python
streamlit run example.py
```

## Usage instructions

The `sketch` object takes a few arguments: 

- sketch : a string representing your P5js sketch
- width : width of the element in Streamlit
- height : height of the element in Streamlit (make sure to match these with your sketch!)

### Example:

```python
import streamlit as st
from streamlit_p5 import sketch

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
```

Wanna build this from source? just run: 

```sh
python setup.py sdist bdist_wheel
```