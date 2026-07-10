# PostgreSQL Warehouse Setup / PostgreSQL 数仓搭建说明

## 1. Purpose / 目的

This document describes how to set up PostgreSQL as the warehouse database for the e-commerce offline data warehouse project.

本文档说明如何为电商离线数仓项目搭建 PostgreSQL 作为数仓数据库。

PostgreSQL will serve as the persistent storage for all warehouse layers (ODS, DWD, DWS, ADS).

PostgreSQL 将作为所有数仓分层（ODS、DWD、DWS、ADS）的持久化存储。

---

## 2. Why PostgreSQL / 为什么选择 PostgreSQL

PostgreSQL is chosen over MySQL for this data warehouse project for the following reasons:

本项目选择 PostgreSQL 而非 MySQL 作为数仓数据库，原因如下：

| Feature / 特性 | PostgreSQL | MySQL |
|---|---|---|
| Window Functions / 窗口函数 | Full support (ROW_NUMBER, LAG, LEAD, etc.) / 完全支持 | Limited before 8.0 / 8.0 前支持有限 |
| CTE (WITH clause) / 公用表表达式 | Full support / 完全支持 | Limited before 8.0 / 8.0 前支持有限 |
| Analytical Queries / 分析查询 | Excellent for OLAP-style aggregations / 优秀 OLAP 风格聚合 | More OLTP-oriented / 更偏向 OLTP |
| dbt Compatibility / dbt 兼容性 | Excellent adapter support / 优秀适配器支持 | Supported but less common / 支持但较少使用 |
| Data Types / 数据类型 | Rich types (JSONB, ARRAY) / 丰富类型 | Basic types / 基础类型 |

This project requires window functions for 7-day moving averages, cumulative metrics, and day-over-day calculations.

本项目需要窗口函数用于 7 日移动平均、累计指标和日环比计算。

---

## 3. Docker PostgreSQL Setup / Docker PostgreSQL 搭建

### 3.1 Prerequisites / 前置条件

- Docker Desktop installed on Windows
- Docker Desktop 在 Windows 上已安装

Check Docker installation:

检查 Docker 安装：

```bat
docker --version
docker compose version
```

### 3.2 PostgreSQL Configuration / PostgreSQL 配置

The PostgreSQL configuration is defined in `docker-compose.postgres.yml`:

PostgreSQL 配置定义在 `docker-compose.postgres.yml`：

| Parameter / 参数 | Value / 值 |
|---|---|
| Image / 镜像 | `postgres:14-alpine` |
| Database name / 数据库名 | `ecommerce_warehouse` |
| User / 用户 | `warehouse_user` |
| Password / 密码 | `warehouse_pass` |
| Port / 端口 | `5432` |
| Volume / 卷 | `postgres_data` (persistent) |

### 3.3 Start PostgreSQL / 启动 PostgreSQL

```bat
docker compose -f docker-compose.postgres.yml up -d
```

### 3.4 Check PostgreSQL Status / 检查 PostgreSQL 状态

```bat
docker compose -f docker-compose.postgres.yml ps
```

Expected output:

预期输出：

```text
NAME                          STATUS    PORTS
ecommerce_warehouse_postgres  running   0.0.0.0:5432->5432/tcp
```

### 3.5 Stop PostgreSQL / 停止 PostgreSQL

```bat
docker compose -f docker-compose.postgres.yml down
```

To remove the volume (reset database):

删除卷（重置数据库）：

```bat
docker compose -f docker-compose.postgres.yml down -v
```

---

## 4. Schema Design / Schema 设计

### 4.1 Warehouse Schemas / 数仓 Schema

| Schema / Schema | Purpose / 用途 |
|---|---|
| `ods` | Operational Data Store - raw business data / 原始数据层 |
| `dwd` | Data Warehouse Detail - cleaned detail data / 明细数据层 |
| `dws` | Data Warehouse Summary - aggregated data / 汇总数据层 |
| `ads` | Application Data Store - dashboard-ready data / 应用数据层 |

### 4.2 Create Schemas / 创建 Schema

Schemas are created by `sql/postgres/create_schemas.sql`:

Schema 由 `sql/postgres/create_schemas.sql` 创建：

```sql
CREATE SCHEMA IF NOT EXISTS ods;
CREATE SCHEMA IF NOT EXISTS dwd;
CREATE SCHEMA IF NOT EXISTS dws;
CREATE SCHEMA IF NOT EXISTS ads;
```

---

## 5. ODS Table List / ODS 表列表

