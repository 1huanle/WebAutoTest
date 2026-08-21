# 双人核对实现计划

> **供智能体执行：** 必须使用 `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans`，逐项完成此计划。使用复选框（`- [ ]`）跟踪进度。

**目标：** 在主写入流程中加入已确认的双人核对步骤。

**架构：** 复用 `DoubleCheckSection`，将四个配置组标记为正确，选择配置的核对人，确认分区并验证其状态。将选择内容保存在 `data/main_write.yaml`，避免依赖固定 UI 坐标。

**技术栈：** Python 3.12、pytest、Playwright、PyYAML。

---

### 任务 1：定义双人核对数据

**文件：**
- 修改：`data/main_write.yaml`
- 测试：`tests/test_main_write_flow.py`

- [ ] **步骤 1：编写失败的数据断言**

```python
assert data["double_check"] == {
    "correct_groups": [
        "dialysis_items",
        "dialysis_parameters",
        "vascular_access",
        "pipeline_connection",
    ],
    "checker": "陈奕源",
}
```

- [ ] **步骤 2：运行测试并确认其失败**

运行：`pytest tests/test_main_write_flow.py -q`

预期：失败，因为 YAML 数据中尚不存在 `double_check`。

- [ ] **步骤 3：添加 YAML 配置**

```yaml
double_check:
  correct_groups:
    - dialysis_items
    - dialysis_parameters
    - vascular_access
    - pipeline_connection
  checker: 陈奕源
```

- [ ] **步骤 4：运行测试并确认其通过**

运行：`pytest tests/test_main_write_flow.py -q`

预期：通过。

### 任务 2：加入主流程双人核对

**文件：**
- 修改：`tests/main_write.py`
- 测试：`tests/test_main_write_flow.py`

- [ ] **步骤 1：编写失败的流程调用预期**

```python
("double_check.mark_group_correct", "dialysis_items"),
("double_check.mark_group_correct", "dialysis_parameters"),
("double_check.mark_group_correct", "vascular_access"),
("double_check.mark_group_correct", "pipeline_connection"),
("double_check.select_checker", "陈奕源"),
("double_check.confirm", None),
("double_check.is_confirmed", None),
```

- [ ] **步骤 2：运行测试并确认其失败**

运行：`pytest tests/test_main_write_flow.py::test_execute_main_write_confirms_assessment_before_filling_prescription -q`

预期：失败，因为主流程尚未操作双人核对分区。

- [ ] **步骤 3：加入双人核对流程**

```python
double_check = dialysis_sheet.double_check
for group in test_data["double_check"]["correct_groups"]:
    double_check.mark_group_correct(group)
double_check.select_checker(test_data["double_check"]["checker"])
double_check.confirm()
if not double_check.is_confirmed():
    raise AssertionError("双人核对确认失败，主流程已停止")
```

- [ ] **步骤 4：运行流程测试并确认其通过**

运行：`pytest tests/test_main_write_flow.py::test_execute_main_write_confirms_assessment_before_filling_prescription -q`

预期：通过。

### 任务 3：验证分区交互

**文件：**
- 测试：`tests/test_double_check_section.py`

- [ ] **步骤 1：运行分区交互测试**

运行：`pytest tests/test_double_check_section.py -q`

预期：通过，确认复选框标签、核对人选择和确认操作都限定在双人核对分区内。

- [ ] **步骤 2：运行聚焦回归测试**

运行：`pytest tests/test_main_write_flow.py tests/test_double_check_section.py -q`

预期：通过。
