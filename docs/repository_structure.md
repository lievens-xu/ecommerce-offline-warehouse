# Repository Structure / 仓库目录结构

## 1. Purpose / 目的

This document describes which files and folders are included in the GitHub repository and which files are excluded.

本文档说明 GitHub 仓库中包含哪些文件和目录，以及哪些文件不会上传。

The goal is to keep the repository clean, lightweight, and suitable for portfolio presentation.

目标是保持仓库整洁、轻量，并适合作为作品集项目展示。

---

## 2. Included Files / 上传的文件

The following files and folders should be committed to GitHub.

以下文件和目录应提交到 GitHub。

| Path / 路径          | Description / 说明                                                       |
| ------------------ | ---------------------------------------------------------------------- |
| `README.md`        | Main project documentation / 项目主说明文档                                   |
| `requirements.txt` | Python dependency list / Python 依赖列表                                   |
| `.gitignore`       | Git ignore rules / Git 忽略规则                                            |
| `scripts/`         | ETL, data quality, pipeline, and dashboard scripts / ETL、数据质量、主流程和看板脚本 |
| `sql/`             | Hive-style table creation SQL files / Hive 风格建表 SQL 文件                 |
| `docs/`            | Design documents and generated reports / 设计文档和生成报告                     |
| `dashboard/`       | Generated dashboard charts and KPI summary / 生成的看板图表和 KPI 汇总           |
| `data/*/.gitkeep`  | Empty folder placeholders / 空目录占位文件                                    |

---

## 3. Excluded Files / 不上传的文件

The following files and folders should not be committed to GitHub.

以下文件和目录不应提交到 GitHub。

| Path / 路径      | Reason / 原因                                       |
| -------------- | ------------------------------------------------- |
| `data/raw/*`   | Raw dataset files may be large / 原始数据文件可能较大       |
| `data/ods/*`   | Generated ODS intermediate data / 生成的 ODS 中间数据    |
| `data/dwd/*`   | Generated DWD intermediate data / 生成的 DWD 中间数据    |
| `data/dws/*`   | Generated DWS intermediate data / 生成的 DWS 中间数据    |
| `data/ads/*`   | Generated ADS intermediate data / 生成的 ADS 中间数据    |
| `.venv/`       | Local Python virtual environment / 本地 Python 虚拟环境 |
| `__pycache__/` | Python cache files / Python 缓存文件                  |
| `*.log`        | Runtime log files / 运行日志文件                        |
| `.env`         | Local environment variables / 本地环境变量文件            |

---

## 4. Data Folder Strategy / 数据目录策略

The repository keeps the `data/` folder structure but excludes actual data files.

仓库会保留 `data/` 目录结构，但不会上传真实数据文件。

This is implemented by using `.gitkeep` files.

该策略通过 `.gitkeep` 文件实现。

Expected data folder structure:

预期数据目录结构：

```
data/
├── raw/
│   └── .gitkeep
├── ods/
│   └── .gitkeep
├── dwd/
│   └── .gitkeep
├── dws/
│   └── .gitkeep
└── ads/
    └── .gitkeep
```

Users should download the dataset separately and place CSV files under:

使用者需要单独下载数据集，并将 CSV 文件放入：

```
data/raw/
```

---

## 5. Dashboard Files / 看板文件

Dashboard image files are included in the repository.

看板图片文件会上传到仓库。

Reason:

原因：

* They show the final output of the data warehouse project.
  它们展示了数仓项目的最终产出。

* They make the GitHub repository more visual.
  它们让 GitHub 仓库展示效果更直观。

* They are useful for resume and interview presentation.
  它们适合用于简历和面试展示。

Included dashboard files:

上传的看板文件包括：

```
dashboard/gmv_trend.png
dashboard/order_count_trend.png
dashboard/aov_trend.png
dashboard/cumulative_business_trend.png
dashboard/delivery_performance.png
dashboard/review_performance.png
dashboard/day_over_day_growth.png
dashboard/dashboard_kpi_summary.csv
dashboard/dashboard_readme.md
```

---

## 6. Generated Reports / 生成报告

Generated report files under `docs/` are included because they demonstrate data profiling, data quality checks, and pipeline execution results.

`docs/` 目录下的生成报告会上传，因为它们可以展示数据探查、数据质量检查和主流程运行结果。

Examples:

示例：

```
docs/raw_data_profile.md
docs/ods_load_report.csv
docs/dwd_order_detail_report.csv
docs/dws_daily_order_summary_report.csv
docs/ads_daily_business_overview_report.csv
docs/data_quality_check_report.csv
docs/data_quality_check_summary.md
docs/pipeline_run_report.csv
docs/pipeline_run_summary.md
```

Runtime log files are excluded because they may change frequently.

运行日志文件不会上传，因为它们变化频繁。

Example:

示例：

```
docs/pipeline_latest_run.log
```

---

## 7. Summary / 总结

This repository is designed to include source code, SQL files, documentation, generated reports, and dashboard outputs.

本仓库设计为包含源代码、SQL 文件、项目文档、生成报告和看板输出。

Large raw and intermediate data files are excluded to keep the repository clean and lightweight.

大型原始数据和中间数据文件不会上传，以保持仓库清晰和轻量。

This makes the project easier to review on GitHub and easier to explain in interviews.

这使项目更容易在 GitHub 上查看，也更适合在面试中讲解。
