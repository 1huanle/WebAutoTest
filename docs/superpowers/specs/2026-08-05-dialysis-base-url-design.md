# 透析管理地址配置

## 目标

将测试框架的默认基础地址从旧小说站点切换到透析管理页，同时保留页面对象使用的登录入口地址。

## 变更范围

- 将 `config/config.py` 与 `.env.example` 的默认 `BASE_URL` 更新为 `https://yunjingzhi.com/yunjingservice/user/txform.shtml`。
- 更新配置测试，使其断言默认基础地址为透析管理页。
- 删除 `reports/` 下含旧地址的历史测试报告。

## 非变更项

- `LoginPage.LOGIN_URL` 保持为登录页地址 `https://yunjingzhi.com/yunjingservice/login.jsp?origin=txjl`。
- 不修改本地 `.env`，它当前未设置 `BASE_URL`。

## 验证

运行配置测试，并搜索项目确认旧地址不再出现在源配置、示例配置、测试或报告中。
