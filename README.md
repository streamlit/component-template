# streamlit_p5

Embed your processing sketches in Streamlit! Check out the demo [here](https://streamlit-p5-examples.fly.dev/)

You can find the source code at: [https://github.com/salable/streamlit-p5](https://github.com/salable/streamlit-p5)

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
- data : a Python dict to pass to the p5 sketch

### Example:

#### Basic 

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

#### Advanced

```python
import streamlit as st
from streamlit_p5 import sketch

value = sketch("""
let word=""
function setup() { 
  createCanvas(700, 500);
  noStroke();
  word=dataToPass.name. // get value passed from Streamlit
}

function draw() {
  background(204, 120);
  fill(0)
  textFont('Courier New')
  textSize(50)
  text(word, mouseX, mouseY)
}

function mousePressed() {
  sendDataToPython({  //Send data to Streamlit - causes a re-render
          value: {
            mouseX: mouseX,
            mouseY: mouseY
          },
          dataType: "json",
        })
}
""", data={
  "name" : "Bob the Builder"
}, width=700, height=500)
```

Wanna build this from source? just run: 

```sh
python setup.py sdist bdist_wheel && twine upload dist/*
```