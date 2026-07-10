# Power BI Dashboard Guide / Power BI 看板指南

## 1. Purpose / 目的

This document describes how to use Microsoft Power BI Desktop to connect to the PostgreSQL warehouse and create an interactive business overview dashboard.

本文档说明如何使用 Microsoft Power BI Desktop 连接到 PostgreSQL 数仓并创建交互式经营概览看板。

Power BI is used as an enterprise reporting layer alongside Apache Superset.

Power BI 作为企业报表层，与 Apache Superset 并行使用。

---

## 2. Architecture / 架构

```text
┌─────────────────────────────────────┐
│  Power BI Desktop (Windows)          │
│                                     │
│  Data source: PostgreSQL (Import)    │
│  Table: ads.ads_daily_business_overview      │
│  Saved to: powerbi/*.pbix            │
│  Screenshots: docs/images/*.png      │
└────────────────┬────────────────────┘
                 │
   localhost:5433
                 │
┌────────────────┴────────────────────┐
│  PostgreSQL Container (Docker)       │
│  docker-compose.postgres.yml         │
│  Database: ecommerce_warehouse       │
│  Table: ads.ads_daily_business_overview (634 rows)           │
└─────────────────────────────────────┘
```

### 2.1 Connection Comparison / 连接方式对比

| Context / 场景 | Host | Port | Why / 原因 |
|---|---|---|---|
| **Power BI Desktop** (Windows host) | `localhost` | `5433` | Direct connection to Docker mapped port |
| **Airflow container** | `host.docker.internal` | `5433` | Docker internal host gateway |
| **Superset container** | `host.docker.internal` | `5433` | Docker internal host gateway |

All three connect to the same PostgreSQL database (`ecommerce_warehouse`).

三者连接到同一个 PostgreSQL 数据库。

---

## 3. Prerequisites / 前置条件

### 3.1 Software / 软件

