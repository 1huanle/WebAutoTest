from playwright.sync_api import Locator, Page, expect

from utils.logger import logger


class BasePage:
    """移动端登录模块页面对象共用的基础操作。"""

    def __init__(self, page: Page) -> None:
        self.page = page

    def navigate(self, url: str) -> "BasePage":
        """打开页面并等待 DOM 加载完成。"""
        logger.info("Navigate to mobile login URL {}", url)
        self.page.goto(url, wait_until="domcontentloaded")
        return self

    def locator(self, selector: str) -> Locator:
        """根据 CSS 选择器返回元素定位器。"""
        return self.page.locator(selector)

    def fill(self, selector: str, value: str) -> None:
        """向输入控件填写文本。"""
        self.locator(selector).fill(value)

    def get_title(self) -> str:
        """返回当前页面标题。"""
        return self.page.title()

    def expect_visible(self, selector: str) -> None:
        """断言指定元素可见。"""
        expect(self.locator(selector)).to_be_visible()
