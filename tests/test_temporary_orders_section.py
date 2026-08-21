import time

import pytest

from pages.hemodialysis.temporary_orders_section import TemporaryOrdersSection


@pytest.mark.no_auth_state
def test_temporary_orders_list_actions_are_scoped_to_selected_order(page):
    """血液透析 > 临时医嘱：按医嘱内容选择行并执行分区内操作。"""
    page.set_content(
        """
        <table><tbody>
          <tr><th>临时医嘱</th></tr>
          <tr><td>
            <button>添加医嘱</button><button>医嘱模板</button>
            <button>执行医嘱</button><button>核对医嘱</button><button>删除</button>
          </td></tr>
          <tr><th>选择</th><th>医嘱内容</th><th>状态</th></tr>
          <tr><td><input type="checkbox"></td><td>测试医嘱</td><td>待执行</td></tr>
          <tr><td><input type="checkbox"></td><td>其他医嘱</td><td>已执行</td></tr>
        </tbody></table>
        <script>
          document.querySelectorAll('button').forEach(button => {
            button.addEventListener('click', () => document.body.dataset.action = button.textContent);
          });
        </script>
        """
    )

    orders = TemporaryOrdersSection(page)
    assert orders.get_order_headers() == ["选择", "医嘱内容", "状态"]
    assert ["测试医嘱", "待执行"] in orders.get_order_rows()
    orders.select_order("测试医嘱")
    assert page.get_by_role("row").filter(has_text="测试医嘱").get_by_role(
        "checkbox"
    ).is_checked()

    orders.open_add_order()
    assert page.locator("body").get_attribute("data-action") == "添加医嘱"
    orders.open_order_template()
    orders.execute_selected()
    orders.check_selected()
    orders.delete_selected()
    assert page.locator("body").get_attribute("data-action") == "删除"


@pytest.mark.no_auth_state
def test_add_orders_skips_existing_order_name(page):
    """血液透析 > 临时医嘱：重跑时已有同名医嘱不得再次打开新增弹窗。"""
    page.set_content(
        """
        <table><tbody>
          <tr><th><span>临时医嘱</span></th></tr>
          <tr><td><button id="open-add">添加医嘱</button></td></tr>
          <tr><td><table><tbody>
            <tr><td><input class="tx_yz_checkbox" type="checkbox"
              data-yzid="existing-1" data-zxsj=""></td>
              <td>陈奕源测试(mg*) 10mg 1支 皮下注射 上午</td></tr>
          </tbody></table></td></tr>
        </tbody></table>
        <script>
          document.querySelector('#open-add').addEventListener('click', () => {
            document.body.dataset.addDialogOpened = 'true';
          });
        </script>
        """
    )

    TemporaryOrdersSection(page).add_orders(
        [{"fields": {"order_name": "陈奕源测试"}}]
    )

    assert page.locator("body").get_attribute("data-add-dialog-opened") is None



@pytest.mark.no_auth_state
def test_existing_order_name_waits_for_delayed_order_list(page):
    """血液透析 > 临时医嘱：应等待目标医嘱异步回填列表。"""
    page.set_content(
        """
        <table><tbody>
          <tr><th><span>临时医嘱</span></th></tr>
          <tr><td><table><tbody id="order-rows"></tbody></table></td></tr>
        </tbody></table>
        <script>
          window.setTimeout(() => {
            const row = document.createElement('tr');
            row.innerHTML =
              '<td><input class="tx_yz_checkbox" type="checkbox" ' +
              'data-yzid="existing-1" data-zxsj=""></td>' +
              '<td>陈奕源测试(mg*) 10mg 1支</td>';
            document.querySelector('#order-rows').appendChild(row);
          }, 500);
        </script>
        """
    )

    assert TemporaryOrdersSection(page).has_order_name("陈奕源测试")


@pytest.mark.no_auth_state
def test_existing_order_name_does_not_match_longer_name(page):
    """血液透析 > 临时医嘱：较长医嘱名不能误判为已有短名称。"""
    page.set_content(
        """
        <table><tbody>
          <tr><th><span>临时医嘱</span></th></tr>
          <tr><td><table><tbody>
            <tr><td><input class="tx_yz_checkbox" type="checkbox"
              data-yzid="existing-1" data-zxsj=""></td>
              <td>陈奕源测试扩展(mg*) 10mg 1支</td></tr>
          </tbody></table></td></tr>
        </tbody></table>
        """
    )

    assert not TemporaryOrdersSection(page).has_order_name("陈奕源测试")


