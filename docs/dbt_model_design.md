# dbt Model Design / dbt 模型设计

## 1. Why dbt / 为什么使用 dbt

This document describes the dbt project for the e-commerce offline data warehouse.

本文档说明电商离线数仓的 dbt 项目。

dbt (data build tool) is a SQL-first transformation tool that enables:

dbt（数据构建工具）是一个 SQL 优先的转换工具，提供以下能力：

| Feature / 特性 | Benefit / 优势 |
|---|---|
| SQL-based modeling / 基于 SQL 建模 | Transformations written in pure SQL, version-controlled / 纯 SQL 编写转换逻辑，版本控制 |
| Automated dependency resolution / 自动依赖解析 | dbt determines model run order / dbt 自动确定模型运行顺序 |
| Built-in testing / 内置测试 | Test data quality with `not_null`, `unique`, `accepted_values` / 测试数据质量 |
| Documentation generation / 文档生成 | Auto-generate project documentation / 自动生成项目文档 |
| Materialization strategies / 物化策略 | `view`, `table`, `incremental` per model / 每个模型可选择物化策略 |

---

## 2. dbt in the Project Context / dbt 在项目中的定位

The e-commerce warehouse now has three parallel pipelines:

电商数仓现在有三条并行主流程：

| Pipeline / 主流程 | Engine / 引擎 | Storage / 存储 | Purpose / 用途 |
|---|---|---|---|
| **Pandas Baseline** / Pandas 基准 | Python / Pandas | Local CSV | Local prototype reference / 本地原型参考 |
| **Spark Migration** / Spark 迁移 | PySpark / Spark SQL | Local CSV | Big-data migration reference / 大数据迁移参考 |
| **Enterprise Stack** (this phase) | dbt + PostgreSQL | PostgreSQL Tables | Production-ready warehouse / 生产就绪数仓 |

Relationship between dbt and the existing pipelines:

dbt 与现有主流程的关系：

- dbt models implement the **same business logic** as the Pandas and Spark pipelines.
- dbt 模型实现了与 Pandas 和 Spark 主流程 **相同的业务逻辑**。
- dbt outputs are materialized as PostgreSQL tables (persistent, queryable).
- dbt 输出物化为 PostgreSQL 表（持久化、可查询）。
- The Pandas and Spark pipelines remain untouched for reference.
- Pandas 和 Spark 主流程保持不变，作为参考。

---

## 3. Project Structure / 项目结构

```text
dbt/ecommerce_warehouse/
├── dbt_project.yml                    # Project configuration / 项目配置
├── profiles.yml.example               # PostgreSQL connection template / 连接配置模板
├── macros/
│   └── generate_schema_name.sql       # Schema name override macro / Schema 名称覆盖宏
├── models/
│   ├── sources.yml                    # ODS source definitions / ODS 源定义
│   ├── schema.yml                     # Model tests / 模型测试
│   ├── staging/                       # Staging models (views) / Staging 模型（视图）
│   │   ├── stg_customers.sql
│   │   ├── stg_orders.sql
│   │   ├── stg_order_items.sql
│   │   ├── stg_order_payments.sql
│   │   ├── stg_order_reviews.sql
│   │   ├── stg_products.sql
│   │   ├── stg_sellers.sql
│   │   └── stg_product_category_translation.sql
│   ├── dwd/
│   │   └── dwd_order_detail.sql       # DWD: order-level detail (table) / 订单明细
│   ├── dws/
│   │   └── dws_daily_order_summary.sql # DWS: daily summary (table) / 每日汇总
│   └── ads/
│       └── ads_daily_business_overview.sql # ADS: business overview (table) / 经营概览
└── README.md
```

---

## 4. Model Layers / 模型分层

### 4.1 Staging Layer / Staging 层

**Materialization: view** (no storage cost, always reflects source).

**物化策略：视图**（无存储成本，始终反映源数据）。

| Model / 模型 | Source / 源 | Purpose / 用途 |
|---|---|---|
| `stg_customers` | `ods.customers` | Type casting and column selection / 类型转换和列选择 |
| `stg_orders` | `ods.orders` | Timestamp casting, lowercase order_status / 时间戳转换，订单状态小写 |
| `stg_order_items` | `ods.order_items` | Cast price/freight to NUMERIC / 转换价格为数值类型 |
| `stg_order_payments` | `ods.order_payments` | Cast payment values / 转换支付金额 |
| `stg_order_reviews` | `ods.order_reviews` | **No deduplication** — preserves all raw rows / **不做去重** — 保留所有原始行 |
| `stg_products` | `ods.products` | Cast dimension columns / 转换维度列 |
| `stg_sellers` | `ods.sellers` | Type casting / 类型转换 |
| `stg_product_category_translation` | `ods.product_category_translation` | Pass-through / 直接传递 |

### 4.2 DWD Layer (Data Warehouse Detail) / DWD 层（明细数据层）

