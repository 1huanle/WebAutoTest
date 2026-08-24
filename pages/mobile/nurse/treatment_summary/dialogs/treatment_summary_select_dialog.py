from playwright.sync_api import Locator, Page, expect


class TreatmentSummarySelectDialog:
    """治疗小结页面内模板、人员和治疗方式选择弹窗。"""

    DIALOG_SELECTOR = "dialog:visible"

    def __init__(self, page: Page) -> None:
        self.page = page

    def root(self) -> Locator:
        return self.page.locator(self.DIALOG_SELECTOR).last

    def wait_for_open(self) -> "TreatmentSummarySelectDialog":
        expect(self.root()).to_be_visible(timeout=10_000)
        return self

    def get_title(self) -> str:
        cells = self.root().locator("table tr").first.locator("td")
        return cells.nth(1).inner_text().strip() if cells.count() > 1 else ""

    def get_options(self) -> list[str]:
        options = self.root().locator("button:visible, li:visible")
        return [
            " ".join(text.split())
            for text in options.all_inner_texts()
            if text.strip()
        ]

    def select_option(self, label: str) -> "TreatmentSummarySelectDialog":
        button = self.root().get_by_role("button", name=label, exact=True)
        if button.count() and button.first.is_visible():
            button.first.click()
            return self
        option = self.root().locator("li:visible").filter(has_text=label).last
        expect(option).to_be_visible()
        option.click()
        return self

    def fill_custom_value(self, value: str) -> "TreatmentSummarySelectDialog":
        textbox = self.root().get_by_role("textbox").last
        expect(textbox).to_be_visible()
        textbox.fill(value)
        return self

    def save(self) -> "TreatmentSummarySelectDialog":
        button = self.root().get_by_text("保存", exact=True).last
        expect(button).to_be_visible()
        button.click()
        return self

    def back(self) -> "TreatmentSummarySelectDialog":
        button = self.root().get_by_text("返回", exact=True).last
        expect(button).to_be_visible()
        button.click()
        return self

    def cancel(self) -> "TreatmentSummarySelectDialog":
        return self.back()

    def is_closed(self) -> bool:
        expect(self.root()).to_be_hidden(timeout=10_000)
        return True
