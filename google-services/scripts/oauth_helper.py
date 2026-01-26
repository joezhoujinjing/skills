#!/usr/bin/env python3
"""
Shared OAuth helper for Google Services skill.
Handles authentication and credential management.
"""

import subprocess
import sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Default secret names in secret-vault
DEFAULT_CLIENT_ID_SECRET = "NEXUS_OAUTH_GOOGLE_CLIENT_ID"
DEFAULT_CLIENT_SECRET_SECRET = "NEXUS_OAUTH_GOOGLE_CLIENT_SECRET"
DEFAULT_REFRESH_TOKEN_SECRET = "google-all-services-refresh-token-joezhoujinjing-gmail-com"


def get_secret(secret_name):
    """Retrieve a secret from Google Secret Manager via gcloud."""
    try:
        result = subprocess.run(
            ["gcloud", "secrets", "versions", "access", "latest", f"--secret={secret_name}"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to retrieve secret '{secret_name}': {e.stderr}", file=sys.stderr)
        sys.exit(1)


def get_credentials(refresh_token_secret=None, scopes=None):
    """
    Get Google API credentials using OAuth refresh token.

    Args:
        refresh_token_secret: Name of secret containing refresh token
        scopes: List of OAuth scopes (optional, for reference)

    Returns:
        google.oauth2.credentials.Credentials object
    """
    if refresh_token_secret is None:
        refresh_token_secret = DEFAULT_REFRESH_TOKEN_SECRET

    # Retrieve OAuth credentials from secret-vault
    client_id = get_secret(DEFAULT_CLIENT_ID_SECRET)
    client_secret = get_secret(DEFAULT_CLIENT_SECRET_SECRET)
    refresh_token = get_secret(refresh_token_secret)

    # Create credentials object
    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=scopes
    )

    # Refresh the access token
    credentials.refresh(Request())

    return credentials


def print_auth_info(service_name):
    """Print authentication info for debugging."""
    print(f"🔐 Authenticating with Google {service_name} API...")
    print(f"   Using refresh token from: {DEFAULT_REFRESH_TOKEN_SECRET}")
