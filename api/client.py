"""Build authenticated Google API service objects."""

import json
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from utils.constants import SCOPES, TOKEN_FILE


def _load_credentials():
    """Load and refresh credentials from saved token."""
    base = Path(__file__).resolve().parent.parent
    token_path = base / TOKEN_FILE
    if not token_path.exists():
        return None

    data = json.loads(token_path.read_text())
    creds = Credentials(
        token=data.get("token"),
        refresh_token=data.get("refresh_token"),
        token_uri=data.get("token_uri"),
        client_id=data.get("client_id"),
        client_secret=data.get("client_secret"),
        scopes=data.get("scopes", SCOPES),
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Save refreshed token
        data["token"] = creds.token
        if creds.expiry:
            data["expiry"] = creds.expiry.isoformat()
        token_path.write_text(json.dumps(data, indent=2))

    return creds


def get_credentials():
    """Get valid credentials or None."""
    return _load_credentials()


def get_auth_headers():
    """Get Authorization headers for direct REST API calls."""
    creds = _load_credentials()
    if not creds:
        return None
    return {"Authorization": "Bearer " + creds.token}
