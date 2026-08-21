# 主流程开始透析弹窗 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在透前评估和透析处方确认成功后，自动打开“开始透析”弹窗，按 YAML 数据填写、确认并校验弹窗关闭。

**Architecture:** 新增继承 `LayuiIframeDialog` 的 `StartDialysisDialog`，用真实页面稳定的 `name` 属性定位字段，并封装只读穿刺字典字段的“点选选项后保存”交互。`DialysisSheetPage` 负责打开弹窗，`execute_main_write()` 只负责编排严格业务顺序。

**Tech Stack:** Python 3.12、pytest、PyYAML、Playwright Page Object Model

---

### Task 1: 开始透析弹窗 POM

**Files:**
- Create: `pages/hemodialysis/dialogs/start_dialysis_dialog.py`
- Modify: `pages/hemodialysis/dialogs/__init__.py`
- Modify: `pages/hemodialysis/dialysis_sheet_page.py`
- Create: `tests/test_start_dialysis_dialog.py`

- [ ] **Step 1: 创建失败的本地 iframe 弹窗测试**

创建 `tests/test_start_dialysis_dialog.py`。测试页面包含：

- 页面顶部“开始透析”按钮。
- `times="4"` 的隐藏 `.layui-layer` 和 `#layui-layer-shade4`。
- 弹层 iframe 内包含以下真实字段：`tx_zl_nurse`、`tx_sjhs`、`tx_ycgl`、`tx_fs`、`tx_sj_nurse`、`tx_ccfs`、`tx_ccz`、`tx_cczxh`、`tx_ccfx`、`tx_ccwd`、`tx_yx`、`tx_txq_no`、`tx_rkfs`。
- 四个只读穿刺字段点击后显示 `role="dialog"` 的选择浮层；选项按钮更新待选值，点击“保存”写回原输入框并关闭浮层。
- iframe 底部“确认”按钮删除弹层和对应遮罩，并在父页面增加 `#start-dialysis-confirmed`。

fixture 使用以下完整实现：

```python
import pytest

from pages.hemodialysis.dialysis_sheet_page import DialysisSheetPage


def install_start_dialysis_fixture(page) -> None:
    """构造只在本地运行的开始透析 iframe 弹窗。"""
    page.set_content(
        """
        <button type="button" id="open-start">开始透析</button>
        <div id="layui-layer-shade4" style="display:none"></div>
        <div id="layui-layer4" times="4" class="layui-layer" style="display:none">
          <h2>开始透析</h2>
          <iframe title="开始透析内容"></iframe>
        </div>
        <script>
          const layer = document.querySelector('#layui-layer4');
          const shade = document.querySelector('#layui-layer-shade4');
          document.querySelector('#open-start').addEventListener('click', () => {
            layer.style.display = 'block';
            shade.style.display = 'block';
          });

          const frameDocument = layer.querySelector('iframe').contentDocument;
          frameDocument.body.innerHTML = `
            <select name="tx_zl_nurse"><option></option><option>陈奕源</option></select>
            <select name="tx_sjhs"><option></option><option>陈奕源</option></select>
            <select name="tx_ycgl"><option></option><option>陈奕源</option></select>
            <select name="tx_fs"><option value="1">换药</option><option value="0">穿刺</option></select>
            <select name="tx_sj_nurse"><option></option><option>陈奕源</option></select>
            <input name="tx_ccfs" class="info-input" readonly>
            <input name="tx_ccz" class="info-input" readonly>
            <input name="tx_cczxh" class="info-input" readonly>
            <input name="tx_ccfx" class="info-input" readonly>
            <input name="tx_ccwd" readonly>
            <input name="tx_yx" type="number">
            <input name="tx_txq_no">
            <select name="tx_rkfs"><option>步行</option><option>扶行</option></select>
            <div id="choice-dialog" role="dialog" style="display:none">
              <div id="choice-buttons"></div>
              <a href="javascript:void(0)" id="choice-save">保存</a>
            </div>
            <button type="button" id="confirm-start">确认</button>
          `;

          const choices = {
            tx_ccfs: ['无', '扣眼法', '绳梯法'],
            tx_ccz: ['无', 'A锐针', 'A钝针'],
            tx_cczxh: ['A端-15号', 'A端-16号', 'A端-17号'],
            tx_ccfx: ['A端向心', 'A端离心', 'V端向心', 'V端离心'],
          };
          const choiceDialog = frameDocument.querySelector('#choice-dialog');
          const choiceButtons = frameDocument.querySelector('#choice-buttons');
          let targetInput = null;
          let selectedChoice = null;

          frameDocument.querySelectorAll('.info-input').forEach(input => {
            input.addEventListener('click', () => {
              targetInput = input;
              selectedChoice = null;
              choiceButtons.innerHTML = '';
              choices[input.name].forEach(value => {
                const button = frameDocument.createElement('button');
                button.type = 'button';
                button.textContent = value;
                button.addEventListener('click', () => { selectedChoice = value; });
                choiceButtons.appendChild(button);
              });
              choiceDialog.style.display = 'block';
            });
          });

          frameDocument.querySelector('#choice-save').addEventListener('click', () => {
            targetInput.value = selectedChoice;
            choiceDialog.style.display = 'none';
          });
          frameDocument.querySelector('#confirm-start').addEventListener('click', () => {
            layer.style.display = 'none';
            shade.style.display = 'none';
            document.body.insertAdjacentHTML(
              'beforeend', '<div id="start-dialysis-confirmed"></div>'
            );
          });
        </script>
        """
    )
```

