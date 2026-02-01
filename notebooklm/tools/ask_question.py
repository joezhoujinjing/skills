#!/usr/bin/env python3
"""Ask a question in a NotebookLM notebook and return the response."""

import argparse
import asyncio
import json

from _utils import (
    NOTEBOOKLM_HOME,
    connect_tab,
    goto_url,
    wait_for_selector,
    fill_first,
    click_first,
    get_last_notebook,
    update_last_notebook,
    normalize_sources_arg,
    print_json,
)
import nb_selectors as nb_selectors

SEND_BUTTON_SELECTORS = [
    'button[aria-label*="Send"]',
    'button[aria-label*="Submit"]',
    'button[aria-label*="Ask"]',
    'button:has-text("Send")',
    'button:has-text("Ask")',
    'button[type="submit"]',
]


def normalize_url(notebook_id: str | None, notebook_url: str | None) -> str | None:
    if notebook_url:
        return notebook_url
    if notebook_id:
        return f"https://notebooklm.google.com/notebook/{notebook_id}"
    return None


async def open_by_name(tab, name: str) -> bool:
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
    return bool(await tab.evaluate(script))


async def exclude_sources(tab, exclude_names: list[str]) -> None:
    if not exclude_names:
        return

    await click_first(tab, nb_selectors.SOURCES_TAB_SELECTORS)
    await tab.sleep(1)

    for name in exclude_names:
        script = f"""
            (function() {{
                var target = {json.dumps(name.lower())};
                var elements = Array.from(document.querySelectorAll('*'));
                for (var i = 0; i < elements.length; i++) {{
                    var el = elements[i];
                    var text = (el.textContent || '').trim().toLowerCase();
                    if (!text || !text.includes(target)) continue;
                    var container = el.closest('[data-source-id]') || el.closest('li') || el.closest('div');
                    if (!container) continue;
                    var toggle = container.querySelector('button[aria-pressed], button[aria-label*="Exclude"], button[aria-label*="Include"], input[type="checkbox"]');
                    if (toggle) {{
                        toggle.click();
                        return true;
                    }}
                }}
                return false;
            }})()
        """
        await tab.evaluate(script)
        await tab.sleep(0.5)


async def ask_question(port: int | None, headless: bool, question: str, name: str | None, notebook_id: str | None, notebook_url: str | None, exclude_sources_arg: str | None) -> dict:
    browser, tab, port, err = await connect_tab(port, NOTEBOOKLM_HOME, headless=headless)
    if err:
        return {"error": err}

    target_url = normalize_url(notebook_id, notebook_url)
    if not target_url and name is None:
        last = get_last_notebook()
        if last:
            target_url = last.get("url")

    if not target_url and not name:
        return {"error": "Provide --notebook-name, --notebook-id, or --notebook-url (or use a last notebook)"}

    if target_url:
        await goto_url(tab, target_url)
    else:
        await goto_url(tab, NOTEBOOKLM_HOME)
        await tab.sleep(2)
        opened = await open_by_name(tab, name)
        if not opened:
            return {"error": f"Notebook not found: {name}"}

    await tab.sleep(3)

    exclude_names = normalize_sources_arg(exclude_sources_arg)
    if exclude_names:
        await exclude_sources(tab, exclude_names)

    sel = await wait_for_selector(tab, nb_selectors.QUERY_INPUT_SELECTORS, timeout=20)
    if not sel:
        return {"error": "Could not find query input"}

    filled = await fill_first(tab, nb_selectors.QUERY_INPUT_SELECTORS, question)
    if not filled:
        return {"error": "Failed to enter question"}

    await tab.sleep(0.5)
    clicked = await click_first(tab, SEND_BUTTON_SELECTORS)
    if not clicked:
        await tab.evaluate(
            """
            (function() {
                var el = document.querySelector('textarea') || document.querySelector('[contenteditable="true"]');
                if (!el) return false;
                var evt = new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true });
                el.dispatchEvent(evt);
                return true;
            })()
            """
        )

    await tab.sleep(2)
    for _ in range(120):
        done = await tab.evaluate(
            """
            (function() {
                var stopBtn = document.querySelector('button[aria-label*="Stop"]');
                if (stopBtn) return false;
                return true;
            })()
            """
        )
        if done:
            break
        await tab.sleep(1)

    response = await tab.evaluate(
        """
        (function() {
            var selectors = [
                '.to-user-container .message-text-content',
                '[data-message-author="bot"]',
                '[data-message-author="assistant"]',
                '.response',
                'main'
            ];
            for (var i = 0; i < selectors.length; i++) {
                var sel = selectors[i];
                var nodes = document.querySelectorAll(sel);
                if (nodes && nodes.length) {
                    var last = nodes[nodes.length - 1];
                    var text = (last.textContent || '').trim();
                    if (text) return text;
                }
            }
            return null;
        })()
        """
    )

    if target_url:
        update_last_notebook({"url": target_url, "name": name or notebook_id or ""})

    return {"response": response}


async def main():
    parser = argparse.ArgumentParser(description="Ask a question in NotebookLM")
    parser.add_argument("--question", required=True, help="Question to ask")
    parser.add_argument("--notebook-name", dest="name", help="Notebook name")
    parser.add_argument("--notebook-id", dest="notebook_id", help="Notebook ID")
    parser.add_argument("--notebook-url", dest="notebook_url", help="Notebook URL")
    parser.add_argument("--exclude-sources", help="Comma-separated sources to exclude")
    parser.add_argument("--port", "-p", type=int, help="Connect to existing browser")
    parser.add_argument("--show-browser", action="store_true", help="Show browser window")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    result = await ask_question(
        args.port,
        not args.show_browser,
        args.question,
        args.name,
        args.notebook_id,
        args.notebook_url,
        args.exclude_sources,
    )

    if args.json:
        print_json(result)
    else:
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(result.get("response") or "(no response)")


if __name__ == "__main__":
    asyncio.run(main())
