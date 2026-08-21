from playwright.sync_api import expect

from pages.base_page import BasePage
from pages.login_page import LoginPage


class HemodialysisPage(BasePage):
    """封装血液透析一级模块的入口、模块标识和顶部业务菜单。"""

    # 明确标识该页面对象属于血液透析模块，供测试和后续页面对象复用。
    MODULE_NAME = "血液透析"
    PAGE_TITLE = "透析单"

    @property
    def module_name(self) -> str:
        """返回页面对象所属的业务模块名称。"""
        return self.MODULE_NAME

    def open(self) -> "HemodialysisPage":
        """打开主任登录态默认进入的透析单页面。"""
        self.navigate(LoginPage.SUCCESS_URL)
        return self

    def is_loaded(self) -> bool:
        """确认透析单标题和血液透析一级菜单均已显示。"""
        expect(self.page.get_by_text(self.MODULE_NAME, exact=True)).to_be_visible()
        return self.get_title() == self.PAGE_TITLE

    def get_top_level_modules(self) -> list[str]:
        """返回页面顶部可见的一级业务模块名称。"""
        return self.page.get_by_role("list").first.get_by_role("listitem").all_inner_texts()