测试主体使用以下数据和断言：

```python
@pytest.mark.no_auth_state
def test_fill_and_confirm_start_dialysis_dialog(page):
    """血液透析 > 开始透析：填写指定内容并确认关闭弹窗。"""
    install_start_dialysis_fixture(page)

    dialysis_sheet = DialysisSheetPage(page)
    dialog = dialysis_sheet.open_start_dialysis_dialog()
    dialog.fill_start_dialysis(
        {
            "treatment_nurse": "陈奕源",
            "machine_nurse": "陈奕源",
            "priming_tubing_nurse": "陈奕源",
            "operation_type": "穿刺",
            "puncture_nurse": "陈奕源",
            "puncture_method": "扣眼法",
            "puncture_needle": "A锐针",
            "puncture_needle_model": "A端-17号",
            "puncture_direction": "V端向心",
            "blood_introduction_flow": "5",
            "admission_method": "步行",
        }
    )

    frame = dialog._frame()
    assert frame.locator('[name="tx_zl_nurse"]').input_value() == "陈奕源"
    assert frame.locator('[name="tx_sjhs"]').input_value() == "陈奕源"
    assert frame.locator('[name="tx_ycgl"]').input_value() == "陈奕源"
    assert frame.locator('[name="tx_fs"]').input_value() == "0"
    assert frame.locator('[name="tx_sj_nurse"]').input_value() == "陈奕源"
    assert frame.locator('[name="tx_ccfs"]').input_value() == "扣眼法"
    assert frame.locator('[name="tx_ccz"]').input_value() == "A锐针"
    assert frame.locator('[name="tx_cczxh"]').input_value() == "A端-17号"
    assert frame.locator('[name="tx_ccfx"]').input_value() == "V端向心"
    assert frame.locator('[name="tx_yx"]').input_value() == "5"
    assert frame.locator('[name="tx_rkfs"]').input_value() == "步行"
    assert frame.locator('[name="tx_ccwd"]').input_value() == ""
    assert frame.locator('[name="tx_txq_no"]').input_value() == ""

    dialog.confirm()

    assert page.locator("#start-dialysis-confirmed").count() == 1
    assert dialog.is_closed()
```

- [ ] **Step 2: 运行测试确认 RED**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_start_dialysis_dialog.py -v --basetemp C:\tmp\webtest-start-dialysis-dialog-red
```

Expected: FAIL，因为 `StartDialysisDialog` 和 `open_start_dialysis_dialog()` 尚未实现。

- [ ] **Step 3: 实现弹窗 POM**

创建 `pages/hemodialysis/dialogs/start_dialysis_dialog.py`：

```python
from playwright.sync_api import expect

from .layui_iframe_dialog import LayuiIframeDialog


class StartDialysisDialog(LayuiIframeDialog):
    """血液透析 > 开始透析触发：封装开始透析 iframe 弹窗。"""

    TITLE = "开始透析"
    SELECT_FIELDS = {
        "treatment_nurse": "tx_zl_nurse",
        "machine_nurse": "tx_sjhs",
        "priming_tubing_nurse": "tx_ycgl",
        "operation_type": "tx_fs",
        "puncture_nurse": "tx_sj_nurse",
        "admission_method": "tx_rkfs",
    }
    CHOICE_FIELDS = {
        "puncture_method": "tx_ccfs",
        "puncture_needle": "tx_ccz",
        "puncture_needle_model": "tx_cczxh",
        "puncture_direction": "tx_ccfx",
    }
    INPUT_FIELDS = {"blood_introduction_flow": "tx_yx"}

    def _field(self, name: str):
        """返回开始透析 iframe 内指定 name 的可见字段。"""
        return self._frame().locator(f'[name="{name}"]:visible')

    def _select_business_choice(self, name: str, value: str) -> None:
        """在只读字段的业务选项浮层中选择值并保存。"""
        self._field(name).click()
        choice_dialog = self._frame().get_by_role("dialog")
        expect(choice_dialog).to_be_visible()
        choice_dialog.get_by_role("button", name=value, exact=True).click()
        choice_dialog.get_by_role("link", name="保存", exact=True).click()
        expect(choice_dialog).to_be_hidden()

    def fill_start_dialysis(self, data: dict[str, str]) -> "StartDialysisDialog":
        """填写血液透析 > 开始透析弹窗中的指定内容。"""
        for key, name in self.SELECT_FIELDS.items():
            self._field(name).select_option(label=data[key])
        for key, name in self.CHOICE_FIELDS.items():
            self._select_business_choice(name, data[key])
        for key, name in self.INPUT_FIELDS.items():
            self._field(name).fill(data[key])
        return self

    def confirm(self) -> "StartDialysisDialog":
        """确认开始透析并等待弹窗及所属遮罩关闭。"""
        self._frame().get_by_role("button", name="确认", exact=True).click()
        self._wait_for_closed()
        return self
