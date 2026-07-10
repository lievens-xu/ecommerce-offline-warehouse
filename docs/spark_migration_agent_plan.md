# Spark Migration Agent Plan / Spark 迁移开发规划

## 0. Goal / 目标

This document describes the remaining Spark migration tasks for the `ecommerce-offline-warehouse` project.

本文档用于规划 `ecommerce-offline-warehouse` 项目的后续 Spark 迁移工作。

The current project already has a complete Pandas-based offline data warehouse pipeline:

当前项目已经完成一条基于 Pandas 的离线数仓链路：

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

The goal of the next development phase is to add a complete Spark SQL version of the warehouse pipeline:

下一阶段目标是新增一条完整的 Spark SQL 版数仓链路：

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

Important rule:

重要规则：

> Do not modify the existing main `run_pipeline.py` and `README.md` until the full Spark migration is completed and verified.

> 在完整 Spark 迁移完成并验证之前，不要修改现有主流程 `run_pipeline.py` 和 `README.md`。

The existing Pandas pipeline should remain stable as the baseline.

现有 Pandas 主流程应保留为稳定基准线。

---

## 1. Current Project State / 当前项目状态

The project currently contains the following completed components:

当前项目已经包含以下完成内容：

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

Current completed output layers:

当前已完成输出层：

```text
data/ods/ods_xxx.csv
data/dwd/dwd_order_detail.csv
data/dws/dws_daily_order_summary.csv
data/ads/ads_daily_business_overview.csv
```

Current Spark component already created:

当前已经创建的 Spark 组件：

```text
scripts/spark_build_dws_daily_order_summary.py
```

Current Spark output already verified:

当前已经验证通过的 Spark 输出：

```text
data/dws/dws_daily_order_summary_spark.csv
docs/spark_dws_daily_order_summary_report.csv
docs/spark_dws_comparison_report.csv
```

The current Spark DWS script reads the Pandas DWD table:

当前 Spark DWS 脚本读取的是 Pandas 版 DWD 表：

```text
data/dwd/dwd_order_detail.csv
```

This is not a complete Spark migration yet.

这还不是完整 Spark 迁移。

A complete migration should build Spark DWD first, then use Spark DWD to build Spark DWS and Spark ADS.

完整迁移应先构建 Spark DWD，再基于 Spark DWD 构建 Spark DWS 和 Spark ADS。

---

## 2. Development Principles / 开发原则

Follow these principles during development:

开发过程中必须遵循以下原则：

### 2.1 Keep Pandas Pipeline Stable / 保持 Pandas 主流程稳定

Do not break existing files:

不要破坏现有文件：

```text
scripts/build_dwd_order_detail.py
scripts/build_dws_daily_order_summary.py
scripts/build_ads_daily_business_overview.py
scripts/run_data_quality_checks.py
scripts/build_dashboard_charts.py
scripts/run_pipeline.py
```

Existing Pandas outputs should continue to work as baseline data.

现有 Pandas 输出应继续作为基准数据使用。

---

### 2.2 Add Spark Scripts Separately / 单独新增 Spark 脚本

Create new Spark scripts instead of replacing existing Pandas scripts.

新增 Spark 脚本，不要直接替换现有 Pandas 脚本。

Use the following naming convention:

使用以下命名规范：

```text
scripts/spark_build_<layer_or_table>.py
```

Expected new scripts:

预期新增脚本：

```text
scripts/spark_build_dwd_order_detail.py
scripts/spark_build_ads_daily_business_overview.py
scripts/compare_pandas_spark_outputs.py
scripts/run_spark_pipeline.py
```

Modify existing Spark script if needed:

如有必要，可以修改已有 Spark 脚本：

```text
scripts/spark_build_dws_daily_order_summary.py
```

---

### 2.3 Use Spark SQL for Core Transformations / 核心转换使用 Spark SQL

The Spark migration should not only use Spark DataFrame API.

Spark 迁移不应只使用 Spark DataFrame API。

For DWD, DWS, and ADS transformations, register temporary views and execute Spark SQL.

DWD、DWS、ADS 加工应注册临时视图并执行 Spark SQL。

Example pattern:

示例模式：

```python
df.createOrReplaceTempView("ods_orders")

result_df = spark.sql("""
    SELECT ...
    FROM ods_orders
""")
```

---

### 2.4 Save Spark Outputs as Single CSV Files / Spark 输出保存为单个 CSV 文件

