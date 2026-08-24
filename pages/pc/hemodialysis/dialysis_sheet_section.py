from playwright.sync_api import Locator, Page, expect


class DialysisSheetSection:
    """封装透析单中共用的血液透析业务分区读取行为。"""

    MODULE_NAME = "血液透析"
    SECTION_TITLE = ""

    def __init__(self, page: Page) -> None:
        """保存当前透析单页面，供分区内定位器复用。"""
        self.page = page

    def _section_table(self) -> Locator:
        """从可见分区标题返回最近业务表格，避免嵌套 tbody 重复匹配。"""
        title = self.page.get_by_text(self.SECTION_TITLE, exact=True).filter(visible=True).first
        return title.locator("xpath=ancestor::table[1]")

    def is_visible(self) -> bool:
        """确认分区标题在当前透析单页面中可见。"""
        expect(self._section_table().get_by_text(self.SECTION_TITLE, exact=True)).to_be_visible()
        return True

    def get_visible_actions(self) -> list[str]:
        """返回分区内当前可见的操作按钮名称，不执行任何操作。"""
        return self._section_table().get_by_role("button").all_inner_texts()

    def get_visible_field_labels(self) -> list[str]:
        """返回分区中当前可见的表单字段标签，不读取或修改字段值。"""
        labels = []
        for cell_text in self._section_table().get_by_role("cell").all_inner_texts():
            normalized_text = " ".join(cell_text.split())
            if normalized_text.endswith((":", "：")):
                labels.append(normalized_text)
        return labels