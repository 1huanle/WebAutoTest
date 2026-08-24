"""移动端护士端透后评估主页 POM。"""

import re
from collections.abc import Mapping
from urllib.parse import urlencode

from playwright.sync_api import Locator, Page, expect

from ..base_page import BasePage
from .dialogs.post_assessment_select_dialog import PostAssessmentSelectDialog


class PostDialysisAssessmentPage(BasePage):
    """封装独立的移动端透后评估页面。"""

    URL = "https://yunjingzhi.com/yunjingservice/txform/mtxform_hzthpg.shtml"
    PAGE_TITLE = "透后评估"
    PATIENT_INFO_SELECTOR = ".page_confirm_table:visible"
    ASSESSMENT_TABLE_SELECTOR = ".table_info:not(.page_confirm_table):visible"
    CONFIRM_BUTTON_SELECTOR = ".mtxform_hzthpg_save:visible"
    CONFIRMED_STATUS = "已确认"
    UNCONFIRMED_STATUS = "未确认"

    FIELD_NAMES = {
        "temperature": "tx_pg_t",
        "pulse": "tx_pg_p",
        "respiration": "tx_pg_hr",
        "systolic_pressure": "tx_pg_BP_shousuo",
        "diastolic_pressure": "tx_pg_BP_shuzhang",
        "blood_pressure_site": "tx_pg_BP_type",
        "actual_ultrafiltration_ml": "txh_sjcll",
        "actual_replacement_liters": "txh_sjzhl",
        "treatment_hours": "txh_sjsc_h",
        "treatment_minutes": "txh_sjsc_f",
        "weighing_method": "txq_czfs",
        "post_weight": "txh_cz",
        "clothing_weight": "tx_peel_weight_h",
        "post_dialysis_weight": "txh_tz",
        "weight_reduction": "txh_tzjs",
        "coagulation": "txh_nx_name",
        "post_dialysis_symptoms": "txh_tqzz_name",
        "fistula": "txh_nl_name",
        "catheter": "txh_dg_name",
        "complications": "txh_hbz_name",
        "total_intake": "txh_txzrl_h_hidden",
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
    SELECT_FIELDS = {
        "blood_pressure_site",
        "weighing_method",
        "coagulation",
        "post_dialysis_symptoms",
        "fistula",
        "catheter",
        "complications",
        "total_intake",
    }
    READ_ONLY_FIELDS = {"post_dialysis_weight", "weight_reduction"}
    SELECTOR_ROWS = {
        "blood_pressure_site": "tx_pg_BP_shousuo",
        "weighing_method": "txq_czfs",
        "coagulation": "txh_nx_name",
        "post_dialysis_symptoms": "txh_tqzz_name",
        "fistula": "txh_nl_name",
        "catheter": "txh_dg_name",
        "complications": "txh_hbz_name",
        "total_intake": "txh_txzrl_h_hidden",
    }

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.select_dialog = PostAssessmentSelectDialog(page)

    def open(
        self,
        tx_number: str,
        tx_name: str,
        tx_time: str,
    ) -> "PostDialysisAssessmentPage":
        query = urlencode(
            {
                "tx_number": tx_number,
                "tx_name": tx_name,
                "tx_time": tx_time,
            }
        )
        self.navigate(f"{self.URL}?{query}")
        return self

    def _assessment_table(self) -> Locator:
        return self.page.locator(self.ASSESSMENT_TABLE_SELECTOR).first

    def is_loaded(self) -> bool:
        expect(self.page).to_have_title(self.PAGE_TITLE)
        expect(self.page.locator(self.PATIENT_INFO_SELECTOR)).to_be_visible()
        expect(self._assessment_table()).to_be_visible()
        expect(self.page.locator(self.CONFIRM_BUTTON_SELECTOR)).to_be_visible()
        return True

    def get_title(self) -> str:
        return self.page.title()

    def get_patient_info(self) -> dict[str, str]:
        table = self.page.locator(self.PATIENT_INFO_SELECTOR).first
        expect(table).to_be_visible()
        text = " ".join(table.inner_text().split())
        name_link = table.locator("a.head_user_a:visible").first
        return {
            "name": name_link.inner_text().strip() if name_link.count() else "",
            "dialysis_number": self._match(text, r"透析号：([^\]\s]+)"),
            "machine_number": self._match(text, r"机号：([^\]\s]+)"),
            "birth_date": self._match(text, r"出生日期：([^\]\s]+)"),
            "age": self._match(text, r"(\d+)岁"),
        }

    @staticmethod
    def _match(text: str, pattern: str) -> str:
        match = re.search(pattern, text)
        return match.group(1).strip() if match else ""

    def get_status(self) -> str:
        status = self.page.get_by_text(
            re.compile(rf"^(?:{self.CONFIRMED_STATUS}|{self.UNCONFIRMED_STATUS})$")
        ).filter(visible=True).first
        expect(status).to_be_visible()
        return status.inner_text().strip()

    def is_confirmed(self) -> bool:
        return self.get_status() == self.CONFIRMED_STATUS

    def _field_name(self, name: str) -> str:
        return self.FIELD_NAMES.get(name, name)

    def field(self, name: str) -> Locator:
        field_name = self._field_name(name)
        table = self._assessment_table()
        visible = table.locator(
            f'[name="{field_name}"]:visible, #{field_name}:visible'
        ).first
        if visible.count():
            return visible
        return table.locator(f'[name="{field_name}"], #{field_name}').first

    def get_field_value(self, name: str) -> str:
        field = self.field(name)
        if not field.count():
            return ""
        expect(field).to_be_attached()
        tag_name = field.evaluate("element => element.tagName.toLowerCase()")
        if tag_name in ("input", "select", "textarea"):
            return field.input_value()
        return field.inner_text().strip()

    def fill_field(self, name: str, value: str) -> "PostDialysisAssessmentPage":
        if name in self.READ_ONLY_FIELDS:
            raise ValueError(f"透后评估字段为只读计算字段，不能填写: {name}")
        field = self.field(name)
        expect(field).to_be_visible()
        expect(field).to_be_editable()
        field.fill(str(value))
        return self

    def open_field_selector(self, name: str) -> PostAssessmentSelectDialog:
        if name not in self.SELECTOR_ROWS:
            raise KeyError(f"不支持选择弹窗的透后评估字段: {name}")
        field = self.field(self.SELECTOR_ROWS[name])
        expect(field).to_be_attached()
        row = field.locator("xpath=ancestor::tr[1]")
        selector = row.locator("a:has(img.modal_select_arrows)").first
        if not selector.count():
            selector = row.get_by_text("选择", exact=True).first
        expect(selector).to_be_visible()
        selector.click()
        return self.select_dialog.wait_for_open()

    def select_field(
        self, name: str, label: str
    ) -> "PostDialysisAssessmentPage":
        dialog = self.open_field_selector(name)
        dialog.select_option(label).save()
        return self

    def fill_assessment(
        self, data: Mapping[str, object]
    ) -> "PostDialysisAssessmentPage":
        for name, value in data.items():
            if name not in self.FIELD_NAMES:
                raise KeyError(f"不支持的透后评估字段: {name}")
            if name in self.READ_ONLY_FIELDS:
                raise ValueError(f"不能填写只读计算字段: {name}")
            if name in self.SELECT_FIELDS:
                self.select_field(name, str(value))
            else:
                self.fill_field(name, str(value))
        return self

    def get_calculated_values(self) -> dict[str, str]:
        return {
            name: self.get_field_value(name) for name in self.READ_ONLY_FIELDS
        }

    def _vitals_row(self, position: str) -> Locator:
        return self._assessment_table().locator("tr").filter(
            has_text=f"{position} P(次/分)"
        ).first

    def save_supine_vitals(self) -> "PostDialysisAssessmentPage":
        button = self._vitals_row("卧位").get_by_role(
            "button", name="保存", exact=True
        )
        expect(button).to_be_visible()
        button.click()
        return self

    def save_standing_vitals(self) -> "PostDialysisAssessmentPage":
        button = self._vitals_row("站位").get_by_role(
            "button", name="保存", exact=True
        )
        expect(button).to_be_visible()
        button.click()
        return self

    def confirm(self) -> "PostDialysisAssessmentPage":
        button = self.page.locator(self.CONFIRM_BUTTON_SELECTOR).first
        expect(button).to_be_visible()
        button.click()
        return self

    def get_visible_actions(self) -> list[str]:
        return [
            " ".join(text.split())
            for text in self.page.locator("button:visible").all_inner_texts()
            if text.strip()
        ]
