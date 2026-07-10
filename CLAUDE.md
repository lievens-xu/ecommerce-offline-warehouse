# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 语言偏好 / Language Preference

- **始终使用简体中文回复用户**，包括代码注释、说明文档和所有对话内容。
- 代码本身（变量名、函数名等）仍使用英文，但注释使用中文。

---

## Project Overview / 项目概述

This is a portfolio-level **e-commerce offline data warehouse** project based on the [Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) public dataset. It demonstrates a complete offline warehouse workflow: Raw → ODS → DWD → DWS → ADS → Quality Checks → Dashboard.

这是一个基于 Olist 巴西电商公开数据集构建的**离线数仓求职展示项目**，演示完整的离线数仓开发流程。

### Target Roles / 目标岗位方向

- Data Warehouse Developer / 数仓开发
- Data Developer / 数据开发
- Junior Big Data Developer / 初级大数据开发
- Data Analyst (with data engineering ability) / 具备数据工程能力的数据分析

---

## Architecture / 架构

### Dual Pipelines / 双主流程

```
             Pandas Baseline                     Spark Migration
        ┌──────────────────────┐           ┌──────────────────────────┐
        │  Raw CSV             │           │  ODS CSV (reused)        │
        │    ↓                 │           │    ↓                     │
        │  ODS (Pandas)        │           │  Spark DWD               │
        │    ↓                 │           │    ↓                     │
        │  DWD (Pandas)        │           │  Spark DWS               │
        │    ↓                 │           │    ↓                     │
        │  DWS (Pandas)        │           │  Spark ADS               │
        │    ↓                 │           │    ↓                     │
        │  ADS (Pandas)        │           │  Pandas vs Spark Compare │
        │    ↓                 │           └──────────────────────────┘
        │  Data Quality Checks │
        │    ↓                 │
        │  Dashboard Charts    │
        └──────────────────────┘
```

- **Pandas baseline**: Stable reference implementation with 7-step pipeline.
- **Spark migration**: PySpark + Spark SQL implementation for DWD/DWS/ADS layers. Reuses ODS CSV files from Pandas pipeline.

---

## Dataset Schema / 数据集字段说明

### ODS Tables (9 tables, `data/ods/`)

| Table / 表 | Key Fields / 关键字段 |
|---|---|
| `ods_customers` | `customer_id`, `customer_unique_id`, `customer_city`, `customer_state` |
| `ods_orders` | `order_id`, `customer_id`, `order_status`, `order_purchase_timestamp`, `order_delivered_customer_date`, `order_estimated_delivery_date` |
| `ods_order_items` | `order_id`, `order_item_id`, `product_id`, `seller_id`, `price`, `freight_value` |
| `ods_order_payments` | `order_id`, `payment_sequential`, `payment_type`, `payment_installments`, `payment_value` |
| `ods_order_reviews` | `review_id`, `order_id`, `review_score` (1-5), `review_comment_message` |
| `ods_products` | `product_id`, `product_category_name`, `product_weight_g`, `product_length_cm`, `product_height_cm`, `product_width_cm` |
| `ods_sellers` | `seller_id`, `seller_city`, `seller_state` |
| `ods_geolocation` | `geolocation_zip_code_prefix`, `geolocation_lat`, `geolocation_lng`, `geolocation_city`, `geolocation_state` |
| `ods_product_category_translation` | `product_category_name`, `product_category_name_english` |

All ODS tables have technical fields: `loaded_at` (TIMESTAMP) and `dt` (STRING partition).

### DWD (1 table, `data/dwd/dwd_order_detail.csv`)

Order-level wide table joining orders + customers + order_items + payments + reviews. ~99,000 rows.

Key columns: `order_id`, `customer_id`, `order_status`, `purchase_date`, `product_amount`, `freight_amount`, `payment_amount`, `review_score`, `delivery_delay_days`, `is_delivered`, `is_late_delivery`.

### DWS (1 table, `data/dws/dws_daily_order_summary.csv`)

Daily aggregated metrics. ~2,400 rows, one row per purchase date.

Metrics: `order_count`, `valid_order_count`, `paid_order_count`, `unique_customer_count`, `delivery_rate`, `late_delivery_rate`, `review_rate`, `total_payment_amount` (GMV), `aov`.

### ADS (1 table, `data/ads/ads_daily_business_overview.csv`)

Dashboard-ready daily business overview table.

Window-function-based metrics: `gmv_7d_moving_avg`, `order_count_7d_moving_avg`, `aov_7d_moving_avg`, `cumulative_gmv`, `gmv_day_over_day_rate`, `order_count_day_over_day_rate`.

---

## Project Structure / 项目目录结构

```
ecommerce-offline-warehouse/
├── data/                  # Generated data (gitignored)
│   ├── raw/               # Raw CSV (must be downloaded separately)
│   ├── ods/               # ODS layer output (Pandas)
│   ├── dwd/               # DWD layer output (Pandas + Spark)
│   ├── dws/               # DWS layer output (Pandas + Spark)
│   └── ads/               # ADS layer output (Pandas + Spark)
├── scripts/               # All ETL scripts
├── docs/                  # Documentation and reports
├── sql/                   # Hive-style DDL SQL
│   ├── ods/               # ODS table creation SQL
│   ├── dwd/               # DWD table creation SQL
│   ├── dws/               # DWS table creation SQL
│   ├── ads/               # ADS table creation SQL
│   ├── postgres/          # PostgreSQL setup SQL
│   └── superset/          # Superset query SQL
├── dashboard/             # Generated dashboard charts
├── notebooks/             # Jupyter notebooks
├── airflow/               # Airflow Docker + DAGs
├── dbt/                   # dbt models for PostgreSQL
├── superset/              # Superset Docker + config
├── powerbi/               # Power BI setup guide
├── docker-compose.*.yml   # Docker environments
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Important Rules / 重要工作规则

1. **Do not modify the Pandas baseline pipeline scripts** unless explicitly requested. Treat them as the stable reference implementation.

2. **Files that should not be modified** before Spark migration is fully verified: `README.md`, `scripts/run_pipeline.py`.

3. **Do not commit generated data** under `data/`. Always run `git status` before committing.

4. **All new Markdown docs must be bilingual** (English + Chinese), using `## Title / 标题` format.

