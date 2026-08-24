"""PC 端新增患者测试用例。"""

from pathlib import Path

import pytest
import yaml

from pages.pc.hzgl import HzglPage


XJHZ_DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "pc" / "xjhz.yaml"


def load_xjhz_data() -> dict:
    """读取新增患者表单数据。"""
    with XJHZ_DATA_FILE.open(encoding="utf-8") as data_file:
        data = yaml.safe_load(data_file)
    if not isinstance(data, dict):
        raise TypeError("新增患者测试数据必须是 YAML 对象")
    return data


@pytest.mark.regression
def test_create_patient(page):
    """打开新增患者页面，填写测试资料并保存患者档案。"""
    patient_list = HzglPage(page).open()
    assert patient_list.is_loaded()

    create_page = patient_list.open_create_patient()
    create_page.fill_form(load_xjhz_data())
    create_page.generate_dialysis_number()
    create_page.save()
