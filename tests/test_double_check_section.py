import pytest


@pytest.mark.no_auth_state
def test_double_check_uses_business_labels_instead_of_checkbox_indexes(page):
    """血液透析 > 双人核对：按业务标签勾选明细并完成核对。"""
    page.set_content(
        """
        <input id="outside" type="checkbox">
        <table><tbody>
          <tr><th>双人核对</th><td><span class="status">未确认</span></td></tr>
          <tr><td>
            <input type="checkbox" name="tx_touXiWuPin_indicator">
            <input name="tx_touXiWuPin_error">
            <input type="checkbox" name="tx_touXiCanShu_indicator">
            <input name="tx_touXiCanShu_error">
            <input type="checkbox" name="tx_xueGuanTongLu_indicator">
            <input name="tx_xueGuanTongLu_error">
            <input type="checkbox" name="tx_guanDao_indicator">
            <input name="tx_guanDao_error">
          </td></tr>
          <tr><td><input type="checkbox"></td><td><span>人工肾</span></td></tr>
          <tr><td><input type="checkbox"></td><td><span>透析方式</span></td></tr>
          <tr><td>
            <select name="tx_hd_nurse"><option>陈奕源</option></select>
            <input name="tx_check_time" value="2026-08-06 11:30" readonly>
            <button type="button">确认</button>
          </td></tr>
        </tbody></table>
        <div id="same-nurse-warning" class="layui-layer" style="display:none">
          <p>核对人员和治疗护士确认是同一个人吗？</p>
          <button type="button">确定</button>
          <button type="button">取消</button>
        </div>
        <script>
          const warning = document.querySelector('#same-nurse-warning');
          document.querySelector('table button').addEventListener('click', () => {
            warning.style.display = 'block';
          });
          warning.querySelector('button').addEventListener('click', () => {
            warning.style.display = 'none';
            document.querySelector('.status').textContent = '已确认';
          });
        </script>
        """
    )

    from pages.hemodialysis.double_check_section import DoubleCheckSection

    double_check = DoubleCheckSection(page)
    double_check.mark_group_correct("dialysis_items")
    double_check.fill_group_error("dialysis_parameters", "参数已复核")
    double_check.set_detail_checked("人工肾", True)
    double_check.set_detail_checked("透析方式", True)
    double_check.select_checker("陈奕源")

    assert page.locator('[name="tx_touXiWuPin_indicator"]').is_checked()
    assert not page.locator('[name="tx_touXiCanShu_indicator"]').is_checked()
    assert page.locator('[name="tx_touXiCanShu_error"]').input_value() == "参数已复核"
    assert not page.locator("#outside").is_checked()
    assert double_check.get_check_time() == "2026-08-06 11:30"
    assert not double_check.is_currently_confirmed()
    double_check.confirm()
    assert page.locator("#same-nurse-warning").is_hidden()
    assert double_check.is_confirmed()
    assert double_check.is_currently_confirmed()
