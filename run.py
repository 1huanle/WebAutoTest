import argparse
import os
import subprocess
import sys
# 123

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="运行云净血透自动化测试")
    parser.add_argument(
        "--target-env",
        choices=("online", "test", "pre"),
        help="目标环境：online=线上，test=测试，pre=预发布",
    )
    arguments, pytest_arguments = parser.parse_known_args()
    environment = {**os.environ, "HEADLESS": os.getenv("HEADLESS", "false")}
    if arguments.target_env:
        environment["TEST_ENV"] = arguments.target_env
        environment["BASE_URL"] = {
            "online": "https://yunjingzhi.com/yunjingservice/user/txform.shtml",
            "test": "https://develop.yunjingzhi.com/yunjingservice/user/txform.shtml",
            "pre": "https://pre.yunjingzhi.com/yunjingservice/user/txform.shtml",
        }[arguments.target_env]
    raise SystemExit(
        subprocess.call(
            [sys.executable, "-m", "pytest", *pytest_arguments], env=environment
        )
    )
