from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STORAGE_STATE_FILE = PROJECT_ROOT / "auth" / "storage_state.json"


def storage_state_path(skip_auth_state: bool = False) -> str | None:
    """返回可供 Playwright 加载的本地登录状态文件路径。"""
    if skip_auth_state or not STORAGE_STATE_FILE.is_file():
        return None
    return str(STORAGE_STATE_FILE)
