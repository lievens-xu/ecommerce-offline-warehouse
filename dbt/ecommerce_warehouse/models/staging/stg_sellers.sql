{{ config(materialized='view') }}

-- Staging model for ODS sellers / ODS 卖家表 Staging 模型
-- Preserves all raw seller data with explicit type casting.
-- 保留所有原始卖家数据，进行显式类型转换。

SELECT
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state,
    loaded_at,
    dt
FROM {{ source('ods', 'sellers') }}