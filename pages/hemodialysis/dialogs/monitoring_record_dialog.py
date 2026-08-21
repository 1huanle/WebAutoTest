from playwright.sync_api import expect

from .layui_iframe_dialog import LayuiIframeDialog


class MonitoringRecordDialog(LayuiIframeDialog):
    """血液透析 > 监测记录触发：封装新增监测记录 iframe 弹窗。"""

    TITLE = "监测记录"
    # 真实页面可见的监测记录可编辑字段。
    FIELDS = {
        "time": "tx_jcjl_time",
        "pulse": "tx_jcjl_mb",
        "respiration": "tx_jcjl_hx",
        "systolic_pressure": "tx_jcjl_xy",
        "diastolic_pressure": "tx_jcjl_xy1",
        "blood_flow": "tx_jcjl_xll",
        "venous_pressure": "tx_jcjl_my",
        "arterial_pressure": "tx_jcjl_dmy",
        "transmembrane_pressure": "tx_jcjl_kmy",
        "ultrafiltration_rate": "tx_jcjl_cll",
        "ultrafiltration_volume": "tx_jcjl_clliang",
        "sodium_concentration": "tx_jcjl_nnd",
        "conductivity": "tx_jcjl_ddd",
        "dialysate_temperature": "tx_jcjl_txywd",
        "ktv": "tx_ktv",
        "blood_temperature": "tx_entend_xw",
        "blood_volume_ml": "tx_jcjl_xrl",
        "blood_volume_liters": "tx_jcjl_xrl_L",
        "blood_volume_change": "tx_entend_xrlbhl",
        "online_urea": "tx_jcjl_zxns",
        "symptoms": "tx_jcjl_zz_show",
        "treatment": "tx_jcjl_cl_show",
        "result": "tx_jcjl_jg_show",
        "temperature": "tx_jcjl_tw",
        "spo2": "tx_spo2",
        "treatment_flow": "tx_entend_cll",
        "plasma_separation_flow": "tx_entend_fjl",
        "transmembrane_pressure_2": "tx_entend_kmy",
        "inlet_pressure": "tx_entend_rky",
        "filtration_pressure": "tx_entend_lgy",
        "heparin_remaining": "tx_entend_gsyl",
        "pump_speed": "tx_entend_bs",
        "heart_rate": "tx_entend_xl",
    }
    READONLY_FIELDS = {
        "date": "tx_jcjl_ymd",
        "replacement_rate": "tx_jcjl_zhl",
        "replacement_volume": "tx_jcjl_zhliang",
        "monitoring_nurse": "tx_jcjl_hsname",
    }
    PICKER_FIELDS = {
        "symptoms": "tx_jcjl_zz",
        "result": "tx_jcjl_jg",
        # 页面中的 tx_jcjl_hsid 是隐藏 ID 字段；人员选择器由可见姓名框触发。
        "monitoring_nurse": "tx_jcjl_hsname",
    }

    def _field(self, name: str):
        """返回监测记录 iframe 内指定 name 的可见控件。"""
        return self._frame().locator(f'[name="{name}"]:visible')

    def fill_record(self, data: dict[str, str]) -> "MonitoringRecordDialog":
        """填写血液透析 > 监测记录触发弹窗的可编辑内容。"""
        for key, value in data.items():
            self._field(self.FIELDS[key]).fill(value)
        return self

    def expect_readonly_values(
        self, data: dict[str, str]
    ) -> "MonitoringRecordDialog":
        """校验监测日期、置换参数和监测护士等只读值。"""
        for key, value in data.items():
            expect(self._field(self.READONLY_FIELDS[key])).to_have_value(value)
        return self

    def _select_picker_values(
        self, field_name: str, values: list[str], save_selection: bool = True
    ) -> None:
        """在监测记录的二级选择页中选择内容，按页面行为决定是否保存。"""
        self._field(field_name).click()
        for value in values:
            self._frame().get_by_text(value, exact=True).last.click()
        if not save_selection:
            return
        # 页面会同时保留隐藏的“保存”元素，必须限定点击当前可见的选择器按钮。
        self._frame().get_by_text("保存", exact=True).filter(visible=True).last.click()

    def select_symptoms(self, symptoms: list[str]) -> "MonitoringRecordDialog":
        """选择监测记录的症状。"""
        self._select_picker_values(self.PICKER_FIELDS["symptoms"], symptoms)
        return self

    def select_result(self, result: str) -> "MonitoringRecordDialog":
        """选择监测记录的结果。"""
        self._select_picker_values(self.PICKER_FIELDS["result"], [result])
        return self

    def select_monitoring_nurse(self, nurse: str) -> "MonitoringRecordDialog":
        """选择监测记录的监测护士。"""
        # 监测护士选择后会自动返回主弹窗，不存在额外的“保存”按钮。
        self._select_picker_values(
            self.PICKER_FIELDS["monitoring_nurse"], [nurse], save_selection=False
        )
        return self

    def confirm(self) -> "MonitoringRecordDialog":
        """确认新增监测记录，并等待该弹窗及所属遮罩关闭。"""
        self._frame().get_by_text("确认", exact=True).last.click()
        self._wait_for_closed()
        return self

    def cancel(self) -> "MonitoringRecordDialog":
        """取消新增监测记录，不保存数据。"""
        self._frame().get_by_text("取消", exact=True).last.click()
        self._wait_for_closed()
        return self
