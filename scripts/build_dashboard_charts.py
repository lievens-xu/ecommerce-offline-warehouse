from pathlib import Path
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt


ROOT_DIR = Path(__file__).resolve().parents[1]
ADS_DIR = ROOT_DIR / "data" / "ads"
DASHBOARD_DIR = ROOT_DIR / "dashboard"
DOCS_DIR = ROOT_DIR / "docs"

DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)


ADS_FILE = ADS_DIR / "ads_daily_business_overview.csv"


REQUIRED_COLUMNS = [
    "stat_date",
    "daily_order_count",
    "daily_unique_customer_count",
    "daily_gmv",
    "daily_aov",
    "daily_delivery_rate",
    "daily_late_delivery_rate",
    "daily_review_rate",
    "daily_average_review_score",
    "gmv_7d_moving_avg",
    "order_count_7d_moving_avg",
    "aov_7d_moving_avg",
    "cumulative_gmv",
    "cumulative_order_count",
    "gmv_day_over_day_rate",
    "order_count_day_over_day_rate",
]


def read_ads_table() -> pd.DataFrame:
    """
    Read ADS daily business overview table.
    """
    if not ADS_FILE.exists():
        raise FileNotFoundError(
            f"ADS table not found: {ADS_FILE}. "
            "Please run scripts/build_ads_daily_business_overview.py first."
        )

    df = pd.read_csv(ADS_FILE, low_memory=False)
    return df


def validate_columns(df: pd.DataFrame) -> None:
    """
    Validate required columns.
    """
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing_columns:
        missing_text = "\n".join(f"- {col}" for col in missing_columns)
        raise ValueError(f"Missing required columns in ADS table:\n{missing_text}")


