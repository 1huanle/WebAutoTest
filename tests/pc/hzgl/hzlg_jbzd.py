"""PC 端患者疾病诊断测试用例。"""

from collections.abc import Mapping
from pathlib import Path

import pytest
import yaml

from pages.pc.hzgl import HzglJbzdPage, HzglPage


JBZD_DATA_FILE = Path(__file__).resolve().parents[3] / "data" / "pc" / "hzlg_jbzd.yaml"


def load_hzlg_jbzd_data() -> dict:
    """读取患者疾病诊断测试数据。"""
    with JBZD_DATA_FILE.open(encoding="utf-8") as data_file:
        data = yaml.safe_load(data_file)
    if not isinstance(data, dict):
        raise TypeError("疾病诊断测试数据必须是 YAML 对象")
    if not isinstance(data.get("patient"), Mapping):
        raise TypeError("疾病诊断测试数据缺少 patient 对象")
    if not isinstance(data.get("diagnosis"), Mapping):
        raise TypeError("疾病诊断测试数据缺少 diagnosis 对象")
    return data


@pytest.mark.regression
def test_add_custom_diagnosis(page):
    """为自动化新增患者添加自定义疾病诊断并保存。"""
    data = load_hzlg_jbzd_data()
    patient_name = str(data["patient"]["name"])

    patient_list = HzglPage(page).open()
    assert patient_list.is_loaded()
    patient_list.filters.search_by_name(patient_name).submit()

    patient_card = patient_list.patient_list.by_name(patient_name)
    dialysis_number = patient_card.get_dialysis_number()

    diagnosis_page = HzglJbzdPage(page).open(dialysis_number)
    diagnosis_page.open_diagnosis_section()

    diagnosis_form = diagnosis_page.open_add_form()
    diagnosis_form.fill_form(data["diagnosis"])
    saved_page = diagnosis_form.save()

    assert not page.locator("#jbzdxx").is_visible()
    assert saved_page.diagnosis_list.has_diagnosis(
        str(data["diagnosis"]["custom_diagnosis"])
    )
