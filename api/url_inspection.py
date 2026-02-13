"""URL Inspection API with rate limiting using direct REST calls."""

import time
from typing import List, Dict, Optional

import requests

from api.client import get_auth_headers
from utils.constants import URL_INSPECTION_RATE_LIMIT_SECONDS

INSPECT_URL = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"


def inspect_url(site_url, inspection_url):
    """Inspect a single URL. Returns the raw inspection result."""
    headers = get_auth_headers()
    if not headers:
        return {}
    body = {"inspectionUrl": inspection_url, "siteUrl": site_url}
    resp = requests.post(INSPECT_URL, headers=headers, json=body)
    if resp.status_code != 200:
        raise Exception("API error {}: {}".format(resp.status_code, resp.text))
    return resp.json().get("inspectionResult", {})


def batch_inspect_urls(site_url, urls, progress_callback=None):
    """Inspect multiple URLs with rate limiting."""
    results = []
    total = len(urls)
    for i, url in enumerate(urls):
        try:
            result = inspect_url(site_url, url)
            results.append({"url": url, "result": result, "error": None})
        except Exception as e:
            results.append({"url": url, "result": None, "error": str(e)})
        if progress_callback:
            progress_callback(i + 1, total)
        if i < total - 1:
            time.sleep(URL_INSPECTION_RATE_LIMIT_SECONDS)
    return results


def format_inspection_result(result):
    """Extract key fields from an inspection result into a flat dict."""
    if not result:
        return {"status": "Error", "details": "No result returned"}
    index_status = result.get("indexStatusResult", {})
    mobile = result.get("mobileUsabilityResult", {})
    rich = result.get("richResultsResult", {})
    return {
        "coverage_state": index_status.get("coverageState", "Unknown"),
        "indexing_state": index_status.get("indexingState", "Unknown"),
        "robots_txt_state": index_status.get("robotsTxtState", "Unknown"),
        "crawled_as": index_status.get("crawledAs", "Unknown"),
        "last_crawl_time": index_status.get("lastCrawlTime", "N/A"),
        "page_fetch_state": index_status.get("pageFetchState", "Unknown"),
        "referring_urls": index_status.get("referringUrls", []),
        "sitemap_urls": index_status.get("sitemap", []),
        "mobile_usability": mobile.get("verdict", "N/A"),
        "rich_results_verdict": rich.get("verdict", "N/A"),
    }
