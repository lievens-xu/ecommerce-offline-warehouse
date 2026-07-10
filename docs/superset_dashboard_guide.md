# Superset Dashboard Guide / Superset 看板指南

## 1. Purpose / 目的

This document describes how to set up Apache Superset as a BI dashboard layer for the e-commerce offline data warehouse enterprise stack.

本文档说明如何搭建 Apache Superset 作为电商离线数仓企业级技术栈的 BI 看板层。

Superset connects to the PostgreSQL warehouse and provides interactive visualization for the `ads.ads_daily_business_overview` table.

Superset 连接到 PostgreSQL 数仓，为 `ads.ads_daily_business_overview` 表提供交互式可视化。

---

## 2. Architecture / 架构

```text
┌────────────────── Docker Container ──────────────────┐
│                                                       │
│  ┌─────────────────────────────────────────────┐      │
│  │  Apache Superset 4.1.1                      │      │
│  │  - Web UI: http://localhost:8088             │      │
│  │  - Metadata: SQLite (persisted volume)       │      │
│  │  - Admin: admin / admin (first login)        │      │
│  └──────────────────┬──────────────────────────┘      │
│                     │                                  │
│    host.docker.internal:5433                           │
└─────────────────────┼──────────────────────────────────┘
                      │
       ┌──────────────┴──────────────┐
       │  PostgreSQL Container       │
       │  (docker-compose.postgres.yml)          │
       │  - Database: ecommerce_warehouse        │
       │  - Table: ads.ads_daily_business_overview (634 rows)           │
       └─────────────────────────────┘
```

---

## 3. How to Start / 如何启动

### 3.1 Prerequisites / 前置条件

```powershell
# Ensure PostgreSQL is running / 确保 PostgreSQL 运行中
docker compose -f docker-compose.postgres.yml ps

# Ensure dbt models have been built (ADS table exists)
# 确保 dbt 模型已构建（ADS 表存在）
docker compose -f docker-compose.airflow.yml exec airflow-scheduler bash -c "
cd /opt/airflow/project/dbt/ecommerce_warehouse &&
dbt run --profiles-dir /opt/airflow/config
" 2>/dev/null

# Or run locally / 或在本地运行
cd dbt\ecommerce_warehouse
dbt run --profiles-dir .
```

### 3.2 Build and Start Superset / 构建和启动 Superset

```powershell
# Step 1: Build the custom Superset image / 构建自定义 Superset 镜像
docker compose -f docker-compose.superset.yml build

# Step 2: Start Superset / 启动 Superset
docker compose -f docker-compose.superset.yml up -d

# Step 3: Check container status / 检查容器状态
docker compose -f docker-compose.superset.yml ps

# Step 4: Check logs / 检查日志
docker compose -f docker-compose.superset.yml logs --tail 30
```

### 3.3 Verify PostgreSQL Connection / 验证 PostgreSQL 连接

```powershell
docker compose -f docker-compose.superset.yml exec superset python -c "
from sqlalchemy import create_engine, text

engine = create_engine(
    'postgresql+psycopg2://warehouse_user:warehouse_pass@host.docker.internal:5433/ecommerce_warehouse'
)

with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM ads.ads_daily_business_overview'))
    print(f'ADS table rows: {result.scalar()}')
"
```

Expected output:

```
ADS table rows: 634
```

---

## 4. Access Superset UI / 访问 Superset UI

| URL | http://localhost:8088 |
|---|---|
| Username | `admin` |
| Password | `admin` |

---

## 5. Connect to PostgreSQL Warehouse / 连接到 PostgreSQL 数仓

After logging in to Superset UI, follow these steps to connect to the warehouse:

登录 Superset UI 后，按照以下步骤连接到数仓：

1. Click **Settings** (gear icon) → **Database Connections**.
   点击 **设置**（齿轮图标）→ **数据库连接**。

2. Click **+ Database**.
   点击 **+ 数据库**。

3. In the **Connect a Database** modal:
   在 **连接数据库** 弹出框中：

   - **Database**: `PostgreSQL`
     选择 PostgreSQL

   - **SQLAlchemy URI**:

     ```
     postgresql+psycopg2://warehouse_user:warehouse_pass@host.docker.internal:5433/ecommerce_warehouse
     ```

   - Click **Test Connection** — should show "Connection looks good!"
     点击 **测试连接** — 应显示 "Connection looks good!"

   - Click **Connect**.
     点击 **连接**。