For local portfolio usage, Spark output should be converted to Pandas and saved as a single CSV file.

为了本地作品集展示，Spark 输出应转为 Pandas 并保存为单个 CSV 文件。

Expected output style:

预期输出形式：

```text
data/dwd/dwd_order_detail_spark.csv
data/dws/dws_daily_order_summary_spark.csv
data/ads/ads_daily_business_overview_spark.csv
```

Do not save Spark partitioned output folders such as:

不要保存 Spark 分区输出目录，例如：

```text
data/dwd/dwd_order_detail_spark/part-0000.csv
```

---

### 2.5 Generate Reports and Comparison Reports / 生成报告和对比报告

Each Spark layer should generate:

每个 Spark 分层都应生成：

```text
Spark output CSV
Spark table report
Pandas vs Spark comparison report
```

Reports should be stored under:

报告存放目录：

```text
docs/
```

---

### 2.6 Documentation Should Be Bilingual / 文档必须中英文对照

All new Markdown documents must be bilingual.

所有新增 Markdown 文档必须中英文对照。

Use this style:

使用以下风格：

```md
## Purpose / 目的

English explanation.

中文说明。
```

---

## 3. Required Tasks / 必须完成的任务

## Task 1: Build Spark DWD Order Detail / 构建 Spark 版 DWD 订单明细宽表

### 1.1 Create Script / 创建脚本

Create:

创建：

```text
scripts/spark_build_dwd_order_detail.py
```

### 1.2 Input Tables / 输入表

Read the following ODS CSV files:

读取以下 ODS CSV 文件：

```text
data/ods/ods_orders.csv
data/ods/ods_customers.csv
data/ods/ods_order_items.csv
data/ods/ods_order_payments.csv
data/ods/ods_order_reviews.csv
```

### 1.3 Output Table / 输出表

Generate:

生成：

```text
data/dwd/dwd_order_detail_spark.csv
```

### 1.4 Required Logic / 必须实现的逻辑

The Spark DWD logic should reproduce the Pandas DWD table as closely as possible.

Spark DWD 逻辑应尽量复现 Pandas DWD 表。

The output columns should match the current Pandas DWD columns:

输出字段应与当前 Pandas DWD 字段保持一致：

```text
order_id
customer_id
customer_unique_id
customer_city
customer_state
order_status
order_purchase_timestamp
purchase_date
purchase_month
order_approved_at
order_delivered_carrier_date
order_delivered_customer_date
order_estimated_delivery_date
order_item_count
product_count
seller_count
total_product_amount
total_freight_amount
total_payment_amount
payment_type_count
main_payment_type
max_payment_installments
average_review_score
review_count
has_review_comment
delivery_days
estimated_delivery_days
delivery_delay_days
is_delivered
is_late_delivery
dwd_loaded_at
dt
```

### 1.5 Processing Details / 加工细节

Implement the following transformations with Spark SQL:

使用 Spark SQL 实现以下转换：

1. Register ODS tables as temporary views.
   将 ODS 表注册为临时视图。

2. Aggregate order items to order level.
   将订单商品明细聚合到订单粒度。

   Metrics:

   指标：

   ```text
   order_item_count
   product_count
   seller_count
   total_product_amount
   total_freight_amount
   ```

3. Aggregate payments to order level.
   将支付明细聚合到订单粒度。

   Metrics:

   指标：

   ```text
   total_payment_amount
   payment_type_count
   max_payment_installments
   main_payment_type
   ```

4. Aggregate reviews to order level.
   将评价明细聚合到订单粒度。

   Metrics:

   指标：

   ```text
   average_review_score
   review_count
   has_review_comment
   ```

5. Join orders, customers, item aggregation, payment aggregation, and review aggregation.
   关联订单、客户、商品聚合、支付聚合和评价聚合。

6. Calculate date fields.
   计算日期字段。

   ```text
   purchase_date
   purchase_month
   ```

7. Calculate logistics fields.
   计算物流字段。

   ```text
   delivery_days
   estimated_delivery_days
   delivery_delay_days
   is_delivered
   is_late_delivery
   ```

8. Add technical fields.
   添加技术字段。

   ```text
   dwd_loaded_at
   dt
   ```

### 1.6 Reports / 报告

Generate:

生成：

```text
docs/spark_dwd_order_detail_report.csv
docs/spark_dwd_comparison_report.csv
```

The Spark DWD report should include:

Spark DWD 报告应包括：

