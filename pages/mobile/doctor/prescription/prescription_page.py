import re
from collections.abc import Mapping
from urllib.parse import urlencode

from playwright.sync_api import Locator, Page, expect

from ..base_page import BasePage
from .dialogs.prescription_modal import PrescriptionModal


class PrescriptionPage(BasePage):
    """医生端独立透析处方页面及其页面内选择弹窗。"""

    URL_PATH = "/yunjingservice/txform/mtxform_hztxcf.shtml"
    PAGE_TITLE = "透析处方"
    FORM_SELECTOR = "#tx_form"
    PATIENT_INFO_SELECTOR = ".page_confirm_table"
    STATUS_VALUES = ("已确认", "未确认")
    CONFIRM_SELECTOR = ".save_hztcxf_txform"
    SYNC_BUTTON_NAME = "同步透析方案"

    FIELD_NAMES = {
        "dry_weight": "txcf_gtz",
        "target_dehydration_reference": "tx_mubiao_ts",
        "dehydration_liters": "tx_jcll",
        "anticoagulant": "tx_knj_name",
        "initial_dose": "tx_sj",
        "maintenance_dose": "tx_weichi",
        "total_dose": "tx_zl",
        "anticoagulant_mode": "tx_zj_status",
        "dialysis_mode": "tx_txfs_id",
        "dialysis_hours": "tx_zlsc",
        "replacement_volume": "tx_zhzl",
        "replacement_mode": "tx_zhfs",
        "dialyzer": "tx_xtq_id",
        "filter": "tx_xlq_id",
        "perfusioner": "tx_glq_id",
        "access_side": "tx_xgtlbw_id",
        "access_type": "tx_xgtl_id",
        "blood_flow": "tx_xll",
        "dialysate_flow": "tx_txyll",
        "potassium": "tx_txycf_jia",
        "formula_sodium": "tx_txycf_na",
        "dialysis_sodium": "tx_txcf_cfna",
        "calcium": "tx_txycf_gai",
        "bicarbonate": "tx_txycf_tsqg",
        "glucose": "tx_txcf_ptt",
        "ultrafiltration_curve": "tx_clqx",
        "sodium_curve": "tx_naqx",
        "initial_sodium": "tx_qsna",
        "plasma_volume": "tx_cfxjl",
        "citrate": "tx_jys",
        "remark": "tx_remark",
        "doctor": "tx_zl_doctor",
    }

    READONLY_FIELDS = {
        "dry_weight",
        "target_dehydration_reference",
        "anticoagulant",
        "initial_dose",
        "maintenance_dose",
        "total_dose",
        "anticoagulant_mode",
        "dialysis_mode",
        "dialyzer",
        "access_side",
        "access_type",
        "doctor",
    }

    SELECT_FIELDS = {
        "anticoagulant",
        "dialysis_mode",
        "replacement_mode",
        "dialyzer",
        "filter",
        "perfusioner",
        "access_side",
        "access_type",
        "doctor",
    }

    SELECTOR_TITLES = {
        "anticoagulant": "txcf_knj",
        "dialysis_mode": "txcf_txfs",
        "dialyzer": "tx_xtq",
        "filter": "tx_xlq",
        "perfusioner": "tx_glq",
        "access_side": "txcf_xgtlbw",
        "access_type": "txcf_xgtl",
        "doctor": "tx_ys",
    }

    FIELD_ROW_LABELS = {"replacement_mode": "置换方式"}

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.modal = PrescriptionModal(page)

    def open(
        self,
        tx_number: str,
        tx_name: str,
        tx_time: str,
    ) -> "PrescriptionPage":
        query = urlencode(
            {"tx_number": tx_number, "tx_name": tx_name, "tx_time": tx_time}
        )
        self.navigate(f"https://yunjingzhi.com{self.URL_PATH}?{query}")
        self.wait_for_paths((self.URL_PATH,))
        return self

    def root(self) -> Locator:
        return self.page.locator(self.FORM_SELECTOR).first

    def is_loaded(self) -> bool:
        expect(self.page).to_have_title(self.PAGE_TITLE)
        expect(self.root()).to_be_visible()
        expect(self.root().locator(self.PATIENT_INFO_SELECTOR)).to_be_visible()
        expect(self.root().locator(self.CONFIRM_SELECTOR + ":visible")).to_be_visible()
        expect(self.page.get_by_role("button", name=self.SYNC_BUTTON_NAME, exact=True)).to_be_visible()
        return True

    def get_title(self) -> str:
        return self.page.title()

    def _status_locator(self) -> Locator:
        pattern = re.compile(r"^(?:已确认|未确认)$")
        return self.root().get_by_text(pattern).filter(visible=True).first

    def get_status(self) -> str:
        status = self._status_locator()
        expect(status).to_be_visible()
        return status.inner_text().strip()

    def is_confirmed(self) -> bool:
        return self.get_status() == "已确认"

    def get_patient_info(self) -> dict[str, str]:
        table = self.root().locator(self.PATIENT_INFO_SELECTOR).first
        expect(table).to_be_visible()
        text = " ".join(table.inner_text().split())

        name_locator = table.locator(".head_user_a:visible").first
        name = name_locator.inner_text().strip() if name_locator.count() else ""
        dialysis = re.search(r"透析号：([^\]\s]+)", text)
        machine = re.search(r"机号：([^\]\s]+)", text)
        mode = re.search(r"\](HDF|HD|HF|CRRT|透析)\b", text)
        return {
            "name": name,
            "dialysis_number": dialysis.group(1) if dialysis else "",
            "machine_number": machine.group(1) if machine else "",
            "dialysis_mode": mode.group(1) if mode else "",
            "status": self.get_status(),
            "text": text,
        }

    def _field_name(self, name: str) -> str:
        try:
            return self.FIELD_NAMES[name]
        except KeyError as exc:
            raise KeyError(f"不支持的医生端透析处方字段: {name}") from exc

    def field(self, name: str) -> Locator:
        field_name = self._field_name(name)
        visible = self.root().locator(f'[name="{field_name}"]:visible').first
        if visible.count():
            return visible
        return self.root().locator(f'[name="{field_name}"]').first

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

    def fill_field(self, name: str, value: str) -> "PrescriptionPage":
        if name in self.READONLY_FIELDS:
            raise AssertionError(f"医生端处方字段只读，不能直接填写: {name}")
        field = self.field(name)
        expect(field).to_be_visible()
        expect(field).to_be_editable()
        tag_name = field.evaluate("element => element.tagName.toLowerCase()")
        if tag_name == "select":
            field.select_option(label=str(value))
        else:
            field.fill(str(value))
        return self

    def _fill_or_expect_current(self, name: str, value: str) -> None:
        expect(self.field(name)).to_have_value(str(value))

    def fill_prescription(self, data: Mapping[str, object]) -> "PrescriptionPage":
        for name, value in data.items():
            if name not in self.FIELD_NAMES:
                raise KeyError(f"不支持的医生端透析处方字段: {name}")
            text_value = str(value)
            if name in self.SELECT_FIELDS:
                self.select_field(name, text_value)
            elif name in self.READONLY_FIELDS:
                self._fill_or_expect_current(name, text_value)
            else:
                self.fill_field(name, text_value)
        return self

    def open_field_selector(self, name: str) -> PrescriptionModal:
        field = self.field(name)
        row = field.locator("xpath=ancestor::tr[1]")
        title = self.SELECTOR_TITLES.get(name)
        if title:
            link = row.locator(f'a[title="{title}"]').first
        else:
            link = row.locator('a:has(img.modal_select_arrows)').first
        expect(link).to_be_visible()
        link.click()
        return self.modal.wait_for_open()

    def select_field(self, name: str, value: str) -> "PrescriptionPage":
        modal = self.open_field_selector(name)
        modal.select_value(value)
        modal.save()
        return self

    def confirm(self) -> "PrescriptionPage":
        self.root().locator(self.CONFIRM_SELECTOR + ":visible").click()
        return self

    def sync_to_dialysis_plan(self) -> "PrescriptionPage":
        """显式点击同步入口，不自动处理后续确认或保存弹窗。"""
        self.page.get_by_role(
            "button", name=self.SYNC_BUTTON_NAME, exact=True
        ).click()
        return self

    def get_visible_actions(self) -> list[str]:
        actions = [
            " ".join(text.split())
            for text in self.root().get_by_role("button").all_inner_texts()
            if text.strip()
        ]
        sync = self.page.get_by_role("button", name=self.SYNC_BUTTON_NAME, exact=True)
        if sync.count() and sync.first.is_visible():
            actions.append(self.SYNC_BUTTON_NAME)
        return actions