---

## 6. Create Dataset / 创建数据集

After connecting the database, register `ads.ads_daily_business_overview` as a dataset:

连接数据库后，将 `ads.ads_daily_business_overview` 注册为数据集：

1. Click **Settings** (gear icon) → **Datasets**.
   点击 **设置** → **数据集**。

2. Click **+ Dataset**.
   点击 **+ 数据集**。

3. In the modal / 在弹出框中：

   - **Database**: `E-Commerce Warehouse` (the connection added above / 上面添加的连接)
   - **Schema**: `ads`
   - **Table**: `ads_daily_business_overview`

4. Click **Add**.
   点击 **添加**。

---

## 7. Create Charts / 创建图表

After the dataset is created, create charts in the **Explore** view.

创建数据集后，在 **Explore** 视图中创建图表。

### General Steps / 通用步骤

1. Click **Charts** → **+ Chart**.
   点击 **图表** → **+ 图表**。

2. Select dataset: `ads.ads_daily_business_overview`.
   选择数据集。

3. Choose chart type and configure metrics and dimensions.
   选择图表类型并配置指标和维度。

4. Click **Save** → name the chart → add to dashboard.
   点击 **保存** → 命名图表 → 添加到看板。

---

### 7.1 Daily GMV Trend / 每日 GMV 趋势

| Parameter / 参数 | Value / 值 |
|---|---|
| Chart type / 图表类型 | **Line Chart** |
| X Axis / X 轴 | `stat_date` |
| Metric / 指标 | `SUM(daily_gmv)` |
| Row limit / 行限制 | `634` |

SQL equivalent / SQL 等价查询：

```sql
SELECT stat_date, daily_gmv
FROM ads.ads_daily_business_overview
ORDER BY stat_date;
```

### 7.2 Daily Order Count Trend / 每日订单量趋势

| Parameter / 参数 | Value / 值 |
|---|---|
| Chart type / 图表类型 | **Line Chart** |
| X Axis / X 轴 | `stat_date` |
| Metric / 指标 | `SUM(daily_order_count)` |

### 7.3 AOV Trend / 平均订单价值趋势

| Parameter / 参数 | Value / 值 |
|---|---|
| Chart type / 图表类型 | **Line Chart** |
| X Axis / X 轴 | `stat_date` |
| Metric / 指标 | `AVG(daily_aov)` |

### 7.4 GMV 7-Day Moving Average / GMV 7日移动平均

| Parameter / 参数 | Value / 值 |
|---|---|
| Chart type / 图表类型 | **Line Chart** |
| X Axis / X 轴 | `stat_date` |
| Metric / 指标 | `AVG(gmv_7d_moving_avg)` (or use `daily_gmv` + `gmv_7d_moving_avg` as two lines) |

SQL equivalent / SQL 等价查询：

```sql
SELECT stat_date, daily_gmv, gmv_7d_moving_avg
FROM ads.ads_daily_business_overview
ORDER BY stat_date;
```

### 7.5 Cumulative GMV / 累计 GMV

| Parameter / 参数 | Value / 值 |
|---|---|
| Chart type / 图表类型 | **Area Chart** |
| X Axis / X 轴 | `stat_date` |
| Metric / 指标 | `MAX(cumulative_gmv)` |

### 7.6 Delivery Rate Trend / 配送率趋势

| Parameter / 参数 | Value / 值 |
|---|---|
| Chart type / 图表类型 | **Line Chart** |
| X Axis / X 轴 | `stat_date` |
| Metric / 指标 | `AVG(daily_delivery_rate)` |

### 7.7 KPI: Total GMV / 总 GMV

| Parameter / 参数 | Value / 值 |
|---|---|
| Chart type / 图表类型 | **Big Number** |
| Metric / 指标 | `SUM(daily_gmv)` |

### 7.8 KPI: Total Orders / 总订单数

| Parameter / 参数 | Value / 值 |
|---|---|
| Chart type / 图表类型 | **Big Number** |
| Metric / 指标 | `SUM(daily_order_count)` |

---

## 8. Create Dashboard / 创建看板

1. Click **Dashboards** → **+ Dashboard**.
   点击 **看板** → **+ 看板**。

2. Name: `E-Commerce Daily Business Overview`
   名称：电商每日经营概览

