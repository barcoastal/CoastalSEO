"""OAuth2 web flow for Google Search Console."""

import streamlit as st
from google_auth_oauthlib.flow import Flow

from auth.token_storage import save_credentials, load_credentials
from utils.constants import SCOPES


def create_flow() -> Flow:
    """Create an OAuth2 flow from Streamlit secrets."""
    oauth_config = st.secrets["google_oauth"]
    client_config = {
        "web": {
            "client_id": oauth_config["client_id"],
            "client_secret": oauth_config["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [oauth_config["redirect_uri"]],
        }
    }
    flow = Flow.from_client_config(client_config, scopes=SCOPES)
    flow.redirect_uri = oauth_config["redirect_uri"]
    return flow


def get_authorization_url() -> str:
    """Generate the Google OAuth2 authorization URL."""
    flow = create_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true",
    )
    return auth_url


def exchange_code_for_credentials(code: str):
    """Exchange the authorization code for credentials and save them."""
    flow = create_flow()
    flow.fetch_token(code=code)
    credentials = flow.credentials
    save_credentials(credentials)
    return credentials


def handle_auth_callback() -> bool:
    """Check for OAuth callback code in query params, exchange it, and rerun.

    Returns True if credentials are available (either loaded or just exchanged).
    """
    creds = load_credentials()
    if creds and creds.valid:
        return True

    query_params = st.query_params
    code = query_params.get("code")

    if code:
        try:
            exchange_code_for_credentials(code)
            st.query_params.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Authentication failed: {e}")
            return False

    return False


def get_credentials():
    """Get valid credentials or None."""
    return load_credentials()
