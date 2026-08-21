from pathlib import Path

import pytest
import yaml

from pages.login_page import LoginPage


LOGIN_DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "login_data.yaml"


@pytest.mark.critical
@pytest.mark.no_auth_state
def test_login_redirects_to_the_success_page(page):
    """验证有效账号完成登录并选择角色后跳转至透析管理页面。"""
    # 从测试数据文件读取账号、密码和角色信息。
    with LOGIN_DATA_FILE.open(encoding="utf-8") as login_data_file:
        login_data = yaml.safe_load(login_data_file)

    # 依次完成登录、角色选择，并等待页面跳转。
    login_page = LoginPage(page).open()
    login_page.login(login_data["username"], login_data["password"])
    login_page.select_role(login_data["role"])
    login_page.wait_for_success_page()

    # 确认浏览器当前地址为登录成功后的透析管理页面。
    assert page.url == LoginPage.SUCCESS_URL
