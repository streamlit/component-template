from typing import TYPE_CHECKING

import streamlit as st

if TYPE_CHECKING:
    from streamlit.components.v2.bidi_component import BidiComponentResult

out = st.components.v2.component(
    "{{ cookiecutter.package_name }}.{{ cookiecutter.import_name }}",
    js="index-*.js",
    html='<div class="react-root"></div>',
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
    int
        The number of times the component's "Click Me" button has been clicked.
        (This is the value passed to `Streamlit.setComponentValue` on the
        frontend.)

    """
    # Call through to our private component function. Arguments we pass here
    # will be sent to the frontend, where they'll be available in an "args"
    # dictionary.
    #
    # "default" is a special argument that specifies the initial return
    # value of the component before the user has interacted with it.
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
