# 血液透析剩余业务分区 POM Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完成透前评估、临时医嘱、双人核对、监测记录、透后评估和治疗小结六个可操作 POM，并为临时医嘱和监测记录提供来源明确的 iframe 弹窗组件。

**Architecture:** 每个血液透析业务分区使用独立 POM 文件；临时医嘱和监测记录的 iframe 使用独立弹窗组件。三个 Layui iframe 弹窗共享所属遮罩跟踪基类，避免把其他弹层的遮罩误判为当前弹窗未关闭。

**Tech Stack:** Python 3.12、pytest、Playwright Sync API、Page Object Model

---

### Task 1: Layui iframe 弹窗基类与处方遮罩隔离

**Files:**
- Create: `pages/hemodialysis/dialogs/layui_iframe_dialog.py`
- Modify: `pages/hemodialysis/dialogs/prescription_medical_order_push_dialog.py`
- Modify: `tests/test_prescription_section.py`

- [ ] **Step 1: Write the failing test**

在医嘱推送测试 DOM 中同时创建当前弹窗遮罩 `#layui-layer-shade2` 和无关遮罩 `#layui-layer-shade99`。点击确定只删除当前弹窗和 `#layui-layer-shade2`，最后仍要求 `is_closed()` 返回 `True`。

```python
assert page.locator("#layui-layer-shade99:visible").count() == 1
assert prescription.medical_order_push_dialog.is_closed()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests\test_prescription_section.py -v --basetemp C:\tmp\webtest-remaining-red-dialog`

Expected: FAIL because the existing implementation asserts every visible Layui shade has disappeared.

- [ ] **Step 3: Write minimal implementation**

Create this shared interface:

```python
class LayuiIframeDialog:
    TITLE = ""

    def __init__(self, page: Page) -> None:
        self.page = page
        self._related_shade = None

    def _root(self):
        return self.page.locator(".layui-layer:visible").filter(has_text=self.TITLE)

    def wait_for_open(self):
        dialog = self._root()
        expect(dialog).to_be_visible(timeout=10_000)
        times = dialog.get_attribute("times")
        self._related_shade = self.page.locator(f"#layui-layer-shade{times}") if times else None
        expect(dialog.locator("iframe")).to_be_visible(timeout=10_000)
        return self

    def _frame(self):
        return self._root().locator("iframe").content_frame

    def _wait_for_closed(self) -> None:
        expect(self._root()).to_be_hidden(timeout=10_000)
        if self._related_shade is not None:
            expect(self._related_shade).to_be_hidden(timeout=10_000)

    def is_closed(self) -> bool:
        self._wait_for_closed()
        return True
```

Make `PrescriptionMedicalOrderPushDialog` inherit this class with `TITLE = "医嘱推送"` and use `_frame()` / `_wait_for_closed()`.

- [ ] **Step 4: Run test to verify it passes**

Run the Step 2 command. Expected: `1 passed`.

### Task 2: 透前评估 POM

**Files:**
- Modify: `pages/hemodialysis/pre_dialysis_assessment_section.py`
- Create: `tests/test_pre_dialysis_assessment_section.py`

- [ ] **Step 1: Write the failing test**

Build a mock `table.tx_table` headed by `透前评估` with editable inputs/selects and readonly calculated inputs. Assert this API:

```python
assessment = PreDialysisAssessmentSection(page)
assessment.fill_assessment({
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
})
assessment.expect_calculated_values({"dry_weight": "待定", "total_ultrafiltration": "1"})
assessment.confirm()
assert assessment.is_confirmed()
```

- [ ] **Step 2: Verify RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\test_pre_dialysis_assessment_section.py -v --basetemp C:\tmp\webtest-pre-assessment-red`

Expected: FAIL because `fill_assessment` does not exist.

- [ ] **Step 3: Implement field maps and actions**

Use editable keys mapped to `tx_pg_t`, `tx_pg_p`, `tx_pg_hr`, `tx_pg_hr_type`, `tx_pg_BP_shousuo`, `tx_pg_BP_shuzhang`, `tx_pg_BP_type`, `#txq_czfs`, `tx_tqcz`, `tx_peel_weight`, `tx_yztsl`, `tx_a_xx`, `tx_v_xx`. Use calculated keys mapped to `tx_gtz`, `tx_qctxhtz`, `tx_tqtz`, `tx_tzzj`, `tx_clzl`, `txqj_name`, `qctxh_name`, `tqzz_name`, `nl_name`, `dg_name`, `hbz_name`.

Implement `fill_assessment`, `expect_calculated_values`, `confirm`, and `is_confirmed`, all with Chinese comments marked `血液透析 > 透前评估`.

- [ ] **Step 4: Verify GREEN**

Run the Step 2 command. Expected: all selected tests pass.

