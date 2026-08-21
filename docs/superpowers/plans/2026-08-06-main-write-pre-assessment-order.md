# 主流程先透前评估后透析处方 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将血液透析主流程调整为先填写并确认透前评估，再填写并确认透析处方，并把截图数据统一写入 `data/main_write.yaml`。

**Architecture:** `tests/main_write.py` 保留真实页面入口，新增 `execute_main_write(dialysis_sheet, test_data)` 负责编排 POM 调用顺序。`tests/test_main_write_flow.py` 使用不访问网站的记录型假对象验证顺序，并直接解析 YAML 验证截图数据。

**Tech Stack:** Python 3.12、pytest、PyYAML、Playwright Page Object Model

---

### Task 1: 透前评估 YAML 截图数据

**Files:**
- Modify: `data/main_write.yaml`
- Create: `tests/test_main_write_flow.py`

- [ ] **Step 1: Write the failing YAML test**

创建 `tests/test_main_write_flow.py`，直接读取 `data/main_write.yaml` 并断言：

```python
from pathlib import Path

import yaml


MAIN_WRITE_DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "main_write.yaml"


def test_main_write_yaml_contains_pre_dialysis_assessment_screenshot_values():
    """主流程 YAML 应完整保存截图中的透前评估填写值和联动期望值。"""
    with MAIN_WRITE_DATA_FILE.open(encoding="utf-8") as data_file:
        test_data = yaml.safe_load(data_file)

    assessment = test_data["pre_dialysis_assessment"]
    assert assessment["editable"] == {
        "temperature": "36",
        "pulse": "80",
        "respiration": "20",
        "respiration_type": "自主呼吸",
        "systolic_pressure": "110",
        "diastolic_pressure": "80",
        "blood_pressure_site": "上肢",
        "weighing_method": "正常",
        "pre_weight": "70",
        "clothing_weight": "0",
        "expected_dehydration_liters": "0",
        "a_thrombus": "/",
        "v_thrombus": "/",
    }
    assert assessment["expected"] == {
        "dry_weight": "待定",
        "last_post_weight": "1",
        "pre_weight": "70",
        "weight_gain": "69",
        "total_ultrafiltration": "1",
        "dialysis_interval": "/",
        "last_post_dialysis": "/",
        "pre_dialysis_symptoms": "无症状",
        "fistula": "/",
        "catheter": "/",
        "comorbidities": "无",
    }
```

- [ ] **Step 2: Run the YAML test to verify RED**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_main_write_flow.py::test_main_write_yaml_contains_pre_dialysis_assessment_screenshot_values -v --basetemp C:\tmp\webtest-main-write-yaml-red
```

Expected: FAIL with `KeyError: 'pre_dialysis_assessment'` because the YAML section does not exist.

- [ ] **Step 3: Add screenshot values to YAML**

Insert this block between `patient` and `prescription` in `data/main_write.yaml`:

```yaml
pre_dialysis_assessment:
  editable:
    temperature: "36"
    pulse: "80"
    respiration: "20"
    respiration_type: 自主呼吸
    systolic_pressure: "110"
    diastolic_pressure: "80"
    blood_pressure_site: 上肢
    weighing_method: 正常
    pre_weight: "70"
    clothing_weight: "0"
    expected_dehydration_liters: "0"
    a_thrombus: "/"
    v_thrombus: "/"
  expected:
    dry_weight: 待定
    last_post_weight: "1"
    pre_weight: "70"
    weight_gain: "69"
    total_ultrafiltration: "1"
    dialysis_interval: "/"
    last_post_dialysis: "/"
    pre_dialysis_symptoms: 无症状
    fistula: "/"
    catheter: "/"
    comorbidities: 无
```

- [ ] **Step 4: Run the YAML test to verify GREEN**

Run the Step 2 command with basetemp `C:\tmp\webtest-main-write-yaml-green`.

Expected: `1 passed`.

### Task 2: 主流程调用顺序

**Files:**
- Modify: `tests/test_main_write_flow.py`
- Modify: `tests/main_write.py`

- [ ] **Step 1: Write the failing sequence test**

在 `tests/test_main_write_flow.py` 中创建记录调用顺序的假对象，并要求 `tests.main_write.execute_main_write` 存在：

```python
from tests import main_write


class RecordingSection:
    def __init__(self, prefix, events):
        self.prefix = prefix
        self.events = events
        self.medical_order_push_dialog = self

    def fill_assessment(self, data):
        self.events.append((f"{self.prefix}.fill_assessment", data))
        return self

    def expect_calculated_values(self, data):
        self.events.append((f"{self.prefix}.expect_calculated_values", data))
        return self

    def fill_prescription(self, data):
        self.events.append((f"{self.prefix}.fill_prescription", data))
        return self

    def confirm(self):
        self.events.append((f"{self.prefix}.confirm", None))
        return self

    def is_confirmed(self):
        self.events.append((f"{self.prefix}.is_confirmed", None))
        return True

    def is_closed(self):
        self.events.append((f"{self.prefix}.dialog.is_closed", None))
        return True


