"""Search Analytics dashboard with charts, tables, and filters."""

import streamlit as st

st.set_page_config(page_title="Search Analytics", page_icon="📊", layout="wide")

from api.client import get_credentials
from components.filters import (
    render_date_range_filter,
    render_search_type_filter,
    collect_dimension_filters,
)
from components.charts import (
    performance_line_chart,
    top_items_bar_chart,
    device_pie_chart,
    country_choropleth,
)
from components.tables import render_analytics_table
from api.search_analytics import (
    get_performance_over_time,
    get_top_queries,
    get_top_pages,
    get_country_breakdown,
    get_device_breakdown,
)
from utils.formatting import format_number, format_ctr, format_position
from components.tips import show_kpi_tips, show_query_tips, show_page_tips, show_device_tips, show_country_tips

SITE_URL = "sc-domain:coastaldebt.com"


def main():
    creds = get_credentials()
    if not creds:
        st.error("No API token found.")
        st.stop()

    st.title("Search Analytics")

    with st.expander("Filters", expanded=True):
        start_date, end_date = render_date_range_filter()
        col1, col2 = st.columns(2)
        with col1:
            search_type = render_search_type_filter()
        dimension_filters = collect_dimension_filters()

    start_str = start_date.isoformat()
    end_str = end_date.isoformat()

    tab_overview, tab_queries, tab_pages, tab_countries, tab_devices = st.tabs(
        ["Overview", "Queries", "Pages", "Countries", "Devices"]
    )

    with tab_overview:
        trend_df = get_performance_over_time(SITE_URL, start_str, end_str, search_type, dimension_filters)
        if not trend_df.empty:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Clicks", format_number(trend_df["clicks"].sum()))
            col2.metric("Total Impressions", format_number(trend_df["impressions"].sum()))
            col3.metric("Avg. CTR", format_ctr(trend_df["ctr"].mean()))
            col4.metric("Avg. Position", format_position(trend_df["position"].mean()))
            show_kpi_tips(
                trend_df["clicks"].sum(), trend_df["impressions"].sum(),
                trend_df["ctr"].mean(), trend_df["position"].mean()
            )
            fig = performance_line_chart(trend_df)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")

    with tab_queries:
        queries_df = get_top_queries(SITE_URL, start_str, end_str, search_type, dimension_filters)
        if not queries_df.empty:
            col1, col2 = st.columns(2)
            with col1:
                fig = top_items_bar_chart(queries_df, "query", "clicks", "Top Queries by Clicks")
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig = top_items_bar_chart(queries_df, "query", "impressions", "Top Queries by Impressions", "#5bb974")
                st.plotly_chart(fig, use_container_width=True)
            render_analytics_table(queries_df, "query", "queries")
            show_query_tips(queries_df)
        else:
            st.info("No query data available.")

    with tab_pages:
        pages_df = get_top_pages(SITE_URL, start_str, end_str, search_type, dimension_filters)
        if not pages_df.empty:
            fig = top_items_bar_chart(pages_df, "page", "clicks", "Top Pages by Clicks")
            st.plotly_chart(fig, use_container_width=True)
            render_analytics_table(pages_df, "page", "pages")
            show_page_tips(pages_df)
        else:
            st.info("No page data available.")

    with tab_countries:
        countries_df = get_country_breakdown(SITE_URL, start_str, end_str, search_type, dimension_filters)
        if not countries_df.empty:
            col1, col2 = st.columns([2, 1])
            with col1:
                fig = country_choropleth(countries_df, "clicks")
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig = top_items_bar_chart(countries_df, "country", "clicks", "Top Countries", "#1a73e8", 15)
                st.plotly_chart(fig, use_container_width=True)
            render_analytics_table(countries_df, "country", "countries")
            show_country_tips(countries_df)
        else:
            st.info("No country data available.")

    with tab_devices:
        devices_df = get_device_breakdown(SITE_URL, start_str, end_str, search_type, dimension_filters)
        if not devices_df.empty:
            col1, col2 = st.columns(2)
            with col1:
                fig = device_pie_chart(devices_df, "clicks")
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig = device_pie_chart(devices_df, "impressions")
                st.plotly_chart(fig, use_container_width=True)
            render_analytics_table(devices_df, "device", "devices")
            show_device_tips(devices_df)
        else:
            st.info("No device data available.")


main()
