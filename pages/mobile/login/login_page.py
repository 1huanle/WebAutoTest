import re
from collections.abc import Sequence

from playwright.sync_api import Page, expect

from .base_page import BasePage


class LoginPage(BasePage):
    """云净血透管理系统移动端正常账号登录页。"""

    DEFAULT_LOGIN_URL = (
        "https://yunjingzhi.com/yunjingservice/login.jsp?origin=txjl_m"
    )
    DEFAULT_SUCCESS_PATHS = (
        "/yunjingservice/txform/mtxform.shtml",
        "/yunjingservice/txform/mtxform_doctor.shtml",
    )

    USERNAME_INPUT = "#userid"
    PASSWORD_INPUT = "#userpwd"
    LOGIN_BUTTON = "#login-btn"

    def __init__(
        self,
        page: Page,
        login_url: str = DEFAULT_LOGIN_URL,
        success_paths: Sequence[str] = DEFAULT_SUCCESS_PATHS,
    ) -> None:
        super().__init__(page)
        self.login_url = login_url
        self.success_paths = tuple(success_paths)

    def open(self) -> "LoginPage":
        """打开移动端登录页面。"""
        self.navigate(self.login_url)
        return self

    def is_loaded(self) -> bool:
        """确认账号、密码和登录按钮均已显示。"""
        return all(
            self.locator(selector).is_visible()
            for selector in (
                self.USERNAME_INPUT,
                self.PASSWORD_INPUT,
                self.LOGIN_BUTTON,
            )
        )

    def fill_username(self, username: str) -> "LoginPage":
        """填写登录账号。"""
        self.fill(self.USERNAME_INPUT, username)
        return self

    def fill_password(self, password: str) -> "LoginPage":
        """填写登录密码。"""
        self.fill(self.PASSWORD_INPUT, password)
        return self

    def click_login(self) -> "LoginPage":
        """点击登录按钮提交账号密码。"""
        self.locator(self.LOGIN_BUTTON).click()
        return self

    def login(self, username: str, password: str) -> "LoginPage":
        """填写账号密码并提交正常登录流程。"""
        return self.fill_username(username).fill_password(password).click_login()

    def wait_for_success_page(self) -> "LoginPage":
        """等待跳转到普通或医生移动端透析页面。"""
        path_pattern = "(?:" + "|".join(
            re.escape(path.rstrip("/")) for path in self.success_paths
        ) + ")" + r"(?:\?.*)?(?:#.*)?$"
        url_pattern = re.compile(path_pattern)
        self.page.wait_for_url(url_pattern, wait_until="domcontentloaded")
        expect(self.page).to_have_url(url_pattern)
        return self
