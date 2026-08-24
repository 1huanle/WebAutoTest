from playwright.sync_api import expect

from ...dialogs.layui_iframe_dialog import LayuiIframeDialog


class PrescriptionSyncDialog(LayuiIframeDialog):
    """透析处方中的“同步到透析方案”弹窗。"""

    TITLE = "同步到透析方案"

    def confirm(self) -> "PrescriptionSyncDialog":
        button = self.frame().get_by_role("button", name="确定", exact=True)
        if not button.count():
            button = self.frame().get_by_role("button", name="确认", exact=True)
        expect(button.first).to_be_visible()
        button.first.click()
        return self

    def cancel(self) -> "PrescriptionSyncDialog":
        button = self.frame().get_by_role("button", name="取消", exact=True)
        expect(button).to_be_visible()
        button.click()
        return self
