from playwright.sync_api import expect

from ...dialogs.layui_iframe_dialog import LayuiIframeDialog


class MedicalOrderPushDialog(LayuiIframeDialog):
    """透析处方确认后可能出现的医嘱推送弹窗。"""

    TITLE = "医嘱推送"

    def confirm(self) -> "MedicalOrderPushDialog":
        button = self.frame().get_by_role("button", name="确定", exact=True)
        if not button.count():
            button = self.frame().get_by_role("button", name="确认", exact=True)
        expect(button.first).to_be_visible()
        button.first.click()
        return self

    def cancel(self) -> "MedicalOrderPushDialog":
        button = self.frame().get_by_role("button", name="取消", exact=True)
        expect(button).to_be_visible()
        button.click()
        return self
