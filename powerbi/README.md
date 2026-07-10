# Power BI Dashboard / Power BI 看板

## Overview / 概述

This directory contains the Power BI Desktop file for the e-commerce offline data warehouse project.

本目录包含电商离线数仓项目的 Power BI Desktop 文件。

Power BI connects to the PostgreSQL warehouse directly from the local Windows machine using the Npgsql connector.

Power BI 通过 Npgsql 连接器从本地 Windows 机器直接连接到 PostgreSQL 数仓。

---

## Files / 文件

| File / 文件 | Description / 说明 |
|---|---|
| `ecommerce_daily_business_overview.pbix` | Power BI Desktop file (created manually) / Power BI Desktop 文件（手动创建） |
| `README.md` | This file / 本文件 |

---

## Connection Configuration / 连接配置

| Parameter / 参数 | Value / 值 |
|---|---|
| Server / 服务器 | `localhost:5433` |
| Database / 数据库 | `ecommerce_warehouse` |
| Authentication / 认证方式 | Database |
| Username / 用户名 | `warehouse_user` |
| Password / 密码 | `warehouse_pass` |
| Source table / 源表 | `ads.ads_daily_business_overview` |
| Mode / 模式 | Import |

---

## Why localhost:5433? / 为什么使用 localhost:5433?

Power BI Desktop runs directly on Windows, not inside a Docker container.

Power BI Desktop 直接在 Windows 上运行，而非 Docker 容器内部。

- **From Windows host** → PostgreSQL is accessible at `localhost:5433` (because `docker-compose.postgres.yml` maps host port 5433 to container port 5432).
- **从 Windows 宿主机** → PostgreSQL 可通过 `localhost:5433` 访问。

- **From Docker containers** (Airflow, Superset) → PostgreSQL is accessible at `host.docker.internal:5433`.
- **从 Docker 容器**（Airflow、Superset）→ PostgreSQL 可通过 `host.docker.internal:5433` 访问。

Both point to the same PostgreSQL database.

两者指向同一个 PostgreSQL 数据库。

---

## Visuals / 图表

| # | Visual / 可视化 | Type / 类型 | Field / 字段 | Description / 说明 |
|---|---|---|---|---|
| 1 | Total GMV / 总 GMV | Card | `SUM(daily_gmv)` | Total gross merchandise value |
| 2 | Total Orders / 总订单数 | Card | `SUM(daily_order_count)` | Total number of orders |
| 3 | Daily GMV Trend / 每日 GMV 趋势 | Line chart | `stat_date` (axis), `daily_gmv` (values) | Revenue over time |
| 4 | Daily Order Count Trend / 每日订单量趋势 | Line chart | `stat_date` (axis), `daily_order_count` (values) | Order volume over time |
| 5 | AOV Trend / 平均订单价值趋势 | Line chart | `stat_date` (axis), `daily_aov` (values) | Average order value over time |
| 6 | Cumulative GMV / 累计 GMV | Line chart | `stat_date` (axis), `cumulative_gmv` (values) | Running total of GMV |
| 7 | Delivery Rate Trend / 配送率趋势 | Line chart | `stat_date` (axis), `daily_delivery_rate` (values) | Delivery performance |

---

## How to Open / 如何打开

```powershell
# Navigate to the powerbi directory / 导航到 powerbi 目录
cd powerbi

# Open the .pbix file / 打开 .pbix 文件
start ecommerce_daily_business_overview.pbix
```

---

## Related Documentation / 相关文档

- [Power BI Dashboard Guide](../docs/powerbi_dashboard_guide.md) — Step-by-step setup guide / 分步设置指南
- [PostgreSQL Warehouse Setup](../docs/postgres_warehouse_setup.md) — Database connection details / 数据库连接详情