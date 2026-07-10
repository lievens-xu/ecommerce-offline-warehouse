#!/bin/bash
# Superset Initialization Script
# Superset 初始化脚本
#
# This script runs at container start to initialize the metadata database,
# create the admin user, and start the Superset web server.
# 此脚本在容器启动时运行，用于初始化元数据库、创建管理员用户并启动 Superset Web 服务器。

set -e

# Step 1: Initialize the metadata database / 初始化元数据库
echo "[INFO] Initializing Superset metadata database ..."
superset db upgrade

echo "[INFO] Initializing Superset ..."
superset init

# Step 2: Create admin user if not already exists
# 第二步：创建管理员用户（如果尚不存在）
superset fab create-admin \
    --username "${SUPERSET_ADMIN_USERNAME:-admin}" \
    --password "${SUPERSET_ADMIN_PASSWORD:-admin}" \
    --firstname Admin \
    --lastname User \
    --email "${SUPERSET_ADMIN_EMAIL:-admin@superset.com}" \
    2>/dev/null || echo "[INFO] Admin user already exists, skipping creation."

# Step 3: Start Superset web server / 第三步：启动 Superset Web 服务器
echo "[INFO] Starting Superset web server on port 8088 ..."
superset run -p 8088 --with-threads --reload -h 0.0.0.0