from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, expect

from .layui_iframe_dialog import LayuiIframeDialog


class TemporaryOrderExecutionDialog(LayuiIframeDialog):
    """血液透析 > 临时医嘱 > 执行医嘱：封装逐条执行弹窗。"""

    TITLE = "执行医嘱"
    SAME_NURSE_WARNING = "执行人员和核对人员确认是同一个人吗"
    FIELDS = {
        "execution_time": "tx_lsyz_zxsj",
        "execution_nurse": "tx_lsyz_qm_nurse",
        "verification_nurse": "tx_lsyz_hd_nurse",
        "note": "tx_yznote",
    }

    def _field(self, name: str):
        """返回执行医嘱 iframe 内指定 name 的可见字段。"""
        return self._frame().locator(f'[name="{name}"]:visible')

    def fill_execution(
        self, data: dict[str, str]
    ) -> "TemporaryOrderExecutionDialog":
        """校验执行人员和核对人员，并填写可选备注。"""
        expect(self._field(self.FIELDS["execution_time"])).not_to_have_value("")
        expect(self._field(self.FIELDS["execution_nurse"])).to_have_value(
            data["execution_nurse"]
        )
        expect(self._field(self.FIELDS["verification_nurse"])).to_have_value(
            data["verification_nurse"]
        )
        self._field(self.FIELDS["note"]).fill(data.get("note", ""))
        return self

    def execute(self) -> "TemporaryOrderExecutionDialog":
        """点击执行，确认同一人员提示并等待医嘱弹窗关闭。"""
        execution_nurse = self._field(
            self.FIELDS["execution_nurse"]
        ).input_value().strip()
        verification_nurse = self._field(
            self.FIELDS["verification_nurse"]
        ).input_value().strip()
        needs_warning = bool(execution_nurse) and (
            execution_nurse == verification_nurse
        )
        self._frame().get_by_role("button", name="执行", exact=True).click()
        if needs_warning:
            self._confirm_same_nurse_warning_if_visible()
        self._wait_for_closed()
        return self

    def _confirm_same_nurse_warning_if_visible(self) -> None:
        """确认临时医嘱执行人员和核对人员相同时触发的提示。"""
        warning = self._frame().locator(".layui-layer:visible").filter(
            has_text=self.SAME_NURSE_WARNING
        )
        try:
            warning.wait_for(state="visible", timeout=3_000)
        except PlaywrightTimeoutError:
            return

        confirm_button = warning.get_by_text("确定", exact=True).filter(
            visible=True
        ).last
        expect(confirm_button).to_be_visible()
        confirm_button.click()
