{{ config(materialized='view') }}

-- Staging model for ODS order items / ODS 订单商品表 Staging 模型
-- Casts price and freight_value to numeric types.
-- 将 price 和 freight_value 转换为数值类型。

SELECT
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date::TIMESTAMP AS shipping_limit_date,
    COALESCE(price::NUMERIC(10,2), 0.0) AS price,
    COALESCE(freight_value::NUMERIC(10,2), 0.0) AS freight_value,
    loaded_at,
    dt
FROM {{ source('ods', 'order_items') }}