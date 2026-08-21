# 主流程开始透析弹窗设计

## 目标

在主流程完成并确认透前评估和透析处方后，点击页面顶部“开始透析”，按照指定数据填写“开始透析”弹窗，点击“确认”保存，并校验弹窗及其遮罩已关闭。

## 流程顺序

主流程顺序固定为：

1. 通过透析号选择患者。
2. 填写并确认透前评估；确认失败立即停止。
3. 填写并确认透析处方，并处理处方触发的医嘱推送弹窗。
4. 点击“开始透析”，等待开始透析 iframe 弹窗打开。
5. 填写弹窗数据，点击“确认”，等待弹窗及对应遮罩关闭。

开始透析步骤不得在透前评估或透析处方确认失败时执行。

## POM 结构

新增 `pages/hemodialysis/dialogs/start_dialysis_dialog.py`，定义 `StartDialysisDialog`，继承现有 `LayuiIframeDialog`。

- `TITLE = "开始透析"`，用于限定当前业务弹层。
- `fill_start_dialysis(data)` 负责选择下拉框、点选穿刺业务字典并填写引血流量。
- 字段使用真实页面已验证的稳定 `name` 属性定位，不使用全局序号定位：治疗护士 `tx_zl_nurse`、上机护士 `tx_sjhs`、预充管路 `tx_ycgl`、穿刺/换药 `tx_fs`、穿刺护士 `tx_sj_nurse`、穿刺方式 `tx_ccfs`、穿刺针 `tx_ccz`、穿刺针型号 `tx_cczxh`、穿刺方向 `tx_ccfx`、引血 `tx_yx`、入科方式 `tx_rkfs`。
- 穿刺方式、穿刺针、穿刺针型号和穿刺方向是只读输入框。POM 点击对应输入框后，在 iframe 内部 `role="dialog"` 的选项浮层中点击精确业务值，再点击“保存”关闭浮层。
- `confirm()` 点击弹窗底部精确文本为“确认”的按钮，并等待弹窗及对应遮罩关闭。
- `is_closed()` 复用基类能力，用于主流程最终断言。

`DialysisSheetPage` 新增 `start_dialysis_dialog` 属性，并新增 `open_start_dialysis_dialog()`：点击页面顶部精确名称为“开始透析”的按钮，等待弹窗打开后返回弹窗对象。

## 测试数据

在 `data/main_write.yaml` 新增 `start_dialysis`：

```yaml
start_dialysis:
  treatment_nurse: 陈奕源
  machine_nurse: 陈奕源
  priming_tubing_nurse: 陈奕源
  operation_type: 穿刺
  puncture_nurse: 陈奕源
  puncture_method: 扣眼法
  puncture_needle: A锐针
  puncture_needle_model: A端-17号
  puncture_direction: V端向心
  blood_introduction_flow: "5"
  admission_method: 步行
```

“穿刺位点”和“透析器编号”不写入 YAML，POM 不操作这两个字段，分别保持“请选择”和空白状态。

## 主流程编排

`tests/main_write.py` 的 `execute_main_write()` 在处方确认和医嘱推送弹窗关闭断言之后：

1. 调用 `dialysis_sheet.open_start_dialysis_dialog()`。
2. 调用 `fill_start_dialysis(test_data["start_dialysis"])`。
3. 调用 `confirm()`。
4. 断言 `is_closed()`。

新增中文注释，明确该弹窗属于“血液透析 > 开始透析”。

## 测试策略

- YAML 测试完整验证 `start_dialysis` 数据，确保空白字段没有被配置。
- 使用本地 HTML iframe 构造开始透析弹窗，验证所有下拉框和引血流量填写、确认按钮以及关联遮罩关闭。
- 扩展记录型主流程测试，验证开始透析只发生在透前评估和透析处方完成之后。
- 增加处方确认失败时不得打开开始透析弹窗的负向测试。
- 运行完整测试套件，但不执行 `tests/main_write.py`，避免自动写入真实患者数据。

## 范围边界

- 不填写穿刺位点。
- 不填写透析器编号。
- 不修改透前评估、透析处方或其他血液透析模块的数据。
- 不在本次自动验证中保存真实开始透析记录。
