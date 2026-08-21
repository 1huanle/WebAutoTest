import pytest


@pytest.mark.no_auth_state
def test_monitoring_records_list_actions_and_confirmation(page):
    """血液透析 > 监测记录：读取、选择并操作分区内记录。"""
    page.set_content(
        """
        <table><tbody>
          <tr><th>监测记录</th><td><span class="status">未确认</span></td></tr>
          <tr><td colspan="4">
            <button>添加监测</button><button>删除</button><button>设置字段</button>
            <button>血压手表</button><button>确认</button>
          </td></tr>
          <tr><th>选择</th><th>时间</th><th>脉搏</th><th>血压</th></tr>
          <tr><td><input type="checkbox"></td><td>11:30</td><td>80</td><td>110/80</td></tr>
        </tbody></table>
        <script>
          document.querySelectorAll('button').forEach(button => button.addEventListener('click', () => {
            document.body.dataset.action = button.textContent;
            if (button.textContent === '确认') document.querySelector('.status').textContent = '已确认';
          }));
        </script>
        """
    )

    from pages.hemodialysis.monitoring_records_section import MonitoringRecordsSection

    records = MonitoringRecordsSection(page)
    assert records.get_record_headers() == ["选择", "时间", "脉搏", "血压"]
    assert records.get_record_rows() == [["11:30", "80", "110/80"]]
    records.select_record("11:30")
    assert page.get_by_role("checkbox").is_checked()
    records.open_add_record().open_field_settings().open_blood_pressure_watch()
    records.delete_selected().confirm()
    assert records.is_confirmed()


