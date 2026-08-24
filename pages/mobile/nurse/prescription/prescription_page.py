"""移动端护士端透析处方页面对象。"""

from collections.abc import Mapping

from playwright.sync_api import Locator, Page, expect

from ..base_page import BasePage
from .dialogs.medical_order_push_dialog import MedicalOrderPushDialog
from .dialogs.prescription_sync_dialog import PrescriptionSyncDialog


class PrescriptionPage(BasePage):
    """封装移动端透析处方表单及其显式弹窗操作。"""

    FORM_SELECTOR = "#txcf_form"
    SECTION_TITLE = "透析处方"
    CONFIRMED_STATUS = "已确认"
    UNCONFIRMED_STATUS = "未确认"

    FIELD_NAMES = {
        "machine_number": "tx_txj_id",
        "anticoagulant": "tx_knj_name",
        "dialysis_mode": "tx_txfs_id",
        "dehydration_liters": "tx_jcll",
        "initial_dose": "tx_sj",
        "maintenance_dose": "tx_weichi",
        "dialysis_hours": "tx_zlsc",
        "dialyzer": "tx_xtq_id",
        "access_side": "tx_xgtlbw_id",
        "access_type": "tx_xgtl_id",
        "blood_flow": "tx_xll",
        "dialysate_flow": "tx_txyll",
        "formula_sodium": "tx_txycf_na",
        "potassium": "tx_txycf_jia",
        "calcium": "tx_txycf_gai",
        "bicarbonate": "tx_txycf_tsqg",
        "dialysis_sodium": "tx_txcf_cfna",
        "glucose": "tx_txcf_ptt",
        "ultrafiltration_curve": "tx_clqx",
        "sodium_curve": "tx_naqx",
        "initial_sodium": "tx_qsna",
        "plasma_volume": "tx_cfxjl",
        "chloride": "tx_jys",
        "doctor": "tx_zl_doctor_select",
        "remark": "tx_remark",
        "blood_tubing": "tx_twhxgl_id",
    }

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.sync_dialog = PrescriptionSyncDialog(page)
        self.medical_order_push_dialog = MedicalOrderPushDialog(page)

    def root(self) -> Locator:
        """返回透析处方表单，所有字段定位均限制在此范围内。"""
        return self.page.locator(self.FORM_SELECTOR).first

    def is_visible(self) -> bool:
        form = self.root()
        expect(form).to_be_visible()
        return True

    def _status_locator(self) -> Locator:
        return self.root().get_by_text(
            self.CONFIRMED_STATUS, exact=True
        ).or_(self.root().get_by_text(self.UNCONFIRMED_STATUS, exact=True)).filter(
            visible=True
        ).first

    def get_status(self) -> str:
        status = self._status_locator()
        expect(status).to_be_visible()
        return status.inner_text().strip()

    def is_confirmed(self) -> bool:
        return self.get_status() == self.CONFIRMED_STATUS

    def _field_name(self, name: str) -> str:
        return self.FIELD_NAMES.get(name, name)

    def field(self, name: str) -> Locator:
        field_name = self._field_name(name)
        form = self.root()
        visible = form.locator(
            f'[name="{field_name}"]:visible, #{field_name}:visible'
        ).first
        if visible.count():
            return visible
        return form.locator(f'[name="{field_name}"], #{field_name}').first

    def get_field_value(self, name: str) -> str:
        field = self.field(name)
        expect(field).to_be_visible()
        tag_name = field.evaluate("element => element.tagName.toLowerCase()")
        if tag_name in ("input", "select", "textarea"):
            return field.input_value()
        return field.inner_text().strip()

    def fill_field(self, name: str, value: str) -> "PrescriptionPage":
        field = self.field(name)
        expect(field).to_be_visible()
        expect(field).to_be_editable()
        tag_name = field.evaluate("element => element.tagName.toLowerCase()")
        if tag_name == "select":
            field.select_option(label=str(value))
        else:
            field.fill(str(value))
        return self

    def select_field(self, name: str, label: str) -> "PrescriptionPage":
        field = self.field(name)
        expect(field).to_be_visible()
        expect(field).to_be_editable()
        tag_name = field.evaluate("element => element.tagName.toLowerCase()")
        if tag_name == "select":
            field.select_option(label=label)
        else:
            field.click()
            field.fill(label)
        return self

    def _fill_or_expect_current(self, name: str, value: str) -> None:
        field = self.field(name)
        expect(field).to_be_visible()
        if field.is_editable():
            self.fill_field(name, value)
        else:
            expect(field).to_have_value(str(value))

    def fill_prescription(self, data: Mapping[str, object]) -> "PrescriptionPage":
        """按业务字段名填写处方，仅操作数据中实际提供的字段。"""
        select_fields = {
            "machine_number",
            "dialysis_mode",
            "dialyzer",
            "access_side",
            "access_type",
            "doctor",
            "blood_tubing",
        }
        readonly_fields = {"initial_dose", "maintenance_dose"}
        for name, value in data.items():
            if name not in self.FIELD_NAMES:
                raise KeyError(f"不支持的透析处方字段: {name}")
            if name in readonly_fields:
                self._fill_or_expect_current(name, str(value))
            elif name in select_fields:
                self.select_field(name, str(value))
            else:
                self.fill_field(name, str(value))
        return self

    def _confirm_button(self) -> Locator:
        return self.root().get_by_role("button", name="确认", exact=True).first

    def confirm(self) -> MedicalOrderPushDialog:
        """点击处方确认按钮并返回医嘱推送弹窗对象。"""
        self._confirm_button().click()
        return self.medical_order_push_dialog

    def open_dialysis_plan_sync_dialog(self) -> PrescriptionSyncDialog:
        button = self.root().get_by_role(
            "button", name="同步到透析方案", exact=True
        )
        expect(button).to_be_visible()
        button.click()
        return self.sync_dialog.wait_for_open()

    def cancel_dialysis_plan_sync(self) -> PrescriptionSyncDialog:
        dialog = self.sync_dialog.wait_for_open()
        dialog.cancel()
        return dialog

    def sync_to_dialysis_plan(self) -> PrescriptionSyncDialog:
        dialog = self.sync_dialog.wait_for_open()
        dialog.confirm()
        return dialog

    def is_medical_order_push_dialog_visible(self) -> bool:
        dialog = self.medical_order_push_dialog.root()
        return dialog.count() > 0 and dialog.first.is_visible()

    def get_visible_actions(self) -> list[str]:
        return [
            " ".join(text.split())
            for text in self.root().get_by_role("button").all_inner_texts()
            if text.strip()
        ]
