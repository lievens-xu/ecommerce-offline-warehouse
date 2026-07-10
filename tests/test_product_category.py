"""
Tests for the product-category ranking logic.
商品类目排名逻辑测试。
"""

import build_ads_product_category_rank as pc


def test_category_rank_orders_by_revenue(synthetic_category_items):
    rank_df = pc.build_category_rank(synthetic_category_items)
    # electronics = 500+300 = 800 应排第一
    assert rank_df.iloc[0]["category"] == "electronics"
    assert rank_df.iloc[0]["revenue_rank"] == 1
    assert round(rank_df.iloc[0]["product_revenue"], 2) == 800.0


def test_revenue_shares_sum_to_100(synthetic_category_items):
    rank_df = pc.build_category_rank(synthetic_category_items)
    assert round(rank_df["revenue_share_pct"].sum(), 1) == 100.0


def test_cumulative_share_is_monotonic_and_ends_at_100(synthetic_category_items):
    rank_df = pc.build_category_rank(synthetic_category_items)
    cum = rank_df["cumulative_revenue_share_pct"].tolist()
    assert cum == sorted(cum)  # 单调不减
    assert round(cum[-1], 1) == 100.0


def test_order_and_item_counts(synthetic_category_items):
    rank_df = pc.build_category_rank(synthetic_category_items)
    electronics = rank_df[rank_df["category"] == "electronics"].iloc[0]
    # electronics 两个明细行，同属订单 o1
    assert electronics["item_count"] == 2
    assert electronics["order_count"] == 1
