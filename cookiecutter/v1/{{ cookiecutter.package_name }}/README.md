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

## Local development

1. Start Streamlit from the project root:

   ```sh
   streamlit run {{ cookiecutter.import_name }}/example.py
   ```

2. In another terminal, run the Vite dev server from `{{ cookiecutter.import_name }}/frontend`:

   ```sh
   npm install
   npm run start
   ```

### Important dev server notes

- The browser connects to the Vite dev server directly. Streamlit does **not** proxy this port, so the Vite port must be reachable from the client just like the Streamlit port.
- Vite listens on the value of `VITE_PORT` (default `3001`). This variable lives in `{{ cookiecutter.import_name }}/frontend/.env`. Update that file whenever you need to change the port, and remember that Windows/WSL/Hyper-V or dev containers may silently remap addresses like `3001`.
- If a port is unavailable or blocked by a firewall/mobile connection, set `VITE_PORT=5173` (Vite's default) or any other open port inside the `.env` file before running `npm run start`, and ensure that port is reachable from your browser.
