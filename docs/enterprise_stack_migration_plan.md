# Enterprise Stack Migration Plan / 企业级技术栈迁移规划

## 1. Purpose / 目的

This document describes the plan to upgrade the current CSV/Pandas/Spark offline data warehouse project into an enterprise-style warehouse project.

本文档说明将当前 CSV/Pandas/Spark 离线数仓项目升级为企业级数仓项目的规划。

The target technology stack is:

目标技术栈为：

| Component / 组件 | Tool / 工具 | Purpose / 用途 |
|---|---|---|
| Warehouse Database / 数仓数据库 | PostgreSQL | Persistent storage, SQL queries / 持久化存储、SQL 查询 |
| Transformation Layer / 转换层 | dbt (data build tool) | SQL-based modeling, version control / 基于 SQL 的建模、版本控制 |
| Orchestration / 调度 | Apache Airflow | DAG-based scheduling, monitoring / DAG 调度、监控 |
| BI Dashboard (Open Source) / BI 看板（开源） | Apache Superset | Web-based visualization, SQL exploration / 基于 Web 的可视化、SQL 探查 |
| BI Dashboard (Enterprise) / BI 看板（企业） | Microsoft Power BI | Desktop visualization, reporting / 桌面可视化、报表 |

---

## 2. Current Architecture / 当前架构

### 2.1 Current Implementation / 当前实现

The project currently has two parallel pipelines:

项目当前有两条并行主流程：

**Pandas Baseline Pipeline / Pandas 基准主流程:**

```text
Raw CSV Files
    ↓
Python/Pandas ODS Loading
    ↓
Python/Pandas DWD Building
    ↓
Python/Pandas DWS Building
    ↓
Python/Pandas ADS Building
    ↓
Data Quality Checks
    ↓
Dashboard Charts (Matplotlib)
```

**Spark SQL Migration Pipeline / Spark SQL 迁移主流程:**

```text
ODS CSV Files (from Pandas)
    ↓
PySpark DWD Building
    ↓
PySpark DWS Building
    ↓
PySpark ADS Building
    ↓
Pandas vs Spark Comparison
    ↓
Spark Pipeline
```

### 2.2 Current Storage / 当前存储

| Layer / 分层 | Storage / 存储 | Format / 格式 |
|---|---|---|
| Raw / 原始层 | Local CSV files | CSV |
| ODS / 原始数据层 | Local CSV files | CSV |
| DWD / 明细层 | Local CSV files | CSV |
| DWS / 汇总层 | Local CSV files | CSV |
| ADS / 应用层 | Local CSV files | CSV |

### 2.3 Current Limitations / 当前局限性

| Limitation / 局限性 | Description / 说明 |
|---|---|
| No persistent database / 无持久化数据库 | Data is regenerated on each pipeline run / 每次主流程运行都重新生成数据 |
| No SQL-based modeling / 无 SQL 建模 | Transformations are Python scripts, not versioned SQL / 转换是 Python 脚本，非版本化 SQL |
| No scheduling / 无调度 | Pipeline runs manually, not on schedule / 主流程手动运行，非定时调度 |
| No interactive BI / 无交互式 BI | Matplotlib charts are static images / Matplotlib 图表是静态图片 |
| No enterprise reporting / 无企业报表 | No Power BI integration / 无 Power BI 集成 |

---

## 3. Target Architecture / 目标架构

### 3.1 Target Implementation / 目标实现

```text
Raw CSV Files (Kaggle source)
    ↓
PostgreSQL ODS Tables
    ↓
dbt DWD Models (SQL)
    ↓
dbt DWS Models (SQL)
    ↓
dbt ADS Models (SQL)
    ↓
dbt Tests (Data Quality)
    ↓
Airflow DAG Scheduling
    ↓
PostgreSQL Final Tables
    ↓
Superset Dashboard (Web)
    ↓
Power BI Dashboard (Desktop)
```

### 3.2 Target Storage / 目标存储

