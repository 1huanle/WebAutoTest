import runpy
from pathlib import Path
from unittest.mock import patch

import pytest


RUN_FILE = Path(__file__).resolve().parents[1] / "run.py"


def test_run_uses_headless_value_from_dotenv(monkeypatch):
    """验证运行入口会将环境变量中的无头模式传递给 pytest。"""
    # 移除进程环境变量，验证 run.py 使用 dotenv 中的默认配置。
    monkeypatch.delenv("HEADLESS", raising=False)

    # 模拟 pytest 子进程，避免测试时真正执行完整测试集。
    with patch("subprocess.call", return_value=0) as subprocess_call:
        with pytest.raises(SystemExit) as exit_info:
            runpy.run_path(str(RUN_FILE), run_name="__main__")

    # 运行入口应正常退出，并向子进程传递无头模式配置。
    assert exit_info.value.code == 0
    assert subprocess_call.call_args.kwargs["env"]["HEADLESS"] == "false"


@pytest.mark.parametrize(
    ("target_env", "expected_url"),
    [
        ("online", "https://yunjingzhi.com/yunjingservice/user/txform.shtml"),
        ("test", "https://develop.yunjingzhi.com/yunjingservice/user/txform.shtml"),
        ("pre", "https://pre.yunjingzhi.com/yunjingservice/user/txform.shtml"),
    ],
)
def test_run_target_env_sets_base_url(monkeypatch, target_env, expected_url):
    """启动命令的目标环境应覆盖子进程的 BASE_URL。"""
    monkeypatch.setattr(
        "sys.argv", [str(RUN_FILE), "--target-env", target_env, "tests/main_write.py"]
    )

    with patch("subprocess.call", return_value=0) as subprocess_call:
        with pytest.raises(SystemExit) as exit_info:
            runpy.run_path(str(RUN_FILE), run_name="__main__")

    assert exit_info.value.code == 0
    assert subprocess_call.call_args.kwargs["env"]["BASE_URL"] == expected_url
    assert subprocess_call.call_args.args[0][-1] == "tests/main_write.py"
