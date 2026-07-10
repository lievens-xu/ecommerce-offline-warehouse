"""
Build ADS customer RFM segmentation table.

构建 ADS 客户 RFM 分层表。

RFM segmentation groups customers by Recency (how recently they bought),
Frequency (how often), and Monetary (how much). It turns the order-level
DWD table into a customer-level marketing view.

RFM 分层基于最近一次消费(Recency)、消费频次(Frequency)和消费金额(Monetary)
对客户进行分群，将订单级 DWD 明细表转化为客户级的营销视角。

Input  / 输入: data/dwd/dwd_order_detail.csv
Output / 输出:
    data/ads/ads_customer_rfm.csv                 (customer-level / 客户级明细)
    data/ads/ads_customer_rfm_segment_summary.csv (segment-level / 分层汇总)
    dashboard/rfm_segment_customers.png
    dashboard/rfm_segment_monetary.png
    docs/ads_customer_rfm_report.csv
"""

from datetime import datetime, timedelta
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")  # 无界面后端，服务器/CI 可用
import matplotlib.pyplot as plt


ROOT_DIR = Path(__file__).resolve().parents[1]
DWD_DIR = ROOT_DIR / "data" / "dwd"
ADS_DIR = ROOT_DIR / "data" / "ads"
DASHBOARD_DIR = ROOT_DIR / "dashboard"
DOCS_DIR = ROOT_DIR / "docs"

for d in (ADS_DIR, DASHBOARD_DIR, DOCS_DIR):
    d.mkdir(parents=True, exist_ok=True)


DWD_FILE = DWD_DIR / "dwd_order_detail.csv"

# 无效订单状态：计算客户价值时排除取消/不可用订单
# Invalid order statuses excluded when measuring customer value.
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
    Keep valid orders and normalize the fields RFM needs.
    保留有效订单并规范 RFM 所需字段。
    """
    df = dwd.copy()

    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"], errors="coerce"
    )
    df["total_payment_amount"] = pd.to_numeric(
        df["total_payment_amount"], errors="coerce"
    ).fillna(0)

    df = df[df["order_purchase_timestamp"].notna()]
    df = df[df["customer_unique_id"].notna()]
    df = df[~df["order_status"].isin(INVALID_ORDER_STATUS)]

    return df


def build_rfm_base(orders: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """
    Aggregate orders to customer level and compute R/F/M.
    将订单聚合到客户级并计算 R/F/M。

    The snapshot date is the last purchase date in the dataset plus one day,
    so recency is measured relative to the dataset, not wall-clock time.
    快照日期取数据集中最后一次购买日期 +1 天，因此 recency 相对数据集衡量，
    而非真实世界当前时间。
    """
    snapshot_date = orders["order_purchase_timestamp"].max() + timedelta(days=1)

    rfm = (
        orders.groupby("customer_unique_id", as_index=False)
        .agg(
            last_purchase=("order_purchase_timestamp", "max"),
            frequency=("order_id", "nunique"),
            monetary=("total_payment_amount", "sum"),
        )
    )

    rfm["recency"] = (snapshot_date - rfm["last_purchase"]).dt.days
    rfm["monetary"] = rfm["monetary"].round(2)

    return rfm, snapshot_date.strftime("%Y-%m-%d")


def score_quintiles(series: pd.Series, ascending: bool) -> pd.Series:
    """
    Assign 1-5 quintile scores using a rank to stay robust against ties.
    使用 rank 后再分箱，避免大量并列值导致 qcut 边界重复而报错。

    ascending=True  -> larger value gets a higher score (Frequency / Monetary).
    ascending=False -> smaller value gets a higher score (Recency).
    """
    ranks = series.rank(method="first", ascending=ascending)
    scores = pd.qcut(ranks, 5, labels=[1, 2, 3, 4, 5])
    return scores.astype(int)


def assign_segment(r: int, f: int) -> str:
    """
    Map an (R, F) score pair to a business segment.
    将 (R, F) 打分映射到业务分层。

    Note: the Olist dataset is dominated by one-time buyers, so Frequency has
    low variance. Segments therefore lean heavily on Recency, which is the
    honest read of this data.
    说明：Olist 数据以一次性购买为主，Frequency 方差很小，因此分层更依赖
    Recency，这是对该数据集诚实的解读。
    """
    if r >= 4 and f >= 4:
        return "Champions / 重要价值客户"
    if r >= 3 and f >= 3:
        return "Loyal / 忠诚客户"
    if r >= 4 and f <= 2:
        return "Recent / 新近活跃客户"
    if r == 3 and f <= 2:
        return "Promising / 有潜力客户"
    if r == 2 and f >= 3:
        return "At Risk / 需挽留客户"
    if r <= 2 and f >= 4:
        return "Cant Lose / 高价值流失预警"
    if r == 2 and f <= 2:
        return "Hibernating / 沉睡客户"
    return "Lost / 已流失客户"


def build_customer_rfm(rfm: pd.DataFrame) -> pd.DataFrame:
    """
    Add R/F/M scores and segments to the customer table.
    为客户表添加 R/F/M 打分与分层。
    """
    rfm = rfm.copy()

    rfm["r_score"] = score_quintiles(rfm["recency"], ascending=False)
    rfm["f_score"] = score_quintiles(rfm["frequency"], ascending=True)
    rfm["m_score"] = score_quintiles(rfm["monetary"], ascending=True)

    rfm["rfm_score"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]
    rfm["rfm_cell"] = (
        rfm["r_score"].astype(str)
        + rfm["f_score"].astype(str)
        + rfm["m_score"].astype(str)
    )
    rfm["segment"] = [
        assign_segment(int(r), int(f))
        for r, f in zip(rfm["r_score"], rfm["f_score"])
    ]

    rfm["ads_loaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rfm["dt"] = datetime.now().strftime("%Y-%m-%d")

    final_columns = [
        "customer_unique_id",
        "recency",
        "frequency",
        "monetary",
        "r_score",
        "f_score",
        "m_score",
        "rfm_score",
        "rfm_cell",
        "segment",
        "ads_loaded_at",
        "dt",
    ]
    return rfm[final_columns]


def build_segment_summary(customer_rfm: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate the customer table into a per-segment summary.
    将客户表汇总为分层级别的概览。
    """
    total_customers = len(customer_rfm)
    total_monetary = customer_rfm["monetary"].sum()

    summary = (
        customer_rfm.groupby("segment", as_index=False)
        .agg(
            customer_count=("customer_unique_id", "nunique"),
            avg_recency=("recency", "mean"),
            avg_frequency=("frequency", "mean"),
            avg_monetary=("monetary", "mean"),
            total_monetary=("monetary", "sum"),
        )
    )

    summary["customer_pct"] = (
        summary["customer_count"] / total_customers * 100
    ).round(2)
    summary["monetary_pct"] = (
        summary["total_monetary"] / total_monetary * 100
    ).round(2)
    summary["avg_recency"] = summary["avg_recency"].round(1)
    summary["avg_frequency"] = summary["avg_frequency"].round(3)
    summary["avg_monetary"] = summary["avg_monetary"].round(2)
    summary["total_monetary"] = summary["total_monetary"].round(2)

    summary = summary.sort_values("total_monetary", ascending=False).reset_index(
        drop=True
    )

    ordered_columns = [
        "segment",
        "customer_count",
        "customer_pct",
        "avg_recency",
        "avg_frequency",
        "avg_monetary",
        "total_monetary",
        "monetary_pct",
    ]
    return summary[ordered_columns]


