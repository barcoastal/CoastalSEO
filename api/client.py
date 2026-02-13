"""Build authenticated Google API service objects."""

import json
import os
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from utils.constants import SCOPES, TOKEN_FILE

# Store last error for debug display
_last_error = None


def get_last_error():
    """Return the last credential loading error for debugging."""
    return _last_error


def _load_from_file():
    """Try loading token data from the JSON file."""
    base = Path(__file__).resolve().parent.parent
    token_path = base / TOKEN_FILE
    if not token_path.exists():
        return None
    try:
        return json.loads(token_path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _load_from_env_vars():
    """Build token data from individual environment variables."""
    refresh_token = os.environ.get("GOOGLE_REFRESH_TOKEN", "")
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "")

    if refresh_token and client_id and client_secret:
        return {
            "token": None,
            "refresh_token": refresh_token,
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": client_id,
            "client_secret": client_secret,
            "scopes": SCOPES,
        }
    return None


def _load_credentials():
    """Load and refresh credentials from file or env vars."""
    global _last_error
    _last_error = None

    # Try 1: token file
    data = _load_from_file()

    # Try 2: individual env vars (no JSON parsing needed)
    if data is None:
        data = _load_from_env_vars()

    if data is None:
        _last_error = "No token file found and GOOGLE_REFRESH_TOKEN/GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET env vars not set"
        return None

    try:
        creds = Credentials(
            token=data.get("token"),
            refresh_token=data.get("refresh_token"),
            token_uri=data.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=data.get("client_id"),
            client_secret=data.get("client_secret"),
            scopes=data.get("scopes", SCOPES),
        )
    except Exception as e:
        _last_error = "Credentials creation failed: {}".format(e)
        return None

    # Refresh if expired or no access token
    if (not creds.token or creds.expired) and creds.refresh_token:
        try:
            creds.refresh(Request())
            # Save refreshed token to file if possible
            try:
                base = Path(__file__).resolve().parent.parent
                token_path = base / TOKEN_FILE
                token_path.parent.mkdir(parents=True, exist_ok=True)
                save_data = {
                    "token": creds.token,
                    "refresh_token": creds.refresh_token,
                    "token_uri": creds.token_uri,
                    "client_id": creds.client_id,
                    "client_secret": creds.client_secret,
                    "scopes": list(creds.scopes or SCOPES),
                }
                if creds.expiry:
                    save_data["expiry"] = creds.expiry.isoformat()
                token_path.write_text(json.dumps(save_data, indent=2))
            except OSError:
                pass
        except Exception as e:
            _last_error = "Token refresh failed: {}".format(e)
            return None

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
