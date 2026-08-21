import pytest


@pytest.mark.no_auth_state
def test_fill_sync_and_confirm_treatment_summary(page):
    """血液透析 > 治疗小结：填写、校验、同步并确认。"""
    page.set_content(
        """
        <table><tbody>
          <tr><th>治疗小结</th><td><span class="status">未确认</span></td></tr>
          <tr><td>
            <input name="tx_xj_muban" value="宣教模板" readonly>
            <textarea name="tx_zlxj_content"></textarea>
            <input name="tx_zlxj_muban" value="小结模板" readonly>
            <textarea name="tx_zlxj_xj"></textarea>
            <select name="tx_xj_person"><option>陈奕源</option></select>
            <select name="tx_xj_qm"><option>陈奕源</option></select>
            <select name="tx_zl_fs"><option>穿刺</option></select>
            <select name="tx_sj_nurse"><option>陈奕源</option></select>
            <select name="tx_zl_nurse"><option>陈奕源</option></select>
            <select name="tx_sjhs"><option>陈奕源</option></select>
            <select name="tx_ycgl"><option>陈奕源</option></select>
            <select name="tx_hd_nurse"><option>陈奕源</option></select>
            <select name="tx_xj_nurse"><option>陈奕源</option></select>
            <select name="tx_zl_doctor"><option>陈奕源</option></select>
            <input name="tx_tltp" value="通路图片" readonly>
            <input name="tx_txq_no">
            <button type="button">确认</button><button type="button">同步到病程</button>
            <button type="button">同步到交班日志</button>
          </td></tr>
        </tbody></table>
        <script>
          document.querySelectorAll('button').forEach(button => button.addEventListener('click', () => {
            document.body.dataset.action = button.textContent;
            if (button.textContent === '确认') document.querySelector('.status').textContent = '已确认';
          }));
        </script>
        """
    )

    from pages.hemodialysis.treatment_summary_section import TreatmentSummarySection

    summary = TreatmentSummarySection(page)
    summary.fill_summary(
        {
            "education_content": "透后注意休息",
            "summary": "治疗过程平稳",
            "dialyzer_number": "D-001",
            "educator": "陈奕源", "summary_signer": "陈奕源",
            "puncture_or_dressing": "穿刺", "dressing_nurse": "陈奕源",
            "treatment_nurse": "陈奕源", "machine_start_nurse": "陈奕源",
            "priming_nurse": "陈奕源", "checker": "陈奕源",
            "machine_stop_nurse": "陈奕源", "treatment_doctor": "陈奕源",
        }
    )
    summary.expect_readonly_values(
        {"education_template": "宣教模板", "summary_template": "小结模板", "access_image": "通路图片"}
    )
    summary.sync_to_medical_record().sync_to_handover_log().confirm()

    assert summary.is_confirmed()