| Layer / 分层 | Storage / 存储 | Format / 格式 |
|---|---|---|
| Raw / 原始层 | Local CSV files (unchanged) | CSV |
| ODS / 原始数据层 | PostgreSQL tables | Database tables |
| DWD / 明细层 | PostgreSQL tables (dbt materialized) | Database tables |
| DWS / 汇总层 | PostgreSQL tables (dbt materialized) | Database tables |
| ADS / 应用层 | PostgreSQL tables (dbt materialized) | Database tables |

### 3.3 Target Benefits / 目标优势

| Benefit / 优势 | Description / 说明 |
|---|---|
| Persistent storage / 持久化存储 | Data persists across sessions, supports incremental updates / 数据跨会话持久，支持增量更新 |
| SQL-based modeling / SQL 建模 | dbt models are versioned, testable SQL files / dbt 模型是版本化、可测试的 SQL 文件 |
| Automated scheduling / 自动调度 | Airflow DAGs run on schedule, with monitoring / Airflow DAG 定时运行，带监控 |
| Interactive BI / 交互式 BI | Superset provides SQL exploration and interactive charts / Superset 提供 SQL 探查和交互式图表 |
| Enterprise reporting / 企业报表 | Power BI enables professional dashboards and reports / Power BI 提供专业看板和报表 |

---

## 4. Why PostgreSQL Over MySQL / 为什么选择 PostgreSQL 而非 MySQL

### 4.1 Technical Comparison / 技术对比

| Feature / 特性 | PostgreSQL | MySQL |
|---|---|---|
| **Window Functions / 窗口函数** | Full support (ROW_NUMBER, LAG, LEAD, etc.) / 完全支持 | Limited support before 8.0 / 8.0 前支持有限 |
| **CTE (Common Table Expressions) / 公用表表达式** | Full support with WITH clause / 完全支持 WITH 子句 | Limited support before 8.0 / 8.0 前支持有限 |
| **Analytical Queries / 分析查询** | Excellent for OLAP-style aggregations / 优秀 OLAP 风格聚合 | More OLTP-oriented / 更偏向 OLTP |
| **dbt Compatibility / dbt 兼容性** | Excellent, well-tested adapter / 优秀，适配器测试完善 | Supported but less common / 支持但较少使用 |
| **Data Types / 数据类型** | Rich types (JSONB, ARRAY, etc.) / 丰富类型 | Basic types / 基础类型 |
| **Performance for Analytics / 分析性能** | Optimized for complex queries / 优化复杂查询 | Optimized for simple reads / 优化简单读取 |

### 4.2 Reason for This Project / 本项目选择原因

This project requires:

本项目需要：

1. **Window functions** for 7-day moving averages, cumulative metrics, and day-over-day calculations.
   **窗口函数**用于 7 日移动平均、累计指标和日环比计算。

2. **CTEs** for complex multi-step SQL transformations in dbt models.
   **CTE**用于 dbt 模型中的复杂多步骤 SQL 转换。

3. **dbt integration** which has excellent PostgreSQL adapter support.
   **dbt 集成**，PostgreSQL 适配器支持优秀。

4. **Analytical query patterns** typical in data warehouse scenarios.
   **分析查询模式**，典型的数仓场景。

**Conclusion: PostgreSQL is better suited for data warehouse and analytical workloads.**

**结论：PostgreSQL 更适合数仓和分析型工作负载。**

---

## 5. Migration Principles / 迁移原则

### 5.1 Preserve Existing Pipelines / 保留现有主流程

| Principle / 原则 | Description / 说明 |
|---|---|
| Keep Pandas baseline / 保留 Pandas 基准 | Pandas pipeline remains as local prototype reference / Pandas 主流程保留为本地原型参考 |
| Keep Spark migration / 保留 Spark 迁移 | Spark pipeline remains as big-data migration reference / Spark 主流程保留为大数据迁移参考 |
| No modification / 不修改 | Do not modify existing `scripts/*.py` files during enterprise migration / 企业迁移期间不修改现有 `scripts/*.py` 文件 |
| Parallel existence / 并行存在 | Enterprise stack adds a third pipeline option / 企业级技术栈添加第三个主流程选项 |

### 5.2 Files Not to Modify / 不修改的文件

During all phases of enterprise stack migration:

在企业级技术栈迁移的所有阶段：

