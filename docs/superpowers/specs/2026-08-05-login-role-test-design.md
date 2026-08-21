# 角色登录测试设计说明

## 目标

为云净血透管理系统增加端到端登录测试：使用 `data` 目录中的测试账号登录，在角色选择框中选择“主任”，并确认进入透析表单页面。

## 数据与安全

- 新建 `data/login_data.yaml`，包含 `username`、`password` 和 `role` 三个字段。
- 该文件含明文测试凭据，必须加入 `.gitignore`。
- 测试仅从 YAML 读取数据，不在测试代码或日志中重复输出凭据。

## 页面对象

- 扩展 `LoginPage`，新增角色选择方法和成功页面等待方法。
- 角色选择以角色名称“主任”为输入；登录成功页面以固定 URL `https://yunjingzhi.com/yunjingservice/user/txform.shtml` 为准。
- 新增方法保留简洁中文注释，并沿用同步 Playwright API。

## 测试

- 新建独立的 `tests/test_login_flow.py`，标记为 `critical`。
- 流程：读取 YAML、打开登录页、执行 `login`、选择“主任”、等待成功页面、断言当前 URL。
- 此测试会向目标站点提交用户明确提供的测试凭据；测试通过后保持在成功页，不执行创建、修改或删除业务数据的操作。
