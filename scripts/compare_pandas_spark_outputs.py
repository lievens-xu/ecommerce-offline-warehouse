from pathlib import Path
from datetime import datetime
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
DOCS_DIR = ROOT_DIR / "docs"

DOCS_DIR.mkdir(parents=True, exist_ok=True)


# Input file pairs
DWD_PANDAS_FILE = DATA_DIR / "dwd" / "dwd_order_detail.csv"
DWD_SPARK_FILE = DATA_DIR / "dwd" / "dwd_order_detail_spark.csv"

DWS_PANDAS_FILE = DATA_DIR / "dws" / "dws_daily_order_summary.csv"
DWS_SPARK_FILE = DATA_DIR / "dws" / "dws_daily_order_summary_spark.csv"

ADS_PANDAS_FILE = DATA_DIR / "ads" / "ads_daily_business_overview.csv"
ADS_SPARK_FILE = DATA_DIR / "ads" / "ads_daily_business_overview_spark.csv"


# Output files
FULL_REPORT_CSV = DOCS_DIR / "pandas_spark_full_comparison_report.csv"
SUMMARY_MD = DOCS_DIR / "pandas_spark_full_comparison_summary.md"


def validate_input_files() -> None:
    """
    Validate all required input files exist.
    Show clear error messages if any file is missing.
    """
    missing_files = []

    # DWD files
    if not DWD_PANDAS_FILE.exists():
        missing_files.append(("DWD Pandas", DWD_PANDAS_FILE, "scripts/build_dwd_order_detail.py"))
    if not DWD_SPARK_FILE.exists():
        missing_files.append(("DWD Spark", DWD_SPARK_FILE, "scripts/spark_build_dwd_order_detail.py"))

    # DWS files
    if not DWS_PANDAS_FILE.exists():
        missing_files.append(("DWS Pandas", DWS_PANDAS_FILE, "scripts/build_dws_daily_order_summary.py"))
    if not DWS_SPARK_FILE.exists():
        missing_files.append(("DWS Spark", DWS_SPARK_FILE, "scripts/spark_build_dws_daily_order_summary.py"))

    # ADS files
    if not ADS_PANDAS_FILE.exists():
        missing_files.append(("ADS Pandas", ADS_PANDAS_FILE, "scripts/build_ads_daily_business_overview.py"))
    if not ADS_SPARK_FILE.exists():
        missing_files.append(("ADS Spark", ADS_SPARK_FILE, "scripts/spark_build_ads_daily_business_overview.py"))

    if missing_files:
        print("=" * 60)
        print("[ERROR] Missing required input files:")
        print("=" * 60)
        for layer, file_path, script in missing_files:
            print(f"  - {layer}: {file_path}")
            print(f"    Please run: python {script}")
        print("=" * 60)
        raise FileNotFoundError(f"Missing {len(missing_files)} required input files. Please run the upstream scripts first.")


def add_comparison(comparison_items: list, layer: str, metric_name: str,
                   pandas_value: float, spark_value: float, tolerance: float) -> None:
    """
    Add a comparison item to the list.
    """
    diff = abs(pandas_value - spark_value)

    if diff <= tolerance:
        status = "PASS"
        message = "Values match within tolerance."
    else:
        status = "FAIL"
        message = f"Difference exceeds tolerance of {tolerance}."

    comparison_items.append({
        "layer": layer,
        "metric_name": metric_name,
        "pandas_value": pandas_value,
        "spark_sql_value": spark_value,
        "difference": round(diff, 4),
        "tolerance": tolerance,
        "status": status,
        "message": message,
    })


