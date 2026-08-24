"""移动端护士端治疗小结主页 POM。"""

import re
from collections.abc import Mapping
from urllib.parse import urlencode

from playwright.sync_api import Locator, Page, expect

from ..base_page import BasePage
from .dialogs.treatment_summary_select_dialog import TreatmentSummarySelectDialog


class TreatmentSummaryPage(BasePage):
    """封装独立的移动端治疗小结页面。"""

    URL = "https://yunjingzhi.com/yunjingservice/txform/mtxform_hzzlxj.shtml"
    PAGE_TITLE = "治疗小结"
    ROOT_SELECTOR = (
        'form[title="mtxform_hzzlxj_save"]:visible, '
        ".mtxform_hzzlxj_save:visible, #tx_form:visible"
    )
    PATIENT_INFO_SELECTOR = ".page_confirm_table:visible"
    SUMMARY_TABLE_SELECTOR = ".table_info:not(.page_confirm_table):visible"
    CONFIRM_BUTTON_SELECTOR = ".save_txform:visible"
    EXPORT_BUTTON_SELECTOR = "#tx_dcdbcjl_btn:visible"
    HANDOVER_BUTTON_SELECTOR = "#tx_dchzbq_btn:visible"
    CONFIRMED_STATUS = "已确认"
    UNCONFIRMED_STATUS = "未确认"

    FIELD_NAMES = {
        "education_template": "tx_xj_muban",
        "educator": "tx_xj_person",
        "education_content": "tx_zlxj_content",
        "summary_template": "tx_zlxj_muban",
        "summary_signer": "tx_xj_qm",
        "summary": "tx_zlxj_xj",
        "puncture_or_dressing": "tx_fs",
        "access_image": "tx_tltp",
        "dressing_nurse": "tx_sj_nurse",
        "treatment_nurse": "tx_zl_nurse",
        "machine_start_nurse": "tx_sjhs",
        "priming_nurse": "tx_ycgl",
        "checker": "tx_hd_nurse",
        "machine_stop_nurse": "tx_xj_nurse",
        "treatment_doctor": "tx_zl_doctor",
        "patient_signature": "tx_hz_qm",
        "dialyzer_number": "tx_txq_no",
    }
    TEXT_FIELDS = {
        "education_content",
        "summary",
        "dialyzer_number",
    }
    SELECT_FIELDS = {
        "educator",
        "summary_signer",
        "puncture_or_dressing",
        "dressing_nurse",
        "treatment_nurse",
        "machine_start_nurse",
        "priming_nurse",
        "checker",
        "machine_stop_nurse",
        "treatment_doctor",
    }
    READ_ONLY_FIELDS = {
        "education_template",
        "summary_template",
        "access_image",
        "patient_signature",
    }
    SELECTOR_FIELDS = SELECT_FIELDS | {
        "education_template",
        "summary_template",
        "access_image",
    }

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.select_dialog = TreatmentSummarySelectDialog(page)

    def open(
        self,
        tx_number: str,
        tx_name: str,
        tx_time: str,
    ) -> "TreatmentSummaryPage":
        """打开指定患者和日期的治疗小结页面。"""
        query = urlencode(
            {
                "tx_number": tx_number,
                "tx_name": tx_name,
                "tx_time": tx_time,
            }
        )
        self.navigate(f"{self.URL}?{query}")
        return self

    def root(self) -> Locator:
        return self.page.locator(self.ROOT_SELECTOR).first

    def summary_table(self) -> Locator:
        return self.root().locator(self.SUMMARY_TABLE_SELECTOR).first

    def is_loaded(self) -> bool:
        expect(self.page).to_have_title(self.PAGE_TITLE)
        expect(self.root()).to_be_visible()
        expect(self.page.locator(self.PATIENT_INFO_SELECTOR)).to_be_visible()
        expect(self.summary_table()).to_be_visible()
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
        table = self.summary_table()
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

    def fill_field(self, name: str, value: str) -> "TreatmentSummaryPage":
        if name in self.READ_ONLY_FIELDS:
            raise ValueError(f"治疗小结字段为只读字段，不能填写: {name}")
        if name in self.SELECT_FIELDS:
            raise ValueError(f"治疗小结选择字段应使用 select_field: {name}")
        field = self.field(name)
        expect(field).to_be_visible()
        expect(field).to_be_editable()
        field.fill(str(value))
        return self

    def open_field_selector(self, name: str) -> TreatmentSummarySelectDialog:
        if name not in self.SELECTOR_FIELDS:
            raise KeyError(f"不支持选择弹窗的治疗小结字段: {name}")
        field = self.field(name)
        expect(field).to_be_attached()
        row = field.locator("xpath=ancestor::tr[1]")
        selector = row.locator("a:has(img.modal_select_arrows)").first
        expect(selector).to_be_visible()
        selector.click()
        return self.select_dialog.wait_for_open()

    def select_field(self, name: str, label: str) -> "TreatmentSummaryPage":
        dialog = self.open_field_selector(name)
        dialog.select_option(label).save()
        return self

    def fill_summary(
        self, data: Mapping[str, object]
    ) -> "TreatmentSummaryPage":
        for name, value in data.items():
            if name not in self.FIELD_NAMES:
                raise KeyError(f"不支持的治疗小结字段: {name}")
            if name in self.READ_ONLY_FIELDS:
                raise ValueError(f"不能填写治疗小结只读字段: {name}")
            if name in self.SELECT_FIELDS:
                self.select_field(name, str(value))
            else:
                self.fill_field(name, str(value))
        return self

    def get_readonly_values(self) -> dict[str, str]:
        return {
            name: self.get_field_value(name) for name in self.READ_ONLY_FIELDS
        }

    def export_medical_record(self) -> "TreatmentSummaryPage":
        button = self.page.locator(self.EXPORT_BUTTON_SELECTOR)
        expect(button).to_be_visible()
        button.click()
        return self

    def sync_to_handover_log(self) -> "TreatmentSummaryPage":
        button = self.page.locator(self.HANDOVER_BUTTON_SELECTOR)
        expect(button).to_be_visible()
        button.click()
        return self

    def confirm(self) -> "TreatmentSummaryPage":
        button = self.page.locator(self.CONFIRM_BUTTON_SELECTOR).first
        expect(button).to_be_visible()
        button.click()
        return self

    def get_visible_actions(self) -> list[str]:
        return [
            " ".join(text.split())
            for text in self.root().locator("button:visible").all_inner_texts()
            if text.strip()
        ]
