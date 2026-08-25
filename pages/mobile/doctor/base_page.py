import re
from collections.abc import Iterable

from playwright.sync_api import Locator, Page, expect

from utils.logger import logger


class BasePage:
    """移动端医生端页面对象共用的基础操作。"""

    def __init__(self, page: Page) -> None:
        self.page = page

    def navigate(self, url: str) -> "BasePage":
        logger.info("Navigate to mobile doctor URL {}", url)
        self.page.goto(url, wait_until="domcontentloaded")
        return self

    def locator(self, selector: str) -> Locator:
        return self.page.locator(selector)

    def wait_for_paths(self, paths: Iterable[str]) -> "BasePage":
        pattern = re.compile(
            "(?:"
            + "|".join(re.escape(path.rstrip("/")) for path in paths)
            + r")(?:\?.*)?(?:#.*)?$"
        )
        self.page.wait_for_url(pattern, wait_until="domcontentloaded")
        return self

    def expect_visible(self, locator: Locator) -> None:
        expect(locator).to_be_visible()
