"""PC 端患者详情页新增医嘱测试用例。"""

from collections.abc import Mapping
from pathlib import Path

import pytest
import yaml
from playwright.sync_api import expect

from pages.pc.hzgl import HzglYzPage


XZYZ_DATA_FILE = (
    Path(__file__).resolve().parents[3] / "data" / "pc" / "hzgl_xzyz.yaml"
)


def load_hzgl_xzyz_data() -> dict:
    """读取新增医嘱测试数据。"""
    with XZYZ_DATA_FILE.open(encoding="utf-8") as data_file:
        data = yaml.safe_load(data_file)

    if not isinstance(data, dict):
        raise TypeError("新增医嘱测试数据必须是 YAML 对象")
    if not isinstance(data.get("patient"), Mapping):
        raise TypeError("新增医嘱测试数据缺少 patient 对象")
    if not isinstance(data.get("order"), Mapping):
        raise TypeError("新增医嘱测试数据缺少 order 对象")
    if not isinstance(data.get("push"), Mapping):
        raise TypeError("新增医嘱测试数据缺少 push 对象")
    return data


@pytest.mark.regression
def test_add_medical_order(page):
    """校验当前患者后新增一条医嘱并保存。"""
    data = load_hzgl_xzyz_data()
    patient_data = data["patient"]
    order_data = data["order"]
    push_data = data["push"]
    patient_name = str(patient_data["name"])
    dialysis_number = str(patient_data["dialysis_number"])
    order_name = str(order_data["order_name"])

    yz_page = HzglYzPage(page).open(dialysis_number)
    expect(page.get_by_text(f"姓名：{patient_name}", exact=True)).to_be_visible()

    yz_page.open_yz_section()
    order_form = yz_page.open_add_order()
    saved_page = order_form.fill_form(order_data).save()

    expect(page.locator('iframe[id^="layui-layer-iframe"]:visible')).to_have_count(0)
    assert saved_page.order_list.has_order(order_name)

    push_form = (
        saved_page.order_list
        .select_order(order_name)
        .open_medication_push()
    )
    pushed_page = (
        push_form
        .select_push_mode(str(push_data["mode"]))
        .select_frequency(str(push_data["frequency"]))
        .confirm()
    )
    expect(page.locator('iframe[id^="layui-layer-iframe"]:visible')).to_have_count(0)
    assert pushed_page.order_list.has_order(order_name)
