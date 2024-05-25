# streamlit-p5

Embed your processing sketches in Streamlit!

## Installation instructions

```sh
pip install streamlit-p5
```

## Usage instructions

```python
import streamlit as st
from streamlit_p5 import sketch

p5_sketch = sketch("""
import streamlit as st
from streamlit_p5 import sketch
value = sketch(st.session_state.selected, width=700, height=500)
st.write("*Code:*")
st.code(st.session_state.selected)
""", width=700, height=500)


```