# {{ cookiecutter.package_name }}

{{ cookiecutter.description }}

## Installation instructions

```sh
uv pip install {{ cookiecutter.package_name }}
```

## Local development

Build the frontend before the first run. Streamlit loads the files in `{{ cookiecutter.import_name }}/frontend/build`, and each `js=` / `css=` glob must match exactly one file there.

From `{{ cookiecutter.import_name }}/frontend`:

```sh
npm install
npm run build
```

From the project root:

```sh
uv pip install -e . --force-reinstall
streamlit run example.py
```

While editing the frontend, run `npm run dev` in `{{ cookiecutter.import_name }}/frontend`. That runs Vite in watch mode. If a glob matches more than one file, run `npm run clean` and build again.

## Usage instructions

```python
import streamlit as st

from {{ cookiecutter.import_name }} import {{ cookiecutter.import_name }}

value = {{ cookiecutter.import_name }}()

st.write(value)
```

## Build a wheel

To package this component for distribution:

1. Build the frontend with Vite (from `{{ cookiecutter.import_name }}/frontend`):

   ```sh
   npm install
   npm run build
   ```

2. Build the Python wheel using UV (from the project root):
   ```sh
   uv build
   ```

This will create a `dist/` directory containing your wheel. The wheel includes the compiled frontend from `{{ cookiecutter.import_name }}/frontend/build`.

### Requirements

- Python >= 3.10
- Node.js >= 24 (LTS)

### Expected output

- `dist/{{ cookiecutter.package_name|replace('-', '_') }}-0.0.1-py3-none-any.whl`
- If you run `uv run --with build python -m build` (without `--wheel`), you’ll also get an sdist: `dist/{{ cookiecutter.package_name }}-0.0.1.tar.gz`
