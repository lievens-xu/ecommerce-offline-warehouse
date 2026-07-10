"""
Tests for the geographic (state-level) summary logic.
地域（州级）汇总逻辑测试。
"""

import build_ads_geo_state_summary as geo


def test_state_summary_excludes_invalid_orders(synthetic_dwd):
    orders = geo.prepare_orders(synthetic_dwd)
    summary = geo.build_state_summary(orders)
    sp = summary[summary["customer_state"] == "SP"].iloc[0]
    # SP 的 canceled 订单 o5(999) 应被排除，GMV = 100+200 = 300
    assert round(sp["gmv"], 2) == 300.0
    assert sp["order_count"] == 2


def test_rates_within_valid_range(synthetic_dwd):
    orders = geo.prepare_orders(synthetic_dwd)
    summary = geo.build_state_summary(orders)
    assert (summary["delivery_rate"].between(0, 1)).all()
    late = summary["late_delivery_rate"].dropna()
    assert (late.between(0, 1)).all()


def test_gmv_shares_sum_to_100(synthetic_dwd):
    orders = geo.prepare_orders(synthetic_dwd)
    summary = geo.build_state_summary(orders)
    assert round(summary["gmv_share_pct"].sum(), 1) == 100.0


def test_aov_equals_gmv_over_orders(synthetic_dwd):
    orders = geo.prepare_orders(synthetic_dwd)
    summary = geo.build_state_summary(orders)
    for _, row in summary.iterrows():
        assert round(row["aov"], 2) == round(row["gmv"] / row["order_count"], 2)
