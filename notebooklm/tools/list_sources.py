#!/usr/bin/env python3
"""List sources in a NotebookLM notebook."""

import argparse
import asyncio

from _utils import (
    NOTEBOOKLM_HOME,
    connect_tab,
    goto_url,
    get_last_notebook,
    ensure_sources_tab,
    list_sources_raw,
    print_json,
)


def normalize_url(notebook_id: str | None, notebook_url: str | None) -> str | None:
    if notebook_url:
        return notebook_url
    if notebook_id:
        return f"https://notebooklm.google.com/notebook/{notebook_id}"
    return None


async def list_sources(port: int | None, headless: bool, name: str | None, notebook_id: str | None, notebook_url: str | None) -> dict:
    browser, tab, port, err = await connect_tab(port, NOTEBOOKLM_HOME, headless=headless)
    if err:
        return {"error": err, "sources": []}

    target_url = normalize_url(notebook_id, notebook_url)
    if not target_url and name is None:
        last = get_last_notebook()
        if last:
            target_url = last.get("url")
    if not target_url and not name:
        return {"error": "Provide --notebook-name, --notebook-id, or --notebook-url", "sources": []}

    if target_url:
        await goto_url(tab, target_url)
    await tab.sleep(3)

    # Get current notebook URL
    current_url = await tab.evaluate("window.location.href")

    await ensure_sources_tab(tab)
    await tab.sleep(1)

    # Get sources with more detail
    sources = await tab.evaluate(
        """
        (function() {
            var results = [];
            var sourceItems = document.querySelectorAll('.source-item, [data-source-id], .source-list-item');
            if (sourceItems.length === 0) {
                // Fallback: look for any items in the sources panel
                var panel = document.querySelector('.sources-panel, [class*="source"]');
                if (panel) {
                    sourceItems = panel.querySelectorAll('li, .item, [role="listitem"]');
                }
            }
            for (var i = 0; i < sourceItems.length; i++) {
                var el = sourceItems[i];
                var text = (el.textContent || '').trim();
                if (!text || text.length > 200) continue;
                var sourceId = el.getAttribute('data-source-id') || null;
                results.push({
                    name: text.split('\\n')[0].trim(),
                    sourceId: sourceId
                });
            }
            return results;
        })()
        """
    )

    # Dedupe sources
    seen = set()
    unique_sources = []
    for s in sources or []:
        name_val = s.get("name", "")
        if name_val and name_val not in seen:
            seen.add(name_val)
            unique_sources.append(s)

    return {
        "notebook_url": current_url,
        "sources": unique_sources
    }


async def main():
    parser = argparse.ArgumentParser(description="List NotebookLM sources")
    parser.add_argument("--notebook-name", dest="name", help="Notebook name")
    parser.add_argument("--notebook-id", dest="notebook_id", help="Notebook ID")
    parser.add_argument("--notebook-url", dest="notebook_url", help="Notebook URL")
    parser.add_argument("--port", "-p", type=int, help="Connect to existing browser")
    parser.add_argument("--show-browser", action="store_true", help="Show browser window")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    result = await list_sources(args.port, not args.show_browser, args.name, args.notebook_id, args.notebook_url)
    if args.json:
        print_json(result)
    else:
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Notebook: {result.get('notebook_url', 'N/A')}")
            print()
            sources = result.get("sources", [])
            for i, item in enumerate(sources, 1):
                print(f"{i}. {item['name']}")
            print(f"\nTotal: {len(sources)}")


if __name__ == "__main__":
    asyncio.run(main())