| Schema | Table / 表 | Source File / 来源文件 |
|---|---|---|
| `ods` | `customers` | `olist_customers_dataset.csv` |
| `ods` | `orders` | `olist_orders_dataset.csv` |
| `ods` | `order_items` | `olist_order_items_dataset.csv` |
| `ods` | `order_payments` | `olist_order_payments_dataset.csv` |
| `ods` | `order_reviews` | `olist_order_reviews_dataset.csv` |
| `ods` | `products` | `olist_products_dataset.csv` |
| `ods` | `sellers` | `olist_sellers_dataset.csv` |
| `ods` | `geolocation` | `olist_geolocation_dataset.csv` |
| `ods` | `product_category_translation` | `product_category_name_translation.csv` |

### 5.1 ODS Table Columns / ODS 表字段

Each ODS table includes:

每个 ODS 表包含：

- **Original columns** from the raw CSV file
- **原始字段**来自原始 CSV 文件
- **Technical fields**:
- **技术字段**：
  - `loaded_at TIMESTAMP` - When the record was loaded / 记录加载时间
  - `dt DATE` - Date when the record was loaded / 记录加载日期

---

## 6. How to Load Raw CSV to PostgreSQL ODS / 如何加载原始 CSV 到 PostgreSQL ODS

### 6.1 Ensure PostgreSQL is Running / 确保 PostgreSQL 运行

```bat
docker compose -f docker-compose.postgres.yml up -d
```

### 6.2 Ensure Raw CSV Files Exist / 确保原始 CSV 文件存在

Raw CSV files should be in:

原始 CSV 文件应在：

```text
data/raw/
```

Required files:

必需文件：

- `olist_customers_dataset.csv`
- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_order_payments_dataset.csv`
- `olist_order_reviews_dataset.csv`
- `olist_products_dataset.csv`
- `olist_sellers_dataset.csv`
- `olist_geolocation_dataset.csv`
- `product_category_name_translation.csv`

### 6.3 Run Load Script / 运行加载脚本

```bat
python scripts\load_raw_to_postgres_ods.py
```

### 6.4 Expected Output / 预期输出

```
[INFO] Loading Raw CSV Files to PostgreSQL ODS Tables
[INFO] Validating raw CSV files...
[OK] All 9 raw CSV files found.
[INFO] Connecting to PostgreSQL: localhost:5432/ecommerce_warehouse
[OK] PostgreSQL connection successful.
[INFO] Setting up schemas and tables...
[OK] Schemas and tables setup completed.
[INFO] Loading: olist_customers_dataset.csv -> ods.customers
[OK] ods.customers: 99441 rows loaded (match)
...
[LOAD SUMMARY]
Total tables: 9
Passed: 9
Failed: 0
[DONE] All ODS tables loaded successfully.
```

---

## 7. How to Check ODS Loading / 如何检查 ODS 加载

### 7.1 Run Check Script / 运行检查脚本

```bat
python scripts\check_postgres_ods.py
```

### 7.2 Expected Output / 预期输出

```
[INFO] PostgreSQL ODS Table Check
[OK] PostgreSQL connection successful.
[INFO] Running ODS table checks...
  Schema ods: PASS
  Table ods.customers exists: PASS
  Table ods.customers row count: 99441 (PASS)
