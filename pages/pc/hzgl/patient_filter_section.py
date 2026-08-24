from collections.abc import Mapping, Sequence

from playwright.sync_api import Locator, Page, expect


class PatientFilterSection:
    """封装患者管理页面的筛选表单。"""

    FORM_SELECTOR = "form.hz_form:visible"
    NAME_SEARCH_PLACEHOLDER = "请输入患者姓名"

    FIELD_LABELS = {
        "schedule": "排班",
        "schedule_date": "排班日期",
        "shift": "班次",
        "today_dialysis_status": "今日透析状态",
        "today_dialysis_mode": "今日透析模式",
        "patient_source": "患者来源",
        "dialysis_plan": "透析方案",
        "payment_method": "付费方式",
        "real_name_verified": "实名认证",
        "binding_status": "绑定状态",
        "infectious_disease": "传染病",
        "attending_doctor": "主治医生",
        "primary_nurse": "主管护士",
        "ward": "病区",
        "access_type": "通路类型",
        "tag": "标签",
    }

    def __init__(self, page: Page) -> None:
        self.page = page

    def _form(self) -> Locator:
        return self.page.locator(self.FORM_SELECTOR)

    def _label_for(self, field: str) -> str:
        return self.FIELD_LABELS.get(field, field)

    def _form_item(self, field: str) -> Locator:
        label = self._label_for(field)
        item = self._form().locator(".el-form-item").filter(has_text=label).first
        expect(item).to_be_visible()
        return item

    def _select_value(self, field: str, value: str) -> None:
        item = self._form_item(field)
        control = item.locator("input.el-input__inner").first
        expect(control).to_be_visible()
        control.click()

        dropdown = self.page.locator(".el-select-dropdown:visible").last
        option = dropdown.locator("li.el-select-dropdown__item").filter(
            has_text=str(value)
        ).first
        if option.count() == 0:
            option = dropdown.get_by_text(str(value), exact=True).last
        expect(option).to_be_visible()
        option.click()

    def _fill_date_range(self, value: object) -> None:
        if isinstance(value, Mapping):
            start = value.get("start")
            end = value.get("end")
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            if len(value) != 2:
                raise ValueError("排班日期需要包含开始日期和结束日期")
            start, end = value
        else:
            raise TypeError("排班日期必须是 {'start': ..., 'end': ...} 或二元序列")

        if start is None or end is None:
            raise ValueError("排班日期的开始日期和结束日期不能为空")

        item = self._form_item("schedule_date")
        date_inputs = item.locator("input.el-range-input")
        if date_inputs.count() != 2:
            raise AssertionError("未找到完整的排班日期范围控件")
        if not date_inputs.nth(0).is_enabled() or not date_inputs.nth(1).is_enabled():
            raise AssertionError("排班日期控件当前不可编辑")
        date_inputs.nth(0).fill(str(start))
        date_inputs.nth(1).fill(str(end))

    def apply_filters(self, filters: Mapping[str, object]) -> "PatientFilterSection":
        """按字段名批量填写筛选条件，不自动提交查询。"""
        for field, value in filters.items():
            if field == "schedule_date" or field == "排班日期":
                self._fill_date_range(value)
                continue

            values = value if isinstance(value, (list, tuple, set)) else [value]
            for option in values:
                self._select_value(field, str(option))
        return self

    def search_by_name(self, name: str) -> "PatientFilterSection":
        """填写患者姓名查询条件。"""
        search_input = self.page.get_by_placeholder(self.NAME_SEARCH_PLACEHOLDER)
        expect(search_input).to_be_visible()
        search_input.fill(name)
        return self

    def submit(self) -> "PatientFilterSection":
        """提交当前筛选条件。"""
        self._form().locator("button").filter(has_text="查询").first.click()
        return self

    def collapse(self) -> "PatientFilterSection":
        """收起筛选区域。"""
        self._form().locator("button").filter(has_text="收起筛选").first.click()
        return self
