import streamlit as st

out = st.components.v2.component(
    "{{ cookiecutter.package_name }}.{{ cookiecutter.import_name }}",
    js="index-*.js",
    {%- if cookiecutter.framework == "React + Typescript" %}
    html='<div class="react-root"></div>',
    {%- else %}
    html="""
        <div class="component-root">
            <span>
                <h1></h1>
                <button>Click me!</button>
            </span>
        </div>
    """,
    {%- endif %}
)


def on_num_clicks_change():
    """Callback function for when the number of clicks changes in the frontend."""
    pass


# Create a wrapper function for the component.
#
# This is an optional best practice. We could simply expose the component
# function returned by `st.components.v2.component` and call it done.
#
# The wrapper allows us to customize our component's API: we can pre-process its
# input args, post-process its output value, and add a docstring for users.
def {{ cookiecutter.import_name }}(name, key=None):
    """Create a new instance of "{{ cookiecutter.import_name }}".

    Parameters
    ----------
    name: str
        The name of the thing we're saying hello to. The component will display
        the text "Hello, {name}!"
    key: str or None
        An optional key that uniquely identifies this component.

    Returns
    -------
    Component state. ``num_clicks`` is the number of button clicks, sent from
    the frontend with ``setStateValue("num_clicks", ...)``.

    """
    # `data` is sent to the frontend on every run.
    # `default` initializes state keys that are not set yet. Each key needs a
    # matching `on_<key>_change` callback, or Streamlit rejects the mount.
    component_value = out(
        name=name,
        key=key,
        default={"num_clicks": 0},
        data={"name": name},
        on_num_clicks_change=on_num_clicks_change,
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
