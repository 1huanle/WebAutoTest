from playwright.sync_api import Locator, Page, expect


class PreAssessmentModal:
    """医生端透前评估页面内的选择弹窗。"""

    MODAL_SELECTOR = "#select_Modal:visible"

    def __init__(self, page: Page) -> None:
        self.page = page

    def root(self) -> Locator:
        modal = self.page.locator(self.MODAL_SELECTOR).last
        if modal.count():
            return modal
        return self.page.locator(".modal:visible").last

    def wait_for_open(self) -> "PreAssessmentModal":
        expect(self.root()).to_be_visible(timeout=10_000)
        return self

    def is_open(self) -> bool:
        modal = self.root()
        return modal.count() > 0 and modal.is_visible()

    def get_title(self) -> str:
        root = self.root()
        title = root.locator(".back_title:visible, .modal-title:visible, h1:visible, h2:visible").first
        if title.count():
            return title.inner_text().strip()
        return ""

    def get_options(self) -> list[str]:
        root = self.root()
        texts = root.locator("li:visible, option:visible, button:visible").all_inner_texts()
        return [" ".join(text.split()) for text in texts if text.strip()]

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

    def select_value(self, value: str, name: str | None = None) -> "PreAssessmentModal":
        root = self.root()
        if name:
            field = self.field(name)
            tag_name = field.evaluate("element => element.tagName.toLowerCase()")
            if tag_name == "select":
                field.select_option(label=str(value))
                return self

        for select in root.locator("select:visible").all():
            if any(option.inner_text().strip() == str(value) for option in select.locator("option").all()):
                select.select_option(label=str(value))
                return self

        option = root.get_by_text(str(value), exact=True).filter(visible=True).last
        expect(option).to_be_visible()
        option.click()
        return self

    def fill_field(self, name: str, value: str) -> "PreAssessmentModal":
        field = self.field(name)
        expect(field).to_be_editable()
        field.fill(str(value))
        return self

    def save(self) -> "PreAssessmentModal":
        save = self.root().get_by_text("保存", exact=True).filter(visible=True).last
        expect(save).to_be_visible()
        save.click()
        return self

    def back(self) -> "PreAssessmentModal":
        root = self.root()
        back = root.get_by_text("返回", exact=True).filter(visible=True).last
        if back.count():
            back.click()
        else:
            close = root.locator('[data-dismiss="modal"]:visible').first
            expect(close).to_be_visible()
            close.click()
        return self

    def cancel(self) -> "PreAssessmentModal":
        return self.back()

    def is_closed(self) -> bool:
        return not self.is_open()