```text
table_name
row_count
unique_order_count
unique_customer_count
total_payment_amount
total_product_amount
delivered_order_count
late_delivery_order_count
average_review_score
generated_at
engine
```

The comparison report should compare Pandas DWD vs Spark DWD:

对比报告应比较 Pandas DWD 与 Spark DWD：

```text
row_count
unique_order_count
unique_customer_count
total_payment_amount
total_product_amount
total_freight_amount
delivered_order_count
late_delivery_order_count
```

Comparison output:

对比输出：

```text
metric_name
pandas_value
spark_sql_value
difference
status
```

Status should be:

状态应为：

```text
PASS
FAIL
```

Use tolerance for floating point metrics:

浮点指标允许误差：

```text
0.01
```

### 1.7 Validation Command / 验证命令

Run:

运行：

```bat
python scripts\spark_build_dwd_order_detail.py
```

Expected success output:

预期成功输出：

```text
[DONE] Spark SQL DWD building completed successfully.
[DONE] Spark DWD result is consistent with Pandas DWD output.
```

---

## Task 2: Modify Spark DWS to Use Spark DWD / 修改 Spark DWS 读取 Spark DWD

### 2.1 Modify Existing Script / 修改已有脚本

Modify:

修改：

```text
scripts/spark_build_dws_daily_order_summary.py
```

### 2.2 Current Input / 当前输入

Current input is:

当前输入是：

```text
data/dwd/dwd_order_detail.csv
```

### 2.3 Required New Input / 新输入要求

Change input to:

改为读取：

```text
data/dwd/dwd_order_detail_spark.csv
```

### 2.4 Output / 输出

Keep output:

保持输出：

```text
data/dws/dws_daily_order_summary_spark.csv
```

### 2.5 Comparison / 对比

Continue comparing Spark DWS output with Pandas DWS output:

继续将 Spark DWS 输出与 Pandas DWS 输出对比：

```text
data/dws/dws_daily_order_summary.csv
```

Comparison report:

对比报告：

```text
docs/spark_dws_comparison_report.csv
```

### 2.6 Validation Command / 验证命令

Run:

运行：

```bat
python scripts\spark_build_dws_daily_order_summary.py
```

Expected success output:

预期成功输出：

```text
[DONE] Spark SQL result is consistent with Pandas DWS output.
[DONE] Spark SQL DWS building completed successfully.
```

---

## Task 3: Build Spark ADS Daily Business Overview / 构建 Spark 版 ADS 每日经营看板表

### 3.1 Create Script / 创建脚本

Create:

创建：

```text
scripts/spark_build_ads_daily_business_overview.py
```

### 3.2 Input Table / 输入表

Read:

读取：

```text
data/dws/dws_daily_order_summary_spark.csv
```

### 3.3 Output Table / 输出表

Generate:

生成：

```text
data/ads/ads_daily_business_overview_spark.csv
```

### 3.4 Required Columns / 必须输出字段

The output columns should match the Pandas ADS table:

输出字段应与 Pandas ADS 表一致：

```text
stat_date
stat_month
daily_order_count
daily_valid_order_count
daily_paid_order_count
daily_unique_customer_count
daily_gmv
daily_product_amount
daily_freight_amount
daily_aov
daily_delivery_rate
daily_late_delivery_rate
daily_review_rate
daily_review_comment_rate
daily_average_review_score
valid_order_rate
paid_order_rate
gmv_7d_moving_avg
order_count_7d_moving_avg
aov_7d_moving_avg
cumulative_gmv
cumulative_order_count
cumulative_customer_count
gmv_day_over_day_change
order_count_day_over_day_change
gmv_day_over_day_rate
order_count_day_over_day_rate
ads_loaded_at
dt
```

### 3.5 Required Logic / 必须实现逻辑

Implement with Spark SQL:

使用 Spark SQL 实现：

1. Register Spark DWS table as temporary view.
   注册 Spark DWS 表为临时视图。

2. Rename DWS fields into ADS dashboard field names.
   将 DWS 字段转换为 ADS 看板字段名。

3. Calculate valid order rate.
   计算有效订单率。

4. Calculate paid order rate.
   计算支付订单率。

5. Calculate 7-day moving averages.
   计算 7 日移动平均。

   Use Spark SQL window functions:

   使用 Spark SQL 窗口函数：

   ```sql
   AVG(daily_gmv) OVER (
       ORDER BY stat_date
       ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
   )
   ```

