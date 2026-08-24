import re
from collections.abc import Iterable

from playwright.sync_api import Locator, Page, expect

from utils.logger import logger


class BasePage:
    """移动端护士端页面对象共用的基础操作。"""

    def __init__(self, page: Page) -> None:
        self.page = page

    def navigate(self, url: str) -> "BasePage":
        logger.info("Navigate to mobile nurse URL {}", url)
        self.page.goto(url, wait_until="domcontentloaded")
        return self

    def locator(self, selector: str) -> Locator:
        return self.page.locator(selector)

    def visible_text(self, text: str, exact: bool = True) -> Locator:
        return self.page.get_by_text(text, exact=exact).filter(visible=True).first

    def first_visible(self, locators: Iterable[Locator]) -> Locator:
        for locator in locators:
            if locator.count() and locator.first.is_visible():
                return locator.first
        raise AssertionError("未找到可见的目标元素")

    def wait_for_paths(self, paths: Iterable[str]) -> "BasePage":
        pattern = re.compile(
            "(?:" + "|".join(re.escape(path.rstrip("/")) for path in paths) + ")"
            + r"(?:\?.*)?(?:#.*)?$"
        )
        self.page.wait_for_url(pattern, wait_until="domcontentloaded")
        return self

    def fill(self, selector: str, value: str) -> None:
        self.locator(selector).fill(value)

    def expect_visible(self, locator: Locator) -> None:
        expect(locator).to_be_visible()
