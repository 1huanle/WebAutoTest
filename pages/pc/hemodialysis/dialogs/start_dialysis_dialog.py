from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, expect

from .layui_iframe_dialog import LayuiIframeDialog


class StartDialysisDialog(LayuiIframeDialog):
    """血液透析 > 开始透析触发：封装开始透析 iframe 弹窗。"""

    TITLE = "开始透析"
    PUNCTURE_SITE_WARNING = "穿刺点位信息未填写"
    SELECT_FIELDS = {
        "treatment_nurse": "tx_zl_nurse",
        "machine_nurse": "tx_sjhs",
        "priming_tubing_nurse": "tx_ycgl",
        "operation_type": "tx_fs",
        "puncture_nurse": "tx_sj_nurse",
        "admission_method": "tx_rkfs",
    }
    CHOICE_FIELDS = {
        "puncture_method": "tx_ccfs",
        "puncture_needle": "tx_ccz",
        "puncture_needle_model": "tx_cczxh",
        "puncture_direction": "tx_ccfx",
    }
    INPUT_FIELDS = {"blood_introduction_flow": "tx_yx"}

    def _field(self, name: str):
        """返回开始透析 iframe 内指定 name 的可见字段。"""
        return self._frame().locator(f'[name="{name}"]:visible')

    def _select_business_choice(self, name: str, value: str) -> None:
        """在只读字段的业务选项浮层中选择值并保存。"""
        self._field(name).click()
        choice_dialog = self._frame().get_by_role("dialog")
        expect(choice_dialog).to_be_visible()
        choice_dialog.get_by_role("button", name=value, exact=True).click()
        choice_dialog.get_by_role("link", name="保存", exact=True).click()
        expect(choice_dialog).to_be_hidden()

    def fill_start_dialysis(self, data: dict[str, str]) -> "StartDialysisDialog":
        """填写血液透析 > 开始透析弹窗中的指定内容。"""
        for key, name in self.SELECT_FIELDS.items():
            self._field(name).select_option(label=data[key])
        for key, name in self.CHOICE_FIELDS.items():
            self._select_business_choice(name, data[key])
        for key, name in self.INPUT_FIELDS.items():
            self._field(name).fill(data[key])
        return self

    def _confirm_puncture_site_warning_if_visible(self) -> None:
        """确认血液透析 > 开始透析触发的穿刺点位未填写提示。"""
        warning = self._frame().locator(".layui-layer:visible").filter(
            has_text=self.PUNCTURE_SITE_WARNING
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

    def confirm(self) -> "StartDialysisDialog":
        """确认开始透析，接受穿刺点位提示并等待弹窗关闭。"""
        self._frame().get_by_role("button", name="确认", exact=True).click()
        self._confirm_puncture_site_warning_if_visible()
        self._wait_for_closed()
        return self
