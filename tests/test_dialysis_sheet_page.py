import pytest

from pages.hemodialysis.dialysis_sheet_page import DialysisSheetPage


@pytest.mark.no_auth_state
def test_run_self_check_waits_for_final_confirmation(page):
    """自查必须等待报告和最终确认请求完成，不能只点击按钮就结束。"""
    page.route(
        "**/txform/mtxform_txreport.shtml",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"status":"","txjcjl":"0","txzlxj_fx":"","txzlxj_wd":""}',
        ),
    )
    page.route(
        "**/txform/mtxform_txreport_confirm.shtml",
        lambda route: route.fulfill(status=200, body="ok"),
    )
    page.set_content(
        """
        <base href="https://example.test/">
        <button id="txform_check_btn" onclick="reporttx();">自查</button>
        <span id="result"></span>
        <script>
          function reporttx() {
            setTimeout(() => {
              fetch('txform/mtxform_txreport.shtml', {method: 'POST'})
                .then(() => fetch('txform/mtxform_txreport_confirm.shtml', {method: 'POST'}))
                .then(() => { document.querySelector('#result').textContent = '已自查'; });
            }, 100);
          }
        </script>
        """
    )

    DialysisSheetPage(page).run_self_check()

    assert page.locator("#result").inner_text() == "已自查"
