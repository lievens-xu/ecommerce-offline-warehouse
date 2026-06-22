# Pipeline Orchestration / 主流程编排

## 1. Purpose / 目的

This document describes the end-to-end pipeline orchestration of the e-commerce offline data warehouse project.

本文档说明电商离线数仓项目的端到端主流程编排设计。

The pipeline script is:

主流程脚本为：

```
scripts/run_pipeline.py
```

The goal of this script is to run all ETL and data quality steps with one command.

该脚本的目标是通过一条命令运行所有 ETL 和数据质量检查步骤。

---

## 2. Pipeline Command / 主流程运行命令

Run the following command from the project root directory:

在项目根目录执行以下命令：

```
python scripts/run_pipeline.py
```

This command will execute the complete offline data warehouse workflow.

该命令会执行完整的离线数仓处理流程。

---

## 3. Pipeline Steps / 主流程步骤

The pipeline contains the following steps:

主流程包含以下步骤：

| Order / 顺序 | Step / 步骤                            | Script / 脚本                            | Description / 说明                                                                  |
| ---------: | ------------------------------------ | -------------------------------------- | --------------------------------------------------------------------------------- |
|          1 | Raw Data Profiling                   | `check_raw_data.py`                    | Profile raw CSV files and generate raw data reports / 检查原始 CSV 文件并生成数据探查报告        |
|          2 | Raw to ODS Loading                   | `load_raw_to_ods.py`                   | Load raw files into the ODS layer / 将原始文件加载到 ODS 层                                |
|          3 | DWD Order Detail Building            | `build_dwd_order_detail.py`            | Build the DWD order detail wide table / 构建 DWD 订单明细宽表                             |
|          4 | DWS Daily Order Summary Building     | `build_dws_daily_order_summary.py`     | Build the DWS daily order summary table / 构建 DWS 每日订单汇总表                          |
|          5 | ADS Daily Business Overview Building | `build_ads_daily_business_overview.py` | Build the ADS dashboard-ready business overview table / 构建 ADS 每日经营看板表            |
|          6 | Data Quality Checks                  | `run_data_quality_checks.py`           | Run data quality checks across all layers / 对所有数仓分层运行数据质量检查                       |
|          7 | Dashboard Chart Building             | `build_dashboard_charts.py`            | Generate dashboard charts and KPI summary from ADS data / 基于 ADS 数据生成看板图表和 KPI 汇总 |

---

## 4. Pipeline Flow / 主流程流向

The full data flow is:

完整数据流如下：

```
```
Raw CSV Files
    ↓
Raw Data Profiling
    ↓
ODS Layer
    ↓
DWD Layer
    ↓
DWS Layer
    ↓
ADS Layer
    ↓
Data Quality Checks
    ↓
Dashboard Charts
    ↓
Reports and Logs
```

Chinese explanation:

中文说明：

```
原始 CSV 文件
    ↓
原始数据探查
    ↓
ODS 原始数据层
    ↓
DWD 明细数据层
    ↓
DWS 汇总数据层
    ↓
ADS 应用数据层
    ↓
数据质量检查
    ↓
看板图表生成
    ↓
