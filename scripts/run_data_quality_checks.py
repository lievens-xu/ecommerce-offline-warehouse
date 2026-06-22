from pathlib import Path
from datetime import datetime
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]

ODS_DIR = ROOT_DIR / "data" / "ods"
DWD_DIR = ROOT_DIR / "data" / "dwd"
DWS_DIR = ROOT_DIR / "data" / "dws"
ADS_DIR = ROOT_DIR / "data" / "ads"
DOCS_DIR = ROOT_DIR / "docs"

DOCS_DIR.mkdir(parents=True, exist_ok=True)


EXPECTED_ODS_FILES = [
    "ods_customers.csv",
    "ods_orders.csv",
    "ods_order_items.csv",
    "ods_order_payments.csv",
    "ods_order_reviews.csv",
    "ods_products.csv",
    "ods_sellers.csv",
    "ods_geolocation.csv",
    "ods_product_category_translation.csv",
]

EXPECTED_LAYER_FILES = {
    "DWD": DWD_DIR / "dwd_order_detail.csv",
    "DWS": DWS_DIR / "dws_daily_order_summary.csv",
    "ADS": ADS_DIR / "ads_daily_business_overview.csv",
}


def read_csv_if_exists(file_path: Path) -> pd.DataFrame:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    return pd.read_csv(file_path, low_memory=False)


def add_result(results, layer, table_name, check_name, status, actual_value, expected_rule, message):
    results.append(
        {
            "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "layer": layer,
            "table_name": table_name,
            "check_name": check_name,
            "status": status,
            "actual_value": actual_value,
            "expected_rule": expected_rule,
            "message": message,
        }
    )


def check_ods_files(results):
    for file_name in EXPECTED_ODS_FILES:
        file_path = ODS_DIR / file_name
        table_name = file_name.replace(".csv", "")

        if not file_path.exists():
            add_result(
                results,
                "ODS",
                table_name,
                "file_existence_check",
                "FAIL",
                "missing",
                "file should exist",
                f"{file_name} does not exist in data/ods/",
            )
            continue

        df = read_csv_if_exists(file_path)

        add_result(
            results,
            "ODS",
            table_name,
            "file_existence_check",
            "PASS",
            "exists",
            "file should exist",
            f"{file_name} exists.",
        )

        row_count = len(df)

        add_result(
            results,
            "ODS",
            table_name,
            "row_count_check",
            "PASS" if row_count > 0 else "FAIL",
            row_count,
            "row_count > 0",
            f"{table_name} row count is {row_count}.",
        )

        required_technical_fields = ["loaded_at", "dt"]
        for col in required_technical_fields:
            status = "PASS" if col in df.columns else "FAIL"
            add_result(
                results,
                "ODS",
                table_name,
                f"technical_field_check_{col}",
                status,
                "exists" if col in df.columns else "missing",
                f"{col} should exist",
                f"{col} field check for {table_name}.",
            )


def check_layer_files(results):
    for layer, file_path in EXPECTED_LAYER_FILES.items():
        table_name = file_path.stem

        if not file_path.exists():
            add_result(
                results,
                layer,
                table_name,
                "file_existence_check",
                "FAIL",
                "missing",
                "file should exist",
                f"{file_path} does not exist.",
            )
            continue

        df = read_csv_if_exists(file_path)
        row_count = len(df)

        add_result(
            results,
            layer,
            table_name,
            "file_existence_check",
            "PASS",
            "exists",
            "file should exist",
            f"{table_name} exists.",
        )

        add_result(
            results,
            layer,
            table_name,
            "row_count_check",
            "PASS" if row_count > 0 else "FAIL",
            row_count,
            "row_count > 0",
            f"{table_name} row count is {row_count}.",
        )


