"""
Build ADS product category ranking table (with Pareto contribution).

构建 ADS 商品类目排名表（含帕累托贡献）。

This joins order items with products and the category translation table,
keeps only valid orders, and ranks categories by revenue. It also computes
the cumulative revenue share so you can see the classic 80/20 (Pareto) effect.

本脚本关联订单商品、商品维表和类目翻译表，仅保留有效订单，按收入对类目排名，
并计算累计收入占比，用于观察经典的二八法则（帕累托效应）。

Input  / 输入: data/ods/ods_order_items.csv, ods_products.csv,
              ods_product_category_translation.csv, ods_orders.csv
Output / 输出:
    data/ads/ads_product_category_rank.csv
    dashboard/product_category_top15_revenue.png
    dashboard/product_category_pareto.png
    docs/ads_product_category_report.csv
"""

from datetime import datetime
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT_DIR = Path(__file__).resolve().parents[1]
ODS_DIR = ROOT_DIR / "data" / "ods"
ADS_DIR = ROOT_DIR / "data" / "ads"
DASHBOARD_DIR = ROOT_DIR / "dashboard"
DOCS_DIR = ROOT_DIR / "docs"

for d in (ADS_DIR, DASHBOARD_DIR, DOCS_DIR):
    d.mkdir(parents=True, exist_ok=True)


INVALID_ORDER_STATUS = {"canceled", "unavailable"}


def read_ods(table_name: str) -> pd.DataFrame:
    """
    Read one ODS CSV table.
    读取一张 ODS CSV 表。
    """
    file_path = ODS_DIR / f"{table_name}.csv"
    if not file_path.exists():
        raise FileNotFoundError(f"ODS table not found: {file_path}")
    return pd.read_csv(file_path, low_memory=False)


def build_category_items() -> pd.DataFrame:
    """
    Join items -> products -> translation, filtered to valid orders.
    关联 商品明细 -> 商品维表 -> 类目翻译，并过滤为有效订单。
    """
    items = read_ods("ods_order_items")
    products = read_ods("ods_products")
    translation = read_ods("ods_product_category_translation")
    orders = read_ods("ods_orders")

    items["price"] = pd.to_numeric(items["price"], errors="coerce").fillna(0)
    items["freight_value"] = pd.to_numeric(
        items["freight_value"], errors="coerce"
    ).fillna(0)

    valid_orders = orders[~orders["order_status"].isin(INVALID_ORDER_STATUS)][
        ["order_id"]
    ]
    items = items.merge(valid_orders, on="order_id", how="inner")

    products = products[["product_id", "product_category_name"]]
    df = items.merge(products, on="product_id", how="left")
    df = df.merge(translation, on="product_category_name", how="left")

    # 英文类目缺失时回退到葡语原名，再缺失标记 unknown
    # Fall back to Portuguese name, then to "unknown".
    df["category"] = (
        df["product_category_name_english"]
        .fillna(df["product_category_name"])
        .fillna("unknown")
    )
    return df