### Task 3: 临时医嘱列表和 iframe 弹窗

**Files:**
- Modify: `pages/hemodialysis/temporary_orders_section.py`
- Create: `pages/hemodialysis/dialogs/temporary_order_dialog.py`
- Modify: `pages/hemodialysis/dialogs/__init__.py`
- Create: `tests/test_temporary_orders_section.py`

- [ ] **Step 1: Write failing list and dialog tests**

The list test requires `get_order_rows`, `select_order`, `open_add_order`, `open_order_template`, `execute_selected`, `check_selected`, and `delete_selected`. The dialog test requires:

```python
dialog.wait_for_open().fill_order({
    "start_time": "2026-08-06 11:00",
    "reminder_date": "2026-08-06",
    "order_name": "测试医嘱",
    "single_dose": "1",
    "quantity": "1",
    "administration_route": "外用",
    "frequency": "每天一剂",
    "execution_department": "测试部",
    "diagnoses": ["测试诊断"],
    "note": "主流程测试",
})
dialog.cancel()
assert dialog.is_closed()
```

- [ ] **Step 2: Verify RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\test_temporary_orders_section.py -v --basetemp C:\tmp\webtest-temporary-orders-red`

Expected: FAIL because the methods and dialog component do not exist.

- [ ] **Step 3: Implement list POM and dialog**

Map dialog keys to `tx_startdate`, `tx_reminddate`, `tx_advicename`, `tx_singledosage`, `tx_drugnumber`, `tx_wayadminister`, `tx_frequency`, `execution_department`, `tx_diagnose_select`, and `tx_yznote`. Validate readonly `tx_advicestyle`, `tx_advicedate`, `tx_lsyz_kz_doctor`, and `tx_advicedescript` when supplied.

The dialog inherits `LayuiIframeDialog`, uses `TITLE = "临时医嘱"`, and exposes `fill_order`, `expect_readonly_values`, `confirm`, and `cancel`.

- [ ] **Step 4: Verify GREEN**

Run the Step 2 command. Expected: all selected tests pass.

### Task 4: 双人核对 POM

**Files:**
- Create: `pages/hemodialysis/double_check_section.py`
- Create: `tests/test_double_check_section.py`

- [ ] **Step 1: Write failing tests**

Create mock groups for the four indicator names. Place detail checkboxes directly before their visible business labels, then require:

```python
double_check.mark_group_correct("dialysis_items")
double_check.set_detail_checked("人工肾", True)
double_check.set_detail_checked("透析方式", True)
double_check.select_checker("陈奕源")
double_check.confirm()
assert double_check.is_confirmed()
```

Assert `set_detail_checked("人工肾")` changes the checkbox adjacent to `人工肾`, even when an unrelated checkbox is inserted before it.

- [ ] **Step 2: Verify RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\test_double_check_section.py -v --basetemp C:\tmp\webtest-double-check-red`

Expected: FAIL because the new module and API do not exist.

- [ ] **Step 3: Implement label-based checkbox handling**

Map groups to `(indicator, error)` pairs: `tx_touXiWuPin_indicator/error`, `tx_touXiCanShu_indicator/error`, `tx_xueGuanTongLu_indicator/error`, and `tx_guanDao_indicator/error`. Implement `mark_group_correct`, `fill_group_error`, `set_detail_checked`, `select_checker`, `get_check_time`, `confirm`, and `is_confirmed`.

Find detail checkboxes from the exact label's preceding sibling or containing cell; do not index all page checkboxes.

- [ ] **Step 4: Verify GREEN**

Run the Step 2 command. Expected: all selected tests pass.

### Task 5: 监测记录列表和 iframe 弹窗

**Files:**
- Create: `pages/hemodialysis/monitoring_records_section.py`
- Create: `pages/hemodialysis/dialogs/monitoring_record_dialog.py`
- Modify: `pages/hemodialysis/dialogs/__init__.py`
- Create: `tests/test_monitoring_records_section.py`

- [ ] **Step 1: Write failing tests**

Require list methods `get_record_headers`, `get_record_rows`, `open_add_record`, `select_record`, `delete_selected`, `open_field_settings`, `open_blood_pressure_watch`, `confirm`, and `is_confirmed`.

Require the iframe dialog to fill `tx_jcjl_time`, `tx_jcjl_mb`, `tx_jcjl_hx`, both blood pressures, blood flow, three pressures, ultrafiltration rate/volume, conductivity, KT/V, blood temperature, replacement values, sodium, symptoms, treatment, and result, then cancel without saving.

