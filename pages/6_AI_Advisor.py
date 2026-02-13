"""AI SEO Advisor - Chat with Claude about your site's SEO performance."""

from datetime import date, timedelta

import streamlit as st

st.set_page_config(page_title="AI SEO Advisor", page_icon="🤖", layout="wide")

from api.client import get_credentials
from api.search_analytics import (
    get_top_queries,
    get_top_pages,
    get_device_breakdown,
    get_country_breakdown,
    query_search_analytics,
)

SITE_URL = "sc-domain:coastaldebt.com"


def get_site_summary():
    """Build a text summary of the site's GSC data to give Claude context."""
    end = date.today() - timedelta(days=3)
    start = end - timedelta(days=27)
    start_str = start.isoformat()
    end_str = end.isoformat()

    summary_parts = []
    summary_parts.append("=== Coastal Debt (coastaldebt.com) Search Console Data ===")
    summary_parts.append("Period: {} to {}".format(start_str, end_str))

    # Overall metrics
    totals = query_search_analytics(SITE_URL, start_str, end_str, [])
    if not totals.empty:
        clicks = int(totals["clicks"].sum())
        impressions = int(totals["impressions"].sum())
        ctr = totals["ctr"].mean()
        position = totals["position"].mean()
        summary_parts.append("\n--- Overall Metrics ---")
        summary_parts.append("Total Clicks: {:,}".format(clicks))
        summary_parts.append("Total Impressions: {:,}".format(impressions))
        summary_parts.append("Average CTR: {:.2%}".format(ctr))
        summary_parts.append("Average Position: {:.1f}".format(position))

    # Top queries
    queries = get_top_queries(SITE_URL, start_str, end_str, row_limit=50)
    if not queries.empty:
        summary_parts.append("\n--- Top 50 Queries ---")
        for _, row in queries.iterrows():
            summary_parts.append("  {} | clicks={} imp={} ctr={:.2%} pos={:.1f}".format(
                row["query"], int(row["clicks"]), int(row["impressions"]),
                row["ctr"], row["position"]
            ))

    # Top pages
    pages = get_top_pages(SITE_URL, start_str, end_str, row_limit=30)
    if not pages.empty:
        summary_parts.append("\n--- Top 30 Pages ---")
        for _, row in pages.iterrows():
            short = row["page"].replace("https://www.coastaldebt.com", "")
            summary_parts.append("  {} | clicks={} imp={} ctr={:.2%} pos={:.1f}".format(
                short, int(row["clicks"]), int(row["impressions"]),
                row["ctr"], row["position"]
            ))

    # Device breakdown
    devices = get_device_breakdown(SITE_URL, start_str, end_str)
    if not devices.empty:
        summary_parts.append("\n--- Device Breakdown ---")
        for _, row in devices.iterrows():
            summary_parts.append("  {} | clicks={} imp={} ctr={:.2%} pos={:.1f}".format(
                row["device"], int(row["clicks"]), int(row["impressions"]),
                row["ctr"], row["position"]
            ))

    # Country breakdown
    countries = get_country_breakdown(SITE_URL, start_str, end_str)
    if not countries.empty:
        summary_parts.append("\n--- Top Countries ---")
        for _, row in countries.head(10).iterrows():
            summary_parts.append("  {} | clicks={} imp={}".format(
                row["country"], int(row["clicks"]), int(row["impressions"])
            ))

    # Low-hanging fruit
    if not queries.empty:
        all_queries = get_top_queries(SITE_URL, start_str, end_str, row_limit=25000)
        lhf = all_queries[
            (all_queries["position"] >= 5) &
            (all_queries["position"] <= 20) &
            (all_queries["impressions"] >= 10)
        ].sort_values("impressions", ascending=False).head(20)
        if not lhf.empty:
            summary_parts.append("\n--- Low-Hanging Fruit (pos 5-20, high impressions) ---")
            for _, row in lhf.iterrows():
                summary_parts.append("  {} | clicks={} imp={} pos={:.1f}".format(
                    row["query"], int(row["clicks"]), int(row["impressions"]), row["position"]
                ))

        # Zero-click queries
        zero = all_queries[(all_queries["clicks"] == 0) & (all_queries["impressions"] >= 20)].sort_values("impressions", ascending=False).head(15)
        if not zero.empty:
            summary_parts.append("\n--- Zero-Click Queries (0 clicks, 20+ impressions) ---")
            for _, row in zero.iterrows():
                summary_parts.append("  {} | imp={} pos={:.1f}".format(
                    row["query"], int(row["impressions"]), row["position"]
                ))

    return "\n".join(summary_parts)