def build_category_rank(category_items: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate to category level and compute revenue rank + Pareto share.
    聚合到类目级别，计算收入排名与帕累托累计占比。
    """
    agg = (
        category_items.groupby("category", as_index=False)
        .agg(
            product_revenue=("price", "sum"),
            freight_revenue=("freight_value", "sum"),
            item_count=("order_item_id", "count"),
            order_count=("order_id", "nunique"),
            product_count=("product_id", "nunique"),
        )
    )

    agg["product_revenue"] = agg["product_revenue"].round(2)
    agg["freight_revenue"] = agg["freight_revenue"].round(2)
    agg["avg_item_price"] = (
        agg["product_revenue"] / agg["item_count"].replace(0, pd.NA)
    ).round(2)

    agg = agg.sort_values("product_revenue", ascending=False).reset_index(drop=True)

    total_revenue = agg["product_revenue"].sum()
    agg["revenue_rank"] = agg.index + 1
    agg["revenue_share_pct"] = (agg["product_revenue"] / total_revenue * 100).round(2)
    agg["cumulative_revenue_share_pct"] = (
        agg["product_revenue"].cumsum() / total_revenue * 100
    ).round(2)

    agg["ads_loaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    agg["dt"] = datetime.now().strftime("%Y-%m-%d")

    ordered_columns = [
        "revenue_rank",
        "category",
        "product_revenue",
        "revenue_share_pct",
        "cumulative_revenue_share_pct",
        "freight_revenue",
        "item_count",
        "order_count",
        "product_count",
        "avg_item_price",
        "ads_loaded_at",
        "dt",
    ]
    return agg[ordered_columns]


def save_top_revenue_chart(rank_df: pd.DataFrame, top_n: int = 15) -> None:
    """
    Horizontal bar chart of the top-N categories by revenue.
    收入前 N 类目的横向柱状图。
    """
    output_path = DASHBOARD_DIR / "product_category_top15_revenue.png"
    top = rank_df.head(top_n).sort_values("product_revenue", ascending=True)

    plt.figure(figsize=(11, 7))
    plt.barh(top["category"], top["product_revenue"], color="#55A868")
    plt.title(f"Top {top_n} Product Categories by Revenue")
    plt.xlabel("Product Revenue (BRL)")
    plt.grid(True, axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"[OK] Chart generated: {output_path}")


def save_pareto_chart(rank_df: pd.DataFrame, top_n: int = 20) -> None:
    """
    Pareto chart: revenue bars + cumulative share line for top-N categories.
    帕累托图：收入柱 + 累计占比折线（前 N 类目）。
    """
    output_path = DASHBOARD_DIR / "product_category_pareto.png"
    top = rank_df.head(top_n)

    fig, ax1 = plt.subplots(figsize=(13, 7))
    ax1.bar(top["category"], top["product_revenue"], color="#4C72B0", label="Revenue")
    ax1.set_ylabel("Product Revenue (BRL)")
    ax1.set_xticks(range(len(top)))
    ax1.set_xticklabels(top["category"], rotation=60, ha="right")

    ax2 = ax1.twinx()
    ax2.plot(
        top["category"],
        top["cumulative_revenue_share_pct"],
        color="#C44E52",
        marker="o",
        label="Cumulative %",
    )
    ax2.axhline(80, color="gray", linestyle="--", alpha=0.6)
    ax2.set_ylabel("Cumulative Revenue Share (%)")
    ax2.set_ylim(0, 105)

    plt.title(f"Product Category Pareto (Top {top_n})")
    fig.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"[OK] Chart generated: {output_path}")


def generate_report(rank_df: pd.DataFrame) -> None:
    """
    Generate a compact report row.
    生成紧凑的报告行。
    """
    total_revenue = rank_df["product_revenue"].sum()
    categories_for_80 = int((rank_df["cumulative_revenue_share_pct"] <= 80).sum()) + 1
    top_row = rank_df.iloc[0]

    report = {
        "table_name": "ads_product_category_rank",
        "category_count": len(rank_df),
        "total_product_revenue": round(total_revenue, 2),
        "top_category": top_row["category"],
        "top_category_revenue": round(top_row["product_revenue"], 2),
        "top_category_share_pct": round(top_row["revenue_share_pct"], 2),
        "categories_for_80pct_revenue": categories_for_80,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    report_df = pd.DataFrame([report])
    report_path = DOCS_DIR / "ads_product_category_report.csv"
    report_df.to_csv(report_path, index=False, encoding="utf-8-sig")
    print(f"[OK] Product category report generated: {report_path}")


def main() -> None:
    print("[INFO] Building ads_product_category_rank ...")

    category_items = build_category_items()
    rank_df = build_category_rank(category_items)

    output_path = ADS_DIR / "ads_product_category_rank.csv"
    rank_df.to_csv(output_path, index=False, encoding="utf-8-sig")

    save_top_revenue_chart(rank_df)
    save_pareto_chart(rank_df)
    generate_report(rank_df)

    print(f"[OK] Product category rank table generated: {output_path}")
    print(f"[DONE] ads_product_category_rank category count: {len(rank_df)}")


if __name__ == "__main__":
    main()
