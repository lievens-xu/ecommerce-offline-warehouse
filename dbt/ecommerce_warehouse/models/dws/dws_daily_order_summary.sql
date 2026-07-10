{{ config(materialized='table', schema='dws') }}

-- DWS Daily Order Summary / DWS 每日订单汇总表
--
-- Daily grain aggregation built from DWD order detail.
-- 基于 DWD 订单明细构建的日粒度汇总表。
--
-- Transformation steps / 转换步骤:
-- 1. Prepare DWD data (clean, flag order types)
-- 2. GROUP BY purchase_date with COUNT, SUM, AVG
-- 3. Calculate ratio metrics (delivery_rate, aov, etc.)
-- 4. Add technical fields

WITH

-- Step 1: Prepare DWD data with business flags
-- 第一步：准备 DWD 数据并添加业务标记
prepared AS (
    SELECT
        purchase_date::DATE AS purchase_date,
        order_id,
        customer_unique_id,
        order_status,
        COALESCE(total_payment_amount::NUMERIC, 0.0) AS total_payment_amount,
        COALESCE(total_product_amount::NUMERIC, 0.0) AS total_product_amount,
        COALESCE(total_freight_amount::NUMERIC, 0.0) AS total_freight_amount,
        average_review_score::NUMERIC AS average_review_score,
        COALESCE(review_count::INT, 0) AS review_count,
        COALESCE(has_review_comment::INT, 0) AS has_review_comment,
        COALESCE(is_delivered::INT, 0) AS is_delivered,
        COALESCE(is_late_delivery::INT, 0) AS is_late_delivery
    FROM {{ ref('dwd_order_detail') }}
    WHERE purchase_date IS NOT NULL
),

-- Step 1b: Add business flags
-- 第一步b：添加业务标记
flagged AS (
    SELECT
        *,
        -- Valid order: not canceled or unavailable / 有效订单：未取消或不可用
        CASE
            WHEN order_status NOT IN ('canceled', 'unavailable') THEN 1
            ELSE 0
        END AS is_valid_order,

        -- Paid order: has payment amount > 0 / 已支付订单
        CASE
            WHEN total_payment_amount > 0 THEN 1
            ELSE 0
        END AS is_paid_order,

        -- Has review: at least one review / 有评价
        CASE
            WHEN review_count > 0 THEN 1
            ELSE 0
        END AS has_review
    FROM prepared
),

-- Step 2: Daily aggregation
-- 第二步：每日聚合
daily AS (
    SELECT
        purchase_date,

        COUNT(DISTINCT order_id) AS order_count,
        SUM(is_valid_order) AS valid_order_count,
        SUM(is_paid_order) AS paid_order_count,
        COUNT(DISTINCT customer_unique_id) AS unique_customer_count,

        SUM(is_delivered) AS delivered_order_count,
        SUM(is_late_delivery) AS late_delivery_order_count,

        SUM(has_review) AS review_order_count,
        SUM(has_review_comment) AS review_comment_order_count,

        SUM(total_payment_amount) AS total_payment_amount,
        SUM(total_product_amount) AS total_product_amount,
        SUM(total_freight_amount) AS total_freight_amount,
        AVG(average_review_score) AS average_review_score
    FROM flagged
    GROUP BY purchase_date
)

-- Step 3 & 4: Calculate ratio metrics and add technical fields
-- 第三步和第四步：计算比率指标并添加技术字段
SELECT
    TO_CHAR(purchase_date, 'YYYY-MM-DD') AS purchase_date,

    order_count::BIGINT AS order_count,
    valid_order_count::BIGINT AS valid_order_count,
    paid_order_count::BIGINT AS paid_order_count,
    unique_customer_count::BIGINT AS unique_customer_count,

    delivered_order_count::BIGINT AS delivered_order_count,
    late_delivery_order_count::BIGINT AS late_delivery_order_count,

    -- delivery_rate: delivered / total orders / 配送率
    ROUND(
        CASE WHEN order_count = 0 THEN 0.0
             ELSE delivered_order_count::NUMERIC / order_count
        END, 4
    ) AS delivery_rate,

    -- late_delivery_rate: late / delivered orders / 延迟配送率
    ROUND(
        CASE WHEN delivered_order_count = 0 THEN 0.0
             ELSE late_delivery_order_count::NUMERIC / delivered_order_count
        END, 4
    ) AS late_delivery_rate,

    review_order_count::BIGINT AS review_order_count,
    review_comment_order_count::BIGINT AS review_comment_order_count,

    -- review_rate: orders with review / total orders / 评价率
    ROUND(
        CASE WHEN order_count = 0 THEN 0.0
             ELSE review_order_count::NUMERIC / order_count
        END, 4
    ) AS review_rate,

    -- review_comment_rate: orders with comment / orders with review / 评价留言率
    ROUND(
        CASE WHEN review_order_count = 0 THEN 0.0
             ELSE review_comment_order_count::NUMERIC / review_order_count
        END, 4
    ) AS review_comment_rate,

    ROUND(total_payment_amount::NUMERIC, 4) AS total_payment_amount,
    ROUND(total_product_amount::NUMERIC, 4) AS total_product_amount,
    ROUND(total_freight_amount::NUMERIC, 4) AS total_freight_amount,

    -- AOV: Average Order Value / 平均订单价值
    ROUND(
        CASE WHEN order_count = 0 THEN 0.0
             ELSE total_payment_amount / order_count
        END, 4
    ) AS aov,

    -- Average product amount per order / 每单平均商品金额
    ROUND(
        CASE WHEN order_count = 0 THEN 0.0
             ELSE total_product_amount / order_count
        END, 4
    ) AS avg_product_amount_per_order,

    -- Average freight amount per order / 每单平均运费
    ROUND(
        CASE WHEN order_count = 0 THEN 0.0
             ELSE total_freight_amount / order_count
        END, 4
    ) AS avg_freight_amount_per_order,

    ROUND(average_review_score::NUMERIC, 4) AS average_review_score,

    -- Technical fields / 技术字段
    TO_CHAR(CURRENT_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS') AS dws_loaded_at,
    CURRENT_DATE AS dt

FROM daily
ORDER BY purchase_date