3. Click **Edit Dashboard** → add charts from the list.
   点击 **编辑看板** → 从列表中添加图表。

4. Arrange charts in a grid layout.
   在网格布局中排列图表。

5. Click **Save**.
   点击 **保存**。

---

## 9. Reference SQL Queries / 参考 SQL 查询

Reference queries are available in:

参考查询文件位于：

```
sql/superset/ads_dashboard_queries.sql
```

These queries can be used in **SQL Lab** (`SQL Lab → SQL Editor`) for ad-hoc analysis.

这些查询可在 **SQL Lab**（`SQL Lab → SQL 编辑器`）中用于临时分析。

---

## 10. Stop Superset / 停止 Superset

```powershell
docker compose -f docker-compose.superset.yml down

# To remove data volume (reset everything) / 删除数据卷（完全重置）
docker compose -f docker-compose.superset.yml down -v
```

---

## 11. Troubleshooting / 故障排查

### 11.1 Superset container exits immediately / 容器立即退出

```powershell
docker compose -f docker-compose.superset.yml logs --tail 50
```

Common issue: Permission denied on `init.sh`.

常见问题：`init.sh` 权限被拒绝。

Fix:

```powershell
docker compose -f docker-compose.superset.yml exec superset chmod +x /app/init.sh
```

### 11.2 Cannot connect to PostgreSQL / 无法连接 PostgreSQL

```powershell
docker compose -f docker-compose.superset.yml exec superset python -c "
from sqlalchemy import create_engine, text

engine = create_engine(
    'postgresql+psycopg2://warehouse_user:warehouse_pass@host.docker.internal:5433/ecommerce_warehouse'
)
with engine.connect() as conn:
    conn.execute(text('SELECT 1'))
    print('PostgreSQL connection OK')
"
```

### 11.3 Superset UI not loading / Superset UI 未加载

Check that port 8088 is not already in use:

检查端口 8088 是否已被占用：

```powershell
netstat -ano | findstr :8088
```

### 11.4 Tables not visible in dataset list / 表在数据集列表中不可见

In Superset UI, go to **Settings → Database Connections → Edit** the connection.

在 Superset UI 中，前往 **设置 → 数据库连接 → 编辑** 连接。

Ensure **Expose in SQL Lab** is enabled and **Allow DML** is disabled.

确保 **在 SQL Lab 中公开** 已启用，**允许 DML** 已禁用。

Then click the **Scan** button in the Datasets view to refresh available tables.

然后在数据集视图中点击 **扫描** 按钮刷新可用表。

---

## 12. File Reference / 文件参考

| File / 文件 | Purpose / 用途 |
|---|---|
| `docker-compose.superset.yml` | Superset service definition / Superset 服务定义 |
| `superset/Dockerfile` | Custom Superset image with psycopg2 / 自定义 Superset 镜像 |
| `superset/superset_config.py` | Superset application config / Superset 应用配置 |
| `superset/init.sh` | Container startup initialization / 容器启动初始化 |
| `superset/.env.example` | Environment variable template / 环境变量模板 |
| `superset/.env` | Local environment (gitignored) / 本地环境配置 |
| `superset/requirements.txt` | Python package dependencies / Python 包依赖 |
| `sql/superset/ads_dashboard_queries.sql` | Reference SQL queries for charts / 图表参考 SQL 查询 |
| `docs/superset_dashboard_guide.md` | This document / 本文档 |

---

## 13. Summary / 总结

This phase adds Apache Superset as the BI visualization layer for the enterprise warehouse stack.

本阶段为企级数仓技术栈添加 Apache Superset 作为 BI 可视化层。

Key achievements / 关键成果：

1. **Docker-based Superset** / Docker 化 Superset: Custom image with psycopg2 for PostgreSQL connectivity
2. **PostgreSQL connection** / PostgreSQL 连接: Via `host.docker.internal:5433` to `ads.ads_daily_business_overview`
3. **8 documented charts** / 8 个文档化图表: GMV trend, order count, AOV, moving average, cumulative GMV, delivery rate, KPI cards
4. **Manual dashboard creation** / 手动看板创建: Step-by-step guide for Superset UI setup
5. **Reference SQL queries** / 参考 SQL 查询: Ready-to-use queries for SQL Lab
6. **No modifications** / 无修改: All existing Pandas, Spark, dbt, and Airflow files remain unchanged