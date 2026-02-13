"""SEO Strategy & Content Recommendations for Coastal Debt."""

from datetime import date, timedelta

import streamlit as st
import pandas as pd

st.set_page_config(page_title="SEO Strategy", page_icon="🎯", layout="wide")

from api.client import get_credentials
from api.search_analytics import get_top_queries, get_top_pages, get_query_page_combinations, query_search_analytics
from components.tips import tip_box

SITE_URL = "sc-domain:coastaldebt.com"


def main():
    creds = get_credentials()
    if not creds:
        st.error("No API token found.")
        st.stop()

    st.title("SEO Strategy & Content Recommendations")
    st.caption("Data-driven action plan for the Coastal Debt SEO team")

    tip_box("Weekly SEO Routine",
        "**Every Monday:** Review this dashboard for new keyword opportunities and ranking changes. "
        "**Every Wednesday:** Publish or update one article targeting a low-hanging fruit keyword. "
        "**Every Friday:** Build 2-3 internal links from new content to your money pages. "
        "Consistency beats intensity — small weekly improvements compound into major gains.")

    end = date.today() - timedelta(days=3)
    start = end - timedelta(days=89)
    start_str = start.isoformat()
    end_str = end.isoformat()

    # Fetch all data
    queries_df = get_top_queries(SITE_URL, start_str, end_str, row_limit=25000)
    pages_df = get_top_pages(SITE_URL, start_str, end_str, row_limit=25000)
    combos_df = get_query_page_combinations(SITE_URL, start_str, end_str, row_limit=25000)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Article Ideas",
        "Keyword Gaps",
        "Quick Wins",
        "Page Optimization",
        "Technical Issues",
    ])

    # ===== TAB 1: ARTICLE IDEAS =====
    with tab1:
        st.subheader("Recommended Articles to Write")
        st.markdown("Based on queries where you're showing up but have **no dedicated content** or **poor rankings**.")

        st.markdown("---")

        # HIGH-PRIORITY ARTICLES
        st.markdown("### Priority 1: High-Volume Topics You're Missing")
        articles = [
            {
                "title": "What Is MCA Debt? A Complete Guide for Business Owners",
                "target_kw": "what is mca debt, what is mca, mca debt",
                "why": "570 impressions for 'what is mca debt' at position 11.5 with 0 clicks. Your existing article ranks poorly. Rewrite with better on-page SEO, add FAQ schema.",
                "impressions": "1,341 combined",
                "current_pos": "11-45",
            },
            {
                "title": "MCA Debt Relief: How It Works and Your Options in 2026",
                "target_kw": "mca debt relief, mca relief, merchant cash advance debt relief",
                "why": "806 impressions for 'mca debt relief' at position 33.8. Your article ranks page 3+. Create a comprehensive pillar page targeting this cluster.",
                "impressions": "1,204 combined",
                "current_pos": "33-53",
            },
            {
                "title": "Best Debt Settlement Companies in 2026 (Updated Guide)",
                "target_kw": "best debt settlement companies 2026, top debt settlement companies 2026, best debt relief companies 2026",
                "why": "382 impressions at position 10.3 with 0 clicks. Your existing article is close to page 1 — update and optimize title/meta.",
                "impressions": "722 combined",
                "current_pos": "9-10",
            },
            {
                "title": "What Happens If You Default on a Merchant Cash Advance?",
                "target_kw": "mca default, mca loan default, what happens if you default on a merchant cash advance",
                "why": "503 combined impressions at positions 31-52 with 0 clicks. High-intent informational query — create a definitive guide.",
                "impressions": "503 combined",
                "current_pos": "31-52",
            },
            {
                "title": "MCA Debt Restructuring: Everything You Need to Know",
                "target_kw": "mca debt restructuring, mca restructuring, business debt restructuring",
                "why": "824 combined impressions at positions 28-80 with only 7 clicks. Massive untapped potential with dedicated content.",
                "impressions": "824 combined",
                "current_pos": "28-80",
            },
            {
                "title": "MCA Debt Settlement: Process, Costs, and What to Expect",
                "target_kw": "mca debt settlement, merchant cash advance settlement",
                "why": "260 impressions at position 48.6 with 1 click. No dedicated page targeting this transactional keyword.",
                "impressions": "260 combined",
                "current_pos": "48-49",
            },
            {
                "title": "Understanding MCA Confession of Judgment: Your Rights",
                "target_kw": "merchant cash advance confession of judgment",
                "why": "229 impressions at position 25 with 0 clicks. Legal-focused content that builds authority and trust.",
                "impressions": "229",
                "current_pos": "25",
            },
            {
                "title": "MCA UCC Liens: What They Are and How to Remove Them",
                "target_kw": "mca ucc, mca ucc lien",
                "why": "183 impressions at position 15.5 with 0 clicks. You have an article but it's not ranking well. Refresh and expand.",
                "impressions": "183",
                "current_pos": "15-16",
            },
            {
                "title": "MCA Agreement Terms: Red Flags Every Business Should Know",
                "target_kw": "merchant cash advance agreement, mca agreement terms",
                "why": "184 impressions at position 51 with 0 clicks. Your existing article ranks poorly — rewrite for featured snippets.",
                "impressions": "184",
                "current_pos": "51",
            },
            {
                "title": "Business Debt Consolidation vs MCA Debt Relief: Which Is Right?",
                "target_kw": "business debt consolidation, business debt restructuring",
                "why": "446 combined impressions at positions 79-84 with 0 clicks. Comparison content that captures decision-stage traffic.",
                "impressions": "446 combined",
                "current_pos": "79-84",
            },
        ]

        for i, a in enumerate(articles, 1):
            with st.expander("{}. {}".format(i, a["title"]), expanded=(i <= 3)):
                col1, col2, col3 = st.columns(3)
                col1.metric("Combined Impressions", a["impressions"])
                col2.metric("Current Position", a["current_pos"])
                col3.metric("Priority", "HIGH" if i <= 5 else "MEDIUM")
                st.markdown("**Target Keywords:** `{}`".format(a["target_kw"]))
                st.markdown("**Why:** {}".format(a["why"]))

        # INDUSTRY-SPECIFIC ARTICLES
        st.markdown("---")
        st.markdown("### Priority 2: Industry-Specific MCA Relief Content")
        st.markdown("You're getting impressions for industry-specific queries. Create dedicated landing pages:")

        industries = [
            {"industry": "Trucking Companies", "kw": "mca debt relief for truck companies", "imp": 148, "pos": 3.0, "note": "Already ranking #3! Create a full landing page to dominate."},
            {"industry": "Retail Businesses", "kw": "mca debt relief for retail", "imp": 131, "pos": 26.9, "note": "Position 27 — dedicated page could reach page 1."},
            {"industry": "Staffing Agencies", "kw": "mca debt relief for staffing business", "imp": 128, "pos": 9.7, "note": "Almost page 1! Quick optimization could push this over."},
            {"industry": "Professional Services", "kw": "mca debt relief for professional service", "imp": 109, "pos": 17.4, "note": "Page 2 — needs dedicated content to break through."},
            {"industry": "Salons & Beauty", "kw": "mca debt relief for salons", "imp": 98, "pos": 33.3, "note": "No dedicated page yet. Easy win with targeted content."},
            {"industry": "Restaurants", "kw": "mca relief restaurant", "imp": 80, "pos": 7.5, "note": "You have /industry/mca-relief-restaurant — optimize it further."},
            {"industry": "Contractors", "kw": "mca relief contractors", "imp": 80, "pos": 8.4, "note": "You have /industry/contractors — add more content and testimonials."},
        ]

        df_ind = pd.DataFrame(industries)
        df_ind.columns = ["Industry", "Target Keyword", "Impressions", "Avg Position", "Action"]
        st.dataframe(df_ind, use_container_width=True, hide_index=True)

    # ===== TAB 2: KEYWORD GAPS =====
    with tab2:
        st.subheader("Keyword Gap Analysis")
        st.markdown("Keywords where you're showing up in search results but **not capturing clicks**.")

        if not queries_df.empty:
            # High impressions, 0 clicks
            zero_click = queries_df[(queries_df["clicks"] == 0) & (queries_df["impressions"] >= 20)].copy()
            zero_click = zero_click.sort_values("impressions", ascending=False)

            st.markdown("### Keywords with 0 Clicks (20+ impressions)")
            st.markdown("These are keywords Google thinks you're relevant for, but users aren't clicking. Fix with better titles, meta descriptions, or dedicated content.")

            if not zero_click.empty:
                display = zero_click[["query", "impressions", "position"]].head(30).copy()
                display["position"] = display["position"].round(1)
                display["action"] = display.apply(lambda r:
                    "Optimize existing page (title/meta)" if r["position"] <= 10
                    else "Create dedicated content" if r["position"] <= 30
                    else "Need new comprehensive article",
                    axis=1)
                display.columns = ["Query", "Impressions", "Position", "Recommended Action"]
                st.dataframe(display, use_container_width=True, hide_index=True)

            # Keyword clusters
            st.markdown("---")
            st.markdown("### Keyword Clusters to Target")
            st.markdown("Group related keywords together for content planning:")

            clusters = {
                "MCA Debt Relief": ["mca debt relief", "mca relief", "merchant cash advance debt relief", "mca debt relief pros", "mca debt advisors", "mca debt advisor"],
                "MCA Default/Legal": ["mca default", "mca loan default", "merchant cash advance confession of judgment", "mca ucc", "what happens if you default on a merchant cash advance"],
                "MCA Restructuring": ["mca debt restructuring", "mca restructuring", "business debt restructuring", "mca debt settlement"],
                "MCA Basics": ["what is mca debt", "what is mca", "merchant cash advance agreement", "mca debt"],
                "Best Companies": ["best debt settlement companies 2026", "best debt relief companies 2026", "top debt settlement companies 2026", "top debt relief companies 2026", "best mca debt relief companies"],
                "Business Debt": ["business debt consolidation", "business debt restructuring", "debt settlement", "debt relief"],
                "Competitors": ["mca suite alternatives", "mca suite competitors", "mca fixed payment llc"],
            }

            for cluster_name, keywords in clusters.items():
                with st.expander(cluster_name):
                    cluster_data = queries_df[queries_df["query"].isin(keywords)].copy()
                    if not cluster_data.empty:
                        cluster_data = cluster_data.sort_values("impressions", ascending=False)
                        total_imp = cluster_data["impressions"].sum()
                        total_clicks = cluster_data["clicks"].sum()
                        st.markdown("**Total impressions:** {:,} | **Total clicks:** {:,}".format(int(total_imp), int(total_clicks)))
                        display = cluster_data[["query", "clicks", "impressions", "position"]].copy()
                        display["position"] = display["position"].round(1)
                        display.columns = ["Query", "Clicks", "Impressions", "Position"]
                        st.dataframe(display, use_container_width=True, hide_index=True)
                    else:
                        st.info("No data for these keywords yet.")

    # ===== TAB 3: QUICK WINS =====
    with tab3:
        st.subheader("Quick Wins — Fix These This Week")
        st.markdown("Changes that can improve your traffic **within days**, not months.")

        st.markdown("---")
        st.markdown("### 1. Fix Duplicate Homepage URLs")
        st.markdown("""
Your homepage has **multiple indexed URLs** eating each other's rankings:
- `/` — 17,151 impressions
- `/#w-tabs-0-data-w-pane-0` through `/#w-tabs-0-data-w-pane-5` — 30,095 combined impressions

**Action:** Add canonical tags pointing all `/#w-tabs-*` URLs to `/`. This is likely caused by tab navigation creating separate indexed URLs. Consider adding `rel="canonical"` and blocking these in robots.txt.
""")

        st.markdown("---")
        st.markdown("### 2. Optimize Titles for Top Queries")
        st.markdown("""
| Query | Impressions | Position | Action |
|---|---|---|---|
| coastal debt solutions | 733 | 4.3 | Position 4 but only 1% CTR — improve meta title to include "Coastal Debt Solutions" |
| coastal debt resolve reviews | 2,156 | 8.1 | Make sure testimonials page title mentions "reviews" explicitly |
| coastal debt collection | 306 | 11.2 | Clarify you're NOT a debt collector — add "debt relief" to disambiguate |
| best debt settlement companies 2026 | 382 | 10.3 | Update article title to match exact query, add year prominently |
| best debt relief companies 2026 | 176 | 9.2 | Same article — ensure "2026" is in H1 and title tag |
""")

        st.markdown("---")
        st.markdown("### 3. Internal Linking Opportunities")
        st.markdown("""
Your articles aren't linking to each other enough. Add internal links:

| From Page | Link To | With Anchor Text |
|---|---|---|
| /articles/what-is-mca-debt | /articles/how-mca-debt-relief-works | "how MCA debt relief works" |
| /articles/what-is-mca-debt | /articles/what-happens-default-merchant-cash-advance | "what happens if you default" |
| /articles/how-mca-debt-relief-works | /services/mca-debt-relief | "our MCA debt relief services" |
| /articles/best-debt-relief-companies-in-2026 | /testimonials | "read our client reviews" |
| /articles/mca-ucc-lien | /articles/what-is-an-mca-agreement-key-terms-to-watch-for | "key MCA terms to watch for" |
| Homepage | /articles/what-is-mca-debt | "learn about MCA debt" |
| Every article | /get-started | "get a free consultation" CTA |
""")

        st.markdown("---")
        st.markdown("### 4. Pages Needing Meta Description Updates")
        if not pages_df.empty:
            low_ctr_pages = pages_df[(pages_df["position"] <= 10) & (pages_df["ctr"] < 0.02) & (pages_df["impressions"] >= 100)].copy()
            low_ctr_pages["short_page"] = low_ctr_pages["page"].str.replace("https://www.coastaldebt.com", "", regex=False)
            if not low_ctr_pages.empty:
                st.markdown("These pages rank on page 1 but have very low CTR — **rewrite their meta descriptions**:")
                display = low_ctr_pages[["short_page", "clicks", "impressions", "ctr", "position"]].copy()
                display["ctr"] = (display["ctr"] * 100).round(2).astype(str) + "%"
                display["position"] = display["position"].round(1)
                display.columns = ["Page", "Clicks", "Impressions", "CTR", "Position"]
                st.dataframe(display, use_container_width=True, hide_index=True)

    # ===== TAB 4: PAGE OPTIMIZATION =====
    with tab4:
        st.subheader("Page-by-Page Optimization Tips")

        page_tips = [
            {
                "page": "/restructure-mca-business-loans-now",
                "issue": "12,133 impressions but only 34 clicks (0.28% CTR) at position 8.1",
                "tips": [
                    "Rewrite meta title to be more compelling — include 'Free Consultation' or '2026 Guide'",
                    "Add FAQ schema markup for common MCA restructuring questions",
                    "Improve page speed — ensure images are optimized",
                    "Add client testimonials directly on this page",
                    "Add clear CTA above the fold",
                ]
            },
            {
                "page": "/articles/best-debt-relief-companies-in-2026",
                "issue": "7,242 impressions but only 67 clicks (0.93% CTR) at position 11",
                "tips": [
                    "Currently position 11 (page 2) — needs link building to push to page 1",
                    "Update the title to 'Best MCA Debt Relief Companies in 2026 (Expert Ranked)'",
                    "Add comparison table at the top of the article",
                    "Include pricing/cost information — Google favors comprehensive content",
                    "Add author bio for E-E-A-T signals",
                ]
            },
            {
                "page": "/articles/what-is-mca-debt",
                "issue": "3,766 impressions but only 29 clicks at position 25",
                "tips": [
                    "Position 25 is page 3 — this article needs a major rewrite",
                    "Target 'what is mca debt' as primary keyword (570 imp, pos 11.5)",
                    "Make it the definitive guide: 2000+ words, diagrams, examples",
                    "Add 'People Also Ask' answers as H2 sections",
                    "Get internal links from every other MCA article pointing to this",
                ]
            },
            {
                "page": "/articles/how-mca-debt-relief-works",
                "issue": "2,667 impressions, 44 clicks at position 37.2",
                "tips": [
                    "Position 37 is terrible for this important page — full rewrite needed",
                    "Target keyword cluster: 'mca debt relief', 'how mca debt relief works', 'mca relief'",
                    "Add step-by-step process with numbered list (featured snippet potential)",
                    "Include real timeline expectations and cost breakdowns",
                    "Add video content explaining the process",
                ]
            },
            {
                "page": "/about-us",
                "issue": "11,669 impressions but only 57 clicks (0.49% CTR) at position 4.2",
                "tips": [
                    "Position 4.2 is great but CTR is very low — meta description isn't compelling",
                    "Rewrite meta to highlight years of experience, number of clients helped, total debt resolved",
                    "The high impressions are from branded queries — make sure title is 'About Coastal Debt Resolve'",
                ]
            },
            {
                "page": "/testimonials",
                "issue": "2,662 impressions, 64 clicks at position 8.5 — good but can improve",
                "tips": [
                    "Add Review schema markup for star ratings in search results",
                    "Rename to 'Reviews' in URL and title — 'coastal debt resolve reviews' has 2,156 impressions",
                    "Add more recent reviews and include specific dollar amounts saved",
                ]
            },
        ]

        for tip in page_tips:
            with st.expander("**{}**".format(tip["page"]), expanded=False):
                st.warning(tip["issue"])
                for t in tip["tips"]:
                    st.markdown("- {}".format(t))

    # ===== TAB 5: TECHNICAL ISSUES =====
    with tab5:
        st.subheader("Technical SEO Issues Detected")

        st.markdown("### Critical Issues")

        st.error("""
**Duplicate Content: Homepage Tab Fragments**

Your homepage has 6+ indexed fragment URLs (`/#w-tabs-0-data-w-pane-0` through `/#w-tabs-0-data-w-pane-5`) generating over **30,000 wasted impressions** combined.

**Fix:**
1. Add `<link rel="canonical" href="https://www.coastaldebt.com/" />` to the homepage
2. Make sure tab content loads via JavaScript without changing the URL hash
3. Submit a URL removal request in Search Console for these fragment URLs
4. Add to robots.txt: `Disallow: /#w-tabs-*`
""")

        st.warning("""
**Low CTR on High-Impression Pages**

Several pages rank well but have terrible CTR:
- `/restructure-mca-business-loans-now` — 0.28% CTR (12K impressions)
- `/#w-tabs-*` pages — 0.02-0.03% CTR (30K+ impressions)
- `/get-started` — 0.07% CTR (1.4K impressions)

**Fix:** Audit and rewrite all meta titles and descriptions. Use action-oriented copy with numbers.
""")

        st.warning("""
**Cannibalization: Multiple Pages Competing for Same Keywords**

'coastal debt resolve' shows results for 10+ different URLs on your site. Top competing pages:
- `/` (homepage) — 5,667 imp, position 1.4
- `/restructure-mca-business-loans-now` — 5,413 imp, position 6.0
- `/about-us` — 3,426 imp, position 2.6
- `/#w-tabs-*` — 14,000+ combined impressions

**Fix:** Consolidate. Make homepage the primary target for branded queries. Add canonical tags and reduce internal competition.
""")

        st.markdown("### Recommendations Checklist")
        st.markdown("""
- [ ] Fix homepage fragment URL indexing (canonical tags)
- [ ] Rewrite meta titles/descriptions for top 15 pages
- [ ] Add FAQ schema to key service pages
- [ ] Add Review schema to testimonials page
- [ ] Build internal linking structure between all MCA articles
- [ ] Create XML sitemap with only canonical URLs
- [ ] Set up 301 redirects for any duplicate content
- [ ] Ensure mobile page speed scores above 90
- [ ] Add author bios to all articles (E-E-A-T)
- [ ] Add structured data (Organization, LocalBusiness) to homepage
""")


main()
