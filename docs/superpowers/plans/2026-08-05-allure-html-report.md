# Allure HTML 报告 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让用户可在测试结束后通过一条 Python 命令生成并打开 Allure HTML 报告。

**Architecture:** pytest 继续只写入 `reports/allure-results/`。新增的 `generate_report.py` 负责调用项目内 `tools/allure-2.35.1/bin/allure.bat`，将原始结果生成至 `reports/allure-report/`，成功后启动 Allure 本地报告服务。

**Tech Stack:** Python 3.12、pytest、allure-pytest、Allure Commandline 2.35.1、Java 8。

---

### Task 1: 安装项目内 Allure Commandline

**Files:**
- Create: `tools/allure-2.35.1/`

- [ ] **Step 1: 下载官方发行包**

Run:

```powershell
Invoke-WebRequest -Uri "https://github.com/allure-framework/allure2/releases/download/2.35.1/allure-2.35.1.zip" -OutFile "$env:TEMP\allure-2.35.1.zip"
Expand-Archive -LiteralPath "$env:TEMP\allure-2.35.1.zip" -DestinationPath "tools" -Force
```

Expected: `tools/allure-2.35.1/bin/allure.bat` 存在。

- [ ] **Step 2: 验证 Allure 可执行文件**

Run: `& .\\tools\\allure-2.35.1\\bin\\allure.bat --version`

Expected: 输出 `2.35.1`，退出码为 0。

### Task 2: 以测试先行方式添加报告脚本

**Files:**
- Create: `tests/test_generate_report.py`
- Create: `generate_report.py`

- [ ] **Step 1: 写入失败测试**

创建空结果目录时，测试 `generate_report.generate_report(open_report=False)` 返回 1，且不调用 `subprocess.run`：

```python
def test_generate_report_returns_error_when_results_are_missing(tmp_path, monkeypatch, mocker):
    monkeypatch.setattr(report, "RESULTS_DIR", tmp_path / "allure-results")
    monkeypatch.setattr(report, "ALLURE_COMMAND", tmp_path / "allure.bat")
    run = mocker.patch("generate_report.subprocess.run")

    assert report.generate_report(open_report=False) == 1
    run.assert_not_called()
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `.venv\\Scripts\\python.exe -m pytest tests/test_generate_report.py -v`

Expected: FAIL，因为 `generate_report` 模块不存在。

- [ ] **Step 3: 编写最小报告脚本**

创建 `generate_report.py`，定义 `RESULTS_DIR`、`REPORT_DIR`、`ALLURE_COMMAND` 和 `generate_report(open_report: bool = True) -> int`。函数按以下顺序执行：检查 `*-result.json` 是否存在、检查 `allure.bat` 是否存在、运行 `allure generate <results> --clean -o <report>`、在成功后以 `allure open <report>` 启动本地报告服务。

- [ ] **Step 4: 运行报告脚本测试并确认通过**

Run: `.venv\\Scripts\\python.exe -m pytest tests/test_generate_report.py -v`

Expected: PASS。

### Task 3: 更新运行文档并验证 HTML 报告

**Files:**
- Modify: `docs/项目运行流程.md`

- [ ] **Step 1: 更新报告操作说明**

将报告生成命令替换为：

```powershell
.\\.venv\\Scripts\\python.exe generate_report.py
```

补充说明该脚本依赖项目内 `tools/allure-2.35.1/`，测试执行成功或失败后均可读取 `allure-results` 生成报告。

- [ ] **Step 2: 运行报告脚本验证输出**

Run: `.venv\\Scripts\\python.exe generate_report.py`

Expected: `reports/allure-report/index.html` 存在，浏览器打开 Allure 报告。

- [ ] **Step 3: 提交变更**

当前目录不是 Git 仓库；跳过提交。若后续在 Git 工作树中执行，使用：

```bash
git add generate_report.py tests/test_generate_report.py docs/项目运行流程.md tools/allure-2.35.1
git commit -m "feat: add local Allure HTML report generator"
```
