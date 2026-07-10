{{ config(materialized='view') }}

-- Staging model for ODS product category translation / ODS 商品类目翻译表 Staging 模型
-- Preserves all raw translation data.
-- 保留所有原始翻译数据。

SELECT
    product_category_name,
    product_category_name_english,
    loaded_at,
    dt
FROM {{ source('ods', 'product_category_translation') }}