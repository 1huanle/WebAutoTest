from collections.abc import Mapping
from datetime import date as date_type
from datetime import datetime
import re
from urllib.parse import urlencode, urlsplit, urlunsplit

from config.config import Config
from playwright.sync_api import Locator, Page, expect

from ..base_page import BasePage


def _build_diagnosis_url(tx_number: str) -> str:
    """根据当前环境和调用方提供的透析号生成疾病诊断地址。"""
    if not str(tx_number).strip():
        raise ValueError("tx_number 不能为空")

    base_url = urlsplit(Config.BASE_URL)
    query = urlencode(
        {
            "sk_hzid": "",
            "tx_number": str(tx_number),
            "cfzt": "jbxx1",
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


class HzglJbzdPage(BasePage):
    """PC 端患者疾病诊断页面。"""

    PAGE_PATH = "/yunjingservice/hz/userMessage.shtml"
    DIAGNOSIS_NAV_SELECTOR = "#left_jbzd"
    MEDICAL_RECORD_MENU = "病案首页"
    MAIN_PAGE_SELECTOR = "#mainpage"
    DIAGNOSIS_TABLE_SELECTOR = "#contentTable"
    ADD_BUTTON_SELECTOR = "#addzd"
    PATIENT_NUMBER_SELECTOR = "#tx_number"

    def open(self, tx_number: str) -> "HzglJbzdPage":
        """按透析号打开疾病诊断页面，不处理登录。"""
        self.navigate(_build_diagnosis_url(tx_number))
        self._wait_for_patient_detail()
        return self

    def _wait_for_patient_detail(self) -> None:
        """等待患者详情页的初始异步内容和左侧菜单完成加载。"""
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
                if (!main) {
                    return false;
                }
                const loading = main.querySelector('.loading-img-main');
                const content = main.querySelector(
                    '#userMessageForm, #contentTable, .page_container'
                );
                return Boolean(content) && !loading;
            }""",
            timeout=Config.NAVIGATION_TIMEOUT,
        )

    def is_loaded(self) -> bool:
        """确认患者信息、疾病诊断入口和诊断列表已加载。"""
        patient_number = self.page.locator(self.PATIENT_NUMBER_SELECTOR)
        expect(patient_number).to_be_attached()
        expect(patient_number).to_have_value(re.compile(r"\S+"))
        medical_record_menu = self.page.get_by_role(
            "link", name=re.compile(rf"^{re.escape(self.MEDICAL_RECORD_MENU)}")
        ).first
        expect(medical_record_menu).to_be_visible()
        self._wait_for_diagnosis_content()
        expect(
            self.page.locator(
                f"{self.MAIN_PAGE_SELECTOR} {self.ADD_BUTTON_SELECTOR}"
            )
        ).to_be_visible()
        return True

    def _wait_for_diagnosis_content(self) -> None:
        """等待诊断内容完成异步重绘，避免操作被替换的旧 DOM 节点。"""
        main = self.page.locator(self.MAIN_PAGE_SELECTOR)
        diagnosis_title = main.locator(".yhis-list-title").filter(
            has_text="诊断列表"
        ).first
        expect(diagnosis_title).to_be_visible()
        table = main.locator(self.DIAGNOSIS_TABLE_SELECTOR)
        expect(table).to_be_visible()

        self.page.wait_for_function(
            """() => {
                const isVisible = (element) => {
                    if (!element || element.getClientRects().length === 0) {
                        return false;
                    }
                    return getComputedStyle(element).visibility !== "hidden";
                };

                const main = document.querySelector('#mainpage');
                const button = main?.querySelector("#addzd");
                const currentTable = main?.querySelector("#contentTable");
                if (!isVisible(button) || !isVisible(currentTable)) {
                    delete window.__hzglDiagnosisStable;
                    return false;
                }

                const state = window.__hzglDiagnosisStable;
                if (!state || state.button !== button || state.table !== currentTable) {
                    window.__hzglDiagnosisStable = {
                        button,
                        table: currentTable,
                        since: performance.now(),
                    };
                    return false;
                }
                return performance.now() - state.since >= 500;
            }""",
            timeout=Config.NAVIGATION_TIMEOUT,
        )

    def _diagnosis_link(self) -> Locator:
        """返回二级菜单中真正负责切换内容的“疾病诊断”链接。"""
        menu_item = self.page.locator(self.DIAGNOSIS_NAV_SELECTOR)
        nested_link = menu_item.locator("a").first
        if nested_link.count() > 0:
            return nested_link
        return menu_item

    def open_diagnosis_section(self) -> "HzglJbzdPage":
        """点击患者详情页左侧的“疾病诊断”菜单并等待内容加载。"""
        self._wait_for_patient_detail()
        diagnosis_link = self._diagnosis_link()
        medical_record_menu = self.page.get_by_role(
            "link", name=re.compile(rf"^{re.escape(self.MEDICAL_RECORD_MENU)}")
        ).first
        expect(medical_record_menu).to_be_visible()
        if not diagnosis_link.is_visible():
            medical_record_menu.click()
            expect(diagnosis_link).to_be_visible(timeout=Config.DEFAULT_TIMEOUT)
        diagnosis_link.click()
        self.is_loaded()
        return self

    @property
    def diagnosis_list(self) -> "DiagnosisListSection":
        """返回疾病诊断列表对象。"""
        return DiagnosisListSection(self.page)

    def open_add_form(self) -> "DiagnosisFormSection":
        """打开新增诊断弹层并返回表单对象。"""
        add_button = self.page.locator(
            f"{self.MAIN_PAGE_SELECTOR} {self.ADD_BUTTON_SELECTOR}:visible"
        )
        expect(add_button).to_be_visible()
        add_button.click()
        form = DiagnosisFormSection(self.page)
        form.is_open()
        return form

    def close_add_form(self) -> "HzglJbzdPage":
        """关闭新增诊断弹层，不保存诊断。"""
        DiagnosisFormSection(self.page).close()
        return self

    def back_to_patient_list(self) -> "HzglPage":
        """返回患者管理列表页。"""
        back = self.page.locator("span").filter(has_text="返回患者列表").first
        expect(back).to_be_visible()
        with self.page.expect_navigation(
            url="**/hz/searchbtn.shtml?tx_select_period=3",
            wait_until="domcontentloaded",
        ):
            back.click()

        from .hzgl_page import HzglPage

        patient_list = HzglPage(self.page)
        patient_list.is_loaded()
        return patient_list


class DiagnosisListSection:
    """封装疾病诊断列表的只读查询和日期排序。"""

    TABLE_SELECTOR = "#contentTable"
    ROW_SELECTOR = "tbody#tab tr"
    COLUMN_KEYS = (
        "index",
        "diagnosis_date",
        "category",
        "name",
        "attribute",
        "doctor",
        "recovery_date",
        "remarks",
        "sync_status",
        "actions",
    )

    def __init__(self, page: Page) -> None:
        self.page = page

    def _table(self) -> Locator:
        return self.page.locator(self.TABLE_SELECTOR)

    def _rows(self) -> Locator:
        rows = self._table().locator(self.ROW_SELECTOR)
        if rows.count() == 0:
            rows = self._table().locator("tbody tr")
        return rows

    @staticmethod
    def _clean(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()

    def _row_data(self, row: Locator) -> dict[str, str] | None:
        if row.locator(".empty-status-td").count() > 0:
            return None

        cells = [self._clean(text) for text in row.locator("td").all_inner_texts()]
        if len(cells) == len(self.COLUMN_KEYS) + 1:
            # 当前页面包含左侧拖拽手柄列，业务字段从第二个单元格开始。
            cells = cells[1:]
        elif len(cells) < len(self.COLUMN_KEYS):
            # 某些页面版本不渲染左侧拖拽手柄列，兼容少一列的表格。
            cells = [""] + cells
        cells = cells[: len(self.COLUMN_KEYS)]
        cells.extend([""] * (len(self.COLUMN_KEYS) - len(cells)))
        return dict(zip(self.COLUMN_KEYS, cells))

    def get_rows(self) -> list[dict[str, str]]:
        """读取诊断列表中的诊断日期、分类、名称及其他列。"""
        result: list[dict[str, str]] = []
        for row in self._rows().all():
            row_data = self._row_data(row)
            if row_data is not None:
                result.append(row_data)
        return result

    def get_count(self) -> int:
        """读取当前诊断数量，空列表返回 0。"""
        return len(self.get_rows())

    def has_diagnosis(self, name: str) -> bool:
        """按诊断名称判断列表中是否存在诊断。"""
        for row in self._rows().all():
            row_data = self._row_data(row)
            if row_data and row_data["name"] == str(name):
                return True
        return False

    def by_name(self, name: str) -> Locator:
        """定位指定诊断所在的表格行。"""
        for row in self._rows().all():
            row_data = self._row_data(row)
            if row_data and row_data["name"] == str(name):
                return row
        raise AssertionError(f"诊断列表中未找到诊断：{name}")

    def sort_by_date(self, direction: str) -> "DiagnosisListSection":
        """按诊断日期升序或降序排序。"""
        normalized = str(direction).lower()
        if normalized not in {"asc", "desc"}:
            raise ValueError("direction 只支持 'asc' 或 'desc'")

        icon = self.page.locator(
            f'{self.TABLE_SELECTOR} span.layui-table-sort '
            f'.yhis-sort-icon[data-sort="{normalized}"]'
        )
        expect(icon).to_be_visible()
        icon.click()
        return self


class DiagnosisFormSection:
    """封装新增疾病诊断弹层表单。"""

    FORM_SELECTOR = "#jbzdxx"
    DATE_PICKER_SELECTOR = ".layui-laydate:visible"

    def __init__(self, page: Page) -> None:
        self.page = page

    def _form(self) -> Locator:
        return self.page.locator(self.FORM_SELECTOR)

    def _visible_form(self) -> Locator:
        return self.page.locator(f"{self.FORM_SELECTOR}:visible")

    def _layer(self) -> Locator:
        return self._form().locator(
            "xpath=ancestor::div[contains(concat(' ', normalize-space(@class), ' '), ' layui-layer ')][1]"
        )

    def is_open(self) -> bool:
        """确认新增诊断弹层和“添加”标题可见。"""
        form = self._visible_form()
        expect(form).to_be_visible()
        layer = self._layer()
        expect(layer).to_be_visible()
        expect(layer.locator(".layui-layer-title")).to_have_text("添加")
        return True

    def select_doctor(self, doctor: str) -> "DiagnosisFormSection":
        """通过原生 select 选择诊断医生。"""
        doctor_select = self._visible_form().locator('select[name="sk_zd_doctor"]')
        expect(doctor_select).to_be_visible()
        doctor_select.select_option(label=str(doctor))
        return self

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
        expect(picker).to_be_visible()
        return picker

    def _set_date(self, field_name: str, value: object) -> None:
        date_text = self._date_text(value)
        field = self._visible_form().locator(f'input[name="{field_name}"]')
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

        day = picker.locator(f'td[lay-ymd="{target.year}-{target.month}-{target.day}"]')
        expect(day).to_be_visible()
        day.click()
        picker.locator(".laydate-btns-confirm").click()
        expect(field).to_have_value(date_text)

    def set_diagnosis_date(self, value: object) -> "DiagnosisFormSection":
        """通过日期选择器设置诊断日期。"""
        self._set_date("sk_zd_date", value)
        return self

    def set_recovery_date(self, value: object) -> "DiagnosisFormSection":
        """通过日期选择器设置可选康复日期。"""
        if value is None or not str(value).strip():
            return self
        self._set_date("sk_kf_date", value)
        return self

    def select_diagnosis_category(self, category: str) -> "DiagnosisFormSection":
        """按分类名称选择系统诊断或自定义诊断的分类。"""
        category_node = self._visible_form().locator(".node_name").filter(
            has_text=re.compile(rf"^\s*{re.escape(str(category))}\s*$")
        ).first
        expect(category_node).to_be_visible()
        category_node.click()
        return self

    def search_system_diagnosis(self, name: str) -> "DiagnosisFormSection":
        """搜索系统诊断项目。"""
        search = self._visible_form().locator('input[name="search_zd_name"]')
        expect(search).to_be_visible()
        search.fill(str(name))
        search.press("Enter")
        return self

    def select_system_diagnosis(self, name: str) -> "DiagnosisFormSection":
        """从系统诊断搜索结果中选择指定项目。"""
        results = self._visible_form().locator("#zdnamelist:visible [data-name]").filter(
            has_text=re.compile(rf"^\s*{re.escape(str(name))}\s*$")
        ).first
        if results.count() == 0:
            results = self._visible_form().locator("#zdnamelist:visible").get_by_text(
                str(name), exact=True
            ).first
        expect(results).to_be_visible()
        before = self._visible_form().locator("#prezdlist .prezdxx").count()
        results.click()
        expect(self._visible_form().locator("#prezdlist .prezdxx")).to_have_count(
            before + 1
        )
        return self

    def fill_custom_diagnosis(self, name: str) -> "DiagnosisFormSection":
        """填写并添加自定义诊断项目。"""
        if not str(name).strip():
            raise ValueError("自定义诊断项目名称不能为空")

        category_id = self._visible_form().locator("#zdtype_id")
        if category_id.input_value().strip() == "":
            raise ValueError("添加自定义诊断前必须先选择诊断分类")

        custom = self._visible_form().locator('input[name="zdy_zd_name"]')
        expect(custom).to_be_visible()
        custom.fill(str(name))
        before = self._visible_form().locator("#prezdlist .prezdxx").count()
        self._visible_form().locator("#addzdyzd").click()
        expect(self._visible_form().locator("#prezdlist .prezdxx")).to_have_count(
            before + 1
        )
        return self

    def fill_remarks(self, text: str) -> "DiagnosisFormSection":
        """填写诊断备注。"""
        remarks = self._visible_form().locator('input[name="sk_remarks"]')
        expect(remarks).to_be_visible()
        remarks.fill(str(text))
        return self

    def fill_form(self, data: Mapping[str, object]) -> "DiagnosisFormSection":
        """按逻辑字段批量填写新增诊断表单。"""
        supported = {
            "doctor",
            "diagnosis_date",
            "recovery_date",
            "diagnosis_category",
            "system_diagnosis",
            "custom_diagnosis",
            "remarks",
        }
        unknown = set(data) - supported
        if unknown:
            raise KeyError(f"新增诊断包含未定义字段：{', '.join(sorted(unknown))}")

        system_name = data.get("system_diagnosis")
        custom_name = data.get("custom_diagnosis")
        if system_name and custom_name:
            raise ValueError("系统诊断和自定义诊断只能选择一种")

        if "doctor" in data:
            self.select_doctor(str(data["doctor"]))
        if "diagnosis_date" in data:
            self.set_diagnosis_date(data["diagnosis_date"])
        if "recovery_date" in data:
            self.set_recovery_date(data["recovery_date"])
        if "diagnosis_category" in data:
            self.select_diagnosis_category(str(data["diagnosis_category"]))
        if system_name:
            self.search_system_diagnosis(str(system_name))
            self.select_system_diagnosis(str(system_name))
        if custom_name:
            self.fill_custom_diagnosis(str(custom_name))
        if "remarks" in data:
            self.fill_remarks(str(data["remarks"]))
        return self

    def save(self) -> HzglJbzdPage:
        """保存诊断，等待弹层关闭和诊断列表重新可见。"""
        save_button = self._visible_form().locator("#save")
        expect(save_button).to_be_visible()
        expect(save_button).to_be_enabled()
        save_button.click()
        expect(self._form()).to_be_hidden(timeout=Config.NAVIGATION_TIMEOUT)
        diagnosis_page = HzglJbzdPage(self.page)
        expect(self.page.locator(HzglJbzdPage.DIAGNOSIS_TABLE_SELECTOR)).to_be_visible()
        return diagnosis_page

    def close(self) -> "DiagnosisFormSection":
        """关闭新增诊断弹层，不保存诊断。"""
        close_button = self._layer().locator(".layui-layer-close")
        expect(close_button).to_be_visible()
        close_button.click()
        expect(self._form()).to_be_hidden()
        return self
