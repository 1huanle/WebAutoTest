import pytest

from pages.hemodialysis.dialysis_sheet_page import DialysisSheetPage


@pytest.mark.no_auth_state
def test_fill_and_confirm_end_dialysis_dialog(page):
    """血液透析 > 结束透析：填写下机护士和回血流量，不覆盖结束时间。"""
    page.set_content(
        """
        <button type="button" id="open-end">结束透析</button>
        <div id="layui-layer-shade6" style="display:none"></div>
        <div id="layui-layer6" times="6" class="layui-layer" style="display:none">
          <h2>结束透析</h2>
          <iframe title="结束透析内容"></iframe>
        </div>
        <script>
          const layer = document.querySelector('#layui-layer6');
          const shade = document.querySelector('#layui-layer-shade6');
          document.querySelector('#open-end').addEventListener('click', () => {
            layer.style.display = 'block';
            shade.style.display = 'block';
          });

          const frameDocument = layer.querySelector('iframe').contentDocument;
          frameDocument.body.innerHTML = `
            <input name="tx_end_time_hi" value="15:30" readonly>
            <select name="tx_xj_nurse"><option></option><option>陈奕源</option></select>
            <input name="tx_hx" type="number">
            <button type="button" id="confirm-end">确认</button>
            <div id="password-warning" class="layui-layer" style="display:none">
              <p>请输入陈奕源的登录密码:</p>
              <input id="srmm_pwd" type="text" placeholder="密码">
              <a href="javascript:void(0)" id="confirm-password">确定</a>
              <a href="javascript:void(0)">取消</a>
            </div>
          `;
          const passwordWarning = frameDocument.querySelector('#password-warning');
          let passwordKeydownCount = 0;
          passwordWarning.querySelector('#srmm_pwd').addEventListener('keydown', () => {
            passwordKeydownCount += 1;
          });
          frameDocument.querySelector('#confirm-end').addEventListener('click', () => {
            passwordWarning.style.display = 'block';
          });
          passwordWarning.querySelector('#confirm-password').addEventListener('click', () => {
            parent.document.body.dataset.endDialysisPassword = passwordWarning.querySelector('#srmm_pwd').value;
            parent.document.body.dataset.endDialysisPasswordKeydownCount = passwordKeydownCount;
            passwordWarning.style.display = 'none';
            layer.style.display = 'none';
            shade.style.display = 'none';
          });
        </script>
        """
    )
    page.set_default_timeout(500)

    dialysis_sheet = DialysisSheetPage(page)
    dialog = dialysis_sheet.open_end_dialysis_dialog()
    dialog.fill_end_dialysis(
        {"off_machine_nurse": "陈奕源", "blood_return_flow": "5"}
    )

    frame = dialog._frame()
    assert frame.locator('[name="tx_end_time_hi"]').input_value() == "15:30"
    assert frame.locator('[name="tx_xj_nurse"]').input_value() == "陈奕源"
    assert frame.locator('[name="tx_hx"]').input_value() == "5"

    dialog.confirm("test-password")

    assert page.locator("body").get_attribute("data-end-dialysis-password") == "test-password"
    assert page.locator("body").get_attribute(
        "data-end-dialysis-password-keydown-count"
    ) == str(len("test-password"))
    assert dialog.is_closed()
