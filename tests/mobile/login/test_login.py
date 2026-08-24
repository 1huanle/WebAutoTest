import os
from pathlib import Path

import pytest
import yaml

from pages.mobile.login.login_page import LoginPage


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
