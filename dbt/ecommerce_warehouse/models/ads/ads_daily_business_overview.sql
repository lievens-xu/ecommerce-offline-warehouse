{{ config(materialized='table', schema='ads') }}

-- ADS Daily Business Overview / ADS 每日经营概览表
--
-- Dashboard-ready daily business overview built from DWS daily summary.
-- 基于 DWS 每日汇总构建的可视化经营概览表。
--
-- Transformation steps / 转换步骤:
-- 1. Rename DWS fields with daily_ prefix
-- 2. Calculate derived rates (valid_order_rate, paid_order_rate)
-- 3. Window functions: 7-day moving averages (AVG OVER ROWS 6 PRECEDING)
-- 4. Window functions: cumulative metrics (SUM OVER UNBOUNDED PRECEDING)
-- 5. LAG functions: day-over-day changes and rates
-- 6. Add technical fields

WITH

-- Step 1: Prepare DWS data with field renaming and casting
-- 第一步：准备 DWS 数据，重命名字段并进行类型转换
prepared AS (
    SELECT
        purchase_date AS stat_date,
        TO_CHAR(purchase_date::DATE, 'YYYY-MM') AS stat_month,

        COALESCE(order_count::BIGINT, 0) AS daily_order_count,
        COALESCE(valid_order_count::BIGINT, 0) AS daily_valid_order_count,
        COALESCE(paid_order_count::BIGINT, 0) AS daily_paid_order_count,
        COALESCE(unique_customer_count::BIGINT, 0) AS daily_unique_customer_count,

        COALESCE(total_payment_amount::NUMERIC, 0.0) AS daily_gmv,
        COALESCE(total_product_amount::NUMERIC, 0.0) AS daily_product_amount,
        COALESCE(total_freight_amount::NUMERIC, 0.0) AS daily_freight_amount,
        COALESCE(aov::NUMERIC, 0.0) AS daily_aov,

        COALESCE(delivery_rate::NUMERIC, 0.0) AS daily_delivery_rate,
        COALESCE(late_delivery_rate::NUMERIC, 0.0) AS daily_late_delivery_rate,
        COALESCE(review_rate::NUMERIC, 0.0) AS daily_review_rate,
        COALESCE(review_comment_rate::NUMERIC, 0.0) AS daily_review_comment_rate,
        COALESCE(average_review_score::NUMERIC, 0.0) AS daily_average_review_score
    FROM {{ ref('dws_daily_order_summary') }}
    WHERE purchase_date IS NOT NULL
),

-- Step 2: Calculate derived rates
-- 第二步：计算派生比率
with_rates AS (
    SELECT
        *,

        -- valid_order_rate: valid orders / total orders / 有效订单率
        ROUND(
            CASE WHEN daily_order_count = 0 THEN 0.0
                 ELSE daily_valid_order_count::NUMERIC / daily_order_count
            END, 4
        ) AS valid_order_rate,

        -- paid_order_rate: paid orders / total orders / 已支付订单率
        ROUND(
            CASE WHEN daily_order_count = 0 THEN 0.0
                 ELSE daily_paid_order_count::NUMERIC / daily_order_count
            END, 4
        ) AS paid_order_rate
    FROM prepared
),

-- Step 3 & 4: Window functions for moving averages and cumulative metrics
-- 第三步和第四步：窗口函数计算移动平均和累计指标
with_window_metrics AS (
    SELECT
        *,

        -- 7-day moving averages / 7日移动平均
        ROUND(
            AVG(daily_gmv) OVER (
                ORDER BY stat_date
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ), 4
        ) AS gmv_7d_moving_avg,

        ROUND(
            AVG(daily_order_count) OVER (
                ORDER BY stat_date
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ), 4
        ) AS order_count_7d_moving_avg,

        ROUND(
            AVG(daily_aov) OVER (
                ORDER BY stat_date
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ), 4
        ) AS aov_7d_moving_avg,

        -- Cumulative metrics / 累计指标
        ROUND(
            SUM(daily_gmv) OVER (
                ORDER BY stat_date
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ), 4
        ) AS cumulative_gmv,

        ROUND(
            SUM(daily_order_count) OVER (
                ORDER BY stat_date
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ), 4
        ) AS cumulative_order_count,

        ROUND(
            SUM(daily_unique_customer_count) OVER (
                ORDER BY stat_date
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ), 4
        ) AS cumulative_customer_count,

        -- Day-over-day absolute changes using LAG / 使用 LAG 计算日环比绝对变化
        ROUND(
            daily_gmv - LAG(daily_gmv) OVER (ORDER BY stat_date), 4
        ) AS gmv_day_over_day_change,

        ROUND(
            daily_order_count - LAG(daily_order_count) OVER (ORDER BY stat_date), 4
        ) AS order_count_day_over_day_change
    FROM with_rates
),

-- Step 5: Calculate day-over-day rates (percentage change)
-- 第五步：计算日环比变化率（百分比变化）
with_rates_final AS (
    SELECT
        *,

        -- GMV day-over-day rate / GMV 日环比增长率
        ROUND(
            CASE
                WHEN LAG(daily_gmv) OVER (ORDER BY stat_date) IS NULL THEN 0.0
                WHEN LAG(daily_gmv) OVER (ORDER BY stat_date) = 0 THEN 0.0
                ELSE (daily_gmv - LAG(daily_gmv) OVER (ORDER BY stat_date))
                     / LAG(daily_gmv) OVER (ORDER BY stat_date)
            END, 4
        ) AS gmv_day_over_day_rate,

        -- Order count day-over-day rate / 订单量日环比增长率
        ROUND(
            CASE
                WHEN LAG(daily_order_count) OVER (ORDER BY stat_date) IS NULL THEN 0.0
                WHEN LAG(daily_order_count) OVER (ORDER BY stat_date) = 0 THEN 0.0
                ELSE (daily_order_count - LAG(daily_order_count) OVER (ORDER BY stat_date))
                     / LAG(daily_order_count) OVER (ORDER BY stat_date)
            END, 4
        ) AS order_count_day_over_day_rate
    FROM with_window_metrics
)

-- Step 6: Final output with COALESCE for NULL day-over-day fields
-- 第六步：最终输出，对日环比字段使用 COALESCE 处理 NULL
SELECT
    stat_date,
    stat_month,
    daily_order_count,
    daily_valid_order_count,
    daily_paid_order_count,
    daily_unique_customer_count,
    daily_gmv,
    daily_product_amount,
    daily_freight_amount,
    daily_aov,
    daily_delivery_rate,
    daily_late_delivery_rate,
    daily_review_rate,
    daily_review_comment_rate,
    daily_average_review_score,
    valid_order_rate,
    paid_order_rate,
    gmv_7d_moving_avg,
    order_count_7d_moving_avg,
    aov_7d_moving_avg,
    cumulative_gmv,
    cumulative_order_count,
    cumulative_customer_count,

    -- Fill NULL day-over-day changes with 0 / 将 NULL 日环比变化填充为 0
    COALESCE(gmv_day_over_day_change, 0.0) AS gmv_day_over_day_change,
    COALESCE(order_count_day_over_day_change, 0.0) AS order_count_day_over_day_change,
    COALESCE(gmv_day_over_day_rate, 0.0) AS gmv_day_over_day_rate,
    COALESCE(order_count_day_over_day_rate, 0.0) AS order_count_day_over_day_rate,

    -- Technical fields / 技术字段
    TO_CHAR(CURRENT_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS') AS ads_loaded_at,
    CURRENT_DATE AS dt

FROM with_rates_final
ORDER BY stat_date