"""Contextual SEO tips displayed throughout the dashboard."""

import streamlit as st
import pandas as pd


def tip_box(title, text, icon="💡"):
    """Render a styled tip box."""
    st.info("{} **{}**\n\n{}".format(icon, title, text))


def show_kpi_tips(clicks, impressions, ctr, position):
    """Show tips based on KPI values."""
    tips = []
    if ctr < 0.02:
        tips.append("Your CTR is below 2%. **Rewrite meta titles and descriptions** to be more compelling. Use numbers, power words, and clear value propositions.")
    if position > 10:
        tips.append("Average position is off page 1. Focus on **building quality backlinks** and **improving content depth** for your target keywords.")
    if position <= 5 and ctr < 0.05:
        tips.append("You rank in top 5 but CTR is low. Your **title tags may not match search intent**. Review top-ranking competitors' titles for inspiration.")
    if impressions > 0 and clicks == 0:
        tips.append("Getting impressions but no clicks means Google sees you as relevant but **users aren't choosing your result**. Test different title/description copy.")
    if clicks > 0 and position <= 3:
        tips.append("You're in the top 3 — **protect these rankings** by keeping content fresh, monitoring competitors, and building internal links.")

    if tips:
        with st.expander("💡 SEO Tips based on your metrics", expanded=False):
            for t in tips:
                st.markdown("- {}".format(t))


def show_query_tips(df):
    """Show tips based on query data."""
    if df.empty:
        return

    tips = []

    # High impression, low click queries
    low_ctr = df[(df["impressions"] >= 50) & (df["ctr"] < 0.01)]
    if len(low_ctr) > 0:
        tips.append("**{} queries** have 50+ impressions but less than 1% CTR. These need better title tags and meta descriptions to earn clicks.".format(len(low_ctr)))

    # Queries on page 2 (position 11-20)
    page2 = df[(df["position"] > 10) & (df["position"] <= 20) & (df["impressions"] >= 20)]
    if len(page2) > 0:
        tips.append("**{} queries** are on page 2 (positions 11-20). These are your **best opportunities** — a small ranking boost puts them on page 1.".format(len(page2)))

    # Branded queries with low CTR
    branded = df[df["query"].str.contains("coastal", case=False, na=False)]
    branded_low = branded[branded["ctr"] < 0.05]
    if len(branded_low) > 0:
        tips.append("**{} branded queries** have less than 5% CTR. People searching your brand should click at a much higher rate — check if competitors are bidding on your brand name.".format(len(branded_low)))

    if tips:
        with st.expander("💡 Query Optimization Tips", expanded=False):
            for t in tips:
                st.markdown("- {}".format(t))


def show_page_tips(df):
    """Show tips based on page data."""
    if df.empty:
        return

    tips = []

    # Pages with high impressions but low CTR
    low_ctr_pages = df[(df["impressions"] >= 100) & (df["ctr"] < 0.01)]
    if len(low_ctr_pages) > 0:
        tips.append("**{} pages** have 100+ impressions but less than 1% CTR. Prioritize rewriting their meta descriptions with clear calls-to-action.".format(len(low_ctr_pages)))

    # Fragment URLs
    fragment_pages = df[df["page"].str.contains("#", na=False)]
    if len(fragment_pages) > 0:
        tips.append("**{} fragment URLs** (with #) are being indexed separately. Add canonical tags pointing to the base URL to consolidate rankings.".format(len(fragment_pages)))

    # Pages with position > 20
    deep_pages = df[(df["position"] > 20) & (df["impressions"] >= 50)]
    if len(deep_pages) > 0:
        tips.append("**{} pages** rank beyond position 20 despite getting impressions. Consider a **content refresh** — update with 2026 data, add FAQ sections, improve word count.".format(len(deep_pages)))

    if tips:
        with st.expander("💡 Page Optimization Tips", expanded=False):
            for t in tips:
                st.markdown("- {}".format(t))


def show_device_tips(df):
    """Show tips based on device breakdown."""
    if df.empty:
        return

    tips = []
    mobile = df[df["device"] == "MOBILE"]
    desktop = df[df["device"] == "DESKTOP"]

    if not mobile.empty and not desktop.empty:
        m_ctr = mobile.iloc[0]["ctr"]
        d_ctr = desktop.iloc[0]["ctr"]
        if m_ctr < d_ctr * 0.7:
            tips.append("Mobile CTR is significantly lower than desktop. **Check mobile page speed** (aim for <3s load time) and ensure tap targets are large enough.")
        m_pos = mobile.iloc[0]["position"]
        d_pos = desktop.iloc[0]["position"]
        if m_pos > d_pos + 2:
            tips.append("Mobile rankings are worse than desktop by {:.1f} positions. Google uses **mobile-first indexing** — prioritize mobile UX and Core Web Vitals.".format(m_pos - d_pos))

    if tips:
        with st.expander("💡 Mobile Optimization Tips", expanded=False):
            for t in tips:
                st.markdown("- {}".format(t))


def show_country_tips(df):
    """Show tips based on country data."""
    if df.empty:
        return

    tips = []
    usa = df[df["country"] == "usa"]
    non_usa = df[df["country"] != "usa"]

    if not usa.empty:
        usa_pct = usa.iloc[0]["clicks"] / max(df["clicks"].sum(), 1) * 100
        if usa_pct < 80:
            tips.append("Only {:.0f}% of clicks come from the US. If you only serve US clients, consider adding **hreflang tags** and geo-targeting in Search Console.".format(usa_pct))

    if not non_usa.empty and len(non_usa) > 5:
        tips.append("You're getting traffic from {} countries. If these aren't your target markets, focus on **US-specific content** and local SEO signals.".format(len(non_usa)))

    if tips:
        with st.expander("💡 Geographic Targeting Tips", expanded=False):
            for t in tips:
                st.markdown("- {}".format(t))


def show_general_seo_tips():
    """Show rotating general SEO tips in the sidebar."""
    import random
    general_tips = [
        "Update your top articles every quarter with fresh data and examples to maintain rankings.",
        "Add FAQ schema to your service pages — it can increase your SERP real estate by 2-3x.",
        "Build internal links from every new article to your top 5 money pages.",
        "Check your Core Web Vitals in PageSpeed Insights monthly — Google uses them as a ranking signal.",
        "Write meta descriptions as 'ad copy' — include a clear benefit and call-to-action under 155 characters.",
        "Add author bios with credentials to all articles — Google values E-E-A-T for financial content.",
        "Monitor your competitors' new content weekly and create better versions of their top-performing articles.",
        "Every article should have one clear primary keyword and 3-5 related secondary keywords.",
        "Images should have descriptive alt text with natural keyword usage — this helps with image search traffic.",
        "Submit new articles to Search Console's URL Inspection tool immediately after publishing for faster indexing.",
        "Review your 'Queries' report weekly to spot new keyword opportunities before competitors.",
        "Add review/testimonial schema markup to build trust signals in search results.",
        "Aim for position 1-3 on your most important queries — positions 4+ see a massive CTR drop-off.",
        "Use Google's 'People Also Ask' boxes as inspiration for FAQ sections and new article topics.",
        "Break up long articles with H2/H3 headings that match common search queries — this targets featured snippets.",
    ]
    random.shuffle(general_tips)
    with st.sidebar:
        st.markdown("---")
        st.markdown("**💡 SEO Tip of the Day**")
        st.caption(general_tips[0])