def check_dwd_order_detail(results):
    file_path = DWD_DIR / "dwd_order_detail.csv"

    if not file_path.exists():
        return

    df = read_csv_if_exists(file_path)
    table_name = "dwd_order_detail"

    required_columns = [
        "order_id",
        "customer_unique_id",
        "purchase_date",
        "order_status",
        "total_payment_amount",
        "total_product_amount",
        "total_freight_amount",
        "is_delivered",
        "is_late_delivery",
        "dt",
    ]

    for col in required_columns:
        status = "PASS" if col in df.columns else "FAIL"
        add_result(
            results,
            "DWD",
            table_name,
            f"required_column_check_{col}",
            status,
            "exists" if col in df.columns else "missing",
            f"{col} should exist",
            f"Required column check for {col}.",
        )

    if "order_id" in df.columns:
        duplicate_count = int(df["order_id"].duplicated().sum())
        add_result(
            results,
            "DWD",
            table_name,
            "primary_key_duplicate_check",
            "PASS" if duplicate_count == 0 else "FAIL",
            duplicate_count,
            "duplicate order_id count = 0",
            "Each row in dwd_order_detail should represent one unique order.",
        )

        missing_order_id = int(df["order_id"].isna().sum())
        add_result(
            results,
            "DWD",
            table_name,
            "primary_key_null_check",
            "PASS" if missing_order_id == 0 else "FAIL",
            missing_order_id,
            "missing order_id count = 0",
            "order_id should not be null.",
        )

    amount_columns = [
        "total_payment_amount",
        "total_product_amount",
        "total_freight_amount",
    ]

    for col in amount_columns:
        if col in df.columns:
            numeric_col = pd.to_numeric(df[col], errors="coerce").fillna(0)
            negative_count = int((numeric_col < 0).sum())

            add_result(
                results,
                "DWD",
                table_name,
                f"negative_amount_check_{col}",
                "PASS" if negative_count == 0 else "FAIL",
                negative_count,
                f"{col} should not be negative",
                f"Negative value check for {col}.",
            )

    if "purchase_date" in df.columns:
        missing_purchase_date = int(df["purchase_date"].isna().sum())
        add_result(
            results,
            "DWD",
            table_name,
            "purchase_date_null_check",
            "PASS" if missing_purchase_date == 0 else "FAIL",
            missing_purchase_date,
            "purchase_date should not be null",
            "purchase_date is required for daily aggregation.",
        )

    flag_columns = ["is_delivered", "is_late_delivery"]

    for col in flag_columns:
        if col in df.columns:
            values = set(pd.to_numeric(df[col], errors="coerce").dropna().unique())
            invalid_values = values - {0, 1}

            add_result(
                results,
                "DWD",
                table_name,
                f"binary_flag_check_{col}",
                "PASS" if len(invalid_values) == 0 else "FAIL",
                str(sorted(list(invalid_values))),
                f"{col} should only contain 0 or 1",
                f"Binary flag check for {col}.",
            )


def check_dws_daily_order_summary(results):
    file_path = DWS_DIR / "dws_daily_order_summary.csv"

    if not file_path.exists():
        return

    df = read_csv_if_exists(file_path)
    table_name = "dws_daily_order_summary"

    if "purchase_date" in df.columns:
        duplicate_date_count = int(df["purchase_date"].duplicated().sum())
        add_result(
            results,
            "DWS",
            table_name,
            "date_granularity_check",
            "PASS" if duplicate_date_count == 0 else "FAIL",
            duplicate_date_count,
            "one row per purchase_date",
            "DWS daily summary should have one row per purchase date.",
        )

    metric_columns_non_negative = [
        "order_count",
        "valid_order_count",
        "paid_order_count",
        "unique_customer_count",
        "delivered_order_count",
        "late_delivery_order_count",
        "total_payment_amount",
        "total_product_amount",
        "total_freight_amount",
        "aov",
    ]

    for col in metric_columns_non_negative:
        if col in df.columns:
            numeric_col = pd.to_numeric(df[col], errors="coerce").fillna(0)
            negative_count = int((numeric_col < 0).sum())

            add_result(
                results,
                "DWS",
                table_name,
                f"non_negative_metric_check_{col}",
                "PASS" if negative_count == 0 else "FAIL",
                negative_count,
                f"{col} should not be negative",
                f"Non-negative metric check for {col}.",
            )

    rate_columns = [
        "delivery_rate",
        "late_delivery_rate",
        "review_rate",
        "review_comment_rate",
    ]

    for col in rate_columns:
        if col in df.columns:
            numeric_col = pd.to_numeric(df[col], errors="coerce").fillna(0)
            invalid_count = int(((numeric_col < 0) | (numeric_col > 1)).sum())

            add_result(
                results,
                "DWS",
                table_name,
                f"rate_range_check_{col}",
                "PASS" if invalid_count == 0 else "FAIL",
                invalid_count,
                f"{col} should be between 0 and 1",
                f"Rate range check for {col}.",
            )


