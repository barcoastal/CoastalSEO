"""Sitemap management using direct REST calls."""

from typing import List, Dict

import requests
import streamlit as st

from api.client import get_auth_headers
from utils.constants import CACHE_TTL

API_BASE = "https://searchconsole.googleapis.com/webmasters/v3/sites"


def _encode_site(site_url):
    return requests.utils.quote(site_url, safe="")


@st.cache_data(ttl=CACHE_TTL)
def list_sitemaps(site_url):
    """List all sitemaps for a property."""
    headers = get_auth_headers()
    if not headers:
        return []
    url = "{}/{}/sitemaps".format(API_BASE, _encode_site(site_url))
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return []
    return resp.json().get("sitemap", [])


def submit_sitemap(site_url, sitemap_url):
    """Submit a sitemap."""
    headers = get_auth_headers()
    if not headers:
        return False
    url = "{}/{}/sitemaps/{}".format(API_BASE, _encode_site(site_url), requests.utils.quote(sitemap_url, safe=""))
    resp = requests.put(url, headers=headers)
    st.cache_data.clear()
    return resp.status_code == 204 or resp.status_code == 200


def delete_sitemap(site_url, sitemap_url):
    """Delete a sitemap."""
    headers = get_auth_headers()
    if not headers:
        return False
    url = "{}/{}/sitemaps/{}".format(API_BASE, _encode_site(site_url), requests.utils.quote(sitemap_url, safe=""))
    resp = requests.delete(url, headers=headers)
    st.cache_data.clear()
    return resp.status_code == 204 or resp.status_code == 200
