"""Sitemap management UI."""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sitemaps", page_icon="🗺️", layout="wide")

from api.client import get_credentials
from api.sitemaps import list_sitemaps, submit_sitemap, delete_sitemap
from components.tips import tip_box

SITE_URL = "sc-domain:coastaldebt.com"


def main():
    creds = get_credentials()
    if not creds:
        st.error("No API token found.")
        st.stop()

    from components.sidebar import render_sidebar
    render_sidebar()

    st.title("Sitemap Management")

    tip_box("Sitemap Best Practices",
        "Keep your sitemap under 50K URLs and 50MB. Only include canonical, indexable pages. "
        "Remove any URLs returning 4xx/5xx errors. Update your sitemap whenever you publish or remove content. "
        "Submit both your main sitemap and a separate one for images if you have visual content.")

    st.subheader("Submit a Sitemap")
    with st.form("submit_sitemap_form"):
        sitemap_url = st.text_input("Sitemap URL", placeholder="https://www.coastaldebt.com/sitemap.xml")
        submitted = st.form_submit_button("Submit Sitemap", type="primary")
        if submitted and sitemap_url:
            if submit_sitemap(SITE_URL, sitemap_url):
                st.success("Sitemap submitted: {}".format(sitemap_url))
                st.rerun()
            else:
                st.error("Failed to submit sitemap.")

    st.divider()
    st.subheader("Existing Sitemaps")

    sitemaps = list_sitemaps(SITE_URL)
    if not sitemaps:
        st.info("No sitemaps found.")
        return

    for sm in sitemaps:
        sm_path = sm.get("path", "Unknown")
        with st.expander("**{}**".format(sm_path), expanded=False):
            col1, col2, col3 = st.columns(3)
            col1.write("**Type:** {}".format(sm.get("type", "N/A")))
            col2.write("**Last submitted:** {}".format(sm.get("lastSubmitted", "N/A")))
            col3.write("**Last downloaded:** {}".format(sm.get("lastDownloaded", "N/A")))

            col1, col2, col3 = st.columns(3)
            col1.write("**Pending:** {}".format("Yes" if sm.get("isPending") else "No"))
            col2.write("**Warnings:** {}".format(sm.get("warnings", 0)))
            col3.write("**Errors:** {}".format(sm.get("errors", 0)))

            contents = sm.get("contents", [])
            if contents:
                st.write("**Contents:**")
                rows = [{"Type": c.get("type", ""), "Submitted": c.get("submitted", 0), "Indexed": c.get("indexed", 0)} for c in contents]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            if st.button("Delete Sitemap", key="delete_{}".format(sm_path), type="secondary"):
                if delete_sitemap(SITE_URL, sm_path):
                    st.success("Deleted: {}".format(sm_path))
                    st.rerun()
                else:
                    st.error("Failed to delete.")


main()