def check_ads_daily_business_overview(results):
    file_path = ADS_DIR / "ads_daily_business_overview.csv"

    if not file_path.exists():
        return

    df = read_csv_if_exists(file_path)
    table_name = "ads_daily_business_overview"

    if "stat_date" in df.columns:
        duplicate_date_count = int(df["stat_date"].duplicated().sum())
        add_result(
            results,
            "ADS",
            table_name,
            "date_granularity_check",
            "PASS" if duplicate_date_count == 0 else "FAIL",
            duplicate_date_count,
            "one row per stat_date",
            "ADS daily overview should have one row per statistic date.",
        )

    non_negative_columns = [
        "daily_order_count",
        "daily_valid_order_count",
        "daily_paid_order_count",
        "daily_unique_customer_count",
        "daily_gmv",
        "daily_product_amount",
        "daily_freight_amount",
        "daily_aov",
        "cumulative_gmv",
        "cumulative_order_count",
        "cumulative_customer_count",
    ]

    for col in non_negative_columns:
        if col in df.columns:
            numeric_col = pd.to_numeric(df[col], errors="coerce").fillna(0)
            negative_count = int((numeric_col < 0).sum())

            add_result(
                results,
                "ADS",
                table_name,
                f"non_negative_metric_check_{col}",
                "PASS" if negative_count == 0 else "FAIL",
                negative_count,
                f"{col} should not be negative",
                f"Non-negative metric check for {col}.",
            )

    rate_columns = [
        "daily_delivery_rate",
        "daily_late_delivery_rate",
        "daily_review_rate",
        "daily_review_comment_rate",
        "valid_order_rate",
        "paid_order_rate",
    ]

    for col in rate_columns:
        if col in df.columns:
            numeric_col = pd.to_numeric(df[col], errors="coerce").fillna(0)
            invalid_count = int(((numeric_col < 0) | (numeric_col > 1)).sum())

            add_result(
                results,
                "ADS",
                table_name,
                f"rate_range_check_{col}",
                "PASS" if invalid_count == 0 else "FAIL",
                invalid_count,
                f"{col} should be between 0 and 1",
                f"Rate range check for {col}.",
            )


def check_cross_layer_consistency(results):
    dwd_path = DWD_DIR / "dwd_order_detail.csv"
    dws_path = DWS_DIR / "dws_daily_order_summary.csv"
    ads_path = ADS_DIR / "ads_daily_business_overview.csv"

    if dwd_path.exists() and dws_path.exists():
        dwd = read_csv_if_exists(dwd_path)
        dws = read_csv_if_exists(dws_path)

        if "order_id" in dwd.columns and "order_count" in dws.columns:
            dwd_order_count = int(dwd["order_id"].nunique())
            dws_order_count = int(pd.to_numeric(dws["order_count"], errors="coerce").fillna(0).sum())

            status = "PASS" if dwd_order_count == dws_order_count else "FAIL"

            add_result(
                results,
                "CROSS_LAYER",
                "DWD_vs_DWS",
                "order_count_consistency_check",
                status,
                f"DWD={dwd_order_count}, DWS={dws_order_count}",
                "DWD unique order count should equal DWS total order count",
                "Check whether DWS aggregation preserves DWD order count.",
            )

    if dws_path.exists() and ads_path.exists():
        dws = read_csv_if_exists(dws_path)
        ads = read_csv_if_exists(ads_path)

        if "total_payment_amount" in dws.columns and "daily_gmv" in ads.columns:
            dws_gmv = round(pd.to_numeric(dws["total_payment_amount"], errors="coerce").fillna(0).sum(), 2)
            ads_gmv = round(pd.to_numeric(ads["daily_gmv"], errors="coerce").fillna(0).sum(), 2)

            status = "PASS" if abs(dws_gmv - ads_gmv) < 0.01 else "FAIL"

            add_result(
                results,
                "CROSS_LAYER",
                "DWS_vs_ADS",
                "gmv_consistency_check",
                status,
                f"DWS={dws_gmv}, ADS={ads_gmv}",
                "DWS total payment amount should equal ADS daily GMV sum",
                "Check whether ADS preserves GMV from DWS.",
            )

        if "order_count" in dws.columns and "daily_order_count" in ads.columns:
            dws_order_count = int(pd.to_numeric(dws["order_count"], errors="coerce").fillna(0).sum())
            ads_order_count = int(pd.to_numeric(ads["daily_order_count"], errors="coerce").fillna(0).sum())

            status = "PASS" if dws_order_count == ads_order_count else "FAIL"

            add_result(
                results,
                "CROSS_LAYER",
                "DWS_vs_ADS",
                "order_count_consistency_check",
                status,
                f"DWS={dws_order_count}, ADS={ads_order_count}",
                "DWS total order count should equal ADS daily order count sum",
                "Check whether ADS preserves order count from DWS.",
            )


