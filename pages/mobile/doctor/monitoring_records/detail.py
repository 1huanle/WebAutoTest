import re
from collections.abc import Mapping
from urllib.parse import urlencode

from playwright.sync_api import Locator, Page, expect

from ..base_page import BasePage
from .dialogs.monitoring_record_select_modal import MonitoringRecordSelectModal


class MonitoringRecordDetailPage(BasePage):
    """医生端监测记录新增/编辑详情页。"""

    URL_PATH = "/yunjingservice/txform/mtxform_hzjcjl_detail.shtml"
    URL = f"https://yunjingzhi.com{URL_PATH}"
    PAGE_TITLE = "监测记录"
    FORM_SELECTOR = "#tx_form"
    SAVE_SELECTOR = ".save_jcjldetail_txform:visible"
    FIELD_NAMES = {
        "date": "tx_jcjl_ymd",
        "time": "tx_jcjl_time",
        "pulse": "tx_jcjl_mb",
        "respiration": "tx_jcjl_hx",
        "systolic_pressure": "tx_jcjl_xy",
        "diastolic_pressure": "tx_jcjl_xy1",
        "blood_flow": "tx_jcjl_xll",
        "venous_pressure": "tx_jcjl_my",
        "arterial_pressure": "tx_jcjl_dmy",
        "transmembrane_pressure": "tx_jcjl_kmy",
        "ultrafiltration_rate": "tx_jcjl_cll",
        "ultrafiltration_volume": "tx_jcjl_clliang",
        "sodium_concentration": "tx_jcjl_nnd",
        "conductivity": "tx_jcjl_ddd",
        "dialysate_temperature": "tx_jcjl_txywd",
        "replacement_rate": "tx_jcjl_zhl",
        "replacement_volume": "tx_jcjl_zhliang",
        "blood_temperature": "tx_entend_xw",
        "blood_volume_ml": "tx_jcjl_xrl",
        "blood_volume_liters": "tx_jcjl_xrl_L",
        "blood_volume_change": "tx_entend_xrlbhl",
        "online_urea": "tx_jcjl_zxns",
        "ktv": "tx_ktv",
        "symptoms": "tx_jcjl_zz_show",
        "treatment": "tx_jcjl_cl_show",
        "result": "tx_jcjl_jg_show",
        "temperature": "tx_jcjl_tw",
        "spo2": "tx_spo2",
        "treatment_flow": "tx_entend_cll",
        "plasma_separation_flow": "tx_entend_fjl",
        "transmembrane_pressure_2": "tx_entend_kmy",
        "inlet_pressure": "tx_entend_rky",
        "filtration_pressure": "tx_entend_lgy",
        "heparin_remaining": "tx_entend_gsyl",
        "pump_speed": "tx_entend_bs",
        "heart_rate": "tx_entend_xl",
        "monitoring_nurse": "tx_jcjl_hsname",
    }
    READONLY_FIELDS = {
        "date", "replacement_rate", "replacement_volume", "monitoring_nurse",
    }
    SELECT_FIELDS = {"symptoms", "treatment", "result", "monitoring_nurse"}

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.modal = MonitoringRecordSelectModal(page)
        self._context: dict[str, str] = {}

    def open(
        self,
        tx_number: str,
        tx_name: str,
        tx_time: str,
        record_id: str | None = None,
        record_date: str | None = None,
        tx_status: str = "0",
    ) -> "MonitoringRecordDetailPage":
        params = {
            "tx_number": tx_number,
            "tx_name": tx_name,
            "tx_time": tx_time,
            "tx_status": tx_status,
            "tx_jcjl_ymd": record_date or tx_time,
        }
        if record_id:
            params["id"] = record_id
        self.navigate(f"{self.URL}?{urlencode(params)}")
        return self.wait_for_loaded()

    def wait_for_loaded(self) -> "MonitoringRecordDetailPage":
        self.wait_for_paths((self.URL_PATH,))
        return self

    def root(self) -> Locator:
        return self.page.locator(self.FORM_SELECTOR).first

    def is_loaded(self) -> bool:
        expect(self.page).to_have_title(self.PAGE_TITLE)
        expect(self.root()).to_be_visible()
        expect(self.root().locator(self.SAVE_SELECTOR)).to_be_visible()
        return True

    def get_title(self) -> str:
        return self.page.title()

    @staticmethod
    def _match(text: str, pattern: str) -> str:
        match = re.search(pattern, text)
        return match.group(1).strip() if match else ""

    def get_patient_info(self) -> dict[str, str]:
        text = " ".join(self.root().inner_text().split())
        return {
            "name": self._match(text, r"姓名[:：]\s*([^\s]+)"),
            "dialysis_number": self._match(text, r"透析号[:：]\s*([^\s]+)"),
        }

    def _field_name(self, name: str) -> str:
        return self.FIELD_NAMES.get(name, name)

    def field(self, name: str) -> Locator:
        field_name = self._field_name(name)
        visible = self.root().locator(
            f'[name="{field_name}"]:visible, #{field_name}:visible'
        ).first
        if visible.count():
            return visible
        return self.root().locator(f'[name="{field_name}"], #{field_name}').first

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

    def fill_field(self, name: str, value: str) -> "MonitoringRecordDetailPage":
        if name in self.READONLY_FIELDS:
            raise AssertionError(f"监测记录字段只读，不能直接填写: {name}")
        field = self.field(name)
        expect(field).to_be_visible()
        expect(field).to_be_editable()
        tag_name = field.evaluate("element => element.tagName.toLowerCase()")
        if tag_name == "select":
            field.select_option(label=str(value))
        else:
            field.fill(str(value))
        return self

    def fill_record(self, data: Mapping[str, object]) -> "MonitoringRecordDetailPage":
        for name, value in data.items():
            if name not in self.FIELD_NAMES:
                raise KeyError(f"不支持的医生端监测记录字段: {name}")
            if name in self.SELECT_FIELDS:
                values = (
                    [str(item) for item in value]
                    if isinstance(value, (list, tuple, set))
                    else [str(value)]
                )
                self.select_field(name, values)
            elif name in self.READONLY_FIELDS:
                expect(self.field(name)).to_have_value(str(value))
            else:
                self.fill_field(name, str(value))
        return self

    def _selector_link(self, name: str) -> Locator:
        row = self.field(name).locator("xpath=ancestor::tr[1]")
        link = row.locator('a:has(img[alt="选择"])').first
        expect(link).to_be_visible()
        return link

    def open_field_selector(self, name: str) -> MonitoringRecordSelectModal:
        if name not in self.SELECT_FIELDS:
            raise KeyError(f"不支持选择弹窗的监测记录字段: {name}")
        self._selector_link(name).click()
        return self.modal.wait_for_open()

    def select_field(self, name: str, values: list[str]) -> "MonitoringRecordDetailPage":
        modal = self.open_field_selector(name)
        modal.select_values(values).confirm()
        return self

    def select_symptoms(self, values: list[str]) -> "MonitoringRecordDetailPage":
        return self.select_field("symptoms", values)

    def select_treatment(self, values: list[str]) -> "MonitoringRecordDetailPage":
        return self.select_field("treatment", values)

    def select_result(self, value: str) -> "MonitoringRecordDetailPage":
        return self.select_field("result", [value])

    def select_monitoring_nurse(self, value: str) -> "MonitoringRecordDetailPage":
        return self.select_field("monitoring_nurse", [value])

    def expect_readonly_values(self, data: Mapping[str, object]) -> "MonitoringRecordDetailPage":
        for name, value in data.items():
            if name not in self.READONLY_FIELDS:
                raise KeyError(f"不是只读监测记录字段: {name}")
            expect(self.field(name)).to_have_value(str(value))
        return self

    def save(self) -> "MonitoringRecordDetailPage":
        button = self.root().locator(self.SAVE_SELECTOR).first
        expect(button).to_be_visible()
        button.click()
        return self

    def cancel(self) -> "MonitoringRecordDetailPage":
        back = self.root().locator("a.back_a:visible").first
        expect(back).to_be_visible()
        back.click()
        return self

    def get_visible_actions(self) -> list[str]:
        return [
            " ".join(text.split())
            for text in self.root().locator("button:visible, a:visible").all_inner_texts()
            if text.strip()
        ]
