import re
from urllib.parse import urlencode

from playwright.sync_api import Locator, Page, expect

from ..base_page import BasePage
from .dialogs.medical_order_dialog import MedicalOrderDialog
from .dialogs.order_type_menu import OrderTypeMenu


class MedicalOrdersPage(BasePage):
    """医生端独立的临时医嘱/长期医嘱页面。"""

    URL = "https://yunjingzhi.com/yunjingservice/txform/mtxform_hzlsyz.shtml"
    PAGE_TITLE = "医嘱信息"
    TEMPORARY_ORDER_TYPE = "临时医嘱"
    LONG_TERM_ORDER_TYPE = "长期医嘱"
    TAB_SELECTOR = ".yz_style:visible"
    ACTIVE_TAB_SELECTOR = ".yz_style.active_style:visible"
    ORDER_CARD_SELECTOR = ".table_info.info_lable.long_press:visible"
    PATIENT_INFO_SELECTOR = ".page_confirm_table:visible"
    ADD_ORDER_SELECTOR = "#add_yizhu_btn:visible"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.order_type_menu = OrderTypeMenu(page)
        self.order_dialog = MedicalOrderDialog(page)

    def open(
        self,
        tx_number: str,
        tx_name: str,
        tx_time: str,
        tx_bc: str = "-1",
    ) -> "MedicalOrdersPage":
        query = urlencode({
            "tx_number": tx_number,
            "tx_name": tx_name,
            "tx_time": tx_time,
            "tx_bc": tx_bc,
        })
        self.navigate(f"{self.URL}?{query}")
        self.wait_for_paths(("/yunjingservice/txform/mtxform_hzlsyz.shtml",))
        return self

    def is_loaded(self) -> bool:
        expect(self.page).to_have_title(self.PAGE_TITLE)
        expect(self.page.locator(self.TAB_SELECTOR).first).to_be_visible()
        expect(self.page.locator(self.PATIENT_INFO_SELECTOR)).to_be_visible()
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

    def _tab(self, order_type: str) -> Locator:
        return self.page.locator(self.TAB_SELECTOR).filter(has_text=order_type).first

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

    def _order_card(self, order_content: str, start_time: str | None = None) -> Locator:
        cards = self._order_cards().filter(has_text=order_content)
        if start_time:
            cards = cards.filter(has_text=start_time)
        card = cards.first
        expect(card).to_be_visible()
        return card

    def _order_card_by_id(self, order_id: str) -> Locator:
        if any(char in str(order_id) for char in ('"', "\\")):
            raise ValueError("医嘱 ID 不能包含引号或反斜杠")
        card = self.page.locator(
            f'{self.ORDER_CARD_SELECTOR}[data-id="{order_id}"]'
        ).first
        expect(card).to_be_visible()
        return card

    @staticmethod
    def _row_value(card: Locator, label: str) -> str:
        row = card.locator("tr").filter(has_text=label).first
        if not row.count():
            return ""
        cells = row.locator("td")
        return " ".join(cells.nth(1).inner_text().split()) if cells.count() > 1 else ""

    @staticmethod
    def _status(card: Locator) -> str:
        for selector in (".waitexe_sign:visible", ".exe_sign:visible", ".hisstatus:visible"):
            status = card.locator(selector).first
            if status.count():
                return " ".join(status.inner_text().replace("修改", "").split())
        return ""

    def _read_order(self, card: Locator) -> dict[str, str]:
        order_id = card.locator('input[name="id"]').first
        return {
            "id": order_id.input_value().strip() if order_id.count() else card.get_attribute("data-id") or "",
            "doctor": self._row_value(card, "开嘱医生"),
            "status": self._status(card),
            "start_time": self._row_value(card, "开始时间"),
            "content": self._row_value(card, "医嘱内容"),
            "remark": self._row_value(card, "备注"),
            "execute_time": self._row_value(card, "执行时间"),
            "executor": self._row_value(card, "执行人员"),
            "checker": self._row_value(card, "核对人员"),
        }

    def get_orders(self) -> list[dict[str, str]]:
        return [self._read_order(card) for card in self._order_cards().all()]

    def get_order_info(self, order_content: str, start_time: str | None = None) -> dict[str, str]:
        return self._read_order(self._order_card(order_content, start_time))

    def get_order_info_by_id(self, order_id: str) -> dict[str, str]:
        return self._read_order(self._order_card_by_id(order_id))

    def get_order_status(self, order_content: str, start_time: str | None = None) -> str:
        return self._status(self._order_card(order_content, start_time))

    def select_order(self, order_content: str, start_time: str | None = None) -> "MedicalOrdersPage":
        card = self._order_card(order_content, start_time)
        radio = card.locator('input[name="lsyzid"]').first
        expect(radio).to_be_visible()
        radio.check()
        return self

    def open_add_order_menu(self) -> OrderTypeMenu:
        button = self.page.locator(self.ADD_ORDER_SELECTOR).first
        expect(button).to_be_visible()
        button.click()
        return self.order_type_menu.wait_for_open()

    def open_add_order(self) -> OrderTypeMenu:
        """打开新增医嘱类型选择层，不自动选择类型或提交医嘱。"""
        return self.open_add_order_menu()

    def open_new_order(self) -> MedicalOrderDialog:
        self.open_add_order_menu().select_new_order()
        return self.order_dialog.wait_for_open()

    def open_edit_order(self, order_content: str, start_time: str | None = None) -> MedicalOrderDialog:
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
