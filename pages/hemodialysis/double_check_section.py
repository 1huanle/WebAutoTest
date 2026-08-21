from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, expect

from .dialysis_sheet_section import DialysisSheetSection


class DoubleCheckSection(DialysisSheetSection):
    """封装血液透析透析单中的双人核对分区。"""

    SECTION_TITLE = "双人核对"
    SAME_NURSE_WARNING = "核对人员和治疗护士确认是同一个人吗"
    # 血液透析 > 双人核对：四类核查组的状态和差错说明字段。
    GROUP_FIELDS = {
        "dialysis_items": ("tx_touXiWuPin_indicator", "tx_touXiWuPin_error"),
        "dialysis_parameters": ("tx_touXiCanShu_indicator", "tx_touXiCanShu_error"),
        "vascular_access": ("tx_xueGuanTongLu_indicator", "tx_xueGuanTongLu_error"),
        "pipeline_connection": ("tx_guanDao_indicator", "tx_guanDao_error"),
    }

    def _field(self, name: str):
        """返回血液透析 > 双人核对分区内指定 name 的控件。"""
        return self._section_table().locator(f'[name="{name}"]:visible')

    def mark_group_correct(self, group: str) -> "DoubleCheckSection":
        """将指定双人核对组标记为正确。"""
        indicator_name, _ = self.GROUP_FIELDS[group]
        self._field(indicator_name).check()
        return self

    def fill_group_error(self, group: str, message: str) -> "DoubleCheckSection":
        """将指定双人核对组标记为差错并填写说明。"""
        indicator_name, error_name = self.GROUP_FIELDS[group]
        self._field(indicator_name).uncheck()
        self._field(error_name).fill(message)
        return self

    def _detail_checkbox(self, label: str):
        """从精确业务标签定位相邻复选框，避免依赖全局固定序号。"""
        label_locator = self._section_table().get_by_text(label, exact=True).last
        checkbox = label_locator.locator(
            "xpath=preceding-sibling::input[@type='checkbox'][1]"
        )
        if checkbox.count():
            return checkbox
        previous_cell_checkbox = label_locator.locator(
            "xpath=ancestor::td[1]/preceding-sibling::td[1]//input[@type='checkbox']"
        )
        if previous_cell_checkbox.count():
            return previous_cell_checkbox
        return label_locator.locator("xpath=ancestor::td[1]//input[@type='checkbox']")

    def set_detail_checked(self, label: str, checked: bool) -> "DoubleCheckSection":
        """按双人核对业务标签设置明细勾选状态。"""
        checkbox = self._detail_checkbox(label)
        if checked:
            checkbox.check()
        else:
            checkbox.uncheck()
        return self

    def select_checker(self, checker: str) -> "DoubleCheckSection":
        """选择血液透析 > 双人核对的核对人员。"""
        self._field("tx_hd_nurse").select_option(label=checker)
        return self

    def get_check_time(self) -> str:
        """读取血液透析 > 双人核对的核对时间。"""
        return self._field("tx_check_time").input_value()

    def confirm(self) -> "DoubleCheckSection":
        """确认双人核对，并接受核对人与治疗护士相同的提示。"""
        self._section_table().get_by_role("button", name="确认", exact=True).click()
        self._confirm_same_nurse_warning_if_visible()
        return self

    def _confirm_same_nurse_warning_if_visible(self) -> None:
        """确认双人核对时核对人与治疗护士相同触发的提示。"""
        warning = self.page.locator(".layui-layer:visible").filter(
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

    def is_confirmed(self) -> bool:
        """确认血液透析 > 双人核对不再显示未确认状态。"""
        expect(self._section_table()).not_to_contain_text("未确认")
        return True

    def is_currently_confirmed(self) -> bool:
        """非等待式检查当前双人核对分区是否已确认。"""
        return not self._section_table().get_by_text("未确认", exact=True).is_visible()
