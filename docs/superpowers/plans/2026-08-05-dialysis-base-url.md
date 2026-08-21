# 透析管理地址配置 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将框架默认基础地址迁移至透析管理页，并移除旧站点的历史测试产物。

**Architecture:** `Config.BASE_URL` 继续是测试框架的唯一默认地址来源，`.env.example` 提供同一默认值。`LoginPage` 继续维护登录入口及登录成功后的管理页地址，配置测试通过 `LoginPage.SUCCESS_URL` 验证两者一致。

**Tech Stack:** Python 3.12、pytest、python-dotenv、Allure。

---

### Task 1: 配置默认地址

**Files:**
- Modify: `tests/test_config.py`
- Modify: `config/config.py`
- Modify: `.env.example`

- [ ] **Step 1: 写入失败的配置测试**

将 `tests/test_config.py` 改为：

```python
from config.config import Config
from pages.login_page import LoginPage


def test_default_base_url_matches_dialysis_management_page():
    assert Config.BASE_URL == LoginPage.SUCCESS_URL
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `pytest tests/test_config.py::test_default_base_url_matches_dialysis_management_page -v`

Expected: FAIL，因 `Config.BASE_URL` 仍为旧默认地址，而 `LoginPage.SUCCESS_URL` 为透析管理页地址。

- [ ] **Step 3: 更新默认与示例配置**

将 `config/config.py` 中的默认值改为：

```python
BASE_URL = os.getenv("BASE_URL", "https://yunjingzhi.com/yunjingservice/user/txform.shtml")
```

将 `.env.example` 中的对应配置改为：

```dotenv
BASE_URL=https://yunjingzhi.com/yunjingservice/user/txform.shtml
```

- [ ] **Step 4: 运行配置测试并确认通过**

Run: `pytest tests/test_config.py::test_default_base_url_matches_dialysis_management_page -v`

Expected: PASS。

### Task 2: 清理旧测试报告并验证

**Files:**
- Delete contents: `reports/allure-results/`
- Delete contents: `reports/screenshots/`

- [ ] **Step 1: 删除历史报告产物**

删除 `reports/allure-results/` 和 `reports/screenshots/` 中的全部文件，保留目录供 pytest 与截图钩子后续自动写入。

- [ ] **Step 2: 搜索旧地址**

Run: `rg -n --hidden --glob '!**/.venv/**' --glob '!**/.git/**' 'http://novel\.hctestedu\.com' .`

Expected: 无输出。

- [ ] **Step 3: 运行完整测试集**

Run: `pytest`

Expected: 配置测试通过；其他测试的结果应反映当前外部站点可用性，pytest 退出码为 0。

- [ ] **Step 4: 提交变更**

当前工作目录不是 Git 仓库；跳过提交。若后续在 Git 工作树中执行，使用：

```bash
git add config/config.py .env.example tests/test_config.py docs/superpowers/specs/2026-08-05-dialysis-base-url-design.md docs/superpowers/plans/2026-08-05-dialysis-base-url.md
git commit -m "chore: update dialysis base url"
```
