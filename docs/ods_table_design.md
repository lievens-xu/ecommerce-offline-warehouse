# ODS Layer Table Design

## 1. Purpose

The ODS layer stores raw business data from the original Olist e-commerce CSV files with minimal transformation.

The main goals of the ODS layer are:

* Preserve original business fields.
* Standardize table names.
* Add `dt` as the ETL date partition.
* Add `loaded_at` as the data loading timestamp.
* Provide stable source tables for the DWD detail layer.

---

## 2. Naming Convention

ODS table names follow this format:

```
ods_<business_entity>
```

Examples:

```
ods_orders
ods_customers
ods_order_items
ods_order_payments
ods_products
ods_sellers
```

---

## 3. Source-to-ODS Mapping

| Source CSV File                         | ODS Table                          | Main Business Key                | Description                             |
| --------------------------------------- | ---------------------------------- | -------------------------------- | --------------------------------------- |
| `olist_customers_dataset.csv`           | `ods_customers`                    | `customer_id`                    | Customer profile information            |
| `olist_orders_dataset.csv`              | `ods_orders`                       | `order_id`                       | Order lifecycle and delivery timestamps |
| `olist_order_items_dataset.csv`         | `ods_order_items`                  | `order_id`, `order_item_id`      | Product items within each order         |
| `olist_order_payments_dataset.csv`      | `ods_order_payments`               | `order_id`, `payment_sequential` | Payment records for each order          |
| `olist_order_reviews_dataset.csv`       | `ods_order_reviews`                | `review_id`                      | Customer review information             |
| `olist_products_dataset.csv`            | `ods_products`                     | `product_id`                     | Product attributes                      |
| `olist_sellers_dataset.csv`             | `ods_sellers`                      | `seller_id`                      | Seller profile information              |
| `olist_geolocation_dataset.csv`         | `ods_geolocation`                  | `geolocation_zip_code_prefix`    | Geolocation reference data              |
| `product_category_name_translation.csv` | `ods_product_category_translation` | `product_category_name`          | Product category translation mapping    |

---

## 4. Partition Design

All ODS tables include a `dt` partition field.

```
dt = ETL processing date
```

Example:

```
dt = 2026-06-22
```

This design makes it easier to support daily incremental loading in future ETL jobs.

Although the current dataset is static CSV data, adding a `dt` field makes the project closer to a real enterprise data warehouse, where data is usually loaded by date.

---

## 5. Additional Technical Fields

Each ODS table includes the following technical fields:

| Field       | Type        | Description                                      |
| ----------- | ----------- | ------------------------------------------------ |
| `loaded_at` | `TIMESTAMP` | Time when the data was loaded into the ODS layer |
| `dt`        | `STRING`    | ETL date partition                               |

These fields are not from the original source data. They are added during the raw-to-ODS loading process.

---

## 6. Design Principles

The ODS layer does not perform complex business cleaning.

Main principles:

* Original column names are preserved.
* Source data is kept as close to the original CSV files as possible.
* Null values are not removed in the ODS layer.
* Business standardization is handled in the DWD layer.
* The ODS layer focuses on traceability and data completeness.
* Each source CSV file maps to one ODS table.

For example, the Olist source file contains the following misspelled columns:

* `product_name_lenght`
* `product_description_lenght`

These names are kept unchanged in the ODS layer. They will be renamed in the DWD layer later.

---

## 7. ODS Table List

### 7.1 `ods_customers`

Source file:

```
olist_customers_dataset.csv
```

Business meaning:

This table stores raw customer profile information.

Main fields:

| Field                      | Description                |
| -------------------------- | -------------------------- |
| `customer_id`              | Customer ID used in orders |
| `customer_unique_id`       | Unique customer identifier |
| `customer_zip_code_prefix` | Customer zip code prefix   |
| `customer_city`            | Customer city              |
| `customer_state`           | Customer state             |
| `loaded_at`                | Data loading timestamp     |
| `dt`                       | ETL date partition         |

---

### 7.2 `ods_orders`

Source file:

```
olist_orders_dataset.csv
```

Business meaning:

This table stores raw order lifecycle information, including purchase time, approval time, delivery time, and estimated delivery time.

Main fields:

| Field                           | Description                           |
| ------------------------------- | ------------------------------------- |
| `order_id`                      | Order ID                              |
| `customer_id`                   | Customer ID                           |
| `order_status`                  | Order status                          |
| `order_purchase_timestamp`      | Order purchase timestamp              |
| `order_approved_at`             | Order approved timestamp              |
| `order_delivered_carrier_date`  | Order delivered to carrier timestamp  |
| `order_delivered_customer_date` | Order delivered to customer timestamp |
| `order_estimated_delivery_date` | Estimated delivery timestamp          |
| `loaded_at`                     | Data loading timestamp                |
| `dt`                            | ETL date partition                    |

---

### 7.3 `ods_order_items`

Source file:

```
olist_order_items_dataset.csv
```

Business meaning:

This table stores item-level information for each order. One order may contain multiple items.

Main fields:

| Field                 | Description                          |
| --------------------- | ------------------------------------ |
| `order_id`            | Order ID                             |
| `order_item_id`       | Item sequence number within an order |
| `product_id`          | Product ID                           |
| `seller_id`           | Seller ID                            |
| `shipping_limit_date` | Shipping deadline                    |
| `price`               | Product item price                   |
| `freight_value`       | Freight value                        |
| `loaded_at`           | Data loading timestamp               |
| `dt`                  | ETL date partition                   |

---

### 7.4 `ods_order_payments`

Source file:

```
olist_order_payments_dataset.csv
```

Business meaning:

This table stores payment information for each order. One order may have multiple payment records.

Main fields:

