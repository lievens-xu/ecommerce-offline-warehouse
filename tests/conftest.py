"""
Shared pytest fixtures and path setup.
共享的 pytest 夹具与路径设置。

Adds the scripts/ directory to sys.path so tests can import the ETL modules,
and builds small synthetic DataFrames so the suite runs without the full
Olist dataset (important for CI).

将 scripts/ 目录加入 sys.path 以便测试导入 ETL 模块，并构造小型合成数据，
使测试无需完整 Olist 数据集即可运行（对 CI 很重要）。
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT_DIR / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture
def synthetic_dwd() -> pd.DataFrame:
    """
    A tiny DWD-like order table covering multiple customers, states and dates.
    一个覆盖多客户、多州、多日期的迷你 DWD 订单表。
    """
    rows = [
        # order_id, customer_unique_id, state, status, ts, payment, delivered, late, del_days, review
        ("o1", "cA", "SP", "delivered", "2018-01-01 10:00:00", 100.0, 1, 0, 5, 5),
        ("o2", "cA", "SP", "delivered", "2018-06-01 10:00:00", 200.0, 1, 1, 20, 3),
        ("o3", "cB", "RJ", "delivered", "2018-08-15 10:00:00", 50.0, 1, 0, 8, 4),
        ("o4", "cC", "MG", "delivered", "2017-02-01 10:00:00", 300.0, 1, 0, 10, 5),
        ("o5", "cD", "SP", "canceled", "2018-09-01 10:00:00", 999.0, 0, 0, None, None),
        ("o6", "cE", "RJ", "shipped", "2018-09-10 10:00:00", 80.0, 0, 0, None, 4),
    ]
    df = pd.DataFrame(
        rows,
        columns=[
            "order_id",
            "customer_unique_id",
            "customer_state",
            "order_status",
            "order_purchase_timestamp",
            "total_payment_amount",
            "is_delivered",
            "is_late_delivery",
            "delivery_days",
            "average_review_score",
        ],
    )
    return df


@pytest.fixture
def synthetic_category_items() -> pd.DataFrame:
    """
    A tiny joined items+category table for category-ranking tests.
    用于类目排名测试的迷你 商品明细+类目 关联表。
    """
    rows = [
        ("o1", 1, "p1", "electronics", 500.0, 20.0),
        ("o1", 2, "p2", "electronics", 300.0, 10.0),
        ("o2", 1, "p3", "furniture", 200.0, 30.0),
        ("o3", 1, "p4", "books", 40.0, 5.0),
        ("o4", 1, "p5", "books", 60.0, 5.0),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "order_id",
            "order_item_id",
            "product_id",
            "category",
            "price",
            "freight_value",
        ],
    )