def prepare_dashboard_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare data for dashboard visualization.
    """
    df = df.copy()

    df["stat_date"] = pd.to_datetime(df["stat_date"], errors="coerce")
    df = df[df["stat_date"].notna()]
    df = df.sort_values("stat_date").reset_index(drop=True)

    numeric_columns = [col for col in REQUIRED_COLUMNS if col != "stat_date"]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    rate_columns = [
        "daily_delivery_rate",
        "daily_late_delivery_rate",
        "daily_review_rate",
        "gmv_day_over_day_rate",
        "order_count_day_over_day_rate",
    ]

    for col in rate_columns:
        df[f"{col}_pct"] = df[col] * 100

    return df


def save_line_chart(df: pd.DataFrame, y_columns: list, title: str, ylabel: str, output_name: str) -> None:
    """
    Save a line chart.
    """
    output_path = DASHBOARD_DIR / output_name

    plt.figure(figsize=(12, 6))

    for col in y_columns:
        plt.plot(df["stat_date"], df[col], label=col)

    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"[OK] Chart generated: {output_path}")


def save_bar_chart(df: pd.DataFrame, y_column: str, title: str, ylabel: str, output_name: str) -> None:
    """
    Save a bar chart.
    """
    output_path = DASHBOARD_DIR / output_name

    plt.figure(figsize=(12, 6))
    plt.bar(df["stat_date"], df[y_column], label=y_column)
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True, axis="y", alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"[OK] Chart generated: {output_path}")


def generate_kpi_summary(df: pd.DataFrame) -> None:
    """
    Generate KPI summary table.
    """
    latest_row = df.iloc[-1]

    summary = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "start_date": df["stat_date"].min().strftime("%Y-%m-%d"),
        "end_date": df["stat_date"].max().strftime("%Y-%m-%d"),
        "total_gmv": round(df["daily_gmv"].sum(), 2),
        "total_order_count": int(df["daily_order_count"].sum()),
        "total_cumulative_gmv_latest": round(latest_row["cumulative_gmv"], 2),
        "total_cumulative_order_count_latest": int(latest_row["cumulative_order_count"]),
        "average_daily_gmv": round(df["daily_gmv"].mean(), 2),
        "average_daily_order_count": round(df["daily_order_count"].mean(), 2),
        "overall_aov": round(df["daily_gmv"].sum() / df["daily_order_count"].sum(), 4)
        if df["daily_order_count"].sum() != 0
        else 0,
        "average_delivery_rate": round(df["daily_delivery_rate"].mean(), 4),
        "average_late_delivery_rate": round(df["daily_late_delivery_rate"].mean(), 4),
        "average_review_rate": round(df["daily_review_rate"].mean(), 4),
        "average_review_score": round(df["daily_average_review_score"].mean(), 4),
        "latest_stat_date": latest_row["stat_date"].strftime("%Y-%m-%d"),
        "latest_daily_gmv": round(latest_row["daily_gmv"], 2),
        "latest_daily_order_count": int(latest_row["daily_order_count"]),
        "latest_daily_aov": round(latest_row["daily_aov"], 4),
    }

    summary_df = pd.DataFrame([summary])
    output_path = DASHBOARD_DIR / "dashboard_kpi_summary.csv"
    summary_df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"[OK] KPI summary generated: {output_path}")


def generate_dashboard_readme() -> None:
    """
    Generate a simple dashboard index file.
    """
    output_path = DASHBOARD_DIR / "dashboard_readme.md"

    with output_path.open("w", encoding="utf-8") as f:
        f.write("# Dashboard Output / 看板输出\n\n")
        f.write("This folder stores dashboard charts generated from the ADS layer.\n\n")
        f.write("本目录存放基于 ADS 层数据生成的看板图表。\n\n")

        f.write("## Generated Charts / 已生成图表\n\n")
        f.write("| Chart / 图表 | File / 文件 |\n")
        f.write("|---|---|\n")
        f.write("| GMV trend / GMV 趋势 | `gmv_trend.png` |\n")
        f.write("| Order count trend / 订单数趋势 | `order_count_trend.png` |\n")
        f.write("| AOV trend / 客单价趋势 | `aov_trend.png` |\n")
        f.write("| Cumulative business trend / 累计经营趋势 | `cumulative_business_trend.png` |\n")
        f.write("| Delivery performance / 物流表现 | `delivery_performance.png` |\n")
        f.write("| Review performance / 评价表现 | `review_performance.png` |\n")
        f.write("| Day-over-day growth / 日环比增长 | `day_over_day_growth.png` |\n\n")

        f.write("## KPI Summary / KPI 汇总\n\n")
        f.write("KPI summary file:\n\n")
        f.write("KPI 汇总文件：\n\n")
        f.write("    dashboard/dashboard_kpi_summary.csv\n")

    print(f"[OK] Dashboard README generated: {output_path}")


def build_dashboard_charts(df: pd.DataFrame) -> None:
    """
    Build all dashboard charts.
    """
    save_line_chart(
        df,
        ["daily_gmv", "gmv_7d_moving_avg"],
        "Daily GMV Trend",
        "GMV",
        "gmv_trend.png",
    )

    save_line_chart(
        df,
        ["daily_order_count", "order_count_7d_moving_avg"],
        "Daily Order Count Trend",
        "Order Count",
        "order_count_trend.png",
    )

    save_line_chart(
        df,
        ["daily_aov", "aov_7d_moving_avg"],
        "Daily AOV Trend",
        "AOV",
        "aov_trend.png",
    )

    save_line_chart(
        df,
        ["cumulative_gmv", "cumulative_order_count"],
        "Cumulative Business Trend",
        "Cumulative Value",
        "cumulative_business_trend.png",
    )

    save_line_chart(
        df,
        ["daily_delivery_rate_pct", "daily_late_delivery_rate_pct"],
        "Delivery Performance",
        "Rate (%)",
        "delivery_performance.png",
    )

    save_line_chart(
        df,
        ["daily_review_rate_pct", "daily_average_review_score"],
        "Review Performance",
        "Review Rate (%) / Review Score",
        "review_performance.png",
    )

    save_line_chart(
        df,
        ["gmv_day_over_day_rate_pct", "order_count_day_over_day_rate_pct"],
        "Day-over-Day Growth Rate",
        "Growth Rate (%)",
        "day_over_day_growth.png",
    )


def main() -> None:
    print("[INFO] Building dashboard charts ...")

    ads = read_ads_table()
    validate_columns(ads)

    dashboard_df = prepare_dashboard_data(ads)

    build_dashboard_charts(dashboard_df)
    generate_kpi_summary(dashboard_df)
    generate_dashboard_readme()

    print("[DONE] Dashboard charts have been generated successfully.")


if __name__ == "__main__":
    main()