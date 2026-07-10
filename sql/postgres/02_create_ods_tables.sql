-- ODS Tables Creation for E-commerce Warehouse
-- 电商数仓 ODS 表创建

-- =====================================================
-- ODS Customers Table / ODS 客户表
-- =====================================================
CREATE TABLE IF NOT EXISTS ods.customers (
    customer_id VARCHAR(64) PRIMARY KEY,
    customer_unique_id VARCHAR(64) NOT NULL,
    customer_zip_code_prefix INTEGER,
    customer_city VARCHAR(100),
    customer_state VARCHAR(2),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dt DATE DEFAULT CURRENT_DATE
);

COMMENT ON TABLE ods.customers IS 'Customer profile data from Olist / Olist 客户信息数据';
COMMENT ON COLUMN ods.customers.loaded_at IS 'Technical field: timestamp when record was loaded / 技术字段：记录加载时间';
COMMENT ON COLUMN ods.customers.dt IS 'Technical field: date when record was loaded / 技术字段：记录加载日期';

-- =====================================================
-- ODS Orders Table / ODS 订单表
-- =====================================================
CREATE TABLE IF NOT EXISTS ods.orders (
    order_id VARCHAR(64) PRIMARY KEY,
    customer_id VARCHAR(64) NOT NULL,
    order_status VARCHAR(50),
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dt DATE DEFAULT CURRENT_DATE
);

COMMENT ON TABLE ods.orders IS 'Order lifecycle data from Olist / Olist 订单生命周期数据';
COMMENT ON COLUMN ods.orders.order_status IS 'Order status: pending, processing, shipped, delivered, canceled, unavailable / 订单状态';

-- =====================================================
-- ODS Order Items Table / ODS 订单商品表
-- =====================================================
CREATE TABLE IF NOT EXISTS ods.order_items (
    order_id VARCHAR(64) NOT NULL,
    order_item_id INTEGER NOT NULL,
    product_id VARCHAR(64),
    seller_id VARCHAR(64),
    shipping_limit_date TIMESTAMP,
    price NUMERIC(10, 2),
    freight_value NUMERIC(10, 2),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dt DATE DEFAULT CURRENT_DATE,
    PRIMARY KEY (order_id, order_item_id)
);

COMMENT ON TABLE ods.order_items IS 'Order item details from Olist / Olist 订单商品明细';
COMMENT ON COLUMN ods.order_items.price IS 'Product price in Brazilian Real / 商品价格（巴西雷亚尔）';
COMMENT ON COLUMN ods.order_items.freight_value IS 'Freight/shipping value in Brazilian Real / 运费（巴西雷亚尔）';

-- =====================================================
-- ODS Order Payments Table / ODS 订单支付表
-- =====================================================
CREATE TABLE IF NOT EXISTS ods.order_payments (
    order_id VARCHAR(64) NOT NULL,
    payment_sequential INTEGER NOT NULL,
    payment_type VARCHAR(50),
    payment_installments INTEGER,
    payment_value NUMERIC(10, 2),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dt DATE DEFAULT CURRENT_DATE,
    PRIMARY KEY (order_id, payment_sequential)
);

COMMENT ON TABLE ods.order_payments IS 'Order payment details from Olist / Olist 订单支付明细';
COMMENT ON COLUMN ods.order_payments.payment_type IS 'Payment method: credit_card, debit_card, boleto, voucher / 支付方式';
COMMENT ON COLUMN ods.order_payments.payment_installments IS 'Number of installment payments / 分期付款次数';

-- =====================================================
-- ODS Order Reviews Table / ODS 订单评价表
-- =====================================================
CREATE TABLE IF NOT EXISTS ods.order_reviews (
    ods_row_id BIGSERIAL PRIMARY KEY,
    review_id VARCHAR(64) NOT NULL,
    order_id VARCHAR(64) NOT NULL,
    review_score INTEGER,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date TIMESTAMP,
    review_answer_timestamp TIMESTAMP,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dt DATE DEFAULT CURRENT_DATE
);

COMMENT ON TABLE ods.order_reviews IS 'Order review data from Olist / Olist 订单评价数据';
COMMENT ON COLUMN ods.order_reviews.ods_row_id IS 'Technical primary key for ODS layer / ODS 层技术主键';
COMMENT ON COLUMN ods.order_reviews.review_id IS 'Source review ID (may have duplicates in raw data) / 来源评价 ID（原始数据中可能重复）';
COMMENT ON COLUMN ods.order_reviews.review_score IS 'Customer review score (1-5) / 客户评价分数（1-5）';

