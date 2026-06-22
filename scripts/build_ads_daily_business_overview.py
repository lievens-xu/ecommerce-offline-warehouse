from pathlib import Path
from datetime import datetime
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
DWS_DIR = ROOT_DIR / "data" / "dws"
ADS_DIR = ROOT_DIR / "data" / "ads"
DOCS_DIR = ROOT_DIR / "docs"

ADS_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)


REQUIRED_COLUMNS = [
    "purchase_date",
    "order_count",
    "valid_order_count",
    "paid_order_count",
    "unique_customer_count",
    "delivered_order_count",
    "late_delivery_order_count",
    "delivery_rate",
    "late_delivery_rate",
    "review_order_count",
    "review_comment_order_count",
    "review_rate",
    "review_comment_rate",
    "total_payment_amount",
    "total_product_amount",
    "total_freight_amount",
    "aov",
    "average_review_score",
]


def read_dws_daily_order_summary() -> pd.DataFrame:
    """
    Read the DWS daily order summary table.
    """
    file_path = DWS_DIR / "dws_daily_order_summary.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            f"DWS table not found: {file_path}. "
            "Please run scripts/build_dws_daily_order_summary.py first."
        )

    return pd.read_csv(file_path, low_memory=False)


def validate_columns(df: pd.DataFrame) -> None:
    """
    Validate whether all required columns exist.
    """
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing_columns:
        missing_text = "\n".join(f"- {col}" for col in missing_columns)
        raise ValueError(f"Missing required columns in dws_daily_order_summary:\n{missing_text}")


def safe_divide(numerator, denominator):
    """
    Avoid division by zero.
    """
    if denominator == 0:
        return 0
    return numerator / denominator


