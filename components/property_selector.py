"""Sidebar property picker for Search Console properties."""

from typing import Optional

import streamlit as st

from api.sites import list_sites


def format_property_name(site_url: str) -> str:
    """Format a property URL for display."""
    if site_url.startswith("sc-domain:"):
        domain = site_url.replace("sc-domain:", "")
        return f"Domain: {domain}"
    return f"URL prefix: {site_url}"


def render_property_selector() -> Optional[str]:
    """Render a property selector in the sidebar. Returns the selected site URL or None."""
    sites = list_sites()

    if not sites:
        st.sidebar.warning("No Search Console properties found for this account.")
        return None

    options = [s["siteUrl"] for s in sites]
    labels = [format_property_name(url) for url in options]

    # Restore previous selection if available
    default_index = 0
    if "selected_property" in st.session_state:
        prev = st.session_state["selected_property"]
        if prev in options:
            default_index = options.index(prev)

    selected_label = st.sidebar.selectbox(
        "Property",
        labels,
        index=default_index,
        key="property_selector",
    )

    selected_url = options[labels.index(selected_label)]
    st.session_state["selected_property"] = selected_url

    # Show permission level
    site_info = next(s for s in sites if s["siteUrl"] == selected_url)
    st.sidebar.caption(f"Permission: {site_info.get('permissionLevel', 'N/A')}")

    return selected_url
