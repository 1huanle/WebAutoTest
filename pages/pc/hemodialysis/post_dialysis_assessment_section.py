import re

from playwright.sync_api import expect

from .dialysis_sheet_section import DialysisSheetSection


class PostDialysisAssessmentSection(DialysisSheetSection):
    """封装血液透析透析单中的透后评估分区。"""

    SECTION_TITLE = "透后评估"
    # 血液透析 > 透后评估：真实页面可编辑字段映射。
    EDITABLE_FIELDS = {
        "temperature": "tx_pg_t",
        "pulse": "tx_pg_p",
        "respiration": "tx_pg_hr",
        "respiration_type": "tx_pg_hr_type",
        "systolic_pressure": "tx_pg_BP_shousuo",
        "diastolic_pressure": "tx_pg_BP_shuzhang",
        "blood_pressure_site": "tx_pg_BP_type",
        "actual_ultrafiltration_ml": "txh_sjcll",
        "actual_replacement_liters": "txh_sjzhl",
        "treatment_hours": "txh_sjsc_h",
        "treatment_minutes": "txh_sjsc_f",
        "post_weight": "txh_cz",
        "clothing_weight": "tx_peel_weight_h",
        "actual_treatment_liters": "tx_sjcll",
        "waste_liquid_liters": "tx_fyl",
        "other": "tx_qt",
        "maximum_blood_flow": "tx_max_ll",
        "extracorporeal_blood_leak": "tx_twxhlx",
        "blood_leak_dose": "tx_lxjl",
        "injury_degree": "tx_sscd",
        "vascular_location": "tx_xgwz",
        "cause_and_timing": "tx_fsyy_sj",
    }
    SELECT_FIELDS = {"respiration_type", "blood_pressure_site"}
    CALCULATED_FIELDS = {
        "post_dialysis_weight": "txh_tz",
        "weight_reduction": "txh_tzjs",
        "coagulation": "txh_nx_name",
        "post_dialysis_symptoms": "txh_tqzz_name",
        "total_intake": "txh_txzrl_h_hidden",
        "fistula": "txh_nl_name",
        "catheter": "txh_dg_name",
        "complications": "txh_hbz_name",
    }

    def _field(self, name: str):
        """返回血液透析 > 透后评估分区内指定 name 的控件。"""
        return self._section_table().locator(f'[name="{name}"]:visible')

    def fill_assessment(self, data: dict[str, str]) -> "PostDialysisAssessmentSection":
        """填写血液透析 > 透后评估的可编辑内容。"""
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
                self._section_table().locator("#txh_czfs:visible").select_option(label=value)
                continue
            field = self._field(self.EDITABLE_FIELDS[key])
            if key in self.SELECT_FIELDS:
                field.select_option(label=value)
            else:
                field.fill(value)
        return self

    def expect_calculated_values(
        self, data: dict[str, str]
    ) -> "PostDialysisAssessmentSection":
        """校验血液透析 > 透后评估的只读或联动字段值。"""
        for key, value in data.items():
            expect(self._field(self.CALCULATED_FIELDS[key])).to_have_value(value)
        return self

    def confirm(self) -> "PostDialysisAssessmentSection":
        """点击血液透析 > 透后评估分区的确认按钮。"""
        self._section_table().get_by_role("button", name="确认", exact=True).click()
        return self

    def is_currently_confirmed(self) -> bool:
        """返回透后评估当前是否已经确认，避免重复写入。"""
        status = (
            self._section_table()
            .get_by_text(re.compile(r"^(?:已确认|未确认)$"))
            .filter(visible=True)
        )
        expect(status).to_have_count(1)
        return status.inner_text().strip() == "已确认"

    def is_confirmed(self) -> bool:
        """确认血液透析 > 透后评估不再显示未确认状态。"""
        expect(self._section_table()).not_to_contain_text("未确认")
        return True
