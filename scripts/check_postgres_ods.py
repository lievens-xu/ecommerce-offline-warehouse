"""
Check PostgreSQL ODS Tables
检查 PostgreSQL ODS 表

This script validates ODS tables in PostgreSQL.
本脚本验证 PostgreSQL 中的 ODS 表。
"""

from pathlib import Path
from datetime import datetime
import pandas as pd
import psycopg2
import sys
import os


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"
DOCS_DIR = ROOT_DIR / "docs"

DOCS_DIR.mkdir(parents=True, exist_ok=True)


# Database connection configuration
# 数据库连接配置
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5433")
DB_NAME = os.getenv("POSTGRES_DB", "ecommerce_warehouse")
DB_USER = os.getenv("POSTGRES_USER", "warehouse_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "warehouse_pass")


# Expected ODS tables
# 预期的 ODS 表
EXPECTED_ODS_TABLES = [
    ("ods", "customers"),
    ("ods", "orders"),
    ("ods", "order_items"),
    ("ods", "order_payments"),
    ("ods", "order_reviews"),
    ("ods", "products"),
    ("ods", "sellers"),
    ("ods", "geolocation"),
    ("ods", "product_category_translation"),
]


# Table to raw CSV file mapping for row count validation
# 表到原始 CSV 文件的映射，用于行数校验
TABLE_TO_CSV_MAPPING = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "product_category_translation": "product_category_name_translation.csv",
}


def get_connection():
    """
    Create psycopg2 connection for PostgreSQL.
    创建 PostgreSQL 的 psycopg2 连接。
    """
    dsn = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
    conn = psycopg2.connect(dsn)
    return conn


def check_schema_exists(conn, schema: str) -> bool:
    """
    Check if a schema exists in PostgreSQL.
    检查 schema 是否存在于 PostgreSQL。
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT EXISTS (
            SELECT FROM information_schema.schemata
            WHERE schema_name = %s
        )
        """,
        (schema,)
    )
    exists = cursor.fetchone()[0]
    cursor.close()
    return exists


def check_table_exists(conn, schema: str, table: str) -> bool:
    """
    Check if a table exists in PostgreSQL.
    检查表是否存在于 PostgreSQL。
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = %s
            AND table_name = %s
        )
        """,
        (schema, table)
    )
    exists = cursor.fetchone()[0]
    cursor.close()
    return exists


def check_table_row_count(conn, schema: str, table: str) -> int:
    """
    Get row count of a table.
    获取表的行数。
    """
    full_table_name = f"{schema}.{table}"
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {full_table_name}")
    count = cursor.fetchone()[0]
    cursor.close()
    return count


def check_column_exists(conn, schema: str, table: str, column: str) -> bool:
    """
    Check if a column exists in a table.
    检查列是否存在于表中。
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT EXISTS (
            SELECT FROM information_schema.columns
            WHERE table_schema = %s
            AND table_name = %s
            AND column_name = %s
        )
        """,
        (schema, table, column)
    )
    exists = cursor.fetchone()[0]
    cursor.close()
    return exists


