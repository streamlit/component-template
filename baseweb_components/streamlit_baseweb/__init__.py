import os

import streamlit as st
import streamlit.components.v1 as components

_RELEASE = False

__title__ = "Baseweb UI"
__author__ = "Thomas Bouamoud"

if not _RELEASE:
    _base_web_modal = components.declare_component(
        "base_web_modal", url="http://localhost:3000",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    modal_dir = os.path.join(parent_dir, "baseweb_components/modal/frontend/build")
    _base_web_modal = components.declare_component("base_web_modal", path=modal_dir)


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
    modal_css = """
    div[data-stale="false"]>iframe[title="streamlit_baseweb.base_web_modal"] {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 9999;
    }

    .stApp {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        color: rgba(0, 0, 0, 0.5);
        z-index: 9998;
    }    
        """
    st.markdown(f"<style>{modal_css}</style>", unsafe_allow_html=True)
