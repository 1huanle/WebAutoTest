from playwright.sync_api import Locator, Page, expect


class OrderTypeMenu:
    """医生端添加医嘱时出现的类型选择层。"""

    SHADE_SELECTOR = ".choose_yz_shade:visible"
    NEW_ORDER_SELECTOR = "#add_yz_type1:visible"
    TEMPLATE_SELECTOR = "#add_yz_type2:visible"

    def __init__(self, page: Page) -> None:
        self.page = page

    def root(self) -> Locator:
        return self.page.locator(self.SHADE_SELECTOR).first

    def wait_for_open(self) -> "OrderTypeMenu":
        expect(self.root()).to_be_visible(timeout=10_000)
        return self

    def is_open(self) -> bool:
        root = self.root()
        return root.count() > 0 and root.is_visible()

    def get_options(self) -> list[str]:
        return [
            " ".join(text.split())
            for text in self.root().locator(".new_yz:visible, .template_yz:visible").all_inner_texts()
            if text.strip()
        ]

    def select_new_order(self) -> "OrderTypeMenu":
        option = self.page.locator(self.NEW_ORDER_SELECTOR).first
        expect(option).to_be_visible()
        option.click()
        return self

    def select_template(self) -> "OrderTypeMenu":
        option = self.page.locator(self.TEMPLATE_SELECTOR).first
        expect(option).to_be_visible()
        option.click()
        return self

    def cancel(self) -> "OrderTypeMenu":
        root = self.root()
        close = root.locator(".tx_yz_cancle:visible, [data-dismiss='modal']:visible").first
        if close.count():
            close.click()
        else:
            self.page.locator("#cancel_yz, .cancel_yz:visible").first.click()
        return self

    def is_closed(self) -> bool:
        return not self.is_open()
