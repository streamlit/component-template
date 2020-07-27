import os
import streamlit.components.v1 as components

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = False

# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

if not _RELEASE:
    _component_func = components.declare_component(
        # We give the component a simple, descriptive name ("my_component"
        # does not fit this bill, so please choose something better for your
        # own component :)
        "my_component",
        # Pass `url` here to tell Streamlit that the component will be served
        # by the local dev server that you run via `npm run start`.
        # (This is useful while your component is in development.)
        url="http://localhost:3001",
    )
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("my_component", path=build_dir)


# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.
def my_component(url, cors_proxy=False):
    """TODO docstring"""
    # Call through to our private component function. Arguments we pass here
    # will be sent to the frontend, where they'll be available in an "args"
    # dictionary.
    #
    # "default" is a special argument that specifies the initial return
    # value of the component before the user has interacted with it.
    component_value = _component_func(url=url, cors_proxy=cors_proxy, default=0)

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value


# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run my_component/__init__.py`
if not _RELEASE:
    import streamlit as st

    st.sidebar.markdown("# Puzzle cheatsheet!")
    st.sidebar.image("https://i.imgur.com/59bBMJB.png")

    "## Puzzled Pint, July 2018"
    "http://puzzledpint.com/puzzles/july-2018"
    # st.subheader("Component with constant args")
    # my_component("http://puzzledpint.com/files/8315/3168/9544/05-science-v6.pdf")

    solutions = [
        "SNAKE EYES",
        "HORSE FEATHERS",
        "WHEN PIGS FLY",
        "MONKEY BUSINESS",
        "POCKET",
    ]
    valid = [False] * 5

    "# Puzzle 1"
    my_component("http://puzzledpint.com/files/9815/3168/9527/01-maze-v6.pdf", True)
    answer1 = st.text_input("Your answer:")
    if answer1 == solutions[0]:
        valid[0] = True
        st.success("Correct!")

    "# Puzzle 2"
    my_component("http://puzzledpint.com/files/8015/3168/9529/02-surgical-v6.pdf", True)
    answer2 = st.text_input("Puzzle 2")
    if answer2 == solutions[1]:
        valid[1] = True
        st.success("Correct!")

    "# Puzzle 3"
    my_component(
        "http://puzzledpint.com/files/8815/3168/9531/03-equipment-v6.pdf", True
    )
    answer3 = st.text_input("Puzzle 3")
    if answer3 == solutions[2]:
        valid[2] = True
        st.success("Correct!")

    "# Puzzle 4"
    my_component("http://puzzledpint.com/files/7315/3168/9536/04-eye-v6.pdf", True)
    answer4 = st.text_input("Puzzle 4")
    if answer4 == solutions[3]:
        valid[3] = True
        st.success("Correct!")

    "# Puzzle 5"
    my_component("http://puzzledpint.com/files/8315/3168/9544/05-science-v6.pdf", True)
    answer5 = st.text_input("Puzzle 5")
    if answer5 == solutions[4]:
        valid[4] = True
        st.success("Correct!")

    # if answer1 and answer2 and answer3 and answer4 and answer5:
    "# Metapuzzled"
    # my_component(
    #     "http://puzzledpint.com/files/5915/3168/9553/99-meta-SOLUTiON-v6.pdf", True,
    # )
    my_component("http://puzzledpint.com/files/6315/3168/9550/99-meta-v6.pdf", True)
    answerMeta = st.text_input("Metapuzzle")
    if answerMeta == "SKIN YOUR OWN SKUNK":
        st.success("Congratulations, you're done!")
        st.balloons()

    # Create an instance of our component with a constant `name` arg, and
    # print its output value.
    # num_clicks = my_component("World")
    # st.markdown("You've clicked %s times!" % int(num_clicks))

    # st.markdown("---")
    # st.subheader("Component with variable args")

    # Create a second instance of our component whose `name` arg will vary
    # based on a text_input widget.
    #
    # We use the special "key" argument to assign a fixed identity to this
    # component instance. By default, when a component's arguments change,
    # it is considered a new instance and will be re-mounted on the frontend
    # and lose its current state. In this case, we want to vary the component's
    # "name" argument without having it get recreated.
    # name_input = st.text_input("Enter a name", value="Streamlit")
    # num_clicks = my_component(name_input, key="foo")
    # st.markdown("You've clicked %s times!" % int(num_clicks))
