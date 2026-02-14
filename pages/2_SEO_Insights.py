"""SEO Insights - Actionable reports for the SEO team."""

from datetime import date, timedelta

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="SEO Insights", page_icon="💡", layout="wide")

from api.client import get_credentials
from api.search_analytics import (
    get_top_queries,
    get_top_pages,
    query_search_analytics,
    get_query_page_combinations,
)
from utils.export import download_csv_button
from components.tips import show_query_tips, show_page_tips, tip_box

SITE_URL = "sc-domain:coastaldebt.com"


def main():
    creds = get_credentials()
    if not creds:
        st.error("No API token found.")
        st.stop()

    from components.sidebar import render_sidebar
    render_sidebar()

    st.title("SEO Insights")
    st.caption("Actionable reports for the Coastal Debt SEO team")

    end = date.today() - timedelta(days=3)
    start = end - timedelta(days=27)
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=27)

    start_str = start.isoformat()
    end_str = end.isoformat()
    prev_start_str = prev_start.isoformat()
    prev_end_str = prev_end.isoformat()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Low-Hanging Fruit",
        "Position Distribution",
        "Trending Queries",
        "Page Performance",
        "CTR Opportunities",
    ])

    # ===== TAB 1: LOW-HANGING FRUIT =====
    with tab1:
        st.subheader("Low-Hanging Fruit Queries")
        st.markdown(
            "Queries ranking positions **5-20** with high impressions — "
            "small ranking improvements here could drive significant traffic."
        )

        queries_df = get_top_queries(SITE_URL, start_str, end_str, row_limit=25000)
        if not queries_df.empty:
            lhf = queries_df[
                (queries_df["position"] >= 5) &
                (queries_df["position"] <= 20) &
                (queries_df["impressions"] >= 10)
            ].copy()
            lhf["potential_clicks"] = (lhf["impressions"] * 0.05).astype(int)  # Est. 5% CTR if page 1
            lhf = lhf.sort_values("impressions", ascending=False)

            if not lhf.empty:
                col1, col2, col3 = st.columns(3)
                col1.metric("Opportunities Found", len(lhf))
                col2.metric("Total Impressions", "{:,}".format(int(lhf["impressions"].sum())))
                col3.metric("Est. Potential Clicks", "{:,}".format(int(lhf["potential_clicks"].sum())))

                # Chart
                top20 = lhf.head(20)
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    y=top20["query"], x=top20["impressions"],
                    orientation="h", name="Impressions",
                    marker_color="#1a73e8",
                ))
                fig.update_layout(
                    title="Top 20 Low-Hanging Fruit by Impressions",
                    height=600, yaxis=dict(autorange="reversed"),
                    margin=dict(l=0, r=0, t=40, b=0),
                )
                st.plotly_chart(fig, use_container_width=True)

                # Table
                display = lhf[["query", "clicks", "impressions", "ctr", "position", "potential_clicks"]].copy()
                display["ctr"] = (display["ctr"] * 100).round(2).astype(str) + "%"
                display["position"] = display["position"].round(1)
                display.columns = ["Query", "Clicks", "Impressions", "CTR", "Position", "Est. Potential Clicks"]
                st.dataframe(display, use_container_width=True, hide_index=True)
                download_csv_button(lhf, "low_hanging_fruit.csv")
                tip_box("Low-Hanging Fruit Strategy",
                    "Focus on queries at positions 8-12 first — these need the smallest push to reach page 1. "
                    "Add the exact query to your page's H1, first paragraph, and meta title. "
                    "Build 2-3 internal links from high-authority pages on your site.")
            else:
                st.info("No low-hanging fruit found in current data.")

    # ===== TAB 2: POSITION DISTRIBUTION =====
    with tab2:
        st.subheader("Query Position Distribution")
        st.markdown("How your queries are distributed across search result positions.")

        if not queries_df.empty:
            bins = [0, 3, 10, 20, 50, 100]
            labels = ["1-3 (Top)", "4-10 (Page 1)", "11-20 (Page 2)", "21-50", "50+"]
            queries_df["position_bucket"] = pd.cut(queries_df["position"], bins=bins, labels=labels, right=True)

            dist = queries_df.groupby("position_bucket", observed=True).agg(
                query_count=("query", "count"),
                total_clicks=("clicks", "sum"),
                total_impressions=("impressions", "sum"),
                avg_ctr=("ctr", "mean"),
            ).reset_index()

            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(dist, values="query_count", names="position_bucket",
                             title="Queries by Position Range",
                             color_discrete_sequence=["#1a73e8", "#5bb974", "#f9ab00", "#e8710a", "#d93025"])
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig = px.pie(dist, values="total_clicks", names="position_bucket",
                             title="Clicks by Position Range",
                             color_discrete_sequence=["#1a73e8", "#5bb974", "#f9ab00", "#e8710a", "#d93025"])
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

            dist_display = dist.copy()
            dist_display["avg_ctr"] = (dist_display["avg_ctr"] * 100).round(2).astype(str) + "%"
            dist_display.columns = ["Position Range", "Queries", "Clicks", "Impressions", "Avg CTR"]
            st.dataframe(dist_display, use_container_width=True, hide_index=True)

    # ===== TAB 3: TRENDING QUERIES =====
    with tab3:
        st.subheader("Trending Queries")
        st.markdown("Queries gaining or losing clicks compared to the previous 28-day period.")

        current_q = get_top_queries(SITE_URL, start_str, end_str, row_limit=25000)
        previous_q = get_top_queries(SITE_URL, prev_start_str, prev_end_str, row_limit=25000)

        if not current_q.empty and not previous_q.empty:
            merged = current_q.merge(previous_q, on="query", suffixes=("_current", "_previous"), how="outer").fillna(0)
            merged["click_change"] = merged["clicks_current"] - merged["clicks_previous"]
            merged["impression_change"] = merged["impressions_current"] - merged["impressions_previous"]
            merged["click_change_pct"] = merged.apply(
                lambda r: (r["click_change"] / r["clicks_previous"] * 100) if r["clicks_previous"] > 0 else 0, axis=1
            )

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Rising Queries")
                rising = merged[merged["click_change"] > 0].sort_values("click_change", ascending=False).head(15)
                if not rising.empty:
                    display = rising[["query", "clicks_current", "clicks_previous", "click_change"]].copy()
                    display.columns = ["Query", "Current Clicks", "Previous Clicks", "Change"]
                    st.dataframe(display, use_container_width=True, hide_index=True)
                else:
                    st.info("No rising queries found.")

            with col2:
                st.markdown("#### Declining Queries")
                declining = merged[merged["click_change"] < 0].sort_values("click_change").head(15)
                if not declining.empty:
                    display = declining[["query", "clicks_current", "clicks_previous", "click_change"]].copy()
                    display.columns = ["Query", "Current Clicks", "Previous Clicks", "Change"]
                    st.dataframe(display, use_container_width=True, hide_index=True)
                else:
                    st.info("No declining queries found.")

            # New queries
            st.markdown("#### New Queries (not seen in previous period)")
            new_queries = merged[merged["clicks_previous"] == 0].sort_values("clicks_current", ascending=False).head(20)
            if not new_queries.empty:
                display = new_queries[["query", "clicks_current", "impressions_current"]].copy()
                display.columns = ["Query", "Clicks", "Impressions"]
                st.dataframe(display, use_container_width=True, hide_index=True)

            download_csv_button(merged, "trending_queries.csv")

            tip_box("Trending Queries Action Plan",
                "**Rising queries:** Double down — create more content around these topics and build internal links. "
                "**Declining queries:** Check if competitors published new content. Update your articles with fresh data and examples. "
                "**New queries:** These reveal emerging search intent — consider dedicated landing pages for high-volume ones.")

    # ===== TAB 4: PAGE PERFORMANCE =====
    with tab4:
        st.subheader("Page Performance Report")

        current_p = get_top_pages(SITE_URL, start_str, end_str, row_limit=25000)
        previous_p = get_top_pages(SITE_URL, prev_start_str, prev_end_str, row_limit=25000)

        if not current_p.empty:
            # Shorten URLs for display
            current_p["short_page"] = current_p["page"].str.replace("https://www.coastaldebt.com", "", regex=False)

            col1, col2 = st.columns(2)
            col1.metric("Total Pages", len(current_p))
            pages_with_clicks = len(current_p[current_p["clicks"] > 0])
            col2.metric("Pages with Clicks", pages_with_clicks)

            # Pages by clicks chart
            top15 = current_p.head(15)
            fig = go.Figure(go.Bar(
                y=top15["short_page"], x=top15["clicks"],
                orientation="h", marker_color="#1a73e8",
            ))
            fig.update_layout(
                title="Top 15 Pages by Clicks",
                height=500, yaxis=dict(autorange="reversed"),
                margin=dict(l=0, r=0, t=40, b=0),
            )
            st.plotly_chart(fig, use_container_width=True)

            # Page comparison with previous period
            if not previous_p.empty:
                st.markdown("#### Page Click Changes vs Previous Period")
                merged_p = current_p.merge(previous_p, on="page", suffixes=("_current", "_previous"), how="outer").fillna(0)
                merged_p["click_change"] = merged_p["clicks_current"] - merged_p["clicks_previous"]
                merged_p["short_page"] = merged_p["page"].str.replace("https://www.coastaldebt.com", "", regex=False)

                declining_pages = merged_p[merged_p["click_change"] < 0].sort_values("click_change").head(10)
                if not declining_pages.empty:
                    st.markdown("**Declining Pages:**")
                    display = declining_pages[["short_page", "clicks_current", "clicks_previous", "click_change"]].copy()
                    display.columns = ["Page", "Current Clicks", "Previous Clicks", "Change"]
                    st.dataframe(display, use_container_width=True, hide_index=True)

                growing_pages = merged_p[merged_p["click_change"] > 0].sort_values("click_change", ascending=False).head(10)
                if not growing_pages.empty:
                    st.markdown("**Growing Pages:**")
                    display = growing_pages[["short_page", "clicks_current", "clicks_previous", "click_change"]].copy()
                    display.columns = ["Page", "Current Clicks", "Previous Clicks", "Change"]
                    st.dataframe(display, use_container_width=True, hide_index=True)

            # Full table
            st.markdown("#### All Pages")
            display = current_p[["short_page", "clicks", "impressions", "ctr", "position"]].copy()
            display["ctr"] = (display["ctr"] * 100).round(2).astype(str) + "%"
            display["position"] = display["position"].round(1)
            display.columns = ["Page", "Clicks", "Impressions", "CTR", "Position"]
            st.dataframe(display, use_container_width=True, hide_index=True)
            download_csv_button(current_p, "page_performance.csv")

    # ===== TAB 5: CTR OPPORTUNITIES =====
    with tab5:
        st.subheader("CTR Optimization Opportunities")
        st.markdown(
            "Queries with **good positions (1-10)** but **low CTR** — "
            "improving titles and meta descriptions for these could boost clicks."
        )

        if not queries_df.empty:
            # Expected CTR by position (rough benchmarks)
            expected_ctr = {1: 0.28, 2: 0.15, 3: 0.11, 4: 0.08, 5: 0.06, 6: 0.05, 7: 0.04, 8: 0.03, 9: 0.03, 10: 0.02}

            page1 = queries_df[queries_df["position"] <= 10].copy()
            page1["position_rounded"] = page1["position"].round().astype(int).clip(1, 10)
            page1["expected_ctr"] = page1["position_rounded"].map(expected_ctr)
            page1["ctr_gap"] = page1["expected_ctr"] - page1["ctr"]

            # Queries underperforming CTR
            underperforming = page1[
                (page1["ctr_gap"] > 0.01) &
                (page1["impressions"] >= 10)
            ].sort_values("ctr_gap", ascending=False)

            if not underperforming.empty:
                col1, col2 = st.columns(2)
                col1.metric("Underperforming Queries", len(underperforming))
                potential = (underperforming["impressions"] * underperforming["ctr_gap"]).sum()
                col2.metric("Est. Missing Clicks", "{:,.0f}".format(potential))

                # Chart
                top15 = underperforming.head(15)
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    y=top15["query"], x=top15["ctr"] * 100,
                    orientation="h", name="Actual CTR",
                    marker_color="#d93025",
                ))
                fig.add_trace(go.Bar(
                    y=top15["query"], x=top15["expected_ctr"] * 100,
                    orientation="h", name="Expected CTR",
                    marker_color="#5bb974",
                ))
                fig.update_layout(
                    title="CTR Gap: Actual vs Expected (Top 15)",
                    barmode="overlay", height=500,
                    xaxis_title="CTR (%)",
                    yaxis=dict(autorange="reversed"),
                    margin=dict(l=0, r=0, t=40, b=0),
                )
                st.plotly_chart(fig, use_container_width=True)

                # Table
                display = underperforming[["query", "clicks", "impressions", "ctr", "position", "expected_ctr", "ctr_gap"]].copy()
                display["ctr"] = (display["ctr"] * 100).round(2).astype(str) + "%"
                display["expected_ctr"] = (display["expected_ctr"] * 100).round(1).astype(str) + "%"
                display["ctr_gap"] = (display["ctr_gap"] * 100).round(2).astype(str) + "pp"
                display["position"] = display["position"].round(1)
                display.columns = ["Query", "Clicks", "Impressions", "Actual CTR", "Position", "Expected CTR", "CTR Gap"]
                st.dataframe(display, use_container_width=True, hide_index=True)
                download_csv_button(underperforming, "ctr_opportunities.csv")
                tip_box("CTR Improvement Checklist",
                    "1. **Rewrite meta titles** — include numbers, brackets, and power words (e.g., 'Complete Guide [2026]')\n\n"
                    "2. **Optimize meta descriptions** — write them like ad copy with a clear CTA under 155 characters\n\n"
                    "3. **Add structured data** — FAQ, Review, and HowTo schema can increase SERP visibility by 2-3x\n\n"
                    "4. **Use breadcrumbs** — they show a clean URL path in search results and improve click confidence")
            else:
                st.success("All page-1 queries are performing at or above expected CTR.")


main()
