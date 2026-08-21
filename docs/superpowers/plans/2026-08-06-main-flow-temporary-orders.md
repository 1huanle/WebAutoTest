# 主流程临时医嘱新增与逐条执行 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在开始透析完成后新增两条指定临时医嘱，并对当前全部未执行医嘱逐条执行。

**Architecture:** `TemporaryOrderDialog` 处理真实自动补全字段，新增 `TemporaryOrderExecutionDialog` 封装执行弹窗，`TemporaryOrdersSection` 负责快照未执行 ID 并编排逐条操作。`execute_main_write()` 仅调用新增和批量执行两个高层接口。

**Tech Stack:** Python 3.12、pytest、PyYAML、Playwright Page Object Model

---

### Task 1: 测试数据和主流程契约

**Files:**
- Modify: `tests/test_main_write_flow.py`
- Modify: `data/main_write.yaml`
- Modify: `tests/main_write.py`

- [ ] **Step 1: 增加 YAML 红灯测试**

断言 `temporary_orders.orders` 包含两条截图数据，第二条不包含 `administration_route` 和 `frequency`；断言 `temporary_orders.execution` 为执行人员、核对人员均为陈奕源且备注为空。

- [ ] **Step 2: 扩展记录型主流程红灯测试**

为 `RecordingSection` 增加 `add_orders()` 和 `execute_all_unexecuted()` 事件，期望它们发生在 `start.dialog.is_closed` 之后。

- [ ] **Step 3: 运行红灯测试**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_main_write_flow.py -v --basetemp C:\tmp\webtest-temporary-main-red
```

Expected: YAML 键缺失，成功路径缺少临时医嘱事件。

### Task 2: 新增医嘱自动补全 POM

**Files:**
- Modify: `tests/test_temporary_orders_section.py`
- Modify: `pages/hemodialysis/dialogs/temporary_order_dialog.py`
- Modify: `pages/hemodialysis/temporary_orders_section.py`

- [ ] **Step 1: 创建真实字段类型的新增弹窗测试**

本地 iframe 使用 `tx_advicename`、`tx_wayadminister`、`tx_frequency` 输入框和候选浮层。选择医嘱候选后更新 `tx_advicedescript`，底部确认关闭所属弹窗与遮罩。

- [ ] **Step 2: 运行测试确认 RED**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_temporary_orders_section.py -v --basetemp C:\tmp\webtest-temporary-add-red
```

Expected: 当前代码把给药途径和执行频率当作 `<select>`，测试失败。

- [ ] **Step 3: 实现自动补全和 `add_orders()`**

`fill_order()` 对 `order_name` 使用 `order_option` 选择候选，对可选的给药途径和执行频率使用精确同名候选。`add_orders()` 逐条打开弹窗、填写、校验 `expected` 只读值并确认。

- [ ] **Step 4: 运行新增弹窗测试确认 GREEN**

重复 Step 2 命令，Expected: 新增相关测试通过。

### Task 3: 执行医嘱弹窗和动态循环

**Files:**
- Create: `pages/hemodialysis/dialogs/temporary_order_execution_dialog.py`
- Modify: `pages/hemodialysis/dialogs/__init__.py`
- Modify: `pages/hemodialysis/temporary_orders_section.py`
- Modify: `tests/test_temporary_orders_section.py`

- [ ] **Step 1: 创建动态未执行列表测试**

本地列表包含三条 `data-zxsj=""` 和一条非空记录；每次点击执行按钮打开标题为“执行医嘱”的 iframe。执行按钮更新当前 ID 的 `data-zxsj` 并关闭弹窗，测试断言三个初始未执行 ID 各执行一次、已执行 ID 为零次。

- [ ] **Step 2: 运行测试确认 RED**

Expected: `TemporaryOrderExecutionDialog` 和 `execute_all_unexecuted()` 尚不存在。

- [ ] **Step 3: 实现执行弹窗 POM**

用 `tx_lsyz_zxsj`、`tx_lsyz_qm_nurse`、`tx_lsyz_hd_nurse` 和 `tx_yznote` 定位字段；校验人员、填写可选备注、点击按钮“执行”并等待关闭。

- [ ] **Step 4: 实现按 ID 快照逐条执行**

从 `.tx_yz_checkbox[data-zxsj=""]` 读取非空 `data-yzid`，逐 ID 清理已勾选状态、勾选目标、打开执行弹窗并执行，最后确认目标不再未执行。

- [ ] **Step 5: 运行测试确认 GREEN**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_temporary_orders_section.py -v --basetemp C:\tmp\webtest-temporary-execute-green
```

Expected: 临时医嘱测试全部通过。

### Task 4: 接入 YAML 和主流程

**Files:**
- Modify: `data/main_write.yaml`
- Modify: `tests/main_write.py`

- [ ] **Step 1: 写入两条医嘱和执行数据**

在 `main_write.yaml` 增加 `temporary_orders.orders` 与 `temporary_orders.execution`，不配置第二条的给药途径、执行频率、执行科室和诊断。

- [ ] **Step 2: 编排主流程**

在开始透析弹窗关闭后调用：

```python
temporary_orders = dialysis_sheet.temporary_orders
temporary_orders.add_orders(test_data["temporary_orders"]["orders"])
temporary_orders.execute_all_unexecuted(
    test_data["temporary_orders"]["execution"]
)
```

- [ ] **Step 3: 运行主流程测试确认 GREEN**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_main_write_flow.py -v --basetemp C:\tmp\webtest-temporary-main-green
```

Expected: 全部通过。

### Task 5: 非写入回归验证

**Files:**
- Verify: `pages/hemodialysis/dialogs/temporary_order_dialog.py`
- Verify: `pages/hemodialysis/dialogs/temporary_order_execution_dialog.py`
- Verify: `pages/hemodialysis/temporary_orders_section.py`
- Verify: `tests/main_write.py`
- Verify: `tests/test_main_write_flow.py`
- Verify: `tests/test_temporary_orders_section.py`

- [ ] **Step 1: 运行聚焦测试**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_temporary_orders_section.py tests\test_main_write_flow.py tests\test_start_dialysis_dialog.py -v --basetemp C:\tmp\webtest-temporary-focused
```

- [ ] **Step 2: 编译变更文件**

```powershell
.\.venv\Scripts\python.exe -m compileall -q pages\hemodialysis\dialogs pages\hemodialysis\temporary_orders_section.py tests\main_write.py tests\test_main_write_flow.py tests\test_temporary_orders_section.py
```

- [ ] **Step 3: 运行完整测试套件**

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q --basetemp C:\tmp\webtest-temporary-suite
```

Expected: 全部测试通过，且不收集 `tests/main_write.py`。

本项目不是 Git 仓库，因此不包含提交、分支或 worktree 步骤。
