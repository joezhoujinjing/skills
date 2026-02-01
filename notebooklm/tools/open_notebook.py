#!/usr/bin/env python3
"""Open a NotebookLM notebook by name, id, or URL."""

import argparse
import asyncio
import json

from _utils import (
    NOTEBOOKLM_HOME,
    connect_tab,
    goto_url,
    update_last_notebook,
)


def normalize_url(notebook_id: str | None, notebook_url: str | None) -> str | None:
    if notebook_url:
        return notebook_url
    if notebook_id:
        return f"https://notebooklm.google.com/notebook/{notebook_id}"
    return None


async def open_notebook(port: int | None, headless: bool, name: str | None, notebook_id: str | None, notebook_url: str | None) -> dict:
    browser, tab, port, err = await connect_tab(port, NOTEBOOKLM_HOME, headless=headless)
    if err:
        return {"error": err}

    target_url = normalize_url(notebook_id, notebook_url)
    if target_url:
        await goto_url(tab, target_url)
        await tab.sleep(3)
        update_last_notebook({"url": target_url, "name": name or notebook_id or ""})
        return {"url": target_url}

    if not name:
        return {"error": "Provide --name, --id, or --url"}

    await tab.sleep(3)
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

    script = f"""
        (function() {{
            var target = {json.dumps(name.lower())};
            var cards = Array.from(document.querySelectorAll('mat-card.project-button-card, .project-button-card, project-button mat-card, project-button'));
            for (var i = 0; i < cards.length; i++) {{
                var card = cards[i];
                var text = (card.textContent || '').toLowerCase();
                if (!text.includes(target)) continue;
                var btn = card.querySelector('button') || card;
                btn.scrollIntoView({{ block: 'center', inline: 'center' }});
                btn.click();
                return true;
            }}
            return false;
        }})()
    """
    clicked = await tab.evaluate(script)
    if not clicked:
        return {"error": f"Notebook not found: {name}"}

    await tab.sleep(3)
    url = await tab.evaluate("window.location.href")
    if url:
        update_last_notebook({"url": url, "name": name})
    return {"url": url, "name": name}


async def main():
    parser = argparse.ArgumentParser(description="Open a NotebookLM notebook")
    parser.add_argument("--port", "-p", type=int, help="Connect to existing browser")
    parser.add_argument("--name", help="Notebook name (fuzzy match)")
    parser.add_argument("--id", dest="notebook_id", help="Notebook ID")
    parser.add_argument("--url", dest="notebook_url", help="Notebook URL")
    parser.add_argument("--show-browser", action="store_true", help="Show browser window")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    result = await open_notebook(args.port, not args.show_browser, args.name, args.notebook_id, args.notebook_url)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Opened: {result['url']}")


if __name__ == "__main__":
    asyncio.run(main())
