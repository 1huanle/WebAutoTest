from playwright.sync_api import Locator, Page, expect


class PatientDetailDialog:
    """患者详情弹窗，只封装打开、状态校验和关闭。"""

    DIALOG_SELECTOR = ".hzdetailDialog:visible"
    TITLE = "患者详情"

    def __init__(self, page: Page) -> None:
        self.page = page

    def _dialog(self) -> Locator:
        return self.page.locator(self.DIALOG_SELECTOR).last

    def wait_for_open(self) -> "PatientDetailDialog":
        """等待患者详情弹窗打开并确认标题可见。"""
        dialog = self._dialog()
        expect(dialog).to_be_visible()
        expect(dialog.get_by_text(self.TITLE, exact=True).first).to_be_visible()
        return self

    def is_open(self) -> bool:
        """返回患者详情弹窗是否可见。"""
        dialog = self._dialog()
        return dialog.is_visible() and dialog.get_by_text(
            self.TITLE, exact=True
        ).first.is_visible()

    def close(self) -> "PatientDetailDialog":
        """关闭患者详情弹窗并等待其隐藏。"""
        dialog = self._dialog()
        dialog.locator("button.el-dialog__headerbtn").click()
        expect(dialog).to_be_hidden()
        return self
