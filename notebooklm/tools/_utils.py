from __future__ import annotations

import inspect
import json
import os
import time
from pathlib import Path
from typing import Any, Iterable
import re

from ai_dev_browser.core import connect_browser, get_active_tab
from ai_dev_browser import tools as adb_tools

import nb_selectors as nb_selectors

NOTEBOOKLM_HOME = nb_selectors.NOTEBOOKLM_HOME

PROFILE_NAME = os.environ.get("NOTEBOOKLM_PROFILE", "Jarvis")
PROFILE_ROOT = Path(os.environ.get("NOTEBOOKLM_PROFILE_ROOT", "~/.ai-dev-browser/profiles")).expanduser()

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CONFIG_PATH = DATA_DIR / "config.json"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text())
        except Exception:
            return {}
    return {}


def get_browser_port() -> int | None:
    """Get stored browser port from config."""
    data = load_config()
    return data.get("browser_port")


def save_browser_port(port: int) -> None:
    """Save browser port to config."""
    data = load_config()
    data["browser_port"] = port
    save_config(data)


def save_config(data: dict) -> None:
    ensure_data_dir()
    CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def update_last_notebook(notebook: dict) -> None:
    data = load_config()
    data["last_notebook"] = notebook
    save_config(data)


def get_last_notebook() -> dict | None:
    data = load_config()
    return data.get("last_notebook")


def get_profile_dir() -> Path:
    return PROFILE_ROOT / PROFILE_NAME


def ensure_profile_dir() -> Path:
    profile_dir = get_profile_dir()
    profile_dir.mkdir(parents=True, exist_ok=True)
    return profile_dir


def _call_with_supported_kwargs(func, **kwargs):
    sig = inspect.signature(func)
    supported = {k: v for k, v in kwargs.items() if k in sig.parameters}
    return func(**supported)


def start_browser(url: str, headless: bool = False) -> dict:
    ensure_profile_dir()
    return _call_with_supported_kwargs(
        adb_tools.browser_start,
        url=url,
        headless=headless,
        user_data_dir=str(PROFILE_ROOT),
        profile=PROFILE_NAME,
        profile_dir=str(get_profile_dir()),
    )


def login_interactive(url: str) -> dict:
    ensure_profile_dir()
    if hasattr(adb_tools, "login_interactive"):
        return _call_with_supported_kwargs(
            adb_tools.login_interactive,
            url=url,
            headless=False,
            user_data_dir=str(PROFILE_ROOT),
            profile=PROFILE_NAME,
            profile_dir=str(get_profile_dir()),
        )
    return start_browser(url=url, headless=False)


async def try_connect_port(port: int):
    """Try to connect to browser on given port."""
    try:
        browser = await connect_browser(port=port)
        return browser
    except Exception:
        return None


async def find_existing_browser() -> int | None:
    """Find an existing browser on common debug ports."""
    # First check saved port
    saved_port = get_browser_port()
    if saved_port:
        browser = await try_connect_port(saved_port)
        if browser:
            return saved_port

    # Try common remote debugging ports
    common_ports = [9222, 9223, 9224, 9225, 9226, 9227, 9228, 9229, 9230]
    for port in common_ports:
        if port == saved_port:
            continue
        browser = await try_connect_port(port)
        if browser:
            save_browser_port(port)
            return port
    return None


async def connect_tab(port: int | None, url: str, headless: bool = False):
    if port is None:
        # Try to find existing browser first
        existing_port = await find_existing_browser()
        if existing_port:
            port = existing_port
        else:
            result = start_browser(url=url, headless=headless)
            if "error" in result:
                return None, None, None, result
            port = result.get("port")
            if port:
                save_browser_port(port)
    browser = await connect_browser(port=port)
    tab = await get_active_tab(browser)
    if url:
        await goto_url(tab, url)
    return browser, tab, port, None


async def wait_for_selector(tab, selectors: Iterable[str], timeout: float = 15.0, interval: float = 0.5) -> str | None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        for sel in selectors:
            match = re.search(r':has-text\\(\"([^\"]+)\"\\)', sel)
            if match:
                text = match.group(1).lower()
                base = sel.split(':has-text', 1)[0].strip() or '*'
                script = f"""
                    (function() {{
                        var nodes = Array.from(document.querySelectorAll({json.dumps(base)}));
                        for (var i = 0; i < nodes.length; i++) {{
                            var el = nodes[i];
                            var content = (el.textContent || el.getAttribute('aria-label') || '').trim().toLowerCase();
                            if (content.includes({json.dumps(text)})) return true;
                        }}
                        return false;
                    }})()
                """
                found = await tab.evaluate(script)
            else:
                script = f"!!document.querySelector({json.dumps(sel)})"
                found = await tab.evaluate(script)
            if found:
                return sel
        await tab.sleep(interval)
    return None