def run_ods_checks(conn) -> list:
    """
    Run all ODS checks and return check results.
    运行所有 ODS 检查并返回检查结果。
    """
    print("[INFO] Running ODS table checks...")

    check_results = []

    # Check schemas
    # 检查 schemas
    expected_schemas = ["ods", "dwd", "dws", "ads"]

    for schema in expected_schemas:
        exists = check_schema_exists(conn, schema)
        status = "PASS" if exists else "FAIL"

        check_results.append({
            "check_type": "schema_exists",
            "schema": schema,
            "table": "",
            "column": "",
            "expected": "exists",
            "actual": "exists" if exists else "not exists",
            "status": status,
            "message": f"Schema {schema} check" if exists else f"Schema {schema} not found",
        })

        print(f"  Schema {schema}: {status}")

    # Check tables
    # 检查表
    for schema, table in EXPECTED_ODS_TABLES:
        full_table_name = f"{schema}.{table}"

        # Check table exists
        # 检查表存在
        table_exists = check_table_exists(conn, schema, table)

        check_results.append({
            "check_type": "table_exists",
            "schema": schema,
            "table": table,
            "column": "",
            "expected": "exists",
            "actual": "exists" if table_exists else "not exists",
            "status": "PASS" if table_exists else "FAIL",
            "message": f"Table {full_table_name} exists" if table_exists else f"Table {full_table_name} not found",
        })

        print(f"  Table {full_table_name} exists: {'PASS' if table_exists else 'FAIL'}")

        if not table_exists:
            continue

        # Check row count > 0
        # 检查行数 > 0
        row_count = check_table_row_count(conn, schema, table)

        check_results.append({
            "check_type": "row_count_positive",
            "schema": schema,
            "table": table,
            "column": "",
            "expected": "> 0",
            "actual": str(row_count),
            "status": "PASS" if row_count > 0 else "FAIL",
            "message": f"Table {full_table_name} has {row_count} rows",
        })

        print(f"  Table {full_table_name} row count: {row_count} ({'PASS' if row_count > 0 else 'FAIL'})")

        # Check loaded_at column exists
        # 检查 loaded_at 列存在
        loaded_at_exists = check_column_exists(conn, schema, table, "loaded_at")

        check_results.append({
            "check_type": "column_exists",
            "schema": schema,
            "table": table,
            "column": "loaded_at",
            "expected": "exists",
            "actual": "exists" if loaded_at_exists else "not exists",
            "status": "PASS" if loaded_at_exists else "FAIL",
            "message": f"Column loaded_at in {full_table_name}",
        })

        print(f"  Table {full_table_name} has loaded_at: {'PASS' if loaded_at_exists else 'FAIL'}")

        # Check dt column exists
        # 检查 dt 列存在
        dt_exists = check_column_exists(conn, schema, table, "dt")

        check_results.append({
            "check_type": "column_exists",
            "schema": schema,
            "table": table,
            "column": "dt",
            "expected": "exists",
            "actual": "exists" if dt_exists else "not exists",
            "status": "PASS" if dt_exists else "FAIL",
            "message": f"Column dt in {full_table_name}",
        })

        print(f"  Table {full_table_name} has dt: {'PASS' if dt_exists else 'FAIL'}")

    # Check raw CSV row count equals loaded row count for each ODS table
    # 检查每个 ODS 表的原始 CSV 行数是否等于加载行数
    print("  Checking raw CSV vs loaded row count equality...")
    for schema, table in EXPECTED_ODS_TABLES:
        result = check_raw_vs_loaded_row_count(conn, schema, table)
        check_results.append(result)
        print(f"  {schema}.{table} raw vs loaded: {result['status']}")

    return check_results


def check_raw_vs_loaded_row_count(conn, schema: str, table: str) -> dict:
    """
    Check that raw CSV row count equals PostgreSQL loaded row count.
    检查原始 CSV 行数是否等于 PostgreSQL 加载行数。

    ODS design principle: ODS should preserve all raw source rows.
    ODS 设计原则：ODS 应保留所有原始源数据行。
    """
    csv_file = TABLE_TO_CSV_MAPPING.get(table)
    if csv_file is None:
        return {
            "check_type": "raw_row_count_match",
            "schema": schema,
            "table": table,
            "column": "",
            "expected": "raw CSV row count",
            "actual": "unknown",
            "status": "PASS",
            "message": f"No raw CSV mapping defined for {schema}.{table}, skipping",
        }

    csv_path = RAW_DATA_DIR / csv_file

    if not csv_path.exists():
        return {
            "check_type": "raw_row_count_match",
            "schema": schema,
            "table": table,
            "column": "",
            "expected": f"CSV file {csv_file} exists",
            "actual": "not found",
            "status": "FAIL",
            "message": f"Raw CSV file not found: {csv_path}",
        }

    # Read raw CSV row count using chunking for large files
    # 使用分块读取方式计算原始 CSV 行数（支持大文件）
    chunk_iter = pd.read_csv(csv_path, low_memory=False, usecols=[0], chunksize=100000)
    raw_row_count = sum(len(chunk) for chunk in chunk_iter)

    # Get loaded row count from PostgreSQL
    # 从 PostgreSQL 获取加载行数
    full_table_name = f"{schema}.{table}"
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {full_table_name}")
    loaded_row_count = cursor.fetchone()[0]
    cursor.close()

    # Compare
    # 比较
    match = raw_row_count == loaded_row_count
    status = "PASS" if match else "FAIL"

    result = {
        "check_type": "raw_row_count_match",
        "schema": schema,
        "table": table,
        "column": "",
        "expected": str(raw_row_count),
        "actual": str(loaded_row_count),
        "status": status,
        "message": f"Raw CSV rows: {raw_row_count}, Loaded rows: {loaded_row_count} ({'match' if match else 'MISMATCH'})",
    }

    return result


