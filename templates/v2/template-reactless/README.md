# streamlit-custom-component

Streamlit component that allows you to do X

## Installation instructions

```sh
uv pip install streamlit-custom-component
```

## Usage instructions

```python
import streamlit as st

from my_component import my_component

value = my_component()

st.write(value)
```

## Build a wheel

To package this component for distribution:

1. Build the frontend assets (from `my_component/frontend`):

   ```sh
   npm i
   npm run build
   ```

2. Build the Python wheel using UV (from the project root with `pyproject.toml`):
   ```sh
   uv run --with build python -m build --wheel
   ```

This will create a `dist/` directory containing your wheel. The wheel includes the compiled frontend from `my_component/frontend/build`.

### Requirements

- Python >= 3.10
- Node.js >= 24 (LTS)

### Expected output

- `dist/streamlit_custom_component-0.0.1-py3-none-any.whl`
- If you run `uv run --with build python -m build` (without `--wheel`), you’ll also get an sdist: `dist/streamlit-custom-component-0.0.1.tar.gz`
