from save_login_state import is_management_page_url


def test_management_page_url_allows_query_parameters():
    assert is_management_page_url(
        "https://yunjingzhi.com/yunjingservice/user/txform.shtml?source=login"
    )
