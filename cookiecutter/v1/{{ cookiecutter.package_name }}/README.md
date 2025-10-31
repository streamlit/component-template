# {{ cookiecutter.package_name }}

{{ cookiecutter.description }}

## Installation instructions

```sh
pip install {{ cookiecutter.package_name }}
```

## Usage instructions

```python
import streamlit as st

from {{ cookiecutter.import_name }} import {{ cookiecutter.import_name }}

value = {{ cookiecutter.import_name }}()

st.write(value)
```