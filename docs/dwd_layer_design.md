# DWD Layer Design / DWD 明细层设计

## 1. Purpose / 目的

The DWD layer stores cleaned and standardized detail-level data.

DWD 层用于存储经过清洗和标准化后的明细级数据。

Compared with the ODS layer, the DWD layer focuses more on business usability.

相比 ODS 层，DWD 层更加关注数据的业务可用性。

The main goals of the DWD layer are:

DWD 层的主要目标包括：

* Clean and standardize raw ODS data.
  清洗并标准化 ODS 原始数据。

* Convert raw fields into business-friendly fields.
  将原始字段转换为更适合业务分析的字段。

* Build stable detail tables for later aggregation.
  构建稳定的明细表，为后续汇总层提供基础。

* Prepare data for DWS and ADS layers.
  为后续 DWS 汇总层和 ADS 应用层做准备。

---

## 2. Layer Position / 分层位置

The DWD layer is located between the ODS layer and the DWS layer.

DWD 层位于 ODS 原始层和 DWS 汇总层之间。

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

In this project, the first DWD table is:

在本项目中，第一张 DWD 表为：

```
dwd_order_detail
```

---

## 3. Table: dwd_order_detail / 表：dwd_order_detail

### 3.1 Business Meaning / 业务含义

The `dwd_order_detail` table is an order-level detail wide table.

`dwd_order_detail` 表是一张订单粒度的明细宽表。

Each row represents one order.

每一行代表一笔订单。

This table combines order, customer, payment, item, review, and logistics information.

该表整合了订单、客户、支付、商品、评价和物流信息。

It will be used to support later business metrics such as GMV, order count, average order value, customer repurchase rate, review score, and delivery delay rate.

该表后续可用于支持 GMV、订单量、客单价、用户复购率、评价分数和物流延迟率等业务指标。

---

## 4. Source Tables / 来源表

The `dwd_order_detail` table is built from the following ODS tables:

`dwd_order_detail` 表由以下 ODS 表加工得到：

| ODS Table / ODS 表    | Usage / 用途                                                                       |
| -------------------- | -------------------------------------------------------------------------------- |
| `ods_orders`         | Provides order lifecycle information / 提供订单生命周期信息                                |
| `ods_customers`      | Provides customer profile information / 提供客户画像信息                                 |
| `ods_order_items`    | Provides item, product, seller, price, and freight information / 提供商品、卖家、价格和运费信息 |
| `ods_order_payments` | Provides payment amount and payment method information / 提供支付金额和支付方式信息           |
| `ods_order_reviews`  | Provides customer review information / 提供客户评价信息                                  |

---

## 5. Processing Logic / 加工逻辑

The DWD building script performs the following steps:

DWD 构建脚本会执行以下步骤：

1. Read required ODS tables.
   读取所需的 ODS 表。

2. Convert timestamp fields into datetime format.
   将时间字段转换为 datetime 类型。

3. Aggregate order item data to order level.
   将订单商品明细聚合到订单粒度。

4. Aggregate payment data to order level.
   将支付明细聚合到订单粒度。

5. Aggregate review data to order level.
   将评价数据聚合到订单粒度。

6. Join order, customer, item, payment, and review data.
   关联订单、客户、商品、支付和评价数据。

7. Calculate logistics-related fields.
   计算物流相关字段。

8. Add DWD technical fields.
   添加 DWD 层技术字段。

9. Save the result to `data/dwd/dwd_order_detail.csv`.
   将结果保存到 `data/dwd/dwd_order_detail.csv`。

---

## 6. Key Field Design / 核心字段设计

| Field / 字段                 | Description / 说明                                                |
| -------------------------- | --------------------------------------------------------------- |
| `order_id`                 | Order ID / 订单 ID                                                |
| `customer_id`              | Customer ID used in orders / 订单中的客户 ID                          |
| `customer_unique_id`       | Unique customer identifier / 唯一客户 ID                            |
| `customer_city`            | Customer city / 客户城市                                            |
| `customer_state`           | Customer state / 客户所在州                                          |
| `order_status`             | Order status / 订单状态                                             |
| `order_purchase_timestamp` | Order purchase timestamp / 下单时间                                 |
| `purchase_date`            | Purchase date / 下单日期                                            |
| `purchase_month`           | Purchase month / 下单月份                                           |
| `order_item_count`         | Number of items in the order / 订单商品行数                           |
| `product_count`            | Number of distinct products in the order / 订单中不同商品数量            |
| `seller_count`             | Number of distinct sellers in the order / 订单中不同卖家数量             |
| `total_product_amount`     | Total product amount / 商品总金额                                    |
| `total_freight_amount`     | Total freight amount / 运费总金额                                    |
| `total_payment_amount`     | Total payment amount / 支付总金额                                    |
| `main_payment_type`        | Main payment method / 主要支付方式                                    |
| `average_review_score`     | Average review score / 平均评价分数                                   |
| `delivery_days`            | Actual delivery days / 实际配送天数                                   |
| `estimated_delivery_days`  | Estimated delivery days / 预计配送天数                                |
| `delivery_delay_days`      | Delivery delay days / 配送延迟天数                                    |
| `is_delivered`             | Whether the order was delivered / 订单是否已送达                       |
| `is_late_delivery`         | Whether the order was delivered later than estimated / 订单是否延迟送达 |
| `dwd_loaded_at`            | DWD loading timestamp / DWD 加载时间                                |
| `dt`                       | ETL date partition / ETL 日期分区                                   |

