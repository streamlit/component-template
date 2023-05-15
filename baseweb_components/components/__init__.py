import os
import streamlit.components.v1 as components

_RELEASE = False

__title__ = "Baseweb UI"
__author__ = "Thomas Bouamoud"


if not _RELEASE:
    _base_web_button = components.declare_component(
        "base_web_button", url="http://localhost:3001",
    )
    _base_web_modal = components.declare_component(
        "base_web_modal", url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    button_dir = os.path.join(parent_dir, "baseweb_components/button/frontend/build")
    _base_web_button = components.declare_component("base_web_button", path=button_dir)
    modal_dir = os.path.join(parent_dir, "baseweb_components/modal/frontend/build")
    _base_web_modal = components.declare_component("base_web_modal", path=modal_dir)


def base_web_button(
    label: str = "you forgot to add a label to your button",
    disabled: bool = False,
    size: str = "default",
    shape: str = "default",
    kind: str = "primary",
    key=None,
) -> None:
    """"""
    _base_web_button(
        label=label,
        disabled=disabled,
        size=size,
        shape=shape,
        kind=kind,
        key=key,
        default=0,
    )


def base_web_modal(
    title: str,
    body: str,
    is_open: bool = False,
    role: str = "dialog",
    size: str = "default",
    key=None,
):
    """

    Parameters
    ----------
    title: modal's title
    body: modal's body
    is_open: modal's initial state
    role: options are 'dialog' or 'alertdialog'
    size: options are 'default', 'full', 'auto'
    -------

    """
    _base_web_modal(
        title=title,
        body=body,
        is_open=is_open,
        role=role,
        size=size,
        key=key,
        default=0,
    )