@pytest.mark.no_auth_state
def test_order_autocomplete_uses_keyboard_input_to_load_candidate(page):
    """血液透析 > 临时医嘱：应通过键盘输入加载并选择候选。"""
    page.set_content(
        """
        <div class="layui-layer"><h2>临时医嘱</h2><iframe></iframe></div>
        <script>
          const frameDocument = document.querySelector('iframe').contentDocument;
          frameDocument.body.innerHTML =
            '<table><tbody>' +
            '<tr><td><input name="tx_advicename">' +
            '<div class="select_div"></div></td></tr>' +
            '<tr><td><input name="tx_wayadminister">' +
            '<div class="select_div"></div></td></tr>' +
            '<tr><td><input name="tx_frequency">' +
            '<div class="select_div"></div></td></tr>' +
            '</tbody></table>';
          const field = frameDocument.querySelector('[name="tx_advicename"]');
          field.addEventListener('keydown', () => {
            window.setTimeout(() => {
              const candidate = frameDocument.createElement('li');
              candidate.textContent = '陈奕源测试mg*';
              candidate.addEventListener('click', () => {
                document.body.dataset.slowCandidateSelected = 'true';
              });
              field.closest('td').querySelector('.select_div').appendChild(candidate);
          }, 100);
        });
        </script>
        """
    )

    dialog = TemporaryOrdersSection(page).order_dialog.wait_for_open()
    dialog.AUTOCOMPLETE_TIMEOUT = 1_000
    dialog.fill_order(
        {
            "order_name": "陈奕源测试",
            "order_option": "陈奕源测试mg*",
        }
    )

    assert page.locator("body").get_attribute(
        "data-slow-candidate-selected"
    ) == "true"


@pytest.mark.no_auth_state
def test_order_autocomplete_accepts_selected_display_value(page):
    """血液透析 > 临时医嘱：候选展示值可不同于搜索词。"""
    page.set_content(
        """
        <div class="layui-layer"><h2>临时医嘱</h2><iframe></iframe></div>
        <script>
          const frameDocument = document.querySelector('iframe').contentDocument;
          frameDocument.body.innerHTML =
            '<table><tbody><tr><td>' +
            '<input name="tx_wayadminister"><div class="select_div"></div>' +
            '</td></tr></tbody></table>';
          const field = frameDocument.querySelector('[name="tx_wayadminister"]');
          field.addEventListener('keydown', () => {
            const candidate = frameDocument.createElement('li');
            candidate.textContent = '胰岛素皮下注射';
            candidate.addEventListener('click', () => {
              field.value = candidate.textContent;
            });
            field.closest('td').querySelector('.select_div').appendChild(candidate);
          }, { once: true });
        </script>
        """
    )

    dialog = TemporaryOrdersSection(page).order_dialog.wait_for_open()
    dialog.AUTOCOMPLETE_TIMEOUT = 1_000
    dialog._select_autocomplete(
        "tx_wayadminister", "皮下注射", "胰岛素皮下注射"
    )

    assert dialog._field("tx_wayadminister").input_value() == "胰岛素皮下注射"


