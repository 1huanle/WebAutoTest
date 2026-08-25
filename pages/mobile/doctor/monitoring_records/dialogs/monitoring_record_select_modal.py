from playwright.sync_api import Locator, Page, expect


class MonitoringRecordSelectModal:
    """医生端监测记录页面共用的 #select_Modal 选择弹窗。"""

    MODAL_SELECTOR = "#select_Modal:visible"

    def __init__(self, page: Page) -> None:
        self.page = page

    def root(self) -> Locator:
        return self.page.locator(self.MODAL_SELECTOR).last

    def wait_for_open(self) -> "MonitoringRecordSelectModal":
        expect(self.root()).to_be_visible(timeout=10_000)
        return self

    def is_open(self) -> bool:
        modal = self.root()
        return modal.count() > 0 and modal.is_visible()

    def get_title(self) -> str:
        title = self.root().locator(".modal_select_title:visible").first
        return title.inner_text().strip() if title.count() else ""

    def get_options(self) -> list[str]:
        root = self.root()
        options = root.locator(
            ".modal_content li:visible, .modal_content label:visible, "
            ".modal_content button:visible, .modal_content option:visible"
        ).all_inner_texts()
        return [" ".join(text.split()) for text in options if text.strip()]

    def select_text(self, value: str) -> "MonitoringRecordSelectModal":
        option = self.root().get_by_text(value, exact=True).filter(visible=True).last
        expect(option).to_be_visible()
        option.click()
        return self

    def select_values(self, values: list[str]) -> "MonitoringRecordSelectModal":
        for value in values:
            self.select_text(value)
        return self

    def confirm(self) -> "MonitoringRecordSelectModal":
        button = self.root().locator("button.modal_confirm_button:visible").first
        expect(button).to_be_visible()
        button.click()
        return self

    def cancel(self) -> "MonitoringRecordSelectModal":
        close = self.root().locator("img.modal_close_pic:visible").first
        expect(close).to_be_visible()
        close.click()
        return self

    def close(self) -> "MonitoringRecordSelectModal":
        return self.cancel()

    def is_closed(self) -> bool:
        return not self.is_open()
