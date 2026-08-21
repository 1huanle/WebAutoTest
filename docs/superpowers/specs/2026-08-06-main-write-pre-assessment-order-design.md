# 主流程先透前评估后透析处方设计

## 目标

优化 `tests/main_write.py` 的血液透析主流程：选择测试患者后，先按截图填写并确认透前评估，确认成功后再填写并确认透析处方。所有主流程数据统一存放在 `data/main_write.yaml`。

本次只调整透前评估和透析处方的执行顺序，不加入临时医嘱、双人核对、监测记录、透后评估或治疗小结。

## 主流程顺序

单条主流程用例按以下顺序执行：

1. 打开透析管理页面。
2. 按透析号 `21000536543` 选择“陈奕源测试”。
3. 使用 `PreDialysisAssessmentSection.fill_assessment()` 填写透前评估。
4. 使用 `expect_calculated_values()` 校验截图中的联动只读值。
5. 点击透前评估“确认”，并断言不再显示“未确认”。
6. 使用 `PrescriptionSection.fill_prescription()` 填写透析处方。
7. 点击透析处方“确认”，处理首次确认可能触发的医嘱推送弹窗。
8. 断言透析处方已确认，且医嘱推送弹窗及所属遮罩已经关闭。

透前评估确认失败时不得继续填写透析处方。

## YAML 数据结构

`data/main_write.yaml` 保留现有 `patient` 和 `prescription`，新增：

```yaml
pre_dialysis_assessment:
  editable:
    temperature: "36"
    pulse: "80"
    respiration: "20"
    respiration_type: 自主呼吸
    systolic_pressure: "110"
    diastolic_pressure: "80"
    blood_pressure_site: 上肢
    weighing_method: 正常
    pre_weight: "70"
    clothing_weight: "0"
    expected_dehydration_liters: "0"
    a_thrombus: "/"
    v_thrombus: "/"
  expected:
    dry_weight: 待定
    last_post_weight: "1"
    pre_weight: "70"
    weight_gain: "69"
    total_ultrafiltration: "1"
    dialysis_interval: "/"
    last_post_dialysis: "/"
    pre_dialysis_symptoms: 无症状
    fistula: "/"
    catheter: "/"
    comorbidities: 无
```

“上一次凝血”和“上一次抗凝剂”是患者历史只读展示，不属于本次可填写字段，不在主流程中修改。

## 代码结构

`tests/main_write.py` 新增一个可单独测试的主流程编排函数。真实 pytest 用例只负责读取 YAML、创建 `DialysisSheetPage` 并调用该函数。编排函数只调用 POM 公开方法，不直接写页面定位器。

原有“取消同步透析方案”测试保留，数据文件常量改为表达主流程含义的名称。

## 测试策略

新增 `tests/test_main_write_flow.py`，使用记录调用顺序的轻量假对象验证：

- 透前评估的填写、联动值校验、确认和确认断言全部发生在透析处方填写之前。
- 主流程从 YAML 取得 `pre_dialysis_assessment.editable`、`pre_dialysis_assessment.expected` 和 `prescription` 数据。
- 顺序测试不访问真实网站，不写入患者数据。

完成后运行顺序测试、相关 POM 测试、YAML 解析检查和 Python 编译。除非用户另行确认，不执行会真实保存患者数据的 `tests/main_write.py`。
