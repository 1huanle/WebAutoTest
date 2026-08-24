import re

from playwright.sync_api import Locator, Page, expect

from .patient_detail_dialog import PatientDetailDialog


class PatientCard:
    """患者列表中的单个患者卡片。"""

    def __init__(self, page: Page, root: Locator) -> None:
        self.page = page
        self.root = root

    def select(self) -> "PatientCard":
        self.root.locator('input[type="checkbox"]').check(force=True)
        return self

    def deselect(self) -> "PatientCard":
        self.root.locator('input[type="checkbox"]').uncheck(force=True)
        return self

    def is_selected(self) -> bool:
        return self.root.locator('input[type="checkbox"]').is_checked()

    def open_detail(self) -> PatientDetailDialog:
        """打开当前患者的详情弹窗。"""
        self.root.get_by_text("患者详情", exact=True).click()
        return PatientDetailDialog(self.page).wait_for_open()


class PatientListSection:
    """封装患者管理页面的患者卡片列表和分页。"""

    CARD_SELECTOR = ".el-checkbox-group .card"
    PAGINATION_SELECTOR = ".el-pagination"

    def __init__(self, page: Page) -> None:
        self.page = page

    def _card(self, identifier: str) -> Locator:
        card = self.page.locator(self.CARD_SELECTOR).filter(has_text=identifier)
        if card.count() == 0:
            raise AssertionError(f"患者列表中未找到匹配项：{identifier}")
        return card.first

    def by_name(self, name: str) -> PatientCard:
        """按患者姓名定位患者卡片。"""
        return PatientCard(self.page, self._card(name))

    def by_dialysis_number(self, dialysis_number: str) -> PatientCard:
        """按透析号定位患者卡片。"""
        return PatientCard(self.page, self._card(dialysis_number))

    def select(self, identifier: str) -> "PatientListSection":
        """按患者姓名或透析号选择患者。"""
        PatientCard(self.page, self._card(identifier)).select()
        return self

    def deselect(self, identifier: str) -> "PatientListSection":
        """按患者姓名或透析号取消选择患者。"""
        PatientCard(self.page, self._card(identifier)).deselect()
        return self

    def _select_all_checkbox(self) -> Locator:
        label = self.page.get_by_text("全选患者列表", exact=True).locator(
            "xpath=ancestor::label[1]"
        )
        expect(label).to_be_visible()
        return label.locator('input[type="checkbox"]')

    def select_all(self) -> "PatientListSection":
        """选择当前列表中的全部患者。"""
        self._select_all_checkbox().check(force=True)
        return self

    def deselect_all(self) -> "PatientListSection":
        """取消当前列表中的全部患者。"""
        self._select_all_checkbox().uncheck(force=True)
        return self

    def get_selected_count(self) -> int:
        """读取当前已选择患者数量。"""
        text = self.page.get_by_text(re.compile(r"^已选择 \d+ 位患者$")).inner_text()
        return int(re.search(r"\d+", text).group())

    def get_total_count(self) -> int:
        """读取患者总数量。"""
        text = self.page.get_by_text(re.compile(r"^总 \d+ 条$")).inner_text()
        return int(re.search(r"\d+", text).group())

    def get_visible_patient_count(self) -> int:
        """读取当前页可见患者卡片数量。"""
        return self.page.locator(self.CARD_SELECTOR).count()

    def set_page_size(self, size: int) -> "PatientListSection":
        """设置患者列表每页数量。"""
        page_size = self.page.locator(
            f'{self.PAGINATION_SELECTOR} input.el-input__inner'
        ).first
        page_size.click()
        dropdown = self.page.locator(".el-select-dropdown:visible").last
        option_text = f"{size}条/页"
        option = dropdown.locator("li.el-select-dropdown__item").filter(
            has_text=option_text
        ).first
        expect(option).to_be_visible()
        option.click()
        return self

    def go_to_page(self, page_number: int) -> "PatientListSection":
        """切换患者列表页码。"""
        if page_number < 1:
            raise ValueError("页码必须大于等于 1")
        page_item = self.page.locator(
            f'{self.PAGINATION_SELECTOR} li.number'
        ).filter(has_text=str(page_number)).first
        expect(page_item).to_be_visible()
        page_item.click()
        return self
