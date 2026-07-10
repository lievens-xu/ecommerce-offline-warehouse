{{ config(materialized='view') }}

-- Staging model for ODS customers / ODS 客户表 Staging 模型
-- Preserves all raw customer data with explicit type casting.
-- 保留所有原始客户数据，进行显式类型转换。

SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state,
    loaded_at,
    dt
FROM {{ source('ods', 'customers') }}