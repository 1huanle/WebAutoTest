import pytest

from pages.hemodialysis.dialysis_sheet_page import DialysisSheetPage
from pages.hemodialysis.hemodialysis_page import HemodialysisPage


@pytest.mark.regression
def test_hemodialysis_module_is_loaded_for_director(page):
    """验证主任登录态可进入并识别血液透析模块。"""
    module_page = HemodialysisPage(page).open()

    assert module_page.module_name == "血液透析"
    assert module_page.is_loaded()
    assert "血液透析" in module_page.get_top_level_modules()


@pytest.mark.regression
def test_dialysis_sheet_exposes_schedule_and_patient_search(page):
    """验证血液透析的透析单可读取排班信息和患者检索入口。"""
    dialysis_sheet = DialysisSheetPage(page).open()

    assert dialysis_sheet.is_loaded()
    assert dialysis_sheet.get_schedule_date()
    assert dialysis_sheet.get_visible_patient_count() >= 0
    assert dialysis_sheet.patient_search_placeholder == "透析号/姓名/姓名首拼"