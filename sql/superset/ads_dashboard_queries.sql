-- Reference SQL Queries for Superset Dashboard Charts
-- Superset 看板图表参考 SQL 查询
--
-- Source table / 源表: ads.ads_daily_business_overview
-- These queries can be used in Superset SQL Lab or as custom SQL in charts.
-- 这些查询可在 Superset SQL Lab 中使用，或作为图表的自定义 SQL。

-- =====================================================
-- 1. Daily GMV Trend / 每日 GMV 趋势
-- =====================================================
SELECT
    stat_date,
    daily_gmv
FROM ads.ads_daily_business_overview
ORDER BY stat_date;

-- =====================================================
-- 2. Daily Order Count Trend / 每日订单量趋势
-- =====================================================
SELECT
    stat_date,
    daily_order_count
FROM ads.ads_daily_business_overview
ORDER BY stat_date;

-- =====================================================
-- 3. AOV Trend / 平均订单价值趋势
-- =====================================================
SELECT
    stat_date,
    daily_aov
FROM ads.ads_daily_business_overview
ORDER BY stat_date;

-- =====================================================
-- 4. GMV 7-Day Moving Average / GMV 7日移动平均
-- =====================================================
SELECT
    stat_date,
    daily_gmv,
    gmv_7d_moving_avg
FROM ads.ads_daily_business_overview
ORDER BY stat_date;

-- =====================================================
-- 5. Cumulative GMV / 累计 GMV
-- =====================================================
SELECT
    stat_date,
    cumulative_gmv
FROM ads.ads_daily_business_overview
ORDER BY stat_date;

-- =====================================================
-- 6. Delivery Rate Trend / 配送率趋势
-- =====================================================
SELECT
    stat_date,
    daily_delivery_rate
FROM ads.ads_daily_business_overview
ORDER BY stat_date;

-- =====================================================
-- 7. KPI: Total GMV / 总 GMV
-- =====================================================
SELECT
    ROUND(SUM(daily_gmv), 2) AS total_gmv
FROM ads.ads_daily_business_overview;

-- =====================================================
-- 8. KPI: Total Orders / 总订单数
-- =====================================================
SELECT
    SUM(daily_order_count) AS total_orders
FROM ads.ads_daily_business_overview;

-- =====================================================
-- 9. KPI: Latest Day Metrics / 最新日指标
-- =====================================================
SELECT
    stat_date,
    daily_gmv AS latest_daily_gmv,
    daily_order_count AS latest_daily_order_count,
    daily_aov AS latest_daily_aov,
    daily_delivery_rate AS latest_daily_delivery_rate
FROM ads.ads_daily_business_overview
ORDER BY stat_date DESC
LIMIT 1;

-- =====================================================
-- 10. Monthly Summary / 月度汇总
-- =====================================================
SELECT
    stat_month,
    ROUND(SUM(daily_gmv), 2) AS monthly_gmv,
    SUM(daily_order_count) AS monthly_orders,
    ROUND(SUM(daily_gmv) / NULLIF(SUM(daily_order_count), 0), 4) AS monthly_aov
FROM ads.ads_daily_business_overview
GROUP BY stat_month
ORDER BY stat_month;