from playwright.sync_api import Locator, Page, expect


class LayuiIframeDialog:
    """血液透析通用组件：封装 Layui iframe 弹窗及其所属遮罩。"""

    TITLE = ""

    def __init__(self, page: Page) -> None:
        """保存页面，并在弹窗打开后记录与其 times 对应的遮罩。"""
        self.page = page
        self._related_shade: Locator | None = None

    def _root(self) -> Locator:
        """返回标题与当前业务弹窗匹配的可见 Layui 弹层。"""
        return self.page.locator(".layui-layer:visible").filter(has_text=self.TITLE)

    def wait_for_open(self) -> "LayuiIframeDialog":
        """等待弹窗和 iframe 可见，并记录当前弹窗所属遮罩。"""
        dialog = self._root()
        expect(dialog).to_be_visible(timeout=10_000)
        times = dialog.get_attribute("times")
        self._related_shade = (
            self.page.locator(f"#layui-layer-shade{times}") if times else None
        )
        expect(dialog.locator("iframe")).to_be_visible(timeout=10_000)
        return self

    def _frame(self):
        """返回当前业务弹窗 iframe 的 FrameLocator。"""
        return self._root().locator("iframe").content_frame

    def _wait_for_closed(self) -> None:
        """只等待当前业务弹窗及其所属遮罩关闭。"""
        expect(self._root()).to_be_hidden(timeout=10_000)
        if self._related_shade is not None:
            expect(self._related_shade).to_be_hidden(timeout=10_000)

    def is_closed(self) -> bool:
        """确认当前业务弹窗及其所属遮罩均已关闭。"""
        self._wait_for_closed()
        return True
