"""
Build ADS product category ranking with Spark SQL.

使用 Spark SQL 构建 ADS 商品类目排名表。

Spark SQL counterpart of scripts/build_ads_product_category_rank.py. Reads ODS
CSVs, joins items -> products -> translation (valid orders only), ranks categories
by revenue with a Pareto cumulative share, and compares against the Pandas output.

scripts/build_ads_product_category_rank.py 的 Spark SQL 版本：读取 ODS CSV，
关联 商品明细 -> 商品 -> 类目翻译（仅有效订单），按收入排名并计算帕累托累计占比，
最后与 Pandas 版对比。
"""

import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from pyspark.sql import SparkSession

ROOT_DIR = Path(__file__).resolve().parents[1]
ODS_DIR = ROOT_DIR / "data" / "ods"
ADS_DIR = ROOT_DIR / "data" / "ads"
DOCS_DIR = ROOT_DIR / "docs"
ADS_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

SPARK_OUTPUT_FILE = ADS_DIR / "ads_product_category_rank_spark.csv"
PANDAS_OUTPUT_FILE = ADS_DIR / "ads_product_category_rank.csv"


def create_spark_session() -> SparkSession:
    """Create a local Spark session. 创建本地 Spark 会话。"""
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
    spark = (
        SparkSession.builder.appName("EcommerceWarehouseSparkCategory")
        .master("local[*]")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark


def register_ods_view(spark: SparkSession, table: str, view: str) -> None:
    """Register an ODS CSV as a temp view. 将 ODS CSV 注册为临时视图。"""
    path = ODS_DIR / f"{table}.csv"
    if not path.exists():
        raise FileNotFoundError(f"ODS table not found: {path}")
    df = spark.read.option("header", "true").option("inferSchema", "false").csv(str(path))
    df.createOrReplaceTempView(view)


def build_category_with_spark_sql(spark: SparkSession):
    """Build the category ranking via Spark SQL. 通过 Spark SQL 构建类目排名。"""
    register_ods_view(spark, "ods_order_items", "ods_order_items")
    register_ods_view(spark, "ods_products", "ods_products")
    register_ods_view(spark, "ods_product_category_translation", "ods_translation")
    register_ods_view(spark, "ods_orders", "ods_orders")

    return spark.sql(
        """
        WITH valid_items AS (
            SELECT
                i.order_id,
                i.order_item_id,
                i.product_id,
                COALESCE(TRY_CAST(i.price AS DOUBLE), 0.0) AS price,
                COALESCE(TRY_CAST(i.freight_value AS DOUBLE), 0.0) AS freight_value
            FROM ods_order_items i
            INNER JOIN ods_orders o ON i.order_id = o.order_id
            WHERE o.order_status NOT IN ('canceled', 'unavailable')
        ),
        items_cat AS (
            SELECT
                vi.*,
                COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS category
            FROM valid_items vi
            LEFT JOIN ods_products p ON vi.product_id = p.product_id
            LEFT JOIN ods_translation t ON p.product_category_name = t.product_category_name
        ),
        cat_agg AS (
            SELECT
                category,
                ROUND(SUM(price), 2) AS product_revenue,
                ROUND(SUM(freight_value), 2) AS freight_revenue,
                COUNT(order_item_id) AS item_count,
                COUNT(DISTINCT order_id) AS order_count,
                COUNT(DISTINCT product_id) AS product_count
            FROM items_cat
            GROUP BY category
        ),
        ranked AS (
            SELECT
                *,
                ROUND(product_revenue / item_count, 2) AS avg_item_price,
                ROW_NUMBER() OVER (ORDER BY product_revenue DESC) AS revenue_rank,
                ROUND(product_revenue / SUM(product_revenue) OVER () * 100, 2) AS revenue_share_pct,
                ROUND(
                    SUM(product_revenue) OVER (
                        ORDER BY product_revenue DESC
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    ) / SUM(product_revenue) OVER () * 100, 2
                ) AS cumulative_revenue_share_pct
            FROM cat_agg
        )
        SELECT
            revenue_rank,
            category,
            product_revenue,
            revenue_share_pct,
            cumulative_revenue_share_pct,
            freight_revenue,
            item_count,
            order_count,
            product_count,
            avg_item_price,
            DATE_FORMAT(CURRENT_TIMESTAMP(), 'yyyy-MM-dd HH:mm:ss') AS ads_loaded_at,
            DATE_FORMAT(CURRENT_DATE(), 'yyyy-MM-dd') AS dt
        FROM ranked
        ORDER BY revenue_rank
        """
    )


def generate_comparison(spark_cat: pd.DataFrame) -> None:
    """Compare Spark category aggregates against Pandas. 与 Pandas 版对比。"""
    if not PANDAS_OUTPUT_FILE.exists():
        print(f"[WARN] Pandas output not found: {PANDAS_OUTPUT_FILE}. Comparison skipped.")
        return

    pandas_cat = pd.read_csv(PANDAS_OUTPUT_FILE, low_memory=False)
    checks = []

    def add(metric, p_val, s_val, tol=0.01):
        same = str(p_val) == str(s_val) if isinstance(p_val, str) else abs(float(p_val) - float(s_val)) <= tol
        checks.append({
            "metric_name": metric,
            "pandas_value": p_val,
            "spark_sql_value": s_val,
            "status": "PASS" if same else "FAIL",
        })

    add("category_count", len(pandas_cat), len(spark_cat), tol=0)
    add("total_product_revenue", round(pandas_cat["product_revenue"].sum(), 2),
        round(spark_cat["product_revenue"].sum(), 2), tol=1.0)
    add("top_category",
        pandas_cat.sort_values("revenue_rank").iloc[0]["category"],
        spark_cat.sort_values("revenue_rank").iloc[0]["category"])

    df = pd.DataFrame(checks)
    path = DOCS_DIR / "spark_category_comparison_report.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    failed = int((df["status"] == "FAIL").sum())
    print(f"[OK] Comparison report: {path}")
    print(f"[COMPARISON] Total: {len(checks)} | Passed: {len(checks)-failed} | Failed: {failed}")


def main() -> None:
    print("=" * 60)
    print("[INFO] Building ADS product category rank with Spark SQL ...")
    print("=" * 60)
    spark = create_spark_session()
    try:
        cat_df = build_category_with_spark_sql(spark)
        cat_pd = cat_df.toPandas()
        cat_pd.to_csv(SPARK_OUTPUT_FILE, index=False, encoding="utf-8-sig")
        print(f"[OK] Spark category CSV generated: {SPARK_OUTPUT_FILE} ({len(cat_pd)} rows)")

        report = pd.DataFrame([{
            "table_name": "ads_product_category_rank_spark",
            "category_count": len(cat_pd),
            "total_product_revenue": round(float(cat_pd["product_revenue"].sum()), 2),
            "top_category": cat_pd.sort_values("revenue_rank").iloc[0]["category"],
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "engine": "Spark SQL",
        }])
        report.to_csv(DOCS_DIR / "spark_category_report.csv", index=False, encoding="utf-8-sig")

        generate_comparison(cat_pd)
        print("[DONE] Spark category building completed.")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
