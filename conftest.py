import sys
from pathlib import Path

import allure
import pytest
from dotenv import load_dotenv

from config.config import Config
from utils.auth_state import storage_state_path
from utils.logger import logger

load_dotenv()


def pytest_addoption(parser):
    parser.addoption("--env", action="store", default=Config.ENV, help="test environment")


@pytest.fixture(scope="session")
def env_config(request):
    return {
        "env": request.config.getoption("--env"),
        "base_url": request.config.getoption("--base-url") or Config.BASE_URL,
        "browser": request.config.getoption("--browser") or Config.BROWSER,
        "headless": Config.HEADLESS,
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "headless": Config.HEADLESS,
        "args": ["--disable-blink-features=AutomationControlled", "--no-sandbox"],
    }


@pytest.fixture(scope="function")
def context(browser, request):
    context_options = {
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
        "locale": "zh-CN",
        "timezone_id": "Asia/Shanghai",
        "record_video_dir": str(Config.VIDEO_DIR) if Config.RECORD_VIDEO else None,
    }
    state_file = storage_state_path(
        skip_auth_state=request.node.get_closest_marker("no_auth_state") is not None
    )
    if state_file:
        context_options["storage_state"] = state_file

    context = browser.new_context(**context_options)
    context.set_default_timeout(Config.DEFAULT_TIMEOUT)
    context.set_default_navigation_timeout(Config.NAVIGATION_TIMEOUT)
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context, request):
    page = context.new_page()
    yield page
    report = getattr(request.node, "rep_call", None)
    if report and report.failed:
        attach_screenshot_on_failure(page, request.node.name)
    page.close()


@pytest.fixture(scope="session", autouse=True)
def allure_environment(env_config):
    environment_file = Config.ALLURE_RESULTS_DIR / "environment.properties"
    environment_file.write_text(
        "\n".join(
            (
                f"Environment={env_config['env']}",
                f"BaseURL={env_config['base_url']}",
                f"Browser={env_config['browser']}",
                f"Headless={env_config['headless']}",
                f"Python.Version={sys.version}",
            )
        ),
        encoding="utf-8",
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    setattr(item, f"rep_{call.when}", outcome.get_result())


def attach_screenshot_on_failure(page, test_name: str) -> None:
    screenshot_file = Path(Config.SCREENSHOT_DIR) / f"{test_name}.png"
    try:
        page.screenshot(path=str(screenshot_file), full_page=True)
        allure.attach.file(
            str(screenshot_file),
            name=f"screenshot_{test_name}",
            attachment_type=allure.attachment_type.PNG,
        )
        logger.error("Test failed; screenshot saved to {}", screenshot_file)
    except Exception as error:
        logger.warning("Could not capture failure screenshot: {}", error)
