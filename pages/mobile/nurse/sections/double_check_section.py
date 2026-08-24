from playwright.sync_api import expect

from .base_section import NurseSection


class DoubleCheckSection(NurseSection):
    SECTION_TITLE = "双人核对"

    def mark_group_correct(self, group_text: str) -> "DoubleCheckSection":
        label = self.root().get_by_text(group_text, exact=True).first
        expect(label).to_be_visible()
        checkbox = label.locator("xpath=ancestor::*[self::label or @role='group'][1]").get_by_role("checkbox")
        if not checkbox.count():
            checkbox = label.locator("xpath=.. ").get_by_role("checkbox")
        checkbox.first.check()
        return self
