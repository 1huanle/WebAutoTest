from utils import auth_state


def test_storage_state_path_returns_none_when_file_is_missing(tmp_path, monkeypatch):
    """状态文件不存在时不应为测试上下文提供登录态。"""
    state_file = tmp_path / "storage_state.json"
    monkeypatch.setattr(auth_state, "STORAGE_STATE_FILE", state_file)

    assert auth_state.storage_state_path() is None


def test_storage_state_path_returns_file_path_when_state_exists(tmp_path, monkeypatch):
    """状态文件存在时应返回供 Playwright 加载的本地路径。"""
    state_file = tmp_path / "storage_state.json"
    state_file.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(auth_state, "STORAGE_STATE_FILE", state_file)

    assert auth_state.storage_state_path() == str(state_file)

def test_storage_state_path_returns_none_when_auth_state_is_skipped(tmp_path, monkeypatch):
    """登录流程可显式跳过已保存状态，确保从登录页开始执行。"""
    state_file = tmp_path / "storage_state.json"
    state_file.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(auth_state, "STORAGE_STATE_FILE", state_file)

    assert auth_state.storage_state_path(skip_auth_state=True) is None
