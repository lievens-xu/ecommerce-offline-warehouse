from pathlib import Path
from datetime import datetime
import sys
import os

import pandas as pd
from pyspark.sql import SparkSession


ROOT_DIR = Path(__file__).resolve().parents[1]
DWS_DIR = ROOT_DIR / "data" / "dws"
ADS_DIR = ROOT_DIR / "data" / "ads"
DOCS_DIR = ROOT_DIR / "docs"

ADS_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)


SPARK_DWS_FILE = DWS_DIR / "dws_daily_order_summary_spark.csv"
SPARK_OUTPUT_FILE = ADS_DIR / "ads_daily_business_overview_spark.csv"
PANDAS_ADS_FILE = ADS_DIR / "ads_daily_business_overview.csv"


def create_spark_session() -> SparkSession:
    """
    Create a local Spark session for Spark SQL processing.
    """
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

    spark = (
        SparkSession.builder
        .appName("EcommerceOfflineWarehouseSparkADS")
        .master("local[*]")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")
    return spark


def validate_input_file() -> None:
    """
    Validate whether the Spark DWS input file exists.
    """
    if not SPARK_DWS_FILE.exists():
        raise FileNotFoundError(
            f"Spark DWS input file not found: {SPARK_DWS_FILE}. "
            "Please run scripts/spark_build_dws_daily_order_summary.py first."
        )


def build_ads_with_spark_sql(spark: SparkSession):
    """
    Build ADS daily business overview using Spark SQL.

    The logic follows the same steps as the Pandas version:
    1. Read Spark DWS CSV
    2. Register as temporary view
    3. Rename DWS fields to ADS field names
    4. Calculate valid_order_rate and paid_order_rate
    5. Calculate 7-day moving averages using window functions
    6. Calculate cumulative metrics using window functions
    7. Calculate day-over-day changes using LAG()
    8. Add technical fields
    """
    print("[INFO] Building ADS daily business overview with Spark SQL ...")

    # Read Spark DWS CSV with inferSchema=False for safe reading
    print(f"[INFO] Reading Spark DWS file: {SPARK_DWS_FILE}")
    dws_df = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "false")
        .csv(str(SPARK_DWS_FILE))
    )

    dws_df.createOrReplaceTempView("dws_daily_order_summary")
    print("[OK] Temporary view created: dws_daily_order_summary")

    print("[INFO] Running Spark SQL for ADS transformation ...")

    ads_df = spark.sql("""
        WITH prepared AS (
            SELECT
                purchase_date AS stat_date,
                DATE_FORMAT(TO_DATE(purchase_date), 'yyyy-MM') AS stat_month,

                COALESCE(TRY_CAST(order_count AS LONG), 0) AS daily_order_count,
                COALESCE(TRY_CAST(valid_order_count AS LONG), 0) AS daily_valid_order_count,
                COALESCE(TRY_CAST(paid_order_count AS LONG), 0) AS daily_paid_order_count,
                COALESCE(TRY_CAST(unique_customer_count AS LONG), 0) AS daily_unique_customer_count,

                COALESCE(TRY_CAST(total_payment_amount AS DOUBLE), 0.0) AS daily_gmv,
                COALESCE(TRY_CAST(total_product_amount AS DOUBLE), 0.0) AS daily_product_amount,
                COALESCE(TRY_CAST(total_freight_amount AS DOUBLE), 0.0) AS daily_freight_amount,
                COALESCE(TRY_CAST(aov AS DOUBLE), 0.0) AS daily_aov,

                COALESCE(TRY_CAST(delivery_rate AS DOUBLE), 0.0) AS daily_delivery_rate,
                COALESCE(TRY_CAST(late_delivery_rate AS DOUBLE), 0.0) AS daily_late_delivery_rate,
                COALESCE(TRY_CAST(review_rate AS DOUBLE), 0.0) AS daily_review_rate,
                COALESCE(TRY_CAST(review_comment_rate AS DOUBLE), 0.0) AS daily_review_comment_rate,
                COALESCE(TRY_CAST(average_review_score AS DOUBLE), 0.0) AS daily_average_review_score
            FROM dws_daily_order_summary
            WHERE purchase_date IS NOT NULL
        ),

        with_rates AS (
            SELECT
                *,
                -- valid_order_rate: valid_order_count / order_count
                ROUND(
                    CASE WHEN daily_order_count = 0 THEN 0.0
                         ELSE daily_valid_order_count / daily_order_count
                    END, 4
                ) AS valid_order_rate,

                -- paid_order_rate: paid_order_count / order_count
                ROUND(
                    CASE WHEN daily_order_count = 0 THEN 0.0
                         ELSE daily_paid_order_count / daily_order_count
                    END, 4
                ) AS paid_order_rate
            FROM prepared
        ),

        with_window_metrics AS (
            SELECT
                *,
                -- 7-day moving averages
                ROUND(
                    AVG(daily_gmv) OVER (
                        ORDER BY stat_date
                        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
                    ), 4
                ) AS gmv_7d_moving_avg,

                ROUND(
                    AVG(daily_order_count) OVER (
                        ORDER BY stat_date
                        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
                    ), 4
                ) AS order_count_7d_moving_avg,

                ROUND(
                    AVG(daily_aov) OVER (
                        ORDER BY stat_date
                        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
                    ), 4
                ) AS aov_7d_moving_avg,

                -- Cumulative metrics
                ROUND(
                    SUM(daily_gmv) OVER (
                        ORDER BY stat_date
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    ), 4
                ) AS cumulative_gmv,

                ROUND(
                    SUM(daily_order_count) OVER (
                        ORDER BY stat_date
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    ), 4
                ) AS cumulative_order_count,

                ROUND(
                    SUM(daily_unique_customer_count) OVER (
                        ORDER BY stat_date
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    ), 4
                ) AS cumulative_customer_count,

                -- Day-over-day changes (absolute)
                ROUND(
                    daily_gmv - LAG(daily_gmv) OVER (ORDER BY stat_date), 4
                ) AS gmv_day_over_day_change,

                ROUND(
                    daily_order_count - LAG(daily_order_count) OVER (ORDER BY stat_date), 4
                ) AS order_count_day_over_day_change
            FROM with_rates
        ),

        with_rates_final AS (
            SELECT
                *,
                -- Day-over-day rates (percentage change)
                ROUND(
                    CASE
                        WHEN LAG(daily_gmv) OVER (ORDER BY stat_date) IS NULL THEN 0.0
                        WHEN LAG(daily_gmv) OVER (ORDER BY stat_date) = 0 THEN 0.0
                        ELSE (daily_gmv - LAG(daily_gmv) OVER (ORDER BY stat_date)) / LAG(daily_gmv) OVER (ORDER BY stat_date)
                    END, 4
                ) AS gmv_day_over_day_rate,

                ROUND(
                    CASE
                        WHEN LAG(daily_order_count) OVER (ORDER BY stat_date) IS NULL THEN 0.0
                        WHEN LAG(daily_order_count) OVER (ORDER BY stat_date) = 0 THEN 0.0
                        ELSE (daily_order_count - LAG(daily_order_count) OVER (ORDER BY stat_date)) / LAG(daily_order_count) OVER (ORDER BY stat_date)
                    END, 4
                ) AS order_count_day_over_day_rate
            FROM with_window_metrics
        )

        SELECT
            stat_date,
            stat_month,
            daily_order_count,
            daily_valid_order_count,
            daily_paid_order_count,
            daily_unique_customer_count,
            daily_gmv,
            daily_product_amount,
            daily_freight_amount,
            daily_aov,
            daily_delivery_rate,
            daily_late_delivery_rate,
            daily_review_rate,
            daily_review_comment_rate,
            daily_average_review_score,
            valid_order_rate,
            paid_order_rate,
            gmv_7d_moving_avg,
            order_count_7d_moving_avg,
            aov_7d_moving_avg,
            cumulative_gmv,
            cumulative_order_count,
            cumulative_customer_count,

            -- Fill NULL day-over-day changes with 0
            COALESCE(gmv_day_over_day_change, 0.0) AS gmv_day_over_day_change,
            COALESCE(order_count_day_over_day_change, 0.0) AS order_count_day_over_day_change,
            COALESCE(gmv_day_over_day_rate, 0.0) AS gmv_day_over_day_rate,
            COALESCE(order_count_day_over_day_rate, 0.0) AS order_count_day_over_day_rate,

            DATE_FORMAT(CURRENT_TIMESTAMP(), 'yyyy-MM-dd HH:mm:ss') AS ads_loaded_at,
            DATE_FORMAT(CURRENT_DATE(), 'yyyy-MM-dd') AS dt
        FROM with_rates_final
        ORDER BY stat_date
    """)

    return ads_df


