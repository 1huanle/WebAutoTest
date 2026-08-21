# 血液透析模块 POM Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为主任角色可见的血液透析页面建立带中文注释、可逐页扩展且可测试的 Playwright POM。

**Architecture:** 新增 `pages/hemodialysis/` 包作为唯一的血液透析归属标识。`HemodialysisPage` 和 `DialysisSheetPage` 负责模块入口及患者选择，`PatientManagementPage` 负责患者上下文和菜单导航；处方、评估、临时医嘱等业务页按菜单组拆成独立 POM。

**Tech Stack:** Python 3.12、pytest、pytest-playwright 同步 API、Allure。

---

### Task 1: 建立血液透析模块入口 POM

**Files:**
- Create: `pages/hemodialysis/__init__.py`
- Create: `pages/hemodialysis/hemodialysis_page.py`
- Create: `tests/test_hemodialysis_module.py`

- [ ] **Step 1: 写入失败的模块入口测试**

```python
import pytest

from pages.hemodialysis.hemodialysis_page import HemodialysisPage


@pytest.mark.regression
def test_hemodialysis_module_is_loaded_for_director(page):
    """验证主任登录态可进入并识别血液透析模块。"""
    module_page = HemodialysisPage(page).open()

    assert module_page.module_name == "血液透析"
    assert module_page.is_loaded()
    assert "血液透析" in module_page.get_top_level_modules()
```

- [ ] **Step 2: 运行测试并确认失败原因是 POM 不存在**

Run: `./.venv/Scripts/python.exe -m pytest tests/test_hemodialysis_module.py::test_hemodialysis_module_is_loaded_for_director -v`

Expected: `ModuleNotFoundError: No module named 'pages.hemodialysis'`.

- [ ] **Step 3: 实现最小模块入口 POM，并添加中文注释**

```python
from playwright.sync_api import expect

from pages.base_page import BasePage
from pages.login_page import LoginPage


class HemodialysisPage(BasePage):
    """封装血液透析一级模块的入口、身份信息与顶级菜单读取。"""

    MODULE_NAME = "血液透析"
    PAGE_TITLE = "透析单"

    def open(self) -> "HemodialysisPage":
        """打开主任登录态默认进入的透析单页面。"""
        self.navigate(LoginPage.SUCCESS_URL)
        return self

    def is_loaded(self) -> bool:
        """确认透析单标题和血液透析一级菜单均已显示。"""
        expect(self.page.get_by_text(self.MODULE_NAME, exact=True)).to_be_visible()
        return self.get_title() == self.PAGE_TITLE

    def get_top_level_modules(self) -> list[str]:
        """返回页面顶部可见的一级业务模块名称。"""
        return self.page.get_by_role("list").first.get_by_role("listitem").all_inner_texts()
```

- [ ] **Step 4: 运行测试并确认通过**

Run: `./.venv/Scripts/python.exe -m pytest tests/test_hemodialysis_module.py::test_hemodialysis_module_is_loaded_for_director -v`

Expected: `1 passed`.

### Task 2: 封装透析单和患者入口

**Files:**
- Create: `pages/hemodialysis/dialysis_sheet_page.py`
- Modify: `pages/hemodialysis/__init__.py`
- Modify: `tests/test_hemodialysis_module.py`

- [ ] **Step 1: 写入失败的透析单读取测试**

```python
from pages.hemodialysis.dialysis_sheet_page import DialysisSheetPage


@pytest.mark.regression
def test_dialysis_sheet_exposes_schedule_and_patient_search(page):
    """验证血液透析的透析单可读取排班信息和患者检索入口。"""
    dialysis_sheet = DialysisSheetPage(page).open()

    assert dialysis_sheet.is_loaded()
    assert dialysis_sheet.get_schedule_date()
    assert dialysis_sheet.get_visible_patient_count() >= 0
    assert dialysis_sheet.patient_search_placeholder == "透析号/姓名/姓名首拼"
```

