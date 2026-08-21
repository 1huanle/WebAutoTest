# 登录状态保存与复用 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让用户保存一次手动登录后的 Playwright 状态，并让 pytest 后续自动复用该会话。

**Architecture:** `utils/auth_state.py` 维护本地状态文件路径及查询函数。`save_login_state.py` 在可视化浏览器中等待用户完成登录后保存状态；`conftest.py` 仅在状态文件存在时向 `browser.new_context()` 传递 `storage_state` 参数。

**Tech Stack:** Python 3.12、pytest、pytest-playwright、Playwright Sync API。

---

### Task 1: 以测试先行方式添加状态路径工具

**Files:**
- Create: `tests/test_auth_state.py`
- Create: `utils/auth_state.py`

- [ ] **Step 1: 写入失败测试**

创建以下测试：

```python
from utils import auth_state


def test_storage_state_path_returns_none_when_file_is_missing(tmp_path, monkeypatch):
    state_file = tmp_path / "storage_state.json"
    monkeypatch.setattr(auth_state, "STORAGE_STATE_FILE", state_file)

    assert auth_state.storage_state_path() is None


def test_storage_state_path_returns_file_path_when_state_exists(tmp_path, monkeypatch):
    state_file = tmp_path / "storage_state.json"
    state_file.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(auth_state, "STORAGE_STATE_FILE", state_file)

    assert auth_state.storage_state_path() == str(state_file)
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `.venv\\Scripts\\python.exe -m pytest tests/test_auth_state.py -v`

Expected: FAIL，因为 `utils.auth_state` 模块不存在。

- [ ] **Step 3: 实现最小状态工具**

创建 `utils/auth_state.py`：

```python
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STORAGE_STATE_FILE = PROJECT_ROOT / "auth" / "storage_state.json"


def storage_state_path() -> str | None:
    return str(STORAGE_STATE_FILE) if STORAGE_STATE_FILE.is_file() else None
```

- [ ] **Step 4: 运行状态工具测试并确认通过**

Run: `.venv\\Scripts\\python.exe -m pytest tests/test_auth_state.py -v`

Expected: 2 passed。

### Task 2: 在 pytest 中复用已保存会话

**Files:**
- Modify: `conftest.py`
- Modify: `.gitignore`

- [ ] **Step 1: 加载可选状态文件**

在 `conftest.py` 导入 `storage_state_path`。创建浏览器上下文时，先组装原有参数；当 `storage_state_path()` 返回路径时，额外传入：

```python
context_options["storage_state"] = storage_state_path()
```

随后调用：

```python
context = browser.new_context(**context_options)
```

- [ ] **Step 2: 忽略本地登录凭证**

在 `.gitignore` 增加：

```gitignore
auth/storage_state.json
```

- [ ] **Step 3: 编译夹具配置**

Run: `.venv\\Scripts\\python.exe -m compileall conftest.py utils`

Expected: 退出码为 0。

### Task 3: 添加手动保存脚本和使用说明

**Files:**
- Create: `save_login_state.py`
- Modify: `docs/项目运行流程.md`

- [ ] **Step 1: 创建手动保存脚本**

脚本使用 `sync_playwright()` 启动 `Config.BROWSER` 指定的可视化浏览器，打开 `LoginPage.LOGIN_URL`；提示用户在浏览器内完成登录及角色选择后按回车。仅当 `page.url` 等于 `LoginPage.SUCCESS_URL` 时，创建 `auth/` 目录并调用：

```python
context.storage_state(path=str(STORAGE_STATE_FILE))
```

否则输出提示并返回 1。无论成功或失败，均关闭上下文和浏览器。

- [ ] **Step 2: 更新运行流程文档**

在 `docs/项目运行流程.md` 新增“保存并复用登录状态”章节，包含：

```powershell
.\\.venv\\Scripts\\python.exe save_login_state.py
```

说明状态文件敏感、会话过期后应删除 `auth/storage_state.json` 并重新保存。

- [ ] **Step 3: 验证无状态回退**

Run: `.venv\\Scripts\\python.exe -m pytest tests/test_auth_state.py -v`

Expected: 无状态文件时测试通过，`storage_state_path()` 返回 `None`。

- [ ] **Step 4: 提交变更**

当前目录不是 Git 仓库；跳过提交。若后续在 Git 工作树中执行，使用：

```bash
git add utils/auth_state.py tests/test_auth_state.py conftest.py save_login_state.py .gitignore docs/项目运行流程.md docs/superpowers/specs/2026-08-05-login-state-design.md docs/superpowers/plans/2026-08-05-login-state.md
git commit -m "feat: reuse saved Playwright login state"
```
