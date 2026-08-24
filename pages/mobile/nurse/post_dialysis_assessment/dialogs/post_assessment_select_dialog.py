from playwright.sync_api import Locator, Page, expect


class PostAssessmentSelectDialog:
    """透后评估页面内的选项选择弹窗。"""

    DIALOG_SELECTOR = "dialog:visible"
    TITLE = "透后评估"

    def __init__(self, page: Page) -> None:
        self.page = page

    def root(self) -> Locator:
        return self.page.locator(self.DIALOG_SELECTOR).last

    def wait_for_open(self) -> "PostAssessmentSelectDialog":
        expect(self.root()).to_be_visible(timeout=10_000)
        return self

    def get_title(self) -> str:
        title = self.root().get_by_text(self.TITLE, exact=True).first
        return title.inner_text().strip() if title.count() else ""

    def get_options(self) -> list[str]:
        return [
            " ".join(text.split())
            for text in self.root().get_by_role("button").all_inner_texts()
            if text.strip()
        ]

    def select_option(self, label: str) -> "PostAssessmentSelectDialog":
        option = self.root().get_by_role("button", name=label, exact=True)
        expect(option).to_be_visible()
        option.click()
        return self

    def fill_custom_value(self, value: str) -> "PostAssessmentSelectDialog":
        textbox = self.root().get_by_role("textbox").last
        expect(textbox).to_be_visible()
        textbox.fill(value)
        return self

    def save(self) -> "PostAssessmentSelectDialog":
        button = self.root().get_by_text("保存", exact=True).last
        expect(button).to_be_visible()
        button.click()
        return self

    def back(self) -> "PostAssessmentSelectDialog":
        button = self.root().get_by_text("返回", exact=True).last
        expect(button).to_be_visible()
        button.click()
        return self

    def cancel(self) -> "PostAssessmentSelectDialog":
        return self.back()

    def is_closed(self) -> bool:
        expect(self.root()).to_be_hidden(timeout=10_000)
        return True
