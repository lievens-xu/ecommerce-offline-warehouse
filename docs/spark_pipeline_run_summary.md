# Spark Pipeline Run Summary / Spark 主流程运行总结

Generated at / 生成时间: 2026-06-24 12:42:48

## 1. Pipeline Timing / 主流程时间

| Metric / 指标 | Value / 数值 |
|---|---|
| Pipeline start time / 主流程开始时间 | 2026-06-24 12:41:22 |
| Pipeline end time / 主流程结束时间 | 2026-06-24 12:42:48 |
| Total duration seconds / 总耗时秒数 | 86.78 |

## 2. Overall Result / 总体结果

| Metric / 指标 | Value / 数值 |
|---|---:|
| Total steps / 总步骤数 | 4 |
| Success steps / 成功步骤数 | 4 |
| Failed steps / 失败步骤数 | 0 |
| Skipped steps / 跳过步骤数 | 0 |

**All pipeline steps completed successfully.**

**所有主流程步骤均已成功完成。**

## 3. Step Details / 步骤明细

| Order / 顺序 | Step / 步骤 | Script / 脚本 | Status / 状态 | Duration / 耗时秒 |
|---:|---|---|---|---:|
| 1 | Spark DWD Order Detail Building | `spark_build_dwd_order_detail.py` | SUCCESS | 47.51 |
| 2 | Spark DWS Daily Order Summary Building | `spark_build_dws_daily_order_summary.py` | SUCCESS | 20.68 |
| 3 | Spark ADS Daily Business Overview Building | `spark_build_ads_daily_business_overview.py` | SUCCESS | 16.16 |
| 4 | Pandas vs Spark Full Comparison | `compare_pandas_spark_outputs.py` | SUCCESS | 2.42 |

## 4. Failed/Skipped Steps Details / 失败/跳过步骤详情

No failed or skipped steps.

无失败或跳过步骤。

## 5. Output Files / 输出文件

The detailed report and log files are generated at:

详细运行报告和日志文件生成在：

    docs/spark_pipeline_run_report.csv
    docs/spark_pipeline_latest_run.log

## 6. Final Result / 最终结果

```
[DONE] Spark pipeline completed successfully.
```

```
[DONE] Spark 主流程已成功完成。
```
