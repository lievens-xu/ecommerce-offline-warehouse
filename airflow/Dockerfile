# Airflow Custom Image for E-Commerce Warehouse Pipeline
# Airflow 电商数仓主流程自定义镜像
#
# Builds on the official Apache Airflow image and adds
# dbt-postgres and Python data packages.
# 基于官方 Apache Airflow 镜像，添加 dbt-postgres 和 Python 数据包。

ARG AIRFLOW_VERSION=2.10.5
FROM apache/airflow:${AIRFLOW_VERSION}

USER root

# Install system dependencies for psycopg2 and git (required by dbt debug)
# 安装 psycopg2 和 git 系统依赖（dbt debug 需要 git）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER airflow

# Install Python packages from requirements.txt
# 从 requirements.txt 安装 Python 包
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Create project mount point / 创建项目挂载点
RUN mkdir -p /opt/airflow/project /opt/airflow/config