"""Coastal Debt - Search Console Dashboard."""

from datetime import date, timedelta

import streamlit as st

st.set_page_config(
    page_title="Coastal Debt - Search Console",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

from api.client import get_credentials, get_last_error
from api.search_analytics import get_performance_over_time, query_search_analytics, get_top_queries, get_top_pages
from utils.formatting import format_number, format_ctr, format_position, format_delta, format_ctr_delta, format_position_delta
from components.charts import performance_line_chart
from components.tips import show_kpi_tips, show_general_seo_tips

SITE_URL = "sc-domain:coastaldebt.com"


def main():
    import os
    from pathlib import Path

    creds = get_credentials()
    if not creds:
        # Debug info for deployment troubleshooting
        base = Path(__file__).resolve().parent
        token_path = base / "tokens" / "token.json"
        has_env = bool(os.environ.get("GOOGLE_TOKEN_JSON", ""))
        st.error("No API token found.")
        st.code(
            "Token file exists: {}\n"
            "Token file path: {}\n"
            "GOOGLE_TOKEN_JSON env var set: {}\n"
            "Working dir: {}\n"
            "Project dir: {}\n"
            "Error: {}".format(
                token_path.exists(), token_path, has_env, os.getcwd(), base,
                get_last_error()
            )
        )
        st.info("Set the GOOGLE_TOKEN_JSON environment variable or run `python3 setup_auth.py` locally.")
        st.stop()

    with st.sidebar:
        st.title("Coastal Debt")
        st.caption("coastaldebt.com")

    st.title("Dashboard Overview")

    # Date ranges
    end = date.today() - timedelta(days=3)
    start_current = end - timedelta(days=27)
    end_previous = start_current - timedelta(days=1)
    start_previous = end_previous - timedelta(days=27)

    # Fetch totals
    current_df = query_search_analytics(SITE_URL, start_current.isoformat(), end.isoformat(), [])
    previous_df = query_search_analytics(SITE_URL, start_previous.isoformat(), end_previous.isoformat(), [])

    cur_clicks = current_df["clicks"].sum() if not current_df.empty else 0
    cur_impressions = current_df["impressions"].sum() if not current_df.empty else 0
    cur_ctr = current_df["ctr"].mean() if not current_df.empty else 0
    cur_position = current_df["position"].mean() if not current_df.empty else 0

    prev_clicks = previous_df["clicks"].sum() if not previous_df.empty else 0
    prev_impressions = previous_df["impressions"].sum() if not previous_df.empty else 0
    prev_ctr = previous_df["ctr"].mean() if not previous_df.empty else 0
    prev_position = previous_df["position"].mean() if not previous_df.empty else 0

    # KPI cards
    st.markdown("**Last 28 days** ({} to {})".format(start_current, end))
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Clicks", format_number(cur_clicks), format_delta(cur_clicks, prev_clicks))
    col2.metric("Total Impressions", format_number(cur_impressions), format_delta(cur_impressions, prev_impressions))
    col3.metric("Average CTR", format_ctr(cur_ctr), format_ctr_delta(cur_ctr, prev_ctr))
    col4.metric("Average Position", format_position(cur_position), format_position_delta(cur_position, prev_position))

    # KPI-based tips
    show_kpi_tips(cur_clicks, cur_impressions, cur_ctr, cur_position)

    # Trend chart
    st.subheader("Performance Trend")
    trend_df = get_performance_over_time(SITE_URL, start_current.isoformat(), end.isoformat())
    if not trend_df.empty:
        fig = performance_line_chart(trend_df)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No performance data available.")

    # Quick summary tables
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Top 10 Queries")
        queries_df = get_top_queries(SITE_URL, start_current.isoformat(), end.isoformat(), row_limit=10)
        if not queries_df.empty:
            display = queries_df[["query", "clicks", "impressions"]].copy()
            display.columns = ["Query", "Clicks", "Impressions"]
            st.dataframe(display, use_container_width=True, hide_index=True)

    with col_right:
        st.subheader("Top 10 Pages")
        pages_df = get_top_pages(SITE_URL, start_current.isoformat(), end.isoformat(), row_limit=10)
        if not pages_df.empty:
            display = pages_df[["page", "clicks", "impressions"]].copy()
            display["page"] = display["page"].str.replace("https://www.coastaldebt.com", "", regex=False)
            display.columns = ["Page", "Clicks", "Impressions"]
            st.dataframe(display, use_container_width=True, hide_index=True)


    # Sidebar SEO tip
    show_general_seo_tips()


if __name__ == "__main__":
    main()
