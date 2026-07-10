{{ config(materialized='table', schema='dwd') }}

-- DWD Order Detail / DWD 订单明细表
--
-- Order-level grain detail table built from ODS staging models.
-- 基于 ODS staging 模型构建的订单粒度明细表。
--
-- Transformation steps / 转换步骤:
-- 1. Aggregate order items to order level (item_agg)
-- 2. Aggregate payments to order level with main payment type (payment_agg)
-- 3. Aggregate reviews to order level (review_agg)
-- 4. LEFT JOIN orders + customers + item_agg + payment_agg + review_agg
-- 5. Calculate date, delivery, and logistics fields
-- 6. Add technical fields

WITH

-- Step 1: Aggregate order items to order level
-- 第一步：将订单商品聚合到订单级别
item_agg AS (
    SELECT
        order_id,
        COUNT(order_item_id) AS order_item_count,
        COUNT(DISTINCT product_id) AS product_count,
        COUNT(DISTINCT seller_id) AS seller_count,
        ROUND(SUM(COALESCE(price, 0.0))::NUMERIC, 4) AS total_product_amount,
        ROUND(SUM(COALESCE(freight_value, 0.0))::NUMERIC, 4) AS total_freight_amount
    FROM {{ ref('stg_order_items') }}
    GROUP BY order_id
),

-- Step 2a: Aggregate payment amounts by order and payment type
-- 第二步a：按订单和支付类型聚合支付金额
payment_type_amount AS (
    SELECT
        order_id,
        payment_type,
        ROUND(SUM(COALESCE(payment_value, 0.0))::NUMERIC, 4) AS payment_type_amount
    FROM {{ ref('stg_order_payments') }}
    GROUP BY order_id, payment_type
),

-- Step 2b: Identify main payment type (one with largest amount)
-- 第二步b：识别主要支付方式（金额最大的）
main_payment_type AS (
    SELECT
        order_id,
        payment_type AS main_payment_type
    FROM (
        SELECT
            order_id,
            payment_type,
            payment_type_amount,
            ROW_NUMBER() OVER (
                PARTITION BY order_id
                ORDER BY payment_type_amount DESC
            ) AS rn
        FROM payment_type_amount
    ) t
    WHERE rn = 1
),

-- Step 2c: Aggregate payment metrics to order level
-- 第二步c：将支付指标聚合到订单级别
payment_agg AS (
    SELECT
        order_id,
        ROUND(SUM(COALESCE(payment_value, 0.0))::NUMERIC, 4) AS total_payment_amount,
        COUNT(DISTINCT payment_type) AS payment_type_count,
        MAX(COALESCE(payment_installments, 0)) AS max_payment_installments
    FROM {{ ref('stg_order_payments') }}
    GROUP BY order_id
),

-- Step 3: Aggregate reviews to order level
-- 第三步：将评价聚合到订单级别
review_agg AS (
    SELECT
        order_id,
        ROUND(AVG(review_score::NUMERIC), 2) AS average_review_score,
        COUNT(review_id) AS review_count,
        MAX(
            CASE
                WHEN COALESCE(TRIM(review_comment_title), '') != ''
                     OR COALESCE(TRIM(review_comment_message), '') != ''
                THEN 1
                ELSE 0
            END
        ) AS has_review_comment
    FROM {{ ref('stg_order_reviews') }}
    GROUP BY order_id
),

-- Step 4: Join all tables
-- 第四步：关联所有表
combined AS (
    SELECT
        o.order_id,
        o.customer_id,
        c.customer_unique_id,
        c.customer_city,
        c.customer_state,
        o.order_status,
        o.order_purchase_timestamp,
        o.order_approved_at,
        o.order_delivered_carrier_date,
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date,

        COALESCE(i.order_item_count, 0) AS order_item_count,
        COALESCE(i.product_count, 0) AS product_count,
        COALESCE(i.seller_count, 0) AS seller_count,
        COALESCE(i.total_product_amount, 0.0) AS total_product_amount,
        COALESCE(i.total_freight_amount, 0.0) AS total_freight_amount,

        COALESCE(p.total_payment_amount, 0.0) AS total_payment_amount,
        COALESCE(p.payment_type_count, 0) AS payment_type_count,
        COALESCE(m.main_payment_type, 'unknown') AS main_payment_type,
        COALESCE(p.max_payment_installments, 0) AS max_payment_installments,

        COALESCE(r.average_review_score, 0.0) AS average_review_score,
        COALESCE(r.review_count, 0) AS review_count,
        COALESCE(r.has_review_comment, 0) AS has_review_comment
    FROM {{ ref('stg_orders') }} o
    LEFT JOIN {{ ref('stg_customers') }} c ON o.customer_id = c.customer_id
    LEFT JOIN item_agg i ON o.order_id = i.order_id
    LEFT JOIN payment_agg p ON o.order_id = p.order_id
    LEFT JOIN main_payment_type m ON o.order_id = m.order_id
    LEFT JOIN review_agg r ON o.order_id = r.order_id
)

-- Step 5 & 6: Calculate derived fields and add technical fields
-- 第五步和第六步：计算派生字段并添加技术字段
SELECT
    order_id,
    customer_id,
    customer_unique_id,
    customer_city,
    customer_state,
    order_status,
    order_purchase_timestamp,
    TO_CHAR(order_purchase_timestamp::DATE, 'YYYY-MM-DD') AS purchase_date,
    TO_CHAR(order_purchase_timestamp::DATE, 'YYYY-MM') AS purchase_month,
    order_approved_at,
    order_delivered_carrier_date,
    order_delivered_customer_date,
    order_estimated_delivery_date,

    order_item_count,
    product_count,
    seller_count,
    total_product_amount,
    total_freight_amount,
    total_payment_amount,
    payment_type_count,
    main_payment_type,
    max_payment_installments,
    average_review_score,
    review_count,
    has_review_comment,

    -- Delivery duration in days / 配送天数
    CASE
        WHEN order_delivered_customer_date IS NOT NULL
             AND order_purchase_timestamp IS NOT NULL
        THEN (order_delivered_customer_date::DATE - order_purchase_timestamp::DATE)
        ELSE NULL
    END AS delivery_days,

    -- Estimated delivery duration in days / 预计配送天数
    CASE
        WHEN order_estimated_delivery_date IS NOT NULL
             AND order_purchase_timestamp IS NOT NULL
        THEN (order_estimated_delivery_date::DATE - order_purchase_timestamp::DATE)
        ELSE NULL
    END AS estimated_delivery_days,

    -- Delivery delay in days (positive = late) / 配送延迟天数（正数 = 延迟）
    CASE
        WHEN order_delivered_customer_date IS NOT NULL
             AND order_estimated_delivery_date IS NOT NULL
        THEN (order_delivered_customer_date::DATE - order_estimated_delivery_date::DATE)
        ELSE NULL
    END AS delivery_delay_days,

    -- Whether the order was delivered / 是否已配送
    CASE
        WHEN order_delivered_customer_date IS NOT NULL THEN 1
        ELSE 0
    END AS is_delivered,

    -- Whether the delivery was late / 是否延迟配送
    CASE
        WHEN order_delivered_customer_date IS NOT NULL
             AND order_estimated_delivery_date IS NOT NULL
             AND (order_delivered_customer_date::DATE - order_estimated_delivery_date::DATE) > 0
        THEN 1
        ELSE 0
    END AS is_late_delivery,

    -- Technical fields / 技术字段
    TO_CHAR(CURRENT_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS') AS dwd_loaded_at,
    CURRENT_DATE AS dt

FROM combined
ORDER BY order_id