@pytest.mark.no_auth_state
def test_add_temporary_orders_with_real_autocomplete_fields(page):
    """血液透析 > 临时医嘱：按真实自动补全字段连续新增两条医嘱。"""
    page.set_content(
        """
        <table><tbody>
          <tr><th><span>临时医嘱</span></th></tr>
          <tr><td><button id="open-add">添加医嘱</button></td></tr>
          <tr><td><table><tbody id="added-order-rows"></tbody></table></td></tr>
        </tbody></table>
        <div id="layui-layer-shade3" style="display:none"></div>
        <div id="temporary-order-layer" times="3" class="layui-layer" style="display:none">
          <h2>临时医嘱</h2><iframe></iframe>
        </div>
        <script>
          window.addedOrders = [];
          const layer = document.querySelector('#temporary-order-layer');
          const shade = document.querySelector('#layui-layer-shade3');
          const frameDocument = layer.querySelector('iframe').contentDocument;
          frameDocument.body.innerHTML = `
            <input name="tx_advicestyle" value="临时" readonly>
            <input name="tx_lsyz_kz_doctor" value="陈奕源" readonly>
            <table><tbody>
              <tr><td><input name="tx_advicename" placeholder="名称/拼音码">
                <div class="select_div"></div></td></tr>
              <tr><td><input name="tx_wayadminister" placeholder="名称/拼音码">
                <div class="select_div"></div></td></tr>
              <tr><td><input name="tx_frequency" placeholder="名称/拼音码">
                <div class="select_div"></div></td></tr>
            </tbody></table>
            <input name="tx_advicedescript" readonly>
            <input name="tx_singledosage" type="number">
            <input name="tx_drugnumber" type="number">
            <select name="execution_department"><option value="">请选择</option></select>
            <select name="tx_diagnose_select" multiple></select>
            <textarea name="tx_yznote"></textarea>
            <button type="button" id="unrelated-order-option">陈奕源测试mg*</button>
            <button type="button" id="unrelated-yes">是</button>
            <button type="button" id="confirm-order">确认</button>
            <div id="missing-fields-warning" class="layui-layer" style="display:none">
              <p>给药途径、执行频率未填写，是否继续保存?</p>
              <button type="button" id="continue-save">是</button>
              <button type="button">否</button>
            </div>
          `;

          const fields = name => frameDocument.querySelector(`[name="${name}"]`);
          const orderOptions = {
            '陈奕源测试': ['陈奕源测试mg*', 'mg* 分散片'],
            '陈奕源低分子肝素测试': [
              '陈奕源低分子肝素测试12μg*1', '12μg*1 注射剂'
            ],
          };

          function clearSuggestions() {
            frameDocument.querySelectorAll('.select_div').forEach(container => {
              container.innerHTML = '';
            });
          }
          function showSuggestion(field, text, onSelect) {
            clearSuggestions();
            const list = frameDocument.createElement('ul');
            list.className = 'list-group';
            const item = frameDocument.createElement('li');
            item.className = 'list-group-item';
            item.textContent = text;
            item.addEventListener('click', onSelect);
            list.appendChild(item);
            field.closest('td').querySelector('.select_div').appendChild(list);
          }

          fields('tx_advicename').addEventListener('input', event => {
            const [option, description] = orderOptions[event.target.value] || [];
            if (!option) return;
            showSuggestion(event.target, option, () => {
              fields('tx_advicename').value = event.target.value;
              fields('tx_advicedescript').value = description;
              clearSuggestions();
            });
          });
          ['tx_wayadminister', 'tx_frequency'].forEach(name => {
            fields(name).addEventListener('input', event => {
              if (!event.target.value) return;
              const value = event.target.value;
              showSuggestion(event.target, value, () => {
                fields(name).value = value;
                clearSuggestions();
              });
            });
          });

          function resetForm() {
            [
              'tx_advicename', 'tx_advicedescript', 'tx_singledosage',
              'tx_drugnumber', 'tx_yznote'
            ].forEach(name => { fields(name).value = ''; });
            clearSuggestions();
          }
          document.querySelector('#open-add').addEventListener('click', () => {
            resetForm(); layer.style.display = 'block'; shade.style.display = 'block';
          });
          frameDocument.querySelector('#unrelated-order-option').addEventListener(
            'click', () => { document.body.dataset.unrelatedOrderOptionClicked = 'true'; }
          );
          frameDocument.querySelector('#unrelated-yes').addEventListener(
            'click', () => { document.body.dataset.unrelatedYesClicked = 'true'; }
          );
          function saveOrder() {
            const addedOrder = {
              order_name: fields('tx_advicename').value,
              order_description: fields('tx_advicedescript').value,
              single_dose: fields('tx_singledosage').value,
              quantity: fields('tx_drugnumber').value,
              administration_route: fields('tx_wayadminister').value,
              frequency: fields('tx_frequency').value,
            };
            window.addedOrders.push(addedOrder);
            const orderId = 'added-' + window.addedOrders.length;
            setTimeout(() => {
              const row = document.createElement('tr');
              row.innerHTML =
                '<td><input class="tx_yz_checkbox" type="checkbox" ' +
                'data-yzid="' + orderId + '" data-zxsj=""></td><td>' +
                addedOrder.order_name + '</td>';
              document.querySelector('#added-order-rows').appendChild(row);
            }, 500);
            layer.style.display = 'none'; shade.style.display = 'none';
          }
          frameDocument.querySelector('#confirm-order').addEventListener('click', () => {
            if (!fields('tx_wayadminister').value && !fields('tx_frequency').value) {
              frameDocument.querySelector('#missing-fields-warning').style.display = 'block';
              return;
            }
            saveOrder();
          });
          frameDocument.querySelector('#continue-save').addEventListener('click', () => {
            frameDocument.querySelector('#missing-fields-warning').style.display = 'none';
            saveOrder();
          });
        </script>
        """
    )

    orders = TemporaryOrdersSection(page)
    orders.add_orders(
        [
            {
                "fields": {
                    "order_name": "陈奕源测试",
                    "order_option": "陈奕源测试mg*",
                    "single_dose": "10",
                    "quantity": "1",
                    "administration_route": "皮下注射",
                    "frequency": "上午",
                },
                "expected": {"order_description": "mg* 分散片"},
            },
            {
                "fields": {
                    "order_name": "陈奕源低分子肝素测试",
                    "order_option": "陈奕源低分子肝素测试12μg*1",
                    "single_dose": "12",
                    "quantity": "1",
                },
                "expected": {"order_description": "12μg*1 注射剂"},
            },
        ]
    )

    assert page.evaluate("window.addedOrders") == [
        {
            "order_name": "陈奕源测试",
            "order_description": "mg* 分散片",
            "single_dose": "10",
            "quantity": "1",
            "administration_route": "皮下注射",
            "frequency": "上午",
        },
        {
            "order_name": "陈奕源低分子肝素测试",
            "order_description": "12μg*1 注射剂",
            "single_dose": "12",
            "quantity": "1",
            "administration_route": "",
            "frequency": "",
        },
    ]
    assert page.locator("#layui-layer-shade3").is_hidden()
    assert page.locator("#added-order-rows .tx_yz_checkbox").count() == 2
    assert page.locator("body").get_attribute(
        "data-unrelated-order-option-clicked"
    ) is None
    assert page.locator("body").get_attribute("data-unrelated-yes-clicked") is None


