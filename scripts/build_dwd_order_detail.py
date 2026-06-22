from pathlib import Path
from datetime import datetime
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
ODS_DIR = ROOT_DIR / "data" / "ods"
DWD_DIR = ROOT_DIR / "data" / "dwd"
DOCS_DIR = ROOT_DIR / "docs"

DWD_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)


def read_ods_table(table_name: str) -> pd.DataFrame:
    """
    Read one ODS CSV table.
    """
    file_path = ODS_DIR / f"{table_name}.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"ODS table not found: {file_path}")

    return pd.read_csv(file_path, low_memory=False)


def parse_datetime_columns(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    Convert selected columns to datetime.
    """
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


def aggregate_order_items(order_items: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate order item data to order level.
    """
    order_items["price"] = pd.to_numeric(order_items["price"], errors="coerce").fillna(0)
    order_items["freight_value"] = pd.to_numeric(order_items["freight_value"], errors="coerce").fillna(0)

    item_agg = (
        order_items
        .groupby("order_id", as_index=False)
        .agg(
            order_item_count=("order_item_id", "count"),
            product_count=("product_id", "nunique"),
            seller_count=("seller_id", "nunique"),
            total_product_amount=("price", "sum"),
            total_freight_amount=("freight_value", "sum"),
        )
    )

    return item_agg


def aggregate_payments(payments: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate payment data to order level.
    """
    payments["payment_value"] = pd.to_numeric(payments["payment_value"], errors="coerce").fillna(0)
    payments["payment_installments"] = pd.to_numeric(
        payments["payment_installments"], errors="coerce"
    ).fillna(0)

    payment_agg = (
        payments
        .groupby("order_id", as_index=False)
        .agg(
            total_payment_amount=("payment_value", "sum"),
            payment_type_count=("payment_type", "nunique"),
            max_payment_installments=("payment_installments", "max"),
        )
    )

    payment_type_amount = (
        payments
        .groupby(["order_id", "payment_type"], as_index=False)
        .agg(payment_type_amount=("payment_value", "sum"))
        .sort_values(["order_id", "payment_type_amount"], ascending=[True, False])
    )

    main_payment_type = (
        payment_type_amount
        .drop_duplicates(subset=["order_id"])
        [["order_id", "payment_type"]]
        .rename(columns={"payment_type": "main_payment_type"})
    )

    payment_agg = payment_agg.merge(main_payment_type, on="order_id", how="left")

    return payment_agg


def aggregate_reviews(reviews: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate review data to order level.
    """
    reviews["review_score"] = pd.to_numeric(reviews["review_score"], errors="coerce")

    title = reviews["review_comment_title"].fillna("").astype(str).str.strip()
    message = reviews["review_comment_message"].fillna("").astype(str).str.strip()

    reviews["has_review_comment"] = ((title != "") | (message != "")).astype(int)

    review_agg = (
        reviews
        .groupby("order_id", as_index=False)
        .agg(
            average_review_score=("review_score", "mean"),
            review_count=("review_id", "count"),
            has_review_comment=("has_review_comment", "max"),
        )
    )

    review_agg["average_review_score"] = review_agg["average_review_score"].round(2)

    return review_agg


def build_dwd_order_detail() -> pd.DataFrame:
    """
    Build DWD order-level detail table.
    """
    orders = read_ods_table("ods_orders")
    customers = read_ods_table("ods_customers")
    order_items = read_ods_table("ods_order_items")
    payments = read_ods_table("ods_order_payments")
    reviews = read_ods_table("ods_order_reviews")

    orders = parse_datetime_columns(
        orders,
        [
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
    )

    item_agg = aggregate_order_items(order_items)
    payment_agg = aggregate_payments(payments)
    review_agg = aggregate_reviews(reviews)

    dwd = (
        orders
        .merge(customers, on="customer_id", how="left")
        .merge(item_agg, on="order_id", how="left")
        .merge(payment_agg, on="order_id", how="left")
        .merge(review_agg, on="order_id", how="left")
    )

    numeric_fill_columns = [
        "order_item_count",
        "product_count",
        "seller_count",
        "total_product_amount",
        "total_freight_amount",
        "total_payment_amount",
        "payment_type_count",
        "max_payment_installments",
        "review_count",
        "has_review_comment",
    ]

    for col in numeric_fill_columns:
        if col in dwd.columns:
            dwd[col] = dwd[col].fillna(0)

    dwd["main_payment_type"] = dwd["main_payment_type"].fillna("unknown")

    dwd["purchase_date"] = dwd["order_purchase_timestamp"].dt.strftime("%Y-%m-%d")
    dwd["purchase_month"] = dwd["order_purchase_timestamp"].dt.strftime("%Y-%m")

    dwd["delivery_days"] = (
        dwd["order_delivered_customer_date"] - dwd["order_purchase_timestamp"]
    ).dt.days

    dwd["estimated_delivery_days"] = (
        dwd["order_estimated_delivery_date"] - dwd["order_purchase_timestamp"]
    ).dt.days

    dwd["delivery_delay_days"] = (
        dwd["order_delivered_customer_date"] - dwd["order_estimated_delivery_date"]
    ).dt.days

    dwd["is_delivered"] = dwd["order_delivered_customer_date"].notna().astype(int)
    dwd["is_late_delivery"] = (dwd["delivery_delay_days"] > 0).fillna(False).astype(int)

    dwd["dwd_loaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dwd["dt"] = datetime.now().strftime("%Y-%m-%d")

    final_columns = [
        "order_id",
        "customer_id",
        "customer_unique_id",
        "customer_city",
        "customer_state",
        "order_status",
        "order_purchase_timestamp",
        "purchase_date",
        "purchase_month",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "order_item_count",
        "product_count",
        "seller_count",
        "total_product_amount",
        "total_freight_amount",
        "total_payment_amount",
        "payment_type_count",
        "main_payment_type",
        "max_payment_installments",
        "average_review_score",
        "review_count",
        "has_review_comment",
        "delivery_days",
        "estimated_delivery_days",
        "delivery_delay_days",
        "is_delivered",
        "is_late_delivery",
        "dwd_loaded_at",
        "dt",
    ]

    dwd = dwd[final_columns]

    return dwd


def generate_report(dwd: pd.DataFrame) -> None:
    """
    Generate DWD table report.
    """
    report = {
        "table_name": "dwd_order_detail",
        "row_count": len(dwd),
        "unique_order_count": dwd["order_id"].nunique(),
        "unique_customer_count": dwd["customer_unique_id"].nunique(),
        "total_payment_amount": round(dwd["total_payment_amount"].sum(), 2),
        "total_product_amount": round(dwd["total_product_amount"].sum(), 2),
        "delivered_order_count": int(dwd["is_delivered"].sum()),
        "late_delivery_order_count": int(dwd["is_late_delivery"].sum()),
        "average_review_score": round(dwd["average_review_score"].mean(), 2),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    report_df = pd.DataFrame([report])
    report_path = DOCS_DIR / "dwd_order_detail_report.csv"
    report_df.to_csv(report_path, index=False, encoding="utf-8-sig")

    column_profile = []

    for col in dwd.columns:
        column_profile.append(
            {
                "table_name": "dwd_order_detail",
                "column_name": col,
                "dtype": str(dwd[col].dtype),
                "missing_count": int(dwd[col].isna().sum()),
                "missing_rate": round(dwd[col].isna().sum() / len(dwd), 4),
                "unique_count": int(dwd[col].nunique(dropna=True)),
            }
        )

    column_profile_df = pd.DataFrame(column_profile)
    column_profile_path = DOCS_DIR / "dwd_order_detail_column_profile.csv"
    column_profile_df.to_csv(column_profile_path, index=False, encoding="utf-8-sig")

    print(f"[OK] DWD report generated: {report_path}")
    print(f"[OK] DWD column profile generated: {column_profile_path}")


def main() -> None:
    print("[INFO] Building dwd_order_detail ...")

    dwd = build_dwd_order_detail()

    output_path = DWD_DIR / "dwd_order_detail.csv"
    dwd.to_csv(output_path, index=False, encoding="utf-8-sig")

    generate_report(dwd)

    print(f"[OK] DWD table generated: {output_path}")
    print(f"[DONE] dwd_order_detail row count: {len(dwd)}")


if __name__ == "__main__":
    main()