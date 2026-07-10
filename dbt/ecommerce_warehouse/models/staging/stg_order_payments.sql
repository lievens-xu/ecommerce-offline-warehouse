{{ config(materialized='view') }}

-- Staging model for ODS order payments / ODS 订单支付表 Staging 模型
-- Casts payment_value and payment_installments to numeric types.
-- 将 payment_value 和 payment_installments 转换为数值类型。

SELECT
    order_id,
    payment_sequential,
    payment_type,
    COALESCE(payment_installments::INT, 0) AS payment_installments,
    COALESCE(payment_value::NUMERIC(10,2), 0.0) AS payment_value,
    loaded_at,
    dt
FROM {{ source('ods', 'order_payments') }}