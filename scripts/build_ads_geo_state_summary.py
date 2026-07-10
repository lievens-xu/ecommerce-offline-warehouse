"""
Build ADS geographic (state-level) business summary table.

构建 ADS 地域（州级）经营汇总表。

Aggregates the DWD order detail table by customer state to compare regional
demand, order value, and delivery performance across Brazil.

按客户所在州对 DWD 订单明细汇总，比较巴西各州的需求规模、客单价和物流表现。

Input  / 输入: data/dwd/dwd_order_detail.csv
Output / 输出:
    data/ads/ads_geo_state_summary.csv
    dashboard/geo_top_states_gmv.png
    dashboard/geo_state_delivery_performance.png
    docs/ads_geo_state_report.csv
"""

from datetime import datetime
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT_DIR = Path(__file__).resolve().parents[1]
DWD_DIR = ROOT_DIR / "data" / "dwd"
ADS_DIR = ROOT_DIR / "data" / "ads"
DASHBOARD_DIR = ROOT_DIR / "dashboard"
DOCS_DIR = ROOT_DIR / "docs"

for d in (ADS_DIR, DASHBOARD_DIR, DOCS_DIR):
    d.mkdir(parents=True, exist_ok=True)


DWD_FILE = DWD_DIR / "dwd_order_detail.csv"
INVALID_ORDER_STATUS = {"canceled", "unavailable"}


def read_dwd() -> pd.DataFrame:
    """
    Read the DWD order detail table.
    读取 DWD 订单明细表。
    """
    if not DWD_FILE.exists():
        raise FileNotFoundError(
            f"DWD table not found: {DWD_FILE}. "
            "Please run scripts/build_dwd_order_detail.py first."
        )
    return pd.read_csv(DWD_FILE, low_memory=False)


def prepare_orders(dwd: pd.DataFrame) -> pd.DataFrame:
    """
    Keep valid orders and normalize numeric fields.
    保留有效订单并规范数值字段。
    """
    df = dwd.copy()
    df = df[df["customer_state"].notna()]
    df = df[~df["order_status"].isin(INVALID_ORDER_STATUS)]

    for col in ["total_payment_amount", "delivery_days", "average_review_score"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["total_payment_amount"] = df["total_payment_amount"].fillna(0)
    df["is_delivered"] = pd.to_numeric(df["is_delivered"], errors="coerce").fillna(0)
    df["is_late_delivery"] = pd.to_numeric(
        df["is_late_delivery"], errors="coerce"
    ).fillna(0)
    return df


def build_state_summary(orders: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate to state level and compute business + delivery metrics.
    聚合到州级，计算经营与物流指标。
    """
    grouped = orders.groupby("customer_state", as_index=False).agg(
        order_count=("order_id", "nunique"),
        customer_count=("customer_unique_id", "nunique"),
        gmv=("total_payment_amount", "sum"),
        delivered_count=("is_delivered", "sum"),
        late_delivered_count=("is_late_delivery", "sum"),
        avg_delivery_days=("delivery_days", "mean"),
        avg_review_score=("average_review_score", "mean"),
    )

    grouped["gmv"] = grouped["gmv"].round(2)
    grouped["aov"] = (grouped["gmv"] / grouped["order_count"]).round(2)
    grouped["delivery_rate"] = (
        grouped["delivered_count"] / grouped["order_count"]
    ).round(4)
    grouped["late_delivery_rate"] = (
        grouped["late_delivered_count"] / grouped["delivered_count"].replace(0, pd.NA)
    ).round(4)
    grouped["avg_delivery_days"] = grouped["avg_delivery_days"].round(2)
    grouped["avg_review_score"] = grouped["avg_review_score"].round(2)

    grouped = grouped.sort_values("gmv", ascending=False).reset_index(drop=True)
    total_gmv = grouped["gmv"].sum()
    grouped["gmv_rank"] = grouped.index + 1
    grouped["gmv_share_pct"] = (grouped["gmv"] / total_gmv * 100).round(2)

    grouped["ads_loaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    grouped["dt"] = datetime.now().strftime("%Y-%m-%d")

    ordered_columns = [
        "gmv_rank",
        "customer_state",
        "gmv",
        "gmv_share_pct",
        "order_count",
        "customer_count",
        "aov",
        "delivery_rate",
        "late_delivery_rate",
        "avg_delivery_days",
        "avg_review_score",
        "ads_loaded_at",
        "dt",
    ]
    return grouped[ordered_columns]


def save_top_states_gmv_chart(summary: pd.DataFrame, top_n: int = 12) -> None:
    """
    Horizontal bar chart of the top-N states by GMV.
    GMV 前 N 州的横向柱状图。
    """
    output_path = DASHBOARD_DIR / "geo_top_states_gmv.png"
    top = summary.head(top_n).sort_values("gmv", ascending=True)

    plt.figure(figsize=(11, 6))
    plt.barh(top["customer_state"], top["gmv"], color="#8172B3")
    plt.title(f"Top {top_n} States by GMV")
    plt.xlabel("GMV (BRL)")
    plt.grid(True, axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"[OK] Chart generated: {output_path}")


def save_delivery_performance_chart(summary: pd.DataFrame, top_n: int = 12) -> None:
    """
    Compare average delivery days across the top-N states by GMV.
    对比 GMV 前 N 州的平均送达天数。
    """
    output_path = DASHBOARD_DIR / "geo_state_delivery_performance.png"
    top = summary.head(top_n).sort_values("avg_delivery_days", ascending=True)

    plt.figure(figsize=(11, 6))
    plt.bar(top["customer_state"], top["avg_delivery_days"], color="#CCB974")
    plt.title(f"Avg Delivery Days by State (Top {top_n} by GMV)")
    plt.xlabel("State")
    plt.ylabel("Avg Delivery Days")
    plt.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"[OK] Chart generated: {output_path}")


def generate_report(summary: pd.DataFrame) -> None:
    """
    Generate a compact report row.
    生成紧凑的报告行。
    """
    top_row = summary.iloc[0]
    top3_share = round(summary.head(3)["gmv_share_pct"].sum(), 2)

    report = {
        "table_name": "ads_geo_state_summary",
        "state_count": len(summary),
        "total_gmv": round(summary["gmv"].sum(), 2),
        "top_state": top_row["customer_state"],
        "top_state_gmv_share_pct": round(top_row["gmv_share_pct"], 2),
        "top3_states_gmv_share_pct": top3_share,
        "national_avg_delivery_days": round(summary["avg_delivery_days"].mean(), 2),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    report_df = pd.DataFrame([report])
    report_path = DOCS_DIR / "ads_geo_state_report.csv"
    report_df.to_csv(report_path, index=False, encoding="utf-8-sig")
    print(f"[OK] Geo state report generated: {report_path}")


def main() -> None:
    print("[INFO] Building ads_geo_state_summary ...")

    dwd = read_dwd()
    orders = prepare_orders(dwd)
    summary = build_state_summary(orders)

    output_path = ADS_DIR / "ads_geo_state_summary.csv"
    summary.to_csv(output_path, index=False, encoding="utf-8-sig")

    save_top_states_gmv_chart(summary)
    save_delivery_performance_chart(summary)
    generate_report(summary)

    print(f"[OK] Geo state summary table generated: {output_path}")
    print(f"[DONE] ads_geo_state_summary state count: {len(summary)}")


if __name__ == "__main__":
    main()
