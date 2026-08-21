# 角色登录测试 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 使用 `data` 中的测试账号完成登录、选择“主任”，并验证进入透析表单页面。

**Architecture:** 测试直接从 YAML 读取凭据与角色，避免在 Python 源码中保存敏感数据。`LoginPage` 扩展角色选择和成功页等待操作，测试通过页面对象完成外部登录流程并断言最终 URL。

**Tech Stack:** Python 3、pytest、pytest-playwright、PyYAML、同步 Playwright API。

---

### Task 1: 定义角色登录的失败测试

**Files:**
- Create: `C:/Users/dev21/Desktop/webtest/tests/test_login_flow.py`

- [ ] **Step 1: 写入失败测试**

```python
from pathlib import Path

import pytest
import yaml

from pages.login_page import LoginPage


def load_login_data() -> dict[str, str]:
    """读取被 Git 忽略的登录测试数据。"""
    data_file = Path(__file__).resolve().parent.parent / "data" / "login_data.yaml"
    return yaml.safe_load(data_file.read_text(encoding="utf-8"))


@pytest.mark.critical
def test_director_can_log_in(page):
    login_data = load_login_data()
    login_page = LoginPage(page).open().login(
        login_data["username"], login_data["password"]
    )

    login_page.select_role(login_data["role"]).wait_for_success_page()

    assert page.url == LoginPage.SUCCESS_URL
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `.\\.venv\\Scripts\\python.exe -m pytest tests\\test_login_flow.py -v`

Expected: FAIL，错误原因为 `data/login_data.yaml` 尚不存在。

### Task 2: 添加受保护的测试数据

**Files:**
- Create: `C:/Users/dev21/Desktop/webtest/data/login_data.yaml`
- Modify: `C:/Users/dev21/Desktop/webtest/.gitignore`
- Test: `C:/Users/dev21/Desktop/webtest/tests/test_login_flow.py`

- [ ] **Step 1: 创建 YAML 测试数据文件**

在 `data/login_data.yaml` 中写入用户在当前任务提供的测试账号和密码，并使用以下角色字段：

```yaml
role: "主任"
```

- [ ] **Step 2: 忽略凭据文件**

在 `.gitignore` 末尾添加：

```gitignore
data/login_data.yaml
```

- [ ] **Step 3: 运行测试并确认下一处失败**

Run: `.\\.venv\\Scripts\\python.exe -m pytest tests\\test_login_flow.py -v`

Expected: FAIL，错误原因为 `LoginPage` 尚未定义 `select_role` 或 `wait_for_success_page`。

### Task 3: 扩展 LoginPage 的角色选择操作

**Files:**
- Modify: `C:/Users/dev21/Desktop/webtest/pages/login_page.py`
- Test: `C:/Users/dev21/Desktop/webtest/tests/test_login_flow.py`

- [ ] **Step 1: 添加成功页常量和页面对象方法**

```python
    SUCCESS_URL = "https://yunjingzhi.com/yunjingservice/user/txform.shtml"

    def select_role(self, role: str) -> "LoginPage":
        """在登录后的角色选择框中选择指定角色。"""
        self.page.get_by_text(role, exact=True).click()
        return self

    def wait_for_success_page(self) -> "LoginPage":
        """等待跳转至透析表单页面。"""
        self.page.wait_for_url(self.SUCCESS_URL, wait_until="domcontentloaded")
        return self
```

- [ ] **Step 2: 运行角色登录测试并确认通过**

Run: `.\\.venv\\Scripts\\python.exe -m pytest tests\\test_login_flow.py -v`

Expected: PASS，1 passed，并且最终 URL 为 `LoginPage.SUCCESS_URL`。

- [ ] **Step 3: 复查敏感数据边界**

确认账号和密码只出现在 `data/login_data.yaml`，该路径位于 `.gitignore` 中，且测试输出未主动记录凭据。

### Task 4: 完整回归验证

**Files:**
- Modify: `C:/Users/dev21/Desktop/webtest/pages/login_page.py`
- Modify: `C:/Users/dev21/Desktop/webtest/tests/test_login_flow.py`

- [ ] **Step 1: 运行完整测试集**

Run: `.\\.venv\\Scripts\\python.exe -m pytest -v`

Expected: PASS，登录页基础测试、角色登录测试和既有小说测试均通过。

- [ ] **Step 2: 检查数据文件忽略规则**

Run: `Select-String -Path .gitignore -Pattern '^data/login_data\\.yaml$'`

Expected: 输出 `data/login_data.yaml`。
