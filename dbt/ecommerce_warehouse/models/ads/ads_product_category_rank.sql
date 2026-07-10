{{ config(materialized='table', schema='ads') }}

-- ADS Product Category Ranking / ADS 商品类目排名表
--
-- Category revenue ranking with Pareto (cumulative) share, built from staging
-- models. Mirrors scripts/build_ads_product_category_rank.py.
-- 基于 staging 模型的类目收入排名与帕累托累计占比，与 scripts/build_ads_product_category_rank.py 一致。
--
-- Transformation steps / 转换步骤:
-- 1. Keep items belonging to valid orders
-- 2. Resolve English category name (fallback to Portuguese, then 'unknown')
-- 3. Aggregate to category level
-- 4. Rank + revenue share + cumulative (Pareto) share
-- 5. Add technical fields

WITH

-- Step 1: items of valid orders / 第一步：有效订单的商品明细
valid_items AS (
    SELECT
        i.order_id,
        i.order_item_id,
        i.product_id,
        i.price,
        i.freight_value
    FROM {{ ref('stg_order_items') }} i
    INNER JOIN {{ ref('stg_orders') }} o
        ON i.order_id = o.order_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
),

-- Step 2: attach resolved category / 第二步：解析类目名
items_with_category AS (
    SELECT
        vi.*,
        COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS category
    FROM valid_items vi
    LEFT JOIN {{ ref('stg_products') }} p
        ON vi.product_id = p.product_id
    LEFT JOIN {{ ref('stg_product_category_translation') }} t
        ON p.product_category_name = t.product_category_name
),

-- Step 3: aggregate to category / 第三步：聚合到类目
category_agg AS (
    SELECT
        category,
        ROUND(SUM(price), 2) AS product_revenue,
        ROUND(SUM(freight_value), 2) AS freight_revenue,
        COUNT(order_item_id) AS item_count,
        COUNT(DISTINCT order_id) AS order_count,
        COUNT(DISTINCT product_id) AS product_count
    FROM items_with_category
    GROUP BY category
),

-- Step 4: rank + Pareto share / 第四步：排名 + 帕累托占比
ranked AS (
    SELECT
        *,
        ROUND(product_revenue / item_count, 2) AS avg_item_price,
        ROW_NUMBER() OVER (ORDER BY product_revenue DESC) AS revenue_rank,
        ROUND(
            product_revenue / SUM(product_revenue) OVER () * 100, 2
        ) AS revenue_share_pct,
        ROUND(
            SUM(product_revenue) OVER (
                ORDER BY product_revenue DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) / SUM(product_revenue) OVER () * 100, 2
        ) AS cumulative_revenue_share_pct
    FROM category_agg
)

-- Step 5: final output / 第五步：最终输出
SELECT
    revenue_rank,
    category,
    product_revenue,
    revenue_share_pct,
    cumulative_revenue_share_pct,
    freight_revenue,
    item_count,
    order_count,
    product_count,
    avg_item_price,
    TO_CHAR(CURRENT_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS') AS ads_loaded_at,
    CURRENT_DATE AS dt
FROM ranked
ORDER BY revenue_rank
