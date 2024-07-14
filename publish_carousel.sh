#!/bin/bash

arg=$1
if [ "$arg" = "patch" ] || [ "$arg" = "minor" ] || [ "$arg" = "major" ]; then
  echo "Publishing '$arg' version"
else
  echo "Invalid argument. Please use 'patch', 'minor', or 'major'."
  /bin/bash
fi

cd bootstrap_carousel
bumpver update --$arg

echo "Building package..."
python -m build
echo "Publishing package..."
twine upload dist/*

echo "Pushing updates..."
cd ..
commit -m "bumped Streamlit Carousel version: $arg update"
commit push

echo "Streamlit Carousel successfully published!"
/bin/bash