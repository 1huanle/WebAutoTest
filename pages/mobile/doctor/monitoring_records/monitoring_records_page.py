import re
from urllib.parse import urlencode

from playwright.sync_api import Locator, Page, expect

from ..base_page import BasePage
from .detail import MonitoringRecordDetailPage


class MonitoringRecordsPage(BasePage):
    """医生端独立监测记录主页。"""

    URL_PATH = "/yunjingservice/txform/mtxform_hzjcjl.shtml"
    URL = f"https://yunjingzhi.com{URL_PATH}"
    PAGE_TITLE = "监测记录"
    FORM_SELECTOR = "#tx_form"
    PATIENT_INFO_SELECTOR = ".page_confirm_table:visible"
    STATUS_SELECTOR = ".head_confirm_status:visible"
    CONFIRM_SELECTOR = ".head_confirm_btn.jcjl_confirm:visible"
    RECORD_SELECTOR = ".jcjl_content.info_lable.long_press:visible"
    ADD_SELECTOR = 'img.page_info_add.info_lable[alt="添加"]:visible'
    BLOOD_PRESSURE_WATCH_SELECTOR = ".bp_watch:visible"

    CELL_FIELDS = {
        "pulse": 0,
        "respiration": 1,
        "blood_pressure": 2,
        "blood_flow": 4,
        "ultrafiltration_rate": 8,
        "ultrafiltration_volume": 9,
        "sodium_concentration": 10,
        "conductivity": 11,
        "dialysate_temperature": 12,
        "replacement_rate": 13,
        "replacement_volume": 14,
        "blood_temperature": 15,
        "blood_volume": 16,
        "blood_volume_change": 17,
        "online_urea": 18,
        "ktv": 19,
        # The compact list omits the detail-only treatment/result columns.
        # Keep their public keys in the returned record with empty values below.
        "symptoms": 20,
        "monitoring_nurse": 21,
        "temperature": 22,
        "spo2": 23,
    }

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.detail = MonitoringRecordDetailPage(page)

    def open(self, tx_number: str, tx_name: str, tx_time: str) -> "MonitoringRecordsPage":
        query = urlencode({
            "tx_number": tx_number,
            "tx_name": tx_name,
            "tx_time": tx_time,
        })
        self.navigate(f"{self.URL}?{query}")
        self.wait_for_paths((self.URL_PATH,))
        return self

    def is_loaded(self) -> bool:
        expect(self.page).to_have_title(self.PAGE_TITLE)
        expect(self.page.locator(self.PATIENT_INFO_SELECTOR)).to_be_visible()
        expect(self.page.locator(self.CONFIRM_SELECTOR)).to_be_visible()
        return True

    def get_title(self) -> str:
        return self.page.title()

    @staticmethod
    def _match(text: str, pattern: str) -> str:
        match = re.search(pattern, text)
        return match.group(1).strip() if match else ""

    def get_patient_info(self) -> dict[str, str]:
        table = self.page.locator(self.PATIENT_INFO_SELECTOR).first
        expect(table).to_be_visible()
        text = " ".join(table.inner_text().split())
        name = table.locator("a.head_user_a:visible").first
        return {
            "name": name.inner_text().strip() if name.count() else "",
            "dialysis_number": self._match(text, r"透析号：([^\]\s]+)"),
            "machine_number": self._match(text, r"机号：([^\]\s]+)"),
            "birth_date": self._match(text, r"出生日期：([^\]\s]+)"),
            "age": self._match(text, r"(\d+)岁"),
        }

    def get_status(self) -> str:
        status = self.page.get_by_text(
            re.compile(r"^(?:已确认|未确认)$")
        ).filter(visible=True).first
        expect(status).to_be_visible()
        return status.inner_text().strip()

    def is_confirmed(self) -> bool:
        return self.get_status() == "已确认"

    def _records(self) -> Locator:
        return self.page.locator(self.RECORD_SELECTOR)

    def get_record_headers(self) -> list[str]:
        headers = self.page.locator(
            ".tx_jcjl_title .jcjl_title_left:visible, "
            ".tx_jcjl_title .jcjl_title:visible"
        ).all_inner_texts()
        return [" ".join(text.split()) for text in headers if text.strip()]

    def get_visible_record_count(self) -> int:
        return self._records().count()

    def _record(self, record_id: str | None = None, record_time: str | None = None) -> Locator:
        if not record_id and not record_time:
            raise ValueError("必须提供监测记录 ID 或记录时间")
        records = self._records()
        if record_id:
            if any(char in record_id for char in ('"', "\\")):
                raise ValueError("监测记录 ID 不能包含引号或反斜杠")
            records = records.filter(
                has=self.page.locator(f'input[name="id"][value="{record_id}"]')
            )
        if record_time:
            records = records.filter(
                has=self.page.locator(".jcjl_time").filter(has_text=record_time)
            )
        record = records.first
        expect(record).to_be_visible()
        return record

    @staticmethod
    def _cell_values(record: Locator) -> list[str]:
        return [" ".join(text.split()) for text in record.locator(".jcjl_swipe_table td").all_inner_texts()]

    def _read_record(self, record: Locator) -> dict[str, str | list[str]]:
        cells = self._cell_values(record)
        values: dict[str, str | list[str]] = {
            "id": record.locator('input[name="id"]').input_value().strip(),
            "date": record.get_attribute("data-jcjlymd") or "",
            "time": record.locator(".jcjl_time:visible").inner_text().strip(),
            "record_type": record.locator("tr[data-jcjlxytype]").get_attribute("data-jcjlxytype") or "",
            "raw_values": cells,
        }
        for name, index in self.CELL_FIELDS.items():
            values[name] = cells[index] if len(cells) > index else ""
        values.setdefault("treatment", "")
        values.setdefault("result", "")
        return values

    def get_records(self) -> list[dict[str, str | list[str]]]:
        return [self._read_record(record) for record in self._records().all()]

    def get_record_info(
        self, record_id: str | None = None, record_time: str | None = None
    ) -> dict[str, str | list[str]]:
        return self._read_record(self._record(record_id, record_time))

    def get_record_status(
        self, record_id: str | None = None, record_time: str | None = None
    ) -> str:
        record = self._record(record_id, record_time)
        return "已确认" if self.is_confirmed() else "未确认"

    def open_record(
        self, record_id: str | None = None, record_time: str | None = None
    ) -> MonitoringRecordDetailPage:
        record = self._record(record_id, record_time)
        record_id_value = record.locator('input[name="id"]').input_value().strip()
        date = record.get_attribute("data-jcjlymd") or ""
        patient = self.get_patient_info()
        record.click()
        self.detail.wait_for_loaded()
        self.detail._context = {
            "tx_number": patient["dialysis_number"],
            "tx_name": patient["name"],
            "tx_time": self.page.locator('input[name="tx_time"]').input_value()
            if self.page.locator('input[name="tx_time"]').count()
            else "",
            "record_id": record_id_value,
            "record_date": date,
        }
        return self.detail

    def open_add_record(self) -> MonitoringRecordDetailPage:
        button = self.page.locator(self.ADD_SELECTOR).first
        expect(button).to_be_visible()
        patient = self.get_patient_info()
        tx_time = self.page.locator('input[name="tx_time"]').input_value()
        button.click()
        self.detail.wait_for_loaded()
        self.detail._context = {
            "tx_number": patient["dialysis_number"],
            "tx_name": patient["name"],
            "tx_time": tx_time,
            "record_id": "",
            "record_date": "",
        }
        return self.detail

    def open_blood_pressure_watch(self) -> "MonitoringRecordsPage":
        button = self.page.locator(self.BLOOD_PRESSURE_WATCH_SELECTOR).first
        expect(button).to_be_visible()
        button.click()
        return self

    def confirm(self) -> "MonitoringRecordsPage":
        button = self.page.locator(self.CONFIRM_SELECTOR).first
        expect(button).to_be_visible()
        button.click()
        return self

    def get_visible_actions(self) -> list[str]:
        return [
            " ".join(text.split())
            for text in self.page.locator("button:visible, a:visible, img:visible").all_inner_texts()
            if text.strip()
        ]
