# Superset Dockerfile for E-Commerce Warehouse Dashboard
# Superset 电商数仓看板 Dockerfile
#
# Builds on the official Apache Superset image and adds
# psycopg2 for PostgreSQL connectivity.
# 基于官方 Apache Superset 镜像，添加 psycopg2 用于 PostgreSQL 连接。

FROM apache/superset:4.1.1

USER root

# Install PostgreSQL client library for psycopg2
# 安装 psycopg2 所需的 PostgreSQL 客户端库
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq-dev \
        gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create writable directory for Superset metadata database
# 为 Superset 元数据库创建可写目录
RUN mkdir -p /app/superset_home && chown superset:superset /app/superset_home

# Copy and set executable permissions as root before switching user
# 以 root 身份复制并设置可执行权限后再切换用户
COPY init.sh /app/init.sh
RUN chmod +x /app/init.sh

USER superset

# Install Python packages from requirements.txt
# 从 requirements.txt 安装 Python 包
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy Superset configuration file / 复制 Superset 配置文件
COPY superset_config.py /app/superset_config.py
ENV SUPERSET_CONFIG_PATH=/app/superset_config.py

EXPOSE 8088

ENTRYPOINT ["/app/init.sh"]