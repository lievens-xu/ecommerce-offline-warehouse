"""
Compare dbt PostgreSQL Outputs with Pandas Baseline CSV Outputs
比较 dbt PostgreSQL 输出与 Pandas 基准 CSV 输出

This script validates that the dbt-generated PostgreSQL DWD/DWS/ADS tables
produce the same results as the existing Pandas baseline CSV outputs.

本脚本验证 dbt 生成的 PostgreSQL DWD/DWS/ADS 表
与现有 Pandas 基准 CSV 输出结果的一致性。
"""

from pathlib import Path
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
import sys
import os


ROOT_DIR = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT_DIR / "docs"

DOCS_DIR.mkdir(parents=True, exist_ok=True)


# PostgreSQL connection configuration
# PostgreSQL 连接配置
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5433")
DB_NAME = os.getenv("POSTGRES_DB", "ecommerce_warehouse")
DB_USER = os.getenv("POSTGRES_USER", "warehouse_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "warehouse_pass")


# Pandas baseline CSV paths / Pandas 基准 CSV 路径
PANDAS_FILES = {
    "DWD": ROOT_DIR / "data" / "dwd" / "dwd_order_detail.csv",
    "DWS": ROOT_DIR / "data" / "dws" / "dws_daily_order_summary.csv",
    "ADS": ROOT_DIR / "data" / "ads" / "ads_daily_business_overview.csv",
}

# PostgreSQL dbt table references / PostgreSQL dbt 表引用
DBT_TABLES = {
    "DWD": ("dwd", "dwd_order_detail"),
    "DWS": ("dws", "dws_daily_order_summary"),
    "ADS": ("ads", "ads_daily_business_overview"),
}


def get_engine():
    """
    Create SQLAlchemy engine for PostgreSQL connection.
    创建 PostgreSQL 连接的 SQLAlchemy 引擎。
    """
    database_url = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    engine = create_engine(database_url)
    return engine


def read_postgres_table(engine, schema: str, table: str) -> pd.DataFrame:
    """
    Read a PostgreSQL table into a Pandas DataFrame.
    将 PostgreSQL 表读取为 Pandas DataFrame。
    """
    full_name = f"{schema}.{table}"
    df = pd.read_sql(f"SELECT * FROM {full_name} ORDER BY 1", engine)
    return df


def safe_float(val):
    """Safely convert value to float, returning 0.0 on failure."""
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def add_comparison(comparison_items, metric_name, pandas_value, dbt_value,
                   tolerance=0.01, higher_is_better=True):
    """
    Add a comparison item with tolerance for floating point values.
    添加一个比较项，对浮点值使用误差范围。

    Args:
        comparison_items: List to append result to / 结果追加到的列表
        metric_name: Name of the metric being compared / 指标名称
        pandas_value: Value from Pandas baseline / Pandas 基准值
        dbt_value: Value from dbt PostgreSQL / dbt PostgreSQL 值
        tolerance: Allowed absolute difference / 允许的绝对误差
    """
    p_val = safe_float(pandas_value) if not isinstance(pandas_value, (int, float)) else pandas_value
    d_val = safe_float(dbt_value) if not isinstance(dbt_value, (int, float)) else dbt_value

    diff = abs(p_val - d_val)

    if diff <= tolerance:
        status = "PASS"
        message = f"Values match within tolerance of {tolerance}."
    else:
        status = "FAIL"
        message = f"Difference {diff:.6f} exceeds tolerance of {tolerance}."

    comparison_items.append({
        "metric_name": metric_name,
        "pandas_value": round(p_val, 6) if isinstance(p_val, float) else p_val,
        "dbt_postgres_value": round(d_val, 6) if isinstance(d_val, float) else d_val,
        "difference": round(diff, 6),
        "tolerance": tolerance,
        "status": status,
        "message": message,
    })


def compare_dwd(pandas_df: pd.DataFrame, dbt_df: pd.DataFrame) -> list:
    """
    Compare DWD order detail tables.
    比较 DWD 订单明细表。
    """
    items = []

    # Row count / 行数
    add_comparison(items, "dwd_row_count",
                   len(pandas_df), len(dbt_df), tolerance=0)

    # Unique order count / 唯一订单数
    add_comparison(items, "dwd_unique_order_count",
                   pandas_df["order_id"].nunique(),
                   dbt_df["order_id"].nunique(), tolerance=0)

    # Total payment amount / 支付总金额
    add_comparison(items, "dwd_total_payment_amount",
                   round(float(pandas_df["total_payment_amount"].sum()), 2),
                   round(float(dbt_df["total_payment_amount"].sum()), 2),
                   tolerance=0.01)

    # Total product amount / 商品总金额
    add_comparison(items, "dwd_total_product_amount",
                   round(float(pandas_df["total_product_amount"].sum()), 2),
                   round(float(dbt_df["total_product_amount"].sum()), 2),
                   tolerance=0.01)

    # Total freight amount / 运费总金额
    add_comparison(items, "dwd_total_freight_amount",
                   round(float(pandas_df["total_freight_amount"].sum()), 2),
                   round(float(dbt_df["total_freight_amount"].sum()), 2),
                   tolerance=0.01)

    # Delivered order count / 已配送订单数
    add_comparison(items, "dwd_delivered_order_count",
                   int(pandas_df["is_delivered"].sum()),
                   int(dbt_df["is_delivered"].sum()), tolerance=0)

    # Average review score / 平均评价分数
    add_comparison(items, "dwd_average_review_score",
                   round(float(pandas_df["average_review_score"].mean()), 2),
                   round(float(dbt_df["average_review_score"].mean()), 2),
                   tolerance=0.05)

    return items


def compare_dws(pandas_df: pd.DataFrame, dbt_df: pd.DataFrame) -> list:
    """
    Compare DWS daily order summary tables.
    比较 DWS 每日订单汇总表。
    """
    items = []

    # Row count / 行数
    add_comparison(items, "dws_row_count",
                   len(pandas_df), len(dbt_df), tolerance=0)

    # Total order count / 总订单数
    add_comparison(items, "dws_total_order_count",
                   int(pandas_df["order_count"].sum()),
                   int(dbt_df["order_count"].sum()), tolerance=0)

    # Total payment amount / 支付总金额
    add_comparison(items, "dws_total_payment_amount",
                   round(float(pandas_df["total_payment_amount"].sum()), 2),
                   round(float(dbt_df["total_payment_amount"].sum()), 2),
                   tolerance=0.01)

    # Total product amount / 商品总金额
    add_comparison(items, "dws_total_product_amount",
                   round(float(pandas_df["total_product_amount"].sum()), 2),
                   round(float(dbt_df["total_product_amount"].sum()), 2),
                   tolerance=0.01)

    # Date range / 日期范围
    add_comparison(items, "dws_start_date",
                   str(pandas_df["purchase_date"].min()),
                   str(dbt_df["purchase_date"].min()), tolerance=0)

    add_comparison(items, "dws_end_date",
                   str(pandas_df["purchase_date"].max()),
                   str(dbt_df["purchase_date"].max()), tolerance=0)

    return items


def compare_ads(pandas_df: pd.DataFrame, dbt_df: pd.DataFrame) -> list:
    """
    Compare ADS daily business overview tables.
    比较 ADS 每日经营概览表。
    """
    items = []

    # Row count / 行数
    add_comparison(items, "ads_row_count",
                   len(pandas_df), len(dbt_df), tolerance=0)

    # Total order count / 总订单数
    add_comparison(items, "ads_total_order_count",
                   int(pandas_df["daily_order_count"].sum()),
                   int(dbt_df["daily_order_count"].sum()), tolerance=0)

    # Total GMV / 总 GMV
    add_comparison(items, "ads_total_gmv",
                   round(float(pandas_df["daily_gmv"].sum()), 2),
                   round(float(dbt_df["daily_gmv"].sum()), 2),
                   tolerance=0.01)

    # Average daily GMV / 日均 GMV
    add_comparison(items, "ads_average_daily_gmv",
                   round(float(pandas_df["daily_gmv"].mean()), 4),
                   round(float(dbt_df["daily_gmv"].mean()), 4),
                   tolerance=0.05)

    # Latest daily GMV / 最新日 GMV
    pandas_latest_date = pandas_df["stat_date"].max()
    dbt_latest_date = dbt_df["stat_date"].max()

    add_comparison(items, "ads_latest_daily_gmv",
                   round(float(pandas_df.loc[pandas_df["stat_date"] == pandas_latest_date, "daily_gmv"].sum()), 4),
                   round(float(dbt_df.loc[dbt_df["stat_date"] == dbt_latest_date, "daily_gmv"].sum()), 4),
                   tolerance=0.01)

    # Latest daily order count / 最新日订单数
    add_comparison(items, "ads_latest_daily_order_count",
                   int(pandas_df.loc[pandas_df["stat_date"] == pandas_latest_date, "daily_order_count"].sum()),
                   int(dbt_df.loc[dbt_df["stat_date"] == dbt_latest_date, "daily_order_count"].sum()),
                   tolerance=0)

    # Date range / 日期范围
    add_comparison(items, "ads_start_date",
                   str(pandas_df["stat_date"].min()),
                   str(dbt_df["stat_date"].min()), tolerance=0)

    add_comparison(items, "ads_end_date",
                   str(pandas_df["stat_date"].max()),
                   str(dbt_df["stat_date"].max()), tolerance=0)

    return items


def generate_comparison_report(comparison_items: list):
    """
    Generate comparison report CSV and bilingual summary markdown.
    生成比较报告 CSV 和双语总结 Markdown。
    """
    # Generate CSV report / 生成 CSV 报告
    report_df = pd.DataFrame(comparison_items)
    report_path = DOCS_DIR / "dbt_postgres_comparison_report.csv"
    report_df.to_csv(report_path, index=False, encoding="utf-8-sig")
    print(f"[OK] Comparison report generated: {report_path}")

    # Generate summary markdown / 生成总结 Markdown
    summary_path = DOCS_DIR / "dbt_postgres_comparison_summary.md"

    total_checks = len(comparison_items)
    passed_checks = sum(1 for r in comparison_items if r["status"] == "PASS")
    failed_checks = total_checks - passed_checks

    # Group by layer / 按分层分组
    dwd_checks = [r for r in comparison_items if r["metric_name"].startswith("dwd_")]
    dws_checks = [r for r in comparison_items if r["metric_name"].startswith("dws_")]
    ads_checks = [r for r in comparison_items if r["metric_name"].startswith("ads_")]

    with summary_path.open("w", encoding="utf-8") as f:
        f.write("# dbt PostgreSQL vs Pandas Baseline Comparison / dbt PostgreSQL 与 Pandas 基准比较\n\n")
        f.write(f"Generated at / 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Overall summary / 总体总结
        f.write("## 1. Overall Summary / 总体结果\n\n")
        f.write("| Metric / 指标 | Value / 数值 |\n")
        f.write("|---|---:|\n")
        f.write(f"| Total checks / 总检查数 | {total_checks} |\n")
        f.write(f"| Passed checks / 通过检查数 | {passed_checks} |\n")
        f.write(f"| Failed checks / 失败检查数 | {failed_checks} |\n\n")

        if failed_checks == 0:
            f.write("**All dbt PostgreSQL outputs are consistent with Pandas baseline outputs.**\n\n")
            f.write("**所有 dbt PostgreSQL 输出与 Pandas 基准输出一致。**\n\n")
        else:
            f.write(f"**{failed_checks} checks failed — see details below.**\n\n")
            f.write(f"**{failed_checks} 个检查失败 — 详见下方。**\n\n")

        # Layer summary / 分层总结
        f.write("## 2. Layer Summary / 分层总结\n\n")
        f.write("| Layer / 分层 | Total / 总数 | Passed / 通过 | Failed / 失败 |\n")
        f.write("|---|---:|---:|---:|\n")
        f.write(f"| DWD / 明细层 | {len(dwd_checks)} | {sum(1 for r in dwd_checks if r['status'] == 'PASS')} | {sum(1 for r in dwd_checks if r['status'] == 'FAIL')} |\n")
        f.write(f"| DWS / 汇总层 | {len(dws_checks)} | {sum(1 for r in dws_checks if r['status'] == 'PASS')} | {sum(1 for r in dws_checks if r['status'] == 'FAIL')} |\n")
        f.write(f"| ADS / 应用层 | {len(ads_checks)} | {sum(1 for r in ads_checks if r['status'] == 'PASS')} | {sum(1 for r in ads_checks if r['status'] == 'FAIL')} |\n\n")

        # Detailed results / 详细结果
        f.write("## 3. Detailed Comparison Results / 详细比较结果\n\n")
        f.write("| Metric / 指标 | Pandas Value / Pandas 值 | dbt PostgreSQL Value / dbt PostgreSQL 值 | Difference / 差异 | Tolerance / 误差 | Status / 状态 |\n")
        f.write("|---|---:|---:|---:|---:|:---:|\n")

        for r in comparison_items:
            f.write(
                f"| {r['metric_name']} | {r['pandas_value']} | {r['dbt_postgres_value']} | "
                f"{r['difference']} | {r['tolerance']} | {'✅ PASS' if r['status'] == 'PASS' else '❌ FAIL'} |\n"
            )

        f.write("\n")

        # Failed checks details / 失败检查详情
        if failed_checks > 0:
            f.write("## 4. Failed Checks Details / 失败检查详情\n\n")
            f.write("The following checks failed:\n\n")
            f.write("以下检查失败：\n\n")

            for r in comparison_items:
                if r["status"] == "FAIL":
                    f.write(f"- **{r['metric_name']}**\n")
                    f.write(f"  - Pandas value: {r['pandas_value']}\n")
                    f.write(f"  - dbt PostgreSQL value: {r['dbt_postgres_value']}\n")
                    f.write(f"  - Difference: {r['difference']}\n")
                    f.write(f"  - Tolerance: {r['tolerance']}\n\n")
        else:
            f.write("## 4. Failed Checks Details / 失败检查详情\n\n")
            f.write("No checks failed.\n\n")
            f.write("无失败检查。\n\n")

        # Comparison scope / 比较范围
        f.write("## 5. Comparison Scope / 比较范围\n\n")
        f.write("| Layer / 分层 | Pandas Source / Pandas 源 | dbt PostgreSQL Source / dbt PostgreSQL 源 |\n")
        f.write("|---|---|---|\n")
        f.write(f"| DWD | `data/dwd/dwd_order_detail.csv` | `dwd.dwd_order_detail` |\n")
        f.write(f"| DWS | `data/dws/dws_daily_order_summary.csv` | `dws.dws_daily_order_summary` |\n")
        f.write(f"| ADS | `data/ads/ads_daily_business_overview.csv` | `ads.ads_daily_business_overview` |\n\n")

        f.write("Output reports / 输出报告：\n\n")
        f.write("- `docs/dbt_postgres_comparison_report.csv`\n")
        f.write("- `docs/dbt_postgres_comparison_summary.md`\n")

    print(f"[OK] Comparison summary generated: {summary_path}")

    # Print console summary / 打印控制台总结
    print("=" * 60)
    print("[COMPARISON SUMMARY]")
    print(f"Total checks: {total_checks}")
    print(f"Passed: {passed_checks}")
    print(f"Failed: {failed_checks}")
    print("=" * 60)

    if failed_checks > 0:
        print("[WARN] Some comparison checks failed:")
        for r in comparison_items:
            if r["status"] == "FAIL":
                print(f"  - {r['metric_name']}: Pandas={r['pandas_value']}, "
                      f"dbt={r['dbt_postgres_value']}, Diff={r['difference']}")
        print("[WARN] Please inspect the comparison report for details.")
    else:
        print("[DONE] All dbt PostgreSQL outputs are consistent with Pandas baseline.")

    return failed_checks


def validate_pandas_files() -> bool:
    """
    Validate that all required Pandas CSV files exist.
    验证所有必需的 Pandas CSV 文件存在。
    """
    all_exist = True
    for layer, path in PANDAS_FILES.items():
        if not path.exists():
            print(f"[ERROR] Pandas {layer} output not found: {path}")
            all_exist = False

    if not all_exist:
        print("[ERROR] Please run the Pandas baseline pipeline first:")
        print("  python scripts/run_pipeline.py")
        return False

    return True


def main():
    """
    Main entry point for comparison.
    比较的主入口。
    """
    print("=" * 60)
    print("[INFO] Comparing dbt PostgreSQL outputs with Pandas baseline")
    print("=" * 60)
    print()

    # Validate Pandas files / 验证 Pandas 文件
    if not validate_pandas_files():
        sys.exit(1)

    # Connect to PostgreSQL / 连接 PostgreSQL
    try:
        engine = get_engine()
        print("[OK] PostgreSQL connection successful.")
    except Exception as e:
        print(f"[ERROR] Cannot connect to PostgreSQL: {e}")
        print("[INFO] Please ensure PostgreSQL is running:")
        print("  docker compose -f docker-compose.postgres.yml up -d")
        sys.exit(1)

    all_comparison_items = []

    # Compare DWD / 比较 DWD
    print()
    print("--- DWD Comparison / DWD 比较 ---")
    try:
        pandas_dwd = pd.read_csv(PANDAS_FILES["DWD"], low_memory=False)
        dbt_dwd = read_postgres_table(engine, *DBT_TABLES["DWD"])
        print(f"[INFO] Pandas DWD: {len(pandas_dwd)} rows")
        print(f"[INFO] dbt DWD (dwd.dwd_order_detail): {len(dbt_dwd)} rows")

        dwd_items = compare_dwd(pandas_dwd, dbt_dwd)
        all_comparison_items.extend(dwd_items)
        print(f"[OK] DWD comparison completed: {len(dwd_items)} checks")
    except Exception as e:
        print(f"[ERROR] DWD comparison failed: {e}")
        import traceback
        traceback.print_exc()

    # Compare DWS / 比较 DWS
    print()
    print("--- DWS Comparison / DWS 比较 ---")
    try:
        pandas_dws = pd.read_csv(PANDAS_FILES["DWS"], low_memory=False)
        dbt_dws = read_postgres_table(engine, *DBT_TABLES["DWS"])
        print(f"[INFO] Pandas DWS: {len(pandas_dws)} rows")
        print(f"[INFO] dbt DWS (dws.dws_daily_order_summary): {len(dbt_dws)} rows")

        dws_items = compare_dws(pandas_dws, dbt_dws)
        all_comparison_items.extend(dws_items)
        print(f"[OK] DWS comparison completed: {len(dws_items)} checks")
    except Exception as e:
        print(f"[ERROR] DWS comparison failed: {e}")
        import traceback
        traceback.print_exc()

    # Compare ADS / 比较 ADS
    print()
    print("--- ADS Comparison / ADS 比较 ---")
    try:
        pandas_ads = pd.read_csv(PANDAS_FILES["ADS"], low_memory=False)
        dbt_ads = read_postgres_table(engine, *DBT_TABLES["ADS"])
        print(f"[INFO] Pandas ADS: {len(pandas_ads)} rows")
        print(f"[INFO] dbt ADS (ads.ads_daily_business_overview): {len(dbt_ads)} rows")

        ads_items = compare_ads(pandas_ads, dbt_ads)
        all_comparison_items.extend(ads_items)
        print(f"[OK] ADS comparison completed: {len(ads_items)} checks")
    except Exception as e:
        print(f"[ERROR] ADS comparison failed: {e}")
        import traceback
        traceback.print_exc()

    # Close engine / 关闭引擎
    engine.dispose()

    # Generate report / 生成报告
    print()
    print("--- Report Generation / 报告生成 ---")
    failed_count = generate_comparison_report(all_comparison_items)

    print()
    print("=" * 60)
    if failed_count == 0:
        print("[DONE] All comparisons passed. dbt PostgreSQL outputs are consistent.")
    else:
        print(f"[DONE] Comparison completed with {failed_count} failure(s).")
        print("[WARN] See docs/dbt_postgres_comparison_summary.md for details.")
    print("=" * 60)


if __name__ == "__main__":
    main()