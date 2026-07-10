"""
Tests for the customer RFM segmentation logic.
客户 RFM 分层逻辑测试。
"""

import pandas as pd

import build_ads_customer_rfm as rfm


def test_score_quintiles_recency_is_reversed():
    """Smaller recency should score higher. 更小的 recency 应得更高分。"""
    s = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    scores = rfm.score_quintiles(s, ascending=False)
    # 最小值应拿到最高分(5)，最大值最低分(1)
    assert scores.iloc[0] == 5
    assert scores.iloc[-1] == 1


def test_score_quintiles_monetary_is_ascending():
    """Larger monetary should score higher. 更大的金额应得更高分。"""
    s = pd.Series([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    scores = rfm.score_quintiles(s, ascending=True)
    assert scores.iloc[0] == 1
    assert scores.iloc[-1] == 5


def test_score_quintiles_handles_heavy_ties():
    """Many tied values must not crash qcut. 大量并列值不应导致 qcut 报错。"""
    s = pd.Series([1] * 90 + [2] * 10)
    scores = rfm.score_quintiles(s, ascending=True)
    assert set(scores.unique()).issubset({1, 2, 3, 4, 5})
    assert len(scores) == 100


def test_assign_segment_champions_and_lost():
    assert "Champions" in rfm.assign_segment(5, 5)
    assert "Lost" in rfm.assign_segment(1, 1)


def test_prepare_orders_excludes_invalid_status(synthetic_dwd):
    orders = rfm.prepare_orders(synthetic_dwd)
    # o5 是 canceled，应被排除
    assert "o5" not in set(orders["order_id"])
    assert "o1" in set(orders["order_id"])


def test_build_rfm_base_aggregates_per_customer(synthetic_dwd):
    orders = rfm.prepare_orders(synthetic_dwd)
    rfm_base, snapshot = rfm.build_rfm_base(orders)

    row_a = rfm_base[rfm_base["customer_unique_id"] == "cA"].iloc[0]
    # 客户 cA 有两笔有效订单，金额 100+200
    assert row_a["frequency"] == 2
    assert round(row_a["monetary"], 2) == 300.0
    # recency 非负
    assert (rfm_base["recency"] >= 0).all()


def test_segment_summary_shares_sum_to_100(synthetic_dwd):
    orders = rfm.prepare_orders(synthetic_dwd)
    rfm_base, _ = rfm.build_rfm_base(orders)
    customers = rfm.build_customer_rfm(rfm_base)
    summary = rfm.build_segment_summary(customers)

    assert round(summary["customer_pct"].sum(), 1) == 100.0
    assert round(summary["monetary_pct"].sum(), 1) == 100.0