```text
README.md (until final phase)
scripts/run_pipeline.py
scripts/run_spark_pipeline.py
scripts/check_raw_data.py
scripts/load_raw_to_ods.py
scripts/build_dwd_order_detail.py
scripts/build_dws_daily_order_summary.py
scripts/build_ads_daily_business_overview.py
scripts/run_data_quality_checks.py
scripts/build_dashboard_charts.py
scripts/spark_build_dwd_order_detail.py
scripts/spark_build_dws_daily_order_summary.py
scripts/spark_build_ads_daily_business_overview.py
scripts/compare_pandas_spark_outputs.py
```

---

## 6. Phase-by-Phase Migration Plan / 分阶段迁移规划

---

## Phase 1: PostgreSQL Warehouse Setup and ODS Loading

## 第一阶段：PostgreSQL 数仓搭建和 ODS 加载

### 1.1 Goal / 目标

Set up PostgreSQL database and load ODS tables from raw CSV files.

搭建 PostgreSQL 数据库并从原始 CSV 文件加载 ODS 表。

This phase establishes the foundation for the enterprise warehouse.

本阶段为企业级数仓建立基础。

### 1.2 Files to Create / 创建文件

| File / 文件 | Purpose / 用途 |
|---|---|
| `sql/postgres/create_ods_tables.sql` | ODS table creation DDL / ODS 表创建 DDL |
| `scripts/pg_load_raw_to_ods.py` | Python script to load raw CSV into PostgreSQL ODS tables / Python 脚本将原始 CSV 加载到 PostgreSQL ODS 表 |
| `scripts/pg_connection.py` | PostgreSQL connection helper module / PostgreSQL 连接辅助模块 |
| `scripts/pg_validate_ods.py` | ODS table validation script / ODS 表校验脚本 |
| `docs/pg_ods_design.md` | PostgreSQL ODS layer design document / PostgreSQL ODS 分层设计文档 |
| `.env.example` | Environment variable template for database credentials / 数据库凭据环境变量模板 |
| `requirements.txt` (update) | Add psycopg2, sqlalchemy (already has psycopg2-binary) / 添加 psycopg2、sqlalchemy |

### 1.3 Files Not to Modify / 不修改文件

```text
README.md
scripts/run_pipeline.py
scripts/load_raw_to_ods.py (Pandas baseline, keep unchanged)
All existing Pandas and Spark scripts
```

### 1.4 Expected Outputs / 预期输出

| Output / 输出 | Description / 说明 |
|---|---|
| PostgreSQL database `ecommerce_dw` | Database created / 数据库已创建 |
| PostgreSQL ODS tables | `ods_orders`, `ods_customers`, `ods_order_items`, `ods_order_payments`, `ods_order_reviews`, `ods_products`, `ods_sellers`, `ods_geolocation`, `ods_product_category_translation` |
| `docs/pg_ods_load_report.csv` | ODS loading report / ODS 加载报告 |
| `docs/pg_ods_validation_report.csv` | ODS validation report / ODS 校验报告 |

### 1.5 Validation Commands / 验证命令

```bat
# Set up PostgreSQL connection
# Setup database and ODS tables
python scripts\pg_load_raw_to_ods.py

# Validate ODS tables
python scripts\pg_validate_ods.py

# Check with SQL
psql -d ecommerce_dw -c "SELECT COUNT(*) FROM ods_orders;"
psql -d ecommerce_dw -c "SELECT COUNT(*) FROM ods_customers;"
```

### 1.6 Acceptance Criteria / 验收标准

| Criteria / 标准 | Requirement / 要求 |
|---|---|
| Database created / 数据库创建 | `ecommerce_dw` database exists in PostgreSQL |
| ODS tables created / ODS 表创建 | All 9 ODS tables created with correct columns |
| Data loaded / 数据加载 | Row counts match Pandas ODS CSV outputs |
| No modification / 无修改 | Existing Pandas `load_raw_to_ods.py` unchanged |
| Report generated / 报告生成 | `pg_ods_load_report.csv` and `pg_ods_validation_report.csv` generated |

---

## Phase 2: dbt Modeling for DWD, DWS, ADS

## 第二阶段：dbt 建模 DWD、DWS、ADS

### 2.1 Goal / 目标

Implement dbt project for DWD, DWS, and ADS layer transformations using SQL models.

