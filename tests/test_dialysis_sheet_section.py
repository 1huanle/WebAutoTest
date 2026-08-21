import pytest

from pages.hemodialysis.dialysis_sheet_page import DialysisSheetPage
from pages.hemodialysis.dialysis_sheet_section import DialysisSheetSection


class NestedSection(DialysisSheetSection):
    """测试专用分区，用于复现真实透析单的嵌套表格结构。"""

    SECTION_TITLE = "双人核对"


@pytest.mark.no_auth_state
def test_section_root_is_single_nearest_table_when_tbody_is_nested(page):
    """公共分区根节点应只返回标题所属的最近业务表格。"""
    page.set_content(
        """
        <table id="layout"><tbody><tr><td>
          <table id="section"><tbody>
            <tr><td><div class="tx_title">双人核对</div></td></tr>
            <tr><td><select name="tx_hd_nurse"><option>陈奕源</option></select></td></tr>
          </tbody></table>
        </td></tr></tbody></table>
        """
    )

    section = NestedSection(page)

    assert section._section_table().count() == 1
    assert section._section_table().locator('[name="tx_hd_nurse"]').count() == 1


@pytest.mark.no_auth_state
def test_patient_dialysis_progress_is_read_from_matching_schedule_row(page):
    """血液透析 > 患者列表：按透析号读取对应患者是否透析中。"""
    page.set_content(
        """
        <table><tbody><tr><td>筛选区域</td></tr></tbody>
          <tbody>
            <tr><td>21000536543</td><td>陈奕源测试</td><td>透析中</td></tr>
            <tr><td>21000536544</td><td>其他患者</td><td>已签到</td></tr>
          </tbody>
        </table>
        """
    )

    dialysis_sheet = DialysisSheetPage(page)

    assert dialysis_sheet.is_patient_dialysis_in_progress("21000536543")
    assert not dialysis_sheet.is_patient_dialysis_in_progress("21000536544")


@pytest.mark.no_auth_state
def test_select_patient_waits_for_target_patient_details(page):
    """血液透析 > 患者列表：点击后应等待详情区切换到目标患者。"""
    page.set_content(
        """
        <table><tbody><tr><td>筛选区域</td></tr></tbody>
          <tbody>
            <tr id="target-patient">
              <td>2</td><td>21000536543</td><td>陈奕源测试</td>
              <td>0002</td><td>透析中</td>
            </tr>
          </tbody>
        </table>
        <input name="tx_hz_name" value="其他患者">
        <script>
          document.querySelector('#target-patient').addEventListener('click', () => {
            window.setTimeout(() => {
              document.querySelector('[name="tx_hz_name"]').value = '陈奕源测试';
            }, 500);
          });
        </script>
        """
    )

    DialysisSheetPage(page).select_patient_by_dialysis_number("21000536543")

    assert page.locator('[name="tx_hz_name"]').input_value() == "陈奕源测试"