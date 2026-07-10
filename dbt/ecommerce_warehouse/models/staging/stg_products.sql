{{ config(materialized='view') }}

-- Staging model for ODS products / ODS 商品表 Staging 模型
-- Casts dimension fields to INTEGER.
-- 将尺寸字段转换为 INTEGER。

SELECT
    product_id,
    product_category_name,
    product_name_lenght::INT AS product_name_lenght,
    product_description_lenght::INT AS product_description_lenght,
    product_photos_qty::INT AS product_photos_qty,
    product_weight_g::INT AS product_weight_g,
    product_length_cm::INT AS product_length_cm,
    product_height_cm::INT AS product_height_cm,
    product_width_cm::INT AS product_width_cm,
    loaded_at,
    dt
FROM {{ source('ods', 'products') }}