使用 SQL 模型实现 dbt 项目进行 DWD、DWS、ADS 分层转换。

### 2.2 dbt Project Structure / dbt 项目结构

```text
dbt_ecommerce_dw/
│
├── dbt_project.yml
├── profiles.yml (PostgreSQL connection)
│
├── models/
│   ├── dwd/
│   │   ├── dwd_order_detail.sql
│   │   ├── schema.yml
│   │
│   ├── dws/
│   │   ├── dws_daily_order_summary.sql
│   │   ├── schema.yml
│   │
│   ├── ads/
│   │   ├── ads_daily_business_overview.sql
│   │   ├── schema.yml
│   │
│   └ staging/
│       ├── stg_orders.sql
│       ├── stg_customers.sql
│       ├── stg_order_items.sql
│       ├── stg_order_payments.sql
│       ├── stg_order_reviews.sql
│
├── tests/
│   ├── test_dwd_primary_key.sql
│   ├── test_dws_metrics.sql
│   ├── test_ads_metrics.sql
│
├── macros/
│   ├── safe_divide.sql
│
└ docs/
    ├── dwd_layer.md
    ├── dws_layer.md
    └ ads_layer.md
```

### 2.3 Files to Create / 创建文件

| File / 文件 | Purpose / 用途 |
|---|---|
| `dbt_ecommerce_dw/dbt_project.yml` | dbt project configuration / dbt 项目配置 |
| `dbt_ecommerce_dw/profiles.yml` | PostgreSQL connection profile / PostgreSQL 连接配置 |
| `dbt_ecommerce_dw/models/staging/*.sql` | Staging models for ODS tables / ODS 表的 staging 模型 |
| `dbt_ecommerce_dw/models/dwd/dwd_order_detail.sql` | DWD order detail model / DWD 订单明细模型 |
| `dbt_ecommerce_dw/models/dwd/schema.yml` | DWD schema and tests / DWD schema 和测试 |
| `dbt_ecommerce_dw/models/dws/dws_daily_order_summary.sql` | DWS daily summary model / DWS 每日汇总模型 |
| `dbt_ecommerce_dw/models/dws/schema.yml` | DWS schema and tests / DWS schema 和测试 |
| `dbt_ecommerce_dw/models/ads/ads_daily_business_overview.sql` | ADS business overview model / ADS 经营概览模型 |
| `dbt_ecommerce_dw/models/ads/schema.yml` | ADS schema and tests / ADS schema 和测试 |
| `dbt_ecommerce_dw/macros/safe_divide.sql` | Safe division macro / 安全除法宏 |
| `dbt_ecommerce_dw/tests/*.sql` | Custom data tests / 自定义数据测试 |
| `docs/dbt_modeling_design.md` | dbt modeling design document / dbt 建模设计文档 |
| `requirements.txt` (update) | Add dbt-postgres / 添加 dbt-postgres |

### 2.4 Files Not to Modify / 不修改文件

```text
README.md
scripts/run_pipeline.py
All existing Pandas and Spark scripts
```

### 2.5 Expected Outputs / 预期输出

| Output / 输出 | Description / 说明 |
|---|---|
| PostgreSQL DWD table | `dwd_order_detail` created by dbt model |
| PostgreSQL DWS table | `dws_daily_order_summary` created by dbt model |
| PostgreSQL ADS table | `ads_daily_business_overview` created by dbt model |
| `dbt_ecommerce_dw/target/run_results.json` | dbt run results |
| `docs/dbt_comparison_report.csv` | Comparison with Pandas/Spark outputs |

### 2.6 Validation Commands / 验证命令

```bat
# Install dbt
pip install dbt-postgres

# Initialize dbt project (if not created)
dbt init dbt_ecommerce_dw

# Run dbt models
cd dbt_ecommerce_dw
dbt run

# Run dbt tests
dbt test

# Generate documentation
dbt docs generate
dbt docs serve

# Verify tables
psql -d ecommerce_dw -c "SELECT COUNT(*) FROM dwd_order_detail;"
psql -d ecommerce_dw -c "SELECT COUNT(*) FROM dws_daily_order_summary;"
psql -d ecommerce_dw -c "SELECT COUNT(*) FROM ads_daily_business_overview;"
```

