#!/usr/bin/env python3
"""Create a new NotebookLM notebook."""

import argparse
import asyncio
import time
import json

from _utils import (
    NOTEBOOKLM_HOME,
    connect_tab,
    wait_for_home,
    click_first,
    fill_first,
    update_last_notebook,
)
import nb_selectors as nb_selectors


NOTEBOOK_NAME_SELECTORS = [
    'input.title-input',  # Primary selector for NotebookLM title input
    'input[class*="title-input"]',
    'input[aria-label*="Notebook"]',
    'input[placeholder*="Notebook"]',
    'input[aria-label*="notebook"]',
    '[contenteditable="true"][role="textbox"]',
]


async def create_notebook(port: int | None, headless: bool, name: str | None) -> dict:
    browser, tab, port, err = await connect_tab(port, NOTEBOOKLM_HOME, headless=headless)
    if err:
        return {"error": err}
    await tab.sleep(2)
    await wait_for_home(tab)

    # Click create button - try aria-label first, then text match
    clicked = await tab.evaluate(
        '(function() {'
        'var btn = document.querySelector(\'button[aria-label="Create new notebook"]\');'
        'if (btn) { btn.click(); return true; }'
        'btn = document.querySelector(\'button[aria-label*="Create"]\');'
        'if (btn) { btn.click(); return true; }'
        'btn = document.querySelector(\'.create-notebook-button\');'
        'if (btn) { btn.click(); return true; }'
        'var buttons = Array.from(document.querySelectorAll(\'button, a\'));'
        'for (var i = 0; i < buttons.length; i++) {'
        'var text = (buttons[i].textContent || \'\').toLowerCase();'
        'if (text.includes(\'new notebook\') || text.includes(\'create new\')) {'
        'buttons[i].click(); return true; }}'
        'return false; })()'
    )
    if not clicked:
        clicked = await click_first(tab, nb_selectors.NEW_NOTEBOOK_SELECTORS)
    if not clicked:
        return {"error": "Could not find 'New notebook' button"}

    await tab.sleep(2)

    # Wait for navigation to the new notebook page (by URL or by time)
    url = None
    deadline = time.time() + 45  # Increased from 25 to 45 seconds
    while time.time() < deadline:
        url = await tab.evaluate("window.location.href")
        if url and isinstance(url, str) and "/notebook/" in url:
            if "?" in url:
                url = url.split("?")[0]
            break
        url = None
        await tab.sleep(0.5)

    if not url or "/notebook/" not in str(url):
        await tab.sleep(2)
        href = await tab.evaluate("window.location.href")
        if href and "/notebook/" in str(href):
            url = href.split("?")[0] if "?" in href else href

    # We're now on the newly opened notebook page. Edit the title when name is provided.
    if name:
        await tab.sleep(2)
        # Dismiss any overlay/dialog so the title field is accessible
        await tab.evaluate(
            '(function() { var c = document.querySelector(\'button[aria-label="Close"]\'); if (c) c.click(); })()'
        )
        await tab.sleep(1)

        # Direct approach: find input.title-input and set value with proper Angular events
        rename_script = (
            "(function() {"
            "var name = " + json.dumps(name) + ";"
            "var el = document.querySelector('input.title-input');"
            "if (!el) el = document.querySelector('input[class*=\"title-input\"]');"
            "if (!el) {"
            "  var inps = document.querySelectorAll('input');"
            "  for (var i = 0; i < inps.length; i++) {"
            "    if ((inps[i].value || '').toLowerCase().includes('untitled')) { el = inps[i]; break; }"
            "  }"
            "}"
            "if (!el) return false;"
            "el.focus();"
            "el.select();"
            "var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;"
            "nativeInputValueSetter.call(el, name);"
            "el.dispatchEvent(new Event('input', { bubbles: true }));"
            "el.dispatchEvent(new Event('change', { bubbles: true }));"
            "el.dispatchEvent(new Event('blur', { bubbles: true }));"
            "return true;"
            "})()"
        )

        for attempt in range(3):
            ok = await tab.evaluate(rename_script)
            if ok:
                await tab.sleep(0.5)
                # Verify it was set
                current = await tab.evaluate("(document.querySelector('input.title-input') || {}).value")
                if current == name:
                    break
            await tab.sleep(1)

        await tab.sleep(1)

    # Re-read URL once we're on the notebook page (SPA may update address bar late)
    if not url or "/notebook/" not in str(url):
        await tab.sleep(2)
        href = await tab.evaluate("window.location.href")
        if href and "/notebook/" in str(href):
            url = href.split("?")[0] if "?" in href else href
    # Try reading from a notebook link on the page as fallback
    if not url or "/notebook/" not in str(url):
        link_url = await tab.evaluate(
            '(function(){ var a = document.querySelector(\'a[href*="/notebook/"]\'); '
            'return a ? a.href : null; })()'
        )
        if link_url and "/notebook/" in str(link_url):
            url = link_url.split("?")[0] if "?" in link_url else link_url

    # Only save/return URL if it's the real notebook page (never home page)
    if url and "/notebook/" in str(url):
        update_last_notebook({"url": url, "name": name or "Untitled"})
    return {"url": url if (url and "/notebook/" in str(url)) else None, "name": name or "Untitled"}


async def main():
    parser = argparse.ArgumentParser(description="Create a NotebookLM notebook")
    parser.add_argument("--port", "-p", type=int, help="Connect to existing browser")
    parser.add_argument("--name", help="Notebook name")
    parser.add_argument("--show-browser", action="store_true", help="Show browser window")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    result = await create_notebook(args.port, not args.show_browser, args.name)
    if args.json:
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            url = result.get("url")
            print(f"Created: {result.get('name')}")
            if url:
                print(url)
            else:
                print("(Notebook URL not captured — check browser for the actual link)")


if __name__ == "__main__":
    asyncio.run(main())
