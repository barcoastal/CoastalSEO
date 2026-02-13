"""Plotly chart builders for Search Console data."""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def performance_line_chart(df: pd.DataFrame) -> go.Figure:
    """Create a dual-axis line chart for clicks, impressions, CTR, and position."""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.6, 0.4],
        subplot_titles=("Clicks & Impressions", "CTR & Position"),
    )

    # Clicks
    fig.add_trace(
        go.Scatter(
            x=df["date"], y=df["clicks"],
            name="Clicks",
            line=dict(color="#1a73e8", width=2),
            hovertemplate="%{y:,.0f} clicks<extra></extra>",
        ),
        row=1, col=1,
    )

    # Impressions on secondary y-axis
    fig.add_trace(
        go.Scatter(
            x=df["date"], y=df["impressions"],
            name="Impressions",
            line=dict(color="#5bb974", width=2),
            yaxis="y2",
            hovertemplate="%{y:,.0f} impressions<extra></extra>",
        ),
        row=1, col=1,
    )

    # CTR
    fig.add_trace(
        go.Scatter(
            x=df["date"], y=df["ctr"].apply(lambda x: x * 100),
            name="CTR (%)",
            line=dict(color="#f9ab00", width=2),
            hovertemplate="%{y:.2f}%<extra></extra>",
        ),
        row=2, col=1,
    )

    # Position (inverted axis - lower is better)
    fig.add_trace(
        go.Scatter(
            x=df["date"], y=df["position"],
            name="Position",
            line=dict(color="#e8710a", width=2),
            yaxis="y4",
            hovertemplate="Position %{y:.1f}<extra></extra>",
        ),
        row=2, col=1,
    )

    fig.update_layout(
        height=500,
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="x unified",
        yaxis=dict(title="Clicks", side="left"),
        yaxis2=dict(title="Impressions", side="right", overlaying="y"),
        yaxis3=dict(title="CTR (%)", side="left"),
        yaxis4=dict(title="Position", side="right", overlaying="y3", autorange="reversed"),
    )

    return fig


def top_items_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str = "clicks",
    title: str = "",
    color: str = "#1a73e8",
    top_n: int = 20,
) -> go.Figure:
    """Create a horizontal bar chart for top items (queries, pages, etc.)."""
    plot_df = df.head(top_n).sort_values(y_col, ascending=True)

    fig = go.Figure(
        go.Bar(
            x=plot_df[y_col],
            y=plot_df[x_col],
            orientation="h",
            marker_color=color,
            hovertemplate="%{y}<br>%{x:,.0f} " + y_col + "<extra></extra>",
        )
    )

    fig.update_layout(
        title=title,
        height=max(400, top_n * 25),
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis_title=y_col.capitalize(),
        yaxis_title="",
    )

    return fig


def device_pie_chart(df: pd.DataFrame, metric: str = "clicks") -> go.Figure:
    """Create a pie chart for device breakdown."""
    colors = {"DESKTOP": "#1a73e8", "MOBILE": "#5bb974", "TABLET": "#f9ab00"}

    fig = go.Figure(
        go.Pie(
            labels=df["device"],
            values=df[metric],
            marker=dict(colors=[colors.get(d, "#999999") for d in df["device"]]),
            hovertemplate="%{label}<br>%{value:,.0f} " + metric + "<br>%{percent}<extra></extra>",
            textinfo="label+percent",
        )
    )

    fig.update_layout(
        title=f"{metric.capitalize()} by Device",
        height=400,
        margin=dict(l=0, r=0, t=40, b=0),
    )

    return fig


def country_choropleth(df: pd.DataFrame, metric: str = "clicks") -> go.Figure:
    """Create a choropleth map for country breakdown."""
    fig = go.Figure(
        go.Choropleth(
            locations=df["country"],
            z=df[metric],
            locationmode="ISO-3",
            colorscale="Blues",
            colorbar_title=metric.capitalize(),
            hovertemplate="%{location}<br>%{z:,.0f} " + metric + "<extra></extra>",
        )
    )

    fig.update_layout(
        title=f"{metric.capitalize()} by Country",
        height=500,
        margin=dict(l=0, r=0, t=40, b=0),
        geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth"),
    )

    return fig
