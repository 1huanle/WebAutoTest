# 血液透析剩余业务分区 POM 设计

## 目标

在已有透析处方 POM 基础上，完成血液透析透析单中透前评估、临时医嘱、双人核对、监测记录、透后评估和治疗小结六个业务分区的可操作 POM。所有公开方法和关键定位逻辑使用中文注释，并明确标记所属业务路径。

本次只封装页面能力，不编排 `main_write.py` 的业务顺序，也不在真实患者上执行确认、执行医嘱、核对医嘱或删除等写入动作。

## 架构

采用“一个业务分区一个 POM 文件，复杂 iframe 弹窗一个独立组件”的结构：

- `pre_dialysis_assessment_section.py`：透前评估页面内表单。
- `temporary_orders_section.py`：临时医嘱列表和列表操作。
- `dialogs/temporary_order_dialog.py`：血液透析 > 临时医嘱触发的新增医嘱 iframe 弹窗。
- `double_check_section.py`：双人核对分组核查表单。
- `monitoring_records_section.py`：监测记录列表和列表操作。
- `dialogs/monitoring_record_dialog.py`：血液透析 > 监测记录触发的新增监测 iframe 弹窗。
- `post_dialysis_assessment_section.py`：透后评估页面内表单。
- `treatment_summary_section.py`：治疗小结页面内表单及同步动作。

删除 `remaining_sections.py` 中的四个空壳类，并由 `DialysisSheetPage` 分别导入新文件。公共可见性、按钮读取和字段标签读取继续复用 `DialysisSheetSection`。

不建立依赖动态来源字符串的万能表单类。各分区即使存在同名字段，也通过所属分区表格限制定位范围。

## 透前评估

`PreDialysisAssessmentSection` 提供：

- `fill_assessment(data)`：填写体温 `tx_pg_t`、脉搏 `tx_pg_p`、呼吸 `tx_pg_hr`、呼吸方式 `tx_pg_hr_type`、收缩压 `tx_pg_BP_shousuo`、舒张压 `tx_pg_BP_shuzhang`、测量部位 `tx_pg_BP_type`、称重方式 `#txq_czfs`、透前称重 `tx_tqcz`、衣物重 `tx_peel_weight`、预期脱水量 `tx_yztsl`、A/V 端血栓 `tx_a_xx` 和 `tx_v_xx`。
- `expect_calculated_values(data)`：校验干体重、上次透后体重、透前体重、体重增加、超滤总量、透析间期、前次透析后、透前症状、内瘘、导管、合并症等只读或联动字段。
- `confirm()` 和 `is_confirmed()`：点击本分区确认并校验状态。

字段定位优先使用 `name`，没有 `name` 的称重方式使用稳定 `id`。

## 临时医嘱

`TemporaryOrdersSection` 提供：

- 读取医嘱列表表头和行数据。
- 按医嘱内容选择目标行。
- 打开添加医嘱、医嘱模板。
- 执行、核对和删除选中医嘱。
- `TemporaryOrderDialog` 属性，用于处理新增医嘱弹窗。

`TemporaryOrderDialog` 明确标记“血液透析 > 临时医嘱触发”，提供：

- 等待 iframe 打开和取消关闭。
- 填写开始时间、提醒日期、医嘱名称、单次剂量、数量、给药途径、频次、执行科室、诊断和备注。
- 校验临时类型、医嘱日期、开嘱医生和只读医嘱描述。
- 点击确认并等待所属弹窗与对应遮罩关闭。

## 双人核对

`DoubleCheckSection` 按四个核查组封装：

- 透析物品核查：`tx_touXiWuPin_indicator`。
- 透析参数核查：`tx_touXiCanShu_indicator`。
- 血管通路核查：`tx_xueGuanTongLu_indicator`。
- 管道连接核查：`tx_guanDao_indicator`。

提供：

- 设置每组“正确”状态或填写差错说明。
- 按人工肾、穿刺针、钾、钙、透析方式、抗凝剂、血流量、通路类型及管道连接等页面业务标签选择明细复选框。
- 选择核对人员 `tx_hd_nurse`。
- 读取核对时间 `tx_check_time`。
- 点击确认并校验已确认。

