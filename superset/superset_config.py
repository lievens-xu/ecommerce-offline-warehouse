"""
Superset Configuration for E-Commerce Warehouse Dashboard
Superset 电商数仓看板配置

This config is loaded by Superset at startup via SUPERSET_CONFIG_PATH.
此配置在 Superset 启动时通过 SUPERSET_CONFIG_PATH 加载。
"""

import os


# Metadata database (SQLite, stored in a Docker volume mount)
# 元数据库（SQLite，存储在 Docker 挂载卷中）
SQLALCHEMY_DATABASE_URI = os.getenv(
    "SUPERSET__SQLALCHEMY_DATABASE_URI",
    "sqlite:////app/superset_home/superset.db",
)

# Secret key for Flask sessions / Flask 会话密钥
SECRET_KEY = os.getenv(
    "SUPERSET_SECRET_KEY",
    "CHANGE_ME_TO_A_RANDOM_SECRET_KEY",
)

# Enable time picker in Explore / 在 Explore 中启用时间选择器
ENABLE_TIME_PICKER = True

# Default timezone / 默认时区
DEFAULT_TIMEZONE = "Asia/Shanghai"

# Feature flags / 功能开关
FEATURE_FLAGS = {
    "THUMBNAILS": False,
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_CROSS_FILTERS": True,
    "ALERTS_ATTACH_REPORTS": False,
}

# SQL Lab / SQL 实验功能
ENABLE_TEMPLATE_PROCESSING = True
SQL_MAX_ROW = 100000

# Explore UI / Explore 界面
ROW_LIMIT = 5000
SAMPLES_ROW_LIMIT = 1000

# Cache / 缓存
CACHE_CONFIG = {"CACHE_TYPE": "NullCache"}

# Logging / 日志
LOG_LEVEL = "WARNING"