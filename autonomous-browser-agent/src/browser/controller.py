import logging
import re

from playwright.async_api import Browser, Page, async_playwright

from src.browser.models import BrowserAction, BrowserSnapshot
from src.config import settings

logger = logging.getLogger(__name__)


class BrowserController:
    def __init__(self, page: Page) -> None:
        self.page = page

    @classmethod
    async def create(cls) -> "BrowserController":
        p = await async_playwright().start()
        browser: Browser = await p.chromium.launch(
            headless=settings.browser_headless,
            slow_mo=settings.browser_slow_mo,
        )
        context = await browser.new_context(
            viewport={
                "width": settings.browser_viewport_width,
                "height": settings.browser_viewport_height,
            },
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/130.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()
        return cls(page)

    async def execute(self, action: BrowserAction) -> dict:
        handler = getattr(self, f"_action_{action.action}", None)
        if handler is None:
            raise ValueError(f"Unknown action: {action.action}")
        return await handler(**action.parameters)

    async def _action_navigate(self, url: str, **kwargs) -> dict:
        logger.info("Navigate: %s", url)
        await self.page.goto(
            url, timeout=settings.browser_nav_timeout, wait_until="domcontentloaded"
        )
        await self.page.wait_for_load_state("networkidle", timeout=10000)
        return {"snapshot": await self._snapshot()}

    async def _action_click(self, selector: str, **kwargs) -> dict:
        logger.info("Click: %s", selector)
        el = self.page.locator(selector)
        await el.wait_for(state="visible", timeout=8000)
        await el.click()
        await self.page.wait_for_timeout(300)
        return {"snapshot": await self._snapshot()}

    async def _action_fill(self, selector: str, value: str, **kwargs) -> dict:
        logger.info("Fill: %s = %s", selector, value)
        el = self.page.locator(selector)
        await el.wait_for(state="visible", timeout=8000)
        await el.fill(value)
        return {"snapshot": await self._snapshot()}

    async def _action_select(self, selector: str, value: str, **kwargs) -> dict:
        logger.info("Select: %s = %s", selector, value)
        el = self.page.locator(selector)
        await el.wait_for(state="visible", timeout=8000)
        await el.select_option(value)
        return {"snapshot": await self._snapshot()}

    async def _action_screenshot(self, **kwargs) -> dict:
        path = f"/tmp/screenshots/{hash(self.page.url)}.png"
        await self.page.screenshot(path=path, full_page=True)
        return {"snapshot": await self._snapshot(), "screenshot_path": path}

    async def _action_extract(self, instruction: str = "", **kwargs) -> dict:
        text = await self.page.inner_text("body")
        extracted = {"raw_text_preview": text[:2000]}
        return {"snapshot": await self._snapshot(), "extracted_data": extracted}

    async def _action_scroll(self, direction: str = "down", **kwargs) -> dict:
        delta = 600 if direction == "down" else -600
        await self.page.evaluate(f"window.scrollBy(0, {delta})")
        await self.page.wait_for_timeout(200)
        return {"snapshot": await self._snapshot()}

    async def _action_wait(self, ms: int = 1000, **kwargs) -> dict:
        await self.page.wait_for_timeout(ms)
        return {"snapshot": await self._snapshot()}

    async def _action_done(self, result: str = "", **kwargs) -> dict:
        return {
            "snapshot": await self._snapshot(),
            "extracted_data": {"final_result": result or "done"},
        }

    async def _snapshot(self) -> BrowserSnapshot:
        url = self.page.url
        title = await self.page.title()
        dom = await self.page.inner_text("body")
        clean = re.sub(r"\s+", " ", dom)[:3000]

        form_fields = await self.page.evaluate("""() => {
            const fields = [];
            document.querySelectorAll('input, textarea, select').forEach(el => {
                if (el.offsetParent !== null) {
                    const label = el.closest('label')?.innerText?.trim()
                        || document.querySelector(`label[for="${el.id}"]`)?.innerText?.trim()
                        || el.placeholder || '';
                    fields.push({tag: el.tagName, type: el.type, name: el.name, id: el.id,
                        placeholder: el.placeholder, label, value: el.value});
                }
            });
            return fields;
        }""") or []

        links = await self.page.evaluate("""() =>
            Array.from(document.querySelectorAll('a[href]')).slice(0, 50).map(a => a.href)
        """) or []

        interactable = await self.page.evaluate("""() =>
            Array.from(document.querySelectorAll('button, a, input, select, textarea'))
                .filter(el => el.offsetParent !== null)
                .slice(0, 50)
                .map(el => {
                    const tag = el.tagName;
                    const raw = el.innerText || el.value || el.placeholder || '';
                    const txt = raw.trim().slice(0, 40);
                    const sel = el.id ? `#${el.id}` : (el.name ? `[name="${el.name}"]` : tag);
                    return `${tag} "${txt}"  → ${sel}`;
                })
        """) or []

        return BrowserSnapshot(
            url=url,
            title=title,
            dom_summary=clean,
            form_fields=form_fields,
            links=links,
            interactable=interactable,
        )
