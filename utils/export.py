"""CSV and Excel download helpers."""

import io

import pandas as pd
import streamlit as st


def download_csv_button(df: pd.DataFrame, filename: str, label: str = "Download CSV"):
    """Render a CSV download button for a DataFrame."""
    csv_data = df.to_csv(index=False)
    st.download_button(
        label=label,
        data=csv_data,
        file_name=filename,
        mime="text/csv",
    )


def download_excel_button(df: pd.DataFrame, filename: str, label: str = "Download Excel"):
    """Render an Excel download button for a DataFrame."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
    buffer.seek(0)
    st.download_button(
        label=label,
        data=buffer,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