def compare_dwd_layer(pandas_dwd: pd.DataFrame, spark_dwd: pd.DataFrame) -> list:
    """
    Compare DWD layer metrics.
    """
    print("[INFO] Comparing DWD layer ...")
    comparison_items = []

    # Row count
    add_comparison(
        comparison_items, "DWD", "row_count",
        len(pandas_dwd), len(spark_dwd),
        tolerance=0
    )

    # Unique order count
    add_comparison(
        comparison_items, "DWD", "unique_order_count",
        pandas_dwd["order_id"].nunique(), spark_dwd["order_id"].nunique(),
        tolerance=0
    )

    # Unique customer count
    add_comparison(
        comparison_items, "DWD", "unique_customer_count",
        pandas_dwd["customer_unique_id"].nunique(), spark_dwd["customer_unique_id"].nunique(),
        tolerance=0
    )

    # Total payment amount
    add_comparison(
        comparison_items, "DWD", "total_payment_amount",
        round(float(pandas_dwd["total_payment_amount"].sum()), 2),
        round(float(spark_dwd["total_payment_amount"].sum()), 2),
        tolerance=0.01
    )

    # Total product amount
    add_comparison(
        comparison_items, "DWD", "total_product_amount",
        round(float(pandas_dwd["total_product_amount"].sum()), 2),
        round(float(spark_dwd["total_product_amount"].sum()), 2),
        tolerance=0.01
    )

    # Total freight amount
    add_comparison(
        comparison_items, "DWD", "total_freight_amount",
        round(float(pandas_dwd["total_freight_amount"].sum()), 2),
        round(float(spark_dwd["total_freight_amount"].sum()), 2),
        tolerance=0.01
    )

    # Delivered order count
    add_comparison(
        comparison_items, "DWD", "delivered_order_count",
        int(pandas_dwd["is_delivered"].sum()),
        int(spark_dwd["is_delivered"].sum()),
        tolerance=0
    )

    # Late delivery order count
    add_comparison(
        comparison_items, "DWD", "late_delivery_order_count",
        int(pandas_dwd["is_late_delivery"].sum()),
        int(spark_dwd["is_late_delivery"].sum()),
        tolerance=0
    )

    # Average review score (use larger tolerance)
    add_comparison(
        comparison_items, "DWD", "average_review_score",
        round(float(pandas_dwd["average_review_score"].mean()), 2),
        round(float(spark_dwd["average_review_score"].mean()), 2),
        tolerance=0.05
    )

    return comparison_items


def compare_dws_layer(pandas_dws: pd.DataFrame, spark_dws: pd.DataFrame) -> list:
    """
    Compare DWS layer metrics.
    """
    print("[INFO] Comparing DWS layer ...")
    comparison_items = []

    # Row count
    add_comparison(
        comparison_items, "DWS", "row_count",
        len(pandas_dws), len(spark_dws),
        tolerance=0
    )

    # Total order count
    add_comparison(
        comparison_items, "DWS", "total_order_count",
        int(pandas_dws["order_count"].sum()),
        int(spark_dws["order_count"].sum()),
        tolerance=0
    )

    # Total valid order count
    add_comparison(
        comparison_items, "DWS", "total_valid_order_count",
        int(pandas_dws["valid_order_count"].sum()),
        int(spark_dws["valid_order_count"].sum()),
        tolerance=0
    )

    # Total payment amount
    add_comparison(
        comparison_items, "DWS", "total_payment_amount",
        round(float(pandas_dws["total_payment_amount"].sum()), 2),
        round(float(spark_dws["total_payment_amount"].sum()), 2),
        tolerance=0.01
    )

    # Total product amount
    add_comparison(
        comparison_items, "DWS", "total_product_amount",
        round(float(pandas_dws["total_product_amount"].sum()), 2),
        round(float(spark_dws["total_product_amount"].sum()), 2),
        tolerance=0.01
    )

    # Total freight amount
    add_comparison(
        comparison_items, "DWS", "total_freight_amount",
        round(float(pandas_dws["total_freight_amount"].sum()), 2),
        round(float(spark_dws["total_freight_amount"].sum()), 2),
        tolerance=0.01
    )

    # Overall AOV
    pandas_total_payment = float(pandas_dws["total_payment_amount"].sum())
    pandas_total_orders = float(pandas_dws["order_count"].sum())
    pandas_overall_aov = round(pandas_total_payment / pandas_total_orders, 4) if pandas_total_orders != 0 else 0

    spark_total_payment = float(spark_dws["total_payment_amount"].sum())
    spark_total_orders = float(spark_dws["order_count"].sum())
    spark_overall_aov = round(spark_total_payment / spark_total_orders, 4) if spark_total_orders != 0 else 0

    add_comparison(
        comparison_items, "DWS", "overall_aov",
        pandas_overall_aov, spark_overall_aov,
        tolerance=0.05
    )

    return comparison_items


