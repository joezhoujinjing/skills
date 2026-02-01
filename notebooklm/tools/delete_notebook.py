#!/usr/bin/env python3
"""Delete a NotebookLM notebook (requires --confirm)."""

import argparse
import asyncio
import json

from _utils import (
    NOTEBOOKLM_HOME,
    connect_tab,
    goto_url,
)


def normalize_url(notebook_id: str | None, notebook_url: str | None) -> str | None:
    if notebook_url:
        return notebook_url
    if notebook_id:
        return f"https://notebooklm.google.com/notebook/{notebook_id}"
    return None


async def open_menu_for_card(tab, name: str) -> bool:
    target = name.lower().strip()
    target_compact = ''.join(ch for ch in target if ch.isalnum() or ch.isspace()).strip()

    script = f"""
        (function() {{
            var target = {json.dumps(target)};
            var targetCompact = {json.dumps(target_compact)};
            var cards = Array.from(document.querySelectorAll('mat-card.project-button-card, .project-button-card, project-button mat-card, project-button'));
            for (var i = 0; i < cards.length; i++) {{
                var card = cards[i];
                var text = (card.textContent || '').toLowerCase();
                text = text.replace(/more_vert/g, ' ').replace(/\\s+/g, ' ').trim();
                var compact = text.replace(/[^a-z0-9\\s]/g, '').replace(/\\s+/g, ' ').trim();
                if (!(text.includes(target) || (targetCompact && compact.includes(targetCompact)))) continue;
                var menuBtn = card.querySelector('button[aria-label="Project Actions Menu"], button.project-button-more, button[aria-label*="Project Actions"], button[aria-label*="Actions Menu"], button[aria-label*="More"]');
                if (menuBtn) {{
                    menuBtn.scrollIntoView({{ block: 'center', inline: 'center' }});
                    menuBtn.click();
                    return true;
                }}
            }}
            return false;
        }})()
    """
    return bool(await tab.evaluate(script))


async def click_menu_item(tab, label: str) -> bool:
    script = f"""
        (function() {{
            var target = {json.dumps(label.lower())};
            var items = Array.from(document.querySelectorAll('.mat-mdc-menu-item, [role=menuitem], button'));
            for (var i = 0; i < items.length; i++) {{
                var el = items[i];
                var text = (el.textContent || '').replace(/\\s+/g,' ').trim().toLowerCase();
                if (!text) continue;
                if (text.includes(target)) {{
                    el.click();
                    return true;
                }}
            }}
            return false;
        }})()
    """
    return bool(await tab.evaluate(script))


async def click_dialog_button(tab, label: str) -> bool:
    script = f"""
        (function() {{
            var target = {json.dumps(label.lower())};
            var dialog = document.querySelector('mat-dialog-container, [role=dialog]');
            if (!dialog) return false;
            var buttons = Array.from(dialog.querySelectorAll('button'));
            for (var i = 0; i < buttons.length; i++) {{
                var btn = buttons[i];
                var text = (btn.textContent || '').replace(/\\s+/g,' ').trim().toLowerCase();
                if (text.includes(target)) {{
                    btn.click();
                    return true;
                }}
            }}
            return false;
        }})()
    """
    return bool(await tab.evaluate(script))


async def delete_notebook(port: int | None, headless: bool, name: str | None, notebook_id: str | None, notebook_url: str | None, confirm: bool) -> dict:
    browser, tab, port, err = await connect_tab(port, NOTEBOOKLM_HOME, headless=headless)
    if err:
        return {"error": err}

    # Extract notebook_id from URL if provided
    if notebook_url and not notebook_id:
        import re
        match = re.search(r"/notebook/([a-f0-9-]+)", notebook_url)
        if match:
            notebook_id = match.group(1)

    # Always go to home page - delete is only available from the card menu there
    await goto_url(tab, NOTEBOOKLM_HOME)
    await tab.sleep(3)

    # Click "My notebooks" tab
    await tab.evaluate(
        """
        (function() {
            var btns = Array.from(document.querySelectorAll('button,[role=tab]'));
            for (var i = 0; i < btns.length; i++) {
                var text = (btns[i].textContent || '').toLowerCase();
                if (text.includes('my notebooks')) { btns[i].click(); return true; }
            }
            for (var i = 0; i < btns.length; i++) {
                var text = (btns[i].textContent || '').toLowerCase();
                if (text.includes('all')) { btns[i].click(); return true; }
            }
            return false;
        })()
        """
    )
    await tab.sleep(2)

    # Find and click the three-dot menu for the target notebook
    if notebook_id:
        # Find card by notebook ID and click its menu
        menu_clicked = await tab.evaluate(
            f"""
            (function() {{
                var targetId = {json.dumps(notebook_id)};
                var cards = document.querySelectorAll("project-button");
                for (var i = 0; i < cards.length; i++) {{
                    var card = cards[i];
                    var btn = card.querySelector('button[aria-labelledby*="project-"]');
                    if (!btn) continue;
                    var labelledBy = btn.getAttribute("aria-labelledby") || "";
                    if (labelledBy.includes("project-" + targetId)) {{
                        var menuBtn = card.querySelector('button[aria-label="Project Actions Menu"]');
                        if (menuBtn) {{ menuBtn.click(); return true; }}
                    }}
                }}
                return false;
            }})()
            """
        )
    elif name:
        menu_clicked = await open_menu_for_card(tab, name)
    else:
        return {"error": "Provide --name, --id, or --url"}

    if not menu_clicked:
        return {"error": "Could not find notebook or open its menu"}

    await tab.sleep(1)
    delete_clicked = await click_menu_item(tab, "delete")
    if not delete_clicked:
        return {"error": "Could not find delete action"}

    if not confirm:
        return {"status": "preview", "message": "Add --confirm to delete"}

    await tab.sleep(1)
    confirm_clicked = await click_dialog_button(tab, "delete")
    if not confirm_clicked:
        return {"error": "Could not confirm deletion"}

    await tab.sleep(2)
    deleted_url = notebook_url or (f"https://notebooklm.google.com/notebook/{notebook_id}" if notebook_id else None)
    return {"status": "deleted", "url": deleted_url or "(by name)"}


async def main():
    parser = argparse.ArgumentParser(description="Delete a NotebookLM notebook")
    parser.add_argument("--port", "-p", type=int, help="Connect to existing browser")
    parser.add_argument("--name", help="Notebook name")
    parser.add_argument("--id", dest="notebook_id", help="Notebook ID")
    parser.add_argument("--url", dest="notebook_url", help="Notebook URL")
    parser.add_argument("--confirm", action="store_true", help="Confirm delete")
    parser.add_argument("--show-browser", action="store_true", help="Show browser window")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    result = await delete_notebook(args.port, not args.show_browser, args.name, args.notebook_id, args.notebook_url, args.confirm)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if "error" in result:
            print(f"Error: {result['error']}")
        elif result.get("status") == "preview":
            print(result["message"])
        else:
            print("Deleted notebook")


if __name__ == "__main__":
    asyncio.run(main())
