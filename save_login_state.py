from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

from config.config import Config
from pages.pc.login_page import LoginPage
from utils.auth_state import STORAGE_STATE_FILE

def is_management_page_url(url: str) -> bool:
    """确认当前地址属于透析管理页面，允许系统附加查询参数。"""
    return urlparse(url).path == urlparse(LoginPage.SUCCESS_URL).path


def save_login_state() -> int:
    """等待用户手动登录后，将浏览器会话保存到本机状态文件。"""
    with sync_playwright() as playwright:
        browser_type = getattr(playwright, Config.BROWSER)
        browser = browser_type.launch(headless=False)
        context = browser.new_context(ignore_https_errors=True, locale="zh-CN")
        page = context.new_page()
        try:
            page.goto(LoginPage.LOGIN_URL, wait_until="domcontentloaded")
            input("请在浏览器中完成登录和角色选择，到达管理页后按回车保存登录状态：")

            STORAGE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            context.storage_state(path=str(STORAGE_STATE_FILE))
            print(f"登录状态已保存至：{STORAGE_STATE_FILE}")
            return 0
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    raise SystemExit(save_login_state())
