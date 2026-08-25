import re
from collections.abc import Mapping
from urllib.parse import urlencode

from playwright.sync_api import Locator, Page, expect

from ..base_page import BasePage
from .dialogs.double_check_modal import DoubleCheckSelectModal, SameNurseWarningModal


class DoubleCheckPage(BasePage):
    """医生端独立双人核对页面。"""

    URL_PATH = "/yunjingservice/txform/mtxform_doublecheck.shtml"
    URL = f"https://yunjingzhi.com{URL_PATH}"
    PAGE_TITLE = "双人核对"
    FORM_SELECTOR = "#tx_form"
    PATIENT_INFO_SELECTOR = ".page_confirm_table"
    CONFIRM_BUTTON_SELECTOR = "button.head_confirm_btn"
    CHECKER_FIELD = "tx_hd_nurse"
    CHECK_TIME_FIELD = "tx_check_time"
    SAME_NURSE_WARNING = SameNurseWarningModal.MESSAGE

    GROUPS = {
        "dialysis_items": {
            "title": "透析物品核查",
            "indicator": "tx_touXiWuPin_indicator",
            "error": "tx_touXiWuPin_error",
        },
        "dialysis_parameters": {
            "title": "透析参数核查",
            "indicator": "tx_touXiCanShu_indicator",
            "error": "tx_touXiCanShu_error",
        },
        "vascular_access": {
            "title": "血管通路核查",
            "indicator": "tx_xueGuanTongLu_indicator",
            "error": "tx_xueGuanTongLu_error",
        },
        "pipeline_connection": {
            "title": "管道连接核查",
            "indicator": "tx_guanDao_indicator",
            "error": "tx_guanDao_error",
        },
    }

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.select_modal = DoubleCheckSelectModal(page)
        self.modal = self.select_modal
        self.warning_modal = SameNurseWarningModal(page)

    def open(self, tx_number: str, tx_name: str, tx_time: str) -> "DoubleCheckPage":
        query = urlencode({"tx_number": tx_number, "tx_name": tx_name, "tx_time": tx_time})
        self.navigate(f"{self.URL}?{query}")
        self.wait_for_paths((self.URL_PATH,))
        return self

    def root(self) -> Locator:
        return self.page.locator(self.FORM_SELECTOR).first

    def is_loaded(self) -> bool:
        expect(self.page).to_have_title(self.PAGE_TITLE)
        expect(self.root()).to_be_visible()
        expect(self.root().locator(self.PATIENT_INFO_SELECTOR + ":visible")).to_be_visible()
        expect(self._status_locator()).to_be_visible()
        expect(self.page.locator(self.CONFIRM_BUTTON_SELECTOR + ":visible")).to_be_visible()
        return True

    def get_title(self) -> str:
        return self.page.title()

    @staticmethod
    def _match(text: str, pattern: str) -> str:
        match = re.search(pattern, text)
        return match.group(1).strip() if match else ""

    def get_patient_info(self) -> dict[str, str]:
        table = self.root().locator(self.PATIENT_INFO_SELECTOR + ":visible").first
        expect(table).to_be_visible()
        text = " ".join(table.inner_text().split())
        name = table.locator(".head_user_a:visible").first
        mode = re.search(r"\](HDF|HD|HF|CRRT|透析)\b", text) or re.search(
            r"(?:透析方式|模式)\s*[：:]?\s*(HDF|HD|HF|CRRT|透析)\b", text
        )
        name_text = name.inner_text().strip() if name.count() else self._match(
            text, r"姓名[：:]([^\s]+)"
        )
        return {
            "name": name_text,
            "dialysis_number": self._match(text, r"透析号[：:]([^\]\s]+)"),
            "machine_number": self._match(text, r"机号[：:]([^\]\s]+)"),
            "dialysis_mode": mode.group(1) if mode else "",
            "text": text,
        }

    def _status_locator(self) -> Locator:
        return self.root().get_by_text(re.compile(r"^(?:已确认|未确认)$")).filter(visible=True).first

    def get_status(self) -> str:
        status = self._status_locator()
        expect(status).to_be_visible()
        return status.inner_text().strip()

    def is_confirmed(self) -> bool:
        return self.get_status() == "已确认"

    def is_currently_confirmed(self) -> bool:
        return self.root().get_by_text("未确认", exact=True).filter(visible=True).count() == 0

    def _field(self, name: str) -> Locator:
        field = self.root().locator(f'[name="{name}"]:visible').first
        if field.count():
            return field
        return self.root().locator(f'[name="{name}"]').first

    @staticmethod
    def _value(field: Locator) -> str:
        tag = field.evaluate("element => element.tagName.toLowerCase()")
        if tag in ("input", "select", "textarea"):
            return field.input_value().strip()
        return " ".join(field.inner_text().split())

    def get_checker(self) -> str:
        field = self._field(self.CHECKER_FIELD)
        expect(field).to_be_visible()
        if field.evaluate("element => element.tagName.toLowerCase()") == "select":
            selected = field.locator("option:checked").first
            return selected.inner_text().strip() if selected.count() else self._value(field)
        return self._value(field)

    def get_check_time(self) -> str:
        field = self._field(self.CHECK_TIME_FIELD)
        expect(field).to_be_visible()
        return self._value(field)

    def _group_config(self, group: str) -> Mapping[str, str]:
        try:
            return self.GROUPS[group]
        except KeyError as exc:
            raise KeyError(f"不支持的医生端双人核对分组: {group}") from exc

    def _group(self, group: str) -> Locator:
        config = self._group_config(group)
        title = self.root().get_by_text(config["title"], exact=True).filter(visible=True).first
        expect(title).to_be_visible()
        table = title.locator("xpath=ancestor::table[1]")
        if table.count():
            return table
        return title.locator("xpath=ancestor::*[self::section or self::div][1]")

    def get_group_names(self) -> list[str]:
        return [config["title"] for config in self.GROUPS.values() if self._group_visible(config["title"])]

    def _group_visible(self, title: str) -> bool:
        locator = self.root().get_by_text(title, exact=True).filter(visible=True)
        return locator.count() > 0

    def get_detail_items(self, group: str) -> list[str]:
        section = self._group(group)
        indicator_name = self._group_config(group)["indicator"]
        values = []
        for checkbox in section.locator('input[type="checkbox"]').all():
            if checkbox.get_attribute("name") == indicator_name:
                continue
            checkbox_id = checkbox.get_attribute("id")
            label = (
                section.locator(f'label[for="{checkbox_id}"]').first
                if checkbox_id
                else checkbox.locator("xpath=ancestor::td[1]").first
            )
            if not label.count():
                label = checkbox.locator("xpath=ancestor::td[1]").first
            text = " ".join(label.inner_text().split()) if label.count() else ""
            if not text:
                row = checkbox.locator("xpath=ancestor::tr[1]")
                text = " ".join(row.inner_text().split()) if row.count() else ""
            if text and text not in values:
                values.append(text)
        return values

    def _detail_checkbox(self, group: str, detail: str) -> Locator:
        section = self._group(group)
        label = section.get_by_text(detail, exact=True).last
        expect(label).to_be_visible()
        for selector in (
            "xpath=preceding-sibling::input[@type='checkbox'][1]",
            "xpath=ancestor::td[1]/preceding-sibling::td[1]//input[@type='checkbox']",
            "xpath=ancestor::td[1]//input[@type='checkbox']",
            "xpath=ancestor::tr[1]//input[@type='checkbox']",
        ):
            checkbox = label.locator(selector).first
            if checkbox.count():
                return checkbox
        raise AssertionError(f"未找到双人核对明细复选框: {group}/{detail}")

    def is_detail_checked(self, group: str, detail: str) -> bool:
        return self._detail_checkbox(group, detail).is_checked()

    def get_group_status(self, group: str) -> str:
        config = self._group_config(group)
        indicator = self._group(group).locator(f'[name="{config["indicator"]}"]').first
        expect(indicator).to_be_visible()
        return "正确" if indicator.is_checked() else "差错"

    def get_group_info(self, group: str) -> dict[str, object]:
        config = self._group_config(group)
        section = self._group(group)
        error = section.locator(f'[name="{config["error"]}"]').first
        return {
            "name": group,
            "title": config["title"],
            "status": self.get_group_status(group),
            "error": self._value(error) if error.count() else "",
            "details": [
                {"text": detail, "checked": self.is_detail_checked(group, detail)}
                for detail in self.get_detail_items(group)
            ],
            "text": " ".join(section.inner_text().split()),
        }

    def get_groups(self) -> dict[str, dict[str, object]]:
        return {group: self.get_group_info(group) for group in self.GROUPS if self._group_visible(self.GROUPS[group]["title"])}

    def set_detail_checked(self, group: str, detail: str, checked: bool = True) -> "DoubleCheckPage":
        checkbox = self._detail_checkbox(group, detail)
        if checked:
            checkbox.check()
        else:
            checkbox.uncheck()
        return self

    def mark_group_correct(self, group: str) -> "DoubleCheckPage":
        config = self._group_config(group)
        indicator = self._group(group).locator(f'[name="{config["indicator"]}"]:visible').first
        expect(indicator).to_be_visible()
        indicator.check()
        return self

    def mark_group_error(self, group: str, message: str) -> "DoubleCheckPage":
        config = self._group_config(group)
        section = self._group(group)
        indicator = section.locator(f'[name="{config["indicator"]}"]:visible').first
        error = section.locator(f'[name="{config["error"]}"]:visible').first
        expect(indicator).to_be_visible()
        expect(error).to_be_visible()
        indicator.uncheck()
        error.fill(str(message))
        return self

    def open_checker_selector(self) -> DoubleCheckSelectModal:
        field = self._field(self.CHECKER_FIELD)
        row = field.locator("xpath=ancestor::tr[1]")
        link = row.locator('a:has(img[alt="选择"]), a:has(img.modal_select_arrows)').first
        expect(link).to_be_visible()
        link.click()
        return self.select_modal.wait_for_open()

    def select_checker(self, name: str) -> "DoubleCheckPage":
        self.open_checker_selector().select_value(name).save()
        return self

    def confirm(self) -> "DoubleCheckPage":
        button = self.page.locator(self.CONFIRM_BUTTON_SELECTOR + ":visible").first
        expect(button).to_be_visible()
        button.click()
        return self

    def get_visible_actions(self) -> list[str]:
        return [
            " ".join(text.split())
            for text in self.root().locator("button:visible, a:visible, img:visible").all_inner_texts()
            if text.strip()
        ]
