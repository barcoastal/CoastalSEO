"""Shared sidebar branding for all pages."""

from pathlib import Path

import streamlit as st

LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "logo.svg"


def render_sidebar():
    """Render the branded sidebar with logo."""
    with st.sidebar:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), use_container_width=True)
        else:
            st.title("Coastal Debt")
        st.caption("coastaldebt.com")