@pytest.mark.no_auth_state
def test_fill_and_cancel_monitoring_record_dialog(page):
    """血液透析 > 监测记录触发：填写真实字段并取消，不保存数据。"""
    page.set_content(
        """
        <div id="layui-layer-shade4" class="layui-layer-shade"></div>
        <div class="layui-layer" times="4"><h2>监测记录</h2><iframe></iframe></div>
        <script>
          const dialog = document.querySelector('.layui-layer');
          const doc = dialog.querySelector('iframe').contentDocument;
          const names = [
            'tx_jcjl_time','tx_jcjl_mb','tx_jcjl_hx','tx_jcjl_xy','tx_jcjl_xy1',
            'tx_jcjl_xll','tx_jcjl_my','tx_jcjl_dmy','tx_jcjl_kmy','tx_jcjl_cll',
            'tx_jcjl_clliang','tx_jcjl_nnd','tx_jcjl_ddd','tx_jcjl_txywd','tx_ktv',
            'tx_entend_xw','tx_jcjl_xrl','tx_jcjl_xrl_L','tx_entend_xrlbhl',
            'tx_jcjl_zxns','tx_jcjl_tw','tx_spo2','tx_entend_cll','tx_entend_fjl',
            'tx_entend_kmy','tx_entend_rky','tx_entend_lgy','tx_entend_gsyl',
            'tx_entend_bs','tx_entend_xl'
          ];
          names.forEach(name => doc.body.insertAdjacentHTML('beforeend', `<input name="${name}">`));
          ['tx_jcjl_zz_show','tx_jcjl_cl_show','tx_jcjl_jg_show'].forEach(name =>
            doc.body.insertAdjacentHTML('beforeend', `<textarea name="${name}"></textarea>`));
          doc.body.insertAdjacentHTML('beforeend', `
            <input name="tx_jcjl_zz" readonly>
            <input name="tx_jcjl_jg" readonly>
            <input type="hidden" name="tx_jcjl_hsid">
            <input name="tx_jcjl_ymd" value="2026-08-06" readonly>
            <input name="tx_jcjl_zhl" value="200" readonly>
            <input name="tx_jcjl_zhliang" value="20" readonly>
            <input name="tx_jcjl_hsname" value="陈奕源" readonly>
            <button type="button">取消</button>`);
          const pickerOptions = {
            tx_jcjl_zz: ['腹痛'],
            tx_jcjl_jg: ['症状好转,继续脱水'],
            tx_jcjl_hsname: ['陈奕源'],
          };
          Object.entries(pickerOptions).forEach(([name, values]) => {
            doc.querySelector(`[name="${name}"]`).addEventListener('click', () => {
              const picker = doc.createElement('div');
              picker.id = 'picker';
              values.forEach(value => {
                const option = doc.createElement('button');
                option.textContent = value;
                option.addEventListener('click', () => {
                  if (name === 'tx_jcjl_hsname') {
                    doc.querySelector('[name="tx_jcjl_hsname"]').value = value;
                    picker.remove();
                    return;
                  }
                  picker.dataset.value = value;
                });
                picker.append(option);
              });
              if (name === 'tx_jcjl_hsname') {
                doc.body.append(picker);
                return;
              }
              const save = doc.createElement('button');
              save.textContent = '保存';
              save.addEventListener('click', () => {
                doc.querySelector(`[name="${name}"]`).value = picker.dataset.value;
                if (name === 'tx_jcjl_jg') doc.querySelector('[name="tx_jcjl_jg_show"]').value = picker.dataset.value;
                if (name === 'tx_jcjl_hsname') doc.querySelector('[name="tx_jcjl_hsname"]').value = picker.dataset.value;
                picker.remove();
              });
              picker.append(save);
              doc.body.append(picker);
              // 模拟真实页面的隐藏保存元素，自动化必须只点击当前可见的保存按钮。
              doc.body.insertAdjacentHTML('beforeend', '<span class="back_save" style="display:none">保存</span>');
            });
          });
          doc.querySelector('button').addEventListener('click', () => {
            dialog.remove(); document.querySelector('#layui-layer-shade4').remove();
          });
        </script>
        """
    )

    from pages.hemodialysis.monitoring_records_section import MonitoringRecordsSection

    dialog = MonitoringRecordsSection(page).record_dialog.wait_for_open()
    dialog.fill_record(
        {
            "time": "11:30", "pulse": "80", "respiration": "20",
            "systolic_pressure": "110", "diastolic_pressure": "80",
            "blood_flow": "225", "venous_pressure": "/", "arterial_pressure": "/",
            "transmembrane_pressure": "/", "ultrafiltration_rate": "0",
            "ultrafiltration_volume": "/", "sodium_concentration": "138",
            "conductivity": "14", "dialysate_temperature": "36.5", "ktv": "/",
            "blood_temperature": "36.5", "blood_volume_ml": "/",
            "blood_volume_liters": "0", "blood_volume_change": "/",
            "online_urea": "/", "symptoms": "无", "treatment": "无", "result": "稳定",
            "temperature": "36.5", "spo2": "99", "treatment_flow": "/",
            "plasma_separation_flow": "/", "transmembrane_pressure_2": "/",
            "inlet_pressure": "/", "filtration_pressure": "/",
            "heparin_remaining": "/", "pump_speed": "/", "heart_rate": "80",
        }
    )
    dialog.expect_readonly_values(
        {"date": "2026-08-06", "replacement_rate": "200",
         "replacement_volume": "20", "monitoring_nurse": "陈奕源"}
    )
    # 缩短错误定位等待时间：该用例验证护士选择器不能点击隐藏 ID 字段。
    page.set_default_timeout(500)
    dialog.select_symptoms(["腹痛"]).select_result(
        "症状好转,继续脱水"
    ).select_monitoring_nurse("陈奕源").cancel()

    assert dialog.is_closed()


