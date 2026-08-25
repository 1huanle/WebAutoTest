from playwright.sync_api import Locator, Page, expect


class PrescriptionModal:
    """医生端透析处方页面内的 Bootstrap modal。"""

    MODAL_SELECTOR = ".modal:visible"

    def __init__(self, page: Page) -> None:
        self.page = page

    def root(self) -> Locator:
        return self.page.locator(self.MODAL_SELECTOR).last

    def wait_for_open(self) -> "PrescriptionModal":
        expect(self.root()).to_be_visible()
        return self

    def is_open(self) -> bool:
        modal = self.root()
        return modal.count() > 0 and modal.is_visible()

    def get_title(self) -> str:
        title = self.root().locator(".back_title:visible").first
        expect(title).to_be_visible()
        return title.inner_text().strip()

    def field(self, name: str) -> Locator:
        field = self.root().locator(f'[name="{name}"]:visible').first
        expect(field).to_be_visible()
        return field

    def get_field_value(self, name: str) -> str:
        field = self.field(name)
        tag_name = field.evaluate("element => element.tagName.toLowerCase()")
        if tag_name in ("input", "select", "textarea"):
            return field.input_value().strip()
        return field.inner_text().strip()

    def get_options(self, name: str | None = None) -> list[str]:
        root = self.root()
        if name:
            return [
                text.strip()
                for text in self.field(name).locator("option").all_inner_texts()
                if text.strip()
            ]
        return [
            text.strip()
            for text in root.locator("li:visible, option:visible").all_inner_texts()
            if text.strip()
        ]

    def select_value(self, value: str, name: str | None = None) -> "PrescriptionModal":
        """按 select 选项或可见列表文本选择值。"""
        root = self.root()
        if name:
            field = self.field(name)
            field.select_option(label=value)
            return self

        selects = root.locator("select:visible")
        for select in selects.all():
            options = select.locator("option")
            if any(option.inner_text().strip() == value for option in options.all()):
                select.select_option(label=value)
                return self

        option = root.get_by_text(value, exact=True).filter(visible=True).last
        expect(option).to_be_visible()
        option.click()
        return self

    def fill_field(self, name: str, value: str) -> "PrescriptionModal":
        field = self.field(name)
        expect(field).to_be_editable()
        field.fill(str(value))
        return self

    def save(self) -> "PrescriptionModal":
        save = self.root().get_by_text("保存", exact=True).filter(visible=True).last
        expect(save).to_be_visible()
        save.click()
        return self

    def cancel(self) -> "PrescriptionModal":
        root = self.root()
        close = root.locator('[data-dismiss="modal"]:visible').first
        if close.count():
            close.click()
        else:
            back = root.get_by_text("返回", exact=True).filter(visible=True).last
            expect(back).to_be_visible()
            back.click()
        return self

    def is_closed(self) -> bool:
        return not self.is_open()
