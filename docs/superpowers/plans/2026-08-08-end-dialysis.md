# 结束透析自动化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在双人核对完成后，自动打开结束透析弹窗，填写下机护士和回血流量并确认结束透析。

**Architecture:** 新增一个继承 `LayuiIframeDialog` 的 `EndDialysisDialog`，由它封装 iframe 内的填写、确认和关闭等待。`DialysisSheetPage` 只提供打开弹窗的入口，`tests/main_write.py` 从 YAML 读取数据并编排该步骤。

**Tech Stack:** Python 3.12、pytest、Playwright Sync API、PyYAML。

---

### Task 1: 结束透析弹窗页面对象

**Files:**
- Create: `pages/hemodialysis/dialogs/end_dialysis_dialog.py`
- Modify: `pages/hemodialysis/dialysis_sheet_page.py`
- Create: `tests/test_end_dialysis_dialog.py`

- [ ] **Step 1: 写入失败的弹窗交互测试**

在 `tests/test_end_dialysis_dialog.py` 构造标题为“结束透析”的 Layui iframe 弹窗，iframe 内放置自动生成的结束时间、文本“下机护士:”后的下拉框、文本“回血(mL/min):”后的数字输入框和“确认”按钮。测试期望：

```python
dialog = DialysisSheetPage(page).open_end_dialysis_dialog()
dialog.fill_end_dialysis({"off_machine_nurse": "陈奕源", "blood_return_flow": "5"})

assert frame.locator('input[name="end_time"]').input_value() == "15:30"
assert frame.locator('select[name="off_machine_nurse"]').input_value() == "陈奕源"
assert frame.locator('input[name="blood_return_flow"]').input_value() == "5"
dialog.confirm()
assert dialog.is_closed()
```

夹具中的结束时间输入框设为只读；确认按钮关闭该弹窗和 `#layui-layer-shade6`。按钮入口使用 `id="open-end"`，文本为“结束透析”。

- [ ] **Step 2: 运行测试并确认失败**

运行：

```powershell
& '.venv\Scripts\python.exe' -m pytest tests/test_end_dialysis_dialog.py --no-header --no-summary -q
```

预期：失败，原因是 `DialysisSheetPage.open_end_dialysis_dialog` 和 `EndDialysisDialog` 尚未实现。

- [ ] **Step 3: 实现弹窗对象和页面入口**

创建 `pages/hemodialysis/dialogs/end_dialysis_dialog.py`：

```python
from .layui_iframe_dialog import LayuiIframeDialog


class EndDialysisDialog(LayuiIframeDialog):
    TITLE = "结束透析"

    def _field_after_label(self, label: str, selector: str):
        return self._frame().locator(
            f"xpath=//*[contains(normalize-space(), '{label}')]/following::{selector}[1]"
        )

    def fill_end_dialysis(self, data: dict[str, str]) -> "EndDialysisDialog":
        self._field_after_label("下机护士", "select").select_option(
            label=data["off_machine_nurse"]
        )
        self._field_after_label("回血(mL/min)", "input").fill(
            data["blood_return_flow"]
        )
        return self

    def confirm(self) -> "EndDialysisDialog":
        self._frame().get_by_role("button", name="确认", exact=True).click()
        self._wait_for_closed()
        return self
```

在 `pages/hemodialysis/dialysis_sheet_page.py` 导入类并添加：

```python
@property
def end_dialysis_dialog(self) -> EndDialysisDialog:
    return EndDialysisDialog(self.page)

def open_end_dialysis_dialog(self) -> EndDialysisDialog:
    dialog = self.end_dialysis_dialog
    self.page.get_by_role("button", name="结束透析", exact=True).click()
    return dialog.wait_for_open()
```

- [ ] **Step 4: 运行弹窗测试并确认通过**

运行：

```powershell
& '.venv\Scripts\python.exe' -m pytest tests/test_end_dialysis_dialog.py --no-header --no-summary -q
```

预期：通过；结束时间保持夹具的 `15:30` 未被修改。

### Task 2: 主流程数据和结束透析编排

**Files:**
- Modify: `data/main_write.yaml`
- Modify: `tests/main_write.py`
- Modify: `tests/test_main_write_flow.py`

- [ ] **Step 1: 写入失败的配置和流程测试**

在 `tests/test_main_write_flow.py` 断言 YAML 新节：

```python
assert data["end_dialysis"] == {
    "off_machine_nurse": "陈奕源",
    "blood_return_flow": "5",
}
```

扩展 `RecordingDialysisSheet`：

```python
self.end_dialysis_dialog = RecordingSection("end_dialysis", self.calls)

def open_end_dialysis_dialog(self):
    self.calls.append(("sheet.open_end_dialysis_dialog", None))
    return self.end_dialysis_dialog
```

扩展 `RecordingSection`：

```python
def fill_end_dialysis(self, data):
    self.calls.append((f"{self.name}.fill_end_dialysis", data))
    return self
```

两个正常流程的 `test_data` 加入 `end_dialysis`，并在每个预期调用序列的双人核对调用之后添加：

```python
("sheet.open_end_dialysis_dialog", None),
("end_dialysis.fill_end_dialysis", {"off_machine_nurse": "陈奕源", "blood_return_flow": "5"}),
("end_dialysis.confirm", None),
("end_dialysis.dialog.is_closed", None),
```

- [ ] **Step 2: 运行流程测试并确认失败**

运行：

```powershell
& '.venv\Scripts\python.exe' -m pytest tests/test_main_write_flow.py --no-header --no-summary -q
```

预期：失败，原因是 YAML 缺少 `end_dialysis`，且主流程尚未打开或填写结束透析弹窗。

- [ ] **Step 3: 添加数据并接入主流程**

在 `data/main_write.yaml` 添加：

```yaml
end_dialysis:
  off_machine_nurse: 陈奕源
  blood_return_flow: "5"
```

在 `tests/main_write.py` 的双人核对步骤后添加逐行中文注释的编排代码：

```python
end_dialysis_dialog = dialysis_sheet.open_end_dialysis_dialog()
end_dialysis_dialog.fill_end_dialysis(test_data["end_dialysis"])
end_dialysis_dialog.confirm()
end_dialysis_dialog.is_closed()
```

不要添加结束时间配置，也不要调用任何结束时间字段。

- [ ] **Step 4: 运行流程测试并确认通过**

运行：

```powershell
& '.venv\Scripts\python.exe' -m pytest tests/test_main_write_flow.py --no-header --no-summary -q
```

预期：通过，结束透析位于双人核对之后。

### Task 3: 聚焦回归验证

**Files:**
- Test: `tests/test_end_dialysis_dialog.py`
- Test: `tests/test_main_write_flow.py`
- Test: `tests/test_double_check_section.py`

- [ ] **Step 1: 运行聚焦回归测试**

运行：

```powershell
& '.venv\Scripts\python.exe' -m pytest tests/test_end_dialysis_dialog.py tests/test_main_write_flow.py tests/test_double_check_section.py --no-header --no-summary -q
```

预期：全部通过。

- [ ] **Step 2: 进行语法检查**

运行：

```powershell
& '.venv\Scripts\python.exe' -m py_compile pages/hemodialysis/dialogs/end_dialysis_dialog.py pages/hemodialysis/dialysis_sheet_page.py tests/main_write.py
```

预期：退出码为 `0`。