def compare_ads_layer(pandas_ads: pd.DataFrame, spark_ads: pd.DataFrame) -> list:
    """
    Compare ADS layer metrics.
    """
    print("[INFO] Comparing ADS layer ...")
    comparison_items = []

    # Row count
    add_comparison(
        comparison_items, "ADS", "row_count",
        len(pandas_ads), len(spark_ads),
        tolerance=0
    )

    # Total order count
    add_comparison(
        comparison_items, "ADS", "total_order_count",
        int(pandas_ads["daily_order_count"].sum()),
        int(spark_ads["daily_order_count"].sum()),
        tolerance=0
    )

    # Total GMV
    add_comparison(
        comparison_items, "ADS", "total_gmv",
        round(float(pandas_ads["daily_gmv"].sum()), 2),
        round(float(spark_ads["daily_gmv"].sum()), 2),
        tolerance=0.01
    )

    # Average daily GMV
    add_comparison(
        comparison_items, "ADS", "average_daily_gmv",
        round(float(pandas_ads["daily_gmv"].mean()), 4),
        round(float(spark_ads["daily_gmv"].mean()), 4),
        tolerance=0.05
    )

    # Overall AOV
    pandas_total_gmv = float(pandas_ads["daily_gmv"].sum())
    pandas_total_orders = float(pandas_ads["daily_order_count"].sum())
    pandas_overall_aov = round(pandas_total_gmv / pandas_total_orders, 4) if pandas_total_orders != 0 else 0

    spark_total_gmv = float(spark_ads["daily_gmv"].sum())
    spark_total_orders = float(spark_ads["daily_order_count"].sum())
    spark_overall_aov = round(spark_total_gmv / spark_total_orders, 4) if spark_total_orders != 0 else 0

    add_comparison(
        comparison_items, "ADS", "overall_aov",
        pandas_overall_aov, spark_overall_aov,
        tolerance=0.05
    )

    # Latest daily GMV
    pandas_latest_date = pandas_ads["stat_date"].max()
    spark_latest_date = spark_ads["stat_date"].max()

    add_comparison(
        comparison_items, "ADS", "latest_daily_gmv",
        round(float(pandas_ads.loc[pandas_ads["stat_date"] == pandas_latest_date, "daily_gmv"].sum()), 4),
        round(float(spark_ads.loc[spark_ads["stat_date"] == spark_latest_date, "daily_gmv"].sum()), 4),
        tolerance=0.01
    )

    # Latest daily order count
    add_comparison(
        comparison_items, "ADS", "latest_daily_order_count",
        int(pandas_ads.loc[pandas_ads["stat_date"] == pandas_latest_date, "daily_order_count"].sum()),
        int(spark_ads.loc[spark_ads["stat_date"] == spark_latest_date, "daily_order_count"].sum()),
        tolerance=0
    )

    return comparison_items


def generate_csv_report(all_comparison_items: list) -> None:
    """
    Generate the full comparison CSV report.
    """
    report_df = pd.DataFrame(all_comparison_items)
    report_df.to_csv(FULL_REPORT_CSV, index=False, encoding="utf-8-sig")
    print(f"[OK] Full comparison report generated: {FULL_REPORT_CSV}")


