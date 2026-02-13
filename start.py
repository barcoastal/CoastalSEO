"""Startup script for Railway deployment.

Creates secrets.toml and token.json from environment variables,
then launches Streamlit.
"""

import os
import subprocess
import sys
from pathlib import Path

# Resolve project root as the directory containing this script
PROJECT_ROOT = Path(__file__).resolve().parent


def setup_secrets():
    """Create .streamlit/secrets.toml from environment variables."""
    secrets_dir = PROJECT_ROOT / ".streamlit"
    secrets_dir.mkdir(parents=True, exist_ok=True)

    secrets_content = os.environ.get("STREAMLIT_SECRETS", "")
    if secrets_content:
        (secrets_dir / "secrets.toml").write_text(secrets_content)
        print("[start.py] Created {}".format(secrets_dir / "secrets.toml"))
    else:
        print("[start.py] WARNING: STREAMLIT_SECRETS env var not set")


def setup_token():
    """Create tokens/token.json from environment variable."""
    tokens_dir = PROJECT_ROOT / "tokens"
    tokens_dir.mkdir(parents=True, exist_ok=True)

    token_content = os.environ.get("GOOGLE_TOKEN_JSON", "")
    if token_content:
        token_path = tokens_dir / "token.json"
        token_path.write_text(token_content)
        print("[start.py] Created {}".format(token_path))
    else:
        print("[start.py] WARNING: GOOGLE_TOKEN_JSON env var not set")


def main():
    setup_secrets()
    setup_token()

    # Verify files exist
    token_path = PROJECT_ROOT / "tokens" / "token.json"
    secrets_path = PROJECT_ROOT / ".streamlit" / "secrets.toml"
    print("[start.py] Token exists: {}".format(token_path.exists()))
    print("[start.py] Secrets exists: {}".format(secrets_path.exists()))
    print("[start.py] Working directory: {}".format(os.getcwd()))
    print("[start.py] Project root: {}".format(PROJECT_ROOT))

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
