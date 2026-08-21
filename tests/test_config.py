from config.config import Config
from pages.login_page import LoginPage


def test_default_base_url_matches_dialysis_management_page():
    """验证框架默认基础地址指向登录后的透析管理页面。"""
    assert Config.BASE_URL == LoginPage.SUCCESS_URL


def test_environment_urls_cover_online_test_and_pre_release():
    """三个目标环境应映射到各自的透析管理地址。"""
    assert Config.ENVIRONMENT_URLS == {
        "online": "https://yunjingzhi.com/yunjingservice/user/txform.shtml",
        "test": "https://develop.yunjingzhi.com/yunjingservice/user/txform.shtml",
        "pre": "https://pre.yunjingzhi.com/yunjingservice/user/txform.shtml",
    }
