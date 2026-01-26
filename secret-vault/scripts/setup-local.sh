#!/bin/bash
# Interactive setup for local development of Google Secret Manager skill

set -e

echo "═══════════════════════════════════════════════════════"
echo "  Secret Vault - Local Setup"
echo "═══════════════════════════════════════════════════════"
echo ""

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Check if gcloud is installed
echo "Step 1: Checking gcloud CLI installation..."
echo "-----------------------------------------------------------"
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found"
    echo ""
    echo "Please install the Google Cloud SDK:"
    echo "  https://cloud.google.com/sdk/docs/install"
    echo ""
    echo "After installation, run this script again."
    exit 1
fi

echo "✓ gcloud CLI is installed ($(gcloud version --format='value(core)' 2>/dev/null))"
echo ""

# Configure Application Default Credentials
echo "Step 2: Configuring Application Default Credentials..."
echo "-----------------------------------------------------------"
echo "This will open a browser window for authentication."
echo "You'll need to sign in with your Google account that has"
echo "access to your GCP project."
echo ""
read -p "Press Enter to continue..."
echo ""

if gcloud auth application-default login; then
    echo ""
    echo "✓ Application Default Credentials configured successfully"
else
    echo ""
    echo "❌ Failed to configure Application Default Credentials"
    exit 1
fi
echo ""

# Set GCP project
echo "Step 3: Setting GCP project..."
echo "-----------------------------------------------------------"

# Check if project is already set
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")

if [ -n "$CURRENT_PROJECT" ]; then
    echo "Current project: $CURRENT_PROJECT"
    echo ""
    read -p "Use this project? (y/n): " USE_CURRENT
    if [[ "$USE_CURRENT" =~ ^[Yy] ]]; then
        PROJECT_ID="$CURRENT_PROJECT"
    else
        echo ""
        echo "Available projects:"
        gcloud projects list --format="table(projectId,name)" 2>/dev/null || echo "  (unable to list projects)"
        echo ""
        read -p "Enter your GCP project ID: " PROJECT_ID
    fi
else
    echo "No project currently configured."
    echo ""
    echo "Available projects:"
    gcloud projects list --format="table(projectId,name)" 2>/dev/null || echo "  (unable to list projects)"
    echo ""
    read -p "Enter your GCP project ID: " PROJECT_ID
fi

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Project ID cannot be empty"
    exit 1
fi

# Set the project
if gcloud config set project "$PROJECT_ID"; then
    echo "✓ Project set to: $PROJECT_ID"
else
    echo "❌ Failed to set project"
    exit 1
fi
echo ""

# Enable Secret Manager API
echo "Step 4: Enabling Secret Manager API..."
echo "-----------------------------------------------------------"
echo "Checking if Secret Manager API is enabled..."

if gcloud services list --enabled --filter="name:secretmanager.googleapis.com" --format="value(name)" 2>/dev/null | grep -q secretmanager; then
    echo "✓ Secret Manager API is already enabled"
else
    echo "Secret Manager API is not enabled."
    read -p "Enable it now? (y/n): " ENABLE_API
    if [[ "$ENABLE_API" =~ ^[Yy] ]]; then
        if gcloud services enable secretmanager.googleapis.com; then
            echo "✓ Secret Manager API enabled successfully"
        else
            echo "❌ Failed to enable Secret Manager API"
            echo "You may need to enable it manually in the Cloud Console."
        fi
    else
        echo "⚠️  Skipped API enablement. You'll need to enable it manually."
    fi
fi
echo ""

# Verify setup
echo "Step 5: Verifying setup..."
echo "-----------------------------------------------------------"
if bash "$SCRIPT_DIR/check-auth.sh"; then
    echo ""
    echo "═══════════════════════════════════════════════════════"
    echo "  ✅ Setup completed successfully!"
    echo "═══════════════════════════════════════════════════════"
    echo ""
    echo "You can now use the /secret-vault skill:"
    echo "  /secret-vault auth-status         - Check authentication"
    echo "  /secret-vault list                - List all secrets"
    echo "  /secret-vault get <name>          - Read a secret"
    echo "  /secret-vault set <name> <value>  - Create/update a secret"
    echo "  /secret-vault delete <name>       - Delete a secret"
    echo ""
    echo "For more information, see:"
    echo "  $SKILL_DIR/SKILL.md"
    echo "  $SKILL_DIR/examples/common-patterns.md"
    echo ""
else
    echo ""
    echo "❌ Setup verification failed"
    echo "Please review the errors above and try again."
    exit 1
fi

exit 0
