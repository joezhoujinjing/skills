#!/usr/bin/env python3
"""Add a source (URL or file) to a NotebookLM notebook."""

import argparse
import asyncio
from pathlib import Path

from _utils import (
    NOTEBOOKLM_HOME,
    connect_tab,
    goto_url,
    get_last_notebook,
    ensure_sources_tab,
    click_first,
    fill_first,
)
import nb_selectors as nb_selectors

FILE_OPTION_SELECTORS = [
    'button:has-text("Upload")',
    'button:has-text("File")',
    '[data-source-type="file"]',
    'div[role="option"]:has-text("Upload")',
]

FILE_INPUT_SELECTORS = [
    'input[type="file"]',
    'input[accept]'
]


def normalize_url(notebook_id: str | None, notebook_url: str | None) -> str | None:
    if notebook_url:
        return notebook_url
    if notebook_id:
        return f"https://notebooklm.google.com/notebook/{notebook_id}"
    return None


async def add_source(port: int | None, headless: bool, name: str | None, notebook_id: str | None, notebook_url: str | None, url: str | None, file_path: str | None) -> dict:
    browser, tab, port, err = await connect_tab(port, NOTEBOOKLM_HOME, headless=headless)
    if err:
        return {"error": err}

    target_url = normalize_url(notebook_id, notebook_url)
    if not target_url and name is None:
        last = get_last_notebook()
        if last:
            target_url = last.get("url")
    if not target_url and not name:
        return {"error": "Provide --notebook-name, --notebook-id, or --notebook-url"}

    if target_url:
        await goto_url(tab, target_url)
    await tab.sleep(3)

    await ensure_sources_tab(tab)
    await tab.sleep(1)

    add_clicked = await click_first(tab, nb_selectors.ADD_SOURCE_BUTTON_SELECTORS)
    if not add_clicked:
        return {"error": "Could not find Add source button"}

    await tab.sleep(1)

    if url:
        await click_first(tab, nb_selectors.WEBSITE_OPTION_SELECTORS)
        await tab.sleep(0.5)
        filled = await fill_first(tab, nb_selectors.URL_INPUT_SELECTORS, url)
        if not filled:
            return {"error": "Could not fill URL input"}
        await tab.sleep(0.5)
        await click_first(tab, nb_selectors.SUBMIT_BUTTON_SELECTORS)
        return {"status": "submitted", "url": url}

    if file_path:
        await click_first(tab, FILE_OPTION_SELECTORS)
        await tab.sleep(0.5)
        file_path = str(Path(file_path).expanduser())

        uploaded = False
        for sel in FILE_INPUT_SELECTORS:
            exists = await tab.evaluate(f"!!document.querySelector({sel!r})")
            if not exists:
                continue
            if hasattr(tab, "set_input_files"):
                await tab.set_input_files(sel, file_path)
                uploaded = True
                break
            if hasattr(tab, "upload_file"):
                await tab.upload_file(sel, file_path)
                uploaded = True
                break

        if not uploaded:
            return {"error": "File input not found or upload API unavailable"}
        await tab.sleep(1)
        return {"status": "uploaded", "file": file_path}

    return {"error": "Provide --url or --file"}


async def main():
    parser = argparse.ArgumentParser(description="Add source to NotebookLM")
    parser.add_argument("--notebook-name", dest="name", help="Notebook name")
    parser.add_argument("--notebook-id", dest="notebook_id", help="Notebook ID")
    parser.add_argument("--notebook-url", dest="notebook_url", help="Notebook URL")
    parser.add_argument("--url", help="Website or YouTube URL")
    parser.add_argument("--file", dest="file_path", help="Local file to upload")
    parser.add_argument("--port", "-p", type=int, help="Connect to existing browser")
    parser.add_argument("--show-browser", action="store_true", help="Show browser window")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    result = await add_source(args.port, not args.show_browser, args.name, args.notebook_id, args.notebook_url, args.url, args.file_path)
    if args.json:
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(result)


if __name__ == "__main__":
    asyncio.run(main())
