import streamlit as st
from my_component import my_component

# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run my_component/example.py`
value = my_component(my_input_value="""
let squareX, squareY;  // Position of square button
let circleX, circleY;  // Position of circle button
let squareSize = 90;   // Width/height of square
let circleSize = 93;   // Diameter of circle

let squareColor;
let circleColor;
let baseColor;

let squareOver = false;
let circleOver = false;

function setup() {
  createCanvas(710, 400);
  squareColor = color(0);
  circleColor = color(255);
  baseColor = color(102);
  circleX = width/2+circleSize/2+10;
  circleY = height/2;
  squareX = width/2-squareSize-10;
  squareY = height/2-squareSize/2;
}

function draw() {
  update(mouseX, mouseY);

  noStroke();
  if (squareOver) {
    background(squareColor, 1);
  } else if (circleOver) {
    background(circleColor, 1);
  } else {
    background(baseColor, 1);
  }

  stroke(255);
  fill(squareColor);
  square(squareX, squareY, squareSize);
  stroke(0);
  fill(circleColor);
  circle(circleX, circleY, circleSize);
}

function update(x, y) {
  if( overCircle(circleX, circleY, circleSize) ) {
    circleOver = true;
    squareOver = false;
  } else if ( overSquare(squareX, squareY, squareSize) ) {
    squareOver = true;
    circleOver = false;
  } else {
    circleOver = squareOver = false;
  }
}

function overSquare(x, y, size) {
  if (mouseX >= x && mouseX <= x+size && 
      mouseY >= y && mouseY <= y+size) {
    return true;
  } else {
    return false;
  }
}

function overCircle(x, y, diameter) {
  const disX = x - mouseX;
  const disY = y - mouseY;
  if(sqrt(sq(disX) + sq(disY)) < diameter/2 ) {
    return true;
  } else {
    return false;
  }
}
""", width=700, height=500)
st.write("Received", value)
