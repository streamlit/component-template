# Streamlit Baseweb

Streamlit Baseweb is a Python package that provides custom components from the Baseweb framework, allowing you to enhance your Streamlit applications with beautiful and interactive UI elements.

## Installation

You can install Streamlit Baseweb using pip:

```shell
pip install streamlit-baseweb
```

## Usage

To use the Baseweb components in your Streamlit application, you need to import the necessary components from the '**streamlit_baseweb**' module and utilize them in your code. Here's an example:

```python
import streamlit as st
from streamlit_baseweb import base_web_modal

st.title("Testing Streamlit Baseweb")
if st.button(label="open modal"):
    base_web_modal(title="modal", body="testing modal", is_open=True, key="base_web_modal")

```

For more details on available components and their usage, refer to the package documentation.

## Contributing
Contributions to Streamlit Baseweb are welcome! If you find any issues or have suggestions for improvements, please open an issue on the [GitHub repository](https://github.com/thomasbs17/streamlit-contributions/tree/master/baseweb_components). If you'd like to contribute code, you can fork the repository, make your changes, and submit a pull request.

Before contributing, please review the [Contributing Guidelines](https://github.com/thomasbs17/streamlit-contributions/blob/master/baseweb_components/README.md) for more information.

## License
This package is licensed under the MIT License. See the [LICENSE file](https://github.com/thomasbs17/streamlit-contributions/blob/master/baseweb_components/LICENSE) for more information.

## Credits
Streamlit Baseweb is created and maintained by Thomas Bouamoud. 
It utilizes the Baseweb framework by [Uber](https://baseweb.design/).

## Contact
If you have any questions or inquiries, feel free to reach out to thomas.bouamoud@gmail.com.

## 👩‍💻 Happy Streamlit Baseweb coding! 👨‍💻