#!/usr/bin/env python3
"""Manage NotebookLM authentication using the Jarvis profile."""

import argparse
import asyncio
from pathlib import Path

from _utils import (
    NOTEBOOKLM_HOME,
    ensure_profile_dir,
    get_profile_dir,
    login_interactive,
    connect_tab,
)


def profile_status() -> dict:
    profile_dir = get_profile_dir()
    exists = profile_dir.exists() and any(profile_dir.iterdir())
    return {
        "profile": profile_dir.as_posix(),
        "exists": exists,
    }


async def check_login() -> dict:
    browser, tab, port, err = await connect_tab(None, NOTEBOOKLM_HOME, headless=False)
    if err:
        return {"error": err}
    await tab.sleep(3)

    logged_in = await tab.evaluate(
        """
        (() => {
            const text = document.body ? document.body.innerText : '';
            if (!text) return true;
            const lowered = text.toLowerCase();
            if (lowered.includes('sign in') || lowered.includes('log in')) return false;
            return true;
        })()
        """
    )
    return {"logged_in": bool(logged_in), "port": port}


def main():
    parser = argparse.ArgumentParser(description="NotebookLM auth manager")
    parser.add_argument("action", choices=["status", "setup", "reauth", "clear"])
    parser.add_argument("--check", action="store_true", help="Open browser and check if logged in")
    args = parser.parse_args()

    if args.action == "status":
        info = profile_status()
        print(f"Profile: {info['profile']}")
        print(f"Exists: {info['exists']}")
        if args.check:
            result = asyncio.run(check_login())
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(f"Logged in: {result['logged_in']}")
        return

    if args.action in {"setup", "reauth"}:
        ensure_profile_dir()
        result = login_interactive(NOTEBOOKLM_HOME)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print("Browser opened for login. Complete Google login in the Jarvis profile.")
        return

    if args.action == "clear":
        profile_dir = get_profile_dir()
        if profile_dir.exists():
            for item in profile_dir.iterdir():
                if item.is_dir():
                    for sub in item.rglob('*'):
                        try:
                            if sub.is_file() or sub.is_symlink():
                                sub.unlink()
                        except Exception:
                            pass
                else:
                    try:
                        item.unlink()
                    except Exception:
                        pass
            print(f"Cleared profile data at {profile_dir}")
        else:
            print("Profile does not exist")


if __name__ == "__main__":
    main()
