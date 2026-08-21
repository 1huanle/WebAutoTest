# LoginPage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为云净血透管理系统登录页提供可复用、带中文注释的 pytest-playwright 页面对象。

**Architecture:** 新建 `LoginPage` 并继承现有 `BasePage`，将登录 URL 和 CSS 定位器集中在类内。页面对象提供基础填写和点击操作，以及组合式 `login` 方法；测试仅验证页面加载和字段填写，不使用真实凭据或提交表单。

**Tech Stack:** Python 3、pytest、pytest-playwright、同步 Playwright API。

---

### Task 1: 定义登录页测试契约

**Files:**
- Create: `C:/Users/dev21/Desktop/webtest/tests/test_login_page.py`

- [ ] **Step 1: 写入失败测试**

```python
import pytest

from pages.login_page import LoginPage


@pytest.mark.smoke
class TestLoginPage:
    def test_login_page_loads(self, page):
        login_page = LoginPage(page).open()

        assert login_page.is_loaded()

    def test_can_fill_login_credentials(self, page):
        login_page = LoginPage(page).open()

        login_page.fill_username("test_user").fill_password("test_password")

        assert page.locator(LoginPage.USERNAME_INPUT).input_value() == "test_user"
        assert page.locator(LoginPage.PASSWORD_INPUT).input_value() == "test_password"
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `pytest tests/test_login_page.py -v`

Expected: FAIL，错误原因为 `ModuleNotFoundError: No module named 'pages.login_page'`。

### Task 2: 实现 LoginPage 页面对象

**Files:**
- Create: `C:/Users/dev21/Desktop/webtest/pages/login_page.py`
- Test: `C:/Users/dev21/Desktop/webtest/tests/test_login_page.py`

- [ ] **Step 1: 实现最小页面对象**

```python
from .base_page import BasePage


class LoginPage(BasePage):
    """云净血透管理系统登录页的页面对象。"""

    LOGIN_URL = "https://yunjingzhi.com/yunjingservice/login.jsp?origin=txjl"

    # 页面使用固定 ID，优先作为稳定定位器维护。
    USERNAME_INPUT = "#userid"
    PASSWORD_INPUT = "#userpwd"
    LOGIN_BUTTON = "#login-btn"

    def open(self) -> "LoginPage":
        """打开登录页面。"""
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
        """组合执行账号填写、密码填写和登录提交。"""
        return self.fill_username(username).fill_password(password).click_login()

    def is_loaded(self) -> bool:
        """确认登录所需的账号、密码和登录按钮均可见。"""
        return all(
            self.locator(selector).is_visible()
            for selector in (self.USERNAME_INPUT, self.PASSWORD_INPUT, self.LOGIN_BUTTON)
        )
```

- [ ] **Step 2: 运行新增测试并确认通过**

Run: `pytest tests/test_login_page.py -v`

Expected: PASS，2 passed。

- [ ] **Step 3: 复查页面对象注释与范围**

确认类说明、稳定定位器说明和 `login` 组合方法说明均为中文；不保存测试账号或密码，也不改动 `BasePage`。

### Task 3: 回归验证

**Files:**
- Modify: `C:/Users/dev21/Desktop/webtest/pages/login_page.py`
- Modify: `C:/Users/dev21/Desktop/webtest/tests/test_login_page.py`

- [ ] **Step 1: 运行完整测试集**

Run: `pytest -v`

Expected: PASS，现有小说页面测试与新增登录页测试均通过。

- [ ] **Step 2: 检查变更范围**

Run: `rg --files pages tests docs/superpowers`

Expected: 仅新增 `pages/login_page.py`、`tests/test_login_page.py`、设计说明与本计划；既有页面对象和配置文件未被修改。
