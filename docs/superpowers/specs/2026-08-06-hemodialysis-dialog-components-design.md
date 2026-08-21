# 血液透析弹窗组件 POM 设计

## 目标

把透析处方首次确认后出现的“医嘱推送”弹窗从 `PrescriptionSection` 中拆成独立 POM 组件，并通过文件名、类名和中文注释明确记录弹窗的业务来源。血液透析下各业务分区出现弹窗时，分别使用所属分区的弹窗组件，禁止跨分区混用。

## 方案选择

采用“按业务来源拆分弹窗组件”的方案：

- 透析处方：`Prescription...Dialog`，文件名前缀为 `prescription_`。
- 透前评估：`PreDialysisAssessment...Dialog`，文件名前缀为 `pre_dialysis_assessment_`。
- 临时医嘱：`TemporaryOrders...Dialog`，文件名前缀为 `temporary_orders_`。
- 双人核对：`DoubleCheck...Dialog`，文件名前缀为 `double_check_`。
- 监测记录：`MonitoringRecords...Dialog`，文件名前缀为 `monitoring_records_`。
- 透后评估：`PostDialysisAssessment...Dialog`，文件名前缀为 `post_dialysis_assessment_`。
- 治疗小结：`TreatmentSummary...Dialog`，文件名前缀为 `treatment_summary_`。
- 不使用一个依赖来源字符串的万能弹窗类，避免调用方传错来源后仍能运行。
- 不继续把弹窗定位器放在分区 POM 中，避免分区填写逻辑与弹窗内部结构耦合。

## 组件设计

新增 `PrescriptionMedicalOrderPushDialog`，其职责仅包括：

1. 定位由“透析处方首次确认”触发的医嘱推送 Layui 弹窗。
2. 等待弹窗出现。
3. 进入弹窗 iframe，点击“确定”。
4. 等待弹窗和遮罩关闭。
5. 提供关闭状态校验。

类注释、公开方法注释及调用处注释都使用中文，并包含“血液透析 > 具体业务分区触发”标识。例如当前组件使用“血液透析 > 透析处方触发”。

`PrescriptionSection` 负责判断处方是否为首次确认、点击处方确认按钮，然后调用 `PrescriptionMedicalOrderPushDialog`。测试用例只操作 `PrescriptionSection` 暴露的业务方法，不直接定位弹窗内部按钮。

## 其他业务分区边界

本次不虚构尚未读取的透前评估、临时医嘱、双人核对、监测记录、透后评估或治疗小结弹窗元素。未来发现这些分区的弹窗时，应按照上面的固定前缀创建独立组件，并在中文注释中标记准确的业务路径。即使不同分区的弹窗标题或按钮相同，也不得复用其他分区的专属类。

## 错误处理

- 首次确认处方时，医嘱推送弹窗是必需流程；超时未出现应让测试明确失败，不能静默跳过。
- 弹窗按钮必须在 iframe 内精确匹配“确定”。
- 点击后必须同时验证弹窗不可见和 Layui 遮罩消失，避免后续步骤被遮挡。

## 测试设计

先修改测试，使其直接要求 `PrescriptionSection` 暴露来源明确的处方弹窗组件。拆分实现前测试应因该属性不存在而失败。随后新增组件并完成接线，使测试通过。

回归范围：

- 延迟出现的 iframe 医嘱推送弹窗会被自动确认。
- 弹窗确认后，弹窗节点和遮罩均关闭。
- `PrescriptionSection` 的原有处方填写、确认和状态校验行为保持不变。