报告与日志
```


---

## 5. Execution Strategy / 执行策略

The pipeline uses a sequential execution strategy.

该主流程采用顺序执行策略。

This means each step depends on the successful completion of the previous step.

这意味着每一步都依赖前一步成功完成。

For example:

例如：

* DWD cannot be built before ODS data is generated.
  在 ODS 数据生成之前，无法构建 DWD 层。

* DWS cannot be built before DWD data is generated.
  在 DWD 数据生成之前，无法构建 DWS 层。

* ADS cannot be built before DWS data is generated.
  在 DWS 数据生成之前，无法构建 ADS 层。

* Data quality checks should run after all data layers are generated.
  数据质量检查应在所有数据分层生成之后运行。

If one step fails, the following steps will be skipped.

如果某一步失败，后续步骤会被跳过。

This prevents later layers from being built on incomplete or incorrect upstream data.

这可以避免后续分层基于不完整或错误的上游数据继续构建。

---

## 6. Output Reports / 输出报告

After running the pipeline, the following files are generated:

运行主流程后，会生成以下文件：

| File / 文件                      | Description / 说明                              |
| ------------------------------ | --------------------------------------------- |
| `docs/pipeline_run_report.csv` | Structured pipeline run report / 结构化主流程运行报告   |
| `docs/pipeline_latest_run.log` | Full pipeline execution log / 完整主流程运行日志       |
| `docs/pipeline_run_summary.md` | Bilingual pipeline run summary / 中英文对照主流程运行总结 |

---

## 7. Report Fields / 报告字段

The pipeline report contains the following fields:

主流程运行报告包含以下字段：

| Field / 字段         | Description / 说明                                               |
| ------------------ | -------------------------------------------------------------- |
| `step_order`       | Execution order of the step / 步骤执行顺序                           |
| `step_name`        | Step name / 步骤名称                                               |
| `script`           | Script executed in this step / 当前步骤执行的脚本                       |
| `status`           | Step status: PASS, FAIL, or SKIPPED / 步骤状态：PASS、FAIL 或 SKIPPED |
| `return_code`      | Process return code / 进程返回码                                    |
| `start_time`       | Step start time / 步骤开始时间                                       |
| `end_time`         | Step end time / 步骤结束时间                                         |
| `duration_seconds` | Step duration in seconds / 步骤耗时秒数                              |
| `description`      | Step description / 步骤说明                                        |
| `error_message`    | Error message if the step fails / 步骤失败时的错误信息                   |

---

## 8. Log File / 日志文件

The full log file is:

完整日志文件为：

```
docs/pipeline_latest_run.log
```

This file stores the standard output and error output of each step.

该文件保存每一步的标准输出和错误输出。

It is useful for debugging when the pipeline fails.

当主流程失败时，该文件可用于排查问题。

---

## 9. Error Handling / 错误处理

The pipeline uses a fail-fast strategy.

主流程采用快速失败策略。

If a step fails, the pipeline will stop executing later ETL steps.

如果某一步失败，主流程会停止执行后续 ETL 步骤。

The failed step will be marked as `FAIL`.

失败步骤会被标记为 `FAIL`。

The following steps will be marked as `SKIPPED`.

后续步骤会被标记为 `SKIPPED`。

This design makes the dependency relationship between data layers clearer.

这种设计使数仓各层之间的依赖关系更加清晰。

---

## 10. Relationship with Data Warehouse Layers / 与数仓分层的关系

The pipeline connects all warehouse layers into one complete workflow.

主流程将所有数仓分层连接成一个完整工作流。

| Layer / 分层    | Generated By / 生成脚本                    | Output / 输出                                |
| ------------- | -------------------------------------- | ------------------------------------------ |
| Raw Profiling | `check_raw_data.py`                    | Raw data profile reports / 原始数据探查报告        |
| ODS           | `load_raw_to_ods.py`                   | `data/ods/ods_xxx.csv`                     |
| DWD           | `build_dwd_order_detail.py`            | `data/dwd/dwd_order_detail.csv`            |
| DWS           | `build_dws_daily_order_summary.py`     | `data/dws/dws_daily_order_summary.csv`     |
| ADS           | `build_ads_daily_business_overview.py` | `data/ads/ads_daily_business_overview.csv` |
| Data Quality  | `run_data_quality_checks.py`           | Data quality reports / 数据质量报告              |

---

## 11. Engineering Value / 工程价值

This pipeline improves the project in several ways:

该主流程从多个方面提升了项目的工程化程度：

* It reduces manual execution work.
  减少手动执行脚本的工作量。

* It makes the ETL workflow repeatable.
  使 ETL 流程可以重复运行。

* It records execution status and runtime.
  记录执行状态和运行耗时。

* It provides logs for debugging.
  提供日志用于问题排查。

* It makes the project closer to a real enterprise data development workflow.
  使项目更加接近真实企业数据开发流程。

---

## 12. Summary / 总结

The pipeline orchestration module connects raw data profiling, ODS loading, DWD building, DWS aggregation, ADS reporting, and data quality checks.

主流程编排模块将原始数据探查、ODS 加载、DWD 构建、DWS 汇总、ADS 报表和数据质量检查连接起来。

With this module, the entire offline data warehouse can be rebuilt using one command.

通过该模块，整个离线数仓可以通过一条命令重新构建。

This is an important step for improving automation, maintainability, and portfolio quality.

这是提升自动化程度、可维护性和项目展示质量的重要一步。