### 2.7 Acceptance Criteria / 验收标准

| Criteria / 标准 | Requirement / 要求 |
|---|---|
| dbt project created / dbt 项目创建 | `dbt_ecommerce_dw` directory exists |
| dbt run succeeds / dbt 运行成功 | `dbt run` completes without errors |
| dbt tests pass / dbt 测试通过 | `dbt test` shows all tests passed |
| DWD table created / DWD 表创建 | Row count matches Pandas DWD output |
| DWS table created / DWS 表创建 | Row count matches Pandas DWS output |
| ADS table created / ADS 表创建 | Row count matches Pandas ADS output |
| Documentation generated / 文档生成 | `dbt docs generate` produces documentation |
| No modification / 无修改 | Existing Pandas/Spark scripts unchanged |

---

## Phase 3: Airflow Orchestration

## 第三阶段：Airflow 调度编排

### 3.1 Goal / 目标

Implement Apache Airflow DAG to orchestrate the enterprise warehouse pipeline.

实现 Apache Airflow DAG 编排企业级数仓主流程。

### 3.2 Airflow DAG Structure / Airflow DAG 结构

```text
airflow/
│
├── dags/
│   ├── ecommerce_dw_pipeline.py
│
├── config/
│   ├── airflow.cfg
│
└ plugins/
    ├── pg_operators.py (optional custom operators)
```

### 3.3 DAG Tasks / DAG 任务

```text
Task 1: check_raw_data_files
    ↓
Task 2: load_raw_to_ods_pg
    ↓
Task 3: dbt_run_staging
    ↓
Task 4: dbt_run_dwd
    ↓
Task 5: dbt_run_dws
    ↓
Task 6: dbt_run_ads
    ↓
Task 7: dbt_test_all
    ↓
Task 8: generate_reports
```

### 3.4 Files to Create / 创建文件

| File / 文件 | Purpose / 用途 |
|---|---|
| `airflow/dags/ecommerce_dw_pipeline.py` | Main DAG definition / 主 DAG 定义 |
| `airflow/config/airflow.cfg` | Airflow configuration template / Airflow 配置模板 |
| `scripts/airflow_setup.py` | Airflow initialization helper / Airflow 初始化辅助脚本 |
| `docs/airflow_orchestration_design.md` | Airflow orchestration design document / Airflow 调度设计文档 |
| `requirements.txt` (update) | Add apache-airflow, apache-airflow-providers-postgres / 添加相关依赖 |

### 3.5 Files Not to Modify / 不修改文件

```text
README.md
scripts/run_pipeline.py
scripts/run_spark_pipeline.py
All existing Pandas and Spark scripts
dbt models (if already created)
```

### 3.6 Expected Outputs / 预期输出

| Output / 输出 | Description / 说明 |
|---|---|
| Airflow DAG registered / DAG 注册 | `ecommerce_dw_pipeline` DAG visible in Airflow UI |
| DAG execution success / DAG 执行成功 | Manual trigger completes all tasks |
| Task logs / 任务日志 | Airflow logs for each task execution |
| `docs/airflow_pipeline_run_report.csv` | Airflow pipeline run report |

### 3.7 Validation Commands / 验证命令

```bat
# Initialize Airflow database
airflow db init

# Create admin user
airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com

# Start Airflow webserver
airflow webserver --port 8080

# Start Airflow scheduler
airflow scheduler

# Trigger DAG manually
airflow dags trigger ecommerce_dw_pipeline

# Check DAG status
airflow dags list
airflow tasks list ecommerce_dw_pipeline
```

### 3.8 Acceptance Criteria / 验收标准

| Criteria / 标准 | Requirement / 要求 |
|---|---|
| Airflow installed / Airflow 安装 | `airflow version` shows correct version |
| DAG registered / DAG 注册 | DAG visible in Airflow UI at localhost:8080 |
| DAG runs manually / DAG 手动运行 | Manual trigger completes all tasks successfully |
| Task dependencies / 任务依赖 | Tasks run in correct order with proper dependencies |
| No modification / 无修改 | Existing Pandas/Spark/dbt files unchanged |

---

