import pytest

from pages.hemodialysis.dialysis_sheet_page import DialysisSheetPage


def install_start_dialysis_fixture(page) -> None:
    """构造只在本地运行的开始透析 iframe 弹窗。"""
    page.set_content(
        """
        <button type="button" id="open-start">开始透析</button>
        <div id="layui-layer-shade4" style="display:none"></div>
        <div id="layui-layer4" times="4" class="layui-layer" style="display:none">
          <h2>开始透析</h2>
          <iframe title="开始透析内容"></iframe>
        </div>
        <script>
          const layer = document.querySelector('#layui-layer4');
          const shade = document.querySelector('#layui-layer-shade4');
          document.querySelector('#open-start').addEventListener('click', () => {
            layer.style.display = 'block';
            shade.style.display = 'block';
          });

          const frameDocument = layer.querySelector('iframe').contentDocument;
          frameDocument.body.innerHTML = `
            <select name="tx_zl_nurse"><option></option><option>陈奕源</option></select>
            <select name="tx_sjhs"><option></option><option>陈奕源</option></select>
            <select name="tx_ycgl"><option></option><option>陈奕源</option></select>
            <select name="tx_fs"><option value="1">换药</option><option value="0">穿刺</option></select>
            <select name="tx_sj_nurse"><option></option><option>陈奕源</option></select>
            <input name="tx_ccfs" class="info-input" readonly>
            <input name="tx_ccz" class="info-input" readonly>
            <input name="tx_cczxh" class="info-input" readonly>
            <input name="tx_ccfx" class="info-input" readonly>
            <input name="tx_ccwd" readonly>
            <input name="tx_yx" type="number">
            <input name="tx_txq_no">
            <select name="tx_rkfs"><option>步行</option><option>扶行</option></select>
            <div id="choice-dialog" role="dialog" style="display:none">
              <div id="choice-buttons"></div>
              <a href="javascript:void(0)" id="choice-save">保存</a>
            </div>
            <button type="button" id="confirm-start">确认</button>
            <button type="button" id="unrelated-confirm">确定</button>
            <div id="puncture-warning" class="layui-layer" style="display:none">
              <p>穿刺点位信息未填写，是否继续保存？</p>
              <label>
                <input id="puncture-warning-never-show" type="checkbox">
                不再提示（7天内不再提示）
              </label>
              <a href="javascript:void(0)" id="puncture-warning-confirm">确定</a>
              <a href="javascript:void(0)" id="puncture-warning-cancel">取消</a>
              <a href="javascript:void(0)" style="display:none">确定</a>
            </div>
          `;

          const choices = {
            tx_ccfs: ['无', '扣眼法', '绳梯法'],
            tx_ccz: ['无', 'A锐针', 'A钝针'],
            tx_cczxh: ['A端-15号', 'A端-16号', 'A端-17号'],
            tx_ccfx: ['A端向心', 'A端离心', 'V端向心', 'V端离心'],
          };
          const choiceDialog = frameDocument.querySelector('#choice-dialog');
          const choiceButtons = frameDocument.querySelector('#choice-buttons');
          let targetInput = null;
          let selectedChoice = null;

          frameDocument.querySelectorAll('.info-input').forEach(input => {
            input.addEventListener('click', () => {
              targetInput = input;
              selectedChoice = null;
              choiceButtons.innerHTML = '';
              choices[input.name].forEach(value => {
                const button = frameDocument.createElement('button');
                button.type = 'button';
                button.textContent = value;
                button.addEventListener('click', () => { selectedChoice = value; });
                choiceButtons.appendChild(button);
              });
              choiceDialog.style.display = 'block';
            });
          });

          frameDocument.querySelector('#choice-save').addEventListener('click', () => {
            targetInput.value = selectedChoice;
            choiceDialog.style.display = 'none';
          });
          const punctureWarning = frameDocument.querySelector('#puncture-warning');
          frameDocument.querySelector('#unrelated-confirm').addEventListener('click', () => {
            document.body.dataset.unrelatedConfirmClicked = 'true';
          });
          frameDocument.querySelector('#confirm-start').addEventListener('click', () => {
            punctureWarning.style.display = 'block';
          });
          frameDocument.querySelector('#puncture-warning-confirm').addEventListener('click', () => {
            document.body.dataset.punctureWarningNeverShowChecked = String(
              frameDocument.querySelector('#puncture-warning-never-show').checked
            );
            punctureWarning.style.display = 'none';
            layer.style.display = 'none';
            shade.style.display = 'none';
            document.body.insertAdjacentHTML(
              'beforeend',
              '<div id="puncture-warning-confirmed"></div>' +
              '<div id="start-dialysis-confirmed"></div>'
            );
          });
        </script>
        """
    )


@pytest.mark.no_auth_state
def test_fill_and_confirm_start_dialysis_dialog(page):
    """血液透析 > 开始透析：填写指定内容并确认关闭弹窗。"""
    install_start_dialysis_fixture(page)

    dialysis_sheet = DialysisSheetPage(page)
    dialog = dialysis_sheet.open_start_dialysis_dialog()
    dialog.fill_start_dialysis(
        {
            "treatment_nurse": "陈奕源",
            "machine_nurse": "陈奕源",
            "priming_tubing_nurse": "陈奕源",
            "operation_type": "穿刺",
            "puncture_nurse": "陈奕源",
            "puncture_method": "扣眼法",
            "puncture_needle": "A锐针",
            "puncture_needle_model": "A端-17号",
            "puncture_direction": "V端向心",
            "blood_introduction_flow": "5",
            "admission_method": "步行",
        }
    )

    frame = dialog._frame()
    assert frame.locator('[name="tx_zl_nurse"]').input_value() == "陈奕源"
    assert frame.locator('[name="tx_sjhs"]').input_value() == "陈奕源"
    assert frame.locator('[name="tx_ycgl"]').input_value() == "陈奕源"
    assert frame.locator('[name="tx_fs"]').input_value() == "0"
    assert frame.locator('[name="tx_sj_nurse"]').input_value() == "陈奕源"
    assert frame.locator('[name="tx_ccfs"]').input_value() == "扣眼法"
    assert frame.locator('[name="tx_ccz"]').input_value() == "A锐针"
    assert frame.locator('[name="tx_cczxh"]').input_value() == "A端-17号"
    assert frame.locator('[name="tx_ccfx"]').input_value() == "V端向心"
    assert frame.locator('[name="tx_yx"]').input_value() == "5"
    assert frame.locator('[name="tx_rkfs"]').input_value() == "步行"
    assert frame.locator('[name="tx_ccwd"]').input_value() == ""
    assert frame.locator('[name="tx_txq_no"]').input_value() == ""

    dialog.confirm()

    assert page.locator("#puncture-warning-confirmed").count() == 1
    assert page.locator("body").get_attribute("data-unrelated-confirm-clicked") is None
    assert page.locator("body").get_attribute("data-puncture-warning-never-show-checked") == "false"
    assert page.locator("#start-dialysis-confirmed").count() == 1
    assert dialog.is_closed()
