import pytest

from pages.hemodialysis.dialogs.prescription_medical_order_push_dialog import (
    PrescriptionMedicalOrderPushDialog,
)
from pages.hemodialysis.prescription_section import PrescriptionSection


@pytest.mark.no_auth_state
def test_first_confirmation_accepts_delayed_medical_order_push(page):
    """血液透析 > 透析处方触发：验证首次确认后自动处理医嘱推送弹窗。"""
    page.set_content(
        """
        <form id="txcf_form">
          <span id="prescription-status">未确认</span>
          <button type="button" id="confirm-prescription">确认</button>
        </form>
        <script>
          document.querySelector('#confirm-prescription').addEventListener('click', () => {
            document.querySelector('#prescription-status').textContent = '已确认';
            window.setTimeout(() => {
              const unrelatedShade = document.createElement('div');
              unrelatedShade.id = 'layui-layer-shade99';
              unrelatedShade.className = 'layui-layer-shade';
              unrelatedShade.style.cssText = 'position: fixed; inset: 0; background: rgba(0,0,0,.2); pointer-events: none;';
              document.body.appendChild(unrelatedShade);

              const shade = document.createElement('div');
              shade.id = 'layui-layer-shade2';
              shade.className = 'layui-layer-shade';
              document.body.appendChild(shade);

              const dialog = document.createElement('div');
              dialog.id = 'layui-layer2';
              dialog.setAttribute('times', '2');
              dialog.className = 'layui-layer';
              dialog.innerHTML = '<h2>医嘱推送</h2><iframe title="医嘱推送内容"></iframe>';
              document.body.appendChild(dialog);

              const iframeDocument = dialog.querySelector('iframe').contentDocument;
              iframeDocument.body.innerHTML = '<button type="button">确定</button>';
              iframeDocument.querySelector('button').addEventListener('click', () => {
                dialog.remove();
                shade.remove();
                const marker = document.createElement('div');
                marker.id = 'medical-order-pushed';
                document.body.appendChild(marker);
              });
            }, 3200);
          });
        </script>
        """
    )

    prescription = PrescriptionSection(page)
    assert isinstance(
        prescription.medical_order_push_dialog,
        PrescriptionMedicalOrderPushDialog,
    )
    assert not prescription.is_currently_confirmed()

    prescription.confirm()

    assert prescription.is_currently_confirmed()
    assert page.locator("#medical-order-pushed").count() == 1
    assert page.locator("#layui-layer-shade99:visible").count() == 1
    assert prescription.medical_order_push_dialog.is_closed()


@pytest.mark.no_auth_state
def test_current_confirmation_waits_for_delayed_prescription_status(page):
    """血液透析 > 透析处方：应等待患者确认状态异步加载完成。"""
    page.set_content(
        """
        <form id="txcf_form"><span id="status"></span></form>
        <script>
          window.setTimeout(() => {
            document.querySelector('#status').textContent = '已确认';
          }, 500);
        </script>
        """
    )

    assert PrescriptionSection(page).is_currently_confirmed()