SYSTEM_PROMPT = """You are an expert SEO advisor for Coastal Debt (coastaldebt.com), a company that provides MCA (Merchant Cash Advance) debt relief and debt settlement services.

You have access to their Google Search Console data which is provided below. Use this data to give specific, actionable SEO recommendations.

Your expertise includes:
- On-page SEO (titles, meta descriptions, headings, content optimization)
- Technical SEO (site structure, canonical tags, schema markup, page speed)
- Content strategy (keyword targeting, content gaps, article ideas)
- Link building (internal linking, backlink strategies)
- CTR optimization (compelling titles and descriptions)
- Local SEO and E-E-A-T optimization

When giving advice:
- Be specific — reference actual queries, pages, and numbers from the data
- Prioritize actions by impact (highest ROI first)
- Give concrete examples of titles, descriptions, or content outlines when relevant
- Keep recommendations actionable — the SEO team should be able to implement them immediately
- When discussing positions, note that position 1-10 is page 1, 11-20 is page 2, etc.

{site_data}
"""


def get_ai_response(messages, site_data):
    """Get a response from Claude API."""
    import anthropic

    api_key = st.secrets.get("anthropic", {}).get("api_key", "")
    if not api_key:
        return "Error: Anthropic API key not configured in .streamlit/secrets.toml"

    client = anthropic.Anthropic(api_key=api_key)

    system = SYSTEM_PROMPT.format(site_data=site_data)

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2048,
        system=system,
        messages=messages,
    )

    return response.content[0].text


def main():
    creds = get_credentials()
    if not creds:
        st.error("No API token found.")
        st.stop()

    st.title("AI SEO Advisor")
    st.caption("Chat with Claude about your site's SEO performance and get personalized recommendations")

    # Initialize chat history
    if "advisor_messages" not in st.session_state:
        st.session_state.advisor_messages = []

    # Load site data (cached)
    if "site_summary" not in st.session_state:
        with st.spinner("Loading your Search Console data..."):
            st.session_state.site_summary = get_site_summary()

    # Sidebar with quick actions
    with st.sidebar:
        st.markdown("---")
        st.markdown("**Quick Questions**")
        quick_questions = [
            "What are my biggest SEO opportunities right now?",
            "Which pages need the most urgent attention?",
            "Give me 5 article ideas based on my keyword gaps",
            "How can I improve my CTR for branded queries?",
            "What technical SEO issues should I fix first?",
            "Create an SEO action plan for this month",
            "Which keywords am I close to ranking on page 1?",
            "How should I optimize my homepage for better rankings?",
        ]
        for q in quick_questions:
            if st.button(q, key="quick_{}".format(hash(q)), use_container_width=True):
                st.session_state.advisor_messages.append({"role": "user", "content": q})
                st.rerun()

        if st.button("Clear Chat", use_container_width=True):
            st.session_state.advisor_messages = []
            st.rerun()

    # Display chat history
    for msg in st.session_state.advisor_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Generate response if last message is from user
    if st.session_state.advisor_messages and st.session_state.advisor_messages[-1]["role"] == "user":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_ai_response(
                    st.session_state.advisor_messages,
                    st.session_state.site_summary,
                )
                st.markdown(response)
                st.session_state.advisor_messages.append({"role": "assistant", "content": response})

    # Chat input
    if prompt := st.chat_input("Ask me about your SEO..."):
        st.session_state.advisor_messages.append({"role": "user", "content": prompt})
        st.rerun()


main()
