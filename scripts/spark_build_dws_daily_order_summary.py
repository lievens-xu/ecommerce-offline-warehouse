from pathlib import Path
from datetime import datetime
import sys
import os

import pandas as pd
from pyspark.sql import SparkSession


ROOT_DIR = Path(__file__).resolve().parents[1]
DWD_DIR = ROOT_DIR / "data" / "dwd"
DWS_DIR = ROOT_DIR / "data" / "dws"
DOCS_DIR = ROOT_DIR / "docs"

DWS_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)


DWD_ORDER_DETAIL_FILE = DWD_DIR / "dwd_order_detail_spark.csv"
SPARK_OUTPUT_FILE = DWS_DIR / "dws_daily_order_summary_spark.csv"
PANDAS_DWS_FILE = DWS_DIR / "dws_daily_order_summary.csv"


def create_spark_session() -> SparkSession:
    """
    Create a local Spark session for Spark SQL processing.
    """
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

    spark = (
        SparkSession.builder
        .appName("EcommerceOfflineWarehouseSparkSQL")
        .master("local[*]")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")
    return spark


def validate_input_file() -> None:
    """
    Validate whether the Spark DWD input file exists.
    """
    if not DWD_ORDER_DETAIL_FILE.exists():
        raise FileNotFoundError(
            f"Spark DWD input file not found: {DWD_ORDER_DETAIL_FILE}. "
            "Please run scripts/spark_build_dwd_order_detail.py first."
        )


def build_dws_with_spark_sql(spark: SparkSession):
    """
    Build DWS daily order summary using Spark SQL.
    """
    print(f"[INFO] Reading DWD file: {DWD_ORDER_DETAIL_FILE}")

    dwd_df = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .csv(str(DWD_ORDER_DETAIL_FILE))
    )

    dwd_df.createOrReplaceTempView("dwd_order_detail")

    print("[INFO] Temporary view created: dwd_order_detail")
    print("[INFO] Running Spark SQL for DWS aggregation ...")

    dws_df = spark.sql("""
        WITH prepared AS (
            SELECT
                TO_DATE(purchase_date) AS purchase_date,
                order_id,
                customer_unique_id,
                LOWER(COALESCE(order_status, '')) AS order_status,

                COALESCE(CAST(total_payment_amount AS DOUBLE), 0.0) AS total_payment_amount,
                COALESCE(CAST(total_product_amount AS DOUBLE), 0.0) AS total_product_amount,
                COALESCE(CAST(total_freight_amount AS DOUBLE), 0.0) AS total_freight_amount,

                CAST(average_review_score AS DOUBLE) AS average_review_score,
                COALESCE(CAST(review_count AS INT), 0) AS review_count,
                COALESCE(CAST(has_review_comment AS INT), 0) AS has_review_comment,
                COALESCE(CAST(is_delivered AS INT), 0) AS is_delivered,
                COALESCE(CAST(is_late_delivery AS INT), 0) AS is_late_delivery
            FROM dwd_order_detail
            WHERE purchase_date IS NOT NULL
        ),

        flagged AS (
            SELECT
                *,
                CASE
                    WHEN order_status NOT IN ('canceled', 'unavailable') THEN 1
                    ELSE 0
                END AS is_valid_order,

                CASE
                    WHEN total_payment_amount > 0 THEN 1
                    ELSE 0
                END AS is_paid_order,

                CASE
                    WHEN review_count > 0 THEN 1
                    ELSE 0
                END AS has_review
            FROM prepared
        ),

        daily AS (
            SELECT
                purchase_date,

                COUNT(DISTINCT order_id) AS order_count,
                SUM(is_valid_order) AS valid_order_count,
                SUM(is_paid_order) AS paid_order_count,
                COUNT(DISTINCT customer_unique_id) AS unique_customer_count,

                SUM(is_delivered) AS delivered_order_count,
                SUM(is_late_delivery) AS late_delivery_order_count,

                SUM(has_review) AS review_order_count,
                SUM(has_review_comment) AS review_comment_order_count,

                SUM(total_payment_amount) AS total_payment_amount,
                SUM(total_product_amount) AS total_product_amount,
                SUM(total_freight_amount) AS total_freight_amount,
                AVG(average_review_score) AS average_review_score
            FROM flagged
            GROUP BY purchase_date
        )

        SELECT
            DATE_FORMAT(purchase_date, 'yyyy-MM-dd') AS purchase_date,

            CAST(order_count AS BIGINT) AS order_count,
            CAST(valid_order_count AS BIGINT) AS valid_order_count,
            CAST(paid_order_count AS BIGINT) AS paid_order_count,
            CAST(unique_customer_count AS BIGINT) AS unique_customer_count,

            CAST(delivered_order_count AS BIGINT) AS delivered_order_count,
            CAST(late_delivery_order_count AS BIGINT) AS late_delivery_order_count,

            ROUND(
                CASE WHEN order_count = 0 THEN 0
                     ELSE delivered_order_count / order_count
                END, 4
            ) AS delivery_rate,

            ROUND(
                CASE WHEN delivered_order_count = 0 THEN 0
                     ELSE late_delivery_order_count / delivered_order_count
                END, 4
            ) AS late_delivery_rate,

            CAST(review_order_count AS BIGINT) AS review_order_count,
            CAST(review_comment_order_count AS BIGINT) AS review_comment_order_count,

            ROUND(
                CASE WHEN order_count = 0 THEN 0
                     ELSE review_order_count / order_count
                END, 4
            ) AS review_rate,

            ROUND(
                CASE WHEN review_order_count = 0 THEN 0
                     ELSE review_comment_order_count / review_order_count
                END, 4
            ) AS review_comment_rate,

            ROUND(total_payment_amount, 4) AS total_payment_amount,
            ROUND(total_product_amount, 4) AS total_product_amount,
            ROUND(total_freight_amount, 4) AS total_freight_amount,

            ROUND(
                CASE WHEN order_count = 0 THEN 0
                     ELSE total_payment_amount / order_count
                END, 4
            ) AS aov,

            ROUND(
                CASE WHEN order_count = 0 THEN 0
                     ELSE total_product_amount / order_count
                END, 4
            ) AS avg_product_amount_per_order,

            ROUND(
                CASE WHEN order_count = 0 THEN 0
                     ELSE total_freight_amount / order_count
                END, 4
            ) AS avg_freight_amount_per_order,

            ROUND(average_review_score, 4) AS average_review_score,

            DATE_FORMAT(CURRENT_TIMESTAMP(), 'yyyy-MM-dd HH:mm:ss') AS dws_loaded_at,
            DATE_FORMAT(CURRENT_DATE(), 'yyyy-MM-dd') AS dt
        FROM daily
        ORDER BY purchase_date
    """)

    return dws_df


