#!/bin/bash
# Check if Google OAuth setup is ready

echo "🔍 Checking Google OAuth setup..."
echo ""

# Check gcloud
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found"
    echo "   Install: https://cloud.google.com/sdk/docs/install"
    exit 1
fi
echo "✅ gcloud CLI installed"

# Check gcloud auth
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo "❌ gcloud not authenticated"
    echo "   Run: gcloud auth login"
    exit 1
fi
echo "✅ gcloud authenticated"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi
echo "✅ Python 3 installed"

# Check google-auth-oauthlib
if ! python3 -c "import google_auth_oauthlib" 2> /dev/null; then
    echo "❌ google-auth-oauthlib not installed"
    echo "   Install: pip install google-auth-oauthlib"
    exit 1
fi
echo "✅ google-auth-oauthlib installed"

# Check credentials in secret vault
if ! gcloud secrets describe NEXUS_OAUTH_GOOGLE_CLIENT_ID &> /dev/null; then
    echo "❌ NEXUS_OAUTH_GOOGLE_CLIENT_ID not found in secret-vault"
    exit 1
fi
echo "✅ OAuth Client ID found in secret-vault"

if ! gcloud secrets describe NEXUS_OAUTH_GOOGLE_CLIENT_SECRET &> /dev/null; then
    echo "❌ NEXUS_OAUTH_GOOGLE_CLIENT_SECRET not found in secret-vault"
    exit 1
fi
echo "✅ OAuth Client Secret found in secret-vault"

echo ""
echo "✅ All checks passed! Ready to generate refresh tokens."
echo ""
echo "Usage:"
echo "  /google-oauth get-token \"https://mail.google.com/\""
echo ""
echo "⚠️  Important: Ensure http://localhost:8080 is added to your"
echo "    OAuth client's authorized redirect URIs in Google Cloud Console:"
echo "    https://console.cloud.google.com/apis/credentials"
