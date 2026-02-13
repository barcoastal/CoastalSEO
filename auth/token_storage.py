"""Token persistence: save, load, refresh, and clear OAuth2 tokens."""

import json
import os
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from utils.constants import SCOPES, TOKEN_FILE


def _token_path() -> Path:
    """Get the absolute path to the token file."""
    base = Path(__file__).resolve().parent.parent
    return base / TOKEN_FILE


def save_credentials(credentials: Credentials) -> None:
    """Persist credentials to disk as JSON."""
    path = _token_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": list(credentials.scopes or SCOPES),
    }
    if credentials.expiry:
        data["expiry"] = credentials.expiry.isoformat()
    path.write_text(json.dumps(data, indent=2))


def load_credentials() -> Optional[Credentials]:
    """Load credentials from disk, refreshing if expired. Returns None if missing/invalid."""
    path = _token_path()
    if not path.exists():
        return None

    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None

    creds = Credentials(
        token=data.get("token"),
        refresh_token=data.get("refresh_token"),
        token_uri=data.get("token_uri"),
        client_id=data.get("client_id"),
        client_secret=data.get("client_secret"),
        scopes=data.get("scopes", SCOPES),
    )

    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            save_credentials(creds)
        except Exception:
            clear_credentials()
            return None

    return creds


def clear_credentials() -> None:
    """Delete the stored token file."""
    path = _token_path()
    if path.exists():
        path.unlink()
