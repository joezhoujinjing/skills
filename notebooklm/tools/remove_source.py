#!/usr/bin/env python3
"""Remove a source from NotebookLM by name (partial match)."""

import argparse
import asyncio
import json

from _utils import (
    NOTEBOOKLM_HOME,
    connect_tab,
    goto_url,
    get_last_notebook,
    ensure_sources_tab,
    print_json,
)

REMOVE_SELECTORS = [
    'button:has-text("Remove")',
    'button:has-text("Delete")',
    'button[aria-label*="Remove"]',
    'button[aria-label*="Delete"]',
]


def normalize_url(notebook_id: str | None, notebook_url: str | None) -> str | None:
    if notebook_url:
        return notebook_url
    if notebook_id:
        return f"https://notebooklm.google.com/notebook/{notebook_id}"
    return None


async def remove_source(port: int | None, headless: bool, name: str | None, notebook_id: str | None, notebook_url: str | None, source: str) -> dict:
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

    selectors_js = json.dumps(REMOVE_SELECTORS)
    script = f"""
        (function() {{
            var target = {json.dumps(source.lower())};
            var selectors = {selectors_js};
            var candidates = Array.from(document.querySelectorAll('[data-source-id], li, div'));
            for (var i = 0; i < candidates.length; i++) {{
                var el = candidates[i];
                var text = (el.textContent || '').trim().toLowerCase();
                if (!text || !text.includes(target)) continue;
                var container = el.closest('[data-source-id]') || el.closest('li') || el.closest('div');
                if (!container) continue;
                for (var j = 0; j < selectors.length; j++) {{
                    var btn = container.querySelector(selectors[j]);
                    if (btn) {{
                        btn.click();
                        return true;
                    }}
                }}
            }}
            return false;
        }})()
    """
    removed = await tab.evaluate(script)
    if not removed:
        return {"error": f"Source not found or remove button missing: {source}"}

    return {"status": "removed", "source": source}


async def main():
    parser = argparse.ArgumentParser(description="Remove NotebookLM source")
    parser.add_argument("source", help="Source name (partial match)")
    parser.add_argument("--notebook-name", dest="name", help="Notebook name")
    parser.add_argument("--notebook-id", dest="notebook_id", help="Notebook ID")
    parser.add_argument("--notebook-url", dest="notebook_url", help="Notebook URL")
    parser.add_argument("--port", "-p", type=int, help="Connect to existing browser")
    parser.add_argument("--show-browser", action="store_true", help="Show browser window")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    result = await remove_source(args.port, not args.show_browser, args.name, args.notebook_id, args.notebook_url, args.source)
    if args.json:
        print_json(result)
    else:
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Removed: {result['source']}")


if __name__ == "__main__":
    asyncio.run(main())