def generate_markdown_summary(all_comparison_items: list) -> None:
    """
    Generate a bilingual Markdown summary.
    """
    report_df = pd.DataFrame(all_comparison_items)

    total_checks = len(all_comparison_items)
    passed_checks = int((report_df["status"] == "PASS").sum())
    failed_checks = int((report_df["status"] == "FAIL").sum())

    # Layer-level summary
    dwd_items = [item for item in all_comparison_items if item["layer"] == "DWD"]
    dws_items = [item for item in all_comparison_items if item["layer"] == "DWS"]
    ads_items = [item for item in all_comparison_items if item["layer"] == "ADS"]

    dwd_passed = sum(1 for item in dwd_items if item["status"] == "PASS")
    dws_passed = sum(1 for item in dws_items if item["status"] == "PASS")
    ads_passed = sum(1 for item in ads_items if item["status"] == "PASS")

    failed_items = [item for item in all_comparison_items if item["status"] == "FAIL"]

    with SUMMARY_MD.open("w", encoding="utf-8") as f:
        f.write("# Pandas vs Spark Comparison Summary / Pandas 与 Spark 对比总结\n\n")
        f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Overall summary
        f.write("## 1. Overall Summary / 总体结果\n\n")
        f.write("| Metric / 指标 | Value / 数值 |\n")
        f.write("|---|---:|\n")
        f.write(f"| Total checks / 总检查数 | {total_checks} |\n")
        f.write(f"| Passed checks / 通过检查数 | {passed_checks} |\n")
        f.write(f"| Failed checks / 失败检查数 | {failed_checks} |\n\n")

        if failed_checks == 0:
            f.write("**All comparison checks passed.**\n\n")
            f.write("**所有对比检查均已通过。**\n\n")
        else:
            f.write(f"**{failed_checks} comparison checks failed.**\n\n")
            f.write(f"**{failed_checks} 个对比检查失败。**\n\n")

        # Layer-level summary
        f.write("## 2. Layer Summary / 分层总结\n\n")
        f.write("| Layer / 分层 | Total / 总数 | Passed / 通过 | Failed / 失败 |\n")
        f.write("|---|---:|---:|---:|\n")
        f.write(f"| DWD | {len(dwd_items)} | {dwd_passed} | {len(dwd_items) - dwd_passed} |\n")
        f.write(f"| DWS | {len(dws_items)} | {dws_passed} | {len(dws_items) - dws_passed} |\n")
        f.write(f"| ADS | {len(ads_items)} | {ads_passed} | {len(ads_items) - ads_passed} |\n\n")

        # Detailed checks per layer
        f.write("## 3. DWD Layer Checks / DWD 分层检查\n\n")
        f.write("| Metric / 指标 | Pandas Value / Pandas 值 | Spark Value / Spark 值 | Difference / 差异 | Tolerance / 容差 | Status / 状态 |\n")
        f.write("|---|---:|---:|---:|---:|---|\n")
        for item in dwd_items:
            f.write(f"| {item['metric_name']} | {item['pandas_value']} | {item['spark_sql_value']} | {item['difference']} | {item['tolerance']} | {item['status']} |\n")

        f.write("\n## 4. DWS Layer Checks / DWS 分层检查\n\n")
        f.write("| Metric / 指标 | Pandas Value / Pandas 值 | Spark Value / Spark 值 | Difference / 差异 | Tolerance / 容差 | Status / 状态 |\n")
        f.write("|---|---:|---:|---:|---:|---|\n")
        for item in dws_items:
            f.write(f"| {item['metric_name']} | {item['pandas_value']} | {item['spark_sql_value']} | {item['difference']} | {item['tolerance']} | {item['status']} |\n")

        f.write("\n## 5. ADS Layer Checks / ADS 分层检查\n\n")
        f.write("| Metric / 指标 | Pandas Value / Pandas 值 | Spark Value / Spark 值 | Difference / 差异 | Tolerance / 容差 | Status / 状态 |\n")
        f.write("|---|---:|---:|---:|---:|---|\n")
        for item in ads_items:
            f.write(f"| {item['metric_name']} | {item['pandas_value']} | {item['spark_sql_value']} | {item['difference']} | {item['tolerance']} | {item['status']} |\n")

        # Failed checks details
        if failed_items:
            f.write("\n## 6. Failed Checks Details / 失败检查详情\n\n")
            f.write("The following checks failed:\n\n")
            f.write("以下检查失败：\n\n")
            for item in failed_items:
                f.write(f"- **{item['layer']} - {item['metric_name']}**:\n")
                f.write(f"  - Pandas value: {item['pandas_value']}\n")
                f.write(f"  - Spark value: {item['spark_sql_value']}\n")
                f.write(f"  - Difference: {item['difference']}\n")
                f.write(f"  - Tolerance: {item['tolerance']}\n")
                f.write(f"  - Message: {item['message']}\n\n")
        else:
            f.write("\n## 6. Failed Checks Details / 失败检查详情\n\n")
            f.write("No checks failed.\n\n")
            f.write("无失败检查。\n\n")

        # Output files
        f.write("## 7. Output Files / 输出文件\n\n")
        f.write("The detailed comparison report is available at:\n\n")
        f.write("详细对比报告生成在：\n\n")
        f.write(f"- `{FULL_REPORT_CSV.relative_to(ROOT_DIR)}`\n\n")

    print(f"[OK] Markdown summary generated: {SUMMARY_MD}")


