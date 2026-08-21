from __future__ import annotations

from pathlib import Path
import subprocess


PROJECT_ROOT = Path(__file__).resolve().parent
RESULTS_DIR = PROJECT_ROOT / "reports" / "allure-results"
REPORT_DIR = PROJECT_ROOT / "reports" / "allure-report"
ALLURE_COMMAND = PROJECT_ROOT / "tools" / "allure-2.44.1" / "bin" / "allure.bat"


def generate_report(open_report: bool = True) -> int:
    """将 Allure 原始结果转换为 HTML 报告，并可选择自动打开。"""
    if not any(RESULTS_DIR.glob("*-result.json")):
        print(f"未找到测试结果：{RESULTS_DIR}。请先运行 pytest。")
        return 1

    if not ALLURE_COMMAND.is_file():
        print(f"未找到 Allure 工具：{ALLURE_COMMAND}。请确认 tools 目录完整。")
        return 1

    result = subprocess.run(
        [str(ALLURE_COMMAND), "generate", str(RESULTS_DIR), "--clean", "-o", str(REPORT_DIR)],
        check=False,
    )
    if result.returncode != 0:
        return result.returncode

    if open_report:
        subprocess.Popen([str(ALLURE_COMMAND), "open", str(REPORT_DIR)])
    return 0


if __name__ == "__main__":
    raise SystemExit(generate_report())
