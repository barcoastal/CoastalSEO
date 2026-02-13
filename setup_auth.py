"""One-time auth setup - paste the code Google gives you."""

import json
from pathlib import Path

from google_auth_oauthlib.flow import Flow

SCOPES = [
    "https://www.googleapis.com/auth/webmasters.readonly",
    "https://www.googleapis.com/auth/webmasters",
]

import toml
secrets = toml.load(".streamlit/secrets.toml")
oauth = secrets["google_oauth"]

client_config = {
    "web": {
        "client_id": oauth["client_id"],
        "client_secret": oauth["client_secret"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
    }
}

flow = Flow.from_client_config(client_config, scopes=SCOPES, redirect_uri="urn:ietf:wg:oauth:2.0:oob")
auth_url, _ = flow.authorization_url(access_type="offline", prompt="consent")

print("\n1) Open this URL in your browser:\n")
print(auth_url)
print("\n2) Sign in and click Allow")
print("3) Copy the code Google shows you and paste it below:\n")

code = input("Paste code here: ").strip()

flow.fetch_token(code=code)
credentials = flow.credentials

token_path = Path("tokens/token.json")
token_path.parent.mkdir(parents=True, exist_ok=True)
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

token_path.write_text(json.dumps(data, indent=2))
print("\nDone! Token saved. You can now run: streamlit run app.py")
