# AGENTS.md

## Project Name / 项目名称

`ecommerce-offline-warehouse`

This is a portfolio-level e-commerce offline data warehouse project.

这是一个用于求职展示的电商离线数仓项目。

The target job direction is:

目标岗位方向：

* Data Warehouse Developer / 数仓开发
* Data Developer / 数据开发
* Junior Big Data Developer / 初级大数据开发
* Data Analyst with data engineering ability / 具备数据工程能力的数据分析岗位

---

## Project Goal / 项目目标

The project simulates a complete offline data warehouse workflow based on the Olist e-commerce dataset.

本项目基于 Olist 电商数据集，模拟完整的离线数仓开发流程。

The current completed baseline pipeline is implemented with Python and Pandas.

当前已完成的基准流程使用 Python 和 Pandas 实现。

Current baseline architecture:

当前基准架构：

```text
Raw CSV
  ↓
ODS
  ↓
DWD
  ↓
DWS
  ↓
ADS
  ↓
Data Quality Checks
  ↓
Dashboard Charts
```

The next development goal is to complete a Spark SQL migration.

下一阶段目标是完成 Spark SQL 迁移。

Spark migration target architecture:

Spark 迁移目标架构：

```text
ODS CSV
  ↓
Spark DWD
  ↓
Spark DWS
  ↓
Spark ADS
  ↓
Pandas vs Spark Comparison
  ↓
Spark Pipeline
```

---

## Important Working Rule / 重要工作规则

Do not directly modify the existing Pandas baseline pipeline unless explicitly requested.

除非明确要求，不要直接修改现有 Pandas 基准主流程。

Do not modify the following files during the first Spark migration stage:

第一阶段 Spark 迁移过程中，不要修改以下文件：

```text
README.md
scripts/run_pipeline.py
```

The reason is that the Spark migration should be completed and verified first.

原因是应先完整完成并验证 Spark 迁移，再统一更新主流程和 README。

---

## Existing Pandas Baseline Scripts / 现有 Pandas 基准脚本

The following scripts already form a complete local offline data warehouse pipeline:

以下脚本已经组成完整的本地离线数仓流程：

```text
scripts/check_raw_data.py
scripts/load_raw_to_ods.py
scripts/build_dwd_order_detail.py
scripts/build_dws_daily_order_summary.py
scripts/build_ads_daily_business_overview.py
scripts/run_data_quality_checks.py
scripts/build_dashboard_charts.py
scripts/run_pipeline.py
```

These files should be treated as the stable baseline.

这些文件应视为稳定基准线。

---

## Existing Data Layers / 现有数据分层

Current generated outputs:

当前已生成输出：

```text
data/ods/ods_customers.csv
data/ods/ods_orders.csv
data/ods/ods_order_items.csv
data/ods/ods_order_payments.csv
data/ods/ods_order_reviews.csv
data/ods/ods_products.csv
data/ods/ods_sellers.csv
data/ods/ods_geolocation.csv
data/ods/ods_product_category_translation.csv

data/dwd/dwd_order_detail.csv
data/dws/dws_daily_order_summary.csv
data/ads/ads_daily_business_overview.csv
```

Files under `data/` are generated data files and should not be committed to Git.

`data/` 下的文件是生成数据，不应提交到 Git。

---

## Existing Spark Work / 已完成 Spark 工作

The following Spark script has already been created and successfully tested:

以下 Spark 脚本已经创建并成功测试：

```text
scripts/spark_build_dws_daily_order_summary.py
```

It currently reads:

当前读取：

```text
data/dwd/dwd_order_detail.csv
```

It outputs:

当前输出：

```text
data/dws/dws_daily_order_summary_spark.csv
docs/spark_dws_daily_order_summary_report.csv
docs/spark_dws_comparison_report.csv
```

Important note:

重要说明：

This is not a complete Spark migration yet because Spark DWS currently depends on Pandas DWD.

这还不是完整 Spark 迁移，因为 Spark DWS 目前依赖 Pandas DWD。

The next goal is to build Spark DWD first, then make Spark DWS read Spark DWD.

下一步目标是先构建 Spark DWD，然后让 Spark DWS 读取 Spark DWD。

---

## Required Spark Migration Tasks / 必须完成的 Spark 迁移任务

Please follow this order:

请严格按以下顺序执行：

### Task 1: Create Spark DWD

Create:

```text
scripts/spark_build_dwd_order_detail.py
```

Input:

```text
data/ods/ods_orders.csv
data/ods/ods_customers.csv
data/ods/ods_order_items.csv
data/ods/ods_order_payments.csv
data/ods/ods_order_reviews.csv
```

Output:

```text
data/dwd/dwd_order_detail_spark.csv
docs/spark_dwd_order_detail_report.csv
docs/spark_dwd_comparison_report.csv
```

The Spark DWD output should match the Pandas DWD output as closely as possible.

Spark DWD 输出应尽量与 Pandas DWD 输出一致。

Compare with:

```text
data/dwd/dwd_order_detail.csv
```

