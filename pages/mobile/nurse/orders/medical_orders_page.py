"""移动端护士端医嘱信息主页 POM。"""

import re
from collections.abc import Mapping
from urllib.parse import urlencode

from playwright.sync_api import Locator, Page, expect

from ..base_page import BasePage
from .dialogs.medical_order_dialog import MedicalOrderDialog


class MedicalOrdersPage(BasePage):
    """封装护士端独立的临时医嘱/长期医嘱页面。"""

    URL = "https://yunjingzhi.com/yunjingservice/txform/mtxform_hzlsyz.shtml"
    PAGE_TITLE = "医嘱信息"
    TEMPORARY_ORDER_TYPE = "临时医嘱"
    LONG_TERM_ORDER_TYPE = "长期医嘱"
    TAB_SELECTOR = ".yz_style:visible"
    ACTIVE_TAB_SELECTOR = ".yz_style.active_style:visible"
    ORDER_CARD_SELECTOR = ".table_info.info_lable.long_press:visible"
    PATIENT_INFO_SELECTOR = ".page_confirm_table:visible"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.order_dialog = MedicalOrderDialog(page)

    def open(
        self,
        tx_number: str,
        tx_name: str,
        tx_time: str,
        tx_bc: str = "-1",
    ) -> "MedicalOrdersPage":
        """打开指定患者、日期和班次的医嘱信息页面。"""
        query = urlencode(
            {
                "tx_number": tx_number,
                "tx_name": tx_name,
                "tx_time": tx_time,
                "tx_bc": tx_bc,
            }
        )
        self.navigate(f"{self.URL}?{query}")
        return self

    def is_loaded(self) -> bool:
        expect(self.page).to_have_title(self.PAGE_TITLE)
        expect(self.page.locator(self.TAB_SELECTOR).first).to_be_visible()
        expect(self.page.locator(self.PATIENT_INFO_SELECTOR)).to_be_visible()
        return True

    def get_title(self) -> str:
        return self.page.title()

    def get_patient_info(self) -> dict[str, str]:
        """读取页面顶部患者信息，不依赖患者卡片序号。"""
        table = self.page.locator(self.PATIENT_INFO_SELECTOR).first
        expect(table).to_be_visible()
        text = " ".join(table.inner_text().split())
        name_link = table.locator("a.head_user_a:visible").first
        name = name_link.inner_text().strip() if name_link.count() else ""
        return {
            "name": name,
            "dialysis_number": self._match(text, r"透析号：([^\]\s]+)"),
            "machine_number": self._match(text, r"机号：([^\]\s]+)"),
            "birth_date": self._match(text, r"出生日期：([^\]\s]+)"),
            "age": self._match(text, r"(\d+)岁"),
        }

    @staticmethod
    def _match(text: str, pattern: str) -> str:
        match = re.search(pattern, text)
        return match.group(1).strip() if match else ""

    def _tab(self, order_type: str) -> Locator:
        return self.page.locator(self.TAB_SELECTOR).filter(
            has_text=order_type
        ).first

    def switch_temporary_orders(self) -> "MedicalOrdersPage":
        tab = self._tab(self.TEMPORARY_ORDER_TYPE)
        expect(tab).to_be_visible()
        tab.click()
        expect(tab).to_have_class(re.compile(r"\bactive_style\b"))
        return self

    def switch_long_term_orders(self) -> "MedicalOrdersPage":
        tab = self._tab(self.LONG_TERM_ORDER_TYPE)
        expect(tab).to_be_visible()
        tab.click()
        expect(tab).to_have_class(re.compile(r"\bactive_style\b"))
        return self

    def get_active_order_type(self) -> str:
        active = self.page.locator(self.ACTIVE_TAB_SELECTOR).first
        expect(active).to_be_visible()
        return " ".join(active.inner_text().split())

    def _order_cards(self) -> Locator:
        return self.page.locator(self.ORDER_CARD_SELECTOR)

    def get_order_count(self) -> int:
        return self._order_cards().count()

    def _order_card(
        self, order_content: str, start_time: str | None = None
    ) -> Locator:
        cards = self._order_cards().filter(has_text=order_content)
        if start_time:
            cards = cards.filter(has_text=start_time)
        card = cards.first
        expect(card).to_be_visible()
        return card

    @staticmethod
    def _row_value(card: Locator, label: str) -> str:
        row = card.locator("tr").filter(has_text=label).first
        if not row.count():
            return ""
        cells = row.locator("td")
        if cells.count() < 2:
            return ""
        return " ".join(cells.nth(1).inner_text().split())

    @staticmethod
    def _status(card: Locator) -> str:
        waiting = card.locator(".waitexe_sign:visible").first
        if waiting.count():
            return " ".join(waiting.inner_text().split())
        executed = card.locator(".exe_sign:visible").first
        if executed.count():
            return " ".join(executed.inner_text().split())
        status = card.locator(".hisstatus:visible").first
        return " ".join(status.inner_text().replace("修改", "").split()) if status.count() else ""

    def _read_order(self, card: Locator) -> dict[str, str]:
        return {
            "doctor": self._row_value(card, "开嘱医生"),
            "status": self._status(card),
            "start_time": self._row_value(card, "开始时间"),
            "content": self._row_value(card, "医嘱内容"),
            "execute_time": self._row_value(card, "执行时间"),
            "executor": self._row_value(card, "执行人员"),
            "checker": self._row_value(card, "核对人员"),
        }

    def get_orders(self) -> list[dict[str, str]]:
        return [self._read_order(card) for card in self._order_cards().all()]

    def get_order_status(
        self, order_content: str, start_time: str | None = None
    ) -> str:
        return self._status(self._order_card(order_content, start_time))

    def select_order(
        self, order_content: str, start_time: str | None = None
    ) -> "MedicalOrdersPage":
        card = self._order_card(order_content, start_time)
        radio = card.locator('input[name="lsyzid"]').first
        expect(radio).to_be_visible()
        radio.check()
        return self

    def open_add_order(self) -> MedicalOrderDialog:
        button = self.page.locator("#add_yizhu_btn:visible")
        expect(button).to_be_visible()
        button.click()
        return self.order_dialog.wait_for_open()

    def open_edit_order(
        self, order_content: str, start_time: str | None = None
    ) -> MedicalOrderDialog:
        card = self._order_card(order_content, start_time)
        button = card.get_by_role("button", name="修改", exact=True)
        expect(button).to_be_visible()
        button.click()
        return self.order_dialog.wait_for_open()

    def get_visible_actions(self) -> list[str]:
        return [
            " ".join(text.split())
            for text in self.page.locator("button:visible, img:visible").all_inner_texts()
            if text.strip()
        ]
