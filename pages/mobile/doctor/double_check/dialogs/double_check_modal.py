import re

from playwright.sync_api import Locator, Page, expect


class DoubleCheckSelectModal:
    """医生端双人核对的核对人员选择弹窗。"""

    SELECTOR = "#select_Modal:visible"

    def __init__(self, page: Page) -> None:
        self.page = page

    def root(self) -> Locator:
        return self.page.locator(self.SELECTOR).first

    def wait_for_open(self) -> "DoubleCheckSelectModal":
        expect(self.root()).to_be_visible()
        return self

    def is_open(self) -> bool:
        return self.root().count() > 0 and self.root().is_visible()

    def get_title(self) -> str:
        root = self.root()
        expect(root).to_be_visible()
        for selector in (".modal-title", ".modal-header", "h4", "h3"):
            title = root.locator(selector).first
            if title.count() and title.is_visible():
                return " ".join(title.inner_text().split())
        return ""

    def get_options(self) -> list[str]:
        root = self.root()
        expect(root).to_be_visible()
        selectors = (
            "option:visible",
            "li:visible",
            ".modal-body a:visible",
            ".modal-body label:visible",
            ".modal-body td:visible",
        )
        for selector in selectors:
            values = [" ".join(value.split()) for value in root.locator(selector).all_inner_texts()]
            values = [value for value in values if value]
            if values:
                return values
        return []

    def select_value(self, value: str) -> "DoubleCheckSelectModal":
        root = self.wait_for_open().root()
        option = root.get_by_text(str(value), exact=True).filter(visible=True).last
        expect(option).to_be_visible()
        option.click()
        return self

    def _action(self, pattern: str) -> Locator:
        root = self.wait_for_open().root()
        action = root.get_by_role("button", name=re.compile(pattern)).filter(visible=True).last
        if not action.count():
            action = root.locator("a, input[type='button'], input[type='submit']").filter(
                has_text=re.compile(pattern)
            ).filter(visible=True).last
        expect(action).to_be_visible()
        return action

    def save(self) -> "DoubleCheckSelectModal":
        self._action(r"^(?:确定|保存|选择)$").click()
        return self

    def cancel(self) -> "DoubleCheckSelectModal":
        self._action(r"^(?:取消|返回)$").click()
        return self

    def close(self) -> "DoubleCheckSelectModal":
        root = self.wait_for_open().root()
        close = root.locator("[data-dismiss='modal'], .close, .modal-close").filter(visible=True).first
        expect(close).to_be_visible()
        close.click()
        return self


class SameNurseWarningModal:
    """双人核对确认时可能出现的同人核对提示。"""

    SELECTOR = ".layui-layer:visible"
    MESSAGE = "核对人员和治疗护士确认是同一个人吗"

    def __init__(self, page: Page) -> None:
        self.page = page

    def root(self) -> Locator:
        return self.page.locator(self.SELECTOR).filter(has_text=self.MESSAGE).first

    def is_open(self) -> bool:
        return self.root().count() > 0 and self.root().is_visible()

    def get_message(self) -> str:
        root = self.root()
        expect(root).to_be_visible()
        return " ".join(root.inner_text().split())

    def _button(self, name: str) -> Locator:
        root = self.root()
        button = root.get_by_text(name, exact=True).filter(visible=True).last
        expect(button).to_be_visible()
        return button

    def accept(self) -> "SameNurseWarningModal":
        self._button("确定").click()
        return self

    def cancel(self) -> "SameNurseWarningModal":
        self._button("取消").click()
        return self

    def close(self) -> "SameNurseWarningModal":
        root = self.root()
        expect(root).to_be_visible()
        close = root.locator(".layui-layer-close, .close").filter(visible=True).first
        expect(close).to_be_visible()
        close.click()
        return self
