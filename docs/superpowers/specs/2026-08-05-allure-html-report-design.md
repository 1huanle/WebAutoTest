# Allure HTML 报告设计

## 目标

在保留现有 pytest 运行入口的前提下，为项目提供一条独立命令，将 `reports/allure-results/` 中的原始结果生成并打开可浏览的 Allure HTML 报告。

## 组件

- 在 `tools/` 下安装 Allure Commandline，使用项目内的 `allure.bat`，不依赖系统 PATH。
- 新增 `generate_report.py`：检查原始结果目录和 Allure 可执行文件，清理并生成 `reports/allure-report/`，随后调用 `allure open` 打开本地报告服务。
- 更新 `docs/项目运行流程.md`，记录生成报告的命令和工具位置。

## 数据流

pytest 继续依据 `pytest.ini` 将测试结果写入 `reports/allure-results/`。用户随后运行 `python generate_report.py`，脚本将原始结果转换为静态 HTML 文件写入 `reports/allure-report/`，并由 Allure 启动本地服务供浏览器查看。

## 错误处理

- 原始结果目录为空时，脚本提示先执行测试并返回非零状态。
- 本地 Allure 工具不存在时，脚本提示重新执行安装步骤并返回非零状态。
- Allure 生成命令失败时，脚本保留命令输出并返回其退出码。

## 验证

- 执行至少一个 pytest 用例产生原始结果。
- 运行报告脚本，确认 `reports/allure-report/index.html` 存在。
- 验证报告目录含 Allure 静态资源，且脚本返回成功。