- [ ] **Step 2: 运行测试并确认失败原因是页面对象不存在**

Run: `./.venv/Scripts/python.exe -m pytest tests/test_hemodialysis_module.py::test_dialysis_sheet_exposes_schedule_and_patient_search -v`

Expected: `ModuleNotFoundError` for `dialysis_sheet_page`.

- [ ] **Step 3: 实现透析单 POM**

实现 `DialysisSheetPage(HemodialysisPage)`，并以中文注释定义以下公开接口：

```python
def get_schedule_date(self) -> str: ...
def get_visible_patient_count(self) -> int: ...
def search_patient(self, keyword: str) -> "DialysisSheetPage": ...
def open_first_visible_patient(self) -> "PatientManagementPage": ...
```

`open_first_visible_patient()` 必须使用 `page.context.expect_page()` 等待新标签页，不能依赖固定睡眠；患者搜索框使用已采集的可访问名称 `透析号/姓名/姓名首拼`。

- [ ] **Step 4: 运行透析单测试并确认通过**

Run: `./.venv/Scripts/python.exe -m pytest tests/test_hemodialysis_module.py -v`

Expected: `2 passed`.

### Task 3: 封装患者上下文与菜单清单

**Files:**
- Create: `pages/hemodialysis/patient_management_page.py`
- Create: `tests/test_patient_management_page.py`

- [ ] **Step 1: 写入失败的患者菜单测试**

```python
import pytest

from pages.hemodialysis.dialysis_sheet_page import DialysisSheetPage


@pytest.mark.regression
def test_patient_management_exposes_director_menu_groups(page):
    """验证患者管理页包含主任角色可见的血液透析业务菜单组。"""
    patient_page = DialysisSheetPage(page).open().open_first_visible_patient()

    assert patient_page.is_loaded()
    assert {"医嘱", "透析管理", "评估工具"}.issubset(patient_page.get_visible_menu_groups())
    assert {"透析方案", "透析记录", "干体重", "排班信息"}.issubset(
        patient_page.get_menu_items("透析管理")
    )
```

- [ ] **Step 2: 运行测试并确认失败原因是患者管理 POM 不存在**

Run: `./.venv/Scripts/python.exe -m pytest tests/test_patient_management_page.py::test_patient_management_exposes_director_menu_groups -v`

Expected: import error for `PatientManagementPage`.

- [ ] **Step 3: 实现患者管理 POM 和菜单导航**

实现并添加中文注释：

```python
class PatientManagementPage(BasePage):
    """封装血液透析患者详情页的患者上下文和左侧业务菜单。"""

    MODULE_NAME = "血液透析"

    def is_loaded(self) -> bool: ...
    def get_patient_summary(self) -> dict[str, str]: ...
    def get_visible_menu_groups(self) -> list[str]: ...
    def expand_menu_group(self, group_name: str) -> "PatientManagementPage": ...
    def get_menu_items(self, group_name: str) -> list[str]: ...
    def open_menu_item(self, group_name: str, item_name: str) -> None: ...
```

菜单组 `透析管理` 使用已采集的链接名；子项 `透析方案`、`透析记录`、`干体重`、`排班信息` 用精确文本定位。`open_menu_item()` 在点击前调用 `expand_menu_group()`，并等待目标页面标题或核心区域出现。

- [ ] **Step 4: 运行患者管理测试并确认通过**

Run: `./.venv/Scripts/python.exe -m pytest tests/test_patient_management_page.py -v`

Expected: `1 passed`.

### Task 4: 分批封装透析方案、评估和临时医嘱

**Files:**
- Create: `pages/hemodialysis/dialysis_plan_page.py`
- Create: `pages/hemodialysis/pre_dialysis_assessment_page.py`
- Create: `pages/hemodialysis/temporary_orders_page.py`
- Create: `tests/test_hemodialysis_business_pages.py`

