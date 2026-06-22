-- =========================================================
-- Project: E-commerce Offline Data Warehouse
-- Layer: ODS - Operational Data Store
-- Description:
--   ODS layer keeps raw business data with minimal changes.
--   Tables are designed in Hive-style SQL and can be adapted
--   to Spark SQL / Hive / data lake environments.
-- =========================================================

CREATE DATABASE IF NOT EXISTS ecommerce_warehouse;

USE ecommerce_warehouse;

-- =========================================================
-- 1. Customers
-- Source file: olist_customers_dataset.csv
-- =========================================================
CREATE TABLE IF NOT EXISTS ods_customers (
    customer_id STRING COMMENT 'Customer ID used in orders',
    customer_unique_id STRING COMMENT 'Unique customer identifier',
    customer_zip_code_prefix STRING COMMENT 'Customer zip code prefix',
    customer_city STRING COMMENT 'Customer city',
    customer_state STRING COMMENT 'Customer state',
    loaded_at TIMESTAMP COMMENT 'Data loading timestamp'
)
COMMENT 'ODS table for raw customer data'
PARTITIONED BY (dt STRING COMMENT 'ETL date partition')
STORED AS PARQUET;


-- =========================================================
-- 2. Orders
-- Source file: olist_orders_dataset.csv
-- =========================================================
CREATE TABLE IF NOT EXISTS ods_orders (
    order_id STRING COMMENT 'Order ID',
    customer_id STRING COMMENT 'Customer ID',
    order_status STRING COMMENT 'Order status',
    order_purchase_timestamp TIMESTAMP COMMENT 'Order purchase timestamp',
    order_approved_at TIMESTAMP COMMENT 'Order approved timestamp',
    order_delivered_carrier_date TIMESTAMP COMMENT 'Order delivered to carrier timestamp',
    order_delivered_customer_date TIMESTAMP COMMENT 'Order delivered to customer timestamp',
    order_estimated_delivery_date TIMESTAMP COMMENT 'Estimated delivery timestamp',
    loaded_at TIMESTAMP COMMENT 'Data loading timestamp'
)
COMMENT 'ODS table for raw order data'
PARTITIONED BY (dt STRING COMMENT 'ETL date partition')
STORED AS PARQUET;


-- =========================================================
-- 3. Order Items
-- Source file: olist_order_items_dataset.csv
-- =========================================================
CREATE TABLE IF NOT EXISTS ods_order_items (
    order_id STRING COMMENT 'Order ID',
    order_item_id INT COMMENT 'Item sequence number within an order',
    product_id STRING COMMENT 'Product ID',
    seller_id STRING COMMENT 'Seller ID',
    shipping_limit_date TIMESTAMP COMMENT 'Shipping deadline',
    price DOUBLE COMMENT 'Product item price',
    freight_value DOUBLE COMMENT 'Freight value',
    loaded_at TIMESTAMP COMMENT 'Data loading timestamp'
)
COMMENT 'ODS table for raw order item data'
PARTITIONED BY (dt STRING COMMENT 'ETL date partition')
STORED AS PARQUET;


-- =========================================================
-- 4. Order Payments
-- Source file: olist_order_payments_dataset.csv
-- =========================================================
CREATE TABLE IF NOT EXISTS ods_order_payments (
    order_id STRING COMMENT 'Order ID',
    payment_sequential INT COMMENT 'Payment sequence number',
    payment_type STRING COMMENT 'Payment method',
    payment_installments INT COMMENT 'Number of payment installments',
    payment_value DOUBLE COMMENT 'Payment amount',
    loaded_at TIMESTAMP COMMENT 'Data loading timestamp'
)
COMMENT 'ODS table for raw order payment data'
PARTITIONED BY (dt STRING COMMENT 'ETL date partition')
STORED AS PARQUET;