@pytest.mark.no_auth_state
def test_execute_all_unexecuted_temporary_orders(page):
    """血液透析 > 临时医嘱：动态快照并逐条执行全部未执行医嘱。"""
    page.set_content(
        """
        <table><tbody>
          <tr><th><span>临时医嘱</span></th></tr>
          <tr><td><button id="open-execution">执行医嘱</button></td></tr>
          <tr><td><table><tbody id="order-rows">
            <tr><td><input class="tx_yz_checkbox" type="checkbox"
              data-yzid="pending-1" data-zxsj=""></td><td>医嘱一</td></tr>
            <tr><td><input class="tx_yz_checkbox" type="checkbox"
              data-yzid="done-1" data-zxsj="2026-08-06 10:00"></td><td>已执行医嘱</td></tr>
            <tr><td><input class="tx_yz_checkbox" type="checkbox"
              data-yzid="pending-2" data-zxsj=""></td><td>医嘱二</td></tr>
            <tr><td><input class="tx_yz_checkbox" type="checkbox"
              data-yzid="pending-3" data-zxsj=""></td><td>医嘱三</td></tr>
          </tbody></table></td></tr>
        </tbody></table>
        <div id="layui-layer-shade5" style="display:none"></div>
        <div id="execution-layer" times="5" class="layui-layer" style="display:none">
          <h2>执行医嘱</h2><iframe></iframe>
        </div>
        <script>
          window.executedOrderIds = [];
          window.executionRecords = [];
          let selectedCheckbox = null;
          const layer = document.querySelector('#execution-layer');
          const shade = document.querySelector('#layui-layer-shade5');
          const frameDocument = layer.querySelector('iframe').contentDocument;
          frameDocument.body.innerHTML = `
            <input name="tx_lsyz_zxsj" value="2026-08-06 20:21">
            <input name="tx_lsyz_qm_nurse" value="陈奕源" readonly>
            <input name="tx_lsyz_hd_nurse" value="陈奕源" readonly>
            <textarea name="tx_yznote"></textarea>
            <button type="button" id="execute-current">执行</button>
            <button type="button" id="unrelated-execution-confirm">确定</button>
            <div id="same-nurse-warning" class="layui-layer" style="display:none">
              <p>执行人员和核对人员确认是同一个人吗?</p>
              <button type="button" id="same-nurse-confirm">确定</button>
              <button type="button">取消</button>
            </div>
          `;

          document.querySelector('#open-execution').addEventListener('click', () => {
            selectedCheckbox = document.querySelector('.tx_yz_checkbox:checked');
            if (!selectedCheckbox) return;
            frameDocument.querySelector('[name="tx_yznote"]').value = '';
            layer.style.display = 'block'; shade.style.display = 'block';
          });
          frameDocument.querySelector('#unrelated-execution-confirm').addEventListener(
            'click', () => { document.body.dataset.unrelatedExecutionConfirmClicked = 'true'; }
          );
          function finishExecution() {
            const orderId = selectedCheckbox.dataset.yzid;
            const orderText = selectedCheckbox.closest('tr').cells[1].textContent;
            const selectedRow = selectedCheckbox.closest('tr');
            window.executedOrderIds.push(orderId);
            window.executionRecords.push({
              execution_nurse: frameDocument.querySelector(
                '[name="tx_lsyz_qm_nurse"]'
              ).value,
              verification_nurse: frameDocument.querySelector(
                '[name="tx_lsyz_hd_nurse"]'
              ).value,
              note: frameDocument.querySelector('[name="tx_yznote"]').value,
            });
            selectedRow.remove();
            setTimeout(() => {
              const row = document.createElement('tr');
              row.innerHTML =
                '<td><input class="tx_yz_checkbox" type="checkbox" ' +
                'data-yzid="' + orderId +
                '" data-zxsj="2026-08-06 20:21"></td><td>' +
                orderText + '</td>';
              document.querySelector('#order-rows').appendChild(row);
            }, 500);
            layer.style.display = 'none'; shade.style.display = 'none';
          }
          frameDocument.querySelector('#execute-current').addEventListener('click', () => {
            const executionNurse = frameDocument.querySelector(
              '[name="tx_lsyz_qm_nurse"]'
            ).value;
            const verificationNurse = frameDocument.querySelector(
              '[name="tx_lsyz_hd_nurse"]'
            ).value;
            if (executionNurse === verificationNurse) {
              frameDocument.querySelector('#same-nurse-warning').style.display = 'block';
              return;
            }
            finishExecution();
          });
          frameDocument.querySelector('#same-nurse-confirm').addEventListener('click', () => {
            frameDocument.querySelector('#same-nurse-warning').style.display = 'none';
            finishExecution();
          });
        </script>
        """
    )

    orders = TemporaryOrdersSection(page)
    orders.execute_all_unexecuted(
        {
            "execution_nurse": "陈奕源",
            "verification_nurse": "陈奕源",
            "note": "",
        }
    )

    assert page.evaluate("window.executedOrderIds") == [
        "pending-1",
        "pending-2",
        "pending-3",
    ]
    assert page.evaluate("window.executionRecords") == [
        {
            "execution_nurse": "陈奕源",
            "verification_nurse": "陈奕源",
            "note": "",
        }
    ] * 3
    assert page.locator('[data-yzid="pending-3"]').count() == 1
    assert page.locator('.tx_yz_checkbox[data-zxsj=""]').count() == 0
    assert page.locator('[data-yzid="done-1"]').get_attribute(
        "data-zxsj"
    ) == "2026-08-06 10:00"
    assert page.locator("body").get_attribute(
        "data-unrelated-execution-confirm-clicked"
    ) is None