-- Index source business ID for join performance while preserving all raw rows
-- 为源业务 ID 创建索引以提升关联性能，同时保留所有原始行
CREATE INDEX IF NOT EXISTS idx_order_reviews_review_id ON ods.order_reviews (review_id);
CREATE INDEX IF NOT EXISTS idx_order_reviews_order_id ON ods.order_reviews (order_id);

-- =====================================================
-- ODS Products Table / ODS 商品表
-- =====================================================
CREATE TABLE IF NOT EXISTS ods.products (
    product_id VARCHAR(64) PRIMARY KEY,
    product_category_name VARCHAR(100),
    product_name_lenght INTEGER,
    product_description_lenght INTEGER,
    product_photos_qty INTEGER,
    product_weight_g INTEGER,
    product_length_cm INTEGER,
    product_height_cm INTEGER,
    product_width_cm INTEGER,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dt DATE DEFAULT CURRENT_DATE
);

COMMENT ON TABLE ods.products IS 'Product information from Olist / Olist 商品信息';

-- =====================================================
-- ODS Sellers Table / ODS 卖家表
-- =====================================================
CREATE TABLE IF NOT EXISTS ods.sellers (
    seller_id VARCHAR(64) PRIMARY KEY,
    seller_zip_code_prefix INTEGER,
    seller_city VARCHAR(100),
    seller_state VARCHAR(2),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dt DATE DEFAULT CURRENT_DATE
);

COMMENT ON TABLE ods.sellers IS 'Seller information from Olist / Olist 卖家信息';

-- =====================================================
-- ODS Geolocation Table / ODS 地理位置表
-- =====================================================
CREATE TABLE IF NOT EXISTS ods.geolocation (
    geolocation_zip_code_prefix INTEGER NOT NULL,
    geolocation_lat NUMERIC(11, 8),
    geolocation_lng NUMERIC(11, 8),
    geolocation_city VARCHAR(100),
    geolocation_state VARCHAR(2),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dt DATE DEFAULT CURRENT_DATE
);

COMMENT ON TABLE ods.geolocation IS 'Geolocation data for zip codes / 邮编地理位置数据';
CREATE INDEX IF NOT EXISTS idx_geolocation_zip_prefix ON ods.geolocation (geolocation_zip_code_prefix);

-- =====================================================
-- ODS Product Category Translation Table / ODS 商品类目翻译表
-- =====================================================
CREATE TABLE IF NOT EXISTS ods.product_category_translation (
    product_category_name VARCHAR(100) PRIMARY KEY,
    product_category_name_english VARCHAR(100),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dt DATE DEFAULT CURRENT_DATE
);

COMMENT ON TABLE ods.product_category_translation IS 'Product category name translation from Portuguese to English / 商品类目名称葡萄牙语到英语翻译';

-- =====================================================
-- Create Indexes for Better Query Performance
-- 创建索引提升查询性能
-- =====================================================

-- Orders indexes
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON ods.orders (customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON ods.orders (order_status);
CREATE INDEX IF NOT EXISTS idx_orders_purchase_timestamp ON ods.orders (order_purchase_timestamp);

-- Order items indexes
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON ods.order_items (order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON ods.order_items (product_id);
CREATE INDEX IF NOT EXISTS idx_order_items_seller_id ON ods.order_items (seller_id);

-- Order payments indexes
CREATE INDEX IF NOT EXISTS idx_order_payments_order_id ON ods.order_payments (order_id);
CREATE INDEX IF NOT EXISTS idx_order_payments_type ON ods.order_payments (payment_type);

-- Order reviews indexes
CREATE INDEX IF NOT EXISTS idx_order_reviews_order_id ON ods.order_reviews (order_id);
CREATE INDEX IF NOT EXISTS idx_order_reviews_score ON ods.order_reviews (review_score);

-- Products indexes
CREATE INDEX IF NOT EXISTS idx_products_category ON ods.products (product_category_name);

-- Sellers indexes
CREATE INDEX IF NOT EXISTS idx_sellers_state ON ods.sellers (seller_state);