def save_spark_result_to_csv(ads_df) -> pd.DataFrame:
    """
    Convert Spark result to Pandas and save as a single CSV file.

    The ADS daily table is small, so converting it to Pandas is acceptable
    for portfolio and local development usage.
    """
    print("[INFO] Converting Spark result to Pandas for single CSV output ...")

    ads_pd = ads_df.toPandas()
    ads_pd.to_csv(SPARK_OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"[OK] Spark ADS CSV generated: {SPARK_OUTPUT_FILE}")
    print(f"[INFO] Spark ADS row count: {len(ads_pd)}")

    return ads_pd


def generate_spark_report(ads_pd: pd.DataFrame) -> None:
    """
    Generate report for Spark SQL ADS result.
    """
    print("[INFO] Generating Spark ADS report ...")

    report = {
        "table_name": "ads_daily_business_overview_spark",
        "row_count": len(ads_pd),
        "start_date": ads_pd["stat_date"].min(),
        "end_date": ads_pd["stat_date"].max(),
        "total_order_count": int(ads_pd["daily_order_count"].sum()),
        "total_gmv": round(float(ads_pd["daily_gmv"].sum()), 2),
        "average_daily_gmv": round(float(ads_pd["daily_gmv"].mean()), 4),
        "average_daily_order_count": round(float(ads_pd["daily_order_count"].mean()), 4),
        "overall_aov": round(
            float(ads_pd["daily_gmv"].sum()) / float(ads_pd["daily_order_count"].sum()),
            4
        ) if float(ads_pd["daily_order_count"].sum()) != 0 else 0,
        "latest_stat_date": ads_pd["stat_date"].max(),
        "latest_daily_gmv": round(
            float(ads_pd.loc[ads_pd["stat_date"] == ads_pd["stat_date"].max(), "daily_gmv"].sum()),
            4
        ),
        "latest_daily_order_count": int(
            ads_pd.loc[ads_pd["stat_date"] == ads_pd["stat_date"].max(), "daily_order_count"].sum()
        ),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "engine": "Spark SQL",
    }

    report_df = pd.DataFrame([report])
    report_path = DOCS_DIR / "spark_ads_daily_business_overview_report.csv"
    report_df.to_csv(report_path, index=False, encoding="utf-8-sig")

    print(f"[OK] Spark ADS report generated: {report_path}")


