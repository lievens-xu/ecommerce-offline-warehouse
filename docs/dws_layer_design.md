# DWS Layer Design / DWS 汇总层设计

## 1. Purpose / 目的

The DWS layer stores subject-level aggregated data.

DWS 层用于存储面向主题的汇总数据。

Compared with the DWD layer, the DWS layer focuses on business metrics and analytical summaries.

相比 DWD 明细层，DWS 层更加关注业务指标和分析汇总结果。

The main goals of the DWS layer are:

DWS 层的主要目标包括：

* Aggregate detail-level data into business-level summary tables.
  将明细级数据聚合为业务级汇总表。

* Reduce repeated calculation in later reporting layers.
  减少后续报表层中的重复计算。

* Provide reusable metric tables for ADS and BI dashboards.
  为 ADS 应用层和 BI 看板提供可复用的指标表。

* Improve query efficiency for common analytical scenarios.
  提升常见分析场景下的查询效率。

---

## 2. Layer Position / 分层位置

The DWS layer is located between the DWD layer and the ADS layer.

DWS 层位于 DWD 明细层和 ADS 应用层之间。

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
```

In this project, the first DWS table is:

在本项目中，第一张 DWS 表为：

```
dws_daily_order_summary
```

---

## 3. Table: dws_daily_order_summary / 表：dws_daily_order_summary

### 3.1 Business Meaning / 业务含义

The `dws_daily_order_summary` table is a daily business summary table.

`dws_daily_order_summary` 表是一张按天汇总的经营分析表。

Each row represents one purchase date.

每一行代表一个下单日期。

This table aggregates order, customer, payment, delivery, and review metrics from the DWD order detail table.

该表基于 DWD 订单明细表，对订单、客户、支付、物流和评价指标进行按天聚合。

It supports later ADS reporting tables and BI dashboards.

该表后续用于支撑 ADS 报表层和 BI 可视化看板。

---

## 4. Source Table / 来源表

The `dws_daily_order_summary` table is built from:

`dws_daily_order_summary` 表由以下表加工得到：

| Source Table / 来源表 | Usage / 用途                                               |
| ------------------ | -------------------------------------------------------- |
| `dwd_order_detail` | Provides cleaned order-level detail data / 提供清洗后的订单级明细数据 |

---

## 5. Data Granularity / 数据粒度

The granularity of `dws_daily_order_summary` is one row per purchase date.

`dws_daily_order_summary` 的数据粒度是一行一个下单日期。

Granularity:

数据粒度：

```
purchase_date
```

This means that all order-level records are aggregated by `purchase_date`.

这意味着所有订单级明细记录都会按照 `purchase_date` 进行聚合。

---

## 6. Processing Logic / 加工逻辑

The DWS building script performs the following steps:

DWS 构建脚本会执行以下步骤：

1. Read `data/dwd/dwd_order_detail.csv`.
   读取 `data/dwd/dwd_order_detail.csv`。

2. Validate whether required columns exist.
   校验所需字段是否存在。

3. Convert amount, review, delivery, and status fields into usable formats.
   将金额、评价、物流和状态字段转换为可计算格式。

4. Create helper flags such as valid order, paid order, and reviewed order.
   构造有效订单、已支付订单、已评价订单等辅助标记。

5. Group records by `purchase_date`.
   按 `purchase_date` 对订单明细进行分组。

6. Calculate daily business metrics.
   计算每日经营指标。

7. Add DWS technical fields.
   添加 DWS 层技术字段。

8. Save the result to `data/dws/dws_daily_order_summary.csv`.
   将结果保存到 `data/dws/dws_daily_order_summary.csv`。

---

## 7. Key Metrics / 核心指标

| Metric / 指标                    | Description / 说明                                                            |
| ------------------------------ | --------------------------------------------------------------------------- |
| `order_count`                  | Total number of orders / 订单总数                                               |
| `valid_order_count`            | Valid orders excluding canceled and unavailable orders / 有效订单数，排除取消和不可用订单   |
| `paid_order_count`             | Orders with payment amount greater than 0 / 支付金额大于 0 的订单数                   |
| `unique_customer_count`        | Number of unique customers / 唯一客户数                                          |
| `delivered_order_count`        | Number of delivered orders / 已送达订单数                                         |
| `late_delivery_order_count`    | Number of late delivery orders / 延迟送达订单数                                    |
| `delivery_rate`                | Delivered orders divided by total orders / 已送达订单数占总订单数的比例                   |
| `late_delivery_rate`           | Late delivery orders divided by delivered orders / 延迟送达订单数占已送达订单数的比例        |
| `review_order_count`           | Number of orders with reviews / 有评价的订单数                                     |
| `review_comment_order_count`   | Number of orders with review comments / 有文字评价的订单数                           |
| `review_rate`                  | Reviewed orders divided by total orders / 有评价订单数占总订单数的比例                    |
| `review_comment_rate`          | Orders with review comments divided by reviewed orders / 有文字评价订单数占已评价订单数的比例 |
| `total_payment_amount`         | Total payment amount / 总支付金额                                                |
| `total_product_amount`         | Total product amount / 商品总金额                                                |
| `total_freight_amount`         | Total freight amount / 运费总金额                                                |
| `aov`                          | Average order value / 平均订单金额，客单价                                            |
| `avg_product_amount_per_order` | Average product amount per order / 平均每单商品金额                                 |
| `avg_freight_amount_per_order` | Average freight amount per order / 平均每单运费                                   |
| `average_review_score`         | Average review score / 平均评价分数                                               |

---

## 8. Metric Calculation Rules / 指标计算规则

### 8.1 Order Count / 订单数

`order_count` counts distinct `order_id`.

`order_count` 统计不同 `order_id` 的数量。

```
order_count = count(distinct order_id)
```

---

### 8.2 Valid Order Count / 有效订单数

`valid_order_count` excludes orders with status `canceled` or `unavailable`.

`valid_order_count` 排除状态为 `canceled` 或 `unavailable` 的订单。

```
valid_order_count = count(order_id where order_status not in ('canceled', 'unavailable'))
```

---

### 8.3 Average Order Value / 客单价

`aov` measures the average payment amount per order.

`aov` 衡量每笔订单的平均支付金额。

```
aov = total_payment_amount / order_count
```

---

### 8.4 Delivery Rate / 送达率

`delivery_rate` measures the percentage of orders that have been delivered.

`delivery_rate` 衡量已送达订单占总订单的比例。

```
delivery_rate = delivered_order_count / order_count
```

---

### 8.5 Late Delivery Rate / 物流延迟率

`late_delivery_rate` measures the percentage of delivered orders that arrived later than the estimated delivery date.

`late_delivery_rate` 衡量已送达订单中延迟送达的比例。

```
late_delivery_rate = late_delivery_order_count / delivered_order_count
```

---

### 8.6 Review Rate / 评价率

`review_rate` measures the percentage of orders that have review records.

`review_rate` 衡量有评价记录的订单占总订单的比例。

```
review_rate = review_order_count / order_count
```

---

## 9. Output Files / 输出文件

After running the DWS building script, the following files are generated:

运行 DWS 构建脚本后，会生成以下文件：

| File / 文件                                         | Description / 说明                                        |
| ------------------------------------------------- | ------------------------------------------------------- |
| `data/dws/dws_daily_order_summary.csv`            | Daily order summary table / 每日订单经营汇总表                   |
| `docs/dws_daily_order_summary_report.csv`         | Table-level summary report / 表级汇总报告                     |
| `docs/dws_daily_order_summary_column_profile.csv` | Column-level profiling report / 字段级数据探查报告               |
| `sql/dws/create_dws_tables.sql`                   | Hive-style DWS table creation SQL / Hive 风格的 DWS 建表 SQL |

---

## 10. Relationship with ADS Layer / 与 ADS 层的关系

The DWS layer provides reusable summary data for the ADS layer.

DWS 层为 ADS 应用层提供可复用的汇总数据。

The `dws_daily_order_summary` table can support the following ADS tables:

`dws_daily_order_summary` 表可以支撑以下 ADS 表：

| ADS Table / ADS 表             | Description / 说明                          |
| ----------------------------- | ----------------------------------------- |
| `ads_daily_business_overview` | Daily business overview report / 每日经营概览报表 |
| `ads_gmv_trend`               | GMV trend report / GMV 趋势报表               |
| `ads_delivery_performance`    | Delivery performance report / 物流表现报表      |
| `ads_review_overview`         | Review performance report / 评价表现报表        |

These ADS tables will later be used for BI dashboard development.

这些 ADS 表后续将用于 BI 看板开发。

---

## 11. Summary / 总结

The DWS layer turns cleaned DWD detail data into reusable business summary tables.

DWS 层将清洗后的 DWD 明细数据加工为可复用的业务汇总表。

The first DWS table, `dws_daily_order_summary`, provides daily metrics for order count, GMV, customer count, delivery performance, review behavior, and average order value.

第一张 DWS 表 `dws_daily_order_summary` 提供了订单数、GMV、客户数、物流表现、评价行为和客单价等每日经营指标。

It is an important bridge between the DWD detail layer and the ADS reporting layer.

它是 DWD 明细层与 ADS 报表层之间的重要桥梁。
