from pathlib import Path
from datetime import datetime
import sys
import os

import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, coalesce, count, countDistinct, sum as spark_sum, max as spark_max, avg as spark_avg, round as spark_round, to_date, date_format, current_timestamp, current_date, isnan, isnull


ROOT_DIR = Path(__file__).resolve().parents[1]
ODS_DIR = ROOT_DIR / "data" / "ods"
DWD_DIR = ROOT_DIR / "data" / "dwd"
DOCS_DIR = ROOT_DIR / "docs"

DWD_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)


SPARK_OUTPUT_FILE = DWD_DIR / "dwd_order_detail_spark.csv"
PANDAS_DWD_FILE = DWD_DIR / "dwd_order_detail.csv"


def create_spark_session() -> SparkSession:
    """
    Create a local Spark session for Spark SQL processing.
    """
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

    spark = (
        SparkSession.builder
        .appName("EcommerceOfflineWarehouseSparkDWD")
        .master("local[*]")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")
    return spark


def validate_ods_files() -> None:
    """
    Validate whether required ODS input files exist.
    """
    required_files = [
        "ods_orders.csv",
        "ods_customers.csv",
        "ods_order_items.csv",
        "ods_order_payments.csv",
        "ods_order_reviews.csv",
    ]

    for file_name in required_files:
        file_path = ODS_DIR / file_name
        if not file_path.exists():
            raise FileNotFoundError(
                f"ODS file not found: {file_path}. "
                "Please run scripts/load_raw_to_ods.py first."
            )


def load_ods_tables(spark: SparkSession) -> dict:
    """
    Load all required ODS tables and register as temporary views.
    """
    print("[INFO] Loading ODS tables ...")

    ods_tables = {}

    for table_name in ["orders", "customers", "order_items", "order_payments", "order_reviews"]:
        file_path = ODS_DIR / f"ods_{table_name}.csv"
        print(f"[INFO] Reading: {file_path}")

        df = (
            spark.read
            .option("header", "true")
            .option("inferSchema", "true")
            .csv(str(file_path))
        )

        view_name = f"ods_{table_name}"
        df.createOrReplaceTempView(view_name)
        ods_tables[table_name] = df
        print(f"[OK] Temporary view created: {view_name}")

    return ods_tables


def build_dwd_with_spark_sql(spark: SparkSession):
    """
    Build DWD order-level detail table using Spark SQL.

    The logic follows the same steps as the Pandas version:
    1. Aggregate order items to order level
    2. Aggregate payments to order level (including main_payment_type)
    3. Aggregate reviews to order level
    4. Join orders + customers + item_agg + payment_agg + review_agg
    5. Calculate date fields and logistics fields
    6. Add technical fields
    """
    print("[INFO] Building DWD order detail with Spark SQL ...")

    # Step 1: Aggregate order items to order level
    print("[INFO] Aggregating order items to order level ...")
    item_agg_df = spark.sql("""
        SELECT
            order_id,
            COUNT(order_item_id) AS order_item_count,
            COUNT(DISTINCT product_id) AS product_count,
            COUNT(DISTINCT seller_id) AS seller_count,
            ROUND(SUM(COALESCE(TRY_CAST(price AS DOUBLE), 0.0)), 4) AS total_product_amount,
            ROUND(SUM(COALESCE(TRY_CAST(freight_value AS DOUBLE), 0.0)), 4) AS total_freight_amount
        FROM ods_order_items
        GROUP BY order_id
    """)
    item_agg_df.createOrReplaceTempView("item_agg")
    print("[OK] Item aggregation completed.")

    # Step 2: Aggregate payments to order level with main_payment_type
    print("[INFO] Aggregating payments to order level ...")

    # First get payment type with max amount per order
    payment_type_amount_df = spark.sql("""
        SELECT
            order_id,
            payment_type,
            ROUND(SUM(COALESCE(TRY_CAST(payment_value AS DOUBLE), 0.0)), 4) AS payment_type_amount
        FROM ods_order_payments
        GROUP BY order_id, payment_type
    """)
    payment_type_amount_df.createOrReplaceTempView("payment_type_amount")

    # Get main payment type (the one with max amount)
    main_payment_type_df = spark.sql("""
        SELECT
            order_id,
            payment_type AS main_payment_type
        FROM (
            SELECT
                order_id,
                payment_type,
                payment_type_amount,
                ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY payment_type_amount DESC) AS rn
            FROM payment_type_amount
        ) t
        WHERE rn = 1
    """)
    main_payment_type_df.createOrReplaceTempView("main_payment_type")

    # Aggregate payment metrics
    payment_agg_df = spark.sql("""
        SELECT
            order_id,
            ROUND(SUM(COALESCE(TRY_CAST(payment_value AS DOUBLE), 0.0)), 4) AS total_payment_amount,
            COUNT(DISTINCT payment_type) AS payment_type_count,
            MAX(COALESCE(TRY_CAST(payment_installments AS INT), 0)) AS max_payment_installments
        FROM ods_order_payments
        GROUP BY order_id
    """)
    payment_agg_df.createOrReplaceTempView("payment_agg")
    print("[OK] Payment aggregation completed.")

    # Step 3: Aggregate reviews to order level
    print("[INFO] Aggregating reviews to order level ...")
    review_agg_df = spark.sql("""
        SELECT
            order_id,
            ROUND(AVG(TRY_CAST(review_score AS DOUBLE)), 2) AS average_review_score,
            COUNT(review_id) AS review_count,
            MAX(
                CASE
                    WHEN COALESCE(TRIM(review_comment_title), '') != ''
                         OR COALESCE(TRIM(review_comment_message), '') != ''
                    THEN 1
                    ELSE 0
                END
            ) AS has_review_comment
        FROM ods_order_reviews
        GROUP BY order_id
    """)
    review_agg_df.createOrReplaceTempView("review_agg")
    print("[OK] Review aggregation completed.")

    # Step 4: Build DWD by joining all aggregations
    print("[INFO] Joining all tables to build DWD ...")
    dwd_df = spark.sql("""
        WITH orders_prepared AS (
            SELECT
                order_id,
                customer_id,
                order_status,
                order_purchase_timestamp,
                order_approved_at,
                order_delivered_carrier_date,
                order_delivered_customer_date,
                order_estimated_delivery_date
            FROM ods_orders
        ),

        customers_prepared AS (
            SELECT
                customer_id,
                customer_unique_id,
                customer_city,
                customer_state
            FROM ods_customers
        ),

        combined AS (
            SELECT
                o.order_id,
                o.customer_id,
                c.customer_unique_id,
                c.customer_city,
                c.customer_state,
                LOWER(COALESCE(o.order_status, '')) AS order_status,
                o.order_purchase_timestamp,
                o.order_approved_at,
                o.order_delivered_carrier_date,
                o.order_delivered_customer_date,
                o.order_estimated_delivery_date,

                COALESCE(i.order_item_count, 0) AS order_item_count,
                COALESCE(i.product_count, 0) AS product_count,
                COALESCE(i.seller_count, 0) AS seller_count,
                COALESCE(i.total_product_amount, 0.0) AS total_product_amount,
                COALESCE(i.total_freight_amount, 0.0) AS total_freight_amount,

                COALESCE(p.total_payment_amount, 0.0) AS total_payment_amount,
                COALESCE(p.payment_type_count, 0) AS payment_type_count,
                COALESCE(m.main_payment_type, 'unknown') AS main_payment_type,
                COALESCE(p.max_payment_installments, 0) AS max_payment_installments,

                COALESCE(r.average_review_score, 0.0) AS average_review_score,
                COALESCE(r.review_count, 0) AS review_count,
                COALESCE(r.has_review_comment, 0) AS has_review_comment
            FROM orders_prepared o
            LEFT JOIN customers_prepared c ON o.customer_id = c.customer_id
            LEFT JOIN item_agg i ON o.order_id = i.order_id
            LEFT JOIN payment_agg p ON o.order_id = p.order_id
            LEFT JOIN main_payment_type m ON o.order_id = m.order_id
            LEFT JOIN review_agg r ON o.order_id = r.order_id
        )

        SELECT
            order_id,
            customer_id,
            customer_unique_id,
            customer_city,
            customer_state,
            order_status,
            order_purchase_timestamp,
            DATE_FORMAT(to_date(order_purchase_timestamp), 'yyyy-MM-dd') AS purchase_date,
            DATE_FORMAT(to_date(order_purchase_timestamp), 'yyyy-MM') AS purchase_month,
            order_approved_at,
            order_delivered_carrier_date,
            order_delivered_customer_date,
            order_estimated_delivery_date,
            order_item_count,
            product_count,
            seller_count,
            total_product_amount,
            total_freight_amount,
            total_payment_amount,
            payment_type_count,
            main_payment_type,
            max_payment_installments,
            average_review_score,
            review_count,
            has_review_comment,

            CASE
                WHEN order_delivered_customer_date IS NOT NULL
                     AND order_purchase_timestamp IS NOT NULL
                THEN DATEDIFF(order_delivered_customer_date, order_purchase_timestamp)
                ELSE NULL
            END AS delivery_days,

            CASE
                WHEN order_estimated_delivery_date IS NOT NULL
                     AND order_purchase_timestamp IS NOT NULL
                THEN DATEDIFF(order_estimated_delivery_date, order_purchase_timestamp)
                ELSE NULL
            END AS estimated_delivery_days,

            CASE
                WHEN order_delivered_customer_date IS NOT NULL
                     AND order_estimated_delivery_date IS NOT NULL
                THEN DATEDIFF(order_delivered_customer_date, order_estimated_delivery_date)
                ELSE NULL
            END AS delivery_delay_days,

            CASE
                WHEN order_delivered_customer_date IS NOT NULL THEN 1
                ELSE 0
            END AS is_delivered,

            CASE
                WHEN order_delivered_customer_date IS NOT NULL
                     AND order_estimated_delivery_date IS NOT NULL
                     AND DATEDIFF(order_delivered_customer_date, order_estimated_delivery_date) > 0
                THEN 1
                ELSE 0
            END AS is_late_delivery,

            DATE_FORMAT(CURRENT_TIMESTAMP(), 'yyyy-MM-dd HH:mm:ss') AS dwd_loaded_at,
            DATE_FORMAT(CURRENT_DATE(), 'yyyy-MM-dd') AS dt
        FROM combined
        ORDER BY order_id
    """)
    print("[OK] DWD join and calculation completed.")

    return dwd_df


def save_spark_result_to_csv(dwd_df) -> pd.DataFrame:
    """
    Convert Spark result to Pandas and save as a single CSV file.

    The DWD table may be large, but converting to Pandas is acceptable
    for portfolio and local development usage.
    """
    print("[INFO] Converting Spark result to Pandas for single CSV output ...")

    dwd_pd = dwd_df.toPandas()
    dwd_pd.to_csv(SPARK_OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"[OK] Spark DWD CSV generated: {SPARK_OUTPUT_FILE}")
    print(f"[INFO] Spark DWD row count: {len(dwd_pd)}")

    return dwd_pd


def generate_spark_report(dwd_pd: pd.DataFrame) -> None:
    """
    Generate report for Spark SQL DWD result.
    """
    print("[INFO] Generating Spark DWD report ...")

    report = {
        "table_name": "dwd_order_detail_spark",
        "row_count": len(dwd_pd),
        "unique_order_count": int(dwd_pd["order_id"].nunique()),
        "unique_customer_count": int(dwd_pd["customer_unique_id"].nunique()),
        "total_payment_amount": round(float(dwd_pd["total_payment_amount"].sum()), 2),
        "total_product_amount": round(float(dwd_pd["total_product_amount"].sum()), 2),
        "total_freight_amount": round(float(dwd_pd["total_freight_amount"].sum()), 2),
        "delivered_order_count": int(dwd_pd["is_delivered"].sum()),
        "late_delivery_order_count": int(dwd_pd["is_late_delivery"].sum()),
        "average_review_score": round(float(dwd_pd["average_review_score"].mean()), 2),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "engine": "Spark SQL",
    }

    report_df = pd.DataFrame([report])
    report_path = DOCS_DIR / "spark_dwd_order_detail_report.csv"
    report_df.to_csv(report_path, index=False, encoding="utf-8-sig")

    print(f"[OK] Spark DWD report generated: {report_path}")


def generate_comparison_report(spark_dwd: pd.DataFrame) -> None:
    """
    Compare Spark SQL DWD output with the existing Pandas DWD output.
    """
    print("[INFO] Generating Spark vs Pandas comparison report ...")

    if not PANDAS_DWD_FILE.exists():
        print(f"[WARN] Pandas DWD output not found: {PANDAS_DWD_FILE}")
        print("[WARN] Comparison report skipped. Please run scripts/build_dwd_order_detail.py first.")
        return

    pandas_dwd = pd.read_csv(PANDAS_DWD_FILE, low_memory=False)

    comparison_items = []

    def add_comparison(metric_name, pandas_value, spark_value, tolerance=0.01):
        """
        Add a comparison item with tolerance for floating point values.
        """
        pandas_val = float(pandas_value) if not isinstance(pandas_value, (int, float)) else pandas_value
        spark_val = float(spark_value) if not isinstance(spark_value, (int, float)) else spark_value

        diff = abs(pandas_val - spark_val)

        if diff <= tolerance:
            status = "PASS"
            message = "Values match within tolerance."
        else:
            status = "FAIL"
            message = f"Difference exceeds tolerance of {tolerance}."

        comparison_items.append({
            "metric_name": metric_name,
            "pandas_value": pandas_val,
            "spark_sql_value": spark_val,
            "difference": round(diff, 4),
            "tolerance": tolerance,
            "status": status,
            "message": message,
        })

    # Row count comparison
    add_comparison(
        "row_count",
        len(pandas_dwd),
        len(spark_dwd),
        tolerance=0
    )

    # Unique order count comparison
    add_comparison(
        "unique_order_count",
        pandas_dwd["order_id"].nunique(),
        spark_dwd["order_id"].nunique(),
        tolerance=0
    )

    # Unique customer count comparison
    add_comparison(
        "unique_customer_count",
        pandas_dwd["customer_unique_id"].nunique(),
        spark_dwd["customer_unique_id"].nunique(),
        tolerance=0
    )

    # Total payment amount comparison
    add_comparison(
        "total_payment_amount",
        round(float(pandas_dwd["total_payment_amount"].sum()), 2),
        round(float(spark_dwd["total_payment_amount"].sum()), 2),
        tolerance=0.01
    )

    # Total product amount comparison
    add_comparison(
        "total_product_amount",
        round(float(pandas_dwd["total_product_amount"].sum()), 2),
        round(float(spark_dwd["total_product_amount"].sum()), 2),
        tolerance=0.01
    )

    # Total freight amount comparison
    add_comparison(
        "total_freight_amount",
        round(float(pandas_dwd["total_freight_amount"].sum()), 2),
        round(float(spark_dwd["total_freight_amount"].sum()), 2),
        tolerance=0.01
    )

    # Delivered order count comparison
    add_comparison(
        "delivered_order_count",
        int(pandas_dwd["is_delivered"].sum()),
        int(spark_dwd["is_delivered"].sum()),
        tolerance=0
    )

    # Late delivery order count comparison
    add_comparison(
        "late_delivery_order_count",
        int(pandas_dwd["is_late_delivery"].sum()),
        int(spark_dwd["is_late_delivery"].sum()),
        tolerance=0
    )

    # Average review score comparison (use larger tolerance due to rounding effects)
    add_comparison(
        "average_review_score",
        round(float(pandas_dwd["average_review_score"].mean()), 2),
        round(float(spark_dwd["average_review_score"].mean()), 2),
        tolerance=0.05
    )

    comparison_df = pd.DataFrame(comparison_items)
    comparison_path = DOCS_DIR / "spark_dwd_comparison_report.csv"
    comparison_df.to_csv(comparison_path, index=False, encoding="utf-8-sig")

    print(f"[OK] Spark vs Pandas comparison report generated: {comparison_path}")

    # Print comparison summary
    failed_count = int((comparison_df["status"] == "FAIL").sum())

    print("=" * 60)
    print("[COMPARISON SUMMARY]")
    print(f"Total checks: {len(comparison_items)}")
    print(f"Passed: {len(comparison_items) - failed_count}")
    print(f"Failed: {failed_count}")
    print("=" * 60)

    if failed_count > 0:
        print("[WARN] Some comparison checks failed:")
        for item in comparison_items:
            if item["status"] == "FAIL":
                print(f"  - {item['metric_name']}: Pandas={item['pandas_value']}, Spark={item['spark_sql_value']}, Diff={item['difference']}")
        print("[WARN] Please inspect the comparison report for details.")
    else:
        print("[DONE] Spark DWD result is consistent with Pandas DWD output.")


def main() -> None:
    print("=" * 60)
    print("[INFO] Building DWD order detail with Spark SQL ...")
    print("=" * 60)

    validate_ods_files()

    spark = create_spark_session()

    try:
        load_ods_tables(spark)
        dwd_df = build_dwd_with_spark_sql(spark)
        spark_dwd = save_spark_result_to_csv(dwd_df)
        generate_spark_report(spark_dwd)
        generate_comparison_report(spark_dwd)

        print("=" * 60)
        print("[DONE] Spark SQL DWD building completed successfully.")
        print("=" * 60)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()