- [ ] **Step 2: Verify RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\test_monitoring_records_section.py -v --basetemp C:\tmp\webtest-monitoring-red`

Expected: FAIL because the new module and dialog API do not exist.

- [ ] **Step 3: Implement list and dialog**

Use field names captured in the design document. `MonitoringRecordDialog` inherits `LayuiIframeDialog`, uses `TITLE = "监测记录"`, and provides `fill_record`, `expect_readonly_values`, `confirm`, and `cancel`.

- [ ] **Step 4: Verify GREEN**

Run the Step 2 command. Expected: all selected tests pass.

### Task 6: 透后评估 POM

**Files:**
- Create: `pages/hemodialysis/post_dialysis_assessment_section.py`
- Create: `tests/test_post_dialysis_assessment_section.py`

- [ ] **Step 1: Write failing test**

Require `fill_assessment`, `expect_calculated_values`, `confirm`, and `is_confirmed`. The editable map includes vital signs, `txh_sjcll`, `txh_sjzhl`, `txh_sjsc_h`, `txh_sjsc_f`, `#txh_czfs`, `txh_cz`, `tx_peel_weight_h`, `tx_sjcll`, `tx_fyl`, `tx_qt`, `tx_max_ll`, `tx_twxhlx`, `tx_lxjl`, `tx_sscd`, `tx_xgwz`, and `tx_fsyy_sj`.

- [ ] **Step 2: Verify RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\test_post_dialysis_assessment_section.py -v --basetemp C:\tmp\webtest-post-assessment-red`

Expected: FAIL because the module does not exist.

- [ ] **Step 3: Implement POM**

Add the editable map above, calculated map from the approved design, select handling for respiration type, blood pressure site, and weighing method, plus confirmation methods and Chinese ownership comments.

- [ ] **Step 4: Verify GREEN**

Run the Step 2 command. Expected: all selected tests pass.

### Task 7: 治疗小结 POM

**Files:**
- Create: `pages/hemodialysis/treatment_summary_section.py`
- Create: `tests/test_treatment_summary_section.py`

- [ ] **Step 1: Write failing test**

Require `fill_summary`, `expect_readonly_values`, `sync_to_medical_record`, `sync_to_handover_log`, `confirm`, and `is_confirmed`. `fill_summary` must cover text fields `tx_zlxj_content`, `tx_zlxj_xj`, `tx_txq_no` and all ten selects listed in the approved design.

- [ ] **Step 2: Verify RED**

Run: `.\.venv\Scripts\python.exe -m pytest tests\test_treatment_summary_section.py -v --basetemp C:\tmp\webtest-treatment-summary-red`

Expected: FAIL because the module does not exist.

- [ ] **Step 3: Implement POM**

Map all fields exactly as documented, restrict buttons to the treatment summary table, and add Chinese ownership comments.

- [ ] **Step 4: Verify GREEN**

Run the Step 2 command. Expected: all selected tests pass.

### Task 8: 聚合对象、导入清理和回归验证

**Files:**
- Modify: `pages/hemodialysis/dialysis_sheet_page.py`
- Modify: `pages/hemodialysis/__init__.py`
- Delete: `pages/hemodialysis/remaining_sections.py`
- Modify: `tests/test_dialysis_sheet_sections.py`

- [ ] **Step 1: Update imports**

Import `DoubleCheckSection`, `MonitoringRecordsSection`, `PostDialysisAssessmentSection`, and `TreatmentSummarySection` from their dedicated modules. Preserve the existing `DialysisSheetPage` property names so future main-flow code remains:

```python
dialysis_sheet.pre_dialysis_assessment
dialysis_sheet.temporary_orders
dialysis_sheet.double_check
dialysis_sheet.monitoring_records
dialysis_sheet.post_dialysis_assessment
dialysis_sheet.treatment_summary
```

- [ ] **Step 2: Extend readonly real-page smoke assertions**

Assert every section exposes its expected primary controls without clicking them: confirm buttons, add-order/add-monitor buttons, checker select, and summary content fields.

- [ ] **Step 3: Run focused simulated suite**

Run: `.\.venv\Scripts\python.exe -m pytest tests\test_prescription_section.py tests\test_pre_dialysis_assessment_section.py tests\test_temporary_orders_section.py tests\test_double_check_section.py tests\test_monitoring_records_section.py tests\test_post_dialysis_assessment_section.py tests\test_treatment_summary_section.py -v --basetemp C:\tmp\webtest-remaining-focused`

Expected: all focused tests pass.

- [ ] **Step 4: Run non-writing regression**

Run: `.\.venv\Scripts\python.exe -m pytest tests -v -k "not main_write" --basetemp C:\tmp\webtest-remaining-regression`

Expected: all collected non-writing tests pass. `main_write.py` is not collected by the configured `test_*.py` pattern.

- [ ] **Step 5: Compile all changed Python files**

Run: `.\.venv\Scripts\python.exe -m compileall -q pages\hemodialysis tests`

Expected: exit code 0 with no output.

本项目没有 `.git` 目录，因此不包含 Git 提交、分支合并或工作树清理步骤。

