{{ config(materialized='table', schema='ads') }}

-- ADS Geographic (State) Summary / ADS 地域（州级）汇总表
--
-- State-level business and delivery metrics built from the DWD order detail table.
-- Mirrors scripts/build_ads_geo_state_summary.py.
-- 基于 DWD 订单明细的州级经营与物流指标，与 scripts/build_ads_geo_state_summary.py 一致。
--
-- Transformation steps / 转换步骤:
-- 1. Keep valid orders with a non-null state
-- 2. Aggregate to state level
-- 3. Derived metrics (AOV, delivery rate, late rate) + GMV rank & share
-- 4. Add technical fields

WITH

-- Step 1: valid orders / 第一步：有效订单
valid_orders AS (
    SELECT
        customer_state,
        order_id,
        customer_unique_id,
        COALESCE(total_payment_amount::NUMERIC, 0.0) AS total_payment_amount,
        delivery_days::NUMERIC AS delivery_days,
        average_review_score::NUMERIC AS average_review_score,
        COALESCE(is_delivered::INT, 0) AS is_delivered,
        COALESCE(is_late_delivery::INT, 0) AS is_late_delivery
    FROM {{ ref('dwd_order_detail') }}
    WHERE customer_state IS NOT NULL
      AND order_status NOT IN ('canceled', 'unavailable')
),

-- Step 2: aggregate to state / 第二步：聚合到州
state_agg AS (
    SELECT
        customer_state,
        COUNT(DISTINCT order_id) AS order_count,
        COUNT(DISTINCT customer_unique_id) AS customer_count,
        ROUND(SUM(total_payment_amount), 2) AS gmv,
        SUM(is_delivered) AS delivered_count,
        SUM(is_late_delivery) AS late_delivered_count,
        ROUND(AVG(delivery_days), 2) AS avg_delivery_days,
        ROUND(AVG(average_review_score), 2) AS avg_review_score
    FROM valid_orders
    GROUP BY customer_state
),

-- Step 3: derived metrics + rank/share / 第三步：派生指标 + 排名/占比
enriched AS (
    SELECT
        *,
        ROUND(gmv / NULLIF(order_count, 0), 2) AS aov,
        ROUND(delivered_count::NUMERIC / NULLIF(order_count, 0), 4) AS delivery_rate,
        ROUND(late_delivered_count::NUMERIC / NULLIF(delivered_count, 0), 4) AS late_delivery_rate,
        ROW_NUMBER() OVER (ORDER BY gmv DESC) AS gmv_rank,
        ROUND(gmv / SUM(gmv) OVER () * 100, 2) AS gmv_share_pct
    FROM state_agg
)

-- Step 4: final output / 第四步：最终输出
SELECT
    gmv_rank,
    customer_state,
    gmv,
    gmv_share_pct,
    order_count,
    customer_count,
    aov,
    delivery_rate,
    late_delivery_rate,
    avg_delivery_days,
    avg_review_score,
    TO_CHAR(CURRENT_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS') AS ads_loaded_at,
    CURRENT_DATE AS dt
FROM enriched
ORDER BY gmv_rank
