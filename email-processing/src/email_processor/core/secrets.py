"""Secret resolution: supports raw values or Google Secret Manager references.

Convention:
  - "gsm:secret-name"  → fetches from Google Secret Manager
  - "raw-value"         → used as-is
"""

import subprocess


def resolve_secret(value: str) -> str:
    """Resolve a secret value. If prefixed with 'gsm:', fetch from Google Secret Manager."""
    if value.startswith("gsm:"):
        secret_name = value[4:]
        try:
            result = subprocess.run(
                ["gcloud", "secrets", "versions", "access", "latest",
                 f"--secret={secret_name}"],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            print(f"⚠️  Could not fetch secret '{secret_name}' from Google Secret Manager")
            return ""
    return value
