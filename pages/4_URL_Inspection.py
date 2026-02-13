"""URL Inspection UI - single and batch inspection."""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="URL Inspection", page_icon="🔎", layout="wide")

from api.client import get_credentials
from api.url_inspection import inspect_url, batch_inspect_urls, format_inspection_result
from utils.constants import URL_INSPECTION_DAILY_QUOTA
from components.tips import tip_box

SITE_URL = "sc-domain:coastaldebt.com"

VERDICT_COLORS = {
    "PASS": "green", "PARTIAL": "orange", "FAIL": "red",
    "NEUTRAL": "gray", "VERDICT_UNSPECIFIED": "gray",
}


def render_badge(label, value):
    color = VERDICT_COLORS.get(value, "gray")
    st.markdown("**{}:** :{}[{}]".format(label, color, value))


def render_single_result(result):
    fmt = format_inspection_result(result)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Index Status")
        render_badge("Coverage", fmt["coverage_state"])
        render_badge("Indexing", fmt["indexing_state"])
        render_badge("Robots.txt", fmt["robots_txt_state"])
        render_badge("Page Fetch", fmt["page_fetch_state"])
        st.write("**Crawled as:** {}".format(fmt["crawled_as"]))
        st.write("**Last crawl:** {}".format(fmt["last_crawl_time"]))
    with col2:
        st.markdown("#### Additional Info")
        render_badge("Mobile Usability", fmt["mobile_usability"])
        render_badge("Rich Results", fmt["rich_results_verdict"])
        if fmt["referring_urls"]:
            st.write("**Referring URLs:**")
            for u in fmt["referring_urls"][:5]:
                st.write("- {}".format(u))
        if fmt["sitemap_urls"]:
            st.write("**Found in sitemaps:**")
            for u in fmt["sitemap_urls"][:5]:
                st.write("- {}".format(u))


def main():
    creds = get_credentials()
    if not creds:
        st.error("No API token found.")
        st.stop()

    st.title("URL Inspection")
    st.caption("Daily quota: {} inspections".format(URL_INSPECTION_DAILY_QUOTA))

    tip_box("URL Inspection Tips",
        "Use this tool to check if Google can find and index your important pages. "
        "Look for: **Coverage = Submitted and indexed** (good), **Crawled as = Googlebot smartphone** (mobile-first), "
        "and **Mobile Usability = PASS**. If a page shows 'Excluded', check for noindex tags, canonical issues, or robots.txt blocks.")

    tab_single, tab_batch = st.tabs(["Single URL", "Batch Inspection"])

    with tab_single:
        st.subheader("Inspect a Single URL")
        url_input = st.text_input("URL to inspect", placeholder="https://www.coastaldebt.com/page", key="single_url")
        if st.button("Inspect", type="primary", key="inspect_single"):
            if not url_input:
                st.warning("Please enter a URL.")
            else:
                with st.spinner("Inspecting URL..."):
                    try:
                        result = inspect_url(SITE_URL, url_input)
                        if result:
                            render_single_result(result)
                        else:
                            st.error("No result returned.")
                    except Exception as e:
                        st.error("Inspection failed: {}".format(e))

    with tab_batch:
        st.subheader("Batch URL Inspection")
        st.markdown("Enter one URL per line.")
        urls_text = st.text_area("URLs to inspect", height=200, key="batch_urls")
        if st.button("Inspect All", type="primary", key="inspect_batch"):
            urls = [u.strip() for u in urls_text.strip().split("\n") if u.strip()]
            if not urls:
                st.warning("Please enter at least one URL.")
            elif len(urls) > URL_INSPECTION_DAILY_QUOTA:
                st.error("Too many URLs. Max {} per day.".format(URL_INSPECTION_DAILY_QUOTA))
            else:
                progress_bar = st.progress(0, text="Inspecting URLs...")
                status_text = st.empty()

                def update_progress(current, total):
                    progress_bar.progress(current / total, text="Inspecting {}/{}...".format(current, total))
                    status_text.text("Processing: {}".format(urls[current - 1]))

                results = batch_inspect_urls(SITE_URL, urls, progress_callback=update_progress)
                progress_bar.progress(1.0, text="Done!")
                status_text.empty()

                table_data = []
                for r in results:
                    if r["error"]:
                        table_data.append({"URL": r["url"], "Coverage": "Error", "Indexing": r["error"], "Last Crawl": "N/A", "Mobile": "N/A"})
                    else:
                        f = format_inspection_result(r["result"])
                        table_data.append({"URL": r["url"], "Coverage": f["coverage_state"], "Indexing": f["indexing_state"], "Last Crawl": f["last_crawl_time"], "Mobile": f["mobile_usability"]})

                results_df = pd.DataFrame(table_data)
                st.dataframe(results_df, use_container_width=True, hide_index=True)
                st.download_button("Download CSV", results_df.to_csv(index=False), "url_inspection.csv", "text/csv")

                st.subheader("Detailed Results")
                for r in results:
                    with st.expander(r["url"]):
                        if r["error"]:
                            st.error(r["error"])
                        else:
                            render_single_result(r["result"])


main()