```

`pages/hemodialysis/dialogs/__init__.py` 导入并将导出列表更新为：

```python
from .monitoring_record_dialog import MonitoringRecordDialog
from .prescription_medical_order_push_dialog import PrescriptionMedicalOrderPushDialog
from .start_dialysis_dialog import StartDialysisDialog
from .temporary_order_dialog import TemporaryOrderDialog

__all__ = [
    "MonitoringRecordDialog",
    "PrescriptionMedicalOrderPushDialog",
    "StartDialysisDialog",
    "TemporaryOrderDialog",
]
```

`pages/hemodialysis/dialysis_sheet_page.py` 导入 `StartDialysisDialog`，并在类内增加：

```python
    @property
    def start_dialysis_dialog(self) -> StartDialysisDialog:
        """返回血液透析 > 开始透析触发的弹窗对象。"""
        return StartDialysisDialog(self.page)

    def open_start_dialysis_dialog(self) -> StartDialysisDialog:
        """点击开始透析并等待对应 iframe 弹窗打开。"""
        dialog = self.start_dialysis_dialog
        self.page.get_by_role("button", name="开始透析", exact=True).click()
        return dialog.wait_for_open()
```

- [ ] **Step 4: 运行弹窗测试确认 GREEN**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_start_dialysis_dialog.py -v --basetemp C:\tmp\webtest-start-dialysis-dialog-green
```

Expected: `1 passed`。

### Task 2: 开始透析 YAML 数据

**Files:**
- Modify: `tests/test_main_write_flow.py`
- Modify: `data/main_write.yaml`

- [ ] **Step 1: 扩展 YAML 测试形成 RED**

在 `test_main_write_yaml_contains_pre_dialysis_assessment_screenshot_values` 后增加：

```python
def test_main_write_yaml_contains_start_dialysis_values():
    """主流程 YAML 应保存开始透析弹窗值，并省略保持空白的字段。"""
    data_path = Path(__file__).parents[1] / "data" / "main_write.yaml"
    data = yaml.safe_load(data_path.read_text(encoding="utf-8"))

    assert data["start_dialysis"] == {
        "treatment_nurse": "陈奕源",
        "machine_nurse": "陈奕源",
        "priming_tubing_nurse": "陈奕源",
        "operation_type": "穿刺",
        "puncture_nurse": "陈奕源",
        "puncture_method": "扣眼法",
        "puncture_needle": "A锐针",
        "puncture_needle_model": "A端-17号",
        "puncture_direction": "V端向心",
        "blood_introduction_flow": "5",
        "admission_method": "步行",
    }
    assert "puncture_site" not in data["start_dialysis"]
    assert "dialyzer_number" not in data["start_dialysis"]
```

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_main_write_flow.py::test_main_write_yaml_contains_start_dialysis_values -v --basetemp C:\tmp\webtest-start-dialysis-yaml-red
```

Expected: FAIL with `KeyError: 'start_dialysis'`。

- [ ] **Step 2: 新增 YAML 数据并确认 GREEN**

在 `data/main_write.yaml` 的 `prescription` 配置后增加：

```yaml
start_dialysis:
  treatment_nurse: 陈奕源
  machine_nurse: 陈奕源
  priming_tubing_nurse: 陈奕源
  operation_type: 穿刺
  puncture_nurse: 陈奕源
  puncture_method: 扣眼法
  puncture_needle: A锐针
  puncture_needle_model: A端-17号
  puncture_direction: V端向心
  blood_introduction_flow: "5"
  admission_method: 步行
```

再次运行 Step 1 命令，Expected: `1 passed`。

### Task 3: 主流程编排开始透析步骤

**Files:**
- Modify: `tests/test_main_write_flow.py`
- Modify: `tests/main_write.py`

- [ ] **Step 1: 扩展记录对象和成功顺序测试形成 RED**

在 `RecordingSection` 增加：

```python
    def fill_start_dialysis(self, data):
        self.calls.append((f"{self.name}.fill_start_dialysis", data))
        return self
