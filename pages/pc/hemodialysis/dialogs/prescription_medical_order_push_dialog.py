from playwright.sync_api import expect

from .layui_iframe_dialog import LayuiIframeDialog


class PrescriptionMedicalOrderPushDialog(LayuiIframeDialog):
    """血液透析 > 透析处方触发：封装首次确认处方后的医嘱推送弹窗。"""

    TITLE = "医嘱推送"

    def confirm(self) -> None:
        """进入透析处方弹窗的 iframe，点击确定并等待所属遮罩关闭。"""
        confirm_button = self._frame().get_by_text("确定", exact=True).last
        expect(confirm_button).to_be_visible(timeout=10_000)
        confirm_button.click()
        self._wait_for_closed()
