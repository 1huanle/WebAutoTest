from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, expect

from .layui_iframe_dialog import LayuiIframeDialog


class TemporaryOrderDialog(LayuiIframeDialog):
    """血液透析 > 临时医嘱触发：封装新增临时医嘱 iframe 弹窗。"""

    TITLE = "临时医嘱"
    MISSING_ROUTE_FREQUENCY_WARNING = "给药途径、执行频率未填写"
    AUTOCOMPLETE_TIMEOUT = 15_000
    FIELDS = {
        "start_time": "tx_startdate",
        "reminder_date": "tx_reminddate",
        "order_name": "tx_advicename",
        "single_dose": "tx_singledosage",
        "quantity": "tx_drugnumber",
        "administration_route": "tx_wayadminister",
        "frequency": "tx_frequency",
        "execution_department": "execution_department",
        "diagnoses": "tx_diagnose_select",
        "note": "tx_yznote",
    }
    SELECT_FIELDS = {
        "execution_department",
        "diagnoses",
    }
    AUTOCOMPLETE_FIELDS = {
        "administration_route",
        "frequency",
    }
    READONLY_FIELDS = {
        "order_type": "tx_advicestyle",
        "order_date": "tx_advicedate",
        "ordering_doctor": "tx_lsyz_kz_doctor",
        "order_description": "tx_advicedescript",
    }

    def _field(self, name: str):
        """返回临时医嘱弹窗 iframe 内指定 name 的控件。"""
        return self._frame().locator(f'[name="{name}"]:visible')

    def _select_autocomplete(
        self, field_name: str, query: str, option: str
    ) -> None:
        """填写真实自动补全字段，并点击指定的可见候选。"""
        field = self._field(field_name)
        field.click()
        field.press("Control+A")
        field.type(query)
        candidate_container = field.locator(
            "xpath=ancestor::td[1]"
        ).locator(".select_div:visible")
        candidate = candidate_container.locator("li").filter(
            has_text=option
        ).last
        expect(candidate).to_be_visible(timeout=self.AUTOCOMPLETE_TIMEOUT)
        candidate.click()
        expect(field).not_to_have_value("")

    def fill_order(self, data: dict[str, object]) -> "TemporaryOrderDialog":
        """填写血液透析 > 临时医嘱触发弹窗中的医嘱内容。"""
        fields = dict(data)
        order_option = str(fields.pop("order_option", fields.get("order_name", "")))
        for key in self.AUTOCOMPLETE_FIELDS - fields.keys():
            field = self._field(self.FIELDS[key])
            field.fill("")
            expect(field).to_have_value("")

        for key, value in fields.items():
            field = self._field(self.FIELDS[key])
            if key == "order_name":
                self._select_autocomplete(
                    self.FIELDS[key], str(value), order_option
                )
            elif key in self.AUTOCOMPLETE_FIELDS:
                self._select_autocomplete(
                    self.FIELDS[key], str(value), str(value)
                )
            elif key in self.SELECT_FIELDS:
                field.select_option(label=value)
            else:
                field.fill(str(value))
        return self

    def expect_readonly_values(
        self, data: dict[str, str]
    ) -> "TemporaryOrderDialog":
        """校验临时医嘱弹窗中的只读业务字段。"""
        for key, value in data.items():
            expect(self._field(self.READONLY_FIELDS[key])).to_have_value(value)
        return self

    def confirm(self) -> "TemporaryOrderDialog":
        """确认新增医嘱，接受空给药途径和频率提示并等待关闭。"""
        needs_warning = any(
            not self._field(self.FIELDS[key]).input_value().strip()
            for key in self.AUTOCOMPLETE_FIELDS
        )
        self._frame().get_by_role("button", name="确认", exact=True).click()
        if needs_warning:
            self._confirm_missing_route_frequency_warning_if_visible()
        self._wait_for_closed()
        return self

    def _confirm_missing_route_frequency_warning_if_visible(self) -> None:
        """确认临时医嘱因给药途径或执行频率为空触发的继续保存提示。"""
        warning = self._frame().locator(".layui-layer:visible").filter(
            has_text=self.MISSING_ROUTE_FREQUENCY_WARNING
        )
        try:
            warning.wait_for(state="visible", timeout=3_000)
        except PlaywrightTimeoutError:
            return

        continue_button = warning.get_by_text("是", exact=True).filter(
            visible=True
        ).last
        expect(continue_button).to_be_visible()
        continue_button.click()

    def cancel(self) -> "TemporaryOrderDialog":
        """取消新增临时医嘱，不保存数据。"""
        self._frame().get_by_text("取消", exact=True).last.click()
        self._wait_for_closed()
        return self
