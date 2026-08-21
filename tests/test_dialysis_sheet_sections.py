import pytest

from pages.hemodialysis.dialysis_sheet_page import DialysisSheetPage


@pytest.mark.regression
def test_dialysis_prescription_section_is_visible(page):
    """验证血液透析透析单中的透析处方分区可读取。"""
    dialysis_sheet = DialysisSheetPage(page).open()

    assert dialysis_sheet.prescription.is_visible()
    assert "确认" in dialysis_sheet.prescription.get_visible_actions()


@pytest.mark.regression
def test_pre_dialysis_assessment_section_is_visible(page):
    """验证血液透析透析单中的透前评估分区可读取。"""
    dialysis_sheet = DialysisSheetPage(page).open()

    assert dialysis_sheet.pre_dialysis_assessment.is_visible()
    assert "确认" in dialysis_sheet.pre_dialysis_assessment.get_visible_actions()


@pytest.mark.regression
def test_temporary_orders_section_is_visible(page):
    """验证血液透析透析单中的临时医嘱分区可读取。"""
    dialysis_sheet = DialysisSheetPage(page).open()

    assert dialysis_sheet.temporary_orders.is_visible()
    assert {"添加医嘱", "医嘱模板", "执行医嘱", "删除"}.issubset(
        dialysis_sheet.temporary_orders.get_visible_actions()
    )

@pytest.mark.regression
@pytest.mark.parametrize(
    ("section_property", "section_title", "expected_action"),
    [
        ("double_check", "双人核对", "确认"),
        ("monitoring_records", "监测记录", "确认"),
        ("post_dialysis_assessment", "透后评估", "确认"),
        ("treatment_summary", "治疗小结", "确认"),
    ],
)
def test_remaining_dialysis_sheet_sections_are_visible(
    page, section_property, section_title, expected_action
):
    """验证血液透析透析单的其余只读业务分区可读取。"""
    dialysis_sheet = DialysisSheetPage(page).open()
    section = getattr(dialysis_sheet, section_property)

    assert section.SECTION_TITLE == section_title
    assert section.is_visible()
    assert expected_action in section.get_visible_actions()

@pytest.mark.regression
def test_dialysis_sheet_sections_expose_visible_field_labels(page):
    """验证血液透析分区可读取当前可见的表单字段标签。"""
    dialysis_sheet = DialysisSheetPage(page).open()

    assert "机号:" in dialysis_sheet.prescription.get_visible_field_labels()
    assert "T(℃):" in dialysis_sheet.pre_dialysis_assessment.get_visible_field_labels()

@pytest.mark.regression
def test_remaining_sections_expose_primary_controls(page):
    """只读验证六个血液透析业务 POM 的主控件均来自真实页面。"""
    dialysis_sheet = DialysisSheetPage(page).open()

    assert "确认" in dialysis_sheet.pre_dialysis_assessment.get_visible_actions()
    assert "添加医嘱" in dialysis_sheet.temporary_orders.get_visible_actions()
    assert dialysis_sheet.double_check._field("tx_hd_nurse").count() == 1
    assert "添加监测" in dialysis_sheet.monitoring_records.get_visible_actions()
    assert "确认" in dialysis_sheet.post_dialysis_assessment.get_visible_actions()
    assert dialysis_sheet.treatment_summary._field("tx_zlxj_content").count() == 1
    assert {"同步到病程", "同步到交班日志"}.issubset(
        dialysis_sheet.treatment_summary.get_visible_actions()
    )
