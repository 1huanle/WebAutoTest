# 导入 Path，用于基于当前文件位置拼出测试数据文件路径。
from pathlib import Path
# 导入 os，用于从环境变量读取结束透析的登录密码。
import os

# 导入 pytest，用于声明该用例的测试分类标记。
import pytest
# 导入 YAML 解析器，用于读取主流程的填写数据。
import yaml

# 导入透析单页面对象，封装页面上的业务操作。
from pages.pc.hemodialysis.dialysis_sheet_page import DialysisSheetPage


# 定义主写入流程使用的 YAML 数据文件绝对路径。
MAIN_WRITE_DATA_FILE = (
    # 从本文件所在目录向上三层定位项目根目录，再拼接 PC 端数据文件。
    Path(__file__).resolve().parents[2] / "data" / "pc" / "main_write.yaml"
)
# 123

# 定义可被测试和其他脚本复用的主写入业务流程。
def execute_main_write(dialysis_sheet, test_data: dict) -> None:
    # 说明该函数会根据页面当前状态跳过已完成的业务步骤。
    """按当前业务状态执行可重复运行的血液透析主流程。"""
    # 从 YAML 数据中读取需要操作的患者透析号。
    dialysis_number = test_data["patient"]["dialysis_number"]
    # 在透析单页面中按透析号选择目标患者。
    dialysis_sheet.select_patient_by_dialysis_number(dialysis_number)

    # 获取“透前评估”分区的页面对象。
    assessment = dialysis_sheet.pre_dialysis_assessment
    # 读取透前评估的可编辑字段数据。
    assessment_data = test_data["pre_dialysis_assessment"]
    # 仅当透前评估尚未确认时，才执行填写和确认，支持重复运行。
    if not assessment.is_currently_confirmed():
        # 填写透前评估中白色背景的可编辑字段。
        assessment.fill_assessment(assessment_data["editable"])
        # 点击透前评估分区的“确认”按钮。
        assessment.confirm()
        # 确认后再次检查状态，防止失败时继续后续高风险流程。
        if not assessment.is_confirmed():
            # 明确中断流程并说明失败原因。
            raise AssertionError("透前评估确认失败，主流程已停止")

    # 获取“透析处方”分区的页面对象。
    prescription = dialysis_sheet.prescription
    # 仅当透析处方尚未确认时，才填写处方并提交。
    if not prescription.is_currently_confirmed():
        # 使用 YAML 中的处方数据填写可编辑字段。
        prescription.fill_prescription(test_data["prescription"])
        # 点击处方分区的“确认”按钮。
        prescription.confirm()
        # 检查处方确认结果，失败时停止主流程。
        if not prescription.is_confirmed():
            # 明确中断流程并说明失败原因。
            raise AssertionError("透析处方确认失败，主流程已停止")
        # 确认医嘱推送弹窗已经关闭，避免遮罩拦截后续操作。
        prescription.medical_order_push_dialog.is_closed()

    # 读取患者是否已处于透析后状态，避免对已结束治疗重复操作。
    is_post_dialysis = dialysis_sheet.is_patient_post_dialysis(dialysis_number)
    # 仅当该患者尚未开始透析且尚未透析后时，才打开开始透析弹窗。
    if (
        not is_post_dialysis
        and not dialysis_sheet.is_patient_dialysis_in_progress(dialysis_number)
    ):
        # 打开“开始透析”弹窗并取得其页面对象。
        start_dialog = dialysis_sheet.open_start_dialysis_dialog()
        # 填写开始透析弹窗中的可编辑字段。
        start_dialog.fill_start_dialysis(test_data["start_dialysis"])
        # 点击弹窗中的“确认”按钮提交开始透析操作。
        start_dialog.confirm()
        # 等待弹窗关闭，确认提交操作已经完成。
        start_dialog.is_closed()

    # 开始透析会自动生成第一条监测记录，先填写该记录。
    monitoring_records_data = test_data.get("monitoring_records")
    monitoring_records = None
    if monitoring_records_data and not is_post_dialysis:
        monitoring_records = dialysis_sheet.monitoring_records
        monitoring_records.fill_existing_records_from(
            [monitoring_records_data["records"][0]], start_index=0
        )

    # 获取“临时医嘱”分区的页面对象。
    temporary_orders = dialysis_sheet.temporary_orders
    # 读取 YAML 中需要新增和执行的临时医嘱数据。
    temporary_orders_data = test_data["temporary_orders"]
    # 新增数据中尚不存在的临时医嘱，已有同名医嘱会被跳过。
    temporary_orders.add_orders(temporary_orders_data["orders"])
    # 逐条执行当前页面上所有尚未执行的临时医嘱。
    temporary_orders.execute_all_unexecuted(
        # 传入执行人、核对人和备注等执行数据。
        temporary_orders_data["execution"]
    )

    # 获取“双人核对”分区的页面对象。
    double_check = dialysis_sheet.double_check
    # 仅当双人核对尚未确认时，才勾选、选择核对人并提交，支持重复运行。
    if not double_check.is_currently_confirmed():
        # 依次将 YAML 配置的每个核查组勾选为“正确”。
        for group in test_data["double_check"]["correct_groups"]:
            # 勾选当前循环中的一个核查组。
            double_check.mark_group_correct(group)
        # 从 YAML 读取并选择双人核对的核对人员。
        double_check.select_checker(test_data["double_check"]["checker"])
        # 点击“双人核对”分区的“确认”按钮提交核对结果。
        double_check.confirm()
        # 确认提交后再次验证状态，失败时停止主流程。
        if not double_check.is_confirmed():
            # 明确中断流程并说明双人核对确认失败。
            raise AssertionError("双人核对确认失败，主流程已停止")

    # 透析后状态代表结束透析已完成，不再重复打开结束透析弹窗。
    if not is_post_dialysis:
        # 打开“结束透析”弹窗并取得其页面对象。
        end_dialysis_dialog = dialysis_sheet.open_end_dialysis_dialog()
        # 填写 YAML 配置的下机护士和回血流量，结束时间由页面自动生成。
        end_dialysis_dialog.fill_end_dialysis(test_data["end_dialysis"])
        # 从环境变量读取结束透析确认所需的登录密码，避免把密码写入代码或 YAML。
        end_dialysis_password = os.getenv("END_DIALYSIS_PASSWORD")
        # 密码未配置时中止流程，防止向页面提交空密码。
        if not end_dialysis_password:
            # 明确说明需要配置的环境变量名称。
            raise AssertionError("未配置结束透析密码环境变量 END_DIALYSIS_PASSWORD")
        # 点击结束透析弹窗中的“确认”按钮提交操作。
        end_dialysis_dialog.confirm(end_dialysis_password)
        # 等待结束透析弹窗关闭，确认提交操作已经完成。
        end_dialysis_dialog.is_closed()

        # 结束透析会自动生成第二条监测记录，填写后确认整个分区。
        if monitoring_records_data and len(monitoring_records_data["records"]) > 1:
            if monitoring_records is None:
                monitoring_records = dialysis_sheet.monitoring_records
            monitoring_records.fill_existing_records_from(
                [monitoring_records_data["records"][1]], start_index=1
            )
            monitoring_records.confirm()
            if not monitoring_records.is_confirmed():
                raise AssertionError("监测记录确认失败，主流程已停止")

    # 结束透析后填写透后评估；页面已确认时跳过，避免重复覆盖业务数据。
    post_assessment_data = test_data.get("post_dialysis_assessment")
    if post_assessment_data:
        post_assessment = dialysis_sheet.post_dialysis_assessment
        if not post_assessment.is_currently_confirmed():
            post_assessment.fill_assessment(post_assessment_data["editable"])
            post_assessment.confirm()
            if not post_assessment.is_confirmed():
                raise AssertionError("透后评估确认失败，主流程已停止")

    # 填写治疗小结的健康宣教和治疗小结文本，并确认该分区。
    treatment_summary_data = test_data.get("treatment_summary")
    if treatment_summary_data:
        treatment_summary = dialysis_sheet.treatment_summary
        if not treatment_summary.is_currently_confirmed():
            treatment_summary.fill_summary(treatment_summary_data)
            treatment_summary.confirm()
            if not treatment_summary.is_confirmed():
                raise AssertionError("治疗小结确认失败，主流程已停止")

    # 所有分区均完成后，检查临时医嘱和监测记录状态，再执行透析单自查。
    if monitoring_records_data and post_assessment_data and treatment_summary_data:
        if not temporary_orders.are_all_executed():
            raise AssertionError("仍有临时医嘱未执行，主流程已停止")
        if monitoring_records is None:
            monitoring_records = dialysis_sheet.monitoring_records
        if not monitoring_records.is_confirmed():
            raise AssertionError("监测记录未确认，主流程已停止")
        dialysis_sheet.run_self_check()


# 将该用例归类为回归测试，便于按标记筛选执行。
@pytest.mark.regression
# 定义端到端测试入口，pytest 会提供已初始化的浏览器页面对象。
def test_confirm_assessment_before_dialysis_prescription_for_test_patient(page):
    # 说明本用例覆盖的完整业务目标。
    """验证指定测试患者完成开始透析后新增并执行全部临时医嘱。"""
    # 以 UTF-8 编码打开 YAML 文件，避免中文内容读取错误。
    with MAIN_WRITE_DATA_FILE.open(encoding="utf-8") as data_file:
        # 将 YAML 内容转换为 Python 字典，供业务流程使用。
        test_data = yaml.safe_load(data_file)

    # 打开透析单页面，并创建对应的页面对象。
    dialysis_sheet = DialysisSheetPage(page).open()
    # 执行上面定义的完整主写入流程。
    execute_main_write(dialysis_sheet, test_data)
