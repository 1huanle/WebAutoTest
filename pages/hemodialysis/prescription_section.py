import re

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, expect

from .dialysis_sheet_section import DialysisSheetSection
from .dialogs.prescription_medical_order_push_dialog import (
    PrescriptionMedicalOrderPushDialog,
)


class PrescriptionSection(DialysisSheetSection):
    """封装血液透析透析单中的透析处方填写与确认操作。"""

    SECTION_TITLE = "透析处方"

    def __init__(self, page: Page) -> None:
        """初始化透析处方，并绑定血液透析 > 透析处方触发的弹窗组件。"""
        super().__init__(page)
        self.medical_order_push_dialog = PrescriptionMedicalOrderPushDialog(page)

    def _prescription_form(self):
        """返回透析处方专属表单，避免与其他分区的同名按钮冲突。"""
        return self.page.locator("#txcf_form")
    
    def _accept_visible_confirmation(self, button_text: str) -> None:
        """接受处方保存后可能出现的业务确认弹窗。"""
        button = self.page.locator(".layui-layer:visible").get_by_text(button_text, exact=True).last
        try:
            button.wait_for(state="visible", timeout=1_500)
        except PlaywrightTimeoutError:
            return
        button.click()
    def _dialysis_plan_sync_dialog(self):
        """返回当前可见的同步透析方案确认弹窗。"""
        return self.page.locator(".layui-layer:visible").filter(has_text="同步到透析方案")

    def open_dialysis_plan_sync_dialog(self) -> "PrescriptionSection":
        """打开同步透析方案确认弹窗，但不执行同步。"""
        self._prescription_form().get_by_role("button", name="同步到透析方案", exact=True).click()
        expect(self._dialysis_plan_sync_dialog()).to_be_visible()
        return self

    def cancel_dialysis_plan_sync(self) -> "PrescriptionSection":
        """点击同步透析方案弹窗的取消按钮并关闭遮罩。"""
        self._dialysis_plan_sync_dialog().get_by_text("取消", exact=True).click()
        return self

    def is_dialysis_plan_sync_dialog_closed(self) -> bool:
        """确认同步透析方案弹窗及其遮罩已关闭。"""
        expect(self._dialysis_plan_sync_dialog()).to_be_hidden()
        return True
    def _field(self, name: str):
        """返回处方分区内指定 name 属性的可编辑控件。"""
        return self._section_table().locator(f'[name="{name}"]:visible')

    def _fill_or_expect_current(self, name: str, value: str) -> None:
        """填写可编辑字段；页面计算出的只读字段则校验其当前值。"""
        field = self._field(name)
        if field.is_editable():
            field.fill(value)
        else:
            expect(field).to_have_value(value)
    def fill_prescription(self, data: dict[str, str]) -> "PrescriptionSection":
        """按 YAML 测试数据填写透析处方的可编辑字段。"""
        self._field("tx_txj_id").select_option(label=data["machine_number"])
        self._field("tx_knj_name").fill(data["anticoagulant"])
        self._field("tx_txfs_id").select_option(label=data["dialysis_mode"])
        self._field("tx_jcll").fill(data["dehydration_liters"])
        self._fill_or_expect_current("tx_sj", data["initial_dose"])
        self._fill_or_expect_current("tx_weichi", data["maintenance_dose"])
        self._field("tx_zlsc").fill(data["dialysis_hours"])
        self._field("tx_xtq_id").select_option(label=data["dialyzer"])
        self._field("tx_xgtlbw_id").select_option(label=data["access_side"])
        self._field("tx_xgtl_id").select_option(label=data["access_type"])
        self._field("tx_xll").fill(data["blood_flow"])
        self._field("tx_txyll").fill(data["dialysate_flow"])
        self._field("tx_txycf_na").fill(data["formula_sodium"])
        self._field("tx_txycf_jia").fill(data["potassium"])
        self._field("tx_txycf_gai").fill(data["calcium"])
        self._field("tx_txycf_tsqg").fill(data["bicarbonate"])
        self._field("tx_txcf_cfna").fill(data["dialysis_sodium"])
        self._field("tx_txcf_ptt").fill(data["glucose"])
        self._field("tx_clqx").fill(data["ultrafiltration_curve"])
        self._field("tx_naqx").fill(data["sodium_curve"])
        self._field("tx_qsna").fill(data["initial_sodium"])
        self._field("tx_cfxjl").fill(data["plasma_volume"])
        self._field("tx_jys").fill(data["chloride"])
        self._field("tx_zl_doctor_select").select_option(label=data["doctor"])
        self._field("tx_remark").fill(data["remark"])
        self._field("tx_twhxgl_id").select_option(label=data["blood_tubing"])
        return self

    def confirm(self) -> "PrescriptionSection":
        """点击透析处方分区的确认按钮，保存当前填写内容。"""
        is_first_confirmation = self._prescription_form().get_by_text(
            "未确认", exact=True
        ).is_visible()
        self._prescription_form().get_by_role("button", name="确认", exact=True).click()
        self._accept_visible_confirmation("继续")
        self._accept_visible_confirmation("确定")
        if is_first_confirmation:
            # 血液透析 > 透析处方触发：首次确认后处理医嘱推送弹窗。
            self.medical_order_push_dialog.wait_for_open().confirm()
        return self

    def is_currently_confirmed(self) -> bool:
        """等待透析处方状态加载完成，并返回当前是否已确认。"""
        status = (
            self._prescription_form()
            .get_by_text(re.compile(r"^(?:已确认|未确认)$"))
            .filter(visible=True)
        )
        expect(status).to_have_count(1)
        return status.inner_text().strip() == "已确认"

    def is_confirmed(self) -> bool:
        """确认处方分区不再显示未确认状态。"""
        expect(self._prescription_form()).not_to_contain_text("未确认")
        return True