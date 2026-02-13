"""Tiny server to catch the OAuth code from Google's redirect."""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from google_auth_oauthlib.flow import Flow
import toml

secrets = toml.load(".streamlit/secrets.toml")
oauth = secrets["google_oauth"]
SCOPES = [
    "https://www.googleapis.com/auth/webmasters.readonly",
    "https://www.googleapis.com/auth/webmasters",
]

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        code = query.get("code", [None])[0]
        if code:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Success! You can close this tab.</h1>")

            # Exchange code for token
            client_config = {
                "web": {
                    "client_id": oauth["client_id"],
                    "client_secret": oauth["client_secret"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost:8501"],
                }
            }
            flow = Flow.from_client_config(client_config, scopes=SCOPES, redirect_uri="http://localhost:8501")
            flow.fetch_token(code=code)
            creds = flow.credentials

            token_path = Path("tokens/token.json")
            token_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "scopes": list(creds.scopes or SCOPES),
            }
            if creds.expiry:
                data["expiry"] = creds.expiry.isoformat()
            token_path.write_text(json.dumps(data, indent=2))
            print("\nTOKEN SAVED to tokens/token.json")
            raise KeyboardInterrupt  # Stop server
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No code found")

    def log_message(self, format, *args):
        pass  # Silence logs

print("Waiting for Google redirect on http://localhost:8501 ...")
try:
    HTTPServer(("localhost", 8501), Handler).serve_forever()
except KeyboardInterrupt:
    print("Done!")