def save_bar_chart(
    summary: pd.DataFrame, value_col: str, title: str, ylabel: str, output_name: str
) -> None:
    """
    Save a horizontal bar chart of a segment metric.
    保存分层指标的横向柱状图。
    """
    output_path = DASHBOARD_DIR / output_name

    plot_df = summary.sort_values(value_col, ascending=True)

    plt.figure(figsize=(11, 6))
    plt.barh(plot_df["segment"], plot_df[value_col], color="#4C72B0")
    plt.title(title)
    plt.xlabel(ylabel)
    plt.grid(True, axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"[OK] Chart generated: {output_path}")


def generate_report(customer_rfm: pd.DataFrame, snapshot_date: str) -> None:
    """
    Generate a compact report row for pipeline dashboards.
    生成用于主流程汇总的紧凑报告行。
    """
    report = {
        "table_name": "ads_customer_rfm",
        "snapshot_date": snapshot_date,
        "customer_count": customer_rfm["customer_unique_id"].nunique(),
        "repeat_customer_count": int((customer_rfm["frequency"] > 1).sum()),
        "avg_recency_days": round(customer_rfm["recency"].mean(), 1),
        "avg_frequency": round(customer_rfm["frequency"].mean(), 3),
        "avg_monetary": round(customer_rfm["monetary"].mean(), 2),
        "segment_count": customer_rfm["segment"].nunique(),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    report_df = pd.DataFrame([report])
    report_path = DOCS_DIR / "ads_customer_rfm_report.csv"
    report_df.to_csv(report_path, index=False, encoding="utf-8-sig")
    print(f"[OK] RFM report generated: {report_path}")


def main() -> None:
    print("[INFO] Building ads_customer_rfm ...")

    dwd = read_dwd()
    orders = prepare_orders(dwd)
    rfm_base, snapshot_date = build_rfm_base(orders)

    customer_rfm = build_customer_rfm(rfm_base)
    segment_summary = build_segment_summary(customer_rfm)

    customer_path = ADS_DIR / "ads_customer_rfm.csv"
    summary_path = ADS_DIR / "ads_customer_rfm_segment_summary.csv"
    customer_rfm.to_csv(customer_path, index=False, encoding="utf-8-sig")
    segment_summary.to_csv(summary_path, index=False, encoding="utf-8-sig")

    save_bar_chart(
        segment_summary,
        "customer_count",
        "RFM Segments by Customer Count",
        "Customer Count",
        "rfm_segment_customers.png",
    )
    save_bar_chart(
        segment_summary,
        "total_monetary",
        "RFM Segments by Revenue Contribution",
        "Total Monetary (BRL)",
        "rfm_segment_monetary.png",
    )

    generate_report(customer_rfm, snapshot_date)

    print(f"[OK] Customer RFM table generated: {customer_path}")
    print(f"[OK] Segment summary generated: {summary_path}")
    print(f"[INFO] Snapshot date: {snapshot_date}")
    print(f"[DONE] ads_customer_rfm customer count: {len(customer_rfm)}")


if __name__ == "__main__":
    main()