def build_ads_daily_business_overview(dws: pd.DataFrame) -> pd.DataFrame:
    """
    Build ADS daily business overview table for BI dashboard.
    """
    df = dws.copy()

    df["purchase_date"] = pd.to_datetime(df["purchase_date"], errors="coerce")
    df = df[df["purchase_date"].notna()]
    df = df.sort_values("purchase_date").reset_index(drop=True)

    numeric_columns = [
        "order_count",
        "valid_order_count",
        "paid_order_count",
        "unique_customer_count",
        "delivered_order_count",
        "late_delivery_order_count",
        "delivery_rate",
        "late_delivery_rate",
        "review_order_count",
        "review_comment_order_count",
        "review_rate",
        "review_comment_rate",
        "total_payment_amount",
        "total_product_amount",
        "total_freight_amount",
        "aov",
        "average_review_score",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df[numeric_columns] = df[numeric_columns].fillna(0)

    ads = pd.DataFrame()

    ads["stat_date"] = df["purchase_date"].dt.strftime("%Y-%m-%d")
    ads["stat_month"] = df["purchase_date"].dt.strftime("%Y-%m")

    ads["daily_order_count"] = df["order_count"]
    ads["daily_valid_order_count"] = df["valid_order_count"]
    ads["daily_paid_order_count"] = df["paid_order_count"]
    ads["daily_unique_customer_count"] = df["unique_customer_count"]

    ads["daily_gmv"] = df["total_payment_amount"]
    ads["daily_product_amount"] = df["total_product_amount"]
    ads["daily_freight_amount"] = df["total_freight_amount"]
    ads["daily_aov"] = df["aov"]

    ads["daily_delivery_rate"] = df["delivery_rate"]
    ads["daily_late_delivery_rate"] = df["late_delivery_rate"]
    ads["daily_review_rate"] = df["review_rate"]
    ads["daily_review_comment_rate"] = df["review_comment_rate"]
    ads["daily_average_review_score"] = df["average_review_score"]

    ads["valid_order_rate"] = df.apply(
        lambda row: safe_divide(row["valid_order_count"], row["order_count"]), axis=1
    )

    ads["paid_order_rate"] = df.apply(
        lambda row: safe_divide(row["paid_order_count"], row["order_count"]), axis=1
    )

    ads["gmv_7d_moving_avg"] = ads["daily_gmv"].rolling(window=7, min_periods=1).mean()
    ads["order_count_7d_moving_avg"] = ads["daily_order_count"].rolling(window=7, min_periods=1).mean()
    ads["aov_7d_moving_avg"] = ads["daily_aov"].rolling(window=7, min_periods=1).mean()

    ads["cumulative_gmv"] = ads["daily_gmv"].cumsum()
    ads["cumulative_order_count"] = ads["daily_order_count"].cumsum()
    ads["cumulative_customer_count"] = df["unique_customer_count"].cumsum()

    ads["gmv_day_over_day_change"] = ads["daily_gmv"].diff()
    ads["order_count_day_over_day_change"] = ads["daily_order_count"].diff()

    ads["gmv_day_over_day_rate"] = ads["daily_gmv"].pct_change().replace([float("inf"), -float("inf")], 0)
    ads["order_count_day_over_day_rate"] = (
        ads["daily_order_count"].pct_change().replace([float("inf"), -float("inf")], 0)
    )

    ads["gmv_day_over_day_change"] = ads["gmv_day_over_day_change"].fillna(0)
    ads["order_count_day_over_day_change"] = ads["order_count_day_over_day_change"].fillna(0)
    ads["gmv_day_over_day_rate"] = ads["gmv_day_over_day_rate"].fillna(0)
    ads["order_count_day_over_day_rate"] = ads["order_count_day_over_day_rate"].fillna(0)

    round_columns = [
        "daily_gmv",
        "daily_product_amount",
        "daily_freight_amount",
        "daily_aov",
        "daily_delivery_rate",
        "daily_late_delivery_rate",
        "daily_review_rate",
        "daily_review_comment_rate",
        "daily_average_review_score",
        "valid_order_rate",
        "paid_order_rate",
        "gmv_7d_moving_avg",
        "order_count_7d_moving_avg",
        "aov_7d_moving_avg",
        "cumulative_gmv",
        "gmv_day_over_day_change",
        "order_count_day_over_day_change",
        "gmv_day_over_day_rate",
        "order_count_day_over_day_rate",
    ]

    for col in round_columns:
        ads[col] = ads[col].round(4)

    ads["ads_loaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ads["dt"] = datetime.now().strftime("%Y-%m-%d")

    final_columns = [
        "stat_date",
        "stat_month",
        "daily_order_count",
        "daily_valid_order_count",
        "daily_paid_order_count",
        "daily_unique_customer_count",
        "daily_gmv",
        "daily_product_amount",
        "daily_freight_amount",
        "daily_aov",
        "daily_delivery_rate",
        "daily_late_delivery_rate",
        "daily_review_rate",
        "daily_review_comment_rate",
        "daily_average_review_score",
        "valid_order_rate",
        "paid_order_rate",
        "gmv_7d_moving_avg",
        "order_count_7d_moving_avg",
        "aov_7d_moving_avg",
        "cumulative_gmv",
        "cumulative_order_count",
        "cumulative_customer_count",
        "gmv_day_over_day_change",
        "order_count_day_over_day_change",
        "gmv_day_over_day_rate",
        "order_count_day_over_day_rate",
        "ads_loaded_at",
        "dt",
    ]

    return ads[final_columns]


def generate_reports(ads: pd.DataFrame) -> None:
    """
    Generate table-level and column-level reports.
    """
    report = {
        "table_name": "ads_daily_business_overview",
        "row_count": len(ads),
        "start_date": ads["stat_date"].min(),
        "end_date": ads["stat_date"].max(),
        "total_order_count": int(ads["daily_order_count"].sum()),
        "total_gmv": round(ads["daily_gmv"].sum(), 2),
        "average_daily_gmv": round(ads["daily_gmv"].mean(), 4),
        "average_daily_order_count": round(ads["daily_order_count"].mean(), 4),
        "overall_aov": round(
            safe_divide(ads["daily_gmv"].sum(), ads["daily_order_count"].sum()), 4
        ),
        "latest_stat_date": ads["stat_date"].max(),
        "latest_daily_gmv": round(
            ads.loc[ads["stat_date"] == ads["stat_date"].max(), "daily_gmv"].sum(), 4
        ),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    report_df = pd.DataFrame([report])
    report_path = DOCS_DIR / "ads_daily_business_overview_report.csv"
    report_df.to_csv(report_path, index=False, encoding="utf-8-sig")

    column_profile = []

    for col in ads.columns:
        column_profile.append(
            {
                "table_name": "ads_daily_business_overview",
                "column_name": col,
                "dtype": str(ads[col].dtype),
                "missing_count": int(ads[col].isna().sum()),
                "missing_rate": round(ads[col].isna().sum() / len(ads), 4),
                "unique_count": int(ads[col].nunique(dropna=True)),
            }
        )

    column_profile_df = pd.DataFrame(column_profile)
    column_profile_path = DOCS_DIR / "ads_daily_business_overview_column_profile.csv"
    column_profile_df.to_csv(column_profile_path, index=False, encoding="utf-8-sig")

    print(f"[OK] ADS report generated: {report_path}")
    print(f"[OK] ADS column profile generated: {column_profile_path}")


def main() -> None:
    print("[INFO] Building ads_daily_business_overview ...")

    dws = read_dws_daily_order_summary()
    validate_columns(dws)

    ads = build_ads_daily_business_overview(dws)

    output_path = ADS_DIR / "ads_daily_business_overview.csv"
    ads.to_csv(output_path, index=False, encoding="utf-8-sig")

    generate_reports(ads)

    print(f"[OK] ADS table generated: {output_path}")
    print(f"[DONE] ads_daily_business_overview row count: {len(ads)}")


if __name__ == "__main__":
    main()