# 透析单分区 POM Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将主任角色透析单中的血液透析业务分区封装为可读、可测试且带中文注释的 POM 组件。

**Architecture:** `DialysisSheetPage` 负责患者列表和页面级数据；各业务分区通过独立组件读取本页 DOM。测试仅断言可见状态和只读数据，不发起医疗数据写入。

**Tech Stack:** Python 3.12、pytest、pytest-playwright 同步 API。

---

### Task 1: 实现透析单页面对象

- [ ] 先运行 `tests/test_hemodialysis_module.py::test_dialysis_sheet_exposes_schedule_and_patient_search`，确认因 POM 不存在而失败。
- [ ] 新建 `pages/hemodialysis/dialysis_sheet_page.py`，封装排班日期、患者搜索框与患者表格行数。
- [ ] 重跑该测试并确认通过。

### Task 2: 实现透析处方与透前评估分区

- [ ] 在 `tests/test_dialysis_sheet_sections.py` 写入两个失败测试，分别断言“透析处方”和“透前评估”区域可见。
- [ ] 新建 `prescription_section.py` 与 `pre_dialysis_assessment_section.py`，提供分区标题、确认状态和可见操作读取方法。
- [ ] 运行两个分区测试并确认通过。

### Task 3: 实现临时医嘱分区

- [ ] 在 `tests/test_dialysis_sheet_sections.py` 写入失败测试，断言“临时医嘱”区域和“添加医嘱、医嘱模板、执行医嘱、删除”可见。
- [ ] 新建 `temporary_orders_section.py`，只封装表格行数和可见操作名称，不调用任何写入操作。
- [ ] 运行临时医嘱分区测试并确认通过。

### Task 4: 扩展其余可见分区与回归

- [ ] 按“分区可见 -> 失败测试 -> 最小 POM -> 测试通过”顺序完成双人核对、监测记录、透后评估和治疗小结。
- [ ] 新建 `docs/血液透析页面清单.md`，标记每个分区所属模块、已覆盖只读元素和测试状态。
- [ ] 使用本机网络权限运行 `./.venv/Scripts/python.exe -m pytest -v` 完成回归验证。
