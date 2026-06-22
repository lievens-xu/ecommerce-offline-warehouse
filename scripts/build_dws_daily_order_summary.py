from pathlib import Path
from datetime import datetime
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
DWD_DIR = ROOT_DIR / "data" / "dwd"
DWS_DIR = ROOT_DIR / "data" / "dws"
DOCS_DIR = ROOT_DIR / "docs"

DWS_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)


REQUIRED_COLUMNS = [
    "order_id",
    "customer_unique_id",
    "order_status",
    "purchase_date",
    "total_payment_amount",
    "total_product_amount",
    "total_freight_amount",
    "average_review_score",
    "review_count",
    "has_review_comment",
    "is_delivered",
    "is_late_delivery",
]


def read_dwd_order_detail() -> pd.DataFrame:
    """
    Read the DWD order detail table.
    """
    file_path = DWD_DIR / "dwd_order_detail.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            f"DWD table not found: {file_path}. Please run scripts/build_dwd_order_detail.py first."
        )

    return pd.read_csv(file_path, low_memory=False)


def validate_columns(df: pd.DataFrame) -> None:
    """
    Validate whether required columns exist.
    """
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing_columns:
        missing_text = "\n".join(f"- {col}" for col in missing_columns)
        raise ValueError(f"Missing required columns in dwd_order_detail:\n{missing_text}")


def prepare_dwd_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare DWD data before aggregation.
    """
    df = df.copy()

    df["purchase_date"] = pd.to_datetime(df["purchase_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df = df[df["purchase_date"].notna()]

    numeric_columns = [
        "total_payment_amount",
        "total_product_amount",
        "total_freight_amount",
        "review_count",
        "has_review_comment",
        "is_delivered",
        "is_late_delivery",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["average_review_score"] = pd.to_numeric(df["average_review_score"], errors="coerce")

    invalid_status = ["canceled", "unavailable"]
    df["is_valid_order"] = (~df["order_status"].fillna("").str.lower().isin(invalid_status)).astype(int)
    df["is_paid_order"] = (df["total_payment_amount"] > 0).astype(int)
    df["has_review"] = (df["review_count"] > 0).astype(int)

    return df


def safe_divide(numerator, denominator):
    """
    Avoid division by zero.
    """
    if denominator == 0:
        return 0
    return numerator / denominator


def build_dws_daily_order_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build daily order summary table.
    """
    daily = (
        df.groupby("purchase_date", as_index=False)
        .agg(
            order_count=("order_id", "nunique"),
            valid_order_count=("is_valid_order", "sum"),
            paid_order_count=("is_paid_order", "sum"),
            unique_customer_count=("customer_unique_id", "nunique"),
            delivered_order_count=("is_delivered", "sum"),
            late_delivery_order_count=("is_late_delivery", "sum"),
            review_order_count=("has_review", "sum"),
            review_comment_order_count=("has_review_comment", "sum"),
            total_payment_amount=("total_payment_amount", "sum"),
            total_product_amount=("total_product_amount", "sum"),
            total_freight_amount=("total_freight_amount", "sum"),
            average_review_score=("average_review_score", "mean"),
        )
    )

    daily["aov"] = daily.apply(
        lambda row: safe_divide(row["total_payment_amount"], row["order_count"]), axis=1
    )

    daily["avg_product_amount_per_order"] = daily.apply(
        lambda row: safe_divide(row["total_product_amount"], row["order_count"]), axis=1
    )

    daily["avg_freight_amount_per_order"] = daily.apply(
        lambda row: safe_divide(row["total_freight_amount"], row["order_count"]), axis=1
    )

    daily["delivery_rate"] = daily.apply(
        lambda row: safe_divide(row["delivered_order_count"], row["order_count"]), axis=1
    )

    daily["late_delivery_rate"] = daily.apply(
        lambda row: safe_divide(row["late_delivery_order_count"], row["delivered_order_count"]), axis=1
    )

    daily["review_rate"] = daily.apply(
        lambda row: safe_divide(row["review_order_count"], row["order_count"]), axis=1
    )

    daily["review_comment_rate"] = daily.apply(
        lambda row: safe_divide(row["review_comment_order_count"], row["review_order_count"]), axis=1
    )

    round_columns = [
        "total_payment_amount",
        "total_product_amount",
        "total_freight_amount",
        "aov",
        "avg_product_amount_per_order",
        "avg_freight_amount_per_order",
        "average_review_score",
        "delivery_rate",
        "late_delivery_rate",
        "review_rate",
        "review_comment_rate",
    ]

    for col in round_columns:
        daily[col] = daily[col].round(4)

    daily["dws_loaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    daily["dt"] = datetime.now().strftime("%Y-%m-%d")

    final_columns = [
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
        "avg_product_amount_per_order",
        "avg_freight_amount_per_order",
        "average_review_score",
        "dws_loaded_at",
        "dt",
    ]

    daily = daily[final_columns].sort_values("purchase_date").reset_index(drop=True)

    return daily


def generate_reports(dws: pd.DataFrame) -> None:
    """
    Generate table-level and column-level reports.
    """
    report = {
        "table_name": "dws_daily_order_summary",
        "row_count": len(dws),
        "start_date": dws["purchase_date"].min(),
        "end_date": dws["purchase_date"].max(),
        "total_order_count": int(dws["order_count"].sum()),
        "total_valid_order_count": int(dws["valid_order_count"].sum()),
        "total_payment_amount": round(dws["total_payment_amount"].sum(), 2),
        "overall_aov": round(safe_divide(dws["total_payment_amount"].sum(), dws["order_count"].sum()), 4),
        "overall_delivery_rate": round(
            safe_divide(dws["delivered_order_count"].sum(), dws["order_count"].sum()), 4
        ),
        "overall_late_delivery_rate": round(
            safe_divide(dws["late_delivery_order_count"].sum(), dws["delivered_order_count"].sum()), 4
        ),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    report_df = pd.DataFrame([report])
    report_path = DOCS_DIR / "dws_daily_order_summary_report.csv"
    report_df.to_csv(report_path, index=False, encoding="utf-8-sig")

    column_profile = []

    for col in dws.columns:
        column_profile.append(
            {
                "table_name": "dws_daily_order_summary",
                "column_name": col,
                "dtype": str(dws[col].dtype),
                "missing_count": int(dws[col].isna().sum()),
                "missing_rate": round(dws[col].isna().sum() / len(dws), 4),
                "unique_count": int(dws[col].nunique(dropna=True)),
            }
        )

    column_profile_df = pd.DataFrame(column_profile)
    column_profile_path = DOCS_DIR / "dws_daily_order_summary_column_profile.csv"
    column_profile_df.to_csv(column_profile_path, index=False, encoding="utf-8-sig")

    print(f"[OK] DWS report generated: {report_path}")
    print(f"[OK] DWS column profile generated: {column_profile_path}")


def main() -> None:
    print("[INFO] Building dws_daily_order_summary ...")

    dwd = read_dwd_order_detail()
    validate_columns(dwd)

    prepared_dwd = prepare_dwd_data(dwd)
    dws = build_dws_daily_order_summary(prepared_dwd)

    output_path = DWS_DIR / "dws_daily_order_summary.csv"
    dws.to_csv(output_path, index=False, encoding="utf-8-sig")

    generate_reports(dws)

    print(f"[OK] DWS table generated: {output_path}")
    print(f"[DONE] dws_daily_order_summary row count: {len(dws)}")


if __name__ == "__main__":
    main()