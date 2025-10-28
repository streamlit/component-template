# Streamlit Component Templates

This repo contains templates and example code for creating [Streamlit](https://streamlit.io) Components.

For complete information, please see the [Streamlit Components documentation](https://docs.streamlit.io/en/latest/streamlit_components.html)!

## Overview

A Streamlit Component is made out of a Python API and a frontend (built using any web tech you prefer).

A Component can be used in any Streamlit app, can pass data between Python and frontend code, and can optionally be distributed on [PyPI](https://pypi.org/) for the rest of the world to use.

```python
import streamlit as st

# Declare the component
my_component = st.components.v2.component(
    "your-package.your_component",
    js="index-*.js",
    html='<div class="react-root"></div>',
)

# Use it directly or via a small wrapper
value = my_component(data={"name": "World"}, default={"num_clicks": 0})
```

```tsx
import { Component } from '@streamlit/component-v2-lib';
import { createRoot } from 'react-dom/client';

const MyComponent: Component = (args) => {
  const root = createRoot(args.parentElement.querySelector('.react-root'));
  root.render(<div>Hello, {args.data.name}!</div>);
};

export default MyComponent;
```

See full examples in `templates/v2/template/` and `templates/v2/template-reactless/`.

<details>
<summary>Show v1 code samples</summary>

```python
import streamlit.components.v1 as components

# Declare the component (v1)
my_component = components.declare_component("my_component", path="frontend/build")

# Use it
value = my_component(name="World", default=0)
```

```tsx
import {
  withStreamlitConnection,
  ComponentProps,
} from 'streamlit-component-lib';

function MyComponent({ args }: ComponentProps) {
  return <div>Hello, {args.name}!\n</div>;
}

export default withStreamlitConnection(MyComponent);
```

</details>

See full examples in `templates/v1/template/` and `templates/v1/template-reactless/`.

## Supported template versions

This repo provides templates for both Streamlit Component APIs:

- v2: Uses `st.components.v2.component()` and `@streamlit/component-v2-lib`.
- v1: Uses `st.components.v1.component()` and `streamlit-component-lib`.

## Quickstart (generate a new component with Cookiecutter)

- Ensure you have [uv](https://docs.astral.sh/uv/), [Node.js](https://nodejs.org), and [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) installed.
- Generate from this template using Cookiecutter via `uvx`:

  - v2 (recommended):

    ```bash
    uvx --from cookiecutter cookiecutter gh:streamlit/component-template --directory cookiecutter/v2
    ```

  - v1:
    ```bash
    uvx --from cookiecutter cookiecutter gh:streamlit/component-template --directory cookiecutter/v1
    ```

- Follow the interactive prompts to generate your project.
- Once created, follow the `README` in your new project to get started.

## Just browsing? Pre-generated outputs

If you want to quickly explore without running Cookiecutter, browse the pre-generated templates in this repo:

- v2 outputs: `templates/v2/template/` and `templates/v2/template-reactless/`
- v1 outputs: `templates/v1/template/` and `templates/v1/template-reactless/`

From within one of these folders, you can inspect the Python package layout and the `my_component/frontend` code. Refer to the template-level `README` for build instructions.

## Examples

See the `examples/v1/` directory for examples working with pandas DataFrames, integrating with third-party libraries, and more.

## Community-provided Templates

These templates are provided by the community. If you run into any issues, please file your issues against their repositories.

- [streamlit-component-svelte-template](https://github.com/93degree/streamlit-component-svelte-template) - [@93degree](https://github.com/93degree)
- [streamlit-component-vue-vite-template](https://github.com/gabrieltempass/streamlit-component-vue-vite-template) - [@gabrieltempass](https://github.com/gabrieltempass)
- [streamlit-component-template-vue](https://github.com/andfanilo/streamlit-component-template-vue) - [@andfanilo](https://github.com/andfanilo)
- [streamlit-component-template-react-hooks](https://github.com/whitphx/streamlit-component-template-react-hooks) - [@whitphx](https://github.com/whitphx)

## Contributing

If you want to contribute to this project, `./dev.py` script will be helpful for you. For details, run `./dev.py --help`.

## More Information

- [Streamlit Components documentation](https://docs.streamlit.io/library/components)
- [Streamlit Forums](https://discuss.streamlit.io/tag/custom-components)
- [Streamlit Components gallery](https://www.streamlit.io/components)
