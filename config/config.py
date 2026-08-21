import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    ENVIRONMENT_URLS = {
        "online": "https://yunjingzhi.com/yunjingservice/user/txform.shtml",
        "test": "https://develop.yunjingzhi.com/yunjingservice/user/txform.shtml",
        "pre": "https://pre.yunjingzhi.com/yunjingservice/user/txform.shtml",
    }
    ENV = os.getenv("TEST_ENV", "online")
    BASE_URL = os.getenv("BASE_URL") or ENVIRONMENT_URLS.get(
        ENV, ENVIRONMENT_URLS["online"]
    )
    BROWSER = os.getenv("BROWSER", "chromium")
    HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
    RECORD_VIDEO = os.getenv("RECORD_VIDEO", "false").lower() == "true"
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "30000"))
    NAVIGATION_TIMEOUT = int(os.getenv("NAVIGATION_TIMEOUT", "60000"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    REPORT_DIR = BASE_DIR / "reports"
    ALLURE_RESULTS_DIR = REPORT_DIR / "allure-results"
    ALLURE_REPORT_DIR = REPORT_DIR / "allure-report"
    SCREENSHOT_DIR = REPORT_DIR / "screenshots"
    VIDEO_DIR = REPORT_DIR / "videos"
    LOG_DIR = BASE_DIR / "logs"

    @classmethod
    def ensure_dirs(cls) -> None:
        for directory in (
            cls.REPORT_DIR,
            cls.ALLURE_RESULTS_DIR,
            cls.ALLURE_REPORT_DIR,
            cls.SCREENSHOT_DIR,
            cls.VIDEO_DIR,
            cls.LOG_DIR,
        ):
            directory.mkdir(parents=True, exist_ok=True)


Config.ensure_dirs()