```

在 `RecordingDialysisSheet` 中增加 `prescription_confirmed` 参数、开始透析弹窗和打开方法：

```python
    def __init__(self, assessment_confirmed=True, prescription_confirmed=True):
        self.calls = []
        self.pre_dialysis_assessment = RecordingSection(
            "assessment", self.calls, confirmed=assessment_confirmed
        )
        self.prescription = RecordingSection(
            "prescription", self.calls, confirmed=prescription_confirmed
        )
        self.start_dialysis_dialog = RecordingSection("start", self.calls)

    def open_start_dialysis_dialog(self):
        self.calls.append(("sheet.open_start_dialysis_dialog", None))
        return self.start_dialysis_dialog
```

在成功顺序测试数据中增加：

```python
"start_dialysis": {"admission_method": "步行"},
```

在原九步期望事件后增加：

```python
("sheet.open_start_dialysis_dialog", None),
("start.fill_start_dialysis", {"admission_method": "步行"}),
("start.confirm", None),
("start.dialog.is_closed", None),
```

运行成功顺序测试，Expected: FAIL，因为 `execute_main_write()` 尚未调用开始透析弹窗。

- [ ] **Step 2: 增加处方失败保护测试并确认 RED**

```python
def test_execute_main_write_stops_before_start_when_prescription_fails():
    """透析处方确认失败时不得打开开始透析弹窗。"""
    dialysis_sheet = RecordingDialysisSheet(prescription_confirmed=False)
    test_data = {
        "patient": {"dialysis_number": "21000536543"},
        "pre_dialysis_assessment": {
            "editable": {"temperature": "36"},
            "expected": {"dry_weight": "待定"},
        },
        "prescription": {"doctor": "陈奕源"},
        "start_dialysis": {"admission_method": "步行"},
    }

    with pytest.raises(AssertionError, match="透析处方确认失败"):
        main_write.execute_main_write(dialysis_sheet, test_data)

    assert not any(name.startswith("start.") for name, _ in dialysis_sheet.calls)
    assert not any(
        name == "sheet.open_start_dialysis_dialog"
        for name, _ in dialysis_sheet.calls
    )
```

运行该测试，Expected: FAIL，因为当前裸 `assert` 没有中文业务错误信息。

- [ ] **Step 3: 实现开始透析编排**

将 `tests/main_write.py` 的处方确认和开始透析阶段改为：

```python
    prescription.fill_prescription(test_data["prescription"])
    prescription.confirm()
    if not prescription.is_confirmed():
        raise AssertionError("透析处方确认失败，主流程已停止")
    prescription.medical_order_push_dialog.is_closed()

    # 血液透析 > 开始透析：两项前置业务确认后填写并提交弹窗。
    start_dialog = dialysis_sheet.open_start_dialysis_dialog()
    start_dialog.fill_start_dialysis(test_data["start_dialysis"])
    start_dialog.confirm()
    start_dialog.is_closed()
```

同时将 `execute_main_write()` 和真实测试的中文 docstring 更新为包含开始透析步骤。

- [ ] **Step 4: 运行主流程测试确认 GREEN**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_main_write_flow.py -v --basetemp C:\tmp\webtest-start-dialysis-flow-green
```

Expected: 当前文件全部测试通过。

### Task 4: 非写入回归验证

**Files:**
- Verify: `pages/hemodialysis/dialogs/start_dialysis_dialog.py`
- Verify: `pages/hemodialysis/dialysis_sheet_page.py`
- Verify: `data/main_write.yaml`
- Verify: `tests/main_write.py`
- Verify: `tests/test_main_write_flow.py`
- Verify: `tests/test_start_dialysis_dialog.py`

- [ ] **Step 1: 运行聚焦测试**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_start_dialysis_dialog.py tests\test_main_write_flow.py tests\test_pre_dialysis_assessment_section.py tests\test_prescription_section.py -v --basetemp C:\tmp\webtest-start-dialysis-focused
```

Expected: 所有选中测试通过。

- [ ] **Step 2: 编译变更 Python 文件**

```powershell
.\.venv\Scripts\python.exe -m compileall -q pages\hemodialysis\dialogs\start_dialysis_dialog.py pages\hemodialysis\dialysis_sheet_page.py tests\main_write.py tests\test_main_write_flow.py tests\test_start_dialysis_dialog.py
```

Expected: exit code 0，无输出。

- [ ] **Step 3: 运行完整测试套件**

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q --basetemp C:\tmp\webtest-start-dialysis-suite
```

Expected: 全部测试通过。`tests/main_write.py` 不符合 pytest 默认 `test_*.py` 文件名模式，不会自动写入真实患者数据。

本项目不是 Git 仓库，因此不包含提交、分支或 worktree 步骤。
