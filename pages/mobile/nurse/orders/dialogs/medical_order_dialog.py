from playwright.sync_api import Locator, Page, expect

from ...dialogs.layui_iframe_dialog import LayuiIframeDialog


class MedicalOrderDialog(LayuiIframeDialog):
    """移动端医嘱新增/修改 iframe 弹窗。"""

    TITLE = "医嘱信息"
    TITLE_ALIASES = ("临时医嘱", "长期医嘱", "新增医嘱", "修改医嘱")

    def field(self, name: str) -> Locator:
        """返回弹窗 iframe 内按 name 或 id 定位的可见字段。"""
        return self.frame().locator(
            f'[name="{name}"]:visible, #{name}:visible'
        ).first

    def get_field_value(self, name: str) -> str:
        field = self.field(name)
        expect(field).to_be_visible()
        tag_name = field.evaluate("element => element.tagName.toLowerCase()")
        if tag_name in ("input", "select", "textarea"):
            return field.input_value()
        return field.inner_text().strip()

    def fill_field(self, name: str, value: str) -> "MedicalOrderDialog":
        field = self.field(name)
        expect(field).to_be_visible()
        expect(field).to_be_editable()
        tag_name = field.evaluate("element => element.tagName.toLowerCase()")
        if tag_name == "select":
            field.select_option(label=str(value))
        else:
            field.fill(str(value))
        return self

    def fill_fields(self, values: dict[str, str]) -> "MedicalOrderDialog":
        for name, value in values.items():
            self.fill_field(name, value)
        return self

    def confirm(self) -> "MedicalOrderDialog":
        button = self._action_button("确认", "确定", "保存")
        button.click()
        return self

    def cancel(self) -> "MedicalOrderDialog":
        self._action_button("取消", "关闭").click()
        return self

    def _action_button(self, *names: str) -> Locator:
        frame = self.frame()
        for name in names:
            button = frame.get_by_role("button", name=name, exact=True)
            if button.count() and button.first.is_visible():
                return button.first
        raise AssertionError(f"医嘱弹窗未找到操作按钮: {names}")