-- =========================================================
-- 5. Order Reviews
-- Source file: olist_order_reviews_dataset.csv
-- =========================================================
CREATE TABLE IF NOT EXISTS ods_order_reviews (
    review_id STRING COMMENT 'Review ID',
    order_id STRING COMMENT 'Order ID',
    review_score INT COMMENT 'Review score from 1 to 5',
    review_comment_title STRING COMMENT 'Review comment title',
    review_comment_message STRING COMMENT 'Review comment message',
    review_creation_date TIMESTAMP COMMENT 'Review creation timestamp',
    review_answer_timestamp TIMESTAMP COMMENT 'Review answer timestamp',
    loaded_at TIMESTAMP COMMENT 'Data loading timestamp'
)
COMMENT 'ODS table for raw review data'
PARTITIONED BY (dt STRING COMMENT 'ETL date partition')
STORED AS PARQUET;


-- =========================================================
-- 6. Products
-- Source file: olist_products_dataset.csv
-- Note:
--   Original Olist column names contain misspellings:
--   product_name_lenght, product_description_lenght.
--   Keep original names in ODS layer.
--   Rename them in DWD layer later.
-- =========================================================
CREATE TABLE IF NOT EXISTS ods_products (
    product_id STRING COMMENT 'Product ID',
    product_category_name STRING COMMENT 'Product category name in Portuguese',
    product_name_lenght INT COMMENT 'Original column: product name length',
    product_description_lenght INT COMMENT 'Original column: product description length',
    product_photos_qty INT COMMENT 'Number of product photos',
    product_weight_g INT COMMENT 'Product weight in grams',
    product_length_cm INT COMMENT 'Product length in cm',
    product_height_cm INT COMMENT 'Product height in cm',
    product_width_cm INT COMMENT 'Product width in cm',
    loaded_at TIMESTAMP COMMENT 'Data loading timestamp'
)
COMMENT 'ODS table for raw product data'
PARTITIONED BY (dt STRING COMMENT 'ETL date partition')
STORED AS PARQUET;


-- =========================================================
-- 7. Sellers
-- Source file: olist_sellers_dataset.csv
-- =========================================================
CREATE TABLE IF NOT EXISTS ods_sellers (
    seller_id STRING COMMENT 'Seller ID',
    seller_zip_code_prefix STRING COMMENT 'Seller zip code prefix',
    seller_city STRING COMMENT 'Seller city',
    seller_state STRING COMMENT 'Seller state',
    loaded_at TIMESTAMP COMMENT 'Data loading timestamp'
)
COMMENT 'ODS table for raw seller data'
PARTITIONED BY (dt STRING COMMENT 'ETL date partition')
STORED AS PARQUET;


-- =========================================================
-- 8. Geolocation
-- Source file: olist_geolocation_dataset.csv
-- =========================================================
CREATE TABLE IF NOT EXISTS ods_geolocation (
    geolocation_zip_code_prefix STRING COMMENT 'Zip code prefix',
    geolocation_lat DOUBLE COMMENT 'Latitude',
    geolocation_lng DOUBLE COMMENT 'Longitude',
    geolocation_city STRING COMMENT 'City',
    geolocation_state STRING COMMENT 'State',
    loaded_at TIMESTAMP COMMENT 'Data loading timestamp'
)
COMMENT 'ODS table for raw geolocation data'
PARTITIONED BY (dt STRING COMMENT 'ETL date partition')
STORED AS PARQUET;


-- =========================================================
-- 9. Product Category Translation
-- Source file: product_category_name_translation.csv
-- =========================================================
CREATE TABLE IF NOT EXISTS ods_product_category_translation (
    product_category_name STRING COMMENT 'Product category name in Portuguese',
    product_category_name_english STRING COMMENT 'Product category name in English',
    loaded_at TIMESTAMP COMMENT 'Data loading timestamp'
)
COMMENT 'ODS table for product category translation data'
PARTITIONED BY (dt STRING COMMENT 'ETL date partition')
STORED AS PARQUET;