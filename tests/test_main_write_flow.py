from pathlib import Path

import pytest
import yaml

from tests import main_write


class RecordingSection:
    def __init__(self, name, calls, confirmed=True, currently_confirmed=False):
        self.name = name
        self.calls = calls
        self.confirmed = confirmed
        self.currently_confirmed = currently_confirmed
        self.medical_order_push_dialog = self

    def fill_assessment(self, data):
        self.calls.append((f"{self.name}.fill_assessment", data))
        return self

    def fill_prescription(self, data):
        self.calls.append((f"{self.name}.fill_prescription", data))
        return self

    def fill_start_dialysis(self, data):
        self.calls.append((f"{self.name}.fill_start_dialysis", data))
        return self

    def fill_end_dialysis(self, data):
        self.calls.append((f"{self.name}.fill_end_dialysis", data))
        return self

    def fill_summary(self, data):
        self.calls.append((f"{self.name}.fill_summary", data))
        return self

    def add_orders(self, data):
        self.calls.append((f"{self.name}.add_orders", data))
        return self

    def execute_all_unexecuted(self, data):
        self.calls.append((f"{self.name}.execute_all_unexecuted", data))
        return self

    def fill_existing_records(self, data):
        self.calls.append((f"{self.name}.fill_existing_records", data))
        return self

    def fill_existing_records_from(self, data, start_index):
        self.calls.append(
            (f"{self.name}.fill_existing_records_from", data, start_index)
        )
        return self

    def mark_group_correct(self, group):
        self.calls.append((f"{self.name}.mark_group_correct", group))
        return self

    def select_checker(self, checker):
        self.calls.append((f"{self.name}.select_checker", checker))
        return self

    def confirm(self, password=None):
        self.calls.append((f"{self.name}.confirm", password))
        return self

    def is_confirmed(self):
        self.calls.append((f"{self.name}.is_confirmed", None))
        return self.confirmed

    def is_currently_confirmed(self):
        self.calls.append((f"{self.name}.is_currently_confirmed", None))
        return self.currently_confirmed

    def is_closed(self):
        self.calls.append((f"{self.name}.dialog.is_closed", None))
        return True

    def are_all_executed(self):
        self.calls.append((f"{self.name}.are_all_executed", None))
        return True


class RecordingDialysisSheet:
    def __init__(
        self,
        assessment_confirmed=True,
        prescription_confirmed=True,
        assessment_currently_confirmed=False,
        prescription_currently_confirmed=False,
        dialysis_in_progress=False,
        post_dialysis=False,
        double_check_confirmed=True,
        double_check_currently_confirmed=False,
    ):
        self.calls = []
        self.dialysis_in_progress = dialysis_in_progress
        self.post_dialysis = post_dialysis
        self.pre_dialysis_assessment = RecordingSection(
            "assessment",
            self.calls,
            confirmed=assessment_confirmed,
            currently_confirmed=assessment_currently_confirmed,
        )
        self.prescription = RecordingSection(
            "prescription",
            self.calls,
            confirmed=prescription_confirmed,
            currently_confirmed=prescription_currently_confirmed,
        )
        self.start_dialysis_dialog = RecordingSection("start", self.calls)
        self.temporary_orders = RecordingSection("temporary_orders", self.calls)
        self.double_check = RecordingSection(
            "double_check",
            self.calls,
            confirmed=double_check_confirmed,
            currently_confirmed=double_check_currently_confirmed,
        )
        self.monitoring_records = RecordingSection("monitoring_records", self.calls)
        self.end_dialysis_dialog = RecordingSection("end_dialysis", self.calls)
        self.post_dialysis_assessment = RecordingSection("post_assessment", self.calls)
        self.treatment_summary = RecordingSection("treatment_summary", self.calls)

    def select_patient_by_dialysis_number(self, dialysis_number):
        self.calls.append(("sheet.select_patient", dialysis_number))
        return self

    def open_start_dialysis_dialog(self):
        self.calls.append(("sheet.open_start_dialysis_dialog", None))
        return self.start_dialysis_dialog

    def open_end_dialysis_dialog(self):
        self.calls.append(("sheet.open_end_dialysis_dialog", None))
        return self.end_dialysis_dialog

    def is_patient_dialysis_in_progress(self, dialysis_number):
        self.calls.append(("sheet.is_patient_dialysis_in_progress", dialysis_number))
        return self.dialysis_in_progress

    def is_patient_post_dialysis(self, dialysis_number):
        self.calls.append(("sheet.is_patient_post_dialysis", dialysis_number))
        return self.post_dialysis

    def run_self_check(self):
        self.calls.append(("sheet.run_self_check", None))
        return self


