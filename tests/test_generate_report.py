from unittest.mock import Mock, patch

import generate_report as report


def test_generate_report_returns_error_when_results_are_missing(tmp_path, monkeypatch):
    """原始结果不存在时，报告脚本应停止生成并返回错误状态。"""
    monkeypatch.setattr(report, "RESULTS_DIR", tmp_path / "allure-results")
    monkeypatch.setattr(report, "ALLURE_COMMAND", tmp_path / "allure.bat")

    assert report.generate_report(open_report=False) == 1


def test_generate_report_runs_allure_and_opens_report(tmp_path, monkeypatch):
    """存在原始结果时，报告脚本应调用 Allure 生成并打开 HTML 报告。"""
    results_dir = tmp_path / "allure-results"
    results_dir.mkdir()
    (results_dir / "example-result.json").write_text("{}", encoding="utf-8")
    allure_command = tmp_path / "allure.bat"
    allure_command.write_text("", encoding="utf-8")
    report_dir = tmp_path / "allure-report"
    monkeypatch.setattr(report, "RESULTS_DIR", results_dir)
    monkeypatch.setattr(report, "ALLURE_COMMAND", allure_command)
    monkeypatch.setattr(report, "REPORT_DIR", report_dir)

    with patch("generate_report.subprocess.run", return_value=Mock(returncode=0)) as run:
        with patch("generate_report.subprocess.Popen") as open_report:
            assert report.generate_report() == 0

    run.assert_called_once_with(
        [str(allure_command), "generate", str(results_dir), "--clean", "-o", str(report_dir)],
        check=False,
    )
    open_report.assert_called_once_with([str(allure_command), "open", str(report_dir)])
