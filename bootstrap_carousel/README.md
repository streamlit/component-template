# Streamlit Carousel

Streamlit Carousel is a Python package that provides a custom component for integrating the React Bootstrap Carousel into Streamlit applications.

## Installation

To install streamlit_carousel, use the following command:

```shell
pip install streamlit-carousel
```

## Usage

Once installed, you can use the streamlit_carousel component in your Streamlit application. Here's an example:

```python
from streamlit_carousel import carousel

test_items = [
    dict(
        title="Slide 1",
        text="A tree in the savannah",
        img="https://img.freepik.com/free-photo/wide-angle-shot-single-tree-growing-clouded-sky-during-sunset-surrounded-by-grass_181624-22807.jpg?w=1380&t=st=1688825493~exp=1688826093~hmac=cb486d2646b48acbd5a49a32b02bda8330ad7f8a0d53880ce2da471a45ad08a4",
        link="https://discuss.streamlit.io/t/new-component-react-bootstrap-carousel/46819",
    ),
    dict(
        title="Slide 2",
        text="A wooden bridge in a forest in Autumn",
        img="https://img.freepik.com/free-photo/beautiful-wooden-pathway-going-breathtaking-colorful-trees-forest_181624-5840.jpg?w=1380&t=st=1688825780~exp=1688826380~hmac=dbaa75d8743e501f20f0e820fa77f9e377ec5d558d06635bd3f1f08443bdb2c1",
        link="https://github.com/thomasbs17/streamlit-contributions/tree/master/bootstrap_carousel",
    ),
    dict(
        title="Slide 3",
        text="A distant mountain chain preceded by a sea",
        img="https://img.freepik.com/free-photo/aerial-beautiful-shot-seashore-with-hills-background-sunset_181624-24143.jpg?w=1380&t=st=1688825798~exp=1688826398~hmac=f623f88d5ece83600dac7e6af29a0230d06619f7305745db387481a4bb5874a0",
        link="https://github.com/thomasbs17/streamlit-contributions/tree/master",
    ),
    dict(
        title="Slide 4",
        text="PANDAS",
        img="pandas.webp",
    ),
    dict(
        title="Slide 4",
        text="CAT",
        img="cat.jpg",
    ),
]

carousel(items=test_items)
```

Please note that the images provided should be the path or URL to the image files.

## Known issues
- If an item's text is too long, it overflows on other items

## Contributing
Contributions to Streamlit Carousel are welcome! If you find any issues or have suggestions for improvements, please open an issue on the [GitHub repository](https://github.com/thomasbs17/streamlit-contributions/tree/master/bootstrap_carousel). If you'd like to contribute code, you can fork the repository, make your changes, and submit a pull request.

Before contributing, please review the [Contributing Guidelines](https://github.com/thomasbs17/streamlit-contributions/tree/master/bootstrap_carousel/README.md) for more information.

## License
This package is licensed under the MIT License. See the [LICENSE file](https://github.com/thomasbs17/streamlit-contributions/tree/master/bootstrap_carousel/LICENSE) for more information.

## Credits
Streamlit Carousel is created and maintained by Thomas Bouamoud. 
It leverages the [React Bootstrap Carousel component](https://react-bootstrap.netlify.app/docs/components/carousel/) and utilizes the Streamlit Custom Components feature.

## Contact
If you have any questions or inquiries, feel free to reach out to thomas.bouamoud@gmail.com.