# ODS Load Process / ODS 数据加载流程

## 1. Purpose / 目的

This document describes how raw CSV files are loaded into the ODS layer.

本文档说明如何将原始 CSV 文件加载到 ODS 原始数据层。

The ODS loading process is implemented by the following script:

ODS 数据加载流程由以下脚本实现：

```
scripts/load_raw_to_ods.py
```

---

## 2. Input Data / 输入数据

The input files are original CSV files stored in:

输入数据为原始 CSV 文件，存放在：

```
data/raw/
```

Expected source files include:

预期的原始数据文件包括：

| Source File / 原始文件                      | ODS Table / ODS 表                  |
| --------------------------------------- | ---------------------------------- |
| `olist_customers_dataset.csv`           | `ods_customers`                    |
| `olist_orders_dataset.csv`              | `ods_orders`                       |
| `olist_order_items_dataset.csv`         | `ods_order_items`                  |
| `olist_order_payments_dataset.csv`      | `ods_order_payments`               |
| `olist_order_reviews_dataset.csv`       | `ods_order_reviews`                |
| `olist_products_dataset.csv`            | `ods_products`                     |
| `olist_sellers_dataset.csv`             | `ods_sellers`                      |
| `olist_geolocation_dataset.csv`         | `ods_geolocation`                  |
| `product_category_name_translation.csv` | `ods_product_category_translation` |

---

## 3. Output Data / 输出数据

The output files are ODS CSV files stored in:

输出数据为 ODS 层 CSV 文件，存放在：

```
data/ods/
```

Each source file is converted into one ODS table file.

每个原始 CSV 文件会被转换为一个对应的 ODS 表文件。

Example:

示例：

```
data/raw/olist_orders_dataset.csv
    ↓
data/ods/ods_orders.csv
```

---

## 4. Technical Fields / 技术字段

During the ODS loading process, two technical fields are added to each table:

在 ODS 加载过程中，每张表都会新增两个技术字段：

| Field / 字段  | Description / 说明                           |
| ----------- | ------------------------------------------ |
| `loaded_at` | Data loading timestamp / 数据加载时间            |
| `dt`        | ETL processing date partition / ETL 处理日期分区 |

Example:

示例：

| loaded_at             | dt           |
| --------------------- | ------------ |
| `2026-06-22 13:30:00` | `2026-06-22` |

These fields are used for ETL traceability and future incremental loading.

这些字段用于 ETL 链路追踪，并为后续增量加载做准备。

---

## 5. Processing Logic / 处理逻辑

The script performs the following steps:

脚本会执行以下步骤：

1. Check whether all required source files exist.
   检查所有必需的原始 CSV 文件是否存在。

2. Read each CSV file with encoding fallback.
   使用多种编码方式读取 CSV 文件，避免编码错误。

3. Add `loaded_at` and `dt` fields.
   添加 `loaded_at` 和 `dt` 技术字段。

4. Rename the output table according to the ODS naming convention.
   按照 ODS 命名规范生成输出表名。

5. Save the processed data into `data/ods/`.
   将处理后的数据保存到 `data/ods/` 目录。

6. Generate an ODS load report.
   生成 ODS 加载报告。

---

## 6. Load Report / 加载报告

After the script runs successfully, a load report will be generated:

脚本成功运行后，会生成加载报告：

```
docs/ods_load_report.csv
```

The report includes:

报告内容包括：

| Column / 字段             | Description / 说明                     |
| ----------------------- | ------------------------------------ |
| `source_file`           | Source CSV file name / 原始 CSV 文件名    |
| `ods_table`             | Target ODS table name / 目标 ODS 表名    |
| `output_file`           | Output file path / 输出文件路径            |
| `original_row_count`    | Row count before loading / 加载前行数     |
| `original_column_count` | Column count before loading / 加载前字段数 |
| `output_row_count`      | Row count after loading / 加载后行数      |
| `output_column_count`   | Column count after loading / 加载后字段数  |
| `loaded_at`             | Loading timestamp / 加载时间             |
| `dt`                    | ETL date partition / ETL 日期分区        |
| `status`                | Loading status / 加载状态                |

---

## 7. Design Notes / 设计说明

The ODS layer keeps the source data as close to the original files as possible.

ODS 层会尽量保持数据与原始文件一致。

At this stage, the script does not perform complex business cleaning.

在这一阶段，脚本不会进行复杂的业务清洗。

For example:

例如：

* Missing values are not removed.
  不删除空值。

* Original column names are preserved.
  保留原始字段名。

* Business fields are not renamed.
  不重命名业务字段。

* Business metrics are not calculated.
  不计算业务指标。

Business cleaning and standardization will be handled in the DWD layer.

业务清洗与标准化将在 DWD 明细层完成。

---

## 8. Relationship with Warehouse Layers / 与数仓分层的关系

The current step belongs to the Raw-to-ODS process.

当前步骤属于 Raw 到 ODS 的数据加载流程。

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

In the next step, ODS data will be cleaned and standardized into DWD detail tables.

下一步会将 ODS 数据清洗并标准化为 DWD 明细层数据表。

---

## 9. Summary / 总结

The ODS loading process completes the first data engineering step of this project.

ODS 数据加载流程完成了本项目的第一个数据工程环节。

It provides standardized raw data tables for later DWD modeling, data quality checks, aggregation, and dashboard development.

它为后续 DWD 建模、数据质量校验、指标汇总和 BI 看板开发提供了标准化的原始数据基础。