def save_spark_result_to_csv(dws_df) -> pd.DataFrame:
    """
    Convert Spark result to Pandas and save as a single CSV file.

    The DWS daily table is small, so converting it to Pandas is acceptable
    for portfolio and local development usage.
    """
    print("[INFO] Converting Spark result to Pandas for single CSV output ...")

    dws_pd = dws_df.toPandas()
    dws_pd.to_csv(SPARK_OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"[OK] Spark DWS CSV generated: {SPARK_OUTPUT_FILE}")
    return dws_pd


def generate_spark_report(dws_pd: pd.DataFrame) -> None:
    """
    Generate report for Spark SQL DWS result.
    """
    report = {
        "table_name": "dws_daily_order_summary_spark",
        "row_count": len(dws_pd),
        "start_date": dws_pd["purchase_date"].min(),
        "end_date": dws_pd["purchase_date"].max(),
        "total_order_count": int(dws_pd["order_count"].sum()),
        "total_valid_order_count": int(dws_pd["valid_order_count"].sum()),
        "total_payment_amount": round(float(dws_pd["total_payment_amount"].sum()), 2),
        "overall_aov": round(
            float(dws_pd["total_payment_amount"].sum()) / float(dws_pd["order_count"].sum()),
            4,
        )
        if float(dws_pd["order_count"].sum()) != 0
        else 0,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "engine": "Spark SQL",
    }

    report_df = pd.DataFrame([report])
    report_path = DOCS_DIR / "spark_dws_daily_order_summary_report.csv"
    report_df.to_csv(report_path, index=False, encoding="utf-8-sig")

    print(f"[OK] Spark DWS report generated: {report_path}")


def generate_comparison_report(spark_dws: pd.DataFrame) -> None:
    """
    Compare Spark SQL DWS output with the existing Pandas DWS output.
    """
    if not PANDAS_DWS_FILE.exists():
        print("[WARN] Pandas DWS output not found. Comparison report skipped.")
        return

    pandas_dws = pd.read_csv(PANDAS_DWS_FILE, low_memory=False)

    comparison_items = []

    def add_comparison(metric_name, pandas_value, spark_value, tolerance=0.0001):
        if isinstance(pandas_value, float) or isinstance(spark_value, float):
            diff = abs(float(pandas_value) - float(spark_value))
            status = "PASS" if diff <= tolerance else "FAIL"
        else:
            diff = pandas_value - spark_value
            status = "PASS" if pandas_value == spark_value else "FAIL"

        comparison_items.append(
            {
                "metric_name": metric_name,
                "pandas_value": pandas_value,
                "spark_sql_value": spark_value,
                "difference": diff,
                "status": status,
            }
        )

    add_comparison(
        "row_count",
        len(pandas_dws),
        len(spark_dws),
        tolerance=0,
    )

    add_comparison(
        "total_order_count",
        int(pd.to_numeric(pandas_dws["order_count"], errors="coerce").fillna(0).sum()),
        int(pd.to_numeric(spark_dws["order_count"], errors="coerce").fillna(0).sum()),
        tolerance=0,
    )

    add_comparison(
        "total_payment_amount",
        round(float(pd.to_numeric(pandas_dws["total_payment_amount"], errors="coerce").fillna(0).sum()), 2),
        round(float(pd.to_numeric(spark_dws["total_payment_amount"], errors="coerce").fillna(0).sum()), 2),
        tolerance=0.01,
    )

    add_comparison(
        "total_product_amount",
        round(float(pd.to_numeric(pandas_dws["total_product_amount"], errors="coerce").fillna(0).sum()), 2),
        round(float(pd.to_numeric(spark_dws["total_product_amount"], errors="coerce").fillna(0).sum()), 2),
        tolerance=0.01,
    )

    comparison_df = pd.DataFrame(comparison_items)
    comparison_path = DOCS_DIR / "spark_dws_comparison_report.csv"
    comparison_df.to_csv(comparison_path, index=False, encoding="utf-8-sig")

    print(f"[OK] Spark vs Pandas comparison report generated: {comparison_path}")

    failed_count = int((comparison_df["status"] == "FAIL").sum())
    if failed_count > 0:
        print("[WARN] Some comparison checks failed. Please inspect the comparison report.")
    else:
        print("[DONE] Spark SQL result is consistent with Pandas DWS output.")


def main() -> None:
    print("[INFO] Building DWS daily order summary with Spark SQL ...")

    validate_input_file()

    spark = create_spark_session()

    try:
        dws_df = build_dws_with_spark_sql(spark)
        spark_dws = save_spark_result_to_csv(dws_df)
        generate_spark_report(spark_dws)
        generate_comparison_report(spark_dws)

        print("[DONE] Spark SQL DWS building completed successfully.")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()