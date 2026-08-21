# Cancel Dialysis Plan Sync Dialog Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Allow the hemodialysis POM to dismiss the "同步透析方案" confirmation dialog by clicking "取消" and remove its overlay.

**Architecture:** Add narrowly scoped actions to `PrescriptionSection`: one opens the dialysis-plan synchronization dialog and one clicks the exact `取消` action inside the currently visible Layui dialog. The regression test selects the existing test patient, opens that dialog, cancels it, and verifies the visible dialog is gone without saving any data.

**Tech Stack:** Python 3.12, pytest, Playwright sync API, existing POM structure, Layui dialogs.

---

### Task 1: Write the dialog-cancellation regression test

**Files:**
- Modify: `C:\Users\dev21\Desktop\webtest\tests\test_dialysis_prescription_write.py`
- Test: `C:\Users\dev21\Desktop\webtest\tests\test_dialysis_prescription_write.py`

- [ ] **Step 1: Add the failing test**

```python
@pytest.mark.regression
def test_cancel_dialysis_plan_sync_dialog(page):
    """验证取消同步透析方案弹窗后遮罩会消失，且不保存任何同步操作。"""
    with PRESCRIPTION_DATA_FILE.open(encoding="utf-8") as data_file:
        test_data = yaml.safe_load(data_file)

    dialysis_sheet = DialysisSheetPage(page).open()
    dialysis_sheet.select_patient_by_dialysis_number(test_data["patient"]["dialysis_number"])

    prescription = dialysis_sheet.prescription
    prescription.open_dialysis_plan_sync_dialog()
    prescription.cancel_dialysis_plan_sync()

    assert prescription.is_dialysis_plan_sync_dialog_closed()
```

- [ ] **Step 2: Run the new test and verify it fails because the POM action does not exist**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_dialysis_prescription_write.py::test_cancel_dialysis_plan_sync_dialog -v --basetemp C:\tmp\webtest-sync-dialog-red
```

Expected: `AttributeError` for `open_dialysis_plan_sync_dialog`.

### Task 2: Add narrowly scoped POM actions

**Files:**
- Modify: `C:\Users\dev21\Desktop\webtest\pages\hemodialysis\prescription_section.py`
- Test: `C:\Users\dev21\Desktop\webtest\tests\test_dialysis_prescription_write.py`

- [ ] **Step 1: Add the dialog-specific locators and actions**

```python
def _visible_dialog(self):
    return self.page.locator(".layui-layer:visible")

def open_dialysis_plan_sync_dialog(self) -> "PrescriptionSection":
    self._prescription_form().get_by_role("button", name="同步到透析方案", exact=True).click()
    expect(self._visible_dialog()).to_be_visible()
    return self

def cancel_dialysis_plan_sync(self) -> "PrescriptionSection":
    self._visible_dialog().get_by_text("取消", exact=True).click()
    return self

def is_dialysis_plan_sync_dialog_closed(self) -> bool:
    expect(self._visible_dialog()).to_be_hidden()
    return True
```

- [ ] **Step 2: Run the focused test and verify it passes**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_dialysis_prescription_write.py::test_cancel_dialysis_plan_sync_dialog -v --basetemp C:\tmp\webtest-sync-dialog-green
```

Expected: `1 passed`. The dialog is dismissed through the user-facing `取消` button; no prescription save or synchronization action is executed.

- [ ] **Step 3: Verify the existing direct-write test still passes without re-running it**

Run:

```powershell
.\.venv\Scripts\python.exe -m py_compile pages\hemodialysis\prescription_section.py tests\test_dialysis_prescription_write.py
```

Expected: exit code `0`. Do not re-run the direct-write test because it would submit an already confirmed prescription a second time.
