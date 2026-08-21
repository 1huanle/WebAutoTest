# 直接写入透析处方 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 自动选择患者陈奕源测试，按截图数据填写透析处方，选择医生陈奕源并确认保存。

**Architecture:** 测试数据保存在 YAML 文件中，测试只描述业务顺序。`DialysisSheetPage` 选择患者，`PrescriptionSection` 读取和填写处方字段、选择医生并确认；每个写入定位器先由可视化页面采集后再写入代码。

**Tech Stack:** Python 3.12、pytest、pytest-playwright、PyYAML。

---

### Task 1: 采集真实写入定位器

**Files:**
- Modify: `pages/hemodialysis/dialysis_sheet_page.py`
- Modify: `pages/hemodialysis/prescription_section.py`

- [ ] **Step 1: 在可视化会话中选择患者并读取处方表单**

使用透析号 `21000536543` 点击患者记录。对处方区域执行 `snapshot`、`generate-locator` 和只读 `eval`，记录下列控件的实际 `name`、`id`、标签或选项：机号、抗凝剂、透析方式、处方脱水量、首剂、维持、透析时长、血透器、血管通路、血流量、透析液流量、电解质、医生和确认按钮。

- [ ] **Step 2: 仅在所有写入控件均有稳定定位器时继续**

确认任何定位器均不依赖截图坐标、动态 CSS 类名或患者列表行号。医生下拉项必须精确匹配“陈奕源”，确认按钮必须限定在“透析处方”分区。

### Task 2: 写入数据与失败测试

**Files:**
- Create: `data/dialysis_prescription_data.yaml`
- Create: `tests/test_dialysis_prescription_write.py`

- [ ] **Step 1: 写入处方测试数据**

```yaml
patient:
  name: 陈奕源测试
  dialysis_number: "21000536543"
prescription:
  machine_number: "58-1"
  anticoagulant: 叶酸片
  dialysis_mode: HD
  dehydration_liters: "1"
  initial_dose: "4000"
  maintenance_dose: "3"
  dialysis_hours: "4"
  dialyzer: 贝丽奇-BLS 512SD
  access_side: 左侧
  access_type: 动静脉直穿
  blood_flow: "225"
  dialysate_flow: "501"
  formula_sodium: "138"
  potassium: "2.0"
  calcium: "1.5"
  bicarbonate: "31"
  doctor: 陈奕源
```

- [ ] **Step 2: 写入失败测试**

```python
@pytest.mark.regression
def test_confirm_dialysis_prescription_for_test_patient(page):
    """验证指定患者的透析处方可按测试数据填写并确认保存。"""
    dialysis_sheet = DialysisSheetPage(page).open()
    dialysis_sheet.select_patient_by_dialysis_number("21000536543")

    dialysis_sheet.prescription.fill_prescription(prescription_data)
    dialysis_sheet.prescription.select_doctor("陈奕源")
    dialysis_sheet.prescription.confirm()

    assert dialysis_sheet.prescription.is_confirmed()
```

- [ ] **Step 3: 运行测试并确认失败原因是 POM 写入接口不存在**

Run: `./.venv/Scripts/python.exe -m pytest tests/test_dialysis_prescription_write.py -v --basetemp C:\tmp\webtest-prescription-red`

Expected: `AttributeError` for `select_patient_by_dialysis_number` or `fill_prescription` before任何处方数据被确认保存。

### Task 3: 实现患者选择和处方写入 POM

**Files:**
- Modify: `pages/hemodialysis/dialysis_sheet_page.py`
- Modify: `pages/hemodialysis/prescription_section.py`

- [ ] **Step 1: 实现按透析号选择患者**

```python
def select_patient_by_dialysis_number(self, dialysis_number: str) -> "DialysisSheetPage":
    """通过患者列表中的透析号点击并选中指定患者。"""
    self.page.get_by_text(dialysis_number, exact=True).click()
    return self
```

- [ ] **Step 2: 实现处方写入和保存接口**

```python
def fill_prescription(self, data: dict[str, str]) -> "PrescriptionSection":
    """按 YAML 测试数据填写透析处方的可编辑字段。"""
    ...

def select_doctor(self, doctor: str) -> "PrescriptionSection":
    """选择处方开立医生。"""
    ...

def confirm(self) -> "PrescriptionSection":
    """点击透析处方分区的确认按钮保存处方。"""
    ...

def is_confirmed(self) -> bool:
    """读取透析处方确认后的可见状态。"""
    ...
```

实现中使用 Task 1 已采集的稳定定位器。`confirm()` 点击后等待“未确认”状态消失或确认按钮禁用状态变化，不能使用固定等待时间。

- [ ] **Step 3: 重跑真实写入测试**

Run: `./.venv/Scripts/python.exe -m pytest tests/test_dialysis_prescription_write.py -v --basetemp C:\tmp\webtest-prescription-green`

Expected: `1 passed`，且该患者的处方显示已确认。

### Task 4: 回归验证

**Files:**
- Test: `tests/`

- [ ] **Step 1: 运行完整回归**

Run: `./.venv/Scripts/python.exe -m pytest -v --basetemp C:\tmp\webtest-prescription-final`

Expected: 所有测试通过；真实写入用例不得因网络或定位器错误留下未确认的部分填写状态。
