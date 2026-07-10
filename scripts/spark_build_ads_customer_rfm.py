"""
Build ADS customer RFM segmentation with Spark SQL.

使用 Spark SQL 构建 ADS 客户 RFM 分层表。

Spark SQL counterpart of scripts/build_ads_customer_rfm.py. Reads the Spark DWD
output, computes R/F/M with NTILE(5) quintiles, maps segments, and compares the
result against the Pandas RFM output.

scripts/build_ads_customer_rfm.py 的 Spark SQL 版本：读取 Spark DWD 产出，用
NTILE(5) 五分位计算 R/F/M 并映射分层，最后与 Pandas 版结果对比。
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
SPARK_OUTPUT_FILE = ADS_DIR / "ads_customer_rfm_spark.csv"
PANDAS_OUTPUT_FILE = ADS_DIR / "ads_customer_rfm.csv"


def create_spark_session() -> SparkSession:
    """Create a local Spark session. 创建本地 Spark 会话。"""
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
    spark = (
        SparkSession.builder.appName("EcommerceWarehouseSparkRFM")
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


def build_rfm_with_spark_sql(spark: SparkSession, input_file: Path):
    """Build the RFM table via Spark SQL. 通过 Spark SQL 构建 RFM 表。"""
    print(f"[INFO] Reading DWD file: {input_file}")
    dwd = (
        spark.read.option("header", "true").option("inferSchema", "false").csv(str(input_file))
    )
    dwd.createOrReplaceTempView("dwd_order_detail")

    return spark.sql(
        """
        WITH valid_orders AS (
            SELECT
                customer_unique_id,
                order_id,
                TO_TIMESTAMP(order_purchase_timestamp) AS ts,
                COALESCE(TRY_CAST(total_payment_amount AS DOUBLE), 0.0) AS amt
            FROM dwd_order_detail
            WHERE customer_unique_id IS NOT NULL
              AND order_purchase_timestamp IS NOT NULL
              AND order_status NOT IN ('canceled', 'unavailable')
        ),
        snap AS (
            SELECT DATE_ADD(TO_DATE(MAX(ts)), 1) AS snapshot_date FROM valid_orders
        ),
        rfm_base AS (
            SELECT
                v.customer_unique_id,
                DATEDIFF(s.snapshot_date, TO_DATE(MAX(v.ts))) AS recency,
                COUNT(DISTINCT v.order_id) AS frequency,
                ROUND(SUM(v.amt), 2) AS monetary
            FROM valid_orders v
            CROSS JOIN snap s
            GROUP BY v.customer_unique_id, s.snapshot_date
        ),
        scored AS (
            SELECT
                *,
                NTILE(5) OVER (ORDER BY recency DESC) AS r_score,
                NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
                NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
            FROM rfm_base
        )
        SELECT
            customer_unique_id,
            recency,
            frequency,
            monetary,
            r_score,
            f_score,
            m_score,
            (r_score + f_score + m_score) AS rfm_score,
            CONCAT(CAST(r_score AS STRING), CAST(f_score AS STRING), CAST(m_score AS STRING)) AS rfm_cell,
            CASE
                WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions / 重要价值客户'
                WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal / 忠诚客户'
                WHEN r_score >= 4 AND f_score <= 2 THEN 'Recent / 新近活跃客户'
                WHEN r_score = 3 AND f_score <= 2 THEN 'Promising / 有潜力客户'
                WHEN r_score = 2 AND f_score >= 3 THEN 'At Risk / 需挽留客户'
                WHEN r_score <= 2 AND f_score >= 4 THEN 'Cant Lose / 高价值流失预警'
                WHEN r_score = 2 AND f_score <= 2 THEN 'Hibernating / 沉睡客户'
                ELSE 'Lost / 已流失客户'
            END AS segment,
            DATE_FORMAT(CURRENT_TIMESTAMP(), 'yyyy-MM-dd HH:mm:ss') AS ads_loaded_at,
            DATE_FORMAT(CURRENT_DATE(), 'yyyy-MM-dd') AS dt
        FROM scored
        ORDER BY monetary DESC
        """
    )


def generate_comparison(spark_rfm: pd.DataFrame) -> None:
    """Compare Spark RFM aggregates against the Pandas RFM output. 与 Pandas 版对比聚合指标。"""
    if not PANDAS_OUTPUT_FILE.exists():
        print(f"[WARN] Pandas RFM output not found: {PANDAS_OUTPUT_FILE}. Comparison skipped.")
        return

    pandas_rfm = pd.read_csv(PANDAS_OUTPUT_FILE, low_memory=False)
    checks = []

    def add(metric, p_val, s_val, tol=0.01):
        diff = abs(float(p_val) - float(s_val))
        checks.append(
            {
                "metric_name": metric,
                "pandas_value": p_val,
                "spark_sql_value": s_val,
                "difference": round(diff, 4),
                "tolerance": tol,
                "status": "PASS" if diff <= tol else "FAIL",
            }
        )

    add("customer_count", len(pandas_rfm), len(spark_rfm), tol=0)
    add("total_monetary", round(pandas_rfm["monetary"].sum(), 2),
        round(spark_rfm["monetary"].sum(), 2), tol=1.0)
    add("segment_count", pandas_rfm["segment"].nunique(), spark_rfm["segment"].nunique(), tol=0)
    add("total_frequency", int(pandas_rfm["frequency"].sum()),
        int(spark_rfm["frequency"].sum()), tol=0)

    df = pd.DataFrame(checks)
    path = DOCS_DIR / "spark_rfm_comparison_report.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    failed = int((df["status"] == "FAIL").sum())
    print(f"[OK] Comparison report: {path}")
    print(f"[COMPARISON] Total: {len(checks)} | Passed: {len(checks)-failed} | Failed: {failed}")


def main() -> None:
    print("=" * 60)
    print("[INFO] Building ADS customer RFM with Spark SQL ...")
    print("=" * 60)
    input_file = resolve_input()
    spark = create_spark_session()
    try:
        rfm_df = build_rfm_with_spark_sql(spark, input_file)
        rfm_pd = rfm_df.toPandas()
        rfm_pd.to_csv(SPARK_OUTPUT_FILE, index=False, encoding="utf-8-sig")
        print(f"[OK] Spark RFM CSV generated: {SPARK_OUTPUT_FILE} ({len(rfm_pd)} rows)")

        report = pd.DataFrame([{
            "table_name": "ads_customer_rfm_spark",
            "customer_count": len(rfm_pd),
            "total_monetary": round(float(rfm_pd["monetary"].sum()), 2),
            "segment_count": int(rfm_pd["segment"].nunique()),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "engine": "Spark SQL",
        }])
        report.to_csv(DOCS_DIR / "spark_rfm_report.csv", index=False, encoding="utf-8-sig")

        generate_comparison(rfm_pd)
        print("[DONE] Spark RFM building completed.")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
