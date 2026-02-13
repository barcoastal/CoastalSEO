"""List verified Search Console properties."""

from typing import List, Dict

import streamlit as st

from api.client import get_webmasters_service
from utils.constants import CACHE_TTL


@st.cache_data(ttl=CACHE_TTL)
def list_sites() -> List[Dict]:
    """Return all verified Search Console properties.

    Each dict has keys: siteUrl, permissionLevel.
    """
    service = get_webmasters_service()
    if not service:
        return []
    response = service.sites().list().execute()
    return response.get("siteEntry", [])