5. **For Spark scripts**, use PySpark and Spark SQL (`spark.sql("""...""")`). Do not use Pandas alone. Converting to Pandas at the end for CSV saving is acceptable.

---

## Scripts Reference / 脚本参考

### Pandas Baseline Pipeline (7 scripts)

| Script | Purpose |
|---|---|
| `check_raw_data.py` | Profile raw CSV files, generate column stats and missing value report |
| `load_raw_to_ods.py` | Load raw CSV → ODS with technical fields (`loaded_at`, `dt`) |
| `build_dwd_order_detail.py` | Build DWD order detail wide table (multi-table join + aggregation) |
| `build_dws_daily_order_summary.py` | Build DWS daily summary (daily aggregation metrics) |
| `build_ads_daily_business_overview.py` | Build ADS with window functions (7d MA, cumulative, day-over-day) |
| `run_data_quality_checks.py` | Run DQ checks across all layers (file existence, PK, nulls, ranges, cross-layer consistency) |
| `build_dashboard_charts.py` | Generate matplotlib dashboard charts from ADS |
| `run_pipeline.py` | Orchestrate all 7 steps sequentially |

### Spark Migration Pipeline (5 scripts)

| Script | Purpose |
|---|---|
| `spark_build_dwd_order_detail.py` | Spark SQL version of DWD build |
| `spark_build_dws_daily_order_summary.py` | Spark SQL version of DWS build |
| `spark_build_ads_daily_business_overview.py` | Spark SQL version of ADS build |
| `compare_pandas_spark_outputs.py` | Compare Pandas vs Spark outputs across all 3 layers (23 checks) |
| `run_spark_pipeline.py` | Orchestrate all 4 Spark steps sequentially |

---

## Commands / 常用命令

### Environment Setup

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Run Pipelines

```bat
REM Pandas baseline (full pipeline)
python scripts\run_pipeline.py

REM Spark migration pipeline
python scripts\run_spark_pipeline.py
```

### Run Individual Scripts

```bat
python scripts\build_dwd_order_detail.py
python scripts\spark_build_dwd_order_detail.py
python scripts\compare_pandas_spark_outputs.py
```

### Docker Services (PostgreSQL, Airflow, Superset)

```bat
REM Start PostgreSQL
docker compose -f docker-compose.postgres.yml up -d

REM Start Airflow (requires PostgreSQL first)
docker compose -f docker-compose.airflow.yml up -d

REM Start Superset (requires PostgreSQL first)
docker compose -f docker-compose.superset.yml up -d
```

### Git

```bat
REM Check what's tracked
git status

REM Commit (avoid committing data/ files)
git add scripts/ docs/ sql/ -- :!data/
git commit -m "message"
```

---

## Environment / 运行环境

- **OS**: Windows 11
- **Java**: 17 (required for Spark)
- **Python**: virtual environment in `.venv/`
- **PySpark**: installed via `requirements.txt`
- **Spark warnings** (winutils.exe, HADOOP_HOME) are safe to ignore for local CSV processing

---

## Key Business Metrics / 核心业务指标

| Metric / 指标 | Definition / 定义 |
|---|---|
| GMV | Total payment amount (sum of `payment_value`) |
| Order Count | Total number of orders |
| Valid Order Count | Excluding canceled and unavailable orders |
| AOV (客单价) | GMV / Order Count |
| Delivery Rate | Delivered orders / Total orders |
| Late Delivery Rate | Late delivered orders / Delivered orders |
| Review Rate | Reviewed orders / Total orders |
| Average Review Score | Average of `review_score` (1-5 scale) |

---

## Key Spark SQL Features Used / 使用的核心 Spark SQL 功能

- **Multi-table JOINs**: 5-table join in DWD (orders + customers + items + payments + reviews)
- **Aggregations**: COUNT, SUM, AVG, COUNT DISTINCT with GROUP BY
- **Window Functions**: 7-day moving average (ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), cumulative SUM, LAG() for day-over-day
- **CASE WHEN**: Flag-based counting for valid orders, delivery status, review status
- **Date functions**: `to_date()`, `date_format()`, `datediff()`, `add_months()`

---

## Data Quality Checks / 数据质量检查

The `run_data_quality_checks.py` script verifies:

| Layer / 层 | Check Items / 检查项 |
|---|---|
| ODS | File existence, row count, technical fields (`loaded_at`, `dt`) |
| DWD | Primary key duplication, null keys, negative amounts, date completeness |
| DWS | Date granularity, non-negative metrics, rate range [0, 1] |
| ADS | Date granularity, metric validity, rate range, non-negative values |
| Cross-layer | Order count and GMV consistency across DWD → DWS → ADS |