def generate_comparison_report(spark_ads: pd.DataFrame) -> None:
    """
    Compare Spark SQL ADS output with the existing Pandas ADS output.
    """
    print("[INFO] Generating Spark vs Pandas comparison report ...")

    if not PANDAS_ADS_FILE.exists():
        print(f"[WARN] Pandas ADS output not found: {PANDAS_ADS_FILE}")
        print("[WARN] Comparison report skipped. Please run scripts/build_ads_daily_business_overview.py first.")
        return

    pandas_ads = pd.read_csv(PANDAS_ADS_FILE, low_memory=False)

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
        len(pandas_ads),
        len(spark_ads),
        tolerance=0
    )

    # Total order count comparison
    add_comparison(
        "total_order_count",
        int(pandas_ads["daily_order_count"].sum()),
        int(spark_ads["daily_order_count"].sum()),
        tolerance=0
    )

    # Total GMV comparison
    add_comparison(
        "total_gmv",
        round(float(pandas_ads["daily_gmv"].sum()), 2),
        round(float(spark_ads["daily_gmv"].sum()), 2),
        tolerance=0.01
    )

    # Average daily GMV comparison
    add_comparison(
        "average_daily_gmv",
        round(float(pandas_ads["daily_gmv"].mean()), 4),
        round(float(spark_ads["daily_gmv"].mean()), 4),
        tolerance=0.05
    )

    # Overall AOV comparison
    pandas_total_gmv = float(pandas_ads["daily_gmv"].sum())
    pandas_total_orders = float(pandas_ads["daily_order_count"].sum())
    pandas_overall_aov = round(pandas_total_gmv / pandas_total_orders, 4) if pandas_total_orders != 0 else 0

    spark_total_gmv = float(spark_ads["daily_gmv"].sum())
    spark_total_orders = float(spark_ads["daily_order_count"].sum())
    spark_overall_aov = round(spark_total_gmv / spark_total_orders, 4) if spark_total_orders != 0 else 0

    add_comparison(
        "overall_aov",
        pandas_overall_aov,
        spark_overall_aov,
        tolerance=0.05
    )

    # Latest daily GMV comparison
    pandas_latest_date = pandas_ads["stat_date"].max()
    spark_latest_date = spark_ads["stat_date"].max()

    add_comparison(
        "latest_daily_gmv",
        round(float(pandas_ads.loc[pandas_ads["stat_date"] == pandas_latest_date, "daily_gmv"].sum()), 4),
        round(float(spark_ads.loc[spark_ads["stat_date"] == spark_latest_date, "daily_gmv"].sum()), 4),
        tolerance=0.01
    )

    # Latest daily order count comparison
    add_comparison(
        "latest_daily_order_count",
        int(pandas_ads.loc[pandas_ads["stat_date"] == pandas_latest_date, "daily_order_count"].sum()),
        int(spark_ads.loc[spark_ads["stat_date"] == spark_latest_date, "daily_order_count"].sum()),
        tolerance=0
    )

    comparison_df = pd.DataFrame(comparison_items)
    comparison_path = DOCS_DIR / "spark_ads_comparison_report.csv"
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
        print("[DONE] Spark ADS result is consistent with Pandas ADS output.")


def main() -> None:
    print("=" * 60)
    print("[INFO] Building ADS daily business overview with Spark SQL ...")
    print("=" * 60)

    validate_input_file()

    spark = create_spark_session()

    try:
        ads_df = build_ads_with_spark_sql(spark)
        spark_ads = save_spark_result_to_csv(ads_df)
        generate_spark_report(spark_ads)
        generate_comparison_report(spark_ads)

        print("=" * 60)
        print("[DONE] Spark SQL ADS building completed successfully.")
        print("=" * 60)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()