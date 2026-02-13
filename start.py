"""Startup script for Railway deployment.

Creates secrets.toml and token.json from environment variables,
then launches Streamlit.
"""

import os
import subprocess
import sys


def setup_secrets():
    """Create .streamlit/secrets.toml from environment variables."""
    os.makedirs(".streamlit", exist_ok=True)

    secrets_content = os.environ.get("STREAMLIT_SECRETS", "")
    if secrets_content:
        with open(".streamlit/secrets.toml", "w") as f:
            f.write(secrets_content)
        print("[start.py] Created .streamlit/secrets.toml")
    else:
        print("[start.py] WARNING: STREAMLIT_SECRETS env var not set")


def setup_token():
    """Create tokens/token.json from environment variable."""
    os.makedirs("tokens", exist_ok=True)

    token_content = os.environ.get("GOOGLE_TOKEN_JSON", "")
    if token_content:
        with open("tokens/token.json", "w") as f:
            f.write(token_content)
        print("[start.py] Created tokens/token.json")
    else:
        print("[start.py] WARNING: GOOGLE_TOKEN_JSON env var not set")


def main():
    setup_secrets()
    setup_token()

    port = os.environ.get("PORT", "8501")

    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port={}".format(port),
        "--server.address=0.0.0.0",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
    ]

    print("[start.py] Starting Streamlit on port {}".format(port))
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
