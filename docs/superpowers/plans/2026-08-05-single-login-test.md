# 单一登录用例 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 删除重复的登录页面测试，仅保留覆盖完整登录流程的一条业务用例。

**Architecture:** `tests/test_login_flow.py` 继续作为唯一登录业务测试，复用 `LoginPage` 完成账号输入、密码输入、角色选择和成功页面跳转校验。删除 `tests/test_login_page.py`，不影响配置、运行入口和报告脚本测试。

**Tech Stack:** Python 3.12、pytest、pytest-playwright、PyYAML。

---

### Task 1: 删除重复登录页面测试

**Files:**
- Delete: `tests/test_login_page.py`
- Test: `tests/test_login_flow.py`

- [ ] **Step 1: 删除重复用例文件**

删除 `tests/test_login_page.py`。该文件只覆盖页面加载与账号密码填写，已被完整登录流程用例覆盖。

- [ ] **Step 2: 检查测试收集结果**

Run: `.venv\\Scripts\\python.exe -m pytest --collect-only -q`

Expected: 输出中包含且仅包含一条登录业务用例 `test_login_redirects_to_the_success_page`，不包含 `TestLoginPage`。

- [ ] **Step 3: 运行保留的登录用例**

Run: `.venv\\Scripts\\python.exe -m pytest tests/test_login_flow.py::test_login_redirects_to_the_success_page -v`

Expected: PASS；若当前执行环境无法访问外部系统，则明确显示网络访问错误，不修改用例逻辑。

- [ ] **Step 4: 提交变更**

当前目录不是 Git 仓库；跳过提交。若后续在 Git 工作树中执行，使用：

```bash
git add -u tests/test_login_page.py docs/superpowers/specs/2026-08-05-single-login-test-design.md docs/superpowers/plans/2026-08-05-single-login-test.md
git commit -m "test: retain a single login flow case"
```