def test_main_write_yaml_contains_editable_pre_dialysis_assessment_values():
    """主写入数据只保留透前评估的可编辑字段。"""
    data_path = Path(__file__).parents[1] / "data" / "main_write.yaml"
    data = yaml.safe_load(data_path.read_text(encoding="utf-8"))

    assert data["pre_dialysis_assessment"]["editable"] == {
        "temperature": "36",
        "pulse": "80",
        "respiration": "20",
        "respiration_type": "自主呼吸",
        "systolic_pressure": "110",
        "diastolic_pressure": "80",
        "blood_pressure_site": "上肢",
        "weighing_method": "正常",
        "pre_weight": "70",
        "clothing_weight": "0",
        "expected_dehydration_liters": "0",
        "a_thrombus": "/",
        "v_thrombus": "/",
    }
    assert "expected" not in data["pre_dialysis_assessment"]


def test_main_write_yaml_contains_start_dialysis_values():
    """主流程 YAML 应保存开始透析弹窗值，并省略保持空白的字段。"""
    data_path = Path(__file__).parents[1] / "data" / "main_write.yaml"
    data = yaml.safe_load(data_path.read_text(encoding="utf-8"))

    assert data["start_dialysis"] == {
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
    assert "puncture_site" not in data["start_dialysis"]
    assert "dialyzer_number" not in data["start_dialysis"]


def test_main_write_yaml_contains_temporary_order_values():
    """主流程 YAML 应保存两条新增医嘱和逐条执行人员。"""
    data_path = Path(__file__).parents[1] / "data" / "main_write.yaml"
    data = yaml.safe_load(data_path.read_text(encoding="utf-8"))

    orders = data["temporary_orders"]["orders"]
    assert orders == [
        {
            "fields": {
                "order_name": "陈奕源测试",
                "order_option": "陈奕源测试mg*",
                "single_dose": "10",
                "quantity": "1",
                "administration_route": "皮下注射",
                "frequency": "上午",
            },
            "expected": {
                "order_type": "临时",
                "ordering_doctor": "陈奕源",
                "order_description": "mg* 分散片",
            },
        },
        {
            "fields": {
                "order_name": "陈奕源低分子肝素测试",
                "order_option": "陈奕源低分子肝素测试12μg*1",
                "single_dose": "12",
                "quantity": "1",
            },
            "expected": {
                "order_type": "临时",
                "ordering_doctor": "陈奕源",
                "order_description": "12μg*1 注射剂",
            },
        },
    ]
    assert "administration_route" not in orders[1]["fields"]
    assert "frequency" not in orders[1]["fields"]
    assert data["temporary_orders"]["execution"] == {
        "execution_nurse": "陈奕源",
        "verification_nurse": "陈奕源",
        "note": "",
    }


def test_main_write_yaml_contains_double_check_values():
    """主流程 YAML 应保存双人核对的正确项与核对人。"""
    data_path = Path(__file__).parents[1] / "data" / "main_write.yaml"
    data = yaml.safe_load(data_path.read_text(encoding="utf-8"))

    assert data["double_check"] == {
        "correct_groups": [
            "dialysis_items",
            "dialysis_parameters",
            "vascular_access",
            "pipeline_connection",
        ],
        "checker": "陈奕源",
    }


def test_main_write_yaml_contains_end_dialysis_values():
    """主流程 YAML 应保存结束透析的下机护士和回血流量。"""
    data_path = Path(__file__).parents[1] / "data" / "main_write.yaml"
    data = yaml.safe_load(data_path.read_text(encoding="utf-8"))

    assert data["end_dialysis"] == {
        "off_machine_nurse": "陈奕源",
        "blood_return_flow": "5",
    }


def test_main_write_yaml_contains_monitoring_record_values():
    """主流程 YAML 应保存两条监测记录，时间由页面自动生成。"""
    data_path = Path(__file__).parents[1] / "data" / "main_write.yaml"
    data = yaml.safe_load(data_path.read_text(encoding="utf-8"))

    records = data["monitoring_records"]["records"]
    assert records == [
        {
            "fields": {
                "pulse": "80",
                "respiration": "20",
                "systolic_pressure": "110",
                "diastolic_pressure": "80",
            },
            "symptoms": ["腹痛"],
            "result": "症状好转,继续脱水",
            "monitoring_nurse": "陈奕源",
        },
        {
            "fields": {
                "pulse": "80",
                "respiration": "20",
                "systolic_pressure": "110",
                "diastolic_pressure": "80",
            },
            "symptoms": ["腹痛"],
            "result": "症状好转,继续脱水",
            "monitoring_nurse": "陈奕源",
        },
    ]
    assert all("time" not in record["fields"] for record in records)


def test_main_write_yaml_contains_post_dialysis_assessment_and_summary_values():
    """主流程 YAML 只保存透后评估的非默认填写值和治疗小结文本。"""
    data_path = Path(__file__).parents[1] / "data" / "main_write.yaml"
    data = yaml.safe_load(data_path.read_text(encoding="utf-8"))

    assert data["post_dialysis_assessment"]["editable"] == {
        "temperature": "37.8",
        "pulse": "80",
        "respiration": "20",
        "respiration_type": "自主呼吸",
        "systolic_pressure": "110",
        "diastolic_pressure": "80",
        "blood_pressure_site": "上肢",
        "actual_ultrafiltration_ml": "/",
        "actual_replacement_liters": "/",
        "treatment_hours": "4",
        "treatment_minutes": "0",
        "weighing_method": "正常",
        "post_weight": "60",
        "clothing_weight": "0",
        "actual_treatment_liters": "/",
        "waste_liquid_liters": "/",
        "other": "/",
        "maximum_blood_flow": "/",
        "extracorporeal_blood_leak": "/",
        "blood_leak_dose": "/",
        "injury_degree": "/",
        "vascular_location": "/",
        "cause_and_timing": "/",
    }
    assert data["treatment_summary"] == {
        "education_content": "测试",
        "summary": "测试",
    }


def test_execute_main_write_confirms_assessment_before_filling_prescription(monkeypatch):
    """主流程应依次完成透前评估、透析处方和开始透析。"""
    assert hasattr(main_write, "execute_main_write"), "主流程编排函数尚未实现"
    monkeypatch.setenv("END_DIALYSIS_PASSWORD", "test-password")
    dialysis_sheet = RecordingDialysisSheet()
    test_data = {
        "patient": {"dialysis_number": "21000536543"},
        "pre_dialysis_assessment": {
            "editable": {"temperature": "36"},
        },
        "prescription": {"doctor": "陈奕源"},
        "start_dialysis": {"admission_method": "步行"},
        "temporary_orders": {
            "orders": [{"fields": {"order_name": "测试医嘱"}}],
            "execution": {"execution_nurse": "陈奕源"},
        },
        "double_check": {
            "correct_groups": [
                "dialysis_items",
                "dialysis_parameters",
                "vascular_access",
                "pipeline_connection",
            ],
            "checker": "陈奕源",
        },
        "monitoring_records": {
            "records": [
                {"fields": {"pulse": "80"}},
                {"fields": {"pulse": "80"}},
            ],
        },
        "end_dialysis": {
            "off_machine_nurse": "陈奕源",
            "blood_return_flow": "5",
        },
    }

    main_write.execute_main_write(dialysis_sheet, test_data)

    assert dialysis_sheet.calls == [
        ("sheet.select_patient", "21000536543"),
        ("assessment.is_currently_confirmed", None),
        ("assessment.fill_assessment", {"temperature": "36"}),
        ("assessment.confirm", None),
        ("assessment.is_confirmed", None),
        ("prescription.is_currently_confirmed", None),
        ("prescription.fill_prescription", {"doctor": "陈奕源"}),
        ("prescription.confirm", None),
        ("prescription.is_confirmed", None),
        ("prescription.dialog.is_closed", None),
        ("sheet.is_patient_post_dialysis", "21000536543"),
        ("sheet.is_patient_dialysis_in_progress", "21000536543"),
        ("sheet.open_start_dialysis_dialog", None),
        ("start.fill_start_dialysis", {"admission_method": "步行"}),
        ("start.confirm", None),
        ("start.dialog.is_closed", None),
        (
            "monitoring_records.fill_existing_records_from",
            [{"fields": {"pulse": "80"}}],
            0,
        ),
        (
            "temporary_orders.add_orders",
            [{"fields": {"order_name": "测试医嘱"}}],
        ),
        (
            "temporary_orders.execute_all_unexecuted",
            {"execution_nurse": "陈奕源"},
        ),
        ("double_check.is_currently_confirmed", None),
        ("double_check.mark_group_correct", "dialysis_items"),
        ("double_check.mark_group_correct", "dialysis_parameters"),
        ("double_check.mark_group_correct", "vascular_access"),
        ("double_check.mark_group_correct", "pipeline_connection"),
        ("double_check.select_checker", "陈奕源"),
        ("double_check.confirm", None),
        ("double_check.is_confirmed", None),
        ("sheet.open_end_dialysis_dialog", None),
        (
            "end_dialysis.fill_end_dialysis",
            {"off_machine_nurse": "陈奕源", "blood_return_flow": "5"},
        ),
        ("end_dialysis.confirm", "test-password"),
        ("end_dialysis.dialog.is_closed", None),
        (
            "monitoring_records.fill_existing_records_from",
            [{"fields": {"pulse": "80"}}],
            1,
        ),
        ("monitoring_records.confirm", None),
        ("monitoring_records.is_confirmed", None),
    ]


def test_execute_main_write_skips_completed_steps_when_rerun(monkeypatch):
    """主流程重跑时跳过已确认和已开始步骤，只处理临时医嘱。"""
    monkeypatch.setenv("END_DIALYSIS_PASSWORD", "test-password")
    dialysis_sheet = RecordingDialysisSheet(
        assessment_currently_confirmed=True,
        prescription_currently_confirmed=True,
        dialysis_in_progress=True,
        double_check_currently_confirmed=True,
    )
    test_data = {
        "patient": {"dialysis_number": "21000536543"},
        "pre_dialysis_assessment": {
            "editable": {"temperature": "36"},
        },
        "prescription": {"doctor": "陈奕源"},
        "start_dialysis": {"admission_method": "步行"},
        "temporary_orders": {
            "orders": [{"fields": {"order_name": "测试医嘱"}}],
            "execution": {"execution_nurse": "陈奕源"},
        },
        "double_check": {
            "correct_groups": [
                "dialysis_items",
                "dialysis_parameters",
                "vascular_access",
                "pipeline_connection",
            ],
            "checker": "陈奕源",
        },
        "end_dialysis": {
            "off_machine_nurse": "陈奕源",
            "blood_return_flow": "5",
        },
    }

    main_write.execute_main_write(dialysis_sheet, test_data)

    assert dialysis_sheet.calls == [
        ("sheet.select_patient", "21000536543"),
        ("assessment.is_currently_confirmed", None),
        ("prescription.is_currently_confirmed", None),
        ("sheet.is_patient_post_dialysis", "21000536543"),
        ("sheet.is_patient_dialysis_in_progress", "21000536543"),
        (
            "temporary_orders.add_orders",
            [{"fields": {"order_name": "测试医嘱"}}],
        ),
        (
            "temporary_orders.execute_all_unexecuted",
            {"execution_nurse": "陈奕源"},
        ),
        ("double_check.is_currently_confirmed", None),
        ("sheet.open_end_dialysis_dialog", None),
        (
            "end_dialysis.fill_end_dialysis",
            {"off_machine_nurse": "陈奕源", "blood_return_flow": "5"},
        ),
        ("end_dialysis.confirm", "test-password"),
        ("end_dialysis.dialog.is_closed", None),
    ]


def test_execute_main_write_skips_start_and_end_for_post_dialysis_patient(monkeypatch):
    """患者状态为透析后时，不得重复开始或结束透析。"""
    monkeypatch.setenv("END_DIALYSIS_PASSWORD", "test-password")
    dialysis_sheet = RecordingDialysisSheet(
        assessment_currently_confirmed=True,
        prescription_currently_confirmed=True,
        dialysis_in_progress=False,
        post_dialysis=True,
        double_check_currently_confirmed=True,
    )
    test_data = {
        "patient": {"dialysis_number": "21000536543"},
        "pre_dialysis_assessment": {"editable": {"temperature": "36"}},
        "prescription": {"doctor": "陈奕源"},
        "start_dialysis": {"admission_method": "步行"},
        "temporary_orders": {"orders": [], "execution": {}},
        "double_check": {"correct_groups": [], "checker": "陈奕源"},
        "end_dialysis": {
            "off_machine_nurse": "陈奕源",
            "blood_return_flow": "5",
        },
    }

    main_write.execute_main_write(dialysis_sheet, test_data)

    assert ("sheet.is_patient_post_dialysis", "21000536543") in dialysis_sheet.calls
    assert not any(
        name == "sheet.open_start_dialysis_dialog" for name, _ in dialysis_sheet.calls
    )
    assert not any(
        name == "sheet.open_end_dialysis_dialog" for name, _ in dialysis_sheet.calls
    )


def test_execute_main_write_fills_and_confirms_post_dialysis_sections(monkeypatch):
    """透析后患者仍应填写并确认透后评估和治疗小结。"""
    monkeypatch.setenv("END_DIALYSIS_PASSWORD", "test-password")
    dialysis_sheet = RecordingDialysisSheet(
        assessment_currently_confirmed=True,
        prescription_currently_confirmed=True,
        double_check_currently_confirmed=True,
        post_dialysis=True,
    )
    post_assessment_data = {"temperature": "37.8", "treatment_hours": "4"}
    treatment_summary_data = {"education_content": "测试", "summary": "测试"}
    test_data = {
        "patient": {"dialysis_number": "21000536543"},
        "pre_dialysis_assessment": {"editable": {}},
        "prescription": {},
        "start_dialysis": {},
        "temporary_orders": {"orders": [], "execution": {}},
        "double_check": {"correct_groups": [], "checker": "陈奕源"},
        "end_dialysis": {},
        "post_dialysis_assessment": {"editable": post_assessment_data},
        "treatment_summary": treatment_summary_data,
    }

    main_write.execute_main_write(dialysis_sheet, test_data)

    assert ("post_assessment.fill_assessment", post_assessment_data) in dialysis_sheet.calls
    assert ("post_assessment.confirm", None) in dialysis_sheet.calls
    assert ("post_assessment.is_confirmed", None) in dialysis_sheet.calls
    assert ("treatment_summary.fill_summary", treatment_summary_data) in dialysis_sheet.calls
    assert ("treatment_summary.confirm", None) in dialysis_sheet.calls
    assert ("treatment_summary.is_confirmed", None) in dialysis_sheet.calls


def test_execute_main_write_runs_self_check_after_all_required_sections(monkeypatch):
    """主流程仅在全部必需分区完成后，才点击页面顶部的自查按钮。"""
    monkeypatch.setenv("END_DIALYSIS_PASSWORD", "test-password")
    dialysis_sheet = RecordingDialysisSheet(
        assessment_currently_confirmed=True,
        prescription_currently_confirmed=True,
        double_check_currently_confirmed=True,
        post_dialysis=True,
    )
    test_data = {
        "patient": {"dialysis_number": "21000536543"},
        "pre_dialysis_assessment": {"editable": {}},
        "prescription": {},
        "start_dialysis": {},
        "temporary_orders": {"orders": [], "execution": {}},
        "double_check": {"correct_groups": [], "checker": "陈奕源"},
        "monitoring_records": {"records": [{"fields": {}}]},
        "end_dialysis": {},
        "post_dialysis_assessment": {"editable": {}},
        "treatment_summary": {"education_content": "测试", "summary": "测试"},
    }

    main_write.execute_main_write(dialysis_sheet, test_data)

    assert ("temporary_orders.are_all_executed", None) in dialysis_sheet.calls
    assert ("monitoring_records.is_confirmed", None) in dialysis_sheet.calls
    assert dialysis_sheet.calls[-1] == ("sheet.run_self_check", None)


def test_execute_main_write_stops_when_double_check_confirmation_fails():
    """双人核对提交后未确认时，主流程必须抛出明确错误。"""
    dialysis_sheet = RecordingDialysisSheet(double_check_confirmed=False)
    test_data = {
        "patient": {"dialysis_number": "21000536543"},
        "pre_dialysis_assessment": {"editable": {"temperature": "36"}},
        "prescription": {"doctor": "陈奕源"},
        "start_dialysis": {"admission_method": "步行"},
        "temporary_orders": {
            "orders": [{"fields": {"order_name": "测试医嘱"}}],
            "execution": {"execution_nurse": "陈奕源"},
        },
        "double_check": {
            "correct_groups": ["dialysis_items"],
            "checker": "陈奕源",
        },
    }

    with pytest.raises(AssertionError, match="双人核对确认失败"):
        main_write.execute_main_write(dialysis_sheet, test_data)


def test_execute_main_write_stops_before_prescription_when_assessment_fails():
    """透前评估确认失败时应停止主流程，不得操作透析处方。"""
    dialysis_sheet = RecordingDialysisSheet(assessment_confirmed=False)
    test_data = {
        "patient": {"dialysis_number": "21000536543"},
        "pre_dialysis_assessment": {
            "editable": {"temperature": "36"},
        },
        "prescription": {"doctor": "陈奕源"},
        "start_dialysis": {"admission_method": "步行"},
        "temporary_orders": {
            "orders": [{"fields": {"order_name": "测试医嘱"}}],
            "execution": {"execution_nurse": "陈奕源"},
        },
    }

    with pytest.raises(AssertionError, match="透前评估确认失败"):
        main_write.execute_main_write(dialysis_sheet, test_data)

    assert not any(
        name.startswith("prescription.") for name, _ in dialysis_sheet.calls
    )
    assert not any(name.startswith("start.") for name, _ in dialysis_sheet.calls)
    assert not any(
        name == "sheet.open_start_dialysis_dialog"
        for name, _ in dialysis_sheet.calls
    )
    assert not any(
        name.startswith("temporary_orders.") for name, _ in dialysis_sheet.calls
    )


def test_execute_main_write_stops_before_start_when_prescription_fails():
    """透析处方确认失败时不得打开开始透析弹窗。"""
    dialysis_sheet = RecordingDialysisSheet(prescription_confirmed=False)
    test_data = {
        "patient": {"dialysis_number": "21000536543"},
        "pre_dialysis_assessment": {
            "editable": {"temperature": "36"},
        },
        "prescription": {"doctor": "陈奕源"},
        "start_dialysis": {"admission_method": "步行"},
        "temporary_orders": {
            "orders": [{"fields": {"order_name": "测试医嘱"}}],
            "execution": {"execution_nurse": "陈奕源"},
        },
    }

    with pytest.raises(AssertionError, match="透析处方确认失败"):
        main_write.execute_main_write(dialysis_sheet, test_data)

    assert not any(name.startswith("start.") for name, _ in dialysis_sheet.calls)
    assert not any(
        name == "sheet.open_start_dialysis_dialog"
        for name, _ in dialysis_sheet.calls
    )
    assert not any(
        name.startswith("temporary_orders.") for name, _ in dialysis_sheet.calls
    )
