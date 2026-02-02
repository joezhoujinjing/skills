#!/usr/bin/env python3
"""Setup Jarvis browser profile."""
import sys
from pathlib import Path

JARVIS_DIR = Path.home() / ".jarvis"

try:
    import ai_dev_browser
    print(f"✓ ai-dev-browser {ai_dev_browser.__version__}")
except ImportError:
    print("Installing ai-dev-browser...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "ai-dev-browser"], check=True)
    print("✓ ai-dev-browser installed")

JARVIS_DIR.mkdir(exist_ok=True)
print(f"✓ Jarvis profile: {JARVIS_DIR}")
print(f"ℹ Cookies: {JARVIS_DIR}/cookies.dat (created on first login)")
print("\nReady! Use jarvis_start to launch browser.")
