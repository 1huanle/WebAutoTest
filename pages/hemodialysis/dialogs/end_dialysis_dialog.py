from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, expect

from .layui_iframe_dialog import LayuiIframeDialog


class EndDialysisDialog(LayuiIframeDialog):
    """血液透析 > 结束透析：封装结束透析 iframe 弹窗。"""

    TITLE = "结束透析"
    FIELDS = {
        "off_machine_nurse": "tx_xj_nurse",
        "blood_return_flow": "tx_hx",
    }
    PASSWORD_WARNING = "登录密码"

    def _field(self, name: str):
        """返回结束透析弹窗内指定 name 的可见控件。"""
        return self._frame().locator(f'[name="{name}"]:visible')

    def fill_end_dialysis(self, data: dict[str, str]) -> "EndDialysisDialog":
        """填写下机护士和回血流量，保留页面自动生成的结束时间。"""
        self._field(self.FIELDS["off_machine_nurse"]).select_option(
            label=data["off_machine_nurse"]
        )
        self._field(self.FIELDS["blood_return_flow"]).fill(
            data["blood_return_flow"]
        )
        return self

    def confirm(self, password: str) -> "EndDialysisDialog":
        """确认结束透析，填写登录密码提示并等待弹窗关闭。"""
        self._frame().get_by_role("button", name="确认", exact=True).click()
        self._confirm_password_warning_if_visible(password)
        self._wait_for_closed()
        return self

    def _confirm_password_warning_if_visible(self, password: str) -> None:
        """填写结束透析提交后出现的登录密码提示。"""
        warning = self._frame().locator(".layui-layer:visible").filter(
            has_text=self.PASSWORD_WARNING
        )
        try:
            warning.wait_for(state="visible", timeout=3_000)
        except PlaywrightTimeoutError:
            return

        password_input = warning.locator("#srmm_pwd:visible")
        expect(password_input).to_be_visible()
        password_input.click()
        password_input.press_sequentially(password)
        confirm_button = warning.get_by_text("确定", exact=True).filter(
            visible=True
        ).last
        expect(confirm_button).to_be_visible()
        confirm_button.click()
