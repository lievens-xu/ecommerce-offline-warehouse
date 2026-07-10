{{ config(materialized='view') }}

-- Staging model for ODS orders / ODS 订单表 Staging 模型
-- Casts timestamp fields and standardizes order_status to lowercase.
-- 转换时间戳字段，并将 order_status 标准化为小写。

SELECT
    order_id,
    customer_id,
    LOWER(TRIM(COALESCE(order_status, ''))) AS order_status,
    order_purchase_timestamp::TIMESTAMP AS order_purchase_timestamp,
    order_approved_at::TIMESTAMP AS order_approved_at,
    order_delivered_carrier_date::TIMESTAMP AS order_delivered_carrier_date,
    order_delivered_customer_date::TIMESTAMP AS order_delivered_customer_date,
    order_estimated_delivery_date::TIMESTAMP AS order_estimated_delivery_date,
    loaded_at,
    dt
FROM {{ source('ods', 'orders') }}