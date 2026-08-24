import time

from playwright.sync_api import Response, expect

from .dialogs.end_dialysis_dialog import EndDialysisDialog
from .dialogs.start_dialysis_dialog import StartDialysisDialog
from .double_check_section import DoubleCheckSection
from .hemodialysis_page import HemodialysisPage
from .monitoring_records_section import MonitoringRecordsSection
from .post_dialysis_assessment_section import PostDialysisAssessmentSection
from .pre_dialysis_assessment_section import PreDialysisAssessmentSection
from .prescription_section import PrescriptionSection
from .temporary_orders_section import TemporaryOrdersSection
from .treatment_summary_section import TreatmentSummarySection


class DialysisSheetPage(HemodialysisPage):
    """封装血液透析模块中透析单的排班与患者列表区域。"""

    # 患者列表上方的检索输入框，使用页面稳定的占位文字定位。
    PATIENT_SEARCH_PLACEHOLDER = "透析号/姓名/姓名首拼"

    @property
    def patient_search_placeholder(self) -> str:
        """返回患者搜索框的占位文字，用于确认当前仍处于透析单页面。"""
        return self.PATIENT_SEARCH_PLACEHOLDER

    def is_loaded(self) -> bool:
        """确认透析单标题、血液透析菜单和患者搜索框均已显示。"""
        if not super().is_loaded():
            return False

        expect(
            self.page.get_by_role("textbox", name=self.PATIENT_SEARCH_PLACEHOLDER)
        ).to_be_visible()
        return True

    def get_schedule_date(self) -> str:
        """读取患者列表筛选区日期控件的当前排班日期。"""
        schedule_date = self.page.locator('input[name="tx_pb_date"]').input_value()
        if not schedule_date:
            raise AssertionError("未在透析单页面读取到排班日期")
        return schedule_date

    def get_visible_patient_count(self) -> int:
        """返回当前患者列表中可见的患者记录数量。"""
        return self.page.locator("tbody").nth(1).locator("tr").count()

    def _patient_row_by_dialysis_number(self, dialysis_number: str):
        """按透析号返回患者排班列表中的对应业务行。"""
        return (
            self.page.locator("tbody")
            .nth(1)
            .locator("tr")
            .filter(has_text=dialysis_number)
            .first
        )

    def is_patient_dialysis_in_progress(self, dialysis_number: str) -> bool:
        """读取指定患者排班状态是否为透析中。"""
        status = self._patient_row_by_dialysis_number(
            dialysis_number
        ).locator("td").last.inner_text().strip()
        return status == "透析中"

    def is_patient_post_dialysis(self, dialysis_number: str) -> bool:
        """读取指定患者排班状态是否为透析后。"""
        status = self._patient_row_by_dialysis_number(
            dialysis_number
        ).locator("td").last.inner_text().strip()
        return status == "透析后"

    def search_patient(self, keyword: str) -> "DialysisSheetPage":
        """按透析号、姓名或姓名首拼筛选当前患者列表。"""
        self.page.get_by_role("textbox", name=self.PATIENT_SEARCH_PLACEHOLDER).fill(keyword)
        return self

    @property
    def start_dialysis_dialog(self) -> StartDialysisDialog:
        """返回血液透析 > 开始透析触发的弹窗对象。"""
        return StartDialysisDialog(self.page)

    def open_start_dialysis_dialog(self) -> StartDialysisDialog:
        """点击开始透析并等待对应 iframe 弹窗打开。"""
        dialog = self.start_dialysis_dialog
        self.page.get_by_role("button", name="开始透析", exact=True).click()
        return dialog.wait_for_open()

    @property
    def end_dialysis_dialog(self) -> EndDialysisDialog:
        """返回血液透析 > 结束透析触发的弹窗对象。"""
        return EndDialysisDialog(self.page)

    def open_end_dialysis_dialog(self) -> EndDialysisDialog:
        """点击结束透析并等待对应 iframe 弹窗打开。"""
        dialog = self.end_dialysis_dialog
        self.page.get_by_role("button", name="结束透析", exact=True).click()
        return dialog.wait_for_open()

    @property
    def prescription(self) -> PrescriptionSection:
        """返回透析单中的透析处方业务分区对象。"""
        return PrescriptionSection(self.page)

    @property
    def pre_dialysis_assessment(self) -> PreDialysisAssessmentSection:
        """返回透析单中的透前评估业务分区对象。"""
        return PreDialysisAssessmentSection(self.page)
    @property
    def temporary_orders(self) -> TemporaryOrdersSection:
        """返回透析单中的临时医嘱业务分区对象。"""
        return TemporaryOrdersSection(self.page)
    @property
    def double_check(self) -> DoubleCheckSection:
        """返回透析单中的双人核对业务分区对象。"""
        return DoubleCheckSection(self.page)

    @property
    def monitoring_records(self) -> MonitoringRecordsSection:
        """返回透析单中的监测记录业务分区对象。"""
        return MonitoringRecordsSection(self.page)

    @property
    def post_dialysis_assessment(self) -> PostDialysisAssessmentSection:
        """返回透析单中的透后评估业务分区对象。"""
        return PostDialysisAssessmentSection(self.page)

    @property
    def treatment_summary(self) -> TreatmentSummarySection:
        """返回透析单中的治疗小结业务分区对象。"""
        return TreatmentSummarySection(self.page)
    def select_patient_by_dialysis_number(self, dialysis_number: str) -> "DialysisSheetPage":
        """通过透析号选中患者，并等待详情区切换到该患者。"""
        patient_row = self._patient_row_by_dialysis_number(dialysis_number)
        patient_name = patient_row.locator("td").nth(2).inner_text().strip()
        patient_row.get_by_text(dialysis_number, exact=True).click()
        expect(self.page.locator('input[name="tx_hz_name"]')).to_have_value(
            patient_name
        )
        return self

    def run_self_check(self) -> "DialysisSheetPage":
        """完成透析单自查，并等待服务端确认请求结束。"""
        confirm_responses: list[Response] = []

        def collect_confirmation(response: Response) -> None:
            if response.url.endswith("txform/mtxform_txreport_confirm.shtml"):
                confirm_responses.append(response)

        self.page.on("response", collect_confirmation)
        try:
            with self.page.expect_response(
                "**/txform/mtxform_txreport.shtml"
            ) as report_response_info:
                self.page.locator("#txform_check_btn:visible").click()

            report_response = report_response_info.value
            if not report_response.ok:
                raise AssertionError(f"自查报告请求失败，HTTP {report_response.status}")
            report = report_response.json()
            if report.get("status"):
                raise AssertionError(f"自查未通过：{report['status']}")

            # 个别提示项需要在弹窗中确认后，页面才会发送最终自查请求。
            if any(
                report.get(key) == "empty"
                for key in ("txzlxj_fx", "txzlxj_wd")
            ) or report.get("txjcjl") == "2":
                self.page.locator(".layui-layer:visible").get_by_text(
                    "确定", exact=True
                ).click()

            deadline = time.monotonic() + 10
            while not confirm_responses and time.monotonic() < deadline:
                self.page.wait_for_timeout(100)
            if not confirm_responses:
                raise AssertionError("自查报告已返回，但未收到最终自查确认请求")
            if not confirm_responses[-1].ok:
                raise AssertionError(
                    f"自查确认请求失败，HTTP {confirm_responses[-1].status}"
                )
        finally:
            self.page.remove_listener("response", collect_confirmation)
        return self
