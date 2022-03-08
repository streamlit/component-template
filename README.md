# Streamlit Component Templates

This repo contains templates and example code for creating [Streamlit](https://streamlit.io) Components.

For complete information, please see the [Streamlit Components documentation](https://docs.streamlit.io/en/latest/streamlit_components.html)!

## Overview

A Streamlit Component is made out of a Python API and a frontend (built using any web tech you prefer). 

A Component can be used in any Streamlit app, can pass data between Python and frontend code, and and can optionally be distributed on [PyPI](https://pypi.org/) for the rest of the world to use.

* Create a component's API in a single line of Python:
```python
import streamlit.components.v1 as components

# Declare the component:
my_component = components.declare_component("my_component", path="frontend/build")

# Use it:
my_component(greeting="Hello", name="World")
```

* Build the component's frontend out of HTML and JavaScript (or TypeScript, or ClojureScript, or whatever you fancy). React is supported, but not required:
```typescript
class MyComponent extends StreamlitComponentBase {
    public render(): ReactNode {
        // Access arguments from Python via `this.props.args`:
        const greeting = this.props.args["greeting"]
        const name = this.props.args["name"]
        return <div>{greeting}, {name}!</div>
    }
}
```

## Quickstart

* Ensure you have [Python 3.6+](https://www.python.org/downloads/), [Node.js](https://nodejs.org), and [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) installed.
* Clone this repo.
* Create a new Python virtual environment for the template:
```
$ cd template
$ python3 -m venv venv  # create venv
$ . venv/bin/activate   # activate venv
$ pip install streamlit # install streamlit
```
* Initialize and run the component template frontend:
```
$ cd template/my_component/frontend
$ npm install    # Install npm dependencies
$ npm run start  # Start the Webpack dev server
```
* From a separate terminal, run the template's Streamlit app:
```
$ cd template
$ . venv/bin/activate  # activate the venv you created earlier
$ streamlit run my_component/__init__.py  # run the example
```
* If all goes well, you should see something like this:
![Quickstart Success](quickstart.png)
* Modify the frontend code at `my_component/frontend/src/MyComponent.tsx`.
* Modify the Python code at `my_component/__init__.py`.

## Examples

See the `template-reactless` directory for a template that does not use [React](https://reactjs.org/).

See the `examples` directory for examples on working with pandas DataFrames, integrating with third-party libraries, and more.

## Community-provided Templates

These templates are provided by the community. If you run into any issues, please file your issues against their repositories.

- [streamlit-component-svelte-template](https://github.com/93degree/streamlit-component-svelte-template) - [@93degree](https://github.com/93degree)
- [streamlit-component-template-vue](https://github.com/andfanilo/streamlit-component-template-vue) - [@andfanilo](https://github.com/andfanilo)
- [streamlit-component-template-react-hooks](https://github.com/whitphx/streamlit-component-template-react-hooks) - [@whitphx](https://github.com/whitphx)

## More Information

* [Streamlit Components documentation](https://docs.streamlit.io/library/components)
* [Streamlit Forums](https://discuss.streamlit.io/tag/custom-components)
* [Streamlit Components gallery](https://www.streamlit.io/components)