6. Calculate cumulative metrics.
   计算累计指标。

   Use Spark SQL window functions:

   使用 Spark SQL 窗口函数：

   ```sql
   SUM(daily_gmv) OVER (
       ORDER BY stat_date
       ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
   )
   ```

7. Calculate day-over-day changes.
   计算日环比变化。

   Use `LAG()`:

   使用 `LAG()`：

   ```sql
   LAG(daily_gmv) OVER (ORDER BY stat_date)
   ```

8. Add technical fields.
   添加技术字段。

   ```text
   ads_loaded_at
   dt
   ```

### 3.6 Reports / 报告

Generate:

生成：

```text
docs/spark_ads_daily_business_overview_report.csv
docs/spark_ads_comparison_report.csv
```

Spark ADS report should include:

Spark ADS 报告应包括：

```text
table_name
row_count
start_date
end_date
total_order_count
total_gmv
average_daily_gmv
average_daily_order_count
overall_aov
latest_stat_date
latest_daily_gmv
generated_at
engine
```

Comparison report should compare:

对比报告应比较：

```text
data/ads/ads_daily_business_overview.csv
data/ads/ads_daily_business_overview_spark.csv
```

Comparison metrics:

对比指标：

```text
row_count
total_order_count
total_gmv
latest_daily_gmv
latest_daily_order_count
overall_aov
```

### 3.7 Validation Command / 验证命令

Run:

运行：

```bat
python scripts\spark_build_ads_daily_business_overview.py
```

Expected success output:

预期成功输出：

```text
[DONE] Spark ADS result is consistent with Pandas ADS output.
[DONE] Spark SQL ADS building completed successfully.
```

---

## Task 4: Build Unified Pandas vs Spark Comparison Script / 构建统一对比脚本

### 4.1 Create Script / 创建脚本

Create:

创建：

```text
scripts/compare_pandas_spark_outputs.py
```

### 4.2 Purpose / 目的

This script should compare all major Pandas outputs and Spark outputs in one place.

该脚本用于统一对比所有主要 Pandas 输出和 Spark 输出。

### 4.3 Input Pairs / 输入对

Compare the following pairs:

对比以下文件对：

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

### 4.4 Output Reports / 输出报告

Generate:

生成：

```text
docs/pandas_spark_full_comparison_report.csv
docs/pandas_spark_full_comparison_summary.md
```

### 4.5 Report Design / 报告设计

The CSV report should contain:

CSV 报告应包含：

```text
layer
metric_name
pandas_value
spark_sql_value
difference
tolerance
status
message
```

The Markdown summary should be bilingual:

Markdown 总结应中英文对照。

It should include:

应包含：

```text
total_checks
passed_checks
failed_checks
layer-level summary
failed check details
```

### 4.6 Required Metrics / 必须对比指标

DWD metrics:

DWD 指标：

```text
row_count
unique_order_count
unique_customer_count
total_payment_amount
total_product_amount
total_freight_amount
delivered_order_count
late_delivery_order_count
```

DWS metrics:

DWS 指标：

```text
row_count
total_order_count
total_valid_order_count
total_payment_amount
total_product_amount
total_freight_amount
overall_aov
```

ADS metrics:

ADS 指标：

```text
row_count
total_order_count
total_gmv
average_daily_gmv
overall_aov
latest_daily_gmv
latest_daily_order_count
```

### 4.7 Validation Command / 验证命令

Run:

运行：

```bat
python scripts\compare_pandas_spark_outputs.py
```

Expected success output:

预期成功输出：

```text
[DONE] All Pandas vs Spark comparison checks passed.
```

---

## Task 5: Build Spark Pipeline / 构建 Spark 版一键流程

### 5.1 Create Script / 创建脚本

Create:

创建：

```text
scripts/run_spark_pipeline.py
```

### 5.2 Purpose / 目的

This script should run the Spark migration pipeline only.

该脚本只运行 Spark 迁移版流程。

It should not replace the existing `run_pipeline.py`.

它不应替换现有 `run_pipeline.py`。

### 5.3 Pipeline Steps / 流程步骤

The Spark pipeline should run the following steps:

Spark 版主流程应执行以下步骤：

```text
1. spark_build_dwd_order_detail.py
2. spark_build_dws_daily_order_summary.py
3. spark_build_ads_daily_business_overview.py
4. compare_pandas_spark_outputs.py
```

### 5.4 Output Reports / 输出报告

Generate:

生成：

