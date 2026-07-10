{{ config(materialized='table', schema='ads') }}

-- ADS Customer RFM Segmentation / ADS 客户 RFM 分层表
--
-- Customer-level RFM (Recency, Frequency, Monetary) segmentation built from the
-- DWD order detail table. Mirrors scripts/build_ads_customer_rfm.py.
-- 基于 DWD 订单明细构建的客户级 RFM 分层表，与 scripts/build_ads_customer_rfm.py 一致。
--
-- Transformation steps / 转换步骤:
-- 1. Keep valid orders (exclude canceled/unavailable)
-- 2. Aggregate to customer level (last purchase, frequency, monetary)
-- 3. Recency vs snapshot date (max purchase date + 1 day)
-- 4. NTILE(5) quintile scores for R/F/M
-- 5. Map (R,F) to business segment
-- 6. Add technical fields

WITH

-- Step 1: valid orders only / 第一步：仅保留有效订单
valid_orders AS (
    SELECT
        customer_unique_id,
        order_id,
        order_purchase_timestamp,
        COALESCE(total_payment_amount::NUMERIC, 0.0) AS total_payment_amount
    FROM {{ ref('dwd_order_detail') }}
    WHERE customer_unique_id IS NOT NULL
      AND order_purchase_timestamp IS NOT NULL
      AND order_status NOT IN ('canceled', 'unavailable')
),

-- Snapshot date = last purchase in the dataset + 1 day / 快照日 = 最后购买日 +1 天
snapshot AS (
    SELECT (MAX(order_purchase_timestamp)::DATE + 1) AS snapshot_date
    FROM valid_orders
),

-- Step 2 & 3: customer-level R/F/M / 第二、三步：客户级 R/F/M
rfm_base AS (
    SELECT
        v.customer_unique_id,
        (s.snapshot_date - MAX(v.order_purchase_timestamp)::DATE) AS recency,
        COUNT(DISTINCT v.order_id) AS frequency,
        ROUND(SUM(v.total_payment_amount), 2) AS monetary
    FROM valid_orders v
    CROSS JOIN snapshot s
    GROUP BY v.customer_unique_id, s.snapshot_date
),

-- Step 4: quintile scores (NTILE) / 第四步：五分位打分
rfm_scored AS (
    SELECT
        customer_unique_id,
        recency,
        frequency,
        monetary,
        -- 更小的 recency 分更高：按 recency 降序分桶
        NTILE(5) OVER (ORDER BY recency DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
    FROM rfm_base
)

-- Step 5 & 6: segment mapping + technical fields / 第五、六步：分层映射 + 技术字段
SELECT
    customer_unique_id,
    recency,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    (r_score + f_score + m_score) AS rfm_score,
    (r_score::TEXT || f_score::TEXT || m_score::TEXT) AS rfm_cell,

    -- 分层顺序与 Python assign_segment 完全一致 / segment order matches Python
    CASE
        WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions / 重要价值客户'
        WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal / 忠诚客户'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'Recent / 新近活跃客户'
        WHEN r_score = 3 AND f_score <= 2 THEN 'Promising / 有潜力客户'
        WHEN r_score = 2 AND f_score >= 3 THEN 'At Risk / 需挽留客户'
        WHEN r_score <= 2 AND f_score >= 4 THEN 'Cant Lose / 高价值流失预警'
        WHEN r_score = 2 AND f_score <= 2 THEN 'Hibernating / 沉睡客户'
        ELSE 'Lost / 已流失客户'
    END AS segment,

    -- Technical fields / 技术字段
    TO_CHAR(CURRENT_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS') AS ads_loaded_at,
    CURRENT_DATE AS dt

FROM rfm_scored
ORDER BY monetary DESC