---

## 7. Data Granularity / 数据粒度

The granularity of `dwd_order_detail` is one row per order.

`dwd_order_detail` 的数据粒度是一行一笔订单。

Granularity:

数据粒度：

```
order_id
```

This means that item-level, payment-level, and review-level data must be aggregated before joining into this table.

这意味着商品明细、支付明细和评价明细都需要先聚合到订单粒度，再关联到该表中。

---

## 8. Data Cleaning Rules / 数据清洗规则

The current DWD table applies the following cleaning rules:

当前 DWD 表应用了以下清洗规则：

| Rule / 规则                        | Description / 说明                                                                        |
| -------------------------------- | --------------------------------------------------------------------------------------- |
| Datetime parsing / 时间解析          | Convert order lifecycle fields into datetime format / 将订单生命周期字段转换为 datetime 类型          |
| Numeric conversion / 数值转换        | Convert amount fields into numeric type / 将金额字段转换为数值类型                                  |
| Missing amount handling / 金额缺失处理 | Fill missing aggregated amount values with 0 / 聚合后的缺失金额填充为 0                            |
| Payment aggregation / 支付聚合       | Aggregate multiple payment records into order-level payment metrics / 将多条支付记录聚合为订单级支付指标 |
| Item aggregation / 商品聚合          | Aggregate multiple order items into order-level item metrics / 将多条商品明细聚合为订单级商品指标        |
| Review aggregation / 评价聚合        | Aggregate review records into order-level review metrics / 将评价记录聚合为订单级评价指标              |
| Logistics calculation / 物流计算     | Calculate delivery days and delay days / 计算配送天数和延迟天数                                    |

---

## 9. Output Files / 输出文件

After running the DWD building script, the following files are generated:

运行 DWD 构建脚本后，会生成以下文件：

| File / 文件                                  | Description / 说明                            |
| ------------------------------------------ | ------------------------------------------- |
| `data/dwd/dwd_order_detail.csv`            | Main DWD order detail table / 核心订单明细宽表      |
| `docs/dwd_order_detail_report.csv`         | Summary report of the DWD table / DWD 表汇总报告 |
| `docs/dwd_order_detail_column_profile.csv` | Column-level profiling report / 字段级数据探查报告   |

---

## 10. Relationship with Later Layers / 与后续分层的关系

The `dwd_order_detail` table will be used to build DWS subject-level summary tables.

`dwd_order_detail` 表将用于构建 DWS 主题汇总表。

Planned DWS tables include:

计划构建的 DWS 表包括：

| DWS Table / DWS 表                  | Description / 说明                              |
| ---------------------------------- | --------------------------------------------- |
| `dws_daily_order_summary`          | Daily order and GMV summary / 每日订单与 GMV 汇总    |
| `dws_customer_purchase_summary`    | Customer purchase behavior summary / 用户购买行为汇总 |
| `dws_city_order_summary`           | City-level order summary / 城市订单汇总             |
| `dws_delivery_performance_summary` | Delivery performance summary / 物流表现汇总         |
| `dws_payment_type_summary`         | Payment method summary / 支付方式汇总               |

These DWS tables will then support ADS reporting tables and BI dashboards.

这些 DWS 表后续会支撑 ADS 报表层和 BI 看板。

---

## 11. Summary / 总结

The DWD layer turns raw ODS data into clean and business-friendly detail data.

DWD 层将 ODS 原始数据加工为清洗后、业务可用的明细数据。

The first DWD table, `dwd_order_detail`, is the core order-level wide table of this project.

第一张 DWD 表 `dwd_order_detail` 是本项目的核心订单级明细宽表。

It provides a stable foundation for later metric calculation, aggregation, and dashboard development.

它为后续指标计算、数据汇总和看板开发提供了稳定的数据基础。
