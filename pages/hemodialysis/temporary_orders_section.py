import re

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, expect

from .dialysis_sheet_section import DialysisSheetSection
from .dialogs.temporary_order_dialog import TemporaryOrderDialog
from .dialogs.temporary_order_execution_dialog import TemporaryOrderExecutionDialog


class TemporaryOrdersSection(DialysisSheetSection):
    """封装血液透析透析单中的临时医嘱列表和操作。"""

    SECTION_TITLE = "临时医嘱"

    def __init__(self, page: Page) -> None:
        """初始化临时医嘱列表及其新增医嘱 iframe 组件。"""
        super().__init__(page)
        self.order_dialog = TemporaryOrderDialog(page)
        self.execution_dialog = TemporaryOrderExecutionDialog(page)

    def get_order_headers(self) -> list[str]:
        """读取血液透析 > 临时医嘱列表的表头。"""
        header_row = self._section_table().locator("tr").filter(has_text="医嘱内容")
        return [text.strip() for text in header_row.locator("th").all_inner_texts()]

    def get_order_rows(self) -> list[list[str]]:
        """读取血液透析 > 临时医嘱中带选择框的业务行。"""
        rows = []
        for row in self._section_table().locator("tr").all():
            if row.get_by_role("checkbox").count():
                rows.append([text.strip() for text in row.locator("td").all_inner_texts()][1:])
        return rows

    def _order_row(self, order_content: str):
        """按医嘱内容返回目标临时医嘱行，避免依赖固定行号。"""
        return self._section_table().locator("tr").filter(
            has=self.page.get_by_text(order_content, exact=True)
        )

    def select_order(self, order_content: str) -> "TemporaryOrdersSection":
        """勾选指定内容的临时医嘱。"""
        self._order_row(order_content).get_by_role("checkbox").check()
        return self

    def _click_action(self, name: str) -> None:
        """在临时医嘱分区内点击指定业务按钮。"""
        self._section_table().get_by_role("button", name=name, exact=True).click()

    def open_add_order(self) -> "TemporaryOrdersSection":
        """打开血液透析 > 临时医嘱触发的新增医嘱弹窗。"""
        self._click_action("添加医嘱")
        return self

    def add_orders(
        self, orders: list[dict[str, dict[str, object]]]
    ) -> "TemporaryOrdersSection":
        """依次新增列表中尚不存在的配置医嘱，避免重跑产生重复数据。"""
        for order in orders:
            order_name = str(order["fields"]["order_name"])
            if self.has_order_name(order_name):
                continue
            existing_ids = self._get_order_ids()
            expected_count = self._all_order_checkboxes().count() + 1
            self.open_add_order()
            dialog = self.order_dialog.wait_for_open()
            dialog.fill_order(order["fields"])
            dialog.expect_readonly_values(order.get("expected", {}))
            dialog.confirm()
            self._wait_for_new_order(existing_ids, expected_count)
        return self

    def has_order_name(self, order_name: str) -> bool:
        """等待临时医嘱列表回填，并判断是否已有指定名称。"""
        matching_row = (
            self._order_checkboxes()
            .locator("xpath=ancestor::tr[1]")
            .filter(
                has_text=re.compile(
                    rf"{re.escape(order_name)}(?=\s|\(|$)"
                )
            )
            .first
        )
        try:
            matching_row.wait_for(state="visible", timeout=1_500)
        except PlaywrightTimeoutError:
            return False
        return True

    def open_order_template(self) -> "TemporaryOrdersSection":
        """打开临时医嘱模板。"""
        self._click_action("医嘱模板")
        return self

    def execute_selected(self) -> "TemporaryOrdersSection":
        """执行当前勾选的临时医嘱。"""
        self._click_action("执行医嘱")
        return self

    def _order_checkboxes(self):
        """返回临时医嘱列表中的可见业务复选框。"""
        return self._section_table().locator(".tx_yz_checkbox:visible")

    def _all_order_checkboxes(self):
        """返回带稳定医嘱 ID 的可见业务复选框。"""
        return self._section_table().locator(
            ".tx_yz_checkbox[data-yzid]:visible"
        )

    def _get_order_ids(self) -> set[str]:
        """读取当前列表中全部带稳定标识的临时医嘱 ID。"""
        return {
            order_id
            for checkbox in self._all_order_checkboxes().all()
            if (order_id := checkbox.get_attribute("data-yzid"))
        }

    def _wait_for_new_order(
        self, existing_ids: set[str], expected_count: int
    ) -> None:
        """等待新增医嘱异步回填列表，并确认出现新的业务 ID。"""
        expect(self._all_order_checkboxes()).to_have_count(
            expected_count, timeout=10_000
        )
        if not self._get_order_ids() - existing_ids:
            raise AssertionError("新增临时医嘱后列表未出现新的 data-yzid")

    def get_unexecuted_order_ids(self) -> list[str]:
        """快照当前所有执行时间为空的临时医嘱 ID。"""
        checkboxes = self._section_table().locator(
            '.tx_yz_checkbox[data-zxsj=""]:visible'
        )
        order_ids = []
        for checkbox in checkboxes.all():
            order_id = checkbox.get_attribute("data-yzid")
            if not order_id:
                raise AssertionError("发现未执行临时医嘱缺少 data-yzid")
            order_ids.append(order_id)
        return order_ids

    def _clear_order_selection(self) -> None:
        """清除临时医嘱列表中的旧勾选，确保每次只操作一条。"""
        for checkbox in self._order_checkboxes().all():
            if checkbox.is_checked():
                checkbox.uncheck()

    def _order_checkbox_by_id(self, order_id: str):
        """按快照 ID 返回对应临时医嘱复选框。"""
        return self._section_table().locator(
            f'.tx_yz_checkbox[data-yzid="{order_id}"]:visible'
        )

    def open_execution_dialog(
        self, order_id: str
    ) -> TemporaryOrderExecutionDialog:
        """勾选指定医嘱并打开血液透析 > 临时医嘱 > 执行医嘱弹窗。"""
        self._clear_order_selection()
        self._order_checkbox_by_id(order_id).check()
        self.execute_selected()
        return self.execution_dialog.wait_for_open()

    def execute_all_unexecuted(
        self, data: dict[str, str]
    ) -> "TemporaryOrdersSection":
        """按初始 ID 快照逐条执行全部未执行临时医嘱。"""
        for order_id in self.get_unexecuted_order_ids():
            dialog = self.open_execution_dialog(order_id)
            dialog.fill_execution(data).execute()
            expect(self._order_checkbox_by_id(order_id)).to_have_attribute(
                "data-zxsj", re.compile(r".+")
            )
        return self

    def are_all_executed(self) -> bool:
        """确认临时医嘱列表中已不存在待执行的医嘱。"""
        return not self.get_unexecuted_order_ids()

    def check_selected(self) -> "TemporaryOrdersSection":
        """核对当前勾选的临时医嘱。"""
        self._click_action("核对医嘱")
        return self

    def delete_selected(self) -> "TemporaryOrdersSection":
        """删除当前勾选的临时医嘱。"""
        self._click_action("删除")
        return self
