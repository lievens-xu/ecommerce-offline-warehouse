{{ config(materialized='view') }}

-- Staging model for ODS order reviews / ODS 订单评价表 Staging 模型
--
-- ODS design principle: Preserve all raw rows without deduplication.
-- ODS 设计原则：保留所有原始行，不做去重。
--
-- review_id may contain duplicates in the raw Olist data.
-- review_id 在原始 Olist 数据中可能重复。
-- Duplicate handling (aggregation by order_id) happens in the DWD layer.
-- 重复处理（按 order_id 聚合）在 DWD 层完成。

SELECT
    review_id,
    order_id,
    review_score::INT AS review_score,
    review_comment_title,
    review_comment_message,
    review_creation_date::TIMESTAMP AS review_creation_date,
    review_answer_timestamp::TIMESTAMP AS review_answer_timestamp,
    loaded_at,
    dt
FROM {{ source('ods', 'order_reviews') }}