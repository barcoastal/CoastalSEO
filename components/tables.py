"""Formatted DataFrame renderers for analytics tables."""

import pandas as pd
import streamlit as st

from utils.formatting import format_number, format_ctr, format_position
from utils.export import download_csv_button, download_excel_button


def render_analytics_table(
    df: pd.DataFrame,
    key_column: str,
    filename_prefix: str = "data",
    page_size: int = 25,
):
    """Render a formatted analytics table with pagination and download buttons.

    Expects columns: [key_column, clicks, impressions, ctr, position].
    """
    if df.empty:
        st.info("No data available.")
        return

    # Format for display
    display_df = df.copy()
    display_df["ctr"] = display_df["ctr"].apply(format_ctr)
    display_df["position"] = display_df["position"].apply(format_position)

    # Rename columns for display
    col_names = {
        "clicks": "Clicks",
        "impressions": "Impressions",
        "ctr": "CTR",
        "position": "Avg. Position",
    }
    if key_column in ("query", "page", "country", "device"):
        col_names[key_column] = key_column.capitalize()
    display_df = display_df.rename(columns=col_names)

    # Show row count
    st.caption(f"{len(display_df):,} rows")

    # Paginate
    total_pages = max(1, (len(display_df) - 1) // page_size + 1)
    page = st.number_input(
        "Page",
        min_value=1,
        max_value=total_pages,
        value=1,
        key=f"page_{filename_prefix}",
    )
    start = (page - 1) * page_size
    end = start + page_size

    st.dataframe(
        display_df.iloc[start:end],
        use_container_width=True,
        hide_index=True,
    )

    # Download buttons
    col1, col2 = st.columns(2)
    with col1:
        download_csv_button(df, f"{filename_prefix}.csv")
    with col2:
        download_excel_button(df, f"{filename_prefix}.xlsx")
