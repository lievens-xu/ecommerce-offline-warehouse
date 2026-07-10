"""
Build ADS geographic (state-level) summary with Spark SQL.

使用 Spark SQL 构建 ADS 地域（州级）汇总表。

Spark SQL counterpart of scripts/build_ads_geo_state_summary.py. Reads the Spark
DWD output, aggregates by customer state, and compares against the Pandas output.

scripts/build_ads_geo_state_summary.py 的 Spark SQL 版本：读取 Spark DWD 产出，
按客户所在州汇总，最后与 Pandas 版对比。
"""

import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from pyspark.sql import SparkSession

ROOT_DIR = Path(__file__).resolve().parents[1]
DWD_DIR = ROOT_DIR / "data" / "dwd"
ADS_DIR = ROOT_DIR / "data" / "ads"
DOCS_DIR = ROOT_DIR / "docs"
ADS_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

SPARK_DWD_FILE = DWD_DIR / "dwd_order_detail_spark.csv"
FALLBACK_DWD_FILE = DWD_DIR / "dwd_order_detail.csv"
SPARK_OUTPUT_FILE = ADS_DIR / "ads_geo_state_summary_spark.csv"
PANDAS_OUTPUT_FILE = ADS_DIR / "ads_geo_state_summary.csv"


def create_spark_session() -> SparkSession:
    """Create a local Spark session. 创建本地 Spark 会话。"""
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
    spark = (
        SparkSession.builder.appName("EcommerceWarehouseSparkGeo")
        .master("local[*]")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark


def resolve_input() -> Path:
    """Prefer the Spark DWD; fall back to the Pandas DWD. 优先 Spark DWD，回退 Pandas DWD。"""
    if SPARK_DWD_FILE.exists():
        return SPARK_DWD_FILE
    if FALLBACK_DWD_FILE.exists():
        print(f"[WARN] Spark DWD not found, using Pandas DWD: {FALLBACK_DWD_FILE}")
        return FALLBACK_DWD_FILE
    raise FileNotFoundError(
        "No DWD input found. Run scripts/spark_build_dwd_order_detail.py or "
        "scripts/build_dwd_order_detail.py first."
    )


def build_geo_with_spark_sql(spark: SparkSession, input_file: Path):
    """Build the state-level summary via Spark SQL. 通过 Spark SQL 构建州级汇总。"""
    print(f"[INFO] Reading DWD file: {input_file}")
    dwd = (
        spark.read.option("header", "true").option("inferSchema", "false").csv(str(input_file))
    )
    dwd.createOrReplaceTempView("dwd_order_detail")

    return spark.sql(
        """
        WITH valid_orders AS (
            SELECT
                customer_state,
                order_id,
                customer_unique_id,
                COALESCE(TRY_CAST(total_payment_amount AS DOUBLE), 0.0) AS amt,
                TRY_CAST(delivery_days AS DOUBLE) AS delivery_days,
                TRY_CAST(average_review_score AS DOUBLE) AS review_score,
                COALESCE(TRY_CAST(is_delivered AS INT), 0) AS is_delivered,
                COALESCE(TRY_CAST(is_late_delivery AS INT), 0) AS is_late_delivery
            FROM dwd_order_detail
            WHERE customer_state IS NOT NULL
              AND order_status NOT IN ('canceled', 'unavailable')
        ),
        state_agg AS (
            SELECT
                customer_state,
                COUNT(DISTINCT order_id) AS order_count,
                COUNT(DISTINCT customer_unique_id) AS customer_count,
                ROUND(SUM(amt), 2) AS gmv,
                SUM(is_delivered) AS delivered_count,
                SUM(is_late_delivery) AS late_delivered_count,
                ROUND(AVG(delivery_days), 2) AS avg_delivery_days,
                ROUND(AVG(review_score), 2) AS avg_review_score
            FROM valid_orders
            GROUP BY customer_state
        ),
        enriched AS (
            SELECT
                *,
                ROUND(gmv / NULLIF(order_count, 0), 2) AS aov,
                ROUND(delivered_count / NULLIF(order_count, 0), 4) AS delivery_rate,
                ROUND(late_delivered_count / NULLIF(delivered_count, 0), 4) AS late_delivery_rate,
                ROW_NUMBER() OVER (ORDER BY gmv DESC) AS gmv_rank,
                ROUND(gmv / SUM(gmv) OVER () * 100, 2) AS gmv_share_pct
            FROM state_agg
        )
        SELECT
            gmv_rank,
            customer_state,
            gmv,
            gmv_share_pct,
            order_count,
            customer_count,
            aov,
            delivery_rate,
            late_delivery_rate,
            avg_delivery_days,
            avg_review_score,
            DATE_FORMAT(CURRENT_TIMESTAMP(), 'yyyy-MM-dd HH:mm:ss') AS ads_loaded_at,
            DATE_FORMAT(CURRENT_DATE(), 'yyyy-MM-dd') AS dt
        FROM enriched
        ORDER BY gmv_rank
        """
    )


def generate_comparison(spark_geo: pd.DataFrame) -> None:
    """Compare Spark geo aggregates against Pandas. 与 Pandas 版对比。"""
    if not PANDAS_OUTPUT_FILE.exists():
        print(f"[WARN] Pandas output not found: {PANDAS_OUTPUT_FILE}. Comparison skipped.")
        return

    pandas_geo = pd.read_csv(PANDAS_OUTPUT_FILE, low_memory=False)
    checks = []

    def add(metric, p_val, s_val, tol=0.01):
        same = str(p_val) == str(s_val) if isinstance(p_val, str) else abs(float(p_val) - float(s_val)) <= tol
        checks.append({
            "metric_name": metric,
            "pandas_value": p_val,
            "spark_sql_value": s_val,
            "status": "PASS" if same else "FAIL",
        })

    add("state_count", len(pandas_geo), len(spark_geo), tol=0)
    add("total_gmv", round(pandas_geo["gmv"].sum(), 2), round(spark_geo["gmv"].sum(), 2), tol=1.0)
    add("top_state",
        pandas_geo.sort_values("gmv_rank").iloc[0]["customer_state"],
        spark_geo.sort_values("gmv_rank").iloc[0]["customer_state"])
    add("total_order_count", int(pandas_geo["order_count"].sum()),
        int(spark_geo["order_count"].sum()), tol=0)

    df = pd.DataFrame(checks)
    path = DOCS_DIR / "spark_geo_comparison_report.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    failed = int((df["status"] == "FAIL").sum())
    print(f"[OK] Comparison report: {path}")
    print(f"[COMPARISON] Total: {len(checks)} | Passed: {len(checks)-failed} | Failed: {failed}")


def main() -> None:
    print("=" * 60)
    print("[INFO] Building ADS geo state summary with Spark SQL ...")
    print("=" * 60)
    input_file = resolve_input()
    spark = create_spark_session()
    try:
        geo_df = build_geo_with_spark_sql(spark, input_file)
        geo_pd = geo_df.toPandas()
        geo_pd.to_csv(SPARK_OUTPUT_FILE, index=False, encoding="utf-8-sig")
        print(f"[OK] Spark geo CSV generated: {SPARK_OUTPUT_FILE} ({len(geo_pd)} rows)")

        report = pd.DataFrame([{
            "table_name": "ads_geo_state_summary_spark",
            "state_count": len(geo_pd),
            "total_gmv": round(float(geo_pd["gmv"].sum()), 2),
            "top_state": geo_pd.sort_values("gmv_rank").iloc[0]["customer_state"],
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "engine": "Spark SQL",
        }])
        report.to_csv(DOCS_DIR / "spark_geo_report.csv", index=False, encoding="utf-8-sig")

        generate_comparison(geo_pd)
        print("[DONE] Spark geo building completed.")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
