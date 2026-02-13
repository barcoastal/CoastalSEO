"""Build authenticated Google API service objects."""

import json
import os
import re
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from utils.constants import SCOPES, TOKEN_FILE

# Store last error for debug display
_last_error = None


def get_last_error():
    """Return the last credential loading error for debugging."""
    return _last_error


def _load_credentials():
    """Load and refresh credentials from saved token file or env var."""
    global _last_error
    _last_error = None
    data = None

    # Try 1: token file relative to project root
    base = Path(__file__).resolve().parent.parent
    token_path = base / TOKEN_FILE
    if token_path.exists():
        try:
            raw = token_path.read_text()
            # Strip control characters that cloud platforms may inject
            raw = re.sub(r'[\x00-\x09\x0b\x0c\x0e-\x1f\x7f]', '', raw)
            data = json.loads(raw)
        except (json.JSONDecodeError, OSError) as e:
            _last_error = "File read/parse error: {}".format(e)

    # Try 2: GOOGLE_TOKEN_JSON environment variable
    if data is None:
        env_token = os.environ.get("GOOGLE_TOKEN_JSON", "")
        if env_token:
            try:
                # Strip control characters that cloud platforms may inject
                env_token = re.sub(r'[\x00-\x09\x0b\x0c\x0e-\x1f\x7f]', '', env_token)
                data = json.loads(env_token)
            except json.JSONDecodeError as e:
                _last_error = "Env var JSON parse error: {}".format(e)

    if data is None:
        if _last_error is None:
            _last_error = "No token file and no GOOGLE_TOKEN_JSON env var"
        return None

    try:
        creds = Credentials(
            token=data.get("token"),
            refresh_token=data.get("refresh_token"),
            token_uri=data.get("token_uri"),
            client_id=data.get("client_id"),
            client_secret=data.get("client_secret"),
            scopes=data.get("scopes", SCOPES),
        )
    except Exception as e:
        _last_error = "Credentials creation failed: {}".format(e)
        return None

    try:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            data["token"] = creds.token
            if creds.expiry:
                data["expiry"] = creds.expiry.isoformat()
            try:
                token_path.parent.mkdir(parents=True, exist_ok=True)
                token_path.write_text(json.dumps(data, indent=2))
            except OSError:
                pass
    except Exception as e:
        _last_error = "Token refresh failed: {}. Returning stale credentials.".format(e)
        # Still return the creds even if refresh failed — the token might still work
        return creds

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