- **Microsoft Power BI Desktop**: Free download from [Microsoft Store](https://powerbi.microsoft.com/desktop/) or [official site](https://powerbi.microsoft.com/en-us/downloads/)
- **Power BI Desktop**：从 Microsoft Store 或官网免费下载

### 3.2 Data Readiness / 数据就绪

Before connecting Power BI, ensure:

在连接 Power BI 之前，请确保：

1. PostgreSQL container is running / PostgreSQL 容器运行中

   ```powershell
   docker compose -f docker-compose.postgres.yml ps
   ```

2. dbt models have been built (ADS table exists) / dbt 模型已构建

   ```powershell
   cd dbt\ecommerce_warehouse
   dbt run --profiles-dir .
   ```

3. ADS table has data / ADS 表有数据

   ```powershell
   python -c "
   import psycopg2
   conn = psycopg2.connect(host='localhost', port=5433, dbname='ecommerce_warehouse',
       user='warehouse_user', password='warehouse_pass')
   cur = conn.cursor()
   cur.execute('SELECT COUNT(*) FROM ads.ads_daily_business_overview')
   print(f'ADS table rows: {cur.fetchone()[0]}')
   conn.close()
   "
   ```

   Expected: `ADS table rows: 634`

---

## 4. Step-by-Step Guide / 分步指南

### Step 1: Open Power BI Desktop / 打开 Power BI Desktop

Launch Power BI Desktop from the Start menu.

从开始菜单启动 Power BI Desktop。

### Step 2: Get Data / 获取数据

1. Click **Home** → **Get Data** → **More...**
   点击 **主页** → **获取数据** → **更多...**

2. Search for `PostgreSQL`
   搜索 `PostgreSQL`

3. Select **PostgreSQL Database** → **Connect**
   选择 **PostgreSQL 数据库** → **连接**

### Step 3: Configure Connection / 配置连接

In the PostgreSQL Database dialog:

在 PostgreSQL 数据库对话框中：

| Field / 字段 | Value / 值 |
|---|---|
| **Server** / 服务器 | `localhost:5433` |
| **Database** / 数据库 | `ecommerce_warehouse` |
| **Data Connectivity mode** / 数据连接模式 | **Import** (recommended for 634 rows) |

Click **OK**.

点击 **确定**。

### Step 4: Authenticate / 认证

In the authentication dialog:

在认证对话框中：

| Field / 字段 | Value / 值 |
|---|---|
| **Authentication** / 认证方式 | **Database** |
| **User name** / 用户名 | `warehouse_user` |
| **Password** / 密码 | `warehouse_pass` |

Click **Connect**.

点击 **连接**。

If prompted about the Npgsql connector, click **Install** to install the PostgreSQL connector.

如果提示安装 Npgsql 连接器，点击 **安装**。

### Step 5: Select Table / 选择表

In the Navigator window:

在导航窗口中：

1. Check the box for `ads.ads_daily_business_overview`
   勾选 `ads.ads_daily_business_overview`

2. You can preview the data on the right side (should show 634 rows).
   您可以在右侧预览数据（应显示 634 行）。

3. Click **Load**.
   点击 **加载**。

### Step 6: Verify Fields / 验证字段

After loading, in the **Fields** pane on the right, you should see:

加载后，在右侧的 **字段** 窗格中，您应该看到：

```
ads_daily_business_overview
├── ads_loaded_at
├── aov_7d_moving_avg
├── cumulative_customer_count
├── cumulative_gmv
├── cumulative_order_count
├── daily_aov
├── daily_average_review_score
├── daily_delivery_rate
├── daily_freight_amount
├── daily_gmv
├── daily_late_delivery_rate
├── daily_order_count
├── daily_paid_order_count
├── daily_product_amount
├── daily_review_comment_rate
├── daily_review_rate
├── daily_unique_customer_count
├── daily_valid_order_count
├── dt
├── gmv_7d_moving_avg
├── gmv_day_over_day_change
├── gmv_day_over_day_rate
├── order_count_7d_moving_avg
├── order_count_day_over_day_change
├── order_count_day_over_day_rate
├── paid_order_rate
├── stat_date
├── stat_month
├── valid_order_rate
```

29 fields total.

共 29 个字段。

---

## 5. Create Visuals / 创建图表

### 5.1 Card: Total GMV / 卡片：总 GMV

1. In the **Visualizations** pane, click the **Card** icon.
   在 **可视化** 窗格中，点击 **卡片** 图标。

2. Drag `daily_gmv` to the **Fields** well.
   将 `daily_gmv` 拖到 **字段** 区域。

3. Click the dropdown arrow on `daily_gmv` in the field well → select **Sum**.
   点击字段区域中 `daily_gmv` 的下拉箭头 → 选择 **求和**。

4. (Optional) Format the value: Select the card → Format → Data label → Display units: None → Value decimal places: 2.
   （可选）格式化数值：选择卡片 → 格式 → 数据标签 → 显示单位：无 → 小数位数：2。

5. Result: `$16,011,382.80` (total GMV)
   结果：总 GMV

### 5.2 Card: Total Orders / 卡片：总订单数

1. Add a new **Card** visual.
   新增一个 **卡片** 可视化。

2. Drag `daily_order_count` → **Sum**.
   拖拽 `daily_order_count` → **求和**。

3. Result: `99,441` (total orders)
   结果：总订单数 99,441

### 5.3 Line Chart: Daily GMV Trend / 折线图：每日 GMV 趋势

1. Click the **Line Chart** icon in Visualizations.
   点击可视化中的 **折线图** 图标。

2. Drag `stat_date` to **X-axis**.
   将 `stat_date` 拖到 **X 轴**。

3. Drag `daily_gmv` to **Y-axis** → select **Sum**.
   将 `daily_gmv` 拖到 **Y 轴** → 选择 **求和**。

### 5.4 Line Chart: Daily Order Count Trend / 折线图：每日订单量趋势

1. Add a new **Line Chart**.
   新增一个 **折线图**。

2. X-axis: `stat_date`.
   X 轴：`stat_date`。

3. Y-axis: `daily_order_count` → **Sum**.
   Y 轴：`daily_order_count` → **求和**。

### 5.5 Line Chart: AOV Trend / 折线图：平均订单价值趋势

1. Add a new **Line Chart**.
   新增一个 **折线图**。

2. X-axis: `stat_date`.
   X 轴：`stat_date`。

3. Y-axis: `daily_aov` → **Average** (not Sum, because AOV is already a per-day value).
   Y 轴：`daily_aov` → **平均值**。

### 5.6 Line Chart: Cumulative GMV / 折线图：累计 GMV

1. Add a new **Line Chart**.
   新增一个 **折线图**。

2. X-axis: `stat_date`.
   X 轴：`stat_date`。

3. Y-axis: `cumulative_gmv` → **Maximum** (since cumulative_gmv already accumulates, MAX gives the latest day's running total).
   Y 轴：`cumulative_gmv` → **最大值**。

### 5.7 Line Chart: Delivery Rate Trend / 折线图：配送率趋势

1. Add a new **Line Chart**.
   新增一个 **折线图**。

2. X-axis: `stat_date`.
   X 轴：`stat_date`。

3. Y-axis: `daily_delivery_rate` → **Average**.
   Y 轴：`daily_delivery_rate` → **平均值**。

---

## 6. Arrange the Dashboard / 布局看板

1. Resize and arrange visuals in a grid layout.
   调整图表大小并按网格布局排列。

2. Suggested layout / 建议布局：

   ```text
   ┌─────────────────────┬─────────────────────┐
   │  Card: Total GMV    │  Card: Total Orders │
   ├─────────────────────┴─────────────────────┤
   │  Line: Daily GMV Trend                     │
   ├───────────────────────────────────────────┤
   │  Line: Daily Order Count Trend             │
   ├─────────────────────┬─────────────────────┤
   │  Line: AOV Trend    │  Line: Delivery Rate│
   ├─────────────────────┴─────────────────────┤
   │  Line: Cumulative GMV                      │
   └───────────────────────────────────────────┘
   ```

3. Save the file / 保存文件：

   ```text
   File → Save As → powerbi/ecommerce_daily_business_overview.pbix
   ```

---

## 7. Take Screenshots / 截图

1. After the dashboard is complete and saved, take a screenshot of the entire Power BI window.
   看板完成后，截取整个 Power BI 窗口的截图。

2. Save the screenshot as:
   将截图保存为：

   ```
   docs/images/powerbi_dashboard_overview.png
   ```

3. (Optional) Crop to show only the dashboard canvas area.
   （可选）裁剪以仅显示看板画布区域。

---

## 8. Power BI vs Superset / Power BI 与 Superset 对比

| Aspect / 方面 | Apache Superset | Microsoft Power BI |
|---|---|---|
| Platform / 平台 | Web-based (Docker) | Desktop (Windows) |
| Installation / 安装 | Docker container | Windows installer |
| Open Source / 开源 | ✅ Yes | ❌ Proprietary |
| Deployment / 部署 | Self-hosted | Enterprise license |
| Connection to DB / 数据库连接 | `host.docker.internal:5433` | `localhost:5433` |
| Charts / 图表 | 8 documented charts | 7 recommended visuals |
| Target audience / 目标受众 | Interactive web dashboards | Enterprise reports / presentations |

---

## 9. Troubleshooting / 故障排查

### 9.1 Cannot find PostgreSQL connector / 找不到 PostgreSQL 连接器

Power BI may prompt to install Npgsql. Click **Install** and restart Power BI.

Power BI 可能提示安装 Npgsql。点击 **安装** 并重启 Power BI。

### 9.2 Connection timeout / 连接超时

```powershell
# Verify PostgreSQL is running / 验证 PostgreSQL 运行中
docker compose -f docker-compose.postgres.yml ps

# Ensure port 5433 is listening / 确保端口 5433 在监听
netstat -ano | findstr :5433
```

### 9.3 "Cannot connect to server" / "无法连接到服务器"

Check that Docker Desktop is running and PostgreSQL container is healthy.

检查 Docker Desktop 是否运行，PostgreSQL 容器是否健康。

### 9.4 Data shows as 0 for all fields / 数据显示为 0

- Ensure you used **Sum** or **Average** aggregation, not Count.
- 确保使用了 **求和** 或 **平均值** 聚合，而不是计数。
- For `daily_aov` and `daily_delivery_rate`, use **Average** (or **Don't summarize** depending on Power BI version).
- 对于 `daily_aov` 和 `daily_delivery_rate`，使用 **平均值**。

---

## 10. Files Reference / 文件参考

| File / 文件 | Purpose / 用途 |
|---|---|
| `powerbi/ecommerce_daily_business_overview.pbix` | Power BI Desktop file (manual) / Power BI Desktop 文件（手动创建） |
| `powerbi/README.md` | Power BI directory overview / Power BI 目录说明 |
| `docs/powerbi_dashboard_guide.md` | This document / 本文档 |
| `docs/images/powerbi_dashboard_overview.png` | Dashboard screenshot (manual) / 看板截图（手动截图） |

---

## 11. Summary / 总结

This phase adds Microsoft Power BI as an enterprise reporting layer for the warehouse stack.

本阶段为企级数仓技术栈添加 Microsoft Power BI 作为企业报表层。

Key points / 关键点：

1. **Direct Windows connection**: Power BI Desktop connects via `localhost:5433` (not `host.docker.internal`)
2. **Import mode**: Small dataset (634 rows) — ideal for Import mode with full interactivity
3. **7 visuals**: 2 KPI cards + 5 line charts covering revenue, volume, AOV, and quality
4. **Manual setup**: pbix file and screenshot created in Power BI Desktop (not automated)
5. **Parallel BI tools**: Superset for web dashboards, Power BI for enterprise reporting
6. **No modifications**: All existing infrastructure remains unchanged