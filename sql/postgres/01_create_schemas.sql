-- Create schemas for the data warehouse
-- 为数据仓库创建 schema

-- Create ODS schema (Operational Data Store)
-- 创建 ODS schema（原始数据层）
CREATE SCHEMA IF NOT EXISTS ods;

-- Create DWD schema (Data Warehouse Detail)
-- 创建 DWD schema（明细数据层）
CREATE SCHEMA IF NOT EXISTS dwd;

-- Create DWS schema (Data Warehouse Summary)
-- 创建 DWS schema（汇总数据层）
CREATE SCHEMA IF NOT EXISTS dws;

-- Create ADS schema (Application Data Store)
-- 创建 ADS schema（应用数据层）
CREATE SCHEMA IF NOT EXISTS ads;

-- Grant permissions to warehouse_user
-- 为 warehouse_user 授权
GRANT ALL PRIVILEGES ON SCHEMA ods TO warehouse_user;
GRANT ALL PRIVILEGES ON SCHEMA dwd TO warehouse_user;
GRANT ALL PRIVILEGES ON SCHEMA dws TO warehouse_user;
GRANT ALL PRIVILEGES ON SCHEMA ads TO warehouse_user;

-- Set default search path
-- 设置默认搜索路径
ALTER USER warehouse_user SET search_path TO ods, dwd, dws, ads, public;