#!/bin/bash
# Verify Google Cloud authentication and project setup

set -e

echo "Checking Google Cloud authentication..."
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ ERROR: gcloud CLI not installed"
    echo ""
    echo "Install gcloud CLI from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "✓ gcloud CLI installed ($(gcloud version --format='value(core)' 2>/dev/null))"

# Check Application Default Credentials
if ! gcloud auth application-default print-access-token &> /dev/null; then
    echo "❌ ERROR: Application Default Credentials not configured"
    echo ""
    echo "To set up authentication, run:"
    echo "  gcloud auth application-default login"
    echo ""
    echo "Or set GOOGLE_APPLICATION_CREDENTIALS environment variable to a service account key file:"
    echo "  export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json"
    exit 1
fi

echo "✓ Application Default Credentials configured"

# Check project configuration
PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT" ]; then
    PROJECT="${GCP_PROJECT}"
fi

if [ -z "$PROJECT" ]; then
    echo "❌ ERROR: No GCP project configured"
    echo ""
    echo "To set a project, run:"
    echo "  gcloud config set project YOUR_PROJECT_ID"
    echo ""
    echo "Or set GCP_PROJECT environment variable:"
    echo "  export GCP_PROJECT=your-project-id"
    exit 1
fi

echo "✓ GCP Project: $PROJECT"

# Check if Secret Manager API is enabled (best effort - may fail if no permission to check)
if gcloud services list --enabled --filter="name:secretmanager.googleapis.com" --format="value(name)" 2>/dev/null | grep -q secretmanager; then
    echo "✓ Secret Manager API enabled"
else
    echo "⚠️  Warning: Could not verify Secret Manager API status"
    echo "   If API is not enabled, run:"
    echo "   gcloud services enable secretmanager.googleapis.com"
fi

echo ""
echo "✅ Authentication check passed!"
echo ""
echo "You can now use the /secrets skill to manage secrets in project: $PROJECT"

exit 0
