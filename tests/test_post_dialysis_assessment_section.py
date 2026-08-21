import pytest


@pytest.mark.no_auth_state
def test_fill_and_confirm_post_dialysis_assessment(page):
    """血液透析 > 透后评估：填写真实字段、校验联动值并确认。"""
    page.set_content(
        """
        <table><tbody>
          <tr><th>透后评估</th><td><span class="status">未确认</span></td></tr>
          <tr><td>
            <input name="tx_pg_t"><input name="tx_pg_p"><input name="tx_pg_hr">
            <select name="tx_pg_hr_type"><option>自主呼吸</option></select>
            <input name="tx_pg_BP_shousuo"><input name="tx_pg_BP_shuzhang">
            <select name="tx_pg_BP_type" onchange="
              document.querySelector('[name=tx_pg_BP_shousuo]').value = '';
              document.querySelector('[name=tx_pg_BP_shuzhang]').value = '';
            "><option>上肢</option></select>
            <input name="txh_sjcll"><input name="txh_sjzhl">
            <input name="txh_sjsc_h"><input name="txh_sjsc_f">
            <select id="txh_czfs"><option>正常</option></select>
            <input name="txh_cz"><input name="tx_peel_weight_h">
            <input name="tx_sjcll"><input name="tx_fyl"><input name="tx_qt">
            <input name="tx_max_ll"><input name="tx_twxhlx"><input name="tx_lxjl">
            <input name="tx_sscd"><input name="tx_xgwz"><input name="tx_fsyy_sj">
            <input name="txh_tz" value="69" readonly>
            <input name="txh_tzjs" value="1" readonly>
            <input name="txh_nx_name" value="默认的" readonly>
            <input name="txh_tqzz_name" value="/" readonly>
            <input name="txh_txzrl_h_hidden" value="/" readonly>
            <input name="txh_nl_name" value="/" readonly>
            <input name="txh_dg_name" value="/" readonly>
            <input name="txh_hbz_name" value="/" readonly>
            <button type="button">确认</button>
          </td></tr>
        </tbody></table>
        <script>
          document.querySelector('button').addEventListener('click', () => {
            document.querySelector('.status').textContent = '已确认';
          });
        </script>
        """
    )

    from pages.hemodialysis.post_dialysis_assessment_section import (
        PostDialysisAssessmentSection,
    )

    assessment = PostDialysisAssessmentSection(page)
    assessment.fill_assessment(
        {
            "temperature": "36.5", "pulse": "80", "respiration": "20",
            "respiration_type": "自主呼吸", "systolic_pressure": "110",
            "diastolic_pressure": "80", "blood_pressure_site": "上肢",
            "actual_ultrafiltration_ml": "1000", "actual_replacement_liters": "0",
            "treatment_hours": "4", "treatment_minutes": "0", "weighing_method": "正常",
            "post_weight": "69", "clothing_weight": "0", "actual_treatment_liters": "/",
            "waste_liquid_liters": "/", "other": "/", "maximum_blood_flow": "225",
            "extracorporeal_blood_leak": "/", "blood_leak_dose": "/",
            "injury_degree": "/", "vascular_location": "/", "cause_and_timing": "/",
        }
    )
    assessment.expect_calculated_values(
        {
            "post_dialysis_weight": "69", "weight_reduction": "1",
            "coagulation": "默认的", "post_dialysis_symptoms": "/",
            "total_intake": "/", "fistula": "/", "catheter": "/", "complications": "/",
        }
    )
    assessment.confirm()

    assert assessment.is_confirmed()
    assert page.locator('[name="tx_pg_BP_shousuo"]').input_value() == "110"
    assert page.locator('[name="tx_pg_BP_shuzhang"]').input_value() == "80"
