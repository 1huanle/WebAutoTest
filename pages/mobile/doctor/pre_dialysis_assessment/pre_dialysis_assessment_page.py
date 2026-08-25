import re
from collections.abc import Mapping
from urllib.parse import urlencode

from playwright.sync_api import Locator, Page, expect

from ..base_page import BasePage
from .dialogs.pre_assessment_modal import PreAssessmentModal


class PreDialysisAssessmentPage(BasePage):
    """医生端独立透前评估页面及其选择弹窗。"""

    URL_PATH = "/yunjingservice/txform/mtxform_hztqpg.shtml"
    PAGE_TITLE = "透前评估"
    FORM_SELECTOR = "#tx_form"
    PATIENT_INFO_SELECTOR = ".page_confirm_table"
    ASSESSMENT_TABLE_SELECTOR = ".table_info:not(.page_confirm_table)"
    CONFIRM_BUTTON_SELECTOR = "button.head_confirm_btn"
    SYNC_BUTTON_SELECTOR = ".xyj-btn"
    SAVE_BUTTON_SELECTOR = "button.btn.btn-info"
    CONFIRMED_STATUS = "已确认"
    UNCONFIRMED_STATUS = "未确认"

    FIELD_NAMES = {
        "temperature": "tx_pg_t",
        "pulse": "tx_pg_p",
        "respiration": "tx_pg_hr",
        "systolic_pressure": "tx_pg_BP_shousuo",
        "diastolic_pressure": "tx_pg_BP_shuzhang",
        "pre_weight": "tx_tqcz",
        "clothing_weight": "tx_peel_weight",
        "expected_dehydration_liters": "tx_yztsl",
        "supine_pulse": "tx_txq_mb",
        "supine_systolic_pressure": "tx_txq_ssy",
        "supine_diastolic_pressure": "tx_txq_szy",
        "a_thrombus": "tx_a_xx",
        "v_thrombus": "tx_v_xx",
        "standing_pulse": "tx_txq_mb_zw",
        "standing_systolic_pressure": "tx_txq_ssy_zw",
        "standing_diastolic_pressure": "tx_txq_szy_zw",
        "dry_weight": "tx_gtz",
        "previous_post_dialysis_weight": "tx_qctxhtz",
        "pre_dialysis_weight_calculated": "tx_tqtz",
        "weight_increase": "tx_tzzj",
        "total_ultrafiltration": "tx_clzl",
        "weighing_method": "txq_czfs",
        "interdialytic_period": "txqj_name",
        "previous_post_dialysis_status": "qctxh_name",
        "pre_dialysis_symptoms": "tqzz_name",
        "fistula_status": "nl_name",
        "catheter_status": "dg_name",
        "comorbidities": "hbz_name",
    }

    EDITABLE_FIELDS = {
        "temperature", "pulse", "respiration",
        "systolic_pressure", "diastolic_pressure",
        "pre_weight", "clothing_weight", "expected_dehydration_liters",
        "supine_pulse", "supine_systolic_pressure", "supine_diastolic_pressure",
        "a_thrombus", "v_thrombus", "standing_pulse", "standing_systolic_pressure",
        "standing_diastolic_pressure",
    }
    READONLY_FIELDS = {
        "dry_weight", "previous_post_dialysis_weight", "pre_dialysis_weight_calculated",
        "weight_increase", "total_ultrafiltration", "weighing_method",
        "interdialytic_period", "previous_post_dialysis_status", "pre_dialysis_symptoms",
        "fistula_status", "catheter_status", "comorbidities",
    }
    SELECT_FIELDS = {
        "weighing_method",
        "interdialytic_period", "previous_post_dialysis_status", "pre_dialysis_symptoms",
        "fistula_status", "catheter_status", "comorbidities",
    }
    SELECTOR_TITLES = {
        "interdialytic_period": "tx_txqj",
        "previous_post_dialysis_status": "tx_thzz",
        "pre_dialysis_symptoms": "tx_tqzz",
        "fistula_status": "txq_nl",
        "catheter_status": "txq_dg",
        "comorbidities": "tx_hbz",
    }

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.modal = PreAssessmentModal(page)

    def open(self, tx_number: str, tx_name: str, tx_time: str) -> "PreDialysisAssessmentPage":
        query = urlencode({"tx_number": tx_number, "tx_name": tx_name, "tx_time": tx_time})
        self.navigate(f"https://yunjingzhi.com{self.URL_PATH}?{query}")
        self.wait_for_paths((self.URL_PATH,))
        return self

    def root(self) -> Locator:
        return self.page.locator(self.FORM_SELECTOR).first

    def assessment_table(self) -> Locator:
        table = self.root().locator(self.ASSESSMENT_TABLE_SELECTOR + ":visible").first
        if table.count():
            return table
        return self.root()

    def is_loaded(self) -> bool:
        expect(self.page).to_have_title(self.PAGE_TITLE)
        expect(self.root()).to_be_visible()
        expect(self.root().locator(self.PATIENT_INFO_SELECTOR + ":visible")).to_be_visible()
        expect(self.page.locator(self.CONFIRM_BUTTON_SELECTOR + ":visible")).to_be_visible()
        return True

    def get_title(self) -> str:
        return self.page.title()

    @staticmethod
    def _match(text: str, pattern: str) -> str:
        match = re.search(pattern, text)
        return match.group(1).strip() if match else ""

    def get_patient_info(self) -> dict[str, str]:
        table = self.root().locator(self.PATIENT_INFO_SELECTOR + ":visible").first
        expect(table).to_be_visible()
        text = " ".join(table.inner_text().split())
        name = table.locator(".head_user_a:visible").first
        return {
            "name": name.inner_text().strip() if name.count() else "",
            "dialysis_number": self._match(text, r"透析号：([^\]\s]+)"),
            "machine_number": self._match(text, r"机号：([^\]\s]+)"),
            "birth_date": self._match(text, r"出生日期：([^\]\s]+)"),
            "age": self._match(text, r"(\d+)岁"),
            "text": text,
        }

    def get_status(self) -> str:
        status = self.root().get_by_text(
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
        table = self.assessment_table()
        visible = table.locator(f'[name="{field_name}"]:visible, #{field_name}:visible').first
        if visible.count():
            return visible
        return table.locator(f'[name="{field_name}"], #{field_name}').first

    def get_field_value(self, name: str) -> str:
        field = self.field(name)
        expect(field).to_be_visible()
        tag_name = field.evaluate("element => element.tagName.toLowerCase()")
        if tag_name in ("input", "select", "textarea"):
            return field.input_value().strip()
        return field.inner_text().strip()

    def get_readonly_values(self) -> dict[str, str]:
        return {
            name: self.get_field_value(name)
            for name in self.READONLY_FIELDS
            if self.field(name).count() and self.field(name).is_visible()
        }

    def fill_field(self, name: str, value: str) -> "PreDialysisAssessmentPage":
        if name in self.READONLY_FIELDS:
            raise AssertionError(f"医生端透前评估字段只读，不能直接填写: {name}")
        field = self.field(name)
        expect(field).to_be_visible()
        expect(field).to_be_editable()
        tag_name = field.evaluate("element => element.tagName.toLowerCase()")
        if tag_name == "select":
            field.select_option(label=str(value))
        else:
            field.fill(str(value))
            if name in {"pre_weight", "clothing_weight"}:
                field.press("End")
        return self

    def _selector_link(self, name: str) -> Locator:
        field = self.field(name)
        row = field.locator("xpath=ancestor::tr[1]")
        title = self.SELECTOR_TITLES.get(name)
        if title:
            link = row.locator(f'a[title="{title}"]').first
        else:
            link = row.locator('a:has(img.modal_select_arrows)').first
        if not link.count():
            link = row.locator('a:has(img.modal_select_arrows)').first
        expect(link).to_be_visible()
        return link

    def open_field_selector(self, name: str) -> PreAssessmentModal:
        if name not in self.SELECT_FIELDS:
            raise KeyError(f"不支持选择弹窗的透前评估字段: {name}")
        self._selector_link(name).click()
        return self.modal.wait_for_open()

    def select_field(self, name: str, value: str) -> "PreDialysisAssessmentPage":
        modal = self.open_field_selector(name)
        modal.select_value(value).save()
        return self

    def fill_assessment(self, data: Mapping[str, object]) -> "PreDialysisAssessmentPage":
        for name, value in data.items():
            if name not in self.FIELD_NAMES:
                raise KeyError(f"不支持的医生端透前评估字段: {name}")
            if name in self.SELECT_FIELDS:
                self.select_field(name, str(value))
            elif name in self.READONLY_FIELDS:
                expect(self.field(name)).to_have_value(str(value))
            else:
                self.fill_field(name, str(value))
        return self

    def confirm(self) -> "PreDialysisAssessmentPage":
        button = self.page.locator(self.CONFIRM_BUTTON_SELECTOR + ":visible").first
        expect(button).to_be_visible()
        button.click()
        return self

    def fetch_from_integration(self) -> "PreDialysisAssessmentPage":
        button = self.page.locator(self.SYNC_BUTTON_SELECTOR + ":visible").first
        expect(button).to_be_visible()
        button.click()
        return self

    def save(self, position: str | None = None) -> "PreDialysisAssessmentPage":
        buttons = self.assessment_table().locator(self.SAVE_BUTTON_SELECTOR + ":visible")
        if position:
            row = self.assessment_table().locator("tr").filter(has_text=position).first
            button = row.locator(self.SAVE_BUTTON_SELECTOR + ":visible").first
        else:
            button = buttons.first
        expect(button).to_be_visible()
        button.click()
        return self

    def save_supine_vitals(self) -> "PreDialysisAssessmentPage":
        return self.save("卧位")

    def save_standing_vitals(self) -> "PreDialysisAssessmentPage":
        return self.save("站位")

    def get_visible_actions(self) -> list[str]:
        return [
            " ".join(text.split())
            for text in self.page.locator("button:visible").all_inner_texts()
            if text.strip()
        ]