```text
docs/spark_pipeline_run_report.csv
docs/spark_pipeline_latest_run.log
docs/spark_pipeline_run_summary.md
```

### 5.5 Behavior / 行为要求

The Spark pipeline should behave like the existing Pandas pipeline:

Spark 版主流程行为应参考现有 Pandas 主流程：

1. Run steps sequentially.
   按顺序运行步骤。

2. Stop if one step fails.
   某一步失败则停止后续步骤。

3. Mark later steps as `SKIPPED`.
   后续步骤标记为 `SKIPPED`。

4. Save report and log files.
   保存运行报告和日志文件。

5. Generate bilingual Markdown summary.
   生成中英文对照 Markdown 总结。

### 5.6 Validation Command / 验证命令

Run:

运行：

```bat
python scripts\run_spark_pipeline.py
```

Expected success output:

预期成功输出：

```text
[DONE] Spark pipeline completed successfully.
```

---

## Task 6: Create Spark Migration Documentation / 创建 Spark 迁移文档

### 6.1 Create or Update Document / 创建或更新文档

Create or update:

创建或更新：

```text
docs/spark_sql_migration.md
```

### 6.2 Documentation Requirements / 文档要求

The document must be bilingual.

文档必须中英文对照。

It should include:

应包含：

```text
1. Purpose / 目的
2. Background / 背景
3. Spark Migration Scope / Spark 迁移范围
4. Spark DWD Design / Spark DWD 设计
5. Spark DWS Design / Spark DWS 设计
6. Spark ADS Design / Spark ADS 设计
7. Pandas vs Spark Comparison / Pandas 与 Spark 对比
8. Spark Pipeline / Spark 版主流程
9. How to Run / 如何运行
10. Output Files / 输出文件
11. Project Value / 项目价值
12. Future Improvements / 后续优化
```

### 6.3 Mention Windows Warnings / 说明 Windows 警告

Document that the following warnings may appear on Windows and can usually be ignored for local CSV processing:

说明 Windows 本地运行 Spark 时可能出现以下警告，本项目读取 CSV 时通常可以忽略：

```text
Did not find winutils.exe
HADOOP_HOME and hadoop.home.dir are unset
Unable to load native-hadoop library
```

---

## Task 7: Final Integration After Spark Migration / Spark 迁移完成后的最终集成

Only perform this task after Tasks 1-6 are completed and verified.

只有在任务 1-6 完成并验证通过后，才执行本任务。

### 7.1 Update Existing Main Pipeline / 更新现有主流程

After Spark migration is stable, decide whether to update:

Spark 迁移稳定后，再决定是否更新：

```text
scripts/run_pipeline.py
```

Recommended final approach:

推荐最终方案：

Keep `run_pipeline.py` as the Pandas baseline pipeline.

保留 `run_pipeline.py` 作为 Pandas 基准流程。

Keep `run_spark_pipeline.py` as the Spark migration pipeline.

保留 `run_spark_pipeline.py` 作为 Spark 迁移流程。

Do not merge them unless explicitly required.

除非明确需要，否则不要合并两个流程。

### 7.2 Update README / 更新 README

Update `README.md` only after full Spark migration is complete.

完整 Spark 迁移完成后再更新 `README.md`。

README should include:

README 应包含：

```text
1. Current implementation includes Pandas and PySpark/Spark SQL.
2. Pandas pipeline is the baseline local pipeline.
3. Spark pipeline is the big-data-style migration pipeline.
4. Spark DWD, DWS, and ADS outputs are compared with Pandas outputs.
5. Spark pipeline can be run with python scripts/run_spark_pipeline.py.
```

### 7.3 Update Technology Stack / 更新技术栈

Add:

添加：

```text
PySpark
Spark SQL
Java 17
```

### 7.4 Update Project Highlights / 更新项目亮点

Add a Spark migration highlight:

增加 Spark 迁移项目亮点：

```text
Implemented a Spark SQL migration path for the offline data warehouse, rebuilding DWD, DWS, and ADS layers with PySpark and Spark SQL, and validating the results against the original Pandas pipeline through automated comparison reports.
```

中文版本：

```text
实现离线数仓的 Spark SQL 迁移路径，使用 PySpark 和 Spark SQL 重构 DWD、DWS、ADS 分层，并通过自动化对比报告校验 Spark 输出与原 Pandas 主流程结果的一致性。
```

---

## 4. Expected Final File Structure / 预期最终文件结构

After all tasks are completed, the following files should exist:

