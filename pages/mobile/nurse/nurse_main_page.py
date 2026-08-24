from playwright.sync_api import expect

from .base_page import BasePage
from .dialysis_sheet_page import DialysisSheetPage
from .orders import MedicalOrdersPage
from .post_dialysis_assessment import PostDialysisAssessmentPage
from .treatment_summary import TreatmentSummaryPage


class NurseMainPage(BasePage):
    """移动端护士端血液透析主页。"""

    URL = "https://yunjingzhi.com/yunjingservice/txform/mtxform_doctor.shtml"
    SUCCESS_PATHS = (
        "/yunjingservice/txform/mtxform.shtml",
        "/yunjingservice/txform/mtxform_doctor.shtml",
    )
    PATIENT_SEARCH_PLACEHOLDER = "透析号/姓名/姓名首拼"
    MODULE_NAME = "血液透析"
    ROLE_SELECTORS = (
        "[data-role]:visible",
        ".user-role:visible",
        ".role-name:visible",
    )

    def open(self, url: str = URL) -> "NurseMainPage":
        self.navigate(url)
        return self

    def is_loaded(self) -> bool:
        """确认主页和护士端患者工作区均已显示。"""
        search = self.page.get_by_placeholder(self.PATIENT_SEARCH_PLACEHOLDER)
        if not search.count():
            search = self.page.get_by_role(
                "textbox", name=self.PATIENT_SEARCH_PLACEHOLDER
            )
        expect(search).to_be_visible()
        expect(self.page.get_by_text(self.MODULE_NAME, exact=True).first).to_be_visible()
        return True

    def get_title(self) -> str:
        return self.page.title()

    def get_top_level_modules(self) -> list[str]:
        """读取当前可见的顶层业务菜单名称。"""
        items = self.page.locator("nav li:visible, .layui-nav li:visible")
        if not items.count():
            items = self.page.get_by_role("listitem").filter(visible=True)
        return [text.strip() for text in items.all_inner_texts() if text.strip()]

    def open_hemodialysis(self) -> DialysisSheetPage:
        """打开血液透析患者工作区。"""
        self.page.get_by_text(self.MODULE_NAME, exact=True).first.click()
        return DialysisSheetPage(self.page)

    def open_medical_orders(
        self,
        tx_number: str,
        tx_name: str,
        tx_time: str,
        tx_bc: str = "-1",
    ) -> MedicalOrdersPage:
        """打开指定患者的独立医嘱信息页面。"""
        return MedicalOrdersPage(self.page).open(
            tx_number=tx_number,
            tx_name=tx_name,
            tx_time=tx_time,
            tx_bc=tx_bc,
        )

    def open_post_dialysis_assessment(
        self,
        tx_number: str,
        tx_name: str,
        tx_time: str,
    ) -> PostDialysisAssessmentPage:
        """打开指定患者的独立透后评估页面。"""
        return PostDialysisAssessmentPage(self.page).open(
            tx_number=tx_number,
            tx_name=tx_name,
            tx_time=tx_time,
        )

    def open_treatment_summary(
        self,
        tx_number: str,
        tx_name: str,
        tx_time: str,
    ) -> TreatmentSummaryPage:
        """打开指定患者的独立治疗小结页面。"""
        return TreatmentSummaryPage(self.page).open(
            tx_number=tx_number,
            tx_name=tx_name,
            tx_time=tx_time,
        )

    @property
    def dialysis_sheet(self) -> DialysisSheetPage:
        """返回当前页面对应的血液透析患者工作区对象。"""
        return DialysisSheetPage(self.page)

    def get_current_role(self) -> str:
        """读取页面提供的当前角色文本；页面未提供时返回空字符串。"""
        role = self.page.locator(",".join(self.ROLE_SELECTORS)).first
        return role.inner_text().strip() if role.count() and role.is_visible() else ""
