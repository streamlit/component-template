# Contributing to Streamlit component template

## Requirements

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/)
- Node.js 24 (LTS) and npm

Create a virtual environment from the repository root:

```sh
uv venv --python 3.13
source .venv/bin/activate
```

## Run a template locally

Install and build every template frontend:

```sh
./dev.py all-npm-install
./dev.py all-npm-build
```

### v2

v2 loads built files from `my_component/frontend/build`. Build that directory before the first run. From `templates/v2/template/my_component/frontend`:

```sh
npm install
npm run build
```

From `templates/v2/template`:

```sh
uv pip install -e . --force-reinstall
streamlit run example.py
```

`npm run dev` in the frontend directory runs Vite in watch mode while you edit. If `index-*.js` matches more than one file, run `npm run clean` and build again.

`template` and `template-reactless` both install as `streamlit-custom-component`. Only one can be installed at a time. Switch with:

```sh
uv pip uninstall streamlit-custom-component
cd templates/v2/template-reactless
uv pip install -e .
```

### v1

v1 templates keep `_RELEASE = False` while developing. That tells Streamlit to load the frontend from the Vite dev server at `http://localhost:3001`. Set `_RELEASE = True` only when building a wheel, and set it back to `False` before committing.

From `templates/v1/template`:

```sh
uv pip install -e .
uv run streamlit run my_component/example.py
```

In another terminal:

```sh
cd templates/v1/template/my_component/frontend
npm install
npm run start
```

The same package-name limit applies to `templates/v1/template` and `templates/v1/template-reactless`.

## Keeping rendered templates in sync

`templates/` is generated from `cookiecutter/`. After editing a cookiecutter source, refresh the rendered copies and check them:

```sh
uvx --from 'cookiecutter==2.2.2' cookiecutter --version
./dev.py templates-update
./dev.py templates-check-not-modified
```

Cookiecutter 2.2.3 breaks the replay files used by that check. `./dev.py --help` lists the other maintenance commands.