def generate_markdown_summary(report_df: pd.DataFrame) -> None:
    summary_path = DOCS_DIR / "data_quality_check_summary.md"

    total_checks = len(report_df)
    pass_count = int((report_df["status"] == "PASS").sum())
    fail_count = int((report_df["status"] == "FAIL").sum())
    warn_count = int((report_df["status"] == "WARN").sum()) if "WARN" in report_df["status"].unique() else 0

    layer_summary = (
        report_df.groupby(["layer", "status"])
        .size()
        .reset_index(name="check_count")
        .sort_values(["layer", "status"])
    )

    failed_checks = report_df[report_df["status"] == "FAIL"]

    with summary_path.open("w", encoding="utf-8") as f:
        f.write("# Data Quality Check Summary / 数据质量检查总结\n\n")

        f.write("## 1. Overall Result / 总体结果\n\n")
        f.write("| Metric / 指标 | Value / 数值 |\n")
        f.write("|---|---:|\n")
        f.write(f"| Total checks / 检查总数 | {total_checks} |\n")
        f.write(f"| Passed checks / 通过检查数 | {pass_count} |\n")
        f.write(f"| Failed checks / 失败检查数 | {fail_count} |\n")
        f.write(f"| Warning checks / 警告检查数 | {warn_count} |\n\n")

        f.write("## 2. Layer Summary / 分层汇总\n\n")
        f.write("| Layer / 分层 | Status / 状态 | Check Count / 检查数 |\n")
        f.write("|---|---|---:|\n")

        for _, row in layer_summary.iterrows():
            f.write(f"| {row['layer']} | {row['status']} | {row['check_count']} |\n")

        f.write("\n## 3. Failed Checks / 失败检查\n\n")

        if failed_checks.empty:
            f.write("No failed checks were found.\n\n")
            f.write("未发现失败的数据质量检查。\n")
        else:
            f.write("| Layer / 分层 | Table / 表 | Check / 检查项 | Actual Value / 实际值 | Expected Rule / 预期规则 |\n")
            f.write("|---|---|---|---|---|\n")

            for _, row in failed_checks.iterrows():
                f.write(
                    f"| {row['layer']} "
                    f"| {row['table_name']} "
                    f"| {row['check_name']} "
                    f"| {row['actual_value']} "
                    f"| {row['expected_rule']} |\n"
                )

        f.write("\n## 4. Report File / 报告文件\n\n")
        f.write("The detailed data quality report is stored at:\n\n")
        f.write("详细的数据质量检查报告存放在：\n\n")
        f.write("    docs/data_quality_check_report.csv\n")

    print(f"[OK] Data quality summary generated: {summary_path}")


def main():
    print("[INFO] Running data quality checks ...")

    results = []

    check_ods_files(results)
    check_layer_files(results)
    check_dwd_order_detail(results)
    check_dws_daily_order_summary(results)
    check_ads_daily_business_overview(results)
    check_cross_layer_consistency(results)

    report_df = pd.DataFrame(results)

    report_path = DOCS_DIR / "data_quality_check_report.csv"
    report_df.to_csv(report_path, index=False, encoding="utf-8-sig")

    generate_markdown_summary(report_df)

    pass_count = int((report_df["status"] == "PASS").sum())
    fail_count = int((report_df["status"] == "FAIL").sum())
    total_count = len(report_df)

    print(f"[OK] Data quality report generated: {report_path}")
    print(f"[DONE] Total checks: {total_count}")
    print(f"[DONE] Passed checks: {pass_count}")
    print(f"[DONE] Failed checks: {fail_count}")

    if fail_count > 0:
        print("[WARN] Some data quality checks failed. Please check docs/data_quality_check_report.csv")
    else:
        print("[DONE] All data quality checks passed.")


if __name__ == "__main__":
    main()