# Data Quality Checks / 数据质量检查

## 1. Purpose / 目的

This document describes the data quality checks used in the e-commerce offline data warehouse project.

本文档说明电商离线数仓项目中的数据质量检查设计。

Data quality checks are used to ensure that data is complete, consistent, valid, and ready for downstream analysis.

数据质量检查用于确保数据具备完整性、一致性、有效性，并能够支持后续分析。

The check script is:

检查脚本为：

```
scripts/run_data_quality_checks.py
```

---

## 2. Why Data Quality Matters / 为什么数据质量重要

In a data warehouse project, each layer depends on the previous layer.

在数仓项目中，每一层数据都依赖上一层数据。

If ODS data is missing, DWD cannot be built correctly.

如果 ODS 数据缺失，DWD 层就无法正确构建。

If DWD contains duplicate primary keys or invalid amounts, DWS metrics may be wrong.

如果 DWD 层存在主键重复或非法金额，DWS 指标就可能出错。

If DWS and ADS are inconsistent, BI dashboards may show incorrect business results.

如果 DWS 和 ADS 指标不一致，BI 看板就可能展示错误的业务结果。

Therefore, data quality checks are necessary for both engineering reliability and business trust.

因此，数据质量检查对于工程稳定性和业务可信度都非常重要。

---

## 3. Check Scope / 检查范围

The current data quality module checks the following layers:

当前数据质量模块检查以下分层：

| Layer / 分层  | Checked Objects / 检查对象                                     |
| ----------- | ---------------------------------------------------------- |
| ODS         | Raw-to-ODS output files / Raw 到 ODS 的输出文件                  |
| DWD         | `dwd_order_detail`                                         |
| DWS         | `dws_daily_order_summary`                                  |
| ADS         | `ads_daily_business_overview`                              |
| Cross-layer | Consistency between DWD, DWS, and ADS / DWD、DWS、ADS 之间的一致性 |

---

## 4. ODS Checks / ODS 检查

The ODS layer focuses on file completeness and technical field completeness.

ODS 层主要检查文件完整性和技术字段完整性。

Main checks include:

主要检查包括：

| Check / 检查项                | Rule / 规则                                                           |
| -------------------------- | ------------------------------------------------------------------- |
| File existence / 文件存在性     | Each expected ODS file should exist / 每个预期的 ODS 文件都应存在              |
| Row count / 行数             | Each ODS table should have more than 0 rows / 每张 ODS 表行数应大于 0       |
| `loaded_at` field / 加载时间字段 | Each ODS table should contain `loaded_at` / 每张 ODS 表应包含 `loaded_at` |
| `dt` field / 日期分区字段        | Each ODS table should contain `dt` / 每张 ODS 表应包含 `dt`               |

---

## 5. DWD Checks / DWD 检查

The DWD layer focuses on detail table correctness.

DWD 层主要检查明细表的正确性。

Main checks include:

主要检查包括：

| Check / 检查项                    | Rule / 规则                                                                                                                       |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| Required columns / 必需字段        | Core fields such as `order_id`, `purchase_date`, and amount fields should exist / `order_id`、`purchase_date`、金额字段等核心字段应存在       |
| Primary key duplication / 主键重复 | `order_id` should not be duplicated / `order_id` 不应重复                                                                           |
| Primary key null / 主键为空        | `order_id` should not be null / `order_id` 不应为空                                                                                 |
| Negative amount / 负金额          | Amount fields should not be negative / 金额字段不应为负数                                                                                |
| Purchase date null / 下单日期为空    | `purchase_date` should not be null / `purchase_date` 不应为空                                                                       |
| Binary flag values / 二值标记值     | Flags such as `is_delivered` and `is_late_delivery` should only contain 0 or 1 / `is_delivered`、`is_late_delivery` 等标记只能为 0 或 1 |

---

## 6. DWS Checks / DWS 检查

The DWS layer focuses on aggregated metric validity.

DWS 层主要检查汇总指标的有效性。

Main checks include:

主要检查包括：