## Phase 4: Superset Dashboard

## 第四阶段：Superset 看板

### 4.1 Goal / 目标

Implement Apache Superset for interactive web-based BI dashboard.

实现 Apache Superset 用于交互式 Web BI 看板。

### 4.2 Superset Configuration / Superset 配置

```text
superset/
│
├── superset_config.py
├── dashboards/
│   ├── ecommerce_daily_business.json (exported dashboard)
│
└ charts/
    ├── gmv_trend.json
    ├── order_count_trend.json
    ├── aov_trend.json
    ├── delivery_performance.json
    ├── review_performance.json
```

### 4.3 Files to Create / 创建文件

| File / 文件 | Purpose / 用途 |
|---|---|
| `superset/superset_config.py` | Superset configuration file / Superset 配置文件 |
| `scripts/superset_setup.py` | Superset initialization and dataset creation / Superset 初始化和数据集创建 |
| `scripts/superset_create_dashboard.py` | Dashboard and chart creation script / 看板和图表创建脚本 |
| `docs/superset_dashboard_design.md` | Superset dashboard design document / Superset 看板设计文档 |
| `requirements.txt` (update) | Add apache-superset / 添加 apache-superset |

### 4.4 Files Not to Modify / 不修改文件

```text
README.md
All existing scripts (Pandas, Spark, dbt, Airflow)
```

### 4.5 Expected Outputs / 预期输出

| Output / 输出 | Description / 说明 |
|---|---|
| Superset running / Superset 运行 | Web UI accessible at localhost:8088 |
| PostgreSQL database connected / 数据库连接 | `ecommerce_dw` database connected as data source |
| Datasets created / 数据集创建 | ADS table registered as dataset |
| Charts created / 图表创建 | GMV trend, order count, AOV, delivery, review charts |
| Dashboard created / 看板创建 | "E-commerce Daily Business Overview" dashboard |

### 4.6 Validation Commands / 验证命令

```bat
# Initialize Superset
pip install apache-superset
superset db upgrade

# Create admin user
superset fab create-admin --username admin --firstname Admin --lastname User --email admin@superset.com --password admin

# Initialize Superset
superset init

# Start Superset
superset run -p 8088 --with-threads --reload

# Access dashboard
# Open browser: http://localhost:8088
```

### 4.7 Acceptance Criteria / 验收标准

| Criteria / 标准 | Requirement / 要求 |
|---|---|
| Superset running / Superset 运行 | Web UI accessible at localhost:8088 |
| Database connected / 数据库连接 | PostgreSQL `ecommerce_dw` visible as data source |
| Dataset created / 数据集创建 | ADS table available for chart creation |
| Dashboard created / 看板创建 | "E-commerce Daily Business Overview" dashboard exists |
| Interactive charts / 交互式图表 | Charts support filtering and drill-down |
| No modification / 无修改 | Existing scripts unchanged |

---

## Phase 5: Power BI Dashboard

## 第五阶段：Power BI 看板

### 5.1 Goal / 目标

Create Microsoft Power BI dashboard for enterprise reporting.

创建 Microsoft Power BI 看板用于企业报表。

### 5.2 Power BI Structure / Power BI 结构

```text
powerbi/
│
├── EcommerceDailyBusiness.pbix
├── data_source_config.txt
├── screenshots/
│   ├── dashboard_overview.png
│   ├── gmv_analysis.png
│   ├── order_analysis.png
│   ├── delivery_analysis.png
│   ├── review_analysis.png
│
└ README.md (Power BI section)
```

### 5.3 Files to Create / 创建文件

| File / 文件 | Purpose / 用途 |
|---|---|
| `powerbi/EcommerceDailyBusiness.pbix` | Power BI Desktop file / Power BI Desktop 文件 |
| `powerbi/data_source_config.txt` | PostgreSQL connection instructions / PostgreSQL 连接说明 |
| `powerbi/screenshots/*.png` | Dashboard screenshots for GitHub display / GitHub 展示的看板截图 |
| `docs/powerbi_dashboard_design.md` | Power BI dashboard design document / Power BI 看板设计文档 |

### 5.4 Files Not to Modify / 不修改文件