def generate_check_report(check_results: list):
    """
    Generate check report CSV.
    生成检查报告 CSV。
    """
    print("[INFO] Generating check report...")

    report_df = pd.DataFrame(check_results)
    report_path = DOCS_DIR / "postgres_ods_check_report.csv"
    report_df.to_csv(report_path, index=False, encoding="utf-8-sig")

    print(f"[OK] Check report generated: {report_path}")


def generate_check_summary(check_results: list):
    """
    Generate bilingual check summary markdown.
    生成双语检查总结 Markdown。
    """
    print("[INFO] Generating check summary...")

    summary_path = DOCS_DIR / "postgres_ods_check_summary.md"

    total_checks = len(check_results)
    passed_checks = sum(1 for r in check_results if r["status"] == "PASS")
    failed_checks = total_checks - passed_checks

    # Count by check type
    # 按检查类型计数
    schema_checks = [r for r in check_results if r["check_type"] == "schema_exists"]
    table_checks = [r for r in check_results if r["check_type"] == "table_exists"]
    row_checks = [r for r in check_results if r["check_type"] == "row_count_positive"]
    column_checks = [r for r in check_results if r["check_type"] == "column_exists"]
    raw_match_checks = [r for r in check_results if r["check_type"] == "raw_row_count_match" and r["status"] != "skipped"]

    with summary_path.open("w", encoding="utf-8") as f:
        f.write("# PostgreSQL ODS Check Summary / PostgreSQL ODS 检查总结\n\n")
        f.write(f"Generated at / 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Overall summary
        # 总体总结
        f.write("## 1. Overall Summary / 总体结果\n\n")
        f.write("| Metric / 指标 | Value / 数值 |\n")
        f.write("|---|---:|\n")
        f.write(f"| Total checks / 总检查数 | {total_checks} |\n")
        f.write(f"| Passed checks / 通过检查数 | {passed_checks} |\n")
        f.write(f"| Failed checks / 失败检查数 | {failed_checks} |\n\n")

        if failed_checks == 0:
            f.write("**All ODS checks passed.**\n\n")
            f.write("**所有 ODS 检查通过。**\n\n")
        else:
            f.write(f"**{failed_checks} checks failed.**\n\n")
            f.write(f"**{failed_checks} 个检查失败。**\n\n")

        # Check type summary
        # 检查类型总结
        f.write("## 2. Check Type Summary / 检查类型总结\n\n")
        f.write("| Check Type / 检查类型 | Total / 总数 | Passed / 通过 | Failed / 失败 |\n")
        f.write("|---|---:|---:|---:|\n")
        f.write(f"| Schema exists / Schema 存在 | {len(schema_checks)} | {sum(1 for r in schema_checks if r['status'] == 'PASS')} | {sum(1 for r in schema_checks if r['status'] == 'FAIL')} |\n")
        f.write(f"| Table exists / 表存在 | {len(table_checks)} | {sum(1 for r in table_checks if r['status'] == 'PASS')} | {sum(1 for r in table_checks if r['status'] == 'FAIL')} |\n")
        f.write(f"| Row count positive / 行数大于0 | {len(row_checks)} | {sum(1 for r in row_checks if r['status'] == 'PASS')} | {sum(1 for r in row_checks if r['status'] == 'FAIL')} |\n")
        f.write(f"| Column exists / 列存在 | {len(column_checks)} | {sum(1 for r in column_checks if r['status'] == 'PASS')} | {sum(1 for r in column_checks if r['status'] == 'FAIL')} |\n")
        f.write(f"| Raw row count match / 原始行数匹配 | {len(raw_match_checks)} | {sum(1 for r in raw_match_checks if r['status'] == 'PASS')} | {sum(1 for r in raw_match_checks if r['status'] == 'FAIL')} |\n\n")

        # ODS tables row count
        # ODS 表行数
        f.write("## 3. ODS Tables Row Count / ODS 表行数\n\n")
        f.write("| Schema | Table / 表 | Row Count / 行数 |\n")
        f.write("|---|---|---:|\n")

        for r in row_checks:
            f.write(f"| {r['schema']} | {r['table']} | {r['actual']} |\n")

        f.write("\n")

        # Failed checks details
        # 失败检查详情
        if failed_checks > 0:
            f.write("## 4. Failed Checks Details / 失败检查详情\n\n")
            f.write("The following checks failed:\n\n")
            f.write("以下检查失败：\n\n")

            for r in check_results:
                if r["status"] == "FAIL":
                    f.write(f"- **{r['check_type']}**: {r['schema']}.{r['table']}\n")
                    f.write(f"  - Expected: {r['expected']}\n")
                    f.write(f"  - Actual: {r['actual']}\n")
                    f.write(f"  - Message: {r['message']}\n\n")
        else:
            f.write("## 4. Failed Checks Details / 失败检查详情\n\n")
            f.write("No checks failed.\n\n")
            f.write("无失败检查。\n\n")

        # Output files
        # 输出文件
        f.write("## 5. Output Files / 输出文件\n\n")
        f.write("The detailed check report is available at:\n\n")
        f.write("详细检查报告生成在：\n\n")
        f.write("- `docs/postgres_ods_check_report.csv`\n\n")

    print(f"[OK] Check summary generated: {summary_path}")


def main():
    """
    Main entry point for ODS check.
    ODS 检查的主入口。
    """
    print("=" * 60)
    print("[INFO] PostgreSQL ODS Table Check")
    print("=" * 60)

    # Create database connection
    # 创建数据库连接
    try:
        conn = get_connection()
        print("[OK] PostgreSQL connection successful.")
    except psycopg2.OperationalError as e:
        print("[ERROR] Cannot connect to PostgreSQL.")
        print(f"[ERROR] {e}")
        print("[INFO] Please ensure PostgreSQL is running:")
        print("  docker compose -f docker-compose.postgres.yml up -d")
        sys.exit(1)

    # Run checks
    # 运行检查
    check_results = run_ods_checks(conn)

    # Generate reports
    # 生成报告
    generate_check_report(check_results)
    generate_check_summary(check_results)

    # Print summary
    # 打印总结
    total_checks = len(check_results)
    passed_checks = sum(1 for r in check_results if r["status"] == "PASS")
    failed_checks = total_checks - passed_checks

    print("=" * 60)
    print("[CHECK SUMMARY]")
    print(f"Total checks: {total_checks}")
    print(f"Passed: {passed_checks}")
    print(f"Failed: {failed_checks}")
    print("=" * 60)

    if failed_checks > 0:
        print("[WARN] Some checks failed. Please review the check report.")
    else:
        print("[DONE] All ODS checks passed.")

    conn.close()

    print("=" * 60)
    print("[DONE] PostgreSQL ODS check completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()