class RecordingDialysisSheet:
    def __init__(self, events):
        self.events = events
        self.pre_dialysis_assessment = RecordingSection("assessment", events)
        self.prescription = RecordingSection("prescription", events)

    def select_patient_by_dialysis_number(self, dialysis_number):
        self.events.append(("sheet.select_patient", dialysis_number))
        return self


def test_execute_main_write_confirms_assessment_before_filling_prescription():
    """主流程必须先完成透前评估确认，之后才能填写透析处方。"""
    assert hasattr(main_write, "execute_main_write"), "主流程编排函数尚未实现"
    events = []
    sheet = RecordingDialysisSheet(events)
    data = {
        "patient": {"dialysis_number": "21000536543"},
        "pre_dialysis_assessment": {
            "editable": {"temperature": "36"},
            "expected": {"dry_weight": "待定"},
        },
        "prescription": {"doctor": "陈奕源"},
    }

    main_write.execute_main_write(sheet, data)

    assert events == [
        ("sheet.select_patient", "21000536543"),
        ("assessment.fill_assessment", {"temperature": "36"}),
        ("assessment.expect_calculated_values", {"dry_weight": "待定"}),
        ("assessment.confirm", None),
        ("assessment.is_confirmed", None),
        ("prescription.fill_prescription", {"doctor": "陈奕源"}),
        ("prescription.confirm", None),
        ("prescription.is_confirmed", None),
        ("prescription.dialog.is_closed", None),
    ]
```

- [ ] **Step 2: Run the sequence test to verify RED**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_main_write_flow.py::test_execute_main_write_confirms_assessment_before_filling_prescription -v --basetemp C:\tmp\webtest-main-write-order-red
```

Expected: FAIL with `主流程编排函数尚未实现`.

- [ ] **Step 3: Implement minimal orchestration**

在 `tests/main_write.py` 中：

1. 将 `PRESCRIPTION_DATA_FILE` 改名为 `MAIN_WRITE_DATA_FILE`。
2. 新增以下函数：

```python
def execute_main_write(dialysis_sheet, test_data: dict) -> None:
    """按业务顺序完成透前评估，再填写并确认透析处方。"""
    dialysis_sheet.select_patient_by_dialysis_number(
        test_data["patient"]["dialysis_number"]
    )

    # 主流程第 1 阶段：透前评估必须确认成功后才能继续。
    assessment = dialysis_sheet.pre_dialysis_assessment
    assessment.fill_assessment(test_data["pre_dialysis_assessment"]["editable"])
    assessment.expect_calculated_values(
        test_data["pre_dialysis_assessment"]["expected"]
    )
    assessment.confirm()
    assert assessment.is_confirmed()

    # 主流程第 2 阶段：填写并确认透析处方。
    prescription = dialysis_sheet.prescription
    prescription.fill_prescription(test_data["prescription"])
    prescription.confirm()
    assert prescription.is_confirmed()
    assert prescription.medical_order_push_dialog.is_closed()
```

3. 将真实用例改为创建已打开的 `DialysisSheetPage` 后调用 `execute_main_write()`；保留取消同步透析方案测试。

- [ ] **Step 4: Run the sequence test to verify GREEN**

Run the Step 2 command with basetemp `C:\tmp\webtest-main-write-order-green`.

Expected: `1 passed`.

### Task 3: 非写入回归验证

**Files:**
- Verify: `tests/main_write.py`
- Verify: `data/main_write.yaml`
- Verify: `tests/test_main_write_flow.py`

- [ ] **Step 1: Run main-flow unit tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_main_write_flow.py tests\test_pre_dialysis_assessment_section.py tests\test_prescription_section.py -v --basetemp C:\tmp\webtest-main-write-focused
```

Expected: all selected tests pass without opening the real application.

- [ ] **Step 2: Compile changed Python files**

Run:

```powershell
.\.venv\Scripts\python.exe -m compileall -q tests\main_write.py tests\test_main_write_flow.py
```

Expected: exit code 0 with no output.

- [ ] **Step 3: Run the full non-writing regression**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -v -k "not main_write" --basetemp C:\tmp\webtest-main-write-regression
```

Expected: all collected non-writing tests pass. `tests/main_write.py` remains outside pytest's `test_*.py` collection pattern and is not executed.

本项目不是 Git 仓库，因此不包含提交、分支或 worktree 步骤。
