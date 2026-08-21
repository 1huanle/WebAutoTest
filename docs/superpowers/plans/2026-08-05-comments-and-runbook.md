# 中文注释与项目运行流程 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为测试和 POM 页面对象补充中文说明，并交付可直接执行的项目运行流程文档。

**Architecture:** 保持测试代码和页面对象的公开接口不变，仅添加 UTF-8 中文文档字符串与关键步骤注释。运行文档从现有 `run.py`、`pytest.ini`、`config/config.py` 和 `conftest.py` 提取实际命令、配置和输出目录。

**Tech Stack:** Python 3.12、pytest、pytest-playwright、Allure、python-dotenv、PyYAML。

---

### Task 1: 为测试用例增加中文注释

**Files:**
- Modify: `tests/test_config.py`
- Modify: `tests/test_login_flow.py`
- Modify: `tests/test_login_page.py`
- Modify: `tests/test_run.py`

- [ ] **Step 1: 记录测试职责**

为每个测试函数增加中文文档字符串。例如：

```python
def test_default_base_url_matches_dialysis_management_page():
    """验证框架默认基础地址指向登录后的透析管理页面。"""
    assert Config.BASE_URL == LoginPage.SUCCESS_URL
```

在登录流程测试的数据文件读取、登录操作链和最终 URL 断言前添加中文行内注释。

- [ ] **Step 2: 检查测试文件语法**

Run: `.venv\\Scripts\\python.exe -m compileall tests`

Expected: 所有测试文件成功编译，退出码为 0。

### Task 2: 为 POM 页面对象增加中文注释

**Files:**
- Modify: `pages/base_page.py`
- Modify: `pages/login_page.py`

- [ ] **Step 1: 记录页面对象职责和操作语义**

为 `BasePage` 与 `LoginPage` 添加类文档字符串，为所有公开方法添加中文文档字符串；在 `LoginPage` 的 URL 与定位器常量分组前加入中文注释。

- [ ] **Step 2: 检查 POM 文件语法**

Run: `.venv\\Scripts\\python.exe -m compileall pages`

Expected: 两个页面对象模块成功编译，退出码为 0。

### Task 3: 编写项目运行流程

**Files:**
- Create: `docs/项目运行流程.md`

- [ ] **Step 1: 编写运行文档**

文档按以下顺序说明项目：

```markdown
# 项目运行流程

## 1. 环境准备
## 2. 配置测试环境
## 3. 执行测试
## 4. 查看测试产物
## 5. 当前运行限制
```

在“执行测试”中给出激活虚拟环境、安装 `requirements.txt`、运行 `run.py`、运行 `pytest`、执行单个配置测试以及生成 Allure 报告的 PowerShell 命令。

- [ ] **Step 2: 验证运行文档中的路径与命令**

Run: `Test-Path docs\\项目运行流程.md; Test-Path reports\\allure-results; Test-Path reports\\screenshots`

Expected: 三项均为 `True`。

### Task 4: 回归验证

**Files:**
- Test: `tests/test_config.py`

- [ ] **Step 1: 运行配置回归测试**

Run: `.venv\\Scripts\\python.exe -m pytest tests/test_config.py::test_default_base_url_matches_dialysis_management_page -v`

Expected: PASS。

- [ ] **Step 2: 提交变更**

当前目录不是 Git 仓库；跳过提交。若后续在 Git 工作树中执行，使用：

```bash
git add tests pages docs/项目运行流程.md docs/superpowers/specs/2026-08-05-comments-and-runbook-design.md docs/superpowers/plans/2026-08-05-comments-and-runbook.md
git commit -m "docs: add Chinese comments and project runbook"
```
