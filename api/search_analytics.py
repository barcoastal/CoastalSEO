"""Search Analytics API using direct REST calls with auto-pagination."""

from datetime import date, timedelta
from typing import List, Dict, Optional

import pandas as pd
import requests
import streamlit as st

from api.client import get_auth_headers
from utils.constants import CACHE_TTL, MAX_ROWS_PER_REQUEST

API_BASE = "https://searchconsole.googleapis.com/webmasters/v3/sites"


def _encode_site(site_url):
    return requests.utils.quote(site_url, safe="")


@st.cache_data(ttl=CACHE_TTL)
def query_search_analytics(
    site_url,
    start_date,
    end_date,
    dimensions=None,
    search_type="web",
    dimension_filters=None,
    row_limit=MAX_ROWS_PER_REQUEST,
    aggregation_type="auto",
):
    """Query Search Analytics with auto-pagination. Returns a DataFrame."""
    headers = get_auth_headers()
    if not headers:
        return pd.DataFrame()

    url = "{}/{}/searchAnalytics/query".format(API_BASE, _encode_site(site_url))
    all_rows = []
    start_row = 0
    dims = dimensions or []

    while True:
        body = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": dims,
            "rowLimit": min(row_limit, MAX_ROWS_PER_REQUEST),
            "startRow": start_row,
            "type": search_type,
            "aggregationType": aggregation_type,
        }
        if dimension_filters:
            body["dimensionFilterGroups"] = [{"filters": dimension_filters}]

        resp = requests.post(url, headers=headers, json=body)
        if resp.status_code != 200:
            break

        rows = resp.json().get("rows", [])
        if not rows:
            break

        for row in rows:
            entry = {}
            keys = row.get("keys", [])
            for i, dim in enumerate(dims):
                entry[dim] = keys[i] if i < len(keys) else ""
            entry["clicks"] = row.get("clicks", 0)
            entry["impressions"] = row.get("impressions", 0)
            entry["ctr"] = row.get("ctr", 0.0)
            entry["position"] = row.get("position", 0.0)
            all_rows.append(entry)

        start_row += len(rows)
        if len(rows) < min(row_limit, MAX_ROWS_PER_REQUEST):
            break
        if start_row >= row_limit:
            break

    return pd.DataFrame(all_rows)


def get_performance_over_time(site_url, start_date, end_date, search_type="web", dimension_filters=None):
    """Get daily performance metrics."""
    df = query_search_analytics(site_url, start_date, end_date, ["date"], search_type, dimension_filters)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
    return df


def get_top_queries(site_url, start_date, end_date, search_type="web", dimension_filters=None, row_limit=MAX_ROWS_PER_REQUEST):
    """Get top queries by clicks."""
    df = query_search_analytics(site_url, start_date, end_date, ["query"], search_type, dimension_filters, row_limit)
    if not df.empty:
        df = df.sort_values("clicks", ascending=False)
    return df


def get_top_pages(site_url, start_date, end_date, search_type="web", dimension_filters=None, row_limit=MAX_ROWS_PER_REQUEST):
    """Get top pages by clicks."""
    df = query_search_analytics(site_url, start_date, end_date, ["page"], search_type, dimension_filters, row_limit)
    if not df.empty:
        df = df.sort_values("clicks", ascending=False)
    return df


def get_country_breakdown(site_url, start_date, end_date, search_type="web", dimension_filters=None):
    """Get performance by country."""
    df = query_search_analytics(site_url, start_date, end_date, ["country"], search_type, dimension_filters)
    if not df.empty:
        df = df.sort_values("clicks", ascending=False)
    return df


def get_device_breakdown(site_url, start_date, end_date, search_type="web", dimension_filters=None):
    """Get performance by device."""
    df = query_search_analytics(site_url, start_date, end_date, ["device"], search_type, dimension_filters)
    if not df.empty:
        df = df.sort_values("clicks", ascending=False)
    return df


def get_query_page_combinations(site_url, start_date, end_date, search_type="web", dimension_filters=None, row_limit=MAX_ROWS_PER_REQUEST):
    """Get query + page combinations."""
    df = query_search_analytics(site_url, start_date, end_date, ["query", "page"], search_type, dimension_filters, row_limit)
    if not df.empty:
        df = df.sort_values("clicks", ascending=False)
    return df