```text
README.md (until Phase 6)
All existing scripts (Pandas, Spark, dbt, Airflow, Superset)
```

### 5.5 Expected Outputs / 预期输出

| Output / 输出 | Description / 说明 |
|---|---|
| Power BI file / Power BI 文件 | `EcommerceDailyBusiness.pbix` created |
| PostgreSQL connection / PostgreSQL 连接 | Direct query mode connected to PostgreSQL |
| Dashboard pages / 看板页面 | Overview, GMV Analysis, Order Analysis, Delivery, Review |
| Screenshots / 截图 | Dashboard screenshots saved for documentation |

### 5.6 Validation Commands / 验证命令

Power BI Desktop is a GUI application. Manual steps:

Power BI Desktop 是图形界面应用。手动步骤：

1. Open Power BI Desktop.
   打开 Power BI Desktop。

2. Connect to PostgreSQL database `ecommerce_dw`.
   连接到 PostgreSQL 数据库 `ecommerce_dw`。

3. Import ADS table `ads_daily_business_overview`.
   导入 ADS 表 `ads_daily_business_overview`。

4. Create dashboard pages and charts.
   创建看板页面和图表。

5. Save as `powerbi/EcommerceDailyBusiness.pbix`.
   保存为 `powerbi/EcommerceDailyBusiness.pbix`。

6. Export screenshots for documentation.
   导出截图用于文档。

### 5.7 Acceptance Criteria / 验收标准

| Criteria / 标准 | Requirement / 要求 |
|---|---|
| Power BI file created / Power BI 文件创建 | `EcommerceDailyBusiness.pbix` exists |
| PostgreSQL connected / PostgreSQL 连接 | Data refreshes from PostgreSQL |
| Dashboard pages created / 看板页面创建 | At least 3 dashboard pages with charts |
| Screenshots saved / 截图保存 | Dashboard screenshots saved in `powerbi/screenshots/` |
| No modification / 无修改 | Existing scripts unchanged |

---

## Phase 6: Final README and GitHub Cleanup

## 第六阶段：最终 README 和 GitHub 清理

### 6.1 Goal / 目标

Update README to document the complete enterprise stack migration.

更新 README 文档完整的企业级技术栈迁移。

Clean up repository and prepare for GitHub presentation.

清理仓库并准备 GitHub 展示。

### 6.2 Files to Create or Modify / 创建或修改文件

| File / 文件 | Action / 操作 | Purpose / 用途 |
|---|---|---|
| `README.md` | **Modify** (final update) | Document enterprise stack / 文档企业级技术栈 |
| `docs/enterprise_stack_summary.md` | Create | Enterprise stack summary / 企业级技术栈总结 |
| `.gitignore` | Modify (if needed) | Ensure correct files are ignored / 确保正确文件被忽略 |
| `powerbi/README.md` | Create | Power BI section README / Power BI 部分 README |

### 6.3 Files Not to Modify / 不修改文件

```text
scripts/run_pipeline.py (Pandas baseline, preserve)
scripts/run_spark_pipeline.py (Spark migration, preserve)
All dbt models
Airflow DAGs
```

### 6.4 Expected Outputs / 预期输出

| Output / 输出 | Description / 说明 |
|---|---|
| Updated README / 更新 README | README reflects enterprise stack architecture |
| Complete documentation / 完整文档 | All phases documented |
| Clean repository / 清理仓库 | No generated data files tracked |
| Ready for GitHub / GitHub 准备 | Project ready for public repository |

### 6.5 Validation Commands / 验证命令

```bat
# Check git status
git status

# Verify no data files are tracked
git ls-files data/

# Review README sections
cat README.md | grep "## "

# Final review of project structure
tree -L 2
```

### 6.6 Acceptance Criteria / 验收标准

| Criteria / 标准 | Requirement / 要求 |
|---|---|
| README updated / README 更新 | README includes enterprise stack architecture |
| No data files tracked / 无数据文件跟踪 | `data/` files not in git |
| All documentation complete / 文档完整 | All phase docs exist |
| Pandas pipeline preserved / Pandas 保留 | `run_pipeline.py` unchanged |
| Spark pipeline preserved / Spark 保留 | `run_spark_pipeline.py` unchanged |
| Enterprise stack documented / 企业级文档 | dbt, Airflow, Superset, Power BI documented |

