-- =========================================================
-- Project: E-commerce Offline Data Warehouse
-- Layer: ADS - Application Data Service
-- Description:
--   ADS layer stores dashboard-ready application data.
--   This file defines the daily business overview table.
-- =========================================================

CREATE DATABASE IF NOT EXISTS ecommerce_warehouse;

USE ecommerce_warehouse;

-- =========================================================
-- 1. Daily Business Overview
-- Source table: dws_daily_order_summary
-- Granularity: one row per statistic date
-- =========================================================
CREATE TABLE IF NOT EXISTS ads_daily_business_overview (
    stat_date STRING COMMENT 'Statistic date',
    stat_month STRING COMMENT 'Statistic month',

    daily_order_count BIGINT COMMENT 'Daily order count',
    daily_valid_order_count BIGINT COMMENT 'Daily valid order count',
    daily_paid_order_count BIGINT COMMENT 'Daily paid order count',
    daily_unique_customer_count BIGINT COMMENT 'Daily unique customer count',

    daily_gmv DOUBLE COMMENT 'Daily GMV based on total payment amount',
    daily_product_amount DOUBLE COMMENT 'Daily product amount',
    daily_freight_amount DOUBLE COMMENT 'Daily freight amount',
    daily_aov DOUBLE COMMENT 'Daily average order value',

    daily_delivery_rate DOUBLE COMMENT 'Daily delivery rate',
    daily_late_delivery_rate DOUBLE COMMENT 'Daily late delivery rate',
    daily_review_rate DOUBLE COMMENT 'Daily review rate',
    daily_review_comment_rate DOUBLE COMMENT 'Daily review comment rate',
    daily_average_review_score DOUBLE COMMENT 'Daily average review score',

    valid_order_rate DOUBLE COMMENT 'Valid order count divided by total order count',
    paid_order_rate DOUBLE COMMENT 'Paid order count divided by total order count',

    gmv_7d_moving_avg DOUBLE COMMENT '7-day moving average of GMV',
    order_count_7d_moving_avg DOUBLE COMMENT '7-day moving average of order count',
    aov_7d_moving_avg DOUBLE COMMENT '7-day moving average of AOV',

    cumulative_gmv DOUBLE COMMENT 'Cumulative GMV',
    cumulative_order_count BIGINT COMMENT 'Cumulative order count',
    cumulative_customer_count BIGINT COMMENT 'Cumulative daily unique customer count',

    gmv_day_over_day_change DOUBLE COMMENT 'GMV day-over-day absolute change',
    order_count_day_over_day_change DOUBLE COMMENT 'Order count day-over-day absolute change',
    gmv_day_over_day_rate DOUBLE COMMENT 'GMV day-over-day growth rate',
    order_count_day_over_day_rate DOUBLE COMMENT 'Order count day-over-day growth rate',

    ads_loaded_at TIMESTAMP COMMENT 'ADS loading timestamp'
)
COMMENT 'ADS daily business overview table for BI dashboard'
PARTITIONED BY (dt STRING COMMENT 'ETL date partition')
STORED AS PARQUET;