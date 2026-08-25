import re

from playwright.sync_api import FrameLocator, Locator, Page, expect


class MedicalOrderDialog:
    """医生端新增/修改医嘱使用的 Layui iframe 弹窗。"""

    DIALOG_SELECTOR = ".layui-layer:visible"
    TITLE_ALIASES = ("医嘱信息", "临时医嘱", "长期医嘱", "新增医嘱", "修改医嘱")

    def __init__(self, page: Page) -> None:
        self.page = page

    def root(self) -> Locator:
        pattern = re.compile("|".join(re.escape(value) for value in self.TITLE_ALIASES))
        return self.page.locator(self.DIALOG_SELECTOR).filter(has_text=pattern).last

    def wait_for_open(self) -> "MedicalOrderDialog":
        expect(self.root()).to_be_visible(timeout=10_000)
        return self

    def is_open(self) -> bool:
        root = self.root()
        return root.count() > 0 and root.is_visible()

    def frame(self) -> FrameLocator:
        return self.root().locator("iframe").content_frame

    def get_title(self) -> str:
        title = self.root().locator(".layui-layer-title:visible").first
        return title.inner_text().strip() if title.count() else ""

    def field(self, name: str) -> Locator:
        return self.frame().locator(f'[name="{name}"]:visible, #{name}:visible').first

    def get_field_value(self, name: str) -> str:
        field = self.field(name)
        expect(field).to_be_visible()
        tag_name = field.evaluate("element => element.tagName.toLowerCase()")
        if tag_name in ("input", "select", "textarea"):
            return field.input_value().strip()
        return field.inner_text().strip()

    def get_visible_fields(self) -> list[str]:
        return [
            name
            for name in self.frame().locator("input:visible, select:visible, textarea:visible").evaluate_all(
                "elements => elements.map(element => element.name || element.id).filter(Boolean)"
            )
            if name
        ]

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

    def fill_fields(self, values: dict[str, object]) -> "MedicalOrderDialog":
        for name, value in values.items():
            self.fill_field(name, str(value))
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
        raise AssertionError(f"医生端医嘱弹窗未找到操作按钮: {names}")

    def is_closed(self) -> bool:
        return not self.is_open()