**Materialization: table** in `dwd` schema.

**物化策略：表**，位于 `dwd` schema。

Model: `dwd_order_detail`

| Step / 步骤 | Description / 说明 |
|---|---|
| 1. Item aggregation / 商品聚合 | Per-order: order_item_count, product_count, seller_count, total_product_amount, total_freight_amount |
| 2. Payment aggregation / 支付聚合 | Per-order: total_payment_amount, payment_type_count, max_payment_installments, main_payment_type |
| 3. Review aggregation / 评价聚合 | Per-order: average_review_score, review_count, has_review_comment |
| 4. Join / 关联 | LEFT JOIN orders + customers + item_agg + payment_agg + review_agg |
| 5. Derived fields / 派生字段 | purchase_date, purchase_month, delivery_days, estimated_delivery_days, delivery_delay_days, is_delivered, is_late_delivery |

**Duplicate review_id handling**: Reviews are aggregated by `order_id` (AVG score, COUNT reviews, MAX has_comment).

Duplicate `review_id` values collapse naturally within the `GROUP BY order_id` — no deduplication needed.

**重复 review_id 处理**：评价按 `order_id` 聚合（评分平均、评价计数、是否有留言取最大）。

重复的 `review_id` 在 `GROUP BY order_id` 过程中自然合并——无需额外去重。

### 4.3 DWS Layer (Data Warehouse Summary) / DWS 层（汇总数据层）

**Materialization: table** in `dws` schema.

**物化策略：表**，位于 `dws` schema。

Model: `dws_daily_order_summary`

| Step / 步骤 | Description / 说明 |
|---|---|
| 1. Prepare / 准备 | Filter null purchase_date, cast columns / 过滤空购买日期，转换列 |
| 2. Flag / 标记 | is_valid_order (not canceled/unavailable), is_paid_order (payment > 0), has_review (count > 0) |
| 3. Aggregate / 聚合 | GROUP BY purchase_date: COUNT, SUM, AVG |
| 4. Ratio metrics / 比率指标 | delivery_rate, late_delivery_rate, review_rate, review_comment_rate, aov, avg_product_amount, avg_freight_amount |

### 4.4 ADS Layer (Application Data Store) / ADS 层（应用数据层）

**Materialization: table** in `ads` schema.

**物化策略：表**，位于 `ads` schema。

Model: `ads_daily_business_overview`

| Feature / 功能 | SQL Technique / SQL 技术 | Description / 说明 |
|---|---|---|
| Field renaming / 字段重命名 | `purchase_date → stat_date` | Standardize field names for BI / 标准化字段名 |
| Derived rates / 派生比率 | `valid_order_rate = valid / total` | Business ratio metrics / 业务比率指标 |
| 7-day moving averages / 7日移动平均 | `AVG(col) OVER (ORDER BY date ROWS 6 PRECEDING)` | Trend smoothing / 趋势平滑 |
| Cumulative metrics / 累计指标 | `SUM(col) OVER (ORDER BY date UNBOUNDED PRECEDING)` | YTD-like totals / 类似年初累计 |
| Day-over-day changes / 日环比变化 | `LAG()` or `col - LAG(col)` | Daily trend analysis / 每日趋势分析 |
| Day-over-day rates / 日环比增长率 | `(col - LAG(col)) / LAG(col)` | Percentage change / 百分比变化 |

---

## 5. Duplicate review_id Strategy / 重复 review_id 策略

The raw Olist `order_reviews` dataset contains **814 duplicate review_id values** (99,224 total rows, 98,410 unique review_ids).

原始 Olist `order_reviews` 数据包含 **814 个重复的 review_id**（共 99,224 行，98,410 个唯一 review_id）。

| Layer / 层 | Strategy / 策略 |
|---|---|
| **ODS** (PostgreSQL) | No PRIMARY KEY on review_id. `ods_row_id BIGSERIAL` as technical PK. Duplicates preserved. |
| **Staging** (dbt view) | Keep all rows — no dedup, no unique constraint / 保留所有行——不去重，不设唯一约束 |
| **DWD** (dbt table) | Aggregate reviews by `order_id` — duplicates naturally collapse / 按 order_id 聚合评价——重复自然合并 |
| **schema.yml tests** | `review_id` is `not_null` but **NOT** `unique` / review_id 设为 not_null 但**不设** unique |

---

## 6. Custom Schema Logic / 自定义 Schema 逻辑

By default, dbt prefixes custom schemas with the target schema (e.g., `dbt_dev_dwd`).

默认情况下，dbt 会在自定义 schema 前加上目标 schema 前缀（例如 `dbt_dev_dwd`）。

A custom `generate_schema_name` macro in `macros/generate_schema_name.sql` overrides this behavior.

`macros/generate_schema_name.sql` 中的自定义 `generate_schema_name` 宏覆盖了这一默认行为。

The macro returns:

