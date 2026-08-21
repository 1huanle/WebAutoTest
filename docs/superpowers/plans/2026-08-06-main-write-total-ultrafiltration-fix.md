# 主流程总超滤量期望值修复 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让透前评估的总超滤量期望值与当前输入及页面联动结果 `0` 保持一致，使主流程不再因旧截图值 `1` 失败。

**Architecture:** 保留现有 POM 的联动值校验，只修正测试契约和 YAML 数据。先修改测试断言形成明确的值不一致失败，再修改 YAML 使测试通过，不改变主流程或页面定位器。

**Tech Stack:** Python 3.12、pytest、PyYAML、Playwright

---

### Task 1: 修正总超滤量期望值

**Files:**
- Modify: `tests/test_main_write_flow.py:79`
- Modify: `data/main_write.yaml:24`

- [ ] **Step 1: 修改测试期望并形成 RED**

在 `test_main_write_yaml_contains_pre_dialysis_assessment_screenshot_values` 的 `expected` 完整字典中，将：

```python
"total_ultrafiltration": "1",
```

改为：

```python
"total_ultrafiltration": "0",
```

- [ ] **Step 2: 运行目标测试确认失败原因**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_main_write_flow.py::test_main_write_yaml_contains_pre_dialysis_assessment_screenshot_values -v --basetemp C:\tmp\webtest-total-ultrafiltration-red
```

Expected: FAIL，字典差异显示 YAML 实际值仍为 `"1"`，测试期望值为 `"0"`。

- [ ] **Step 3: 修改 YAML 数据**

在 `data/main_write.yaml` 中将：

```yaml
total_ultrafiltration: "1"
```

改为：

```yaml
total_ultrafiltration: "0"
```

- [ ] **Step 4: 运行目标测试确认 GREEN**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_main_write_flow.py::test_main_write_yaml_contains_pre_dialysis_assessment_screenshot_values -v --basetemp C:\tmp\webtest-total-ultrafiltration-green
```

Expected: `1 passed`。

- [ ] **Step 5: 运行相关回归**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_main_write_flow.py tests\test_pre_dialysis_assessment_section.py -v --basetemp C:\tmp\webtest-total-ultrafiltration-focused
```

Expected: `4 passed`，且不收集或运行 `tests/main_write.py`。

- [ ] **Step 6: 运行完整测试套件**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q --basetemp C:\tmp\webtest-total-ultrafiltration-suite
```

Expected: 全部测试通过；`tests/main_write.py` 不符合 pytest 默认 `test_*.py` 文件名模式，因此不会执行真实患者写入。

本项目不是 Git 仓库，因此不包含提交步骤。
