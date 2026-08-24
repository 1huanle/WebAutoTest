import re

from playwright.sync_api import expect

from .dialysis_sheet_section import DialysisSheetSection


class PreDialysisAssessmentSection(DialysisSheetSection):
    """封装血液透析透析单中的透前评估分区。"""

    SECTION_TITLE = "透前评估"

    # 血液透析 > 透前评估：业务字段到页面 name 的映射。
    EDITABLE_FIELDS = {
        "temperature": "tx_pg_t",
        "pulse": "tx_pg_p",
        "respiration": "tx_pg_hr",
        "respiration_type": "tx_pg_hr_type",
        "systolic_pressure": "tx_pg_BP_shousuo",
        "diastolic_pressure": "tx_pg_BP_shuzhang",
        "blood_pressure_site": "tx_pg_BP_type",
        "pre_weight": "tx_tqcz",
        "clothing_weight": "tx_peel_weight",
        "expected_dehydration_liters": "tx_yztsl",
        "a_thrombus": "tx_a_xx",
        "v_thrombus": "tx_v_xx",
    }
    SELECT_FIELDS = {"respiration_type", "blood_pressure_site"}
    WEIGHT_FIELDS = {"pre_weight", "clothing_weight"}

    def _field(self, name: str):
        """返回血液透析 > 透前评估分区内指定 name 的控件。"""
        return self._section_table().locator(f'[name="{name}"]:visible')

    def fill_assessment(self, data: dict[str, str]) -> "PreDialysisAssessmentSection":
        """填写血液透析 > 透前评估的可编辑内容。"""
        # 血压部位变更会清空血压值，必须先选择部位再填写收缩压和舒张压。
        blood_pressure_site = data.get("blood_pressure_site")
        if blood_pressure_site is not None:
            self._field(self.EDITABLE_FIELDS["blood_pressure_site"]).select_option(
                label=blood_pressure_site
            )
        for key, value in data.items():
            if key == "blood_pressure_site":
                continue
            if key == "weighing_method":
                self._section_table().locator("#txq_czfs").select_option(label=value)
                continue
            field = self._field(self.EDITABLE_FIELDS[key])
            if key in self.SELECT_FIELDS:
                field.select_option(label=value)
            else:
                field.fill(value)
                # 页面只在称重框触发 keyup 时，才会计算只读的透前体重。
                if key in self.WEIGHT_FIELDS:
                    field.press("End")
        return self

    def confirm(self) -> "PreDialysisAssessmentSection":
        """点击血液透析 > 透前评估分区的确认按钮。"""
        self._section_table().get_by_role("button", name="确认", exact=True).click()
        return self

    def is_currently_confirmed(self) -> bool:
        """等待透前评估状态加载完成，并返回当前是否已确认。"""
        status = (
            self._section_table()
            .get_by_text(re.compile(r"^(?:已确认|未确认)$"))
            .filter(visible=True)
        )
        expect(status).to_have_count(1)
        return status.inner_text().strip() == "已确认"

    def is_confirmed(self) -> bool:
        """确认血液透析 > 透前评估不再显示未确认状态。"""
        expect(self._section_table()).not_to_contain_text("未确认")
        return True
