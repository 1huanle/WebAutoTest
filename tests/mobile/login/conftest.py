from pathlib import Path

import pytest

from config.config import Config
from utils.auth_state import storage_state_path


@pytest.fixture(scope="function")
def mobile_page(browser, playwright, request):
    """使用 iPhone 13 设备参数创建无登录态的移动端页面。"""
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
