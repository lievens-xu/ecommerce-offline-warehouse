-- =========================================================
-- Project: E-commerce Offline Data Warehouse
-- Layer: DWS - Data Warehouse Summary
-- Description:
--   DWS layer stores subject-level aggregated data.
--   This file defines the daily order summary table.
-- =========================================================

CREATE DATABASE IF NOT EXISTS ecommerce_warehouse;

USE ecommerce_warehouse;

-- =========================================================
-- 1. Daily Order Summary
-- Source table: dwd_order_detail
-- Granularity: one row per purchase date
-- =========================================================
CREATE TABLE IF NOT EXISTS dws_daily_order_summary (
    purchase_date STRING COMMENT 'Purchase date',

    order_count BIGINT COMMENT 'Total number of orders',
    valid_order_count BIGINT COMMENT 'Total number of valid orders excluding canceled and unavailable orders',
    paid_order_count BIGINT COMMENT 'Total number of paid orders',
    unique_customer_count BIGINT COMMENT 'Number of unique customers',

    delivered_order_count BIGINT COMMENT 'Number of delivered orders',
    late_delivery_order_count BIGINT COMMENT 'Number of late delivery orders',
    delivery_rate DOUBLE COMMENT 'Delivered orders divided by total orders',
    late_delivery_rate DOUBLE COMMENT 'Late delivery orders divided by delivered orders',

    review_order_count BIGINT COMMENT 'Number of orders with reviews',
    review_comment_order_count BIGINT COMMENT 'Number of orders with review comments',
    review_rate DOUBLE COMMENT 'Orders with reviews divided by total orders',
    review_comment_rate DOUBLE COMMENT 'Orders with review comments divided by reviewed orders',

    total_payment_amount DOUBLE COMMENT 'Total payment amount',
    total_product_amount DOUBLE COMMENT 'Total product amount',
    total_freight_amount DOUBLE COMMENT 'Total freight amount',
    aov DOUBLE COMMENT 'Average order value',
    avg_product_amount_per_order DOUBLE COMMENT 'Average product amount per order',
    avg_freight_amount_per_order DOUBLE COMMENT 'Average freight amount per order',
    average_review_score DOUBLE COMMENT 'Average review score',

    dws_loaded_at TIMESTAMP COMMENT 'DWS loading timestamp'
)
COMMENT 'DWS daily order summary table'
PARTITIONED BY (dt STRING COMMENT 'ETL date partition')
STORED AS PARQUET;