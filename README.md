# E-commerce Offline Data Warehouse / 电商离线数仓项目

![CI](https://github.com/lievens-xu/ecommerce-offline-warehouse/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Engines](https://img.shields.io/badge/engines-Pandas%20%7C%20Spark%20SQL%20%7C%20dbt-orange)
![License](https://img.shields.io/badge/license-MIT-green)

> Raw → ODS → DWD → DWS → ADS → Analysis (RFM · Category · Geo) → DQ → BI.
> Implemented in **Pandas**, migrated to **Spark SQL**, and modeled in **PostgreSQL + dbt**,
> with an interactive HTML dashboard, unit tests, and CI.
>
> 完整离线数仓分层 + 业务分析层，三套引擎（Pandas / Spark SQL / dbt）实现，
> 含交互式 HTML 看板、单元测试与 CI。

### Dashboard Preview / 看板预览

Open [`dashboard/index.html`](dashboard/index.html) in a browser (self-contained,
interactive). Static analysis charts:

浏览器打开 [`dashboard/index.html`](dashboard/index.html)（自包含、可交互）。静态分析图表：

| RFM Segments | Category Pareto | Top States |
|---|---|---|
| ![RFM](dashboard/rfm_segment_customers.png) | ![Pareto](dashboard/product_category_pareto.png) | ![States](dashboard/geo_top_states_gmv.png) |

---

## 1. Project Overview / 项目概述

This project is an offline data warehouse project built on the Brazilian E-Commerce public dataset by Olist.

本项目是一个基于 Olist 巴西电商公开数据集构建的离线数仓项目。

The project simulates a typical enterprise data warehouse workflow, including raw data profiling, ODS loading, DWD detail table construction, DWS summary table construction, ADS dashboard-ready table construction, data quality checks, and pipeline orchestration.

本项目模拟企业中常见的数据仓库开发流程，包括原始数据探查、ODS 原始层加载、DWD 明细层构建、DWS 汇总层构建、ADS 应用层构建、数据质量检查和主流程编排。

The main goal is to build a complete and explainable data development project for data warehouse developer, data engineer, BI developer, and data analyst roles.

项目主要目标是构建一个完整、可解释、适合求职展示的数据开发项目，适用于数仓开发、数据开发、BI 开发和数据分析相关岗位。

The project now includes **two parallel pipelines**:

项目现在包含**两条并行的主流程**：

| Pipeline / 主流程 | Engine / 引擎 | Purpose / 目的 |
|---|---|---|
| **Pandas baseline pipeline** / Pandas 基准主流程 | Python + Pandas | Local prototype, stable baseline / 本地原型、稳定基准 |
| **Spark SQL migration pipeline** / Spark SQL 迁移主流程 | PySpark + Spark SQL | Big-data-style migration, validation against baseline / 大数据风格迁移、基准校验 |

On top of the pipelines the project adds a **business-analysis layer** (RFM,
product-category Pareto, geography), a **test suite + CI**, and **architecture
diagrams**, making it an end-to-end portfolio project.

在主流程之上，项目还增加了 **业务分析层**（RFM、商品类目帕累托、地域）、
**测试套件 + CI** 与 **架构图**，使其成为端到端的作品集项目。

---

## Highlights & Quick Links / 项目亮点与快速导航

| Area / 方面 | Highlight / 亮点 | Link / 链接 |
|---|---|---|
| Architecture / 架构 | Layered warehouse + multi-engine (Pandas/Spark/dbt) diagrams / 分层数仓 + 多引擎图示 | [`docs/architecture.md`](docs/architecture.md) |
| Business analysis / 业务分析 | RFM segmentation, category Pareto, geographic concentration / RFM 分层、类目帕累托、地域集中度 | [`docs/business_insights.md`](docs/business_insights.md) |
| Data quality / 数据质量 | Cross-layer checks + dbt schema tests / 跨层校验 + dbt 测试 | [`docs/data_quality_checks.md`](docs/data_quality_checks.md) |
| Engineering / 工程 | `pytest` unit tests + GitHub Actions CI (ruff) / 单元测试 + CI | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) |
| Migration / 迁移 | Pandas → Spark SQL (23 checks pass) → PostgreSQL + dbt / 三套引擎一致性校验 | [`docs/spark_sql_migration.md`](docs/spark_sql_migration.md) |

**Headline KPIs / 核心指标** (2016-09 ~ 2018-10): GMV **R$ 16.0M** · Orders
**99,441** · Customers **96,096** · AOV **R$ 161** · Delivery rate **93.1%** ·
Avg review **4.09/5**.

---

## 2. Business Scenario / 业务场景

The dataset contains e-commerce business data, including customers, orders, order items, payments, reviews, products, sellers, and geolocation information.

该数据集包含电商业务数据，包括客户、订单、订单商品、支付、评价、商品、卖家和地理位置信息。

Based on these data sources, this project builds business metrics such as GMV, order count, average order value, customer count, delivery rate, late delivery rate, review rate, and review score.

基于这些数据源，本项目构建 GMV、订单数、客单价、客户数、送达率、物流延迟率、评价率和评价分数等经营分析指标。

---

## 3. Technology Stack / 技术栈

**Current implementation:**

当前实现使用：

| Category / 类别                 | Tools / 工具           |
| ----------------------------- | -------------------- |
| Programming Language / 编程语言   | Python               |
| Data Processing / 数据处理        | Pandas, PySpark      |
| SQL Engine / SQL 引擎           | Spark SQL            |
| Data Storage / 数据存储           | CSV files            |
| Warehouse Modeling / 数仓建模     | ODS, DWD, DWS, ADS   |
| Data Quality / 数据质量           | Custom Python checks |
| Pipeline Orchestration / 流程编排 | Python subprocess    |
| Documentation / 项目文档          | Markdown             |
| Version Control / 版本控制        | Git                  |
| Runtime Environment / 运行环境     | Java 17 (for Spark)  |

**Planned extensions:**

后续可扩展方向：

| Category / 类别                  | Tools / 工具                   |
| ------------------------------ | ---------------------------- |
| Big Data SQL / 大数据 SQL         | Hive SQL, Spark SQL          |
| Distributed Processing / 分布式计算 | PySpark                      |
| Workflow Scheduling / 工作流调度    | Airflow                      |
| OLAP / 分析型数据库                  | ClickHouse, PostgreSQL       |
| BI Dashboard / BI 看板           | Power BI, Superset, Metabase |

---

## 4. Data Warehouse Architecture / 数仓架构

The project follows a typical offline data warehouse layered architecture.

本项目采用典型的离线数仓分层架构。

### 4.1 Pandas Baseline Pipeline / Pandas 基准主流程

```
Raw CSV Files
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
Reports and Dashboard
```

Chinese explanation:

中文说明：

```
原始 CSV 文件
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
报告与看板展示
```

### 4.2 Spark SQL Migration Pipeline / Spark SQL 迁移主流程

```
ODS CSV Files (from Pandas baseline)
    ↓
Spark DWD Order Detail
    ↓
Spark DWS Daily Order Summary
    ↓
Spark ADS Daily Business Overview
    ↓
Pandas vs Spark Full Comparison
    ↓
Spark Pipeline Orchestration
```

Chinese explanation:

中文说明：

```
ODS CSV 文件 (来自 Pandas 基准)
    ↓
Spark DWD 订单明细层
    ↓
Spark DWS 每日订单汇总层
    ↓
Spark ADS 每日经营概览层
    ↓
Pandas 与 Spark 全量对比
    ↓
Spark 一键主流程
```

**Important note / 重要说明:**

The Spark migration reuses ODS CSV files generated by the Pandas baseline pipeline.

Spark 迁移复用 Pandas 基准主流程生成的 ODS CSV 文件。

ODS layer is still generated by Pandas, while DWD/DWS/ADS are migrated to Spark SQL.

ODS 层仍由 Pandas 生成，而 DWD/DWS/ADS 已迁移至 Spark SQL。

This reflects how data teams migrate local prototypes to scalable processing.

这反映了数据团队如何将本地原型迁移到可扩展处理方案。

---

## 5. Layer Design / 分层设计

### 5.1 Raw Layer / 原始数据层

The Raw layer stores original CSV files downloaded from the data source.

Raw 层用于存放从数据源下载的原始 CSV 文件。

Path:

路径：

```
data/raw/
```

Expected files:

预期文件：

| Source File / 原始文件                      | Description / 说明                            |
| --------------------------------------- | ------------------------------------------- |
| `olist_customers_dataset.csv`           | Customer profile data / 客户信息                |
| `olist_orders_dataset.csv`              | Order lifecycle data / 订单生命周期信息             |
| `olist_order_items_dataset.csv`         | Order item data / 订单商品明细                    |
| `olist_order_payments_dataset.csv`      | Payment data / 支付信息                         |
| `olist_order_reviews_dataset.csv`       | Review data / 评价信息                          |
| `olist_products_dataset.csv`            | Product data / 商品信息                         |
| `olist_sellers_dataset.csv`             | Seller data / 卖家信息                          |
| `olist_geolocation_dataset.csv`         | Geolocation data / 地理位置数据                   |
| `product_category_name_translation.csv` | Product category translation data / 商品类目翻译表 |

---

### 5.2 ODS Layer / ODS 原始数据层

The ODS layer stores raw business data with minimal transformation.

ODS 层用于存储经过轻度标准化处理的原始业务数据。

Main features:

主要特点：

* Preserve original business fields.
  保留原始业务字段。

* Add technical fields `loaded_at` and `dt`.
  添加 `loaded_at` 和 `dt` 技术字段。

* Map each raw CSV file to one ODS table.
  每个原始 CSV 文件对应一张 ODS 表。

Output path:

输出路径：

```
data/ods/
```

Main ODS tables:

主要 ODS 表：

| ODS Table / ODS 表                  | Source File / 来源文件                      |
| ---------------------------------- | --------------------------------------- |
| `ods_customers`                    | `olist_customers_dataset.csv`           |
| `ods_orders`                       | `olist_orders_dataset.csv`              |
| `ods_order_items`                  | `olist_order_items_dataset.csv`         |
| `ods_order_payments`               | `olist_order_payments_dataset.csv`      |
| `ods_order_reviews`                | `olist_order_reviews_dataset.csv`       |
| `ods_products`                     | `olist_products_dataset.csv`            |
| `ods_sellers`                      | `olist_sellers_dataset.csv`             |
| `ods_geolocation`                  | `olist_geolocation_dataset.csv`         |
| `ods_product_category_translation` | `product_category_name_translation.csv` |

---

### 5.3 DWD Layer / DWD 明细层

The DWD layer stores cleaned and standardized detail-level data.

DWD 层用于存储清洗后、标准化后的明细级数据。

Current DWD table:

当前已构建的 DWD 表：

| DWD Table / DWD 表  | Description / 说明                        |
| ------------------ | --------------------------------------- |
| `dwd_order_detail` | Order-level detail wide table / 订单级明细宽表 |

The `dwd_order_detail` table combines order, customer, payment, item, review, and logistics information.

`dwd_order_detail` 表整合了订单、客户、支付、商品、评价和物流信息。

It supports later metrics such as GMV, order count, average order value, delivery delay rate, review rate, and customer purchase behavior.

该表支持后续 GMV、订单数、客单价、物流延迟率、评价率和客户购买行为等指标计算。

Output path:

输出路径：

```
data/dwd/dwd_order_detail.csv
```

---

### 5.4 DWS Layer / DWS 汇总层

The DWS layer stores subject-level aggregated data.

DWS 层用于存储面向主题的汇总数据。

Current DWS table:

当前已构建的 DWS 表：

| DWS Table / DWS 表         | Description / 说明                                   |
| ------------------------- | -------------------------------------------------- |
| `dws_daily_order_summary` | Daily order and business summary table / 每日订单经营汇总表 |

This table aggregates daily order count, GMV, customer count, delivery performance, review behavior, and average order value.

该表按天汇总订单数、GMV、客户数、物流表现、评价行为和客单价等指标。

Output path:

输出路径：

```
data/dws/dws_daily_order_summary.csv
```

---

### 5.5 ADS Layer / ADS 应用层

The ADS layer stores dashboard-ready application data.

ADS 层用于存储可直接服务于 BI 看板和业务报表的应用数据。

Current ADS table:

当前已构建的 ADS 表：

| ADS Table / ADS 表             | Description / 说明                                                  |
| ----------------------------- | ----------------------------------------------------------------- |
| `ads_daily_business_overview` | Daily business overview table for BI dashboard / 用于 BI 看板的每日经营概览表 |

This table includes daily metrics, 7-day moving averages, cumulative metrics, and day-over-day changes.

该表包含每日指标、7 日移动平均、累计指标和日环比变化指标。

Output path:

输出路径：

```
data/ads/ads_daily_business_overview.csv
```

---

## 6. Project Structure / 项目目录结构

```
ecommerce-offline-warehouse/
│
├── data/
│   ├── raw/      # Raw CSV files / 原始 CSV 数据
│   ├── ods/      # ODS output data / ODS 层数据
│   ├── dwd/      # DWD output data (Pandas + Spark) / DWD 层数据
│   ├── dws/      # DWS output data (Pandas + Spark) / DWS 层数据
│   └── ads/      # ADS output data (Pandas + Spark) / ADS 层数据
│
├── scripts/
│   ├── check_raw_data.py
│   ├── load_raw_to_ods.py
│   ├── build_dwd_order_detail.py
│   ├── build_dws_daily_order_summary.py
│   ├── build_ads_daily_business_overview.py
│   ├── run_data_quality_checks.py
│   ├── build_dashboard_charts.py
│   ├── run_pipeline.py                    # Pandas baseline pipeline / Pandas 基准主流程
│   ├── spark_build_dwd_order_detail.py    # Spark DWD script / Spark DWD 脚本
│   ├── spark_build_dws_daily_order_summary.py  # Spark DWS script / Spark DWS 脚本
│   ├── spark_build_ads_daily_business_overview.py  # Spark ADS script / Spark ADS 脚本
│   ├── compare_pandas_spark_outputs.py    # Unified comparison script / 统一对比脚本
│   ├── run_spark_pipeline.py              # Spark migration pipeline / Spark 迁移主流程
│   ├── build_ads_customer_rfm.py          # RFM segmentation / RFM 用户分层
│   ├── build_ads_product_category_rank.py # Category Pareto / 类目帕累托
│   ├── build_ads_geo_state_summary.py     # Geographic summary / 地域汇总
│   ├── run_analysis_pipeline.py           # Analysis pipeline / 分析主流程
│   ├── spark_build_ads_customer_rfm.py    # Spark RFM / Spark RFM
│   ├── spark_build_ads_product_category_rank.py  # Spark category / Spark 类目
│   ├── spark_build_ads_geo_state_summary.py      # Spark geo / Spark 地域
│   ├── run_spark_analysis_pipeline.py     # Spark analysis pipeline / Spark 分析主流程
│   └── build_html_dashboard.py            # Self-contained HTML dashboard / HTML 看板
│
├── dbt/ecommerce_warehouse/models/ads/
│   ├── ads_customer_rfm.sql               # dbt RFM model / dbt RFM 模型
│   ├── ads_product_category_rank.sql      # dbt category model / dbt 类目模型
│   └── ads_geo_state_summary.sql          # dbt geo model / dbt 地域模型
│
├── tests/                                 # pytest unit tests / 单元测试
│   ├── conftest.py
│   ├── test_rfm.py
│   ├── test_product_category.py
│   └── test_geo.py
│
├── .github/workflows/ci.yml               # GitHub Actions CI
│
├── sql/
│   ├── ods/
│   ├── dwd/
│   ├── dws/
│   └── ads/
│
├── docs/
│   ├── raw_data_profile.md
│   ├── ods_table_design.md
│   ├── ods_load_process.md
│   ├── dwd_layer_design.md
│   ├── dws_layer_design.md
│   ├── ads_layer_design.md
│   ├── data_quality_checks.md
│   ├── dashboard_design.md
│   ├── pipeline_orchestration.md
│   ├── spark_sql_migration.md             # Spark migration documentation / Spark 迁移文档
│   ├── pandas_spark_full_comparison_summary.md  # Comparison summary / 对比总结
│   ├── spark_pipeline_run_summary.md      # Spark pipeline summary / Spark 主流程总结
│   └── other generated reports
│
├── notebooks/
├── airflow/
├── dashboard/
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 7. How to Run / 如何运行

### 7.1 Prerequisites / 前置条件

**Java requirement for Spark:**

**Spark 需要 Java 环境：**

```bat
java -version
```

Expected output:

预期输出：

```text
openjdk version "17.x.x"
```

### 7.2 Create Virtual Environment / 创建虚拟环境

Run the following commands from the project root directory.

在项目根目录执行以下命令。

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

### 7.2 Prepare Raw Data / 准备原始数据

Download the Olist e-commerce dataset and put all CSV files into:

下载 Olist 电商数据集，并将所有 CSV 文件放入：

```
data/raw/
```

The raw data directory is ignored by Git.

原始数据目录不会上传到 Git。

---

### 7.3 Run the Full Pandas Pipeline / 运行完整 Pandas 主流程

Run:

执行：

```bat
python scripts\run_pipeline.py
```

This command will run the whole offline warehouse workflow using Pandas.

该命令会使用 Pandas 运行完整的离线数仓处理流程。

Pipeline steps:

主流程步骤：
| Order / 顺序 | Step / 步骤                                | Script / 脚本                            |
| ---------: | ---------------------------------------- | -------------------------------------- |
|          1 | Raw data profiling / 原始数据探查              | `check_raw_data.py`                    |
|          2 | Raw to ODS loading / Raw 到 ODS 加载        | `load_raw_to_ods.py`                   |
|          3 | DWD detail table building / DWD 明细表构建    | `build_dwd_order_detail.py`            |
|          4 | DWS summary table building / DWS 汇总表构建   | `build_dws_daily_order_summary.py`     |
|          5 | ADS dashboard table building / ADS 看板表构建 | `build_ads_daily_business_overview.py` |
|          6 | Data quality checks / 数据质量检查             | `run_data_quality_checks.py`           |
|          7 | Dashboard chart building / 看板图表生成        | `build_dashboard_charts.py`            |

---

### 7.4 Run the Spark SQL Migration Pipeline / 运行 Spark SQL 迁移主流程

After the Pandas pipeline completes, run the Spark migration pipeline:

Pandas 主流程完成后，运行 Spark 迁移主流程：

```bat
python scripts\run_spark_pipeline.py
```

This command will run the Spark SQL migration workflow.

该命令会运行 Spark SQL 迁移工作流程。

Spark pipeline steps:

Spark 主流程步骤：
| Order / 顺序 | Step / 步骤                                       | Script / 脚本                                |
| ---------: | ----------------------------------------------- | ------------------------------------------ |
|          1 | Spark DWD building / Spark DWD 构建               | `spark_build_dwd_order_detail.py`          |
|          2 | Spark DWS building / Spark DWS 构建               | `spark_build_dws_daily_order_summary.py`   |
|          3 | Spark ADS building / Spark ADS 构建               | `spark_build_ads_daily_business_overview.py` |
|          4 | Pandas vs Spark comparison / Pandas 与 Spark 对比 | `compare_pandas_spark_outputs.py`          |

---

### 7.5 Run Scripts Separately / 单独运行脚本

The scripts can also be executed separately.

也可以单独执行各个脚本。

```
python scripts\check_raw_data.py
python scripts\load_raw_to_ods.py
python scripts\build_dwd_order_detail.py
python scripts\build_dws_daily_order_summary.py
python scripts\build_ads_daily_business_overview.py
python scripts\run_data_quality_checks.py
```

---

## 8. Main Output Files / 主要输出文件

### 8.1 Data Output / 数据输出

| Layer / 分层 | Output File / 输出文件                         |
| ---------- | ------------------------------------------ |
| ODS        | `data/ods/ods_xxx.csv`                     |
| DWD        | `data/dwd/dwd_order_detail.csv`            |
| DWS        | `data/dws/dws_daily_order_summary.csv`     |
| ADS        | `data/ads/ads_daily_business_overview.csv` |

---

### 8.2 Report Output / 报告输出

| Report / 报告                                   | Description / 说明                          |
| --------------------------------------------- | ----------------------------------------- |
| `docs/raw_data_profile.md`                    | Raw data profiling report / 原始数据探查报告      |
| `docs/raw_data_summary.csv`                   | Raw data summary / 原始数据汇总                 |
| `docs/raw_missing_values.csv`                 | Missing value report / 缺失值报告              |
| `docs/ods_load_report.csv`                    | ODS loading report / ODS 加载报告             |
| `docs/dwd_order_detail_report.csv`            | DWD table summary report / DWD 表汇总报告      |
| `docs/dws_daily_order_summary_report.csv`     | DWS table summary report / DWS 表汇总报告      |
| `docs/ads_daily_business_overview_report.csv` | ADS table summary report / ADS 表汇总报告      |
| `docs/data_quality_check_report.csv`          | Detailed data quality report / 详细数据质量检查报告 |
| `docs/data_quality_check_summary.md`          | Data quality summary / 数据质量检查总结           |
| `docs/pipeline_run_report.csv`                | Pipeline run report / 主流程运行报告             |
| `docs/pipeline_latest_run.log`                | Pipeline execution log / 主流程运行日志          |
| `docs/pipeline_run_summary.md`                | Pipeline run summary / 主流程运行总结            |

---

## 9. Key Metrics / 核心指标

The project currently supports the following business metrics.

本项目当前支持以下业务指标。

| Metric / 指标                    | Description / 说明                                                         |
| ------------------------------ | ------------------------------------------------------------------------ |
| GMV                            | Total payment amount / 总支付金额                                             |
| Order count / 订单数              | Number of orders / 订单数量                                                  |
| Valid order count / 有效订单数      | Orders excluding canceled and unavailable orders / 排除取消和不可用订单后的订单数       |
| Paid order count / 支付订单数       | Orders with payment amount greater than 0 / 支付金额大于 0 的订单数                |
| Unique customer count / 唯一客户数  | Number of unique customers / 唯一客户数量                                      |
| AOV / 客单价                      | GMV divided by order count / GMV 除以订单数                                   |
| Delivery rate / 送达率            | Delivered orders divided by total orders / 已送达订单占总订单比例                   |
| Late delivery rate / 物流延迟率     | Late delivered orders divided by delivered orders / 延迟送达订单占已送达订单比例       |
| Review rate / 评价率              | Reviewed orders divided by total orders / 有评价订单占总订单比例                    |
| Review comment rate / 文字评价率    | Orders with review comments divided by reviewed orders / 有文字评价订单占已评价订单比例 |
| Average review score / 平均评价分数  | Average customer review score / 客户评价平均分                                  |
| 7-day moving average / 7 日移动平均 | Smoothed trend metrics / 平滑后的趋势指标                                        |
| Day-over-day growth / 日环比增长    | Daily change compared with the previous day / 相比前一天的变化                   |

---

## 10. Data Quality Checks / 数据质量检查

The project includes a data quality check module.

本项目包含数据质量检查模块。

The check script is:

检查脚本为：

```
scripts/run_data_quality_checks.py
```

The module checks:

该模块检查：

| Scope / 范围  | Check Items / 检查项                                                                             |
| ----------- | --------------------------------------------------------------------------------------------- |
| ODS         | File existence, row count, technical fields / 文件存在性、行数、技术字段                                   |
| DWD         | Primary key duplication, null keys, negative amounts, date completeness / 主键重复、主键为空、负金额、日期完整性 |
| DWS         | Date granularity, non-negative metrics, rate range / 日期粒度、非负指标、比率范围                           |
| ADS         | Date granularity, dashboard metric validity, rate range / 日期粒度、看板指标有效性、比率范围                   |
| Cross-layer | Order count and GMV consistency / 订单数和 GMV 跨层一致性                                              |

Output files:

输出文件：

```
docs/data_quality_check_report.csv
docs/data_quality_check_summary.md
```

---

## 11. Pipeline Orchestration / 主流程编排

The pipeline orchestration script is:

主流程编排脚本为：

```
scripts/run_pipeline.py
```

It connects all ETL and data quality steps into a complete workflow.

它将所有 ETL 和数据质量检查步骤连接成一个完整工作流。

The pipeline uses a sequential execution strategy.

该主流程采用顺序执行策略。

If one step fails, the following steps will be skipped.

如果某一步失败，后续步骤会被跳过。

This prevents downstream layers from being built on incomplete upstream data.

这可以避免下游分层基于不完整的上游数据继续构建。

---

## 12. SQL Design / SQL 设计

The project includes Hive-style table creation SQL files.

本项目包含 Hive 风格的建表 SQL 文件。

| Layer / 分层 | SQL File / SQL 文件               |
| ---------- | ------------------------------- |
| ODS        | `sql/ods/create_ods_tables.sql` |
| DWS        | `sql/dws/create_dws_tables.sql` |
| ADS        | `sql/ads/create_ads_tables.sql` |

These SQL files are used to describe how the project can be adapted to a Hive or Spark SQL environment.

这些 SQL 文件用于说明本项目如何迁移或扩展到 Hive / Spark SQL 环境。

---

## 13. Spark SQL Migration / Spark SQL 迁移

The project has completed a Spark SQL migration for DWD, DWS, and ADS layers.

项目已完成 DWD、DWS、ADS 分层的 Spark SQL 迁移。

### 13.1 Migration Architecture / 迁移架构

```
ODS CSV Files (from Pandas baseline)
    ↓
Spark DWD Order Detail
    ↓
Spark DWS Daily Order Summary
    ↓
Spark ADS Daily Business Overview
    ↓
Pandas vs Spark Full Comparison
```

**Important note / 重要说明:** ODS layer is still generated by the Pandas baseline pipeline. Spark migration starts from ODS CSV files.

**重要说明：** ODS 层仍由 Pandas 基准主流程生成。Spark 迁移从 ODS CSV 文件开始。

### 13.2 Spark Scripts / Spark 脚本

| Script / 脚本 | Purpose / 目的 |
|---|---|
| `spark_build_dwd_order_detail.py` | Build DWD from ODS using Spark SQL / 使用 Spark SQL 从 ODS 构建 DWD |
| `spark_build_dws_daily_order_summary.py` | Build DWS from Spark DWD using Spark SQL / 使用 Spark SQL 从 Spark DWD 构建 DWS |
| `spark_build_ads_daily_business_overview.py` | Build ADS from Spark DWS using Spark SQL / 使用 Spark SQL 从 Spark DWS 构建 ADS |
| `compare_pandas_spark_outputs.py` | Compare Pandas vs Spark across all layers / 跨所有分层对比 Pandas 与 Spark |
| `run_spark_pipeline.py` | Spark migration pipeline orchestration / Spark 迁移主流程编排 |

### 13.3 Key Spark SQL Features / 关键 Spark SQL 功能

| Feature / 功能 | Description / 说明 |
|---|---|
| Multi-table joins / 多表关联 | Join orders, customers, items, payments, reviews in DWD / 在 DWD 中关联订单、客户、商品、支付、评价 |
| Aggregations / 聚合计算 | Order-level and daily-level aggregations / 订单级和日级聚合 |
| Window functions / 窗口函数 | 7-day moving averages, cumulative metrics, LAG() for day-over-day / 7 日移动平均、累计指标、LAG() 日环比 |
| Validation / 校验 | Automated Pandas vs Spark comparison / 自动化 Pandas 与 Spark 对比 |

For detailed documentation, see `docs/spark_sql_migration.md`.

详细文档请参阅 `docs/spark_sql_migration.md`。

---

## 14. Pandas vs Spark Validation Results / Pandas 与 Spark 校验结果

### 14.1 Full Comparison Summary / 全量对比总结

| Summary / 总结 | Value / 数值 |
|---|---|
| **Total checks** / 总检查数 | **23** |
| **Passed** / 通过数 | **23** |
| **Failed** / 失败数 | **0** |

### 14.2 Layer-level Results / 分层结果

| Layer / 分层 | Checks / 检查数 | Passed / 通过 | Failed / 失败 |
|---|---:|---:|---:|
| DWD | 9 | 9 | 0 |
| DWS | 7 | 7 | 0 |
| ADS | 7 | 7 | 0 |

### 14.3 Spark Pipeline Latest Run / Spark 主流程最新运行

| Summary / 总结 | Value / 数值 |
|---|---|
| Total steps / 总步骤数 | 4 |
| Success / 成功数 | 4 |
| Failed / 失败数 | 0 |
| Skipped / 跳过数 | 0 |

**Result: All comparison checks passed. Spark pipeline completed successfully.**

**结果：所有对比检查通过。Spark 主流程成功完成。**

---

## 15. Dashboard Output / 看板输出

The project generates dashboard charts from the ADS layer.

本项目基于 ADS 应用层数据生成经营分析看板图表。

Dashboard source table:

看板来源表：

    data/ads/ads_daily_business_overview.csv

Dashboard output directory:

看板输出目录：

    dashboard/

Generated dashboard files:

已生成的看板文件：

| Chart / 图表 | File / 文件 | Description / 说明 |
|---|---|---|
| GMV Trend / GMV 趋势 | `dashboard/gmv_trend.png` | Daily GMV and 7-day moving average / 每日 GMV 与 7 日移动平均 |
| Order Count Trend / 订单数趋势 | `dashboard/order_count_trend.png` | Daily order count and 7-day moving average / 每日订单数与 7 日移动平均 |
| AOV Trend / 客单价趋势 | `dashboard/aov_trend.png` | Daily average order value trend / 每日客单价趋势 |
| Cumulative Business Trend / 累计经营趋势 | `dashboard/cumulative_business_trend.png` | Cumulative GMV and cumulative order count / 累计 GMV 与累计订单数 |
| Delivery Performance / 物流表现 | `dashboard/delivery_performance.png` | Delivery rate and late delivery rate / 送达率与物流延迟率 |
| Review Performance / 评价表现 | `dashboard/review_performance.png` | Review rate and average review score / 评价率与平均评价分数 |
| Day-over-Day Growth / 日环比增长 | `dashboard/day_over_day_growth.png` | GMV and order count day-over-day growth / GMV 与订单数日环比增长 |

KPI summary file:

KPI 汇总文件：

    dashboard/dashboard_kpi_summary.csv

This module makes the final ADS output visible and easier to present in GitHub, resume projects, and interviews.

该模块使最终 ADS 层产出可视化，更适合用于 GitHub 展示、简历项目和面试讲解。

## 15B. Business Analysis Layer / 业务分析层

Beyond the daily overview, the project builds three customer/merchandising
analyses on top of DWD/ODS. Run them together with:

在每日经营概览之外，项目在 DWD/ODS 之上构建了三项客户/商品分析。一键运行：

```bat
python scripts\run_analysis_pipeline.py
```

| Analysis / 分析 | Script / 脚本 | Output / 产出 |
|---|---|---|
| **RFM segmentation** / RFM 用户分层 | `build_ads_customer_rfm.py` | `data/ads/ads_customer_rfm.csv`, segment summary, 2 charts |
| **Product category Pareto** / 商品类目帕累托 | `build_ads_product_category_rank.py` | `data/ads/ads_product_category_rank.csv`, top-15 + Pareto charts |
| **Geographic (state) summary** / 地域（州级）汇总 | `build_ads_geo_state_summary.py` | `data/ads/ads_geo_state_summary.csv`, GMV + delivery charts |

The analysis layer is implemented across **all three engines** for parity, just
like the core layers:

分析层同样在 **三套引擎** 上实现并做一致性对比，与核心层保持一致：

| Engine / 引擎 | Entry point / 入口 |
|---|---|
| Pandas | `python scripts\run_analysis_pipeline.py` |
| Spark SQL | `python scripts\run_spark_analysis_pipeline.py` (writes `*_spark.csv` + comparison) |
| dbt | `dbt run --select ads_customer_rfm ads_product_category_rank ads_geo_state_summary` |

An interactive, self-contained dashboard is generated with:

用以下命令生成交互式、自包含看板：

```bat
python scripts\build_html_dashboard.py
```

then open [`dashboard/index.html`](dashboard/index.html). Findings and how to read
each table are written up in [`docs/business_insights.md`](docs/business_insights.md).

随后打开 [`dashboard/index.html`](dashboard/index.html)。各表结论与解读见
[`docs/business_insights.md`](docs/business_insights.md)。

Key structural insight: with **96,096 customers** behind **99,441 orders**, the
marketplace is dominated by **one-time buyers**, so growth levers are acquisition
and reactivation rather than a loyalty loop.

关键结构性洞察：**9.94 万订单** 背后是 **9.61 万唯一客户**，平台以 **一次性购买**
为主，增长抓手是拉新与唤醒，而非复购闭环。

---

## 15C. Testing & CI / 测试与持续集成

The analysis layer is covered by self-contained `pytest` unit tests that use small
synthetic data (no dataset download needed), so they also run in CI.

分析层由自包含的 `pytest` 单元测试覆盖，使用小型合成数据（无需下载数据集），
因此也能在 CI 中运行。

```bat
pip install -r requirements-dev.txt
pytest
```

| Item / 项 | Detail / 说明 |
|---|---|
| Unit tests / 单元测试 | `tests/test_rfm.py`, `tests/test_product_category.py`, `tests/test_geo.py` |
| Lint / 静态检查 | `ruff check scripts tests` (config in `ruff.toml`) |
| CI | `.github/workflows/ci.yml` — ruff + pytest on Python 3.10/3.11 |

---

## 16. Project Highlights / 项目亮点

### 16.1 Complete Warehouse Layering / 完整数仓分层

The project implements Raw, ODS, DWD, DWS, and ADS layers.

项目实现了 Raw、ODS、DWD、DWS 和 ADS 分层。

This structure is close to a real offline data warehouse workflow.

该结构接近真实企业离线数仓开发流程。

---

### 16.2 Business-Oriented Metric System / 面向业务的指标体系

The project builds business metrics such as GMV, AOV, order count, customer count, delivery performance, and review performance.

项目构建了 GMV、客单价、订单数、客户数、物流表现和评价表现等业务指标。

These metrics can support business analysis and dashboard development.

这些指标可以支撑经营分析和 BI 看板开发。

---

### 16.3 Data Quality Module / 数据质量模块

The project includes automated data quality checks across multiple warehouse layers.

项目包含跨多个数仓分层的自动化数据质量检查。

This improves reliability and makes the project closer to enterprise data development practice.

这提升了数据链路可靠性，也让项目更接近企业数据开发实践。

---

### 16.4 Pipeline Automation / 主流程自动化

The project provides one-command pipeline scripts for both Pandas and Spark.

项目为 Pandas 和 Spark 都提供一键运行主流程脚本。

Pandas baseline pipeline:

Pandas 基准主流程：

```bat
python scripts\run_pipeline.py
```

Spark migration pipeline:

Spark 迁移主流程：

```bat
python scripts\run_spark_pipeline.py
```

---

### 16.5 Spark SQL Migration / Spark SQL 迁移

The project implements a complete Spark SQL migration for DWD, DWS, and ADS layers.

项目实现了 DWD、DWS、ADS 分层的完整 Spark SQL 迁移。

Key features include:

关键功能包括：

* Multi-table joins and aggregations using Spark SQL.
  使用 Spark SQL 完成多表关联和聚合计算。

* Window functions for 7-day moving averages, cumulative metrics, and day-over-day changes.
  使用窗口函数计算 7 日移动平均、累计指标和日环比变化。

* Automated Pandas vs Spark comparison with 23 validation checks all passed.
  自动化 Pandas 与 Spark 对比，23 项校验检查全部通过。

* Separate Pandas baseline and Spark migration pipelines.
  Pandas 基准和 Spark 迁移主流程保持分离。

* Migration thinking from local prototype to big-data-style processing.
  从本地原型到大数据风格处理的迁移思维。

---

### 16.6 Bilingual Documentation / 中英文对照文档

The project documentation is written in both English and Chinese.

项目文档采用中英文对照形式编写。

This makes the project easier to explain in both Chinese and English interviews.

这使项目更适合在中文和英文面试场景中讲解。

---

## 17. Current Progress / 当前进度

Completed:

已完成：

* Project directory structure.
  项目目录结构。

* Raw data profiling script.
  原始数据探查脚本。

* ODS table design.
  ODS 表设计。

* Raw-to-ODS loading script.
  Raw 到 ODS 加载脚本。

* DWD order detail table (Pandas + Spark).
  DWD 订单明细宽表（Pandas + Spark）。

* DWS daily order summary table (Pandas + Spark).
  DWS 每日订单汇总表（Pandas + Spark）。

* ADS daily business overview table (Pandas + Spark).
  ADS 每日经营概览表（Pandas + Spark）。

* Data quality check module.
  数据质量检查模块。

* Dashboard chart generation.
  看板图表生成。

* Pandas baseline pipeline orchestration.
  Pandas 基准主流程编排。

* **Spark SQL migration for DWD, DWS, and ADS layers.**
  **DWD、DWS、ADS 分层的 Spark SQL 迁移。**

* **Pandas vs Spark automated comparison (23 checks passed).**
  **Pandas 与 Spark 自动化对比（23 项检查通过）。**

* **Spark migration pipeline orchestration.**
  **Spark 迁移主流程编排。**

* Bilingual documentation.
  中英文对照文档。

---

## 18. Future Improvements / 后续优化方向

Planned improvements:

计划优化方向：

| Direction / 方向                  | Description / 说明                                                                            | Status / 状态 |
| ------------------------------- | ------------------------------------------------------------------------------------------- | --- |
| More DWD tables / 更多 DWD 表      | Build product, seller, customer, and logistics detail tables / 构建商品、卖家、客户和物流明细表             | Planned / 计划 |
| More DWS summaries / 更多 DWS 汇总表 | Build customer, product, city, payment, and delivery summary tables / 构建客户、商品、城市、支付和物流主题汇总表 | Planned / 计划 |
| BI dashboard / BI 看板            | Build Power BI or Superset dashboard / 构建 Power BI 或 Superset 看板                            | Planned / 计划 |
| **Spark migration / Spark 迁移**  | **Replace Pandas processing with PySpark for DWD/DWS/ADS / 使用 PySpark 重构 DWD/DWS/ADS 处理逻辑** | **Completed / 已完成** |
| Spark ODS loading / Spark ODS 加载 | Replace Pandas ODS loading with Spark / 使用 Spark 替换 Pandas ODS 加载                              | Planned / 计划 |
| Airflow scheduling / Airflow 调度 | Schedule ETL pipeline with Airflow DAGs / 使用 Airflow DAG 调度 ETL 流程                          | Planned / 计划 |
| Database storage / 数据库存储        | Load final tables into PostgreSQL or ClickHouse / 将最终表加载到 PostgreSQL 或 ClickHouse           | Planned / 计划 |
| Data visualization / 数据可视化      | Add dashboard screenshots and analysis results / 增加看板截图和分析结论                                | Planned / 计划 |
| Customer analysis / 用户分析        | Add RFM customer segmentation / 增加 RFM 用户分层                                                 | Planned / 计划 |
| Product analysis / 商品分析         | Add product category ranking and sales contribution analysis / 增加商品类目排名和销售贡献分析              | Planned / 计划 |

---

## 19. Resume Description / 简历描述

### 19.1 Pandas Baseline Version / Pandas 基准版本

Chinese version:

中文简历描述：

基于 Olist 电商订单数据构建离线数仓项目，设计 Raw-ODS-DWD-DWS-ADS 分层架构，使用 Python 和 Pandas 实现原始数据探查、ODS 加载、DWD 订单明细宽表构建、DWS 每日经营汇总和 ADS 看板指标表生成；构建 GMV、订单量、客单价、物流延迟率、评价率等核心指标，并开发数据质量检查模块和一键 ETL 主流程脚本，实现文件完整性、主键重复、金额合法性、指标范围和跨层一致性校验。

English version:

英文简历描述：

Built an offline e-commerce data warehouse based on the Olist order dataset, designing a Raw-ODS-DWD-DWS-ADS layered architecture. Implemented raw data profiling, ODS loading, DWD order detail modeling, DWS daily business aggregation, and ADS dashboard-ready metric tables using Python and Pandas. Developed key metrics including GMV, order count, AOV, delivery delay rate, and review rate, and implemented automated data quality checks and a one-command ETL pipeline for file completeness, primary key uniqueness, amount validation, metric range checks, and cross-layer consistency validation.

### 19.1b Analysis & Engineering Add-on / 分析与工程增强补充

Chinese version / 中文简历描述：

在数仓基础上补充业务分析层：基于 DWD 实现 RFM 用户分层（rank 分位打分，对复购稀疏
的电商数据做稳健处理）、商品类目帕累托贡献分析与地域（州级）经营/物流分析，产出 ADS
表、可视化图表与业务洞察报告；并为分析层编写 pytest 单元测试与 GitHub Actions CI
（ruff + pytest），提升项目工程化与可维护性。

English version / 英文简历描述：

Extended the warehouse with a business-analysis layer: RFM customer segmentation
(rank-based quintile scoring, robust to the sparse-repeat nature of e-commerce
data), product-category Pareto contribution analysis, and geographic (state-level)
performance/logistics analysis — producing ADS tables, charts, and an insights
report. Added pytest unit tests and a GitHub Actions CI pipeline (ruff + pytest)
for the analysis layer to improve engineering quality and maintainability.

### 19.2 Spark SQL Enhanced Version / Spark SQL 增强版本

Chinese version:

中文简历描述：

在电商离线数仓项目中实现 Spark SQL 迁移，基于 PySpark 重构 DWD 订单明细层、DWS 每日经营汇总层和 ADS 看板指标层，使用 Spark SQL 完成多表关联、聚合计算、窗口函数指标（7 日移动平均、累计指标、日环比）和自动化 Pandas 与 Spark 输出对比校验，23 项核心指标全部一致。保留 Pandas 基准主流程，展示了从本地原型到大数据风格处理的迁移思维。

English version:

英文简历描述：

Implemented a Spark SQL migration for an e-commerce offline data warehouse, rebuilding DWD, DWS, and ADS layers with PySpark and Spark SQL. Developed multi-table joins, aggregations, window-function-based metrics (7-day moving averages, cumulative metrics, day-over-day changes), and automated Pandas-vs-Spark validation reports with all 23 core comparison checks passed. Kept Pandas baseline pipeline separate, demonstrating migration thinking from local prototype to big-data-style processing.

---

## 20. Interview Talking Points / 面试讲解要点

When explaining this project in an interview, the key points are:

面试中讲解该项目时，可以重点说明：

1. I designed a complete offline warehouse architecture from Raw to ADS.
   我设计了从 Raw 到 ADS 的完整离线数仓架构。

2. I separated detail data, summary data, and dashboard-ready data into different layers.
   我将明细数据、汇总数据和看板应用数据拆分到不同分层中。

3. I built a core DWD order detail wide table as the foundation for later metrics.
   我构建了核心 DWD 订单明细宽表，作为后续指标计算基础。

4. I created reusable DWS and ADS tables for business analysis and BI dashboards.
   我构建了可复用的 DWS 和 ADS 表，用于业务分析和 BI 看板。

5. I added data quality checks to ensure file completeness, primary key uniqueness, metric validity, and cross-layer consistency.
   我加入了数据质量检查，保证文件完整性、主键唯一性、指标有效性和跨层一致性。

6. I automated the whole workflow with one-command pipeline scripts for both Pandas and Spark.
   我使用一键主流程脚本自动化完整 ETL 链路（Pandas 和 Spark 两套）。

7. I implemented Spark SQL migration for DWD, DWS, and ADS layers using PySpark.
   我实现了 DWD、DWS、ADS 分层的 Spark SQL 迁移，使用 PySpark。

8. I used Spark SQL window functions for moving averages, cumulative metrics, and day-over-day changes.
   我使用 Spark SQL 窗口函数计算移动平均、累计指标和日环比变化。

9. I built automated Pandas vs Spark comparison to validate migration correctness (23 checks all passed).
   我构建了自动化 Pandas 与 Spark 对比校验（23 项检查全部通过）。

10. The project first used Pandas as a local baseline, then added Spark SQL migration. ODS is reused. DWD/DWS/ADS are rebuilt with Spark SQL. Results are validated against Pandas output. This reflects how data teams migrate prototypes to scalable processing.
    项目先使用 Pandas 作为本地基准，再添加 Spark SQL 迁移。ODS 复用。DWD/DWS/ADS 用 Spark SQL 重构。结果与 Pandas 输出校验。这反映了数据团队如何将原型迁移到可扩展处理方案。

---

## 21. Notes / 说明

The raw data files are not included in this repository because they may be large.

由于原始数据文件较大，本仓库不包含原始数据文件。

Please download the dataset separately and place the CSV files under:

请单独下载数据集，并将 CSV 文件放入：

```
data/raw/
```

Generated intermediate data files under `data/ods/`, `data/dwd/`, `data/dws/`, and `data/ads/` are also ignored by Git by default.

默认情况下，`data/ods/`、`data/dwd/`、`data/dws/` 和 `data/ads/` 下生成的中间数据文件也不会上传到 Git。

This project is designed for learning, portfolio demonstration, and interview preparation.

本项目主要用于学习、作品集展示和面试准备。
