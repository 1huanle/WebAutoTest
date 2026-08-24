from playwright.sync_api import Locator, expect

from .base_page import BasePage
from .dialogs.end_dialysis_dialog import EndDialysisDialog
from .dialogs.start_dialysis_dialog import StartDialysisDialog
from .sections.double_check_section import DoubleCheckSection
from .sections.monitoring_records_section import MonitoringRecordsSection
from .sections.post_dialysis_assessment_section import PostDialysisAssessmentSection
from .sections.pre_dialysis_assessment_section import PreDialysisAssessmentSection
from .prescription import PrescriptionPage
from .sections.temporary_orders_section import TemporaryOrdersSection
from .sections.treatment_summary_section import TreatmentSummarySection


class DialysisSheetPage(BasePage):
    """移动端护士端血液透析患者工作区。"""

    PATIENT_SEARCH_PLACEHOLDER = "透析号/姓名/姓名首拼"
    PATIENT_TABLE = "tbody"
    START_BUTTON_NAMES = ("上机准备", "开始透析")
    END_BUTTON_NAMES = ("下机", "结束透析")

    def _patient_search(self) -> Locator:
        search = self.page.get_by_placeholder(self.PATIENT_SEARCH_PLACEHOLDER)
        if not search.count():
            search = self.page.get_by_role(
                "textbox", name=self.PATIENT_SEARCH_PLACEHOLDER
            )
        return search.first

    def is_loaded(self) -> bool:
        """确认患者搜索区和至少一个透析业务分区均已显示。"""
        expect(self._patient_search()).to_be_visible()
        section_titles = ("透析处方", "透前评估", "监测记录", "患者信息")
        if not any(self.page.get_by_text(title, exact=True).filter(visible=True).count() for title in section_titles):
            raise AssertionError("未找到移动端透析业务分区")
        return True

    def get_schedule_date(self) -> str:
        """读取当前排班日期。"""
        fields = self.page.locator('input[name="tx_pb_date"]:visible')
        if not fields.count():
            fields = self.page.locator("input[type=date]:visible")
        return fields.first.input_value() if fields.count() else ""

    def get_visible_patient_count(self) -> int:
        """返回当前患者列表中的可见行数。"""
        tables = self.page.locator(self.PATIENT_TABLE)
        if tables.count() > 1:
            return tables.nth(1).locator("tr:visible").count()
        return tables.last.locator("tr:visible").count() if tables.count() else 0

    def _patient_rows(self) -> Locator:
        tables = self.page.locator(self.PATIENT_TABLE)
        return tables.nth(1).locator("tr") if tables.count() > 1 else tables.last.locator("tr")

    def _patient_row(self, keyword: str) -> Locator:
        row = self._patient_rows().filter(has_text=keyword).first
        expect(row).to_be_visible()
        return row

    def search_patient(self, keyword: str) -> "DialysisSheetPage":
        """按透析号、姓名或拼音搜索患者。"""
        self._patient_search().fill(keyword)
        self._patient_search().press("Enter")
        return self

    def select_patient_by_dialysis_number(self, dialysis_number: str) -> "DialysisSheetPage":
        """按透析号选择患者。"""
        row = self._patient_row(dialysis_number)
        target = row.get_by_text(dialysis_number, exact=True)
        (target if target.count() else row).first.click()
        return self

    def get_patient_status(self, dialysis_number: str) -> str:
        """读取指定患者当前状态。"""
        row = self._patient_row(dialysis_number)
        cells = row.locator("td")
        return cells.last.inner_text().strip() if cells.count() else row.inner_text().strip()

    def _open_dialog(self, names: tuple[str, ...], dialog):
        button = self.first_visible(
            self.page.get_by_role("button", name=name, exact=True) for name in names
        )
        button.click()
        return dialog.wait_for_open()

    def open_start_dialysis_dialog(self) -> StartDialysisDialog:
        """打开上机准备/开始透析弹窗。"""
        return self._open_dialog(self.START_BUTTON_NAMES, StartDialysisDialog(self.page))

    def open_end_dialysis_dialog(self) -> EndDialysisDialog:
        """打开下机/结束透析弹窗。"""
        return self._open_dialog(self.END_BUTTON_NAMES, EndDialysisDialog(self.page))

    @property
    def pre_dialysis_assessment(self) -> PreDialysisAssessmentSection:
        return PreDialysisAssessmentSection(self.page)

    @property
    def prescription(self) -> PrescriptionPage:
        return PrescriptionPage(self.page)

    @property
    def temporary_orders(self) -> TemporaryOrdersSection:
        return TemporaryOrdersSection(self.page)

    @property
    def double_check(self) -> DoubleCheckSection:
        return DoubleCheckSection(self.page)

    @property
    def monitoring_records(self) -> MonitoringRecordsSection:
        return MonitoringRecordsSection(self.page)

    @property
    def post_dialysis_assessment(self) -> PostDialysisAssessmentSection:
        return PostDialysisAssessmentSection(self.page)

    @property
    def treatment_summary(self) -> TreatmentSummarySection:
        return TreatmentSummarySection(self.page)
