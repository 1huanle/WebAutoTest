# 血液透析弹窗组件 POM Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 将透析处方触发的医嘱推送 iframe 弹窗拆成来源明确的独立 POM 组件，并建立血液透析各业务分区统一的弹窗命名规范。

**Architecture:** 在 `pages/hemodialysis/dialogs/` 下按触发分区存放弹窗组件，当前只实现已读取真实结构的 `PrescriptionMedicalOrderPushDialog`。`PrescriptionSection` 负责处方业务动作并组合该组件，弹窗组件负责等待、跨 iframe 点击和关闭校验。

**Tech Stack:** Python 3.12、pytest、Playwright Sync API、Page Object Model

---

### Task 1: 用测试固定处方弹窗组件接口

**Files:**
- Modify: `tests/test_prescription_section.py`

- [x] **Step 1: Write the failing test**

在现有 iframe 弹窗场景中增加来源明确的组件断言，并通过该组件校验弹窗关闭：

```python
from pages.hemodialysis.dialogs.prescription_medical_order_push_dialog import (
    PrescriptionMedicalOrderPushDialog,
)

assert isinstance(
    prescription.medical_order_push_dialog,
    PrescriptionMedicalOrderPushDialog,
)
assert prescription.medical_order_push_dialog.is_closed()
```

- [x] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests\test_prescription_section.py -v --basetemp C:\tmp\webtest-dialog-red`

Expected: FAIL during collection because `pages.hemodialysis.dialogs` does not exist.

### Task 2: 新增透析处方医嘱推送弹窗组件

**Files:**
- Create: `pages/hemodialysis/dialogs/__init__.py`
- Create: `pages/hemodialysis/dialogs/prescription_medical_order_push_dialog.py`
- Modify: `pages/hemodialysis/prescription_section.py`

- [x] **Step 1: Write minimal implementation**

新增 `PrescriptionMedicalOrderPushDialog`，中文注释统一标记“血液透析 > 透析处方触发”。公开接口为：

```python
class PrescriptionMedicalOrderPushDialog:
    """血液透析 > 透析处方触发：封装首次确认处方后的医嘱推送弹窗。"""

    def __init__(self, page: Page): ...
    def wait_for_open(self) -> "PrescriptionMedicalOrderPushDialog": ...
    def confirm(self) -> None: ...
    def is_closed(self) -> bool: ...
```

在 `PrescriptionSection.__init__()` 中创建：

```python
self.medical_order_push_dialog = PrescriptionMedicalOrderPushDialog(page)
```

首次确认处方时调用：

```python
self.medical_order_push_dialog.wait_for_open().confirm()
```

- [x] **Step 2: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest tests\test_prescription_section.py -v --basetemp C:\tmp\webtest-dialog-green`

Expected: `1 passed`。

### Task 3: 更新真实处方用例的弹窗校验接口

**Files:**
- Modify: `tests/test_dialysis_prescription_write.py`

- [x] **Step 1: Replace the old section-level assertion**

```python
assert prescription.medical_order_push_dialog.is_closed()
```

测试注释明确写明这是“血液透析 > 透析处方首次确认触发”的弹窗。

- [x] **Step 2: Run non-writing regression tests**

Run: `.\.venv\Scripts\python.exe -m pytest tests -v -k "not test_confirm_dialysis_prescription_for_test_patient and not test_cancel_dialysis_plan_sync_dialog" --basetemp C:\tmp\webtest-dialog-regression`

Expected: 所有选中用例通过。排除两条会依赖真实患者页面状态或执行真实业务动作的用例。

### Task 4: Verify syntax and source labels

**Files:**
- Verify: `pages/hemodialysis/dialogs/prescription_medical_order_push_dialog.py`
- Verify: `pages/hemodialysis/prescription_section.py`
- Verify: `tests/test_prescription_section.py`
- Verify: `tests/test_dialysis_prescription_write.py`

- [x] **Step 1: Compile changed Python files**

Run: `.\.venv\Scripts\python.exe -m py_compile pages\hemodialysis\dialogs\prescription_medical_order_push_dialog.py pages\hemodialysis\prescription_section.py tests\test_prescription_section.py tests\test_dialysis_prescription_write.py`

Expected: exit code 0 with no output.

- [x] **Step 2: Check business-source comments**

Run: `Select-String -Path pages\hemodialysis\dialogs\*.py,pages\hemodialysis\prescription_section.py,tests\test_prescription_section.py,tests\test_dialysis_prescription_write.py -Pattern '血液透析 > 透析处方'`

Expected: 命中弹窗类、调用处和测试注释。

本项目没有 `.git` 目录，因此不包含 Git 提交步骤。

