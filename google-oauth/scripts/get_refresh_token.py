#!/usr/bin/env python3
"""
Generate OAuth 2.0 refresh token for Google services.

Usage:
    python get_refresh_token.py "scope1 scope2 ..." [--port PORT]

Example:
    python get_refresh_token.py "https://mail.google.com/" --port 8080
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

def get_secret(secret_name):
    """Retrieve secret from Google Secret Manager."""
    try:
        result = subprocess.run(
            ['gcloud', 'secrets', 'versions', 'access', 'latest', f'--secret={secret_name}'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving secret '{secret_name}': {e.stderr}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Generate Google OAuth 2.0 refresh token')
    parser.add_argument('scopes', help='Space-separated OAuth scopes')
    parser.add_argument('--port', type=int, default=8080, help='Local server port (default: 8080)')
    args = parser.parse_args()

    # Parse scopes
    scopes = args.scopes.split()
    if not scopes:
        print("Error: At least one scope is required", file=sys.stderr)
        sys.exit(1)

    print(f"📋 Requesting scopes:")
    for scope in scopes:
        print(f"   - {scope}")
    print()

    # Fetch credentials from secret vault
    print("🔐 Fetching OAuth credentials from secret-vault...")
    client_id = get_secret('NEXUS_OAUTH_GOOGLE_CLIENT_ID')
    client_secret = get_secret('NEXUS_OAUTH_GOOGLE_CLIENT_SECRET')
    print(f"   Client ID: {client_id[:20]}...")
    print()

    # Create temporary credentials file
    credentials = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": [f"http://localhost:{args.port}"]
        }
    }

    temp_creds_file = Path("/tmp/google_oauth_credentials.json")
    with open(temp_creds_file, 'w') as f:
        json.dump(credentials, f)

    # Run OAuth flow
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow

        print(f"🌐 Starting OAuth flow on http://localhost:{args.port}")
        print("   Your browser will open automatically...")
        print()

        flow = InstalledAppFlow.from_client_secrets_file(
            str(temp_creds_file),
            scopes=scopes
        )

        creds = flow.run_local_server(port=args.port, open_browser=True)

        print()
        print("✅ Authorization successful!")
        print()
        print("=" * 70)
        print("REFRESH TOKEN:")
        print("=" * 70)
        print(creds.refresh_token)
        print("=" * 70)
        print()
        print("💾 To store this token in secret-vault, run:")
        print(f"   /secret-vault set <secret-name> \"{creds.refresh_token}\"")
        print()
        print("Example:")
        print("   /secret-vault set gmail-refresh-token \"<token>\"")
        print()

    except ImportError:
        print("❌ Error: google-auth-oauthlib is not installed", file=sys.stderr)
        print("   Install it with: pip install google-auth-oauthlib", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during OAuth flow: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Clean up temporary file
        if temp_creds_file.exists():
            temp_creds_file.unlink()

if __name__ == '__main__':
    main()
