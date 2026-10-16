# streamlit-custom-component

Streamlit component that allows you to do X

## Installation instructions

```sh
uv pip install streamlit-custom-component
```

## Local development

Build the frontend before the first run. Streamlit loads the files in `my_component/frontend/build`, and each `js=` / `css=` glob must match exactly one file there.

From `my_component/frontend`:

```sh
npm install
npm run build
```

From the project root:

```sh
uv pip install -e . --force-reinstall
streamlit run example.py
```

While editing the frontend, run `npm run dev` in `my_component/frontend`. That runs Vite in watch mode. If a glob matches more than one file, run `npm run clean` and build again.

## Usage instructions

```python
import streamlit as st

from my_component import my_component

value = my_component()

st.write(value)
```

## Build a wheel

To package this component for distribution:

1. Build the frontend with Vite (from `my_component/frontend`):

   ```sh
   npm install
   npm run build
   ```

2. Build the Python wheel using UV (from the project root):
   ```sh
   uv build
   ```

This will create a `dist/` directory containing your wheel. The wheel includes the compiled frontend from `my_component/frontend/build`.

### Requirements

- Python >= 3.10
- Node.js >= 24 (LTS)

### Expected output

- `dist/streamlit_custom_component-0.0.1-py3-none-any.whl`
- If you run `uv run --with build python -m build` (without `--wheel`), you’ll also get an sdist: `dist/streamlit-custom-component-0.0.1.tar.gz`