---

### Task 2: Modify Spark DWS

Modify:

```text
scripts/spark_build_dws_daily_order_summary.py
```

Change input from:

```text
data/dwd/dwd_order_detail.csv
```

To:

```text
data/dwd/dwd_order_detail_spark.csv
```

Keep output:

```text
data/dws/dws_daily_order_summary_spark.csv
docs/spark_dws_daily_order_summary_report.csv
docs/spark_dws_comparison_report.csv
```

Compare with:

```text
data/dws/dws_daily_order_summary.csv
```

---

### Task 3: Create Spark ADS

Create:

```text
scripts/spark_build_ads_daily_business_overview.py
```

Input:

```text
data/dws/dws_daily_order_summary_spark.csv
```

Output:

```text
data/ads/ads_daily_business_overview_spark.csv
docs/spark_ads_daily_business_overview_report.csv
docs/spark_ads_comparison_report.csv
```

Compare with:

```text
data/ads/ads_daily_business_overview.csv
```

---

### Task 4: Create Unified Comparison Script

Create:

```text
scripts/compare_pandas_spark_outputs.py
```

It should compare:

```text
DWD:
data/dwd/dwd_order_detail.csv
data/dwd/dwd_order_detail_spark.csv

DWS:
data/dws/dws_daily_order_summary.csv
data/dws/dws_daily_order_summary_spark.csv

ADS:
data/ads/ads_daily_business_overview.csv
data/ads/ads_daily_business_overview_spark.csv
```

Output:

```text
docs/pandas_spark_full_comparison_report.csv
docs/pandas_spark_full_comparison_summary.md
```

---

### Task 5: Create Spark Pipeline

Create:

```text
scripts/run_spark_pipeline.py
```

It should run:

```text
1. spark_build_dwd_order_detail.py
2. spark_build_dws_daily_order_summary.py
3. spark_build_ads_daily_business_overview.py
4. compare_pandas_spark_outputs.py
```

Output:

```text
docs/spark_pipeline_run_report.csv
docs/spark_pipeline_latest_run.log
docs/spark_pipeline_run_summary.md
```

Do not replace the existing `scripts/run_pipeline.py`.

不要替换现有 `scripts/run_pipeline.py`。

---

## Coding Requirements / 代码要求

Use PySpark and Spark SQL.

使用 PySpark 和 Spark SQL。

For core DWD, DWS, and ADS transformations, register temporary views and execute SQL through:

核心 DWD、DWS、ADS 转换应注册临时视图，并使用以下方式执行 SQL：

```python
spark.sql("""
    SELECT ...
""")
```

Do not only use Pandas.

不要只使用 Pandas。

It is acceptable to convert the final Spark result to Pandas only for saving a single CSV file.

允许仅在最终保存单个 CSV 文件时将 Spark 结果转为 Pandas。

---

## Documentation Requirements / 文档要求

All new Markdown documents must be bilingual.

所有新增 Markdown 文档必须中英文对照。

Use this format:

```markdown
## Purpose / 目的

English explanation.

中文说明。
```

---

## Environment / 环境

The project is developed on Windows.

项目运行在 Windows 环境。

Java 17 is installed.

已安装 Java 17。

PySpark is installed in the project virtual environment.

PySpark 已安装在项目虚拟环境中。

Windows Spark warnings such as the following can usually be ignored for local CSV processing:

Windows 本地运行 Spark 时，以下警告通常可以忽略：

```text
Did not find winutils.exe
HADOOP_HOME and hadoop.home.dir are unset
Unable to load native-hadoop library
```

---

## Validation Commands / 验证命令

Run these commands after implementation:

实现后运行以下命令：

```bat
python scripts\spark_build_dwd_order_detail.py
python scripts\spark_build_dws_daily_order_summary.py
python scripts\spark_build_ads_daily_business_overview.py
python scripts\compare_pandas_spark_outputs.py
python scripts\run_spark_pipeline.py
```

Expected final result:

预期最终结果：

```text
All Spark layer outputs are generated.
All Pandas vs Spark comparison checks pass.
Spark pipeline completes successfully.
```

---

## Git Rule / Git 规则

Do not commit generated data files under:

不要提交以下目录下的生成数据文件：

```text
data/
```

Scripts and documentation should be committed.

脚本和文档可以提交。

Before committing, run:

提交前运行：

```bat
git status
```

Make sure generated data files are not tracked.

确认生成数据文件没有被跟踪。

---

## Final Acceptance Criteria / 最终验收标准

The Spark migration is complete only when:

只有满足以下条件，Spark 迁移才算完成：

```text
1. Spark DWD script runs successfully.
2. Spark DWS reads Spark DWD and runs successfully.
3. Spark ADS script runs successfully.
4. Unified Pandas vs Spark comparison passes.
5. Spark pipeline runs successfully.
6. Existing Pandas pipeline remains unchanged.
7. README.md is not modified until Spark migration is fully verified.
8. scripts/run_pipeline.py is not modified until Spark migration is fully verified.
```
