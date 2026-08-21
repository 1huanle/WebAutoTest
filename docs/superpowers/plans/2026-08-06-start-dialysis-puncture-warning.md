# 开始透析穿刺点位提示处理 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 开始透析确认后自动接受“穿刺点位信息未填写”提示，并继续等待业务弹窗关闭。

**Architecture:** 在 `StartDialysisDialog.confirm()` 内处理开始透析 iframe 中的业务提示层。定位器同时限定可见 Layui 弹层和提示文本，只点击该提示层内部“确定”，避免误点页面其他按钮。

**Tech Stack:** Python 3.12、pytest、Playwright Page Object Model

---

### Task 1: 用本地弹窗测试复现阻塞

**Files:**
- Modify: `tests/test_start_dialysis_dialog.py`

- [ ] **Step 1: 扩展本地 iframe 夹具**

在开始透析 iframe 内增加默认隐藏的 `.layui-layer` 提示层，内容包含“穿刺点位信息未填写，是否继续保存？”、“不再提示（7天内不再提示）”、“确定”和“取消”。开始透析底部“确认”只显示提示层；提示层“确定”才关闭外层弹窗和遮罩，并写入 `#start-dialysis-confirmed`。

- [ ] **Step 2: 增加行为断言**

在测试中保留无关“确定”按钮，并在 `dialog.confirm()` 后断言提示层的确定事件已发生、无关按钮未被点击、外层弹窗和遮罩已关闭。

- [ ] **Step 3: 运行测试确认 RED**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_start_dialysis_dialog.py -v --basetemp C:\tmp\webtest-start-warning-red
```

Expected: FAIL，因为当前 `confirm()` 点击底部确认后直接等待外层弹窗关闭，没有处理提示层。

### Task 2: 实现提示层自动确认

**Files:**
- Modify: `pages/hemodialysis/dialogs/start_dialysis_dialog.py`

- [ ] **Step 1: 增加提示文本常量和内部方法**

新增 `PUNCTURE_SITE_WARNING = "穿刺点位信息未填写"`。内部方法在 iframe 中定位包含该文本的可见 `.layui-layer`，等待出现后点击其内部精确文本为“确定”的最后一个元素。

- [ ] **Step 2: 接入确认流程**

`confirm()` 点击底部“确认”后调用提示层处理方法，再调用 `_wait_for_closed()`。中文注释明确该提示属于“血液透析 > 开始透析 > 穿刺点位未填写”。

- [ ] **Step 3: 运行测试确认 GREEN**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_start_dialysis_dialog.py -v --basetemp C:\tmp\webtest-start-warning-green
```

Expected: `1 passed`。

### Task 3: 非写入回归验证

**Files:**
- Verify: `pages/hemodialysis/dialogs/start_dialysis_dialog.py`
- Verify: `tests/test_start_dialysis_dialog.py`
- Verify: `tests/test_main_write_flow.py`

- [ ] **Step 1: 运行聚焦测试**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_start_dialysis_dialog.py tests\test_main_write_flow.py -v --basetemp C:\tmp\webtest-start-warning-focused
```

Expected: 所有选中测试通过。

- [ ] **Step 2: 编译变更文件**

```powershell
.\.venv\Scripts\python.exe -m compileall -q pages\hemodialysis\dialogs\start_dialysis_dialog.py tests\test_start_dialysis_dialog.py
```

Expected: exit code 0，无输出。

- [ ] **Step 3: 运行完整测试套件**

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q --basetemp C:\tmp\webtest-start-warning-suite
```

Expected: 全部测试通过；`tests/main_write.py` 不会被默认收集。

本项目不是 Git 仓库，因此不包含提交、分支或 worktree 步骤。
