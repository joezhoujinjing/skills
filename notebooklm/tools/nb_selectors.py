from __future__ import annotations

NOTEBOOKLM_HOME = "https://notebooklm.google.com/"

QUERY_INPUT_SELECTORS = [
    "textarea.query-box-input",
    'textarea[aria-label="Input for queries"]',
    'textarea[aria-label="Feld für Anfragen"]',
    'div[contenteditable="true"]',
]

RESPONSE_SELECTORS = [
    ".to-user-container .message-text-content",
    "[data-message-author='bot']",
    "[data-message-author='assistant']",
]

SOURCES_TAB_SELECTORS = [
    'button:has-text("Sources")',
    '[role="tab"]:has-text("Sources")',
    'div:has-text("Sources"):not(:has(*))',
]

HOME_TAB_SELECTORS = [
    'button:has-text("My notebooks")',
    'button:has-text("All")',
    '[role="tab"]:has-text("My notebooks")',
    '[role="tab"]:has-text("All")',
]

NOTEBOOK_CARD_SELECTORS = [
    "mat-card.project-button-card",
    ".project-button-card",
    "project-button mat-card",
    "project-button",
]

ADD_SOURCE_BUTTON_SELECTORS = [
    'button[aria-label="Add source"]',
    'button[aria-label="Add sources"]',
    'button:has-text("Add source")',
    'button:has-text("Add")',
]

WEBSITE_OPTION_SELECTORS = [
    'button:has-text("Websites")',
    'button:has-text("Website")',
    '[data-source-type="website"]',
    '[data-source-type="link"]',
    'div:has-text("Websites")',
    'li:has-text("Websites")',
]

YOUTUBE_OPTION_SELECTORS = [
    'button:has-text("YouTube")',
    '[data-source-type="youtube"]',
    'div[role="option"]:has-text("YouTube")',
    'li:has-text("YouTube")',
]

URL_INPUT_SELECTORS = [
    'textarea[placeholder*="Paste"]',
    'textarea[placeholder*="link"]',
    'input[type="url"]',
    'input[placeholder*="URL"]',
    'input[placeholder*="link"]',
    'input[placeholder*="http"]',
    'textarea:visible',
]

SUBMIT_BUTTON_SELECTORS = [
    'button:has-text("Insert")',
    'button:has-text("Add")',
    'button:has-text("Submit")',
    'button[type="submit"]',
]

NEW_NOTEBOOK_SELECTORS = [
    'button:has-text("New notebook")',
    'button:has-text("Create new notebook")',
    'button:has-text("Create new")',
    'button:has-text("Create notebook")',
    'button[aria-label*="Create new notebook"]',
    'button[aria-label*="Create notebook"]',
    'a:has-text("New notebook")',
]

NOTEBOOK_LINK_SELECTOR = 'a[href*="/notebook/"]'
