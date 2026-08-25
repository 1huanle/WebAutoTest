from collections.abc import Mapping

from playwright.sync_api import Locator, Page, expect

from .base_page import BasePage
from .double_check import DoubleCheckPage
from .monitoring_records import MonitoringRecordsPage
from .orders import MedicalOrdersPage
from .pre_dialysis_assessment import PreDialysisAssessmentPage
from .prescription import PrescriptionPage


class DoctorMainPage(BasePage):
    """移动端医生端血液透析主页及患者排班列表。"""

    URL = "https://yunjingzhi.com/yunjingservice/txform/mtxform_doctor.shtml"
    LOGIN_URL = "https://yunjingzhi.com/yunjingservice/login.jsp?origin=txjl_m"
    SUCCESS_PATHS = ("/yunjingservice/txform/mtxform_doctor.shtml",)
    PAGE_TITLE = "云净血透管理系统医生端"

    SEARCH_SELECTOR = "#searchparam"
    PATIENT_LIST_SELECTOR = ".page_user_list"
    PATIENT_CARD_SELECTOR = ".pgae_user_item"
    MODULE_SELECTOR = ".page_flex_ul_item"
    MODULE_TEXT_SELECTOR = ".page_menue_a"

    SHIFT_SELECTOR = "#tx_bc"
    WARD_SELECTOR = "#tx_bq"
    SORT_SELECTOR = "#tx_order"

    MODULE_NAMES = (
        "透析处方",
        "医嘱信息",
        "透析记录",
        "检验检查",
        "病程记录",
        "血管通路",
        "文书管理",
        "病历摘要",
    )

    def open(self, url: str = URL) -> "DoctorMainPage":
        """打开医生端主页；未登录时保留登录页结果供调用方判断。"""
        self.navigate(url)
        if any(path.rstrip("/") in self.page.url for path in self.SUCCESS_PATHS):
            self.wait_for_paths(self.SUCCESS_PATHS)
        return self

    def is_loaded(self) -> bool:
        """确认医生端主页的角色、菜单、筛选区和患者列表容器均已显示。"""
        expect(self.page).to_have_title(self.PAGE_TITLE)
        expect(self.page.locator(self.MODULE_SELECTOR + ":visible").first).to_be_visible()
        expect(self.page.locator(self.SEARCH_SELECTOR + ":visible")).to_be_visible()
        expect(self.page.locator(self.PATIENT_LIST_SELECTOR + ":visible")).to_be_visible()
        return True

    def get_title(self) -> str:
        return self.page.title()

    def get_current_role(self) -> str:
        """读取医生端角色；角色菜单隐藏时由当前页面路径和标题推断。"""
        role = self.page.get_by_text("医生端", exact=True).filter(visible=True).first
        if role.count() and role.is_visible():
            return role.inner_text().strip()
        if self.page.url.find("mtxform_doctor.shtml") >= 0 or self.get_title() == self.PAGE_TITLE:
            return "医生端"
        return ""

    def get_top_level_modules(self) -> list[str]:
        """读取当前可见的医生端一级菜单。"""
        return [
            text.strip()
            for text in self.page.locator(self.MODULE_SELECTOR + ":visible").all_inner_texts()
            if text.strip()
        ]

    def get_visible_modules(self) -> list[str]:
        """按已知医生端业务名称返回当前可见菜单。"""
        visible = {
            text.strip()
            for text in self.page.locator(self.MODULE_TEXT_SELECTOR + ":visible").all_inner_texts()
            if text.strip()
        }
        return [name for name in self.MODULE_NAMES if name in visible]

    def _filter(self, selector: str) -> Locator:
        field = self.page.locator(selector + ":visible").first
        expect(field).to_be_visible()
        return field

    @staticmethod
    def _selected_option_text(field: Locator) -> str:
        selected = field.locator("option:checked").first
        if selected.count():
            return selected.inner_text().strip()
        return field.input_value().strip()

    def get_selected_filters(self) -> dict[str, str]:
        """读取当前班次、病区和患者排序筛选的显示值。"""
        return {
            "shift": self._selected_option_text(self._filter(self.SHIFT_SELECTOR)),
            "ward": self._selected_option_text(self._filter(self.WARD_SELECTOR)),
            "sort_order": self._selected_option_text(self._filter(self.SORT_SELECTOR)),
        }

    def _select_filter(self, selector: str, value: str) -> "DoctorMainPage":
        field = self._filter(selector)
        options = field.locator("option")
        for option in options.all():
            if option.inner_text().strip() == str(value):
                field.select_option(label=str(value))
                return self
        field.select_option(value=str(value))
        return self

    def select_shift(self, value: str) -> "DoctorMainPage":
        """按选项文本或 value 选择班次。"""
        return self._select_filter(self.SHIFT_SELECTOR, value)

    def select_ward(self, value: str) -> "DoctorMainPage":
        """按选项文本或 value 选择病区。"""
        return self._select_filter(self.WARD_SELECTOR, value)

    def select_sort_order(self, value: str) -> "DoctorMainPage":
        """按选项文本或 value 选择患者排序方式。"""
        return self._select_filter(self.SORT_SELECTOR, value)

    def _patient_cards(self) -> Locator:
        return self.page.locator(
            f"{self.PATIENT_LIST_SELECTOR} {self.PATIENT_CARD_SELECTOR}:visible"
        )

    def _patient_card(self, dialysis_number: str) -> Locator:
        number = str(dialysis_number)
        if any(char in number for char in ('"', "\\")):
            raise ValueError("透析号不能包含引号或反斜杠")
        card = self.page.locator(
            f'{self.PATIENT_CARD_SELECTOR}[data-txnumber="{number}"]:visible'
        ).first
        expect(card).to_be_visible()
        return card

    def get_visible_patient_count(self) -> int:
        """返回当前患者列表中可见患者卡片数量。"""
        return self._patient_cards().count()

    def search_patient(self, keyword: str) -> "DoctorMainPage":
        """按透析号、姓名或姓名首拼筛选患者。"""
        search = self._filter(self.SEARCH_SELECTOR)
        search.fill(keyword)
        search.press("Enter")
        return self

    @staticmethod
    def _card_value(card: Locator, selector: str) -> str:
        field = card.locator(selector).first
        return field.inner_text().strip() if field.count() else ""

    @staticmethod
    def _card_input_value(card: Locator, name: str) -> str:
        field = card.locator(f'input[name="{name}"]').first
        return field.input_value().strip() if field.count() else ""

    def get_patient_info(self, dialysis_number: str) -> Mapping[str, str]:
        """读取指定患者卡片的业务信息。"""
        card = self._patient_card(dialysis_number)
        return {
            "dialysis_number": self._card_input_value(card, "tx_number")
            or card.get_attribute("data-txnumber")
            or str(dialysis_number),
            "name": self._card_input_value(card, "tx_name")
            or self._card_value(card, ".item_user_name"),
            "machine_number": self._card_input_value(card, "txjid")
            or self._card_value(card, ".txcf_txjid"),
            "status": self._card_value(card, ".item_tx_status"),
            "prescription_status": self._card_value(card, ".tx_txcf_status"),
            "dialysis_mode": self._card_value(card, ".txfs"),
        }

    def select_patient_by_dialysis_number(self, dialysis_number: str) -> "DoctorMainPage":
        """按透析号选择患者卡片。"""
        card = self._patient_card(dialysis_number)
        content = card.locator(".page_user_content:visible").first
        (content if content.count() else card).click()
        return self

    def get_patient_status(self, dialysis_number: str) -> str:
        """读取指定患者当前状态。"""
        return str(self.get_patient_info(dialysis_number)["status"])

    def open_prescription(
        self,
        tx_number: str,
        tx_name: str,
        tx_time: str,
    ) -> PrescriptionPage:
        """打开指定患者的医生端透析处方页面。"""
        return PrescriptionPage(self.page).open(
            tx_number=tx_number,
            tx_name=tx_name,
            tx_time=tx_time,
        )

    def open_pre_dialysis_assessment(
        self,
        tx_number: str,
        tx_name: str,
        tx_time: str,
    ) -> PreDialysisAssessmentPage:
        """打开指定患者的医生端透前评估页面。"""
        return PreDialysisAssessmentPage(self.page).open(
            tx_number=tx_number,
            tx_name=tx_name,
            tx_time=tx_time,
        )

    def open_medical_orders(
        self,
        tx_number: str,
        tx_name: str,
        tx_time: str,
        tx_bc: str = "-1",
    ) -> MedicalOrdersPage:
        """打开指定患者的医生端医嘱信息页面。"""
        return MedicalOrdersPage(self.page).open(
            tx_number=tx_number,
            tx_name=tx_name,
            tx_time=tx_time,
            tx_bc=tx_bc,
        )

    def open_monitoring_records(
        self,
        tx_number: str,
        tx_name: str,
        tx_time: str,
    ) -> MonitoringRecordsPage:
        """打开指定患者的医生端监测记录页面。"""
        return MonitoringRecordsPage(self.page).open(
            tx_number=tx_number,
            tx_name=tx_name,
            tx_time=tx_time,
        )

    def open_double_check(
        self,
        tx_number: str,
        tx_name: str,
        tx_time: str,
    ) -> DoubleCheckPage:
        """打开指定患者的医生端双人核对页面。"""
        return DoubleCheckPage(self.page).open(
            tx_number=tx_number,
            tx_name=tx_name,
            tx_time=tx_time,
        )
