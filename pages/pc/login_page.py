from .base_page import BasePage
from config.config import Config


class LoginPage(BasePage):
    """封装云净智透析管理系统登录页的定位器和交互操作。"""

    # 登录入口与登录成功后的透析管理页面地址。
    SUCCESS_URL = Config.BASE_URL
    LOGIN_URL = SUCCESS_URL.replace(
        "/user/txform.shtml", "/login.jsp?origin=txjl"
    )

    # 登录页使用固定 ID，作为稳定的页面元素定位器。
    USERNAME_INPUT = "#userid"
    PASSWORD_INPUT = "#userpwd"
    LOGIN_BUTTON = "#login-btn"

    def open(self) -> "LoginPage":
        """打开系统登录页面。"""
        self.navigate(self.LOGIN_URL)
        return self

    def fill_username(self, username: str) -> "LoginPage":
        """填写登录账号。"""
        self.fill(self.USERNAME_INPUT, username)
        return self

    def fill_password(self, password: str) -> "LoginPage":
        """填写登录密码。"""
        self.fill(self.PASSWORD_INPUT, password)
        return self

    def click_login(self) -> "LoginPage":
        """点击登录按钮提交当前表单。"""
        self.locator(self.LOGIN_BUTTON).click()
        return self

    def login(self, username: str, password: str) -> "LoginPage":
        """依次填写账号、密码并提交登录。"""
        return self.fill_username(username).fill_password(password).click_login()

    def select_role(self, role: str) -> "LoginPage":
        """选择登录后的角色。"""
        self.page.get_by_text(role, exact=True).click()
        return self

    def wait_for_success_page(self) -> "LoginPage":
        """等待页面跳转至透析管理页面。"""
        self.page.wait_for_url(self.SUCCESS_URL, wait_until="domcontentloaded")
        return self

    def is_loaded(self) -> bool:
        """确认账号、密码和登录按钮均已显示。"""
        return all(
            self.locator(selector).is_visible()
            for selector in (self.USERNAME_INPUT, self.PASSWORD_INPUT, self.LOGIN_BUTTON)
        )
