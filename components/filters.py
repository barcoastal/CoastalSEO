"""Filter components for Search Analytics."""

from datetime import date, timedelta
from typing import List, Dict, Optional, Tuple

import streamlit as st

from utils.constants import SEARCH_TYPES, DEVICES, DATE_RANGE_PRESETS


def render_date_range_filter() -> Tuple[date, date]:
    """Render a date range filter with presets. Returns (start_date, end_date)."""
    col1, col2 = st.columns([1, 2])

    with col1:
        preset = st.selectbox(
            "Date range",
            list(DATE_RANGE_PRESETS.keys()) + ["Custom"],
            index=1,  # Default: Last 28 days
            key="date_preset",
        )

    end_date = date.today() - timedelta(days=3)

    if preset == "Custom":
        with col2:
            c1, c2 = st.columns(2)
            with c1:
                start_date = st.date_input(
                    "Start date",
                    value=end_date - timedelta(days=28),
                    max_value=end_date,
                    key="custom_start",
                )
            with c2:
                end_date = st.date_input(
                    "End date",
                    value=end_date,
                    max_value=end_date,
                    key="custom_end",
                )
    else:
        days = DATE_RANGE_PRESETS[preset]
        start_date = end_date - timedelta(days=days - 1)

    return start_date, end_date


def render_search_type_filter() -> str:
    """Render a search type filter. Returns the selected search type key."""
    return st.selectbox(
        "Search type",
        list(SEARCH_TYPES.keys()),
        format_func=lambda x: SEARCH_TYPES[x],
        key="search_type_filter",
    )


def render_query_filter() -> Optional[List[Dict]]:
    """Render a query filter input. Returns a dimension filter list or None."""
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        filter_enabled = st.checkbox("Filter by query", key="query_filter_enabled")

    if not filter_enabled:
        return None

    with col2:
        operator = st.selectbox(
            "Operator",
            ["contains", "notContains", "equals", "notEquals", "includingRegex", "excludingRegex"],
            key="query_operator",
        )

    with col3:
        expression = st.text_input("Query expression", key="query_expression")

    if not expression:
        return None

    return [{"dimension": "query", "operator": operator, "expression": expression}]


def render_page_filter() -> Optional[List[Dict]]:
    """Render a page URL filter input. Returns a dimension filter list or None."""
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        filter_enabled = st.checkbox("Filter by page", key="page_filter_enabled")

    if not filter_enabled:
        return None

    with col2:
        operator = st.selectbox(
            "Operator",
            ["contains", "notContains", "equals", "notEquals", "includingRegex", "excludingRegex"],
            key="page_operator",
        )

    with col3:
        expression = st.text_input("Page URL expression", key="page_expression")

    if not expression:
        return None

    return [{"dimension": "page", "operator": operator, "expression": expression}]


def collect_dimension_filters() -> Optional[List[Dict]]:
    """Collect all active dimension filters into one list."""
    filters = []
    query_filters = render_query_filter()
    if query_filters:
        filters.extend(query_filters)
    page_filters = render_page_filter()
    if page_filters:
        filters.extend(page_filters)
    return filters or None