async def click_first(tab, selectors: Iterable[str]) -> str | None:
    for sel in selectors:
        match = re.search(r':has-text\\(\"([^\"]+)\"\\)', sel)
        if match:
            text = match.group(1).lower()
            base = sel.split(':has-text', 1)[0].strip() or '*'
            script = f"""
                (function() {{
                    var nodes = Array.from(document.querySelectorAll({json.dumps(base)}));
                    for (var i = 0; i < nodes.length; i++) {{
                        var el = nodes[i];
                        var content = (el.textContent || el.getAttribute('aria-label') || '').trim().toLowerCase();
                        if (!content.includes({json.dumps(text)})) continue;
                        el.scrollIntoView({{ block: 'center', inline: 'center' }});
                        el.click();
                        return true;
                    }}
                    return false;
                }})()
            """
            clicked = await tab.evaluate(script)
        else:
            script = f"""
                (function() {{
                    var el = document.querySelector({json.dumps(sel)});
                    if (!el) return false;
                    el.scrollIntoView({{ block: 'center', inline: 'center' }});
                    el.click();
                    return true;
                }})()
            """
            clicked = await tab.evaluate(script)
        if clicked:
            return sel
    return None


async def fill_first(tab, selectors: Iterable[str], value: str) -> str | None:
    for sel in selectors:
        script = f"""
            (function() {{
                var el = document.querySelector({json.dumps(sel)});
                if (!el) return false;
                el.focus();
                if (el.isContentEditable) {{
                    el.innerText = {json.dumps(value)};
                }} else {{
                    el.value = {json.dumps(value)};
                }}
                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                return true;
            }})()
        """
        filled = await tab.evaluate(script)
        if filled:
            return sel
    return None


async def goto_url(tab, url: str):
    script = f"window.location.href = {json.dumps(url)}"
    await tab.evaluate(script)


async def list_notebook_links(tab) -> list[dict]:
    items = await tab.evaluate(
        """
        (function() {
            var links = Array.from(document.querySelectorAll('a[href*="/notebook/"]'));
            var out = [];
            for (var i = 0; i < links.length; i++) {
                var link = links[i];
                var url = link.href;
                var name = (link.textContent || '').trim();
                if (!url) continue;
                out.push({ name: name, url: url });
            }
            return out;
        })()
        """
    )
    if not items:
        return []

    seen = set()
    results = []
    for item in items:
        url = item.get("url")
        if not url or url in seen:
            continue
        seen.add(url)
        name = (item.get("name") or "").strip()
        results.append({"name": name, "url": url})
    return results


async def find_notebook_by_name(tab, name: str) -> dict | None:
    name_l = name.lower()
    items = await list_notebook_links(tab)
    best = None
    for item in items:
        label = (item.get("name") or "").strip()
        if not label:
            continue
        if label.lower() == name_l:
            return item
        if name_l in label.lower():
            if best is None:
                best = item
    return best


async def wait_for_home(tab) -> None:
    await wait_for_selector(tab, [nb_selectors.NOTEBOOK_LINK_SELECTOR] + nb_selectors.NEW_NOTEBOOK_SELECTORS, timeout=20)


async def ensure_sources_tab(tab) -> bool:
    await click_first(tab, nb_selectors.SOURCES_TAB_SELECTORS)
    await tab.sleep(1.0)
    return True


async def list_sources_raw(tab) -> list[dict]:
    items = await tab.evaluate(
        """
        (function() {
            var candidates = Array.from(document.querySelectorAll('[data-source-id], [data-testid*="source"], a[href*="source"], li, div'));
            var out = [];
            for (var i = 0; i < candidates.length; i++) {
                var el = candidates[i];
                var text = (el.textContent || '').trim();
                if (!text) continue;
                if (text.length > 200) continue;
                if (text.toLowerCase().includes('source')) {
                    out.push({ name: text });
                }
            }
            return out;
        })()
        """
    )
    if not items:
        return []

    seen = set()
    results = []
    for item in items:
        name = (item.get("name") or "").strip()
        if not name:
            continue
        if name in seen:
            continue
        seen.add(name)
        results.append({"name": name})
    return results


def normalize_sources_arg(value: str | None) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def unwrap_cdp(value: Any) -> Any:
    if isinstance(value, dict) and "type" in value and "value" in value:
        vtype = value.get("type")
        raw = value.get("value")
        if vtype in {"string", "number", "boolean"}:
            return raw
        if vtype == "object" and isinstance(raw, list):
            obj = {}
            for entry in raw:
                if isinstance(entry, list) and len(entry) == 2:
                    key = unwrap_cdp(entry[0])
                    obj[str(key)] = unwrap_cdp(entry[1])
            return obj
        if vtype == "array" and isinstance(raw, list):
            return [unwrap_cdp(item) for item in raw]
        return raw
    if isinstance(value, list):
        return [unwrap_cdp(item) for item in value]
    if isinstance(value, dict):
        return {k: unwrap_cdp(v) for k, v in value.items()}
    return value
