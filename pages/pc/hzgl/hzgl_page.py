from urllib.parse import urlsplit, urlunsplit

from config.config import Config
from playwright.sync_api import expect

from ..base_page import BasePage
from .patient_create_page import PatientCreatePage
from .patient_detail_dialog import PatientDetailDialog
from .patient_filter_section import PatientFilterSection
from .patient_list_section import PatientListSection


def _build_hzgl_url() -> str:
    """根据当前环境的域名生成患者管理地址。"""
    base_url = urlsplit(Config.BASE_URL)
    return urlunsplit(
        (
            base_url.scheme,
            base_url.netloc,
            "/yunjingservice/hz/searchbtn.shtml",
            "tx_select_period=3",
            "",
        )
    )


class HzglPage(BasePage):
    """PC 端患者管理页面。"""

    HZGL_URL = _build_hzgl_url()
    PAGE_TITLE = "患者管理"
    PATIENT_NAME_PLACEHOLDER = "请输入患者姓名"

    def open(self) -> "HzglPage":
        """打开患者管理页面。"""
        self.navigate(self.HZGL_URL)
        return self

    def is_loaded(self) -> bool:
        """确认患者管理页面的主要区域已经显示。"""
        self.page.get_by_role("menuitem", name=self.PAGE_TITLE, exact=True).wait_for(
            state="visible"
        )
        self.page.locator("form.hz_form:visible").wait_for(state="visible")
        self.page.get_by_placeholder(self.PATIENT_NAME_PLACEHOLDER).wait_for(
            state="visible"
        )
        self.page.locator("form.hz_form:visible button").filter(
            has_text="查询"
        ).first.wait_for(state="visible")
        return True

    @property
    def filters(self) -> PatientFilterSection:
        """返回患者筛选区域对象。"""
        return PatientFilterSection(self.page)

    @property
    def patient_list(self) -> PatientListSection:
        """返回患者卡片列表对象。"""
        return PatientListSection(self.page)

    @property
    def patient_detail_dialog(self) -> PatientDetailDialog:
        """返回患者详情弹窗对象。"""
        return PatientDetailDialog(self.page)

    def open_create_patient(self) -> PatientCreatePage:
        """点击“新增患者”并返回患者档案表单对象。"""
        create_button = self.page.locator("button").filter(has_text="新增患者").first
        expect(create_button).to_be_visible()
        create_page = PatientCreatePage(self.page)
        with self.page.expect_navigation(
            url="**/manage/useraddyj.shtml", wait_until="domcontentloaded"
        ):
            create_button.click()
        return create_page.wait_for_open()
