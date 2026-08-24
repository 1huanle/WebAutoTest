import re

from playwright.sync_api import Page, expect

from .dialysis_sheet_section import DialysisSheetSection
from .dialogs.monitoring_record_dialog import MonitoringRecordDialog


class MonitoringRecordsSection(DialysisSheetSection):
    """封装血液透析透析单中的监测记录列表和操作。"""

    SECTION_TITLE = "监测记录"

    def __init__(self, page: Page) -> None:
        """初始化监测记录列表及其新增记录 iframe 组件。"""
        super().__init__(page)
        self.record_dialog = MonitoringRecordDialog(page)

    def get_record_headers(self) -> list[str]:
        """读取血液透析 > 监测记录表头。"""
        return [
            text.strip()
            for text in self._section_table().locator("th").all_inner_texts()
            if text.strip() != self.SECTION_TITLE
        ]

    def get_record_rows(self) -> list[list[str]]:
        """读取血液透析 > 监测记录中带选择框的数据行。"""
        rows = []
        for row in self._section_table().locator("tr").all():
            if row.get_by_role("checkbox").count():
                rows.append([text.strip() for text in row.locator("td").all_inner_texts()][1:])
        return rows

    def select_record(self, time: str) -> "MonitoringRecordsSection":
        """按监测时间勾选目标记录，避免依赖固定行号。"""
        row = self._section_table().locator("tr").filter(
            has=self.page.get_by_text(time, exact=True)
        )
        row.get_by_role("checkbox").check()
        return self

    def _click_action(self, name: str) -> None:
        """在监测记录分区内点击指定业务按钮。"""
        self._section_table().get_by_role("button", name=name, exact=True).click()

    def open_add_record(self) -> "MonitoringRecordsSection":
        """打开血液透析 > 监测记录触发的新增记录弹窗。"""
        self._click_action("添加监测")
        return self

    def fill_existing_records_from(
        self, records: list[dict], start_index: int
    ) -> "MonitoringRecordsSection":
        """从指定序号开始，按页面显示顺序填写已有监测记录。"""
        rows = [
            row
            for row in self._section_table().locator("tr").all()
            if re.search(r"\d{2}:\d{2}", row.inner_text())
            and row.evaluate(
                """
                element => Array.from(element.children).filter(
                    child => child.tagName === 'TD'
                ).length >= 2
                """
            )
        ]
        if len(rows) < start_index + len(records):
            raise AssertionError("页面中可编辑的监测记录数量不足")

        for index, record in enumerate(records):
            rows[start_index + index].dblclick()
            dialog = self.record_dialog.wait_for_open()
            dialog.fill_record(record["fields"])
            dialog.select_symptoms(record["symptoms"])
            dialog.select_result(record["result"])
            dialog.select_monitoring_nurse(record["monitoring_nurse"])
            dialog.confirm()
        return self

    def fill_existing_records(self, records: list[dict]) -> "MonitoringRecordsSection":
        """从第一条开始填写已有监测记录。"""
        return self.fill_existing_records_from(records, start_index=0)

    def delete_selected(self) -> "MonitoringRecordsSection":
        """删除当前勾选的监测记录。"""
        self._click_action("删除")
        return self

    def open_field_settings(self) -> "MonitoringRecordsSection":
        """打开监测记录字段设置。"""
        self._click_action("设置字段")
        return self

    def open_blood_pressure_watch(self) -> "MonitoringRecordsSection":
        """打开监测记录的血压手表功能。"""
        self._click_action("血压手表")
        return self

    def confirm(self) -> "MonitoringRecordsSection":
        """点击血液透析 > 监测记录分区的确认按钮。"""
        self._click_action("确认")
        return self

    def is_confirmed(self) -> bool:
        """确认血液透析 > 监测记录不再显示未确认状态。"""
        expect(self._section_table()).not_to_contain_text("未确认")
        return True
