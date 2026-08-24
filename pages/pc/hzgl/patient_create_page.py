from collections.abc import Mapping
from urllib.parse import urlsplit, urlunsplit

from config.config import Config
from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError, expect

from ..base_page import BasePage


def _build_create_patient_url() -> str:
    """根据当前环境的域名生成新增患者页面地址。"""
    base_url = urlsplit(Config.BASE_URL)
    return urlunsplit(
        (
            base_url.scheme,
            base_url.netloc,
            "/yunjingservice/manage/useraddyj.shtml",
            "",
            "",
        )
    )


class PatientCreatePage(BasePage):
    """PC 端新增患者页面的完整表单对象。"""

    CREATE_PATIENT_URL = _build_create_patient_url()
    PAGE_TITLE = "患者管理"

    TEXT_FIELDS = {
        "name": "hzda_tx_name",
        "pinyin_code": "hzda_tx_szm_code",
        "alias": "hzda_tx_bieming",
        "dialysis_number": "hzda_tx_number",
        "id_number": "hzda_tx_zjno",
        "age": "hzda_tx_age",
        "medical_record_number": "hzda_id",
        "bed_number": "hzda_tx_bed_number",
        "ancestral_home": "hzda_tx_ancestral_home",
        "insurance_location": "hzda_tx_insurance_location",
        "medical_insurance_number": "hzda_tx_ybno",
        "height_cm": "hzda_tx_height",
        "initial_weight_kg": "tx_bgWeight",
        "smoking": "tx_isSmorking",
        "vision_impairment": "tx_viewIm",
        "drinking": "tx_isDrinking",
        "religious_belief": "tx_faith",
        "rfid": "tx_rfid",
        "erythropoietin_dose": "week_chs",
        "dialysis_frequency": "tx_frequency",
        "postal_code": "tx_postal_code",
        "personal_phone": "hzda_tx_phone",
        "family_name": "hzda_tx_js_name",
        "family_phone": "hzda_tx_phone_2",
        "home_address": "hzda_tx_add",
        "email": "tx_email",
        "work_unit": "hzda_tx_gzdw",
        "dialysis_age": "hzda_txtime",
        "initial_dialysis_count": "hzda_tx_yiTouXiCiShu",
        "total_dialysis_count": "hzda_tx_zlcs",
    }

    SELECT_FIELDS = {
        "patient_type": "hzda_hzlx",
        "sex": "hzda_tx_sex",
        "id_type": "hzda_tx_zjlx",
        "patient_source": "hzda_source",
        "ward": "hzda_tx_bing_qu",
        "marital_status": "hzda_tx_hyzk",
        "reimbursement_method": "hzda_tx_bxfs",
        "blood_type": "hzda_tx_xue_xing",
        "rh": "hzda_tx_xue_xing_rh",
        "education_level": "hzda_tx_wen_hua_cheng_du",
        "occupation": "hzda_tx_zhi_ye",
        "nationality": "tx_nationality",
        "infection": "tx_crb",
        "attending_doctor": "hzda_tx_treatDOC",
        "treatment_nurse": "tx_treatNurse",
        "first_dialysis_reason": "first_txtd",
        "first_access_side": "first_xgtl_bw_name",
        "first_access_type": "first_xgtl_name",
    }

    DATE_FIELDS = {
        "birth_date": "hzda_tx_BirthDay",
        "medical_insurance_expiry_date": "hzda_tx_ybdqdate",
        "medical_insurance_renewal_date": "hzda_tx_ybdqtxdate",
        "received_date": "hzda_tx_patient_enter_date",
        "first_dialysis_date": "hzda_tx_first_date",
        "induction_end_date": "tx_ydq_date",
    }

    TEXTAREA_FIELDS = {
        "diagnosis": "hzda_tx_zhen_duan",
        "note": "tx_comment",
        "allergy_history": "tx_gms",
        "tumor_history": "tx_zls",
    }

    AUTOCOMPLETE_FIELDS = {
        "family_relation": "hzda_tx_js_gx",
    }

    BASIC_FIELDS = {
        "patient_type",
        "name",
        "pinyin_code",
        "alias",
        "dialysis_number",
        "sex",
        "id_type",
        "id_number",
        "birth_date",
        "age",
        "patient_source",
        "medical_record_number",
        "ward",
        "bed_number",
        "marital_status",
        "ancestral_home",
        "insurance_location",
        "reimbursement_method",
        "medical_insurance_number",
        "medical_insurance_expiry_date",
        "medical_insurance_renewal_date",
        "height_cm",
        "initial_weight_kg",
        "blood_type",
        "rh",
        "education_level",
        "occupation",
        "smoking",
        "vision_impairment",
        "drinking",
        "religious_belief",
        "nationality",
        "rfid",
        "erythropoietin_dose",
        "dialysis_frequency",
        "postal_code",
    }

    CONTACT_FIELDS = {
        "personal_phone",
        "family_name",
        "family_relation",
        "family_phone",
        "home_address",
        "email",
        "work_unit",
    }

    TREATMENT_FIELDS = {
        "received_date",
        "first_dialysis_date",
        "dialysis_age",
        "induction_end_date",
        "initial_dialysis_count",
        "total_dialysis_count",
        "infection",
        "attending_doctor",
        "treatment_nurse",
        "first_dialysis_reason",
        "first_access_side",
        "first_access_type",
    }

    NOTE_FIELDS = set(TEXTAREA_FIELDS)
    # These values are calculated or managed by the page.  They are only
    # fillable when the page exposes an editable control (for example, birth
    # date becomes editable for non-mainland ID types).
    READ_ONLY_FIELDS = {
        "birth_date",
        "age",
        "dialysis_age",
        "total_dialysis_count",
        "diagnosis",
    }

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def open(self) -> "PatientCreatePage":
        """直接打开新增患者页面。"""
        self.navigate(self.CREATE_PATIENT_URL)
        return self

    def wait_for_open(self) -> "PatientCreatePage":
        """等待新增患者表单加载完成。"""
        self.is_loaded()
        return self

    def is_loaded(self) -> bool:
        """确认新增患者页面的关键控件可见或已挂载。"""
        self.page.locator('select[name="hzda_hzlx"]').wait_for(state="attached")
        self.page.locator('input[name="hzda_tx_name"]').wait_for(state="visible")
        self.page.locator('select[name="hzda_tx_zjlx"]').wait_for(state="attached")
        self.page.locator('button[name="save"]').wait_for(state="visible")
        self.page.locator('button[name="exit"]').wait_for(state="visible")
        return True

    def _field_locator(self, field: str) -> Locator:
        if field in self.TEXT_FIELDS:
            name = self.TEXT_FIELDS[field]
            return self.page.locator(f'input[name="{name}"]')
        if field in self.AUTOCOMPLETE_FIELDS:
            name = self.AUTOCOMPLETE_FIELDS[field]
            return self.page.locator(f'input[name="{name}"]')
        if field in self.SELECT_FIELDS:
            name = self.SELECT_FIELDS[field]
            return self.page.locator(f'select[name="{name}"]')
        if field in self.DATE_FIELDS:
            name = self.DATE_FIELDS[field]
            return self.page.locator(f'input[name="{name}"]')
        if field in self.TEXTAREA_FIELDS:
            name = self.TEXTAREA_FIELDS[field]
            return self.page.locator(f'textarea[name="{name}"]')
        raise KeyError(f"未定义的新增患者字段：{field}")

    def _fill_autocomplete(self, field: str, value: object) -> None:
        locator = self._field_locator(field)
        expect(locator).to_be_visible()
        # 页面在输入框聚焦时会先按空值打开候选项；逐字键入才能触发其过滤逻辑。
        locator.fill("")
        locator.press_sequentially(str(value))
        suggestions = self.page.locator(
            "ul.ui-autocomplete:visible li, .ui-autocomplete:visible li"
        ).filter(has_text=str(value)).first
        try:
            suggestions.wait_for(state="visible", timeout=5000)
        except PlaywrightTimeoutError:
            raise AssertionError(
                f"字段 {field} 未出现匹配的自动补全候选项：{value}"
            ) from None
        suggestions.click()

    def _fill_field(self, field: str, value: object) -> None:
        if field in self.AUTOCOMPLETE_FIELDS:
            self._fill_autocomplete(field, value)
            return

        locator = self._field_locator(field)
        expect(locator).to_be_attached()
        if not locator.is_enabled() or locator.get_attribute("readonly") is not None:
            if field in self.READ_ONLY_FIELDS and not str(value).strip():
                return
            raise ValueError(f"字段 {field} 当前由页面自动计算或不可编辑")
        if field in self.SELECT_FIELDS:
            locator.select_option(label=str(value))
        else:
            locator.fill(str(value))

    def _fill_fields(self, fields: Mapping[str, object]) -> "PatientCreatePage":
        for field, value in fields.items():
            self._fill_field(field, value)
        return self

    def fill_basic_info(self, data: Mapping[str, object]) -> "PatientCreatePage":
        """填写患者基础资料。"""
        self._ensure_fields(data, self.BASIC_FIELDS, "基础资料")
        return self._fill_fields(data)

    def fill_contact_info(self, data: Mapping[str, object]) -> "PatientCreatePage":
        """填写患者联系方式。"""
        self._ensure_fields(data, self.CONTACT_FIELDS, "联系方式")
        return self._fill_fields(data)

    def fill_treatment_info(self, data: Mapping[str, object]) -> "PatientCreatePage":
        """填写患者治疗信息。"""
        self._ensure_fields(data, self.TREATMENT_FIELDS, "治疗信息")
        return self._fill_fields(data)

    def fill_notes(self, data: Mapping[str, object]) -> "PatientCreatePage":
        """填写诊断、备注、过敏史和肿瘤史。"""
        self._ensure_fields(data, self.NOTE_FIELDS, "文本信息")
        return self._fill_fields(data)

    def fill_form(self, data: Mapping[str, object]) -> "PatientCreatePage":
        """按分组或逻辑字段名填写完整患者档案表单。"""
        sections = {
            "basic": self.fill_basic_info,
            "basic_info": self.fill_basic_info,
            "contact": self.fill_contact_info,
            "contact_info": self.fill_contact_info,
            "treatment": self.fill_treatment_info,
            "treatment_info": self.fill_treatment_info,
            "notes": self.fill_notes,
        }
        for key, value in data.items():
            if key in sections:
                if not isinstance(value, Mapping):
                    raise TypeError(f"表单分组 {key} 必须是字段字典")
                sections[key](value)
            else:
                self._fill_field(key, value)
        return self

    def _ensure_fields(
        self, fields: Mapping[str, object], allowed: set[str], section: str
    ) -> None:
        unknown = set(fields) - allowed
        if unknown:
            names = ", ".join(sorted(unknown))
            raise KeyError(f"{section}包含未定义字段：{names}")

    def generate_dialysis_number(self) -> "PatientCreatePage":
        """点击“自动生成”生成透析号。"""
        number = self.page.locator('input[name="hzda_tx_number"]')
        with self.page.expect_response(
            "**/gexsystxnumber.shtml", timeout=Config.NAVIGATION_TIMEOUT
        ):
            self.page.locator("#getcalctx_number").click()
        expect(number).not_to_have_value("", timeout=Config.NAVIGATION_TIMEOUT)
        return self

    def click_his_import(self) -> "PatientCreatePage":
        """点击“HIS导入”入口。"""
        self.page.locator('button[name="hishz"]').click()
        return self

    def save(self) -> "PatientCreatePage":
        """提交患者档案，并确认后端保存成功后跳转到详情页。"""
        save_button = self.page.locator('button[name="save"]:visible')
        expect(save_button).to_be_visible()
        expect(save_button).to_be_enabled()

        try:
            with self.page.expect_navigation(
                url="**/manage/hz/userMessage.shtml?tx_number=*",
                wait_until="domcontentloaded",
                timeout=Config.NAVIGATION_TIMEOUT,
            ):
                save_button.click()
        except PlaywrightTimeoutError:
            messages = self.page.locator(
                ".layui-layer-dialog:visible, .layui-layer-msg:visible, "
                ".layui-layer-content:visible"
            ).all_text_contents()
            detail = "；".join(message.strip() for message in messages if message.strip())
            suffix = f" 页面提示：{detail}" if detail else " 未完成保存后的页面跳转"
            raise AssertionError(f"点击保存后未完成提交。{suffix}") from None
        return self

    def exit_to_patient_list(self):
        """退出新增患者页面并返回患者管理页面对象。"""
        from .hzgl_page import HzglPage

        with self.page.expect_navigation(
            url="**/hz/searchbtn.shtml?tx_select_period=3",
            wait_until="domcontentloaded",
        ):
            self.page.locator('button[name="exit"]').click()
        patient_list = HzglPage(self.page)
        patient_list.is_loaded()
        return patient_list
