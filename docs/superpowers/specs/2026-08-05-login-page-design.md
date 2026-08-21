# LoginPage 设计说明

## 目标

为云净血透管理系统登录页创建独立的页面对象，集中维护页面 URL、稳定定位器和登录交互，供 pytest-playwright 用例复用。

## 结构

- 新建 `pages/login_page.py`，定义继承 `BasePage` 的 `LoginPage`。
- 使用页面已确认的稳定 ID：`#userid`、`#userpwd`、`#login-btn`。
- 页面对象公开 `open`、`fill_username`、`fill_password`、`click_login`、`login` 与 `is_loaded` 方法。
- `login` 仅组合填写账号、填写密码和点击登录三个已有操作，不保存或提供真实凭据。

## 测试

- 新建 `tests/test_login_page.py`。
- 测试真实页面能加载，并确认登录页标题与关键控件可见。
- 测试账号和密码填写操作会更新相应输入框的值。
- 测试不提交登录表单，避免在没有测试账号时产生外部登录请求。

## 代码约定

- 复用现有同步 Playwright 与 `BasePage` 帮助方法。
- 对类职责、稳定定位器和组合登录方法添加简洁中文注释。
- 不修改现有小说站点页面对象、测试配置或默认 `BASE_URL`。