@pytest.mark.no_auth_state
def test_execute_order_skips_same_nurse_warning_for_different_people(page):
    """血液透析 > 临时医嘱：执行人与核对人不同时不等待同人提示。"""
    page.set_content(
        """
        <div id="layui-layer-shade5"></div>
        <div id="execution-layer" times="5" class="layui-layer">
          <h2>执行医嘱</h2><iframe></iframe>
        </div>
        <script>
          const layer = document.querySelector('#execution-layer');
          const shade = document.querySelector('#layui-layer-shade5');
          const frameDocument = layer.querySelector('iframe').contentDocument;
          frameDocument.body.innerHTML = `
            <input name="tx_lsyz_zxsj" value="2026-08-06 21:41">
            <input name="tx_lsyz_qm_nurse" value="陈奕源" readonly>
            <input name="tx_lsyz_hd_nurse" value="其他护士" readonly>
            <textarea name="tx_yznote"></textarea>
            <button type="button" id="execute-current">执行</button>
          `;
          frameDocument.querySelector('#execute-current').addEventListener('click', () => {
            document.body.dataset.executedWithDifferentNurses = 'true';
            layer.style.display = 'none';
            shade.style.display = 'none';
          });
        </script>
        """
    )

    dialog = TemporaryOrdersSection(page).execution_dialog.wait_for_open()
    dialog.fill_execution(
        {
            "execution_nurse": "陈奕源",
            "verification_nurse": "其他护士",
            "note": "",
        }
    )

    started_at = time.monotonic()
    dialog.execute()

    assert time.monotonic() - started_at < 2
    assert page.locator("body").get_attribute(
        "data-executed-with-different-nurses"
    ) == "true"


