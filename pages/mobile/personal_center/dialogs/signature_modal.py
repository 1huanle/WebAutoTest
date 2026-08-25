from playwright.sync_api import Locator, Page, expect


class SignatureModal:
    """个人中心签名编辑弹层。"""

    SELECTOR = "#signWrap"
    CANVAS_SELECTOR = "#signature canvas.jSignature"

    def __init__(self, page: Page) -> None:
        self.page = page

    def root(self) -> Locator:
        return self.page.locator(self.SELECTOR).first

    def wait_for_open(self) -> "SignatureModal":
        expect(self.root()).to_be_visible()
        return self

    def is_open(self) -> bool:
        return self.root().count() > 0 and self.root().is_visible()

    def clear(self) -> "SignatureModal":
        self.wait_for_open()
        self.page.evaluate(
            """() => {
                const target = window.jQuery && window.jQuery('#signature');
                if (target && typeof target.jSignature === 'function') {
                    target.jSignature('reset');
                }
            }"""
        )
        return self

    def save(self) -> "SignatureModal":
        button = self.root().locator("button.save-sign:visible").first
        expect(button).to_be_visible()
        button.click()
        return self

    def cancel(self) -> "SignatureModal":
        button = self.root().locator("button.cancel-sign:visible").first
        expect(button).to_be_visible()
        button.click()
        return self

    def close(self) -> "SignatureModal":
        close = self.root().locator("#closeSign:visible").first
        if close.count():
            close.click()
        else:
            self.cancel()
        return self