def print_final_result(all_comparison_items: list) -> None:
    """
    Print the final result summary.
    """
    report_df = pd.DataFrame(all_comparison_items)
    failed_checks = int((report_df["status"] == "FAIL").sum())

    print("=" * 60)
    print("[COMPARISON SUMMARY]")
    print(f"Total checks: {len(all_comparison_items)}")
    print(f"Passed: {len(all_comparison_items) - failed_checks}")
    print(f"Failed: {failed_checks}")
    print("=" * 60)

    # Layer breakdown
    dwd_items = [item for item in all_comparison_items if item["layer"] == "DWD"]
    dws_items = [item for item in all_comparison_items if item["layer"] == "DWS"]
    ads_items = [item for item in all_comparison_items if item["layer"] == "ADS"]

    print("\nLayer Summary:")
    print(f"  DWD: {len(dwd_items)} checks, {sum(1 for i in dwd_items if i['status'] == 'PASS')} passed")
    print(f"  DWS: {len(dws_items)} checks, {sum(1 for i in dws_items if i['status'] == 'PASS')} passed")
    print(f"  ADS: {len(ads_items)} checks, {sum(1 for i in ads_items if i['status'] == 'PASS')} passed")

    print("=" * 60)

    if failed_checks > 0:
        print("[WARN] Some Pandas vs Spark comparison checks failed.")
        print("\nFailed checks:")
        for item in all_comparison_items:
            if item["status"] == "FAIL":
                print(f"  - {item['layer']} - {item['metric_name']}: "
                      f"Pandas={item['pandas_value']}, Spark={item['spark_sql_value']}, "
                      f"Diff={item['difference']}, Tolerance={item['tolerance']}")
    else:
        print("[DONE] All Pandas vs Spark comparison checks passed.")


def main() -> None:
    print("=" * 60)
    print("[INFO] Pandas vs Spark Full Comparison")
    print("=" * 60)

    validate_input_files()

    # Load all files
    print("[INFO] Loading data files ...")
    pandas_dwd = pd.read_csv(DWD_PANDAS_FILE, low_memory=False)
    spark_dwd = pd.read_csv(DWD_SPARK_FILE, low_memory=False)
    print(f"[OK] DWD files loaded: Pandas={len(pandas_dwd)} rows, Spark={len(spark_dwd)} rows")

    pandas_dws = pd.read_csv(DWS_PANDAS_FILE, low_memory=False)
    spark_dws = pd.read_csv(DWS_SPARK_FILE, low_memory=False)
    print(f"[OK] DWS files loaded: Pandas={len(pandas_dws)} rows, Spark={len(spark_dws)} rows")

    pandas_ads = pd.read_csv(ADS_PANDAS_FILE, low_memory=False)
    spark_ads = pd.read_csv(ADS_SPARK_FILE, low_memory=False)
    print(f"[OK] ADS files loaded: Pandas={len(pandas_ads)} rows, Spark={len(spark_ads)} rows")

    # Run comparisons
    all_comparison_items = []

    dwd_items = compare_dwd_layer(pandas_dwd, spark_dwd)
    all_comparison_items.extend(dwd_items)

    dws_items = compare_dws_layer(pandas_dws, spark_dws)
    all_comparison_items.extend(dws_items)

    ads_items = compare_ads_layer(pandas_ads, spark_ads)
    all_comparison_items.extend(ads_items)

    # Generate reports
    generate_csv_report(all_comparison_items)
    generate_markdown_summary(all_comparison_items)

    # Print final result
    print_final_result(all_comparison_items)

    print("=" * 60)
    print("[DONE] Full comparison completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()