---

## 7. Final Target Technology Stack / 最终目标技术栈

| Layer / 分层 | Tool / 工具 | Description / 说明 |
|---|---|---|
| Database / 数据库 | PostgreSQL 14+ | Warehouse storage, SQL engine |
| Modeling / 建模 | dbt 1.5+ | SQL-based transformation, version control |
| Scheduling / 调度 | Apache Airflow 2.5+ | DAG orchestration, monitoring |
| BI (Web) / BI (Web) | Apache Superset 2.0+ | Interactive dashboards, SQL exploration |
| BI (Desktop) / BI (桌面) | Microsoft Power BI | Enterprise reporting, presentations |
| Python / Python | Python 3.10+ | Helper scripts, data loading |

---

## 8. Preservation Strategy / 保留策略

### 8.1 Three Pipeline Options / 三个主流程选项

After enterprise migration, the project will have three pipeline options:

企业级迁移完成后，项目将有三个主流程选项：

| Pipeline / 主流程 | Run Command / 运行命令 | Purpose / 用途 |
|---|---|---|
| **Pandas Baseline** / Pandas 基准 | `python scripts\run_pipeline.py` | Local CSV prototype, learning reference / 本地 CSV 原型，学习参考 |
| **Spark Migration** / Spark 迁移 | `python scripts\run_spark_pipeline.py` | Big-data migration reference / 大数据迁移参考 |
| **Enterprise Stack** / 企业级 | `airflow dags trigger ecommerce_dw_pipeline` | Production-ready pipeline / 生产就绪主流程 |

### 8.2 Value of Each Pipeline / 每个主流程的价值

| Pipeline / 主流程 | Interview Value / 面试价值 |
|---|---|
| Pandas / Pandas | Demonstrates local prototype and baseline development / 展示本地原型和基准开发 |
| Spark / Spark | Demonstrates big-data migration thinking / 展示大数据迁移思维 |
| Enterprise / 企业级 | Demonstrates production-ready stack (dbt, Airflow, Superset) / 展示生产就绪技术栈 |

---

## 9. Timeline Estimate / 时间估算

| Phase / 阶段 | Estimated Time / 预估时间 |
|---|---|
| Phase 1: PostgreSQL / PostgreSQL | 1-2 days / 1-2 天 |
| Phase 2: dbt / dbt | 2-3 days / 2-3 天 |
| Phase 3: Airflow / Airflow | 1-2 days / 1-2 天 |
| Phase 4: Superset / Superset | 1-2 days / 1-2 天 |
| Phase 5: Power BI / Power BI | 1 day / 1 天 |
| Phase 6: Documentation / 文档 | 1 day / 1 天 |
| **Total** / 总计 | **7-11 days** / **7-11 天** |

---

## 10. Summary / 总结

This plan describes a comprehensive migration from CSV/Pandas/Spark local warehouse to an enterprise-style warehouse using PostgreSQL, dbt, Airflow, Superset, and Power BI.

本规划说明从 CSV/Pandas/Spark 本地数仓迁移到使用 PostgreSQL、dbt、Airflow、Superset、Power BI 的企业级数仓。

Key principles:

关键原则：

1. Preserve existing Pandas and Spark pipelines as reference.
   保留现有 Pandas 和 Spark 主流程作为参考。

2. Use PostgreSQL for warehouse database (better for analytical queries).
   使用 PostgreSQL 作为数仓数据库（更适合分析查询）。

3. Use dbt for SQL-based modeling (version control, testing).
   使用 dbt 进行 SQL 建模（版本控制、测试）。

4. Use Airflow for production scheduling.
   使用 Airflow 进行生产调度。

5. Use Superset for interactive web dashboards.
   使用 Superset 进行交互式 Web 看板。

6. Use Power BI for enterprise reporting.
   使用 Power BI 进行企业报表。

The migration will result in a portfolio-ready project demonstrating:

迁移后将形成一个适合作品集展示的项目，展示：

- Local prototype (Pandas)
- Big-data migration (Spark)
- Production stack (PostgreSQL + dbt + Airflow + Superset + Power BI)