@pytest.mark.no_auth_state
def test_fill_and_cancel_temporary_order_dialog(page):
    """血液透析 > 临时医嘱触发：填写 iframe 后取消且只关闭所属遮罩。"""
    page.set_content(
        """
        <div id="layui-layer-shade3" class="layui-layer-shade"></div>
        <div id="layui-layer-shade99" class="layui-layer-shade" style="position:fixed;inset:0;pointer-events:none"></div>
        <div class="layui-layer" times="3"><h2>临时医嘱</h2><iframe></iframe></div>
        <script>
          const dialog = document.querySelector('.layui-layer');
          const doc = dialog.querySelector('iframe').contentDocument;
          doc.body.innerHTML = `
            <input name="tx_startdate"><input name="tx_reminddate">
            <table><tbody>
              <tr><td><input name="tx_advicename"><div class="select_div"></div></td></tr>
              <tr><td><input name="tx_wayadminister"><div class="select_div"></div></td></tr>
              <tr><td><input name="tx_frequency"><div class="select_div"></div></td></tr>
            </tbody></table>
            <input name="tx_singledosage">
            <input name="tx_drugnumber">
            <select name="execution_department"><option>测试科</option></select>
            <select name="tx_diagnose_select" multiple><option>测试诊断</option></select>
            <textarea name="tx_yznote"></textarea>
            <input name="tx_advicestyle" value="临时" readonly>
            <button type="button">取消</button>`;
          function clearSuggestions() {
            doc.querySelectorAll('.select_div').forEach(container => {
              container.innerHTML = '';
            });
          }
          ['tx_advicename', 'tx_wayadminister', 'tx_frequency'].forEach(name => {
            const field = doc.querySelector('[name="' + name + '"]');
            field.addEventListener('input', () => {
              clearSuggestions();
              const option = doc.createElement('li');
              option.textContent = field.value;
              option.addEventListener('click', () => {
                clearSuggestions();
              });
              field.closest('td').querySelector('.select_div').appendChild(option);
            });
          });
          doc.querySelector('button[type="button"]:last-child').addEventListener('click', () => {
            dialog.remove(); document.querySelector('#layui-layer-shade3').remove();
          });
        </script>
        """
    )

    orders = TemporaryOrdersSection(page)
    dialog = orders.order_dialog.wait_for_open().fill_order(
        {
            "start_time": "2026-08-06 11:00",
            "reminder_date": "2026-08-06",
            "order_name": "测试医嘱",
            "single_dose": "1",
            "quantity": "1",
            "administration_route": "外用",
            "frequency": "每天一剂",
            "execution_department": "测试科",
            "diagnoses": ["测试诊断"],
            "note": "主流程测试",
        }
    )
    dialog.expect_readonly_values({"order_type": "临时"}).cancel()

    assert dialog.is_closed()
    assert page.locator("#layui-layer-shade99:visible").count() == 1