宏返回：

- `custom_schema_name` if provided (e.g., `dwd` → schema `dwd`)
- 如果提供了 `custom_schema_name`，直接使用（例如 `dwd` → schema `dwd`）
- `target.schema` if no custom schema (e.g., `dbt_dev`)
- 如果没有自定义 schema，使用 `target.schema`（例如 `dbt_dev`）

This ensures models land in the correct PostgreSQL schemas:

这确保模型落入正确的 PostgreSQL schema：

| Model / 模型 | Schema / Schema |
|---|---|
| `stg_*` (views) | `dbt_dev` (target schema) |
| `dwd_order_detail` | `dwd` |
| `dws_daily_order_summary` | `dws` |
| `ads_daily_business_overview` | `ads` |

---

## 7. Test Strategy / 测试策略

Tests are defined in `models/schema.yml`.

测试定义在 `models/schema.yml` 中。

| Test Type / 测试类型 | Applied to / 应用于 | Purpose / 目的 |
|---|---|---|
| `not_null` | Primary keys and required fields (order_id, customer_id, stat_date, etc.) | Ensure no NULLs in key columns / 确保关键列无空值 |
| `unique` | Truly unique columns (order_id, product_id, seller_id, purchase_date, stat_date) | Verify uniqueness / 验证唯一性 |
| `unique` (NOT applied) | `review_id` | Olist raw data has duplicates / Olist 原始数据有重复 |
| `accepted_values` | `order_status`, `payment_type`, `review_score` | Validate categorical values / 验证分类值 |

---

## 8. How to Run / 如何运行

### Prerequisites / 前置条件

```bat
pip install dbt-postgres
```

### Run dbt / 运行 dbt

```bat
cd dbt\ecommerce_warehouse

# Verify connection / 验证连接
dbt debug --profiles-dir .

# Run all models / 运行所有模型
dbt run --profiles-dir .

# Run all tests / 运行所有测试
dbt test --profiles-dir .

# Generate documentation / 生成文档 (optional / 可选)
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir .
```

### Expected outputs / 预期输出

| Model / 模型 | Schema | Materialization / 物化 |
|---|---|---|
| `dwd_order_detail` | `dwd` | Table |
| `dws_daily_order_summary` | `dws` | Table |
| `ads_daily_business_overview` | `ads` | Table |

---

## 9. Comparison with Pandas and Spark / 与 Pandas 和 Spark 的对比

| Aspect / 方面 | Pandas | Spark | dbt + PostgreSQL |
|---|---|---|---|
| Language / 语言 | Python | PySpark / Spark SQL | SQL |
| Storage / 存储 | CSV files | CSV files | PostgreSQL tables |
| Types / 类型 | Implicit (Pandas objects) | Explicit (Spark types) | Explicit (PostgreSQL types) |
| 7-day moving avg / 7日移动平均 | `.rolling(7).mean()` | `AVG() OVER (ROWS 6 PRECEDING)` | `AVG() OVER (ROWS 6 PRECEDING)` |
| Cumulative sum / 累计求和 | `.cumsum()` | `SUM() OVER (UNBOUNDED PRECEDING)` | `SUM() OVER (UNBOUNDED PRECEDING)` |
| Day-over-day / 日环比 | `.diff()`, `.pct_change()` | `LAG()`, `(val - LAG) / LAG` | `LAG()`, `(val - LAG) / LAG` |
| Safe divide / 安全除法 | `if d == 0: return 0` | `CASE WHEN d=0 THEN 0 ELSE n/d END` | `CASE WHEN d=0 THEN 0.0 ELSE n/d END` |
| Testing / 测试 | Manual / Python asserts | Manual / Python asserts | dbt `not_null`, `unique`, `accepted_values` |
| Docs / 文档 | Manual | Manual | dbt docs generate |

---

## 10. Summary / 总结

This dbt project adds a **production-ready SQL transformation layer** on top of PostgreSQL ODS tables.

本 dbt 项目在 PostgreSQL ODS 表之上增加了 **生产就绪的 SQL 转换层**。

Key design principles / 关键设计原则：

1. **SQL-first / SQL 优先**: All transformations are pure SQL / 所有转换都是纯 SQL
2. **Layer separation / 分层分离**: staging (view) → DWD (table) → DWS (table) → ADS (table)
3. **Raw data preservation / 原始数据保留**: No deduplication in ODS or staging / ODS 和 staging 不做去重
4. **Duplicate-tolerant design / 容重复设计**: `review_id` is not set as unique; aggregation handles duplicates naturally / review_id 不设唯一约束；聚合自然处理重复
5. **Automated testing / 自动化测试**: dbt built-in tests verify data quality / dbt 内置测试验证数据质量
6. **Parallel pipeline / 并行主流程**: dbt coexists with Pandas and Spark pipelines without modification / dbt 与 Pandas、Spark 主流程并行共存，互不修改