| Check / 检查项                 | Rule / 规则                                                                                    |
| --------------------------- | -------------------------------------------------------------------------------------------- |
| Date granularity / 日期粒度     | There should be one row per `purchase_date` / 每个 `purchase_date` 应只有一行                       |
| Non-negative metrics / 非负指标 | Order counts, customer counts, GMV, and AOV should not be negative / 订单数、客户数、GMV、客单价等指标不应为负数 |
| Rate range / 比率范围           | Rate fields should be between 0 and 1 / 比率字段应在 0 到 1 之间                                      |

---

## 7. ADS Checks / ADS 检查

The ADS layer focuses on dashboard-ready metric validity.

ADS 层主要检查看板指标的有效性。

Main checks include:

主要检查包括：

| Check / 检查项                 | Rule / 规则                                                            |
| --------------------------- | -------------------------------------------------------------------- |
| Date granularity / 日期粒度     | There should be one row per `stat_date` / 每个 `stat_date` 应只有一行       |
| Non-negative metrics / 非负指标 | Daily and cumulative metrics should not be negative / 每日指标和累计指标不应为负数 |
| Rate range / 比率范围           | Rate fields should be between 0 and 1 / 比率字段应在 0 到 1 之间              |

---

## 8. Cross-layer Consistency Checks / 跨层一致性检查

Cross-layer checks ensure that aggregation does not change key business totals incorrectly.

跨层一致性检查用于确保聚合过程不会错误改变核心业务总量。

Main checks include:

主要检查包括：

| Check / 检查项                               | Rule / 规则                                                                              |
| ----------------------------------------- | -------------------------------------------------------------------------------------- |
| DWD vs DWS order count / DWD 与 DWS 订单数一致性 | DWD unique order count should equal DWS total order count / DWD 唯一订单数应等于 DWS 总订单数      |
| DWS vs ADS GMV / DWS 与 ADS GMV 一致性        | DWS total payment amount should equal ADS daily GMV sum / DWS 总支付金额应等于 ADS 每日 GMV 汇总   |
| DWS vs ADS order count / DWS 与 ADS 订单数一致性 | DWS total order count should equal ADS daily order count sum / DWS 总订单数应等于 ADS 每日订单数汇总 |

---

## 9. Output Files / 输出文件

After running the script, the following files are generated:

运行脚本后，会生成以下文件：

| File / 文件                            | Description / 说明                                 |
| ------------------------------------ | ------------------------------------------------ |
| `docs/data_quality_check_report.csv` | Detailed data quality check report / 详细数据质量检查报告  |
| `docs/data_quality_check_summary.md` | Summary of data quality check results / 数据质量检查总结 |

---

## 10. Report Fields / 报告字段

The detailed report contains the following fields:

详细报告包含以下字段：

| Field / 字段      | Description / 说明                                          |
| --------------- | --------------------------------------------------------- |
| `check_time`    | Time when the check was executed / 检查执行时间                 |
| `layer`         | Warehouse layer being checked / 被检查的数仓分层                  |
| `table_name`    | Table or object name / 表名或对象名                             |
| `check_name`    | Data quality check name / 数据质量检查项名称                       |
| `status`        | Check status: PASS, FAIL, or WARN / 检查状态：PASS、FAIL 或 WARN |
| `actual_value`  | Actual observed value / 实际检查值                             |
| `expected_rule` | Expected rule or condition / 预期规则或条件                      |
| `message`       | Additional explanation / 补充说明                             |

---

## 11. How to Run / 如何运行

Run the following command from the project root directory:

在项目根目录执行以下命令：

```
python scripts/run_data_quality_checks.py
```

After running the command, check the generated report files in the `docs/` directory.

运行命令后，在 `docs/` 目录中查看生成的报告文件。

---

## 12. Summary / 总结

The data quality module improves the reliability of the data warehouse pipeline.

数据质量模块提升了数仓链路的可靠性。

It checks file completeness, key fields, primary keys, amount values, date granularity, metric ranges, and cross-layer consistency.

它检查文件完整性、核心字段、主键、金额值、日期粒度、指标范围和跨层一致性。

This module makes the project closer to a real enterprise data development workflow.

该模块使项目更加接近真实企业中的数据开发流程。
