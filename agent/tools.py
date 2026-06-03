import base64
import json
from playwright.sync_api import BrowserContext, Page


class BrowserTools:
    """
    Wraps Playwright with multi-tab support and self-healing click selectors.
    All tools return a plain string observation fed back into the agent loop.
    """

    def __init__(self, context: BrowserContext, openai_client):
        self.context = context
        self.client  = openai_client
        self.pages: list[Page] = [context.pages[0]]
        self.active: int = 0

    #active page helper

    @property
    def page(self) -> Page:
        return self.pages[self.active]

    #screenshot / dom

    def get_screenshot_b64(self) -> str:
        """Return current page screenshot as base64 PNG."""
        data = self.page.screenshot(type="png", full_page=False)
        return base64.standard_b64encode(data).decode("utf-8")

    def get_dom_snapshot(self) -> list[dict]:
        """Return up to 60 interactive elements from the current page."""
        return self.page.evaluate("""() => {
            const sel = 'a, button, input, select, textarea, [role="button"], [role="link"]';
            return Array.from(document.querySelectorAll(sel))
                .slice(0, 60)
                .map(el => ({
                    tag:   el.tagName.toLowerCase(),
                    text:  (el.innerText || el.value || '').slice(0, 80).trim(),
                    id:    el.id        || null,
                    name:  el.name      || null,
                    type:  el.type      || null,
                    href:  el.href      || null,
                    role:  el.getAttribute('role') || null,
                }));
        }""")

    #basic browser actions

    def navigate(self, url: str) -> str:
        self.page.goto(url, wait_until="domcontentloaded", timeout=20_000)
        return f"Navigated to {url} | title: '{self.page.title()}'"

    def click(self, selector: str) -> str:
        """Click with automatic self-healing on failure."""
        try:
            self.page.click(selector, timeout=5_000)
            self.page.wait_for_load_state("networkidle", timeout=8_000)
            return f"Clicked '{selector}'"
        except Exception as e:
            return self._heal_and_click(selector, str(e))

    def _heal_and_click(self, original_selector: str, error: str) -> str:
        """Ask GPT-4o mini to suggest a better selector when the original fails."""
        dom = self.get_dom_snapshot()
        heal_prompt = f"""The Playwright selector '{original_selector}' failed with:
{error}

Interactive elements currently on the page:
{json.dumps(dom, indent=2)}

The user was trying to click something matching: '{original_selector}'.
Return ONLY valid JSON with one key, no explanation:
{{"selector": "your_suggested_playwright_selector"}}"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=128,
            messages=[{"role": "user", "content": heal_prompt}],
        )
        try:
            healed = json.loads(response.choices[0].message.content.strip())
            new_sel = healed["selector"]
            self.page.click(new_sel, timeout=5_000)
            self.page.wait_for_load_state("networkidle", timeout=8_000)
            return f"[HEALED] '{original_selector}' → '{new_sel}' | click succeeded"
        except Exception as e2:
            return f"[HEAL FAILED] original='{original_selector}' | error={e2}"

    def type_text(self, selector: str, text: str) -> str:
        self.page.fill(selector, text)
        return f"Typed '{text}' into '{selector}'"

    def scroll(self, direction: str = "down") -> str:
        delta = 600 if direction == "down" else -600
        self.page.evaluate(f"window.scrollBy(0, {delta})")
        return f"Scrolled {direction}"

    def press_key(self, key: str) -> str:
        self.page.keyboard.press(key)
        return f"Pressed '{key}'"

    #multi tab actions

    def open_tab(self, url: str) -> str:
        new_page = self.context.new_page()
        new_page.goto(url, wait_until="domcontentloaded", timeout=20_000)
        self.pages.append(new_page)
        self.active = len(self.pages) - 1
        return f"Opened tab [{self.active}]: '{new_page.title()}' at {url}"

    def switch_tab(self, index: int) -> str:
        if 0 <= index < len(self.pages):
            self.active = index
            return f"Switched to tab [{index}]: {self.page.url}"
        return f"Tab [{index}] doesn't exist. Valid indices: 0–{len(self.pages)-1}"

    def close_tab(self, index: int) -> str:
        if len(self.pages) == 1:
            return "Cannot close the only open tab."
        if not (0 <= index < len(self.pages)):
            return f"Tab [{index}] doesn't exist."
        self.pages[index].close()
        self.pages.pop(index)
        self.active = min(self.active, len(self.pages) - 1)
        return f"Closed tab [{index}]. Active tab is now [{self.active}]."

    def list_tabs(self) -> str:
        tabs = [
            {
                "index":  i,
                "url":    p.url,
                "title":  p.title(),
                "active": i == self.active,
            }
            for i, p in enumerate(self.pages)
        ]
        return json.dumps(tabs, indent=2)
