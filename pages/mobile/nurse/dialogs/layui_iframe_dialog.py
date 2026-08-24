import re

from playwright.sync_api import FrameLocator, Locator, Page, expect


class LayuiIframeDialog:
    """移动端 Layui iframe 弹窗及其对应遮罩。"""

    TITLE = ""
    TITLE_ALIASES = ()

    def __init__(self, page: Page) -> None:
        self.page = page
        self._shade: Locator | None = None

    def root(self) -> Locator:
        titles = (self.TITLE, *self.TITLE_ALIASES)
        pattern = re.compile("|".join(re.escape(title) for title in titles if title))
        return self.page.locator(".layui-layer:visible").filter(has_text=pattern).first

    def wait_for_open(self) -> "LayuiIframeDialog":
        dialog = self.root()
        expect(dialog).to_be_visible(timeout=10_000)
        times = dialog.get_attribute("times")
        if times:
            self._shade = self.page.locator(f"#layui-layer-shade{times}")
        return self

    def frame(self) -> FrameLocator:
        return self.root().locator("iframe").content_frame

    def fill_fields(self, values: dict[str, str]) -> "LayuiIframeDialog":
        frame = self.frame()
        for name, value in values.items():
            field = frame.locator(f'[name="{name}"]:visible, #{name}:visible').first
            expect(field).to_be_visible()
            if field.evaluate("el => el.tagName.toLowerCase()") == "select":
                field.select_option(label=value)
            else:
                field.fill(value)
        return self

    def confirm(self) -> "LayuiIframeDialog":
        self.frame().get_by_role("button", name="确认", exact=True).click()
        return self

    def cancel(self) -> "LayuiIframeDialog":
        self.frame().get_by_role("button", name="取消", exact=True).click()
        return self

    def is_closed(self) -> bool:
        expect(self.root()).to_be_hidden(timeout=10_000)
        if self._shade is not None:
            expect(self._shade).to_be_hidden(timeout=10_000)
        return True
