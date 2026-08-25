from collections.abc import Mapping
from datetime import date as date_type
from datetime import datetime
import re
from urllib.parse import urlencode, urlsplit, urlunsplit

from config.config import Config
from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError, expect

from ..base_page import BasePage
from ..hemodialysis.dialogs.layui_iframe_dialog import LayuiIframeDialog


def _build_yz_url(tx_number: str) -> str:
    """根据当前环境和调用方提供的透析号生成患者详情地址。"""
    if not str(tx_number).strip():
        raise ValueError("tx_number 不能为空")

    base_url = urlsplit(Config.BASE_URL)
    query = urlencode(
        {
            "sk_hzid": "",
            "tx_number": str(tx_number),
            "cfzt": "jbxx2",
        }
    )
    return urlunsplit(
        (
            base_url.scheme,
            base_url.netloc,
            "/yunjingservice/hz/userMessage.shtml",
            query,
            "",
        )
    )


class HzglYzPage(BasePage):
    """PC 端患者详情页中的长期医嘱模块。"""

    PAGE_PATH = "/yunjingservice/hz/userMessage.shtml"
    MEDICAL_RECORD_MENU = "病案首页"
    MAIN_PAGE_SELECTOR = "#mainpage"
    YZ_NAV_SELECTOR = "#left_yz"
    YZ_FORM_SELECTOR = "#yzForm"
    YZ_TABLE_SELECTOR = "#contentTable.yz-tb"
    ADD_BUTTON_SELECTOR = "#addyz"
    PATIENT_NUMBER_SELECTOR = "#tx_number"

    def open(self, tx_number: str) -> "HzglYzPage":
        """按透析号打开患者详情页，不处理登录或医嘱菜单。"""
        self.navigate(_build_yz_url(tx_number))
        self._wait_for_patient_detail()
        return self

    def _wait_for_patient_detail(self) -> None:
        """等待患者详情页初始异步内容和病案首页菜单加载完成。"""
        patient_header = self.page.locator(".nav-hzinfo-0216").filter(
            has_text="透析号："
        ).first
        expect(patient_header).to_be_visible()
        medical_record_menu = self.page.get_by_role(
            "link", name=re.compile(rf"^{re.escape(self.MEDICAL_RECORD_MENU)}")
        ).first
        expect(medical_record_menu).to_be_visible()
        self.page.wait_for_function(
            """() => {
                const main = document.querySelector('#mainpage');
                if (!main) return false;
                const loading = main.querySelector('.loading-img-main');
                const content = main.querySelector(
                    '#userMessageForm, #contentTable, .page_container'
                );
                return Boolean(content) && !loading;
            }""",
            timeout=Config.NAVIGATION_TIMEOUT,
        )

    def _wait_for_yz_content(self) -> None:
        """等待医嘱区域完成异步重绘，避免操作旧 DOM 节点。"""
        main = self.page.locator(self.MAIN_PAGE_SELECTOR)
        expect(main.locator(self.YZ_FORM_SELECTOR)).to_be_visible()
        expect(main.locator(self.YZ_TABLE_SELECTOR)).to_be_visible()
        expect(main.locator(self.ADD_BUTTON_SELECTOR)).to_be_visible()
        self.page.wait_for_function(
            """() => {
                const visible = (element) => {
                    if (!element || element.getClientRects().length === 0) return false;
                    return getComputedStyle(element).visibility !== 'hidden';
                };
                const main = document.querySelector('#mainpage');
                const form = main?.querySelector('#yzForm');
                const table = main?.querySelector('#contentTable.yz-tb');
                const button = main?.querySelector('#addyz');
                if (!visible(form) || !visible(table) || !visible(button)) {
                    delete window.__hzglYzStable;
                    return false;
                }
                const state = window.__hzglYzStable;
                if (!state || state.form !== form || state.table !== table || state.button !== button) {
                    window.__hzglYzStable = {
                        form,
                        table,
                        button,
                        since: performance.now(),
                    };
                    return false;
                }
                return performance.now() - state.since >= 300;
            }""",
            timeout=Config.NAVIGATION_TIMEOUT,
        )

    def is_loaded(self) -> bool:
        """校验医嘱筛选区、列表和新增按钮已经显示。"""
        patient_number = self.page.locator(self.PATIENT_NUMBER_SELECTOR)
        expect(patient_number).to_be_attached()
        expect(patient_number).to_have_value(re.compile(r"\S+"))
        self._wait_for_yz_content()
        expect(self.page.get_by_text("医嘱列表", exact=True)).to_be_visible()
        return True

    def _yz_link(self) -> Locator:
        """返回病案首页二级菜单中真正负责切换医嘱内容的链接。"""
        menu_item = self.page.locator(self.YZ_NAV_SELECTOR)
        nested_link = menu_item.locator("a").first
        return nested_link if nested_link.count() > 0 else menu_item

    def open_yz_section(self) -> "HzglYzPage":
        """先展开病案首页，再点击医嘱并等待医嘱区域加载。"""
        self._wait_for_patient_detail()
        medical_record_menu = self.page.get_by_role(
            "link", name=re.compile(rf"^{re.escape(self.MEDICAL_RECORD_MENU)}")
        ).first
        yz_link = self._yz_link()
        expect(medical_record_menu).to_be_visible()
        if not yz_link.is_visible():
            medical_record_menu.click()
            expect(yz_link).to_be_visible(timeout=Config.DEFAULT_TIMEOUT)
        yz_link.click()
        self.is_loaded()
        return self

    @property
    def order_list(self) -> "YzListSection":
        """返回当前患者的医嘱列表对象。"""
        return YzListSection(self.page)

    def open_add_order(self) -> "YzFormSection":
        """打开添加医嘱弹窗并返回表单对象。"""
        add_button = self.page.locator(
            f"{self.MAIN_PAGE_SELECTOR} {self.ADD_BUTTON_SELECTOR}:visible"
        )
        expect(add_button).to_be_visible()
        add_button.click()
        form = YzFormSection(self.page)
        form.is_open()
        return form


