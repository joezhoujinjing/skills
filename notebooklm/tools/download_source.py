#!/usr/bin/env python3
"""Download/extract source content from a NotebookLM notebook."""

import argparse
import asyncio
import json
from pathlib import Path

from _utils import (
    NOTEBOOKLM_HOME,
    connect_tab,
    goto_url,
    get_last_notebook,
    ensure_sources_tab,
    print_json,
    ensure_data_dir,
    DATA_DIR,
)

CONTENT_SELECTORS = [
    '[data-testid="source-content"]',
    '.source-content',
    'main',
]


def normalize_url(notebook_id: str | None, notebook_url: str | None) -> str | None:
    if notebook_url:
        return notebook_url
    if notebook_id:
        return f"https://notebooklm.google.com/notebook/{notebook_id}"
    return None


async def open_source(tab, source: str) -> bool:
    script = f"""
        (function() {{
            var target = {json.dumps(source.lower())};
            var candidates = Array.from(document.querySelectorAll('[data-source-id], li, div, a'));
            for (var i = 0; i < candidates.length; i++) {{
                var el = candidates[i];
                var text = (el.textContent || '').trim().toLowerCase();
                if (!text || !text.includes(target)) continue;
                el.scrollIntoView({{ block: 'center', inline: 'center' }});
                el.click();
                return true;
            }}
            return false;
        }})()
    """
    return bool(await tab.evaluate(script))


async def extract_source_text(tab) -> str | None:
    for sel in CONTENT_SELECTORS:
        script = f"""
            (function() {{
                var el = document.querySelector({json.dumps(sel)});
                if (!el) return null;
                var text = (el.textContent || '').trim();
                return text || null;
            }})()
        """
        text = await tab.evaluate(script)
        if text:
            return text
    return None


async def download_source(port: int | None, headless: bool, name: str | None, notebook_id: str | None, notebook_url: str | None, source: str, out_path: str | None) -> dict:
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

    opened = await open_source(tab, source)
    if not opened:
        return {"error": f"Source not found: {source}"}

    await tab.sleep(2)
    text = await extract_source_text(tab)
    if not text:
        return {"error": "Could not extract source content"}

    ensure_data_dir()
    if out_path:
        out_file = Path(out_path).expanduser()
    else:
        downloads_dir = DATA_DIR / "downloads"
        downloads_dir.mkdir(parents=True, exist_ok=True)
        safe = "".join([c for c in source if c.isalnum() or c in "-_ "]).strip() or "source"
        out_file = downloads_dir / f"{safe}.txt"

    out_file.write_text(text)
    return {"status": "saved", "path": str(out_file)}


async def main():
    parser = argparse.ArgumentParser(description="Download NotebookLM source")
    parser.add_argument("source", help="Source name (partial match)")
    parser.add_argument("--notebook-name", dest="name", help="Notebook name")
    parser.add_argument("--notebook-id", dest="notebook_id", help="Notebook ID")
    parser.add_argument("--notebook-url", dest="notebook_url", help="Notebook URL")
    parser.add_argument("-o", "--out", dest="out_path", help="Output path")
    parser.add_argument("--port", "-p", type=int, help="Connect to existing browser")
    parser.add_argument("--show-browser", action="store_true", help="Show browser window")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    result = await download_source(args.port, not args.show_browser, args.name, args.notebook_id, args.notebook_url, args.source, args.out_path)
    if args.json:
        print_json(result)
    else:
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Saved to: {result['path']}")


if __name__ == "__main__":
    asyncio.run(main())