明细复选框没有稳定 `name/id`。定位必须从业务标签查找相邻复选框，禁止使用全局固定序号。

## 监测记录

`MonitoringRecordsSection` 提供：

- 读取时间、脉搏、呼吸、血压、KT/V、血流量、静脉压、动脉压、跨膜压、超滤率、超滤量、电导度、置换率、置换量、症状、处理、结果、监测护士等表格列。
- 打开添加监测、选择记录、删除、打开设置字段和血压手表。
- 点击分区确认并校验已确认。
- `MonitoringRecordDialog` 属性，用于处理新增监测弹窗。

`MonitoringRecordDialog` 明确标记“血液透析 > 监测记录触发”，提供：

- 填写监测时间 `tx_jcjl_time`、脉搏 `tx_jcjl_mb`、呼吸 `tx_jcjl_hx`、血压 `tx_jcjl_xy/tx_jcjl_xy1`、血流量 `tx_jcjl_xll`、静脉压 `tx_jcjl_my`、动脉压 `tx_jcjl_dmy`、跨膜压 `tx_jcjl_kmy`、超滤率 `tx_jcjl_cll`、超滤量 `tx_jcjl_clliang`、电导度 `tx_jcjl_ddd`、KT/V `tx_ktv`、血温、置换量、置换率、钠值、症状、处理和结果。
- 校验日期、自动计算字段和只读监测护士。
- 确认或取消，并等待所属弹窗与对应遮罩关闭。

## 透后评估

`PostDialysisAssessmentSection` 提供：

- 填写体温、脉搏、呼吸方式、血压、实际脱水量、实际置换量、治疗时长、称重方式、透后称重、衣物重、实际回血量、反应、其他、最大血流量及通路相关字段。
- 校验透后体重、体重减少、抗凝相关值、透前症状、透析中总入量、内瘘、导管和并发症等只读字段。
- 点击确认并校验已确认。

## 治疗小结

`TreatmentSummarySection` 提供：

- 填写透后宣教内容 `tx_zlxj_content`、透析小结 `tx_zlxj_xj`、透析器编号 `tx_txq_no`。
- 选择宣教人 `tx_xj_person`、小结签名 `tx_xj_qm`、穿刺/换药 `tx_zl_fs`、换药护士 `tx_sj_nurse`、治疗护士 `tx_zl_nurse`、上机护士 `tx_sjhs`、预充管路 `tx_ycgl`、核对人员 `tx_hd_nurse`、下机护士 `tx_xj_nurse` 和治疗医生 `tx_zl_doctor`。
- 校验只读模板和通路图片字段。
- 封装同步到病程、同步到交班日志、确认和已确认校验。

## 弹窗和遮罩

iframe 弹窗组件只校验自己所属的 Layui 弹层和对应遮罩。组件在弹窗打开时读取外层 `times` 属性，并关联 `#layui-layer-shade{times}`，禁止使用全局 `.layui-layer-shade:visible` 数量作为关闭条件，避免页面上其他弹层导致误判。

必需弹窗超时未出现时测试应明确失败，不能静默跳过。取消方法不得提交数据。

## 测试策略

- 每个分区先编写模拟 DOM 测试并观察失败，再实现最小 POM 代码。
- 页面内表单测试覆盖字段填写、下拉选择、只读校验、确认和业务范围隔离。
- iframe 组件测试覆盖等待打开、跨 iframe 填写、确认、取消和所属遮罩关闭。
- 双人核对测试通过业务标签验证复选框定位，不允许用固定索引断言。
- 真实页面只执行加载、分区可见、字段和按钮存在的只读回归。
- 不在本轮真实页面测试中点击确认、执行、核对、删除或同步按钮。

## 后续主流程

六个分区 POM 完成后，再根据用户提供的业务顺序和字段值编排 `tests/main_write.py`。所有主流程数据统一放在 `data/main_write.yaml`，主流程测试只负责组织 POM，不直接写定位器。