| Field                  | Description                    |
| ---------------------- | ------------------------------ |
| `order_id`             | Order ID                       |
| `payment_sequential`   | Payment sequence number        |
| `payment_type`         | Payment method                 |
| `payment_installments` | Number of payment installments |
| `payment_value`        | Payment amount                 |
| `loaded_at`            | Data loading timestamp         |
| `dt`                   | ETL date partition             |

---

### 7.5 `ods_order_reviews`

Source file:

```
olist_order_reviews_dataset.csv
```

Business meaning:

This table stores customer review information for orders.

Main fields:

| Field                     | Description               |
| ------------------------- | ------------------------- |
| `review_id`               | Review ID                 |
| `order_id`                | Order ID                  |
| `review_score`            | Review score from 1 to 5  |
| `review_comment_title`    | Review comment title      |
| `review_comment_message`  | Review comment message    |
| `review_creation_date`    | Review creation timestamp |
| `review_answer_timestamp` | Review answer timestamp   |
| `loaded_at`               | Data loading timestamp    |
| `dt`                      | ETL date partition        |

---

### 7.6 `ods_products`

Source file:

```
olist_products_dataset.csv
```

Business meaning:

This table stores raw product attribute information.

Main fields:

| Field                        | Description                                 |
| ---------------------------- | ------------------------------------------- |
| `product_id`                 | Product ID                                  |
| `product_category_name`      | Product category name in Portuguese         |
| `product_name_lenght`        | Original column: product name length        |
| `product_description_lenght` | Original column: product description length |
| `product_photos_qty`         | Number of product photos                    |
| `product_weight_g`           | Product weight in grams                     |
| `product_length_cm`          | Product length in cm                        |
| `product_height_cm`          | Product height in cm                        |
| `product_width_cm`           | Product width in cm                         |
| `loaded_at`                  | Data loading timestamp                      |
| `dt`                         | ETL date partition                          |

Note:

The source column names `product_name_lenght` and `product_description_lenght` are misspelled in the original dataset. They are kept unchanged in the ODS layer and will be renamed in the DWD layer.

---

### 7.7 `ods_sellers`

Source file:

```
olist_sellers_dataset.csv
```

Business meaning:

This table stores raw seller profile information.

Main fields:

| Field                    | Description            |
| ------------------------ | ---------------------- |
| `seller_id`              | Seller ID              |
| `seller_zip_code_prefix` | Seller zip code prefix |
| `seller_city`            | Seller city            |
| `seller_state`           | Seller state           |
| `loaded_at`              | Data loading timestamp |
| `dt`                     | ETL date partition     |

---

### 7.8 `ods_geolocation`

Source file:

```
olist_geolocation_dataset.csv
```

Business meaning:

This table stores zip-code-level geolocation information.

Main fields:

| Field                         | Description            |
| ----------------------------- | ---------------------- |
| `geolocation_zip_code_prefix` | Zip code prefix        |
| `geolocation_lat`             | Latitude               |
| `geolocation_lng`             | Longitude              |
| `geolocation_city`            | City                   |
| `geolocation_state`           | State                  |
| `loaded_at`                   | Data loading timestamp |
| `dt`                          | ETL date partition     |

---

### 7.9 `ods_product_category_translation`

Source file:

```
product_category_name_translation.csv
```

Business meaning:

This table stores product category translation mapping from Portuguese to English.

Main fields:

| Field                           | Description                         |
| ------------------------------- | ----------------------------------- |
| `product_category_name`         | Product category name in Portuguese |
| `product_category_name_english` | Product category name in English    |
| `loaded_at`                     | Data loading timestamp              |
| `dt`                            | ETL date partition                  |

---

## 8. Data Quality Considerations

The ODS layer only performs basic technical checks, such as:

* Whether the source file exists.
* Whether the file can be read successfully.
* Whether required columns exist.
* Whether the row count is greater than zero.
* Whether technical fields `loaded_at` and `dt` are added successfully.

The following business-level checks are not handled in the ODS layer:

* Order status standardization.
* Null value replacement.
* Duplicate business key handling.
* Invalid timestamp correction.
* Product category translation.
* Delivery delay calculation.
* Payment amount aggregation.

These checks and transformations will be handled in the DWD layer.

---

## 9. Relationship with Other Layers

The overall warehouse layering design is:

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

Layer responsibilities:

| Layer | Responsibility                                     |
| ----- | -------------------------------------------------- |
| Raw   | Original CSV files downloaded from the data source |
| ODS   | Raw data storage with minimal transformation       |
| DWD   | Cleaned and standardized detail data               |
| DWS   | Subject-level aggregated data                      |
| ADS   | Application-level reporting and dashboard data     |

---

## 10. Next Layer: DWD

The DWD layer will clean and standardize ODS data.

Planned DWD tables:

| DWD Table               | Description                                 |
| ----------------------- | ------------------------------------------- |
| `dwd_order_detail`      | Cleaned order-level detail table            |
| `dwd_order_item_detail` | Cleaned order item detail table             |
| `dwd_payment_detail`    | Cleaned payment detail table                |
| `dwd_product_detail`    | Cleaned product detail table                |
| `dwd_customer_detail`   | Cleaned customer detail table               |
| `dwd_seller_detail`     | Cleaned seller detail table                 |
| `dwd_review_detail`     | Cleaned review detail table                 |
| `dwd_logistics_detail`  | Cleaned logistics and delivery detail table |

---

## 11. Summary

The ODS layer is the foundation of this e-commerce offline data warehouse project.

It provides:

* A standardized raw data storage layer.
* A clear mapping between CSV files and warehouse tables.
* Technical fields for ETL traceability.
* A stable data source for later DWD cleaning and business modeling.

This design follows a typical offline data warehouse structure and prepares the project for further ETL development, data quality checks, and BI reporting.
