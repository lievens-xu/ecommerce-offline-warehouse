# Pipeline Run Summary / 主流程运行总结

## 1. Overall Result / 总体结果

| Metric / 指标 | Value / 数值 |
|---|---:|
| Total steps / 总步骤数 | 7 |
| Passed steps / 通过步骤数 | 7 |
| Failed steps / 失败步骤数 | 0 |
| Skipped steps / 跳过步骤数 | 0 |
| Total duration seconds / 总耗时秒数 | 45.04 |

## 2. Step Details / 步骤明细

| Order / 顺序 | Step / 步骤 | Script / 脚本 | Status / 状态 | Duration / 耗时秒 |
|---:|---|---|---|---:|
| 1 | Raw Data Profiling | `check_raw_data.py` | PASS | 5.36 |
| 2 | Raw to ODS Loading | `load_raw_to_ods.py` | PASS | 11.26 |
| 3 | DWD Order Detail Building | `build_dwd_order_detail.py` | PASS | 8.47 |
| 4 | DWS Daily Order Summary Building | `build_dws_daily_order_summary.py` | PASS | 3.5 |
| 5 | ADS Daily Business Overview Building | `build_ads_daily_business_overview.py` | PASS | 1.4 |
| 6 | Data Quality Checks | `run_data_quality_checks.py` | PASS | 7.91 |
| 7 | Dashboard Chart Building | `build_dashboard_charts.py` | PASS | 7.14 |

## 3. Output Files / 输出文件

The detailed report and log files are generated at:

详细运行报告和日志文件生成在：

    docs/pipeline_run_report.csv
    docs/pipeline_latest_run.log

All pipeline steps completed successfully.

所有主流程步骤均已成功完成。