@pytest.mark.no_auth_state
def test_fill_existing_monitoring_records_in_page_order(page):
    """监测记录按页面顺序填写，保留自动生成的时间。"""
    page.set_content(
        """
        <table><tbody>
          <tr><th>监测记录</th><td><span class="status">未确认</span></td></tr>
          <tr><td><button>确认</button></td></tr>
          <tr><td colspan="2"><table><tbody>
            <tr><th>时间</th><th>脉搏</th></tr>
            <tr class="record"><td>16:50</td><td></td></tr>
            <tr class="record"><td>16:56</td><td></td></tr>
          </tbody></table></td></tr>
        </tbody></table>
        <div id="layui-layer-shade4" style="display:none"></div>
        <div class="layui-layer" times="4" style="display:none"><h2>监测记录</h2><iframe></iframe></div>
        <script>
          const layer = document.querySelector('.layui-layer');
          const shade = document.querySelector('#layui-layer-shade4');
          const doc = layer.querySelector('iframe').contentDocument;
          doc.body.innerHTML = `
            <input name="tx_jcjl_mb"><input name="tx_jcjl_hx">
            <input name="tx_jcjl_xy"><input name="tx_jcjl_xy1">
            <textarea name="tx_jcjl_zz_show"></textarea>
            <input name="tx_jcjl_zz" readonly>
            <textarea name="tx_jcjl_jg_show"></textarea>
            <input name="tx_jcjl_jg" readonly>
            <input name="tx_jcjl_hsname" readonly>
            <input type="hidden" name="tx_jcjl_hsid">
            <button type="button" id="confirm-record">确认</button>`;
          const values = {
            tx_jcjl_zz: '腹痛',
            tx_jcjl_jg: '症状好转,继续脱水',
            tx_jcjl_hsname: '陈奕源',
          };
          Object.entries(values).forEach(([name, value]) => {
            doc.querySelector(`[name="${name}"]`).addEventListener('click', () => {
              const picker = doc.createElement('div');
              picker.id = 'picker';
              picker.innerHTML = name === 'tx_jcjl_hsname'
                ? `<button>${value}</button>`
                : `<button>${value}</button><button>保存</button>`;
              picker.querySelector('button').addEventListener('click', () => {
                if (name === 'tx_jcjl_hsname') {
                  doc.querySelector('[name="tx_jcjl_hsname"]').value = value;
                  picker.remove();
                  return;
                }
                picker.dataset.value = value;
              });
              if (name !== 'tx_jcjl_hsname') picker.querySelectorAll('button')[1].addEventListener('click', () => {
                doc.querySelector(`[name="${name}"]`).value = picker.dataset.value;
                if (name === 'tx_jcjl_zz') doc.querySelector('[name="tx_jcjl_zz_show"]').value = picker.dataset.value;
                if (name === 'tx_jcjl_jg') doc.querySelector('[name="tx_jcjl_jg_show"]').value = picker.dataset.value;
                if (name === 'tx_jcjl_hsname') doc.querySelector('[name="tx_jcjl_hsname"]').value = picker.dataset.value;
                picker.remove();
              });
              doc.body.append(picker);
              // 模拟真实页面的隐藏保存元素，自动化必须只点击当前可见的保存按钮。
              doc.body.insertAdjacentHTML('beforeend', '<span class="back_save" style="display:none">保存</span>');
            });
          });
          window.savedRecords = [];
          doc.querySelector('#confirm-record').addEventListener('click', () => {
            window.savedRecords.push({
              pulse: doc.querySelector('[name="tx_jcjl_mb"]').value,
              respiration: doc.querySelector('[name="tx_jcjl_hx"]').value,
              systolicPressure: doc.querySelector('[name="tx_jcjl_xy"]').value,
              diastolicPressure: doc.querySelector('[name="tx_jcjl_xy1"]').value,
              symptoms: doc.querySelector('[name="tx_jcjl_zz_show"]').value,
              result: doc.querySelector('[name="tx_jcjl_jg_show"]').value,
              nurse: doc.querySelector('[name="tx_jcjl_hsname"]').value,
            });
            layer.style.display = 'none'; shade.style.display = 'none';
          });
          document.querySelectorAll('.record').forEach(row => row.addEventListener('dblclick', () => {
            layer.style.display = 'block'; shade.style.display = 'block';
          }));
          document.querySelector('table button').addEventListener('click', () => {
            document.querySelector('.status').textContent = '已确认';
          });
        </script>
        """
    )

    from pages.hemodialysis.monitoring_records_section import MonitoringRecordsSection

    record = {
        "fields": {
            "pulse": "80",
            "respiration": "20",
            "systolic_pressure": "110",
            "diastolic_pressure": "80",
        },
        "symptoms": ["腹痛"],
        "result": "症状好转,继续脱水",
        "monitoring_nurse": "陈奕源",
    }
    records = MonitoringRecordsSection(page)
    records.fill_existing_records([record, record]).confirm()

    assert page.evaluate("window.savedRecords") == [
        {
            "pulse": "80",
            "respiration": "20",
            "systolicPressure": "110",
            "diastolicPressure": "80",
            "symptoms": "腹痛",
            "result": "症状好转,继续脱水",
            "nurse": "陈奕源",
        }
    ] * 2
    assert records.is_confirmed()
