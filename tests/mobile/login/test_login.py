import os
from pathlib import Path

import pytest
import yaml

from config.config import Config
from pages.mobile.login.login_page import LoginPage
from utils.auth_state import storage_state_path


LOGIN_DATA_FILE = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "mobile"
    / "login"
    / "login_data.example.yaml"
)


def _required_environment_value(name: str) -> str:
    value = os.getenv(name)
    if not value:
        pytest.fail(f"未配置移动端登录环境变量 {name}")
    return value


@pytest.fixture(scope="function")
def mobile_page(browser, playwright, request):
    """使用 iPhone 13 设备参数创建移动端测试页面。"""
    context_options = {
        **playwright.devices["iPhone 13"],
        "ignore_https_errors": True,
        "locale": "zh-CN",
        "timezone_id": "Asia/Shanghai",
        "record_video_dir": str(Config.VIDEO_DIR) if Config.RECORD_VIDEO else None,
    }
    state_file = storage_state_path(
        skip_auth_state=request.node.get_closest_marker("no_auth_state") is not None
    )
    if state_file:
        context_options["storage_state"] = state_file

    context = browser.new_context(**context_options)
    context.set_default_timeout(Config.DEFAULT_TIMEOUT)
    context.set_default_navigation_timeout(Config.NAVIGATION_TIMEOUT)
    page = context.new_page()
    try:
        yield page
    finally:
        report = getattr(request.node, "rep_call", None)
        if report and report.failed:
            screenshot_file = Path(Config.SCREENSHOT_DIR) / f"{request.node.name}.png"
            page.screenshot(path=str(screenshot_file), full_page=True)
        page.close()
        context.close()


@pytest.mark.smoke
@pytest.mark.no_auth_state
def test_mobile_login(mobile_page):
    """验证移动端账号密码登录成功并进入移动端透析页面。"""
    with LOGIN_DATA_FILE.open(encoding="utf-8") as data_file:
        test_data = yaml.safe_load(data_file)

    username = _required_environment_value(test_data["username_env"])
    password = _required_environment_value(test_data["password_env"])
    login_page = LoginPage(
        mobile_page,
        login_url=test_data["login_url"],
        success_paths=test_data["success_paths"],
    )

    login_page.open()
    assert login_page.is_loaded(), "移动端登录表单未完整显示"
    login_page.login(username, password)
    login_page.wait_for_success_page()
