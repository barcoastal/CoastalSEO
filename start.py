"""Startup script for Railway deployment.

Creates .streamlit/config.toml from environment variables,
then launches Streamlit.
"""

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


def setup_streamlit_config():
    """Create .streamlit/secrets.toml from individual env vars."""
    secrets_dir = PROJECT_ROOT / ".streamlit"
    secrets_dir.mkdir(parents=True, exist_ok=True)

    # Build secrets.toml from env vars
    lines = []

    api_key = os.environ.get("api_key", "")
    if api_key:
        lines.append('[anthropic]')
        lines.append('api_key = "{}"'.format(api_key))

    client_id = os.environ.get("GOOGLE_CLIENT_ID", "") or os.environ.get("client_id", "")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "") or os.environ.get("client_secret", "")
    redirect_uri = os.environ.get("redirect_uri", "https://www.coastaldebt.com")

    if client_id and client_secret:
        lines.append('')
        lines.append('[google_oauth]')
        lines.append('client_id = "{}"'.format(client_id))
        lines.append('client_secret = "{}"'.format(client_secret))
        lines.append('redirect_uri = "{}"'.format(redirect_uri))

    if lines:
        (secrets_dir / "secrets.toml").write_text("\n".join(lines) + "\n")
        print("[start.py] Created secrets.toml")


def main():
    setup_streamlit_config()

    # Ensure tokens directory exists
    (PROJECT_ROOT / "tokens").mkdir(parents=True, exist_ok=True)

    port = os.environ.get("PORT", "8501")

    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(PROJECT_ROOT / "app.py"),
        "--server.port={}".format(port),
        "--server.address=0.0.0.0",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
    ]

    print("[start.py] Starting Streamlit on port {}".format(port))
    os.chdir(str(PROJECT_ROOT))
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
