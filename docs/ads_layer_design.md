# ADS Layer Design / ADS 应用层设计

## 1. Purpose / 目的

The ADS layer stores application-oriented data for reporting and dashboard usage.

ADS 层用于存储面向应用、报表和看板的数据。

Compared with the DWS layer, the ADS layer is closer to business users and visualization tools.

相比 DWS 汇总层，ADS 层更加接近业务用户和可视化工具。

The main goals of the ADS layer are:

ADS 层的主要目标包括：

* Provide dashboard-ready data tables.
  提供可以直接用于看板的数据表。

* Simplify BI metric usage.
  简化 BI 层的指标使用方式。

* Support business overview, trend analysis, and operational monitoring.
  支持经营概览、趋势分析和运营监控。

* Reduce repeated calculations in Power BI, Superset, or other BI tools.
  减少 Power BI、Superset 等 BI 工具中的重复计算。

---

## 2. Layer Position / 分层位置

The ADS layer is the final application layer of the offline data warehouse.

ADS 层是离线数仓的最终应用层。

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
BI Dashboard
```

In this project, the first ADS table is:

在本项目中，第一张 ADS 表为：

```
ads_daily_business_overview
```

---

## 3. Table: ads_daily_business_overview / 表：ads_daily_business_overview

### 3.1 Business Meaning / 业务含义

The `ads_daily_business_overview` table is a dashboard-ready daily business overview table.

`ads_daily_business_overview` 表是一张可直接用于 BI 看板的每日经营概览表。

Each row represents one statistic date.

每一行代表一个统计日期。

This table is built from the DWS daily order summary table and includes daily metrics, moving averages, cumulative metrics, and day-over-day changes.

该表基于 DWS 每日订单汇总表构建，包含每日指标、移动平均、累计指标和环比变化指标。

It is designed to support business monitoring and visualization.

该表用于支持经营监控和可视化展示。

---

## 4. Source Table / 来源表

The `ads_daily_business_overview` table is built from:

`ads_daily_business_overview` 表由以下表加工得到：

| Source Table / 来源表        | Usage / 用途                                                                                |
| ------------------------- | ----------------------------------------------------------------------------------------- |
| `dws_daily_order_summary` | Provides daily order, GMV, customer, delivery, and review metrics / 提供每日订单、GMV、客户、物流和评价指标 |

---

## 5. Data Granularity / 数据粒度

The granularity of `ads_daily_business_overview` is one row per statistic date.

`ads_daily_business_overview` 的数据粒度是一行一个统计日期。

Granularity:

数据粒度：

```
stat_date
```

This means that each record can be directly used as one daily point in a dashboard trend chart.

这意味着每条记录都可以直接作为看板趋势图中的一个日粒度数据点。

---

## 6. Processing Logic / 加工逻辑

The ADS building script performs the following steps:

ADS 构建脚本会执行以下步骤：

1. Read `data/dws/dws_daily_order_summary.csv`.
   读取 `data/dws/dws_daily_order_summary.csv`。

2. Validate whether all required fields exist.
   校验所需字段是否存在。

3. Rename DWS metrics into dashboard-friendly ADS field names.
   将 DWS 指标重命名为更适合看板使用的 ADS 字段名。

4. Calculate valid order rate and paid order rate.
   计算有效订单率和支付订单率。

5. Calculate 7-day moving average metrics.
   计算 7 日移动平均指标。

6. Calculate cumulative GMV and cumulative order count.
   计算累计 GMV 和累计订单数。

7. Calculate day-over-day changes and growth rates.
   计算日环比变化和增长率。

8. Add ADS technical fields.
   添加 ADS 层技术字段。

9. Save the result to `data/ads/ads_daily_business_overview.csv`.
   将结果保存到 `data/ads/ads_daily_business_overview.csv`。

---

## 7. Key Metrics / 核心指标

| Metric / 指标                       | Description / 说明                                              |
| --------------------------------- | ------------------------------------------------------------- |
| `daily_order_count`               | Daily order count / 每日订单数                                     |
| `daily_valid_order_count`         | Daily valid order count / 每日有效订单数                             |
| `daily_paid_order_count`          | Daily paid order count / 每日支付订单数                              |
| `daily_unique_customer_count`     | Daily unique customer count / 每日唯一客户数                         |
| `daily_gmv`                       | Daily GMV based on payment amount / 基于支付金额的每日 GMV             |
| `daily_product_amount`            | Daily product amount / 每日商品金额                                 |
| `daily_freight_amount`            | Daily freight amount / 每日运费金额                                 |
| `daily_aov`                       | Daily average order value / 每日客单价                             |
| `daily_delivery_rate`             | Daily delivery rate / 每日送达率                                   |
| `daily_late_delivery_rate`        | Daily late delivery rate / 每日物流延迟率                            |
| `daily_review_rate`               | Daily review rate / 每日评价率                                     |
| `daily_review_comment_rate`       | Daily review comment rate / 每日文字评价率                           |
| `daily_average_review_score`      | Daily average review score / 每日平均评价分数                         |
| `valid_order_rate`                | Valid order count divided by total order count / 有效订单数占总订单数比例 |
| `paid_order_rate`                 | Paid order count divided by total order count / 支付订单数占总订单数比例  |
| `gmv_7d_moving_avg`               | 7-day moving average of GMV / GMV 的 7 日移动平均                   |
| `order_count_7d_moving_avg`       | 7-day moving average of order count / 订单数的 7 日移动平均            |
| `aov_7d_moving_avg`               | 7-day moving average of AOV / 客单价的 7 日移动平均                    |
| `cumulative_gmv`                  | Cumulative GMV / 累计 GMV                                       |
| `cumulative_order_count`          | Cumulative order count / 累计订单数                                |
| `cumulative_customer_count`       | Cumulative daily unique customer count / 累计每日唯一客户数            |
| `gmv_day_over_day_change`         | GMV day-over-day absolute change / GMV 日环比变化值                 |
| `order_count_day_over_day_change` | Order count day-over-day absolute change / 订单数日环比变化值          |
| `gmv_day_over_day_rate`           | GMV day-over-day growth rate / GMV 日环比增长率                     |
| `order_count_day_over_day_rate`   | Order count day-over-day growth rate / 订单数日环比增长率              |

---

## 8. Metric Calculation Rules / 指标计算规则

### 8.1 Daily GMV / 每日 GMV

Daily GMV is calculated from the total payment amount.

每日 GMV 基于总支付金额计算。

```
daily_gmv = total_payment_amount
```

---

### 8.2 Daily AOV / 每日客单价

Daily AOV measures the average payment amount per order.

每日客单价衡量每笔订单的平均支付金额。

```
daily_aov = daily_gmv / daily_order_count
```

---

### 8.3 Valid Order Rate / 有效订单率

Valid order rate measures the percentage of valid orders among all orders.

有效订单率衡量有效订单在全部订单中的占比。

```
valid_order_rate = daily_valid_order_count / daily_order_count
```

---

### 8.4 Paid Order Rate / 支付订单率

Paid order rate measures the percentage of paid orders among all orders.

支付订单率衡量已支付订单在全部订单中的占比。

```
paid_order_rate = daily_paid_order_count / daily_order_count
```

---

### 8.5 7-Day Moving Average / 7 日移动平均

The 7-day moving average smooths daily fluctuations and shows the overall trend.

7 日移动平均用于平滑每日波动，展示整体趋势。

```
gmv_7d_moving_avg = average(daily_gmv over current day and previous 6 days)
```

---

### 8.6 Cumulative GMV / 累计 GMV

Cumulative GMV measures the total GMV from the beginning of the dataset to the current date.

累计 GMV 衡量从数据开始日期到当前日期的累计成交金额。

```
cumulative_gmv = sum(daily_gmv from start date to current date)
```

---

### 8.7 Day-over-Day Growth Rate / 日环比增长率

Day-over-day growth rate measures the relative change compared with the previous day.

日环比增长率衡量相比前一天的相对变化。

```
gmv_day_over_day_rate = (today_gmv - yesterday_gmv) / yesterday_gmv
```

---

## 9. Output Files / 输出文件

After running the ADS building script, the following files are generated:

运行 ADS 构建脚本后，会生成以下文件：

| File / 文件                                             | Description / 说明                                                  |
| ----------------------------------------------------- | ----------------------------------------------------------------- |
| `data/ads/ads_daily_business_overview.csv`            | Daily business overview table for BI dashboard / 用于 BI 看板的每日经营概览表 |
| `docs/ads_daily_business_overview_report.csv`         | Table-level summary report / 表级汇总报告                               |
| `docs/ads_daily_business_overview_column_profile.csv` | Column-level profiling report / 字段级数据探查报告                         |
| `sql/ads/create_ads_tables.sql`                       | Hive-style ADS table creation SQL / Hive 风格的 ADS 建表 SQL           |

---

## 10. Dashboard Usage / 看板用途

The ADS table can be used directly in BI tools.

ADS 表可以直接用于 BI 工具。

Recommended dashboard modules include:

推荐的看板模块包括：

| Dashboard Module / 看板模块     | Metrics / 指标                                                                          |
| --------------------------- | ------------------------------------------------------------------------------------- |
| Business Overview / 经营概览    | GMV, order count, AOV, customer count / GMV、订单数、客单价、客户数                               |
| GMV Trend / GMV 趋势          | daily GMV, 7-day moving average, cumulative GMV / 每日 GMV、7 日移动平均、累计 GMV               |
| Order Trend / 订单趋势          | daily order count, 7-day moving average, cumulative order count / 每日订单数、7 日移动平均、累计订单数 |
| Delivery Performance / 物流表现 | delivery rate, late delivery rate / 送达率、物流延迟率                                         |
| Review Performance / 评价表现   | review rate, review comment rate, average review score / 评价率、文字评价率、平均评分               |
| Growth Monitoring / 增长监控    | day-over-day change and growth rate / 环比变化和增长率                                        |

---

## 11. Relationship with BI Layer / 与 BI 层的关系

The ADS layer reduces the amount of calculation required in BI tools.

ADS 层减少了 BI 工具中的计算工作量。

Instead of repeatedly calculating rates, moving averages, and cumulative metrics in Power BI or Superset, the BI layer can directly read these fields from the ADS table.

BI 层不需要在 Power BI 或 Superset 中重复计算比例、移动平均和累计指标，而是可以直接读取 ADS 表中的字段。

This makes the dashboard more stable, reusable, and easier to maintain.

这使得看板更加稳定、可复用，也更容易维护。

---

## 12. Summary / 总结

The ADS layer turns reusable DWS summary data into dashboard-ready application data.

ADS 层将可复用的 DWS 汇总数据加工成可以直接用于看板的应用数据。

The first ADS table, `ads_daily_business_overview`, provides daily business metrics, trend indicators, cumulative indicators, and growth indicators.

第一张 ADS 表 `ads_daily_business_overview` 提供了每日经营指标、趋势指标、累计指标和增长指标。

It prepares the project for BI dashboard development and final portfolio presentation.

它为后续 BI 看板开发和最终项目展示打下基础。