...
[CHECK SUMMARY]
Total checks: 40
Passed: 40
Failed: 0
[DONE] All ODS checks passed.
```

### 7.3 Check Reports / 检查报告

| Report / 报告 | Description / 说明 |
|---|---|
| `docs/postgres_ods_load_report.csv` | Load statistics for each table / 每个表的加载统计 |
| `docs/postgres_ods_check_report.csv` | Detailed check results / 详细检查结果 |
| `docs/postgres_ods_check_summary.md` | Bilingual check summary / 双语检查总结 |

---

## 8. Manual PostgreSQL Queries / 手动 PostgreSQL 查询

### 8.1 Connect to PostgreSQL / 连接 PostgreSQL

Using psql (if installed):

使用 psql（如已安装）：

```bat
psql -h localhost -p 5432 -U warehouse_user -d ecommerce_warehouse
```

Password: `warehouse_pass`

密码：`warehouse_pass`

### 8.2 Check Schemas / 检查 Schema

```sql
SELECT schema_name FROM information_schema.schemata WHERE schema_name IN ('ods', 'dwd', 'dws', 'ads');
```

### 8.3 Check Tables / 检查表

```sql
SELECT table_schema, table_name 
FROM information_schema.tables 
WHERE table_schema = 'ods';
```

### 8.4 Check Row Counts / 检查行数

```sql
SELECT COUNT(*) FROM ods.customers;
SELECT COUNT(*) FROM ods.orders;
SELECT COUNT(*) FROM ods.order_items;
SELECT COUNT(*) FROM ods.order_payments;
SELECT COUNT(*) FROM ods.order_reviews;
SELECT COUNT(*) FROM ods.products;
SELECT COUNT(*) FROM ods.sellers;
SELECT COUNT(*) FROM ods.geolocation;
SELECT COUNT(*) FROM ods.product_category_translation;
```

---

## 9. Output Reports / 输出报告

### 9.1 Load Report / 加载报告

`docs/postgres_ods_load_report.csv` contains:

包含以下字段：

| Column / 字段 | Description / 说明 |
|---|---|
| `csv_file` | Source CSV file name / 来源 CSV 文件名 |
| `schema` | Target schema / 目标 schema |
| `table` | Target table name / 目标表名 |
| `full_table_name` | Full table name (schema.table) / 完整表名 |
| `raw_row_count` | Row count in CSV file / CSV 文件行数 |
| `raw_column_count` | Column count in CSV file / CSV 文件列数 |
| `loaded_row_count` | Row count loaded to PostgreSQL / 加载到 PostgreSQL 的行数 |
| `row_count_match` | Whether counts match / 行数是否匹配 |
| `status` | PASS or FAIL / 状态 |
| `loaded_at` | Load timestamp / 加载时间戳 |

### 9.2 Check Report / 检查报告

`docs/postgres_ods_check_report.csv` contains:

包含以下字段：

| Column / 字段 | Description / 说明 |
|---|---|
| `check_type` | Type of check (schema_exists, table_exists, etc.) / 检查类型 |
| `schema` | Schema name / Schema 名 |
| `table` | Table name / 表名 |
| `column` | Column name (for column checks) / 列名 |
| `expected` | Expected value / 预期值 |
| `actual` | Actual value / 实际值 |
| `status` | PASS or FAIL / 状态 |
| `message` | Check message / 检查消息 |

---

## 10. Common Windows/Docker Troubleshooting / Windows/Docker 常见问题排查

### 10.1 Docker Desktop Not Running / Docker Desktop 未运行

Error message:

错误信息：

```
error during connect: This error may indicate that the docker daemon is not running
```

Solution:

解决方案：

- Start Docker Desktop manually
- 手动启动 Docker Desktop

### 10.2 Port 5432 Already in Use / 端口 5432 已被占用

Error message:

错误信息：

```
Error starting userland proxy: listen tcp 0.0.0.0:5432: bind: address already in use
```

Solution:

解决方案：

- Check if PostgreSQL is already installed locally
- 检查是否已安装本地 PostgreSQL

```bat
netstat -ano | findstr :5432
```

- Stop local PostgreSQL service or change Docker port
- 停止本地 PostgreSQL 服务或更改 Docker 端口

### 10.3 Volume Already Exists / 卷已存在

If you want to reset the database:

如需重置数据库：

```bat
docker compose -f docker-compose.postgres.yml down -v
docker compose -f docker-compose.postgres.yml up -d
```

### 10.4 Connection Refused / 连接被拒绝

Python script error:

Python 脚本错误：

```
OperationalError: could not connect to server
```

Solution:

解决方案：

- Wait a few seconds after starting Docker for PostgreSQL to initialize
- Docker 启动后等待几秒让 PostgreSQL 初始化
- Check Docker container status:
- 检查 Docker 容器状态：

```bat
docker compose -f docker-compose.postgres.yml ps
```

### 10.5 Permission Denied / 权限被拒绝

If you encounter permission errors with volumes:

如遇到卷权限错误：

- On Windows, Docker Desktop typically handles permissions automatically
- Windows 上 Docker Desktop 通常自动处理权限

---

## 11. Environment Variables / 环境变量

The scripts support environment variables for database connection:

脚本支持数据库连接的环境变量：

| Variable / 变量 | Default / 默认值 | Description / 说明 |
|---|---|---|
| `POSTGRES_HOST` | `localhost` | PostgreSQL host / PostgreSQL 主机 |
| `POSTGRES_PORT` | `5432` | PostgreSQL port / PostgreSQL 端口 |
| `POSTGRES_DB` | `ecommerce_warehouse` | Database name / 数据库名 |
| `POSTGRES_USER` | `warehouse_user` | Database user / 数据库用户 |
| `POSTGRES_PASSWORD` | `warehouse_pass` | Database password / 数据库密码 |

To use custom values:

使用自定义值：

```bat
set POSTGRES_HOST=192.168.1.100
python scripts\load_raw_to_postgres_ods.py
```

---

## 12. Summary / 总结

This phase establishes PostgreSQL as the warehouse database:

本阶段建立了 PostgreSQL 作为数仓数据库：

- Docker PostgreSQL container setup
- Docker PostgreSQL 容器搭建

- Schemas created: `ods`, `dwd`, `dws`, `ads`
- Schema 创建：`ods`、`dwd`、`dws`、`ads`

- 9 ODS tables loaded with raw CSV data
- 9 个 ODS 表加载原始 CSV 数据

- Automated validation and reporting
- 自动化校验和报告生成

This forms the foundation for the next phase: dbt modeling for DWD, DWS, and ADS.

这为下一阶段奠定了基础：dbt 建模 DWD、DWS、ADS。