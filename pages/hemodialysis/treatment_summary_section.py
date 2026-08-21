import re

from playwright.sync_api import expect

from .dialysis_sheet_section import DialysisSheetSection


class TreatmentSummarySection(DialysisSheetSection):
    """封装血液透析透析单中的治疗小结分区。"""

    SECTION_TITLE = "治疗小结"
    TEXT_FIELDS = {
        "education_content": "tx_zlxj_content",
        "summary": "tx_zlxj_xj",
        "dialyzer_number": "tx_txq_no",
    }
    # 血液透析 > 治疗小结：人员签名和治疗操作下拉字段。
    SELECT_FIELDS = {
        "educator": "tx_xj_person",
        "summary_signer": "tx_xj_qm",
        "puncture_or_dressing": "tx_zl_fs",
        "dressing_nurse": "tx_sj_nurse",
        "treatment_nurse": "tx_zl_nurse",
        "machine_start_nurse": "tx_sjhs",
        "priming_nurse": "tx_ycgl",
        "checker": "tx_hd_nurse",
        "machine_stop_nurse": "tx_xj_nurse",
        "treatment_doctor": "tx_zl_doctor",
    }
    READONLY_FIELDS = {
        "education_template": "tx_xj_muban",
        "summary_template": "tx_zlxj_muban",
        "access_image": "tx_tltp",
    }

    def _field(self, name: str):
        """返回血液透析 > 治疗小结分区内指定 name 的控件。"""
        return self._section_table().locator(f'[name="{name}"]:visible')

    def fill_summary(self, data: dict[str, str]) -> "TreatmentSummarySection":
        """填写血液透析 > 治疗小结的文本和人员选择项。"""
        for key, value in data.items():
            if key in self.TEXT_FIELDS:
                self._field(self.TEXT_FIELDS[key]).fill(value)
            else:
                self._field(self.SELECT_FIELDS[key]).select_option(label=value)
        return self

    def expect_readonly_values(
        self, data: dict[str, str]
    ) -> "TreatmentSummarySection":
        """校验治疗小结中的模板和通路图片只读字段。"""
        for key, value in data.items():
            expect(self._field(self.READONLY_FIELDS[key])).to_have_value(value)
        return self

    def _click_action(self, name: str) -> None:
        """在治疗小结分区内点击指定业务按钮。"""
        self._section_table().get_by_role("button", name=name, exact=True).click()

    def sync_to_medical_record(self) -> "TreatmentSummarySection":
        """点击血液透析 > 治疗小结的同步到病程按钮。"""
        self._click_action("同步到病程")
        return self

    def sync_to_handover_log(self) -> "TreatmentSummarySection":
        """点击血液透析 > 治疗小结的同步到交班日志按钮。"""
        self._click_action("同步到交班日志")
        return self

    def confirm(self) -> "TreatmentSummarySection":
        """点击血液透析 > 治疗小结分区的确认按钮。"""
        self._click_action("确认")
        return self

    def is_currently_confirmed(self) -> bool:
        """返回治疗小结当前是否已经确认，避免重复写入。"""
        status = (
            self._section_table()
            .get_by_text(re.compile(r"^(?:已确认|未确认)$"))
            .filter(visible=True)
        )
        expect(status).to_have_count(1)
        return status.inner_text().strip() == "已确认"

    def is_confirmed(self) -> bool:
        """确认血液透析 > 治疗小结不再显示未确认状态。"""
        expect(self._section_table()).not_to_contain_text("未确认")
        return True