class YzListSection:
    """封装患者详情页医嘱列表的只读查询。"""

    TABLE_SELECTOR = "#contentTable.yz-tb"
    COLUMN_KEYS = (
        "index",
        "start_time",
        "order_name",
        "specification",
        "medication_push",
        "single_dose",
        "administration_route",
        "frequency",
        "ordering_doctor",
        "remarks",
        "stop_time",
        "stop_reason",
        "stop_doctor",
        "actions",
    )

    def __init__(self, page: Page) -> None:
        self.page = page

    def _table(self) -> Locator:
        return self.page.locator(self.TABLE_SELECTOR)

    def _rows(self) -> Locator:
        return self._table().locator("tbody tr")

    @staticmethod
    def _clean(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()

    def _row_data(self, row: Locator) -> dict[str, str] | None:
        if row.locator(".empty-status-td").count() > 0:
            return None
        cells = [self._clean(text) for text in row.locator("td").all_inner_texts()]
        if len(cells) == len(self.COLUMN_KEYS) + 1:
            cells = cells[1:]
        if len(cells) < len(self.COLUMN_KEYS):
            return None
        return dict(zip(self.COLUMN_KEYS, cells[: len(self.COLUMN_KEYS)]))

    def get_rows(self) -> list[dict[str, str]]:
        """读取医嘱列表业务行。"""
        rows: list[dict[str, str]] = []
        for row in self._rows().all():
            row_data = self._row_data(row)
            if row_data is not None:
                rows.append(row_data)
        return rows

    def get_count(self) -> int:
        """读取当前医嘱数量，空列表返回 0。"""
        return len(self.get_rows())

    def by_name(self, name: str) -> Locator:
        """按医嘱名称定位列表行。"""
        target = str(name)
        for row in self._rows().all():
            row_data = self._row_data(row)
            if row_data and row_data["order_name"] == target:
                return row
        raise AssertionError(f"医嘱列表中未找到医嘱：{name}")

    def has_order(self, name: str) -> bool:
        """判断医嘱列表中是否存在指定名称。"""
        try:
            self.by_name(name)
        except AssertionError:
            return False
        return True


class YzFormSection(LayuiIframeDialog):
    """封装患者详情页“添加医嘱”Layui iframe 表单。"""

    TITLE = "添加医嘱"
    DATE_PICKER_SELECTOR = ".layui-laydate:visible"
    AUTOCOMPLETE_TIMEOUT = 15_000

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def is_open(self) -> bool:
        """确认添加医嘱弹窗、iframe 和确定按钮可见。"""
        self.wait_for_open()
        expect(self._frame().locator("#subbmit_btn_addYz")).to_be_visible()
        return True

    def _field(self, selector: str) -> Locator:
        return self._frame().locator(selector).first

    def _named_field(self, name: str) -> Locator:
        return self._field(f'[name="{name}"]')

    @staticmethod
    def _date_text(value: object) -> str:
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")
        if isinstance(value, date_type):
            return value.isoformat()
        try:
            return datetime.strptime(str(value), "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError as exc:
            raise ValueError(f"日期必须使用 YYYY-MM-DD 格式：{value}") from exc

    def _date_picker(self) -> Locator:
        picker = self.page.locator(self.DATE_PICKER_SELECTOR).last
        try:
            expect(picker).to_be_visible(timeout=2_000)
        except PlaywrightTimeoutError:
            picker = self._frame().locator(self.DATE_PICKER_SELECTOR).last
            expect(picker).to_be_visible()
        return picker

    def _set_date(self, field_name: str, value: object) -> None:
        date_text = self._date_text(value)
        field = self._named_field(field_name)
        expect(field).to_be_visible()
        field.click()
        picker = self._date_picker()
        target = datetime.strptime(date_text, "%Y-%m-%d").date()
        target_month = (target.year, target.month)

        for _ in range(240):
            month_header = picker.locator('span[lay-type="month"]').first
            month_key = month_header.get_attribute("lay-ym")
            if not month_key:
                raise AssertionError("日期选择器缺少当前年月标识")
            current_year, current_month = (
                int(part) for part in month_key.split("-", maxsplit=1)
            )
            current_month_key = (current_year, current_month)
            if current_month_key == target_month:
                break
            if current_month_key > target_month:
                picker.locator(".laydate-prev-m").click()
            else:
                picker.locator(".laydate-next-m").click()
        else:
            raise AssertionError(f"日期选择器无法切换到目标月份：{date_text}")

        day = picker.locator(
            f'td[lay-ymd="{target.year}-{target.month}-{target.day}"]'
        )
        expect(day).to_be_visible()
        day.click()
        confirm = picker.locator(".laydate-btns-confirm")
        if confirm.count() > 0 and confirm.is_visible():
            confirm.click()
        expect(field).to_have_value(date_text)

    def _select_autocomplete(
        self, field_name: str, query: str, option: str | None = None
    ) -> None:
        """填写自动补全字段并点击对应的可见候选项。"""
        field = self._named_field(field_name)
        expect(field).to_be_visible()
        field.click()
        field.press("Control+A")
        field.fill("")
        field.type(str(query))
        expected = str(option or query)
        local_candidates = field.locator(
            "xpath=ancestor::td[1]"
        ).locator(".select_div:visible li")
        candidate = local_candidates.filter(has_text=expected).last
        if candidate.count() == 0:
            candidate = self._frame().locator(
                ".select_div:visible li, .layui-anim:visible li"
            ).filter(has_text=expected).last
        expect(candidate).to_be_visible(timeout=self.AUTOCOMPLETE_TIMEOUT)
        candidate.click()
        expect(field).not_to_have_value("")

    def select_order_type(self, order_type: str) -> "YzFormSection":
        """选择医嘱类型。"""
        field = self._named_field("sk_yz_type")
        expect(field).to_be_visible()
        field.select_option(label=str(order_type))
        return self

    def set_order_time(self, value: object) -> "YzFormSection":
        """通过日期控件设置医嘱时间。"""
        self._set_date("sk_yz_time", value)
        return self

    def select_order_name(
        self, name: str, option: str | None = None
    ) -> "YzFormSection":
        """搜索并选择医嘱名称候选项。"""
        self._select_autocomplete("sk_yz_name", name, option)
        return self

    def set_start_time(self, value: object) -> "YzFormSection":
        """通过日期控件设置医嘱开始时间。"""
        self._set_date("sk_start_time", value)
        return self

    def fill_single_dose(self, value: object) -> "YzFormSection":
        """填写单次用量。"""
        field = self._named_field("sk_yz_dcl")
        expect(field).to_be_visible()
        field.fill(str(value))
        return self

    def fill_quantity(self, value: object) -> "YzFormSection":
        """填写开药数量。"""
        field = self._named_field("sk_yz_kyl")
        expect(field).to_be_visible()
        field.fill(str(value))
        return self

    def select_administration_route(
        self, route: str, option: str | None = None
    ) -> "YzFormSection":
        """搜索并选择给药途径候选项。"""
        self._select_autocomplete("sk_yz_tj", route, option)
        return self

    def select_frequency(
        self, frequency: str, option: str | None = None
    ) -> "YzFormSection":
        """搜索并选择执行频率候选项。"""
        self._select_autocomplete("sk_yz_pl", frequency, option)
        return self

    def select_doctor(self, doctor: str) -> "YzFormSection":
        """选择开嘱医生。"""
        field = self._named_field("sk_yz_doctor")
        expect(field).to_be_visible()
        field.select_option(label=str(doctor))
        return self

    def select_execution_department(self, department: str) -> "YzFormSection":
        """选择执行科室。"""
        field = self._named_field("execution_department")
        expect(field).to_be_visible()
        field.select_option(label=str(department))
        return self

    def select_diagnosis(self, diagnosis: str) -> "YzFormSection":
        """选择诊断，兼容原生 select 和页面自定义下拉控件。"""
        native = self._frame().locator('select[name="tx_diagnose_select"]')
        if native.count() > 0:
            expect(native).to_be_visible()
            native.select_option(label=str(diagnosis))
            return self

        field = self._named_field("tx_diagnose_select")
        expect(field).to_be_visible()
        field.click()
        option = self._frame().locator(
            ".layui-anim:visible dd, .layui-anim:visible li, "
            ".select_div:visible li"
        ).filter(has_text=str(diagnosis)).last
        expect(option).to_be_visible()
        option.click()
        return self

    def fill_note(self, note: object) -> "YzFormSection":
        """填写医嘱备注。"""
        field = self._named_field("tx_yznote")
        expect(field).to_be_visible()
        field.fill(str(note))
        return self

    def expect_order_description(self, value: str) -> "YzFormSection":
        """校验页面根据医嘱名称自动生成的只读描述。"""
        field = self._named_field("sk_yz_dec")
        expect(field).to_have_value(str(value))
        return self

    def fill_form(self, data: Mapping[str, object]) -> "YzFormSection":
        """按逻辑字段批量填写新增医嘱表单。"""
        supported = {
            "order_type",
            "order_time",
            "order_name",
            "order_name_option",
            "start_time",
            "single_dose",
            "quantity",
            "administration_route",
            "administration_route_option",
            "frequency",
            "frequency_option",
            "doctor",
            "execution_department",
            "diagnosis",
            "note",
        }
        unknown = set(data) - supported
        if unknown:
            raise KeyError(f"新增医嘱包含未定义字段：{', '.join(sorted(unknown))}")

        if "order_type" in data:
            self.select_order_type(str(data["order_type"]))
        if "order_time" in data:
            self.set_order_time(data["order_time"])
        if "order_name" in data:
            self.select_order_name(
                str(data["order_name"]),
                str(data["order_name_option"])
                if data.get("order_name_option") is not None
                else None,
            )
        if "start_time" in data:
            self.set_start_time(data["start_time"])
        if "single_dose" in data:
            self.fill_single_dose(data["single_dose"])
        if "quantity" in data:
            self.fill_quantity(data["quantity"])
        if "administration_route" in data:
            self.select_administration_route(
                str(data["administration_route"]),
                str(data["administration_route_option"])
                if data.get("administration_route_option") is not None
                else None,
            )
        if "frequency" in data:
            self.select_frequency(
                str(data["frequency"]),
                str(data["frequency_option"])
                if data.get("frequency_option") is not None
                else None,
            )
        if "doctor" in data:
            self.select_doctor(str(data["doctor"]))
        if "execution_department" in data:
            self.select_execution_department(str(data["execution_department"]))
        if "diagnosis" in data:
            self.select_diagnosis(str(data["diagnosis"]))
        if "note" in data:
            self.fill_note(data["note"])
        return self

    def save(self) -> HzglYzPage:
        """点击确定保存医嘱，等待弹窗关闭和医嘱列表重新显示。"""
        save_button = self._frame().locator("#subbmit_btn_addYz")
        expect(save_button).to_be_visible()
        expect(save_button).to_be_enabled()
        save_button.click()
        self._wait_for_closed()
        page = HzglYzPage(self.page)
        expect(self.page.locator(HzglYzPage.YZ_TABLE_SELECTOR)).to_be_visible(
            timeout=Config.NAVIGATION_TIMEOUT
        )
        return page

    def close(self) -> "YzFormSection":
        """关闭新增医嘱弹窗，不保存。"""
        close_button = self._frame().locator("#close_btn_addYz")
        expect(close_button).to_be_visible()
        close_button.click()
        self._wait_for_closed()
        return self
