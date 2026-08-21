import pytest

from pages.hemodialysis.pre_dialysis_assessment_section import (
    PreDialysisAssessmentSection,
)


@pytest.mark.no_auth_state
def test_fill_and_confirm_pre_dialysis_assessment(page):
    """血液透析 > 透前评估：填写可编辑项并确认。"""
    page.set_content(
        """
        <table class="tx_table"><tbody>
          <tr><th>透前评估</th><td><span class="status">未确认</span></td></tr>
          <tr><td>
            <input name="tx_pg_t"><input name="tx_pg_p"><input name="tx_pg_hr">
            <select name="tx_pg_hr_type"><option>自主呼吸</option></select>
            <input name="tx_pg_BP_shousuo"><input name="tx_pg_BP_shuzhang">
            <select name="tx_pg_BP_type" onchange="
              document.querySelector('[name=tx_pg_BP_shousuo]').value = '';
              document.querySelector('[name=tx_pg_BP_shuzhang]').value = '';
            "><option>上肢</option></select>
            <select id="txq_czfs"><option>正常</option></select>
            <input name="tx_tqcz"><input name="tx_peel_weight"><input name="tx_yztsl">
            <input name="tx_tqtz" readonly>
            <input name="tx_a_xx"><input name="tx_v_xx">
            <button type="button" class="confirm">确认</button>
          </td></tr>
        </tbody></table>
        <script>
          document.querySelector('[name="tx_tqcz"]').addEventListener('keyup', () => {
            document.querySelector('[name="tx_tqtz"]').value =
              document.querySelector('[name="tx_tqcz"]').value;
          });
          document.querySelector('.confirm').addEventListener('click', () => {
            document.querySelector('.status').textContent = '已确认';
          });
        </script>
        """
    )

    assessment = PreDialysisAssessmentSection(page)
    assert not assessment.is_currently_confirmed()
    assessment.fill_assessment(
        {
            "temperature": "36",
            "pulse": "80",
            "respiration": "20",
            "respiration_type": "自主呼吸",
            "systolic_pressure": "110",
            "diastolic_pressure": "80",
            "blood_pressure_site": "上肢",
            "weighing_method": "正常",
            "pre_weight": "70",
            "clothing_weight": "0",
            "expected_dehydration_liters": "0",
            "a_thrombus": "/",
            "v_thrombus": "/",
        }
    )
    assessment.confirm()

    assert assessment.is_confirmed()
    assert assessment.is_currently_confirmed()
    assert page.locator('[name="tx_pg_t"]').input_value() == "36"
    assert page.locator('[name="tx_pg_BP_shousuo"]').input_value() == "110"
    assert page.locator('[name="tx_pg_BP_shuzhang"]').input_value() == "80"
    assert page.locator('[name="tx_tqtz"]').input_value() == "70"
    assert page.locator('#txq_czfs').input_value() == "正常"


@pytest.mark.no_auth_state
def test_current_confirmation_waits_for_delayed_assessment_status(page):
    """血液透析 > 透前评估：应等待患者确认状态异步加载完成。"""
    page.set_content(
        """
        <table><tbody>
          <tr><th>透前评估</th><td><span id="status"></span></td></tr>
        </tbody></table>
        <script>
          window.setTimeout(() => {
            document.querySelector('#status').textContent = '已确认';
          }, 500);
        </script>
        """
    )

    assert PreDialysisAssessmentSection(page).is_currently_confirmed()
