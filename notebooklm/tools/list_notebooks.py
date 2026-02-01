#!/usr/bin/env python3
"""List NotebookLM notebooks."""

import argparse
import asyncio
import re

from _utils import (
    NOTEBOOKLM_HOME,
    connect_tab,
    unwrap_cdp,
    print_json,
)


async def list_notebooks(port: int | None, headless: bool) -> list[dict]:
    browser, tab, port, err = await connect_tab(port, NOTEBOOKLM_HOME, headless=headless)
    if err:
        return []
    await tab.sleep(3)

    # Click "My notebooks" or "All" tab via text matching
    await tab.evaluate(
        """
        (function() {
            var btns = Array.from(document.querySelectorAll('button,[role=tab]'));
            var target = null;
            for (var i = 0; i < btns.length; i++) {
                var text = (btns[i].textContent || '').toLowerCase();
                if (text.includes('my notebooks')) { target = btns[i]; break; }
            }
            if (!target) {
                for (var i = 0; i < btns.length; i++) {
                    var text = (btns[i].textContent || '').toLowerCase();
                    if (text.includes('all')) { target = btns[i]; break; }
                }
            }
            if (target) target.click();
            return true;
        })()
        """
    )
    await tab.sleep(2)

    raw_items = await tab.evaluate(
        """
        (function() {
            var cards = Array.from(document.querySelectorAll('mat-card.project-button-card, .project-button-card, project-button mat-card, project-button'));
            var out = [];
            for (var i = 0; i < cards.length; i++) {
                var card = cards[i];
                var text = (card.textContent || '').replace(/\\s+/g, ' ').trim();
                if (!text) continue;
                // Extract notebook ID from aria-labelledby attribute (format: project-{uuid}-title)
                var btn = card.querySelector('button[aria-labelledby*="project-"]');
                var notebookId = null;
                if (btn) {
                    var labelledBy = btn.getAttribute('aria-labelledby') || '';
                    var match = labelledBy.match(/project-([a-f0-9-]+)-title/);
                    if (match) notebookId = match[1];
                }
                out.push({ text: text, notebookId: notebookId });
            }
            return out;
        })()
        """
    )
    items = unwrap_cdp(raw_items)

    results = []
    seen_ids = set()
    for item in items or []:
        text = (item.get("text") or "").strip()
        if not text:
            continue
        # Deduplicate by notebook ID, not by text (allows same-name notebooks)
        notebook_id = item.get("notebookId")
        if notebook_id:
            if notebook_id in seen_ids:
                continue
            seen_ids.add(notebook_id)

        # Parse name, created_at, num_of_sources from text
        # Format: "📔more_vert Title Fix Test Feb 1, 2026·0 sources"
        name = text
        created_at = None
        num_of_sources = 0

        # Extract sources count
        if "·" in text:
            parts = text.split("·")
            name_part = parts[0].strip()
            sources_part = parts[1].strip() if len(parts) > 1 else ""
            # Parse "0 sources" or "3 sources"
            match = re.search(r"(\d+)\s*source", sources_part)
            if match:
                num_of_sources = int(match.group(1))
            name = name_part

        # Clean up name - remove emoji prefix and "more_vert"
        name = name.replace("more_vert", "").strip()

        # Extract date (format: "Mon DD, YYYY" at the end)
        date_match = re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}", name)
        if date_match:
            created_at = date_match.group(0)
            # Remove date from name
            name = name[:date_match.start()].strip()

        # Remove leading emoji if present
        if name and ord(name[0]) > 127:
            # Skip emoji characters at start
            i = 0
            while i < len(name) and (ord(name[i]) > 127 or name[i] in ' \ufe0f'):
                i += 1
            name = name[i:].strip()

        if not name or name.lower() == "add create new":
            continue

        # Build URL from notebook ID
        notebook_id = item.get("notebookId")
        url = f"https://notebooklm.google.com/notebook/{notebook_id}" if notebook_id else None

        results.append({
            "name": name,
            "created_at": created_at,
            "url": url,
            "num_of_sources": num_of_sources
        })
    return results


async def main():
    parser = argparse.ArgumentParser(description="List NotebookLM notebooks")
    parser.add_argument("--port", "-p", type=int, help="Connect to existing browser")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--show-browser", action="store_true", help="Show browser window")
    args = parser.parse_args()

    results = await list_notebooks(args.port, headless=not args.show_browser)
    if args.json:
        print_json(results)
    else:
        for i, item in enumerate(results, 1):
            print(f"{i}. {item['name']}")
        print(f"\nTotal: {len(results)}")


if __name__ == "__main__":
    asyncio.run(main())
