import os
from typing import Literal

import streamlit as st
import streamlit.components.v1 as components

_RELEASE = True

__title__ = "Baseweb UI"
__author__ = "Thomas Bouamoud"

if not _RELEASE:
    _base_web_modal = components.declare_component(
        "base_web_modal", url="http://localhost:3000",
    )
    _base_web_button = components.declare_component(
        "base_web_button", url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    modal_dir = os.path.join(parent_dir, "modal/build")
    _base_web_modal = components.declare_component("base_web_modal", path=modal_dir)
    button_dir = os.path.join(parent_dir, "button/build")
    _base_web_button = components.declare_component("base_web_button", path=button_dir)


def base_web_modal(
    title: str,
    body: str,
    is_open: bool = True,
    role: Literal["dialog", "alertdialog"] = "dialog",
    size: Literal["full", "default", "auto"] = "full",
    validation_button_label: str = "Okay",
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
    validation_button_label: label to display for validation button
    -------

    """
    _base_web_modal(
        title=title,
        body=body,
        is_open=is_open,
        role=role,
        size=size,
        validation_button_label=validation_button_label,
        key=key,
        default=0,
    )
    modal_css = """
    div[data-stale="false"]>iframe[title="streamlit_baseweb.base_web_modal"] {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background-color: rgba(0, 0, 0, 1);
        z-index: 9999;
    }
    [data-baseweb="modal"] {
        background-color: rgba(0, 0, 0, 1);
    }
    [data-testid="stSidebar"] {
        display: none
    }
    [data-testid="stHeader"] {
        background-color: rgba(0, 0, 0, 1);
        color: rgba(255, 255, 255, 1);
    }
    .stApp {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 1);
        z-index: 9998;
    }    
        """
    st.sidebar.markdown(f"<style>{modal_css}</style>", unsafe_allow_html=True)


def base_web_button(
    label: str = "Submit",
    disabled: bool = False,
    size: Literal["default", "compact", "large"] = "default",
    shape: Literal["default", "pill", "round", "square"] = "default",
    kind: Literal["primary", "secondary", "tertiary"] = "primary",
    key=None,
) -> bool:
    """

    Parameters
    ----------
    label : str, optional
        The label or text to display on the button. Default is "Submit".
    disabled : bool, optional
        Whether the button should be disabled or not. Default is False.
    size : str, optional
        The size of the button. Available options are "default", "compact", and "large".
        Default is "default".
    shape : str, optional
        The shape of the button. Available options are "default", "pill", "round", and "square".
        Default is "default".
    kind : str, optional
        The kind or style of the button. Available options are "primary", "secondary", "tertiary",
        "minimal", and "outline". Default is "primary".
    key : Any, optional
        A unique identifier for the button. Default is None.

    Returns
    -------

    """
    if _base_web_button(
        label=label,
        disabled=disabled,
        size=size,
        shape=shape,
        kind=kind,
        key=key,
        default=0,
    ):
        return True