所有任务完成后，应存在以下文件：

```text
scripts/
├── spark_build_dwd_order_detail.py
├── spark_build_dws_daily_order_summary.py
├── spark_build_ads_daily_business_overview.py
├── compare_pandas_spark_outputs.py
└── run_spark_pipeline.py

data/
├── dwd/
│   └── dwd_order_detail_spark.csv
├── dws/
│   └── dws_daily_order_summary_spark.csv
└── ads/
    └── ads_daily_business_overview_spark.csv

docs/
├── spark_dwd_order_detail_report.csv
├── spark_dwd_comparison_report.csv
├── spark_dws_daily_order_summary_report.csv
├── spark_dws_comparison_report.csv
├── spark_ads_daily_business_overview_report.csv
├── spark_ads_comparison_report.csv
├── pandas_spark_full_comparison_report.csv
├── pandas_spark_full_comparison_summary.md
├── spark_pipeline_run_report.csv
├── spark_pipeline_run_summary.md
└── spark_sql_migration.md
```

Note:

说明：

Data files under `data/` are ignored by Git and should not be committed.

`data/` 下的数据文件被 Git 忽略，不应提交。

Scripts and documentation should be committed.

脚本和文档应提交。

---

## 5. Environment Requirements / 环境要求

The local environment should satisfy:

本地环境应满足：

```text
Python virtual environment is activated.
Java 17 is installed and available.
PySpark is installed.
```

Check Java:

检查 Java：

```bat
java -version
```

Expected:

预期：

```text
openjdk version "17.x.x"
```

Install dependencies:

安装依赖：

```bat
pip install -r requirements.txt
```

`requirements.txt` should include:

`requirements.txt` 应包含：

```text
pyspark
```

---

## 6. Testing Order / 测试顺序

Run tests in this order:

按以下顺序测试：

```bat
python scripts\spark_build_dwd_order_detail.py
python scripts\spark_build_dws_daily_order_summary.py
python scripts\spark_build_ads_daily_business_overview.py
python scripts\compare_pandas_spark_outputs.py
python scripts\run_spark_pipeline.py
```

All commands should complete successfully.

所有命令都应成功运行。

Expected final result:

最终预期结果：

```text
All Spark layer outputs are generated.
All Pandas vs Spark comparison checks pass.
Spark pipeline completes successfully.
```

---

## 7. Commit Strategy / 提交策略

After successful validation, commit changes:

验证成功后提交：

```bat
git status
git add .
git commit -m "Complete Spark SQL migration pipeline"
git push
```

Before committing, ensure that real data files are not tracked.

提交前确认真实数据文件没有被 Git 跟踪。

Check:

检查：

```bat
git status
```

Should not include:

不应包含：

```text
data/dwd/dwd_order_detail_spark.csv
data/dws/dws_daily_order_summary_spark.csv
data/ads/ads_daily_business_overview_spark.csv
```

These files are generated outputs and should remain ignored by `.gitignore`.

这些文件是生成结果，应继续被 `.gitignore` 忽略。

---

## 8. Final Acceptance Criteria / 最终验收标准

The Spark migration is complete only when all of the following are true:

只有满足以下条件，才算 Spark 迁移完成：

```text
1. spark_build_dwd_order_detail.py runs successfully.
2. spark_build_dws_daily_order_summary.py reads Spark DWD output and runs successfully.
3. spark_build_ads_daily_business_overview.py runs successfully.
4. compare_pandas_spark_outputs.py reports all checks passed.
5. run_spark_pipeline.py runs all Spark steps successfully.
6. docs/spark_sql_migration.md is complete and bilingual.
7. README.md is updated after Spark migration is verified.
8. Existing Pandas pipeline still works.
9. No generated data files under data/ are committed to Git.
```

Chinese version:

中文验收标准：

```text
1. spark_build_dwd_order_detail.py 能成功运行。
2. spark_build_dws_daily_order_summary.py 已改为读取 Spark DWD 输出，并能成功运行。
3. spark_build_ads_daily_business_overview.py 能成功运行。
4. compare_pandas_spark_outputs.py 显示所有对比检查通过。
5. run_spark_pipeline.py 能成功跑完整个 Spark 迁移流程。
6. docs/spark_sql_migration.md 完整且中英文对照。
7. README.md 在 Spark 迁移验证完成后再更新。
8. 原 Pandas 主流程仍然可运行。
9. data/ 目录下的生成数据文件没有被提交到 Git。
```
