# Streamlit Component Templates

Templates for creating [Streamlit](https://streamlit.io) Components. [Components v2](https://docs.streamlit.io/develop/concepts/custom-components/components-v2) is the way to build a new component. This repository is the official package template: generate a project from it, then customize. Components v1 is still supported for components that already use it.

## Components v2

v2 components are part of the Streamlit page. [Components v2](https://docs.streamlit.io/develop/concepts/custom-components/components-v2) covers registration, mounting, state versus trigger values, and packaged frontends. From the [overview](https://docs.streamlit.io/develop/concepts/custom-components/overview):

- Components render in the page. They are not isolated in an iframe.
- You can pass multiple callbacks. State values persist, and trigger values fire once per event.
- Data exchange includes JSON, dataframes (Apache Arrow), and bytes.
- You can prototype with HTML, CSS, and JavaScript from Python, or package a frontend with TypeScript and Vite.
- Theme values are available as CSS custom properties.

A packaged component registers a fully qualified name, points `js=` at a file under `asset_dir`, and declares each state key in `default` with a matching `on_<key>_change` callback:

```python
import streamlit as st

my_component = st.components.v2.component(
    "your-package.your_component",
    js="index-*.js",
    html="<button>Click</button>",
)

value = my_component(
    data={"name": "World"},
    default={"num_clicks": 0},
    on_num_clicks_change=lambda: None,
)
```

```tsx
import { FrontendRenderer } from "@streamlit/component-v2-lib";

const MyComponent: FrontendRenderer = ({ parentElement, data, setStateValue }) => {
  const button = parentElement.querySelector("button");
  if (!button) return;

  button.textContent = `Hello, ${data.name}!`;
  button.onclick = () => setStateValue("num_clicks", 1);
};

export default MyComponent;
```

Full templates: `templates/v2/template/` (React) and `templates/v2/template-reactless/` (TypeScript).

## Components v1 (legacy)

v1 is the original component API, stable since 2020. New components should use v2. v1 components run in an iframe, and the API is mainly one-way: Python sends arguments, and the component returns a single value.

```python
import streamlit.components.v1 as components

my_component = components.declare_component("my_component", path="frontend/build")
value = my_component(name="World", default=0)
```

Full templates: `templates/v1/template/` and `templates/v1/template-reactless/`.

## Quickstart

Install [uv](https://docs.astral.sh/uv/), [Node.js](https://nodejs.org) 24, and npm. Generate a project with Cookiecutter:

```bash
uvx --from cookiecutter cookiecutter gh:streamlit/component-template --directory cookiecutter/v2
```

For a legacy v1 component:

```bash
uvx --from cookiecutter cookiecutter gh:streamlit/component-template --directory cookiecutter/v1
```

Follow the prompts, then the `README` in the generated project. Sample apps install with `uv` and build the frontend with Vite.

## Pre-generated templates

The `templates/` directory is the cookiecutter output, so you can read a complete project without generating one:

- v2: `templates/v2/template/` and `templates/v2/template-reactless/`
- v1: `templates/v1/template/` and `templates/v1/template-reactless/`

## Community-provided templates

These templates are maintained outside this repo. File issues against their repositories.

- [streamlit-component-svelte-template](https://github.com/93degree/streamlit-component-svelte-template) - [@93degree](https://github.com/93degree)
- [streamlit-component-vue-vite-template](https://github.com/gabrieltempass/streamlit-component-vue-vite-template) - [@gabrieltempass](https://github.com/gabrieltempass)
- [streamlit-component-template-vue](https://github.com/andfanilo/streamlit-component-template-vue) - [@andfanilo](https://github.com/andfanilo)
- [streamlit-component-template-react-hooks](https://github.com/whitphx/streamlit-component-template-react-hooks) - [@whitphx](https://github.com/whitphx)

## Contributing

`./dev.py` refreshes the rendered templates and checks that they still match the cookiecutter sources. See `CONTRIBUTING.md`.

## More information

- [Custom components overview](https://docs.streamlit.io/develop/concepts/custom-components/overview)
- [Streamlit Forums](https://discuss.streamlit.io/tag/custom-components)
- [Streamlit Components gallery](https://www.streamlit.io/components)
