from playwright.sync_api import Locator, Page, expect


class NurseSection:
    """移动端透析业务分区的通用定位和显式操作。"""

    SECTION_TITLE = ""

    def __init__(self, page: Page) -> None:
        self.page = page

    def title(self) -> Locator:
        return self.page.get_by_text(self.SECTION_TITLE, exact=True).filter(visible=True).first

    def root(self) -> Locator:
        title = self.title()
        scoped = title.locator(
            "xpath=ancestor::*[self::table or @role='region' or "
            "contains(@class,'section') or contains(@class,'card')][1]"
        )
        return scoped.first if scoped.count() else title.locator("xpath=..").first

    def is_visible(self) -> bool:
        expect(self.title()).to_be_visible()
        return True

    def field(self, name: str) -> Locator:
        return self.root().locator(f'[name="{name}"]:visible, #{name}:visible').first

    def fill_fields(self, values: dict[str, str]) -> "NurseSection":
        for name, value in values.items():
            field = self.field(name)
            expect(field).to_be_visible()
            if field.evaluate("el => el.tagName.toLowerCase()") == "select":
                field.select_option(label=value)
            else:
                field.fill(value)
        return self

    def click_action(self, *names: str) -> "NurseSection":
        for name in names:
            button = self.root().get_by_role("button", name=name, exact=True)
            if button.count() and button.first.is_visible():
                button.first.click()
                return self
        raise AssertionError(f"分区 {self.SECTION_TITLE} 未找到操作按钮: {names}")

    def confirm(self) -> "NurseSection":
        return self.click_action("确认")

    def is_confirmed(self) -> bool:
        status = self.root().get_by_text("未确认", exact=True).filter(visible=True)
        return not status.count()

    def get_visible_actions(self) -> list[str]:
        return [text.strip() for text in self.root().get_by_role("button").all_inner_texts() if text.strip()]

    def get_visible_field_labels(self) -> list[str]:
        return [
            " ".join(text.split())
            for text in self.root().get_by_role("cell").all_inner_texts()
            if text.strip().endswith((":", "："))
        ]