- [ ] **Step 1: 逐页采集实际元素并记录稳定定位器**

在已登录的可视化会话中，依次打开 `透析管理 > 透析方案`、`评估工具 > 血液透析患者评估表` 和 `医嘱` 页面。医嘱页面使用“医嘱类型”下拉框选择“临时”，不调用新增、保存、撤销或删除。对每页执行 `snapshot` 与 `generate-locator`，仅记录页面标题、页签、搜索框、表格、表单字段和主要按钮。

- [ ] **Step 2: 为三页写入失败加载测试**

```python
import pytest

from pages.hemodialysis.dialysis_sheet_page import DialysisSheetPage


@pytest.mark.regression
@pytest.mark.parametrize(
    ("page_type", "menu_group", "menu_item"),
    [
        ("dialysis_plan", "透析管理", "透析方案"),
        ("pre_dialysis_assessment", "评估工具", "血液透析患者评估表"),
        ("temporary_orders", "医嘱", "临时医嘱"),
    ],
)
def test_hemodialysis_business_page_loads(page, page_type, menu_group, menu_item):
    """验证血液透析业务页面可由患者上下文进入。"""
    patient_page = DialysisSheetPage(page).open().open_first_visible_patient()
    business_page = patient_page.open_business_page(page_type, menu_group, menu_item)

    assert business_page.module_name == "血液透析"
    assert business_page.is_loaded()
```

- [ ] **Step 3: 逐页实现最小 POM**

每个业务页定义 `MODULE_NAME = "血液透析"`、中文类注释、`is_loaded()`、`get_visible_tabs()`、`get_visible_fields()`、`get_visible_actions()`；`TemporaryOrdersPage` 额外提供 `select_order_type(order_type: str)` 与 `get_order_type()`，定位“医嘱类型”下拉框的“长期”和“临时”选项。只有在页面元素存在且确认不写入数据时，才增加只读筛选和详情读取方法。临时医嘱的新增、保存、撤销、删除等写入行为不作为自动化默认动作，而是保留为显式方法并在测试中不调用。

- [ ] **Step 4: 执行业务页测试并确认通过**

Run: `./.venv/Scripts/python.exe -m pytest tests/test_hemodialysis_business_pages.py -v`

Expected: `3 passed`.

### Task 5: 建立“全部可见页面”清单并完成回归

**Files:**
- Create: `docs/血液透析页面清单.md`
- Modify: `pages/hemodialysis/__init__.py`
- Modify: `tests/test_hemodialysis_business_pages.py`

- [ ] **Step 1: 写入菜单清单回归测试**

```python
def test_hemodialysis_page_inventory_matches_visible_menu(page):
    """验证页面清单覆盖主任角色当前可见的血液透析菜单。"""
    patient_page = DialysisSheetPage(page).open().open_first_visible_patient()

    assert patient_page.get_visible_menu_groups()
```

- [ ] **Step 2: 运行测试并确认页面清单尚未建立**

Run: `./.venv/Scripts/python.exe -m pytest tests/test_hemodialysis_business_pages.py::test_hemodialysis_page_inventory_matches_visible_menu -v`

Expected: failure because the inventory assertion has not yet been connected to the discovered menu list.

- [ ] **Step 3: 补齐页面清单与导出项**

`docs/血液透析页面清单.md` 以“菜单组、页面名称、POM 类、已覆盖元素、只读测试状态”五列记录每个主任角色可见页面。`pages/hemodialysis/__init__.py` 只导出已经有实际定位器和通过测试的 POM；发现新菜单项时先补清单、失败测试和单独页面对象，再加入导出。

- [ ] **Step 4: 执行完整验证**

Run: `./.venv/Scripts/python.exe -m pytest -v`

Expected: 所有本地单元测试通过；若真实站点请求被网络策略阻断，输出中必须明确为网络访问错误，并将该错误与 POM 测试断言失败区分开。
