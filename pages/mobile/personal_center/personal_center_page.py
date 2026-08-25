import re

from playwright.sync_api import Locator, Page, expect

from .dialogs.signature_modal import SignatureModal


class PersonalCenterPage:
    """移动端通用个人中心页面对象，与具体角色页面保持独立。"""

    URL_PATH = "/yunjingservice/txform/mtxform_grzx.shtml"
    URL = f"https://yunjingzhi.com{URL_PATH}"
    PAGE_TITLE = "个人中心"

    HEADER_SELECTOR = "#mGrzxHeader"
    MENU_SELECTOR = "#mGrzxItems"
    MENU_ITEM_SELECTOR = ".item"
    USER_NAME_SELECTOR = ".header-b"
    AVATAR_SELECTOR = "#txgrzx_yjuser_avatar"
    AVATAR_UPLOAD_SELECTOR = "#page_grzx_upload_input"
    SIGNATURE_IMAGE_SELECTOR = "#user_sign_img"
    LOGOUT_SELECTOR = "#tx_logout_div"

    MENU_NAMES = {
        "myWorkTime": "医护排班",
        "myShare": "我的案例分享",
        "myPatient": "我的患者",
        "myhzchangepbjl": "调班申请",
        "mySst": "我的肾世图",
        "myAccount": "我的账号",
        "CAAuth": "CA实名认证",
    }

    def __init__(self, page: Page) -> None:
        self.page = page
        self.signature_modal = SignatureModal(page)
        self.modal = self.signature_modal

    def navigate(self, url: str) -> "PersonalCenterPage":
        self.page.goto(url, wait_until="domcontentloaded")
        return self

    def open(self) -> "PersonalCenterPage":
        """打开通用个人中心页面并等待目标路径。"""
        self.navigate(self.URL)
        self.page.wait_for_url(re.compile(rf"{re.escape(self.URL_PATH)}(?:\?.*)?(?:#.*)?$"))
        return self

    def is_loaded(self) -> bool:
        expect(self.page).to_have_title(self.PAGE_TITLE)
        expect(self.page.locator(self.HEADER_SELECTOR)).to_be_visible()
        expect(self.page.locator(f"{self.MENU_SELECTOR} {self.MENU_ITEM_SELECTOR}:visible").first).to_be_visible()
        return True

    def get_title(self) -> str:
        return self.page.title()

    @staticmethod
    def _text(locator: Locator) -> str:
        return " ".join(locator.inner_text().split())

    @staticmethod
    def _numeric_text(locator: Locator) -> str:
        return PersonalCenterPage._text(locator)

    def get_user_name(self) -> str:
        locator = self.page.locator(f"{self.HEADER_SELECTOR} {self.USER_NAME_SELECTOR}:visible").first
        expect(locator).to_be_visible()
        return self._text(locator)

    def get_avatar_src(self) -> str:
        avatar = self.page.locator(f"{self.HEADER_SELECTOR} {self.AVATAR_SELECTOR}:visible").first
        expect(avatar).to_be_visible()
        return avatar.get_attribute("src") or ""

    def get_points(self) -> str:
        points = self.page.locator(f"{self.HEADER_SELECTOR} .store-num:visible").first
        expect(points).to_be_visible()
        return self._numeric_text(points)

    def get_signed_days(self) -> str:
        days = self.page.locator(f"{self.HEADER_SELECTOR} .day:visible").first
        expect(days).to_be_visible()
        return self._numeric_text(days)

    def get_ca_auth_status(self) -> str:
        status = self.page.locator(f"{self.MENU_SELECTOR} #CAAuth .caauthflag:visible").first
        return self._text(status) if status.count() else ""

    def get_profile_info(self) -> dict[str, str]:
        header = self.page.locator(self.HEADER_SELECTOR).first
        expect(header).to_be_visible()
        return {
            "user_name": self.get_user_name(),
            "avatar_src": self.get_avatar_src(),
            "points": self.get_points(),
            "signed_days": self.get_signed_days(),
            "ca_auth_status": self.get_ca_auth_status(),
            "text": self._text(header),
        }

    def _menu_item(self, name_or_id: str) -> Locator:
        value = str(name_or_id)
        menu = self.page.locator(f"{self.MENU_SELECTOR} {self.MENU_ITEM_SELECTOR}:visible")
        if value in self.MENU_NAMES:
            item = self.page.locator(f"{self.MENU_SELECTOR} #{value}:visible").first
        else:
            item = menu.filter(has_text=value).first
        expect(item).to_be_visible()
        return item

    def get_menu_items(self) -> list[dict[str, str]]:
        items = []
        for item in self.page.locator(f"{self.MENU_SELECTOR} {self.MENU_ITEM_SELECTOR}:visible").all():
            item_id = item.get_attribute("id") or ""
            auth = item.locator(".caauthflag:visible").first
            auth_text = self._text(auth) if auth.count() else ""
            text = self._text(item)
            if auth_text:
                text = text.replace(auth_text, "").strip()
            items.append({
                "id": item_id,
                "name": self.MENU_NAMES.get(item_id, text),
                "ca_auth_status": auth_text,
                "text": self._text(item),
            })
        return items

    def get_menu_names(self) -> list[str]:
        return [str(item["name"]) for item in self.get_menu_items()]

    def get_visible_actions(self) -> list[str]:
        actions = self.get_menu_names()
        if self.page.locator(f"{self.SIGNATURE_IMAGE_SELECTOR}:visible").count():
            actions.append("签名")
        if self.page.locator(f"{self.LOGOUT_SELECTOR}:visible").count():
            actions.append("退出登录")
        return actions

    def open_menu(self, name_or_id: str) -> "PersonalCenterPage":
        """按菜单 ID 或业务文本显式打开个人中心菜单。"""
        self._menu_item(name_or_id).click()
        return self

    def go_back(self) -> "PersonalCenterPage":
        back = self.page.locator(f"{self.HEADER_SELECTOR} a.back_a:visible").first
        expect(back).to_be_visible()
        back.click()
        return self

    def upload_avatar(self, path: str) -> "PersonalCenterPage":
        upload = self.page.locator(self.AVATAR_UPLOAD_SELECTOR).first
        expect(upload).to_be_attached()
        upload.set_input_files(path)
        return self

    def open_signature(self) -> SignatureModal:
        image = self.page.locator(f"{self.SIGNATURE_IMAGE_SELECTOR}:visible").first
        expect(image).to_be_visible()
        image.click()
        return self.signature_modal.wait_for_open()

    def logout(self) -> "PersonalCenterPage":
        button = self.page.locator(f"{self.LOGOUT_SELECTOR}:visible").first
        expect(button).to_be_visible()
        button.click()
        return self
