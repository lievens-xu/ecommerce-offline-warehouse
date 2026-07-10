# Pandas vs Spark Comparison Summary / Pandas 与 Spark 对比总结

Generated at: 2026-06-24 12:42:48

## 1. Overall Summary / 总体结果

| Metric / 指标 | Value / 数值 |
|---|---:|
| Total checks / 总检查数 | 23 |
| Passed checks / 通过检查数 | 23 |
| Failed checks / 失败检查数 | 0 |

**All comparison checks passed.**

**所有对比检查均已通过。**

## 2. Layer Summary / 分层总结

| Layer / 分层 | Total / 总数 | Passed / 通过 | Failed / 失败 |
|---|---:|---:|---:|
| DWD | 9 | 9 | 0 |
| DWS | 7 | 7 | 0 |
| ADS | 7 | 7 | 0 |

## 3. DWD Layer Checks / DWD 分层检查

| Metric / 指标 | Pandas Value / Pandas 值 | Spark Value / Spark 值 | Difference / 差异 | Tolerance / 容差 | Status / 状态 |
|---|---:|---:|---:|---:|---|
| row_count | 99441 | 99441 | 0 | 0 | PASS |
| unique_order_count | 99441 | 99441 | 0 | 0 | PASS |
| unique_customer_count | 96096 | 96096 | 0 | 0 | PASS |
| total_payment_amount | 16008872.12 | 16008872.12 | 0.0 | 0.01 | PASS |
| total_product_amount | 13591643.7 | 13591643.7 | 0.0 | 0.01 | PASS |
| total_freight_amount | 2251909.54 | 2251909.54 | 0.0 | 0.01 | PASS |
| delivered_order_count | 96476 | 96476 | 0 | 0 | PASS |
| late_delivery_order_count | 6535 | 6535 | 0 | 0 | PASS |
| average_review_score | 4.09 | 4.06 | 0.03 | 0.05 | PASS |

## 4. DWS Layer Checks / DWS 分层检查

| Metric / 指标 | Pandas Value / Pandas 值 | Spark Value / Spark 值 | Difference / 差异 | Tolerance / 容差 | Status / 状态 |
|---|---:|---:|---:|---:|---|
| row_count | 634 | 634 | 0 | 0 | PASS |
| total_order_count | 99441 | 99441 | 0 | 0 | PASS |
| total_valid_order_count | 98207 | 98207 | 0 | 0 | PASS |
| total_payment_amount | 16008872.12 | 16008872.12 | 0.0 | 0.01 | PASS |
| total_product_amount | 13591643.7 | 13591643.7 | 0.0 | 0.01 | PASS |
| total_freight_amount | 2251909.54 | 2251909.54 | 0.0 | 0.01 | PASS |
| overall_aov | 160.9886 | 160.9886 | 0.0 | 0.05 | PASS |

## 5. ADS Layer Checks / ADS 分层检查

| Metric / 指标 | Pandas Value / Pandas 值 | Spark Value / Spark 值 | Difference / 差异 | Tolerance / 容差 | Status / 状态 |
|---|---:|---:|---:|---:|---|
| row_count | 634 | 634 | 0 | 0 | PASS |
| total_order_count | 99441 | 99441 | 0 | 0 | PASS |
| total_gmv | 16008872.12 | 16008872.12 | 0.0 | 0.01 | PASS |
| average_daily_gmv | 25250.5869 | 25250.5869 | 0.0 | 0.05 | PASS |
| overall_aov | 160.9886 | 160.9886 | 0.0 | 0.05 | PASS |
| latest_daily_gmv | 89.71 | 89.71 | 0.0 | 0.01 | PASS |
| latest_daily_order_count | 1 | 1 | 0 | 0 | PASS |

## 6. Failed Checks Details / 失败检查详情

No checks failed.

无失败检查。

## 7. Output Files / 输出文件

The detailed comparison report is available at:

详细对比报告生成在：

- `docs\pandas_spark_full_comparison_report.csv`

