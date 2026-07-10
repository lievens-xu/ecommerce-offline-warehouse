# dbt PostgreSQL vs Pandas Baseline Comparison / dbt PostgreSQL 与 Pandas 基准比较

Generated at / 生成时间: 2026-06-24 09:34:35

## 1. Overall Summary / 总体结果

| Metric / 指标 | Value / 数值 |
|---|---:|
| Total checks / 总检查数 | 21 |
| Passed checks / 通过检查数 | 21 |
| Failed checks / 失败检查数 | 0 |

**All dbt PostgreSQL outputs are consistent with Pandas baseline outputs.**

**所有 dbt PostgreSQL 输出与 Pandas 基准输出一致。**

## 2. Layer Summary / 分层总结

| Layer / 分层 | Total / 总数 | Passed / 通过 | Failed / 失败 |
|---|---:|---:|---:|
| DWD / 明细层 | 7 | 7 | 0 |
| DWS / 汇总层 | 6 | 6 | 0 |
| ADS / 应用层 | 8 | 8 | 0 |

## 3. Detailed Comparison Results / 详细比较结果

| Metric / 指标 | Pandas Value / Pandas 值 | dbt PostgreSQL Value / dbt PostgreSQL 值 | Difference / 差异 | Tolerance / 误差 | Status / 状态 |
|---|---:|---:|---:|---:|:---:|
| dwd_row_count | 99441 | 99441 | 0 | 0 | ✅ PASS |
| dwd_unique_order_count | 99441 | 99441 | 0 | 0 | ✅ PASS |
| dwd_total_payment_amount | 16008872.12 | 16008872.12 | 0.0 | 0.01 | ✅ PASS |
| dwd_total_product_amount | 13591643.7 | 13591643.7 | 0.0 | 0.01 | ✅ PASS |
| dwd_total_freight_amount | 2251909.54 | 2251909.54 | 0.0 | 0.01 | ✅ PASS |
| dwd_delivered_order_count | 96476 | 96476 | 0 | 0 | ✅ PASS |
| dwd_average_review_score | 4.09 | 4.06 | 0.03 | 0.05 | ✅ PASS |
| dws_row_count | 634 | 634 | 0 | 0 | ✅ PASS |
| dws_total_order_count | 99441 | 99441 | 0 | 0 | ✅ PASS |
| dws_total_payment_amount | 16008872.12 | 16008872.12 | 0.0 | 0.01 | ✅ PASS |
| dws_total_product_amount | 13591643.7 | 13591643.7 | 0.0 | 0.01 | ✅ PASS |
| dws_start_date | 0.0 | 0.0 | 0.0 | 0 | ✅ PASS |
| dws_end_date | 0.0 | 0.0 | 0.0 | 0 | ✅ PASS |
| ads_row_count | 634 | 634 | 0 | 0 | ✅ PASS |
| ads_total_order_count | 99441 | 99441 | 0 | 0 | ✅ PASS |
| ads_total_gmv | 16008872.12 | 16008872.12 | 0.0 | 0.01 | ✅ PASS |
| ads_average_daily_gmv | 25250.5869 | 25250.5869 | 0.0 | 0.05 | ✅ PASS |
| ads_latest_daily_gmv | 89.71 | 89.71 | 0.0 | 0.01 | ✅ PASS |
| ads_latest_daily_order_count | 1 | 1 | 0 | 0 | ✅ PASS |
| ads_start_date | 0.0 | 0.0 | 0.0 | 0 | ✅ PASS |
| ads_end_date | 0.0 | 0.0 | 0.0 | 0 | ✅ PASS |

## 4. Failed Checks Details / 失败检查详情

No checks failed.

无失败检查。

## 5. Comparison Scope / 比较范围

| Layer / 分层 | Pandas Source / Pandas 源 | dbt PostgreSQL Source / dbt PostgreSQL 源 |
|---|---|---|
| DWD | `data/dwd/dwd_order_detail.csv` | `dwd.dwd_order_detail` |
| DWS | `data/dws/dws_daily_order_summary.csv` | `dws.dws_daily_order_summary` |
| ADS | `data/ads/ads_daily_business_overview.csv` | `ads.ads_daily_business_overview` |

Output reports / 输出报告：

- `docs/dbt_postgres_comparison_report.csv`
- `docs/dbt_postgres_comparison_summary.md`
