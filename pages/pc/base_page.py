from playwright.sync_api import Locator, Page, expect

from utils.logger import logger


class BasePage:
    """封装所有页面对象共用的 Playwright 基础操作。"""

    def __init__(self, page: Page) -> None:
        """保存当前测试上下文中的浏览器页面对象。"""
        self.page = page

    def navigate(self, url: str) -> "BasePage":
        """导航到指定地址，并等待 DOM 内容加载完成。"""
        logger.info("Navigate to {}", url)
        self.page.goto(url, wait_until="domcontentloaded")
        return self

    def get_title(self) -> str:
        """返回当前页面标题。"""
        return self.page.title()

    def locator(self, selector: str) -> Locator:
        """根据 CSS 选择器获取页面元素定位器。"""
        return self.page.locator(selector)

    def fill(self, selector: str, value: str) -> None:
        """向指定输入控件填写文本。"""
        self.page.locator(selector).fill(value)

    def press_enter(self, selector: str) -> None:
        """在指定控件上触发 Enter 按键。"""
        self.page.locator(selector).press("Enter")

    def screenshot(self, name: str) -> bytes:
        """截取当前完整页面，并保存到指定路径。"""
        return self.page.screenshot(path=name, full_page=True)

    def expect_visible(self, selector: str) -> None:
        """断言指定控件在页面中可见。"""
        expect(self.page.locator(selector)).to_be_visible()
