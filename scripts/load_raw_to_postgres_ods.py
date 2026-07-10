"""
Load Raw CSV Files to PostgreSQL ODS Tables
将原始 CSV 文件加载到 PostgreSQL ODS 表

This script reads raw Olist CSV files and loads them into PostgreSQL ODS tables.
本脚本读取原始 Olist CSV 文件并将其加载到 PostgreSQL ODS 表。
"""

from pathlib import Path
from datetime import datetime
import pandas as pd
import psycopg2
import psycopg2.extras
import sys
import os


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"
SQL_DIR = ROOT_DIR / "sql" / "postgres"
DOCS_DIR = ROOT_DIR / "docs"

DOCS_DIR.mkdir(parents=True, exist_ok=True)


# Database connection configuration
# 数据库连接配置
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5433")
DB_NAME = os.getenv("POSTGRES_DB", "ecommerce_warehouse")
DB_USER = os.getenv("POSTGRES_USER", "warehouse_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "warehouse_pass")


# Raw CSV file to ODS table mapping
# 原始 CSV 文件到 ODS 表的映射
RAW_TO_ODS_MAPPING = {
    "olist_customers_dataset.csv": ("ods", "customers"),
    "olist_orders_dataset.csv": ("ods", "orders"),
    "olist_order_items_dataset.csv": ("ods", "order_items"),
    "olist_order_payments_dataset.csv": ("ods", "order_payments"),
    "olist_order_reviews_dataset.csv": ("ods", "order_reviews"),
    "olist_products_dataset.csv": ("ods", "products"),
    "olist_sellers_dataset.csv": ("ods", "sellers"),
    "olist_geolocation_dataset.csv": ("ods", "geolocation"),
    "product_category_name_translation.csv": ("ods", "product_category_translation"),
}


def get_connection():
    """
    Create psycopg2 connection for PostgreSQL.
    创建 PostgreSQL 的 psycopg2 连接。
    """
    print(f"[INFO] Connecting to PostgreSQL: {DB_HOST}:{DB_PORT}/{DB_NAME}")

    # Use DSN format for connection
    # 使用 DSN 格式连接
    dsn = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"

    conn = psycopg2.connect(dsn)

    print("[OK] PostgreSQL connection successful.")
    return conn


def execute_sql_file(conn, sql_file_path: Path):
    """
    Execute SQL file against the database.
    执行 SQL 文件。
    """
    print(f"[INFO] Executing SQL file: {sql_file_path}")

    with open(sql_file_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    cursor = conn.cursor()

    # Execute the SQL content
    # 执行 SQL 内容
    try:
        cursor.execute(sql_content)
        conn.commit()
        print(f"[OK] SQL file executed: {sql_file_path}")
    except psycopg2.errors.DuplicateSchema as e:
        # Ignore duplicate schema errors
        # 忽略重复 schema 错误
        print(f"[WARN] Schema already exists, skipping")
        conn.commit()
    except psycopg2.errors.DuplicateTable as e:
        # Ignore duplicate table errors
        # 忽略重复表错误
        print(f"[WARN] Table already exists, skipping")
        conn.commit()
    except Exception as e:
        print(f"[ERROR] SQL execution error: {e}")
        conn.rollback()
        raise

    cursor.close()


def setup_schemas_and_tables(conn):
    """
    Create schemas and ODS tables by executing SQL files.
    通过执行 SQL 文件创建 schema 和 ODS 表。
    """
    print("[INFO] Setting up schemas and tables...")

    # Execute schema creation SQL
    # 执行 schema 创建 SQL
    schema_sql = SQL_DIR / "01_create_schemas.sql"
    if schema_sql.exists():
        execute_sql_file(conn, schema_sql)
    else:
        print(f"[WARN] Schema SQL file not found: {schema_sql}")

    # Execute ODS tables creation SQL
    # 执行 ODS 表创建 SQL
    tables_sql = SQL_DIR / "02_create_ods_tables.sql"
    if tables_sql.exists():
        execute_sql_file(conn, tables_sql)
    else:
        print(f"[WARN] Tables SQL file not found: {tables_sql}")

    print("[OK] Schemas and tables setup completed.")


def validate_raw_files():
    """
    Validate that all required raw CSV files exist.
    验证所有必需的原始 CSV 文件存在。
    """
    print("[INFO] Validating raw CSV files...")

    missing_files = []

    for csv_file, (_, _) in RAW_TO_ODS_MAPPING.items():
        file_path = RAW_DATA_DIR / csv_file
        if not file_path.exists():
            missing_files.append(csv_file)

    if missing_files:
        print("[ERROR] Missing raw CSV files:")
        for f in missing_files:
            print(f"  - {f}")
        raise FileNotFoundError(f"Missing {len(missing_files)} raw CSV files in {RAW_DATA_DIR}")

    print(f"[OK] All {len(RAW_TO_ODS_MAPPING)} raw CSV files found.")


def load_csv_to_postgres(conn, csv_file: str, schema: str, table: str) -> dict:
    """
    Load a single CSV file into PostgreSQL ODS table.
    将单个 CSV 文件加载到 PostgreSQL ODS 表。

    Returns dict with load statistics.
    返回加载统计信息的字典。
    """
    csv_path = RAW_DATA_DIR / csv_file
    full_table_name = f"{schema}.{table}"

    print(f"[INFO] Loading: {csv_file} -> {full_table_name}")

    # Read CSV file
    # 读取 CSV 文件
    df = pd.read_csv(csv_path, low_memory=False, encoding="utf-8", na_values=['', 'NaN', 'nan'])
    raw_row_count = len(df)
    raw_column_count = len(df.columns)

    # Replace NaN with None for proper NULL handling in PostgreSQL
    # 将 NaN 替换为 None 以便 PostgreSQL 正确处理 NULL
    df = df.where(pd.notna(df), None)

    # Also replace empty strings with None
    # 同时将空字符串替换为 None
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].replace('', None)

    # Add technical fields
    # 添加技术字段
    now = datetime.now()
    df["loaded_at"] = now
    df["dt"] = now.date()

    # Truncate existing table
    # 清空现有表
    cursor = conn.cursor()
    cursor.execute(f"TRUNCATE TABLE {full_table_name}")
    conn.commit()

    # Insert data using execute_values for efficiency
    # 使用 execute_values 高效插入数据
    columns = list(df.columns)

    # Convert DataFrame rows to list of tuples, handling None values
    # 将 DataFrame 行转换为元组列表，处理 None 值
    values = []
    for row in df.itertuples(index=False, name=None):
        # Convert numpy.nan to None explicitly
        # 显式将 numpy.nan 转换为 None
        row_tuple = tuple(None if (pd.isna(x) or (isinstance(x, float) and str(x) == 'nan')) else x for x in row)
        values.append(row_tuple)

    insert_sql = f"""
        INSERT INTO {full_table_name} ({', '.join(columns)})
        VALUES %s
    """

    cursor = conn.cursor()
    psycopg2.extras.execute_values(
        cursor,
        insert_sql,
        values,
        template=None,
        page_size=1000
    )
    conn.commit()

    # Verify loaded row count
    # 验证加载的行数
    cursor.execute(f"SELECT COUNT(*) FROM {full_table_name}")
    loaded_row_count = cursor.fetchone()[0]
    cursor.close()

    status = "PASS" if loaded_row_count == raw_row_count else "FAIL"

    load_stats = {
        "csv_file": csv_file,
        "schema": schema,
        "table": table,
        "full_table_name": full_table_name,
        "raw_row_count": raw_row_count,
        "raw_column_count": raw_column_count,
        "loaded_row_count": loaded_row_count,
        "row_count_match": loaded_row_count == raw_row_count,
        "status": status,
        "loaded_at": now.strftime("%Y-%m-%d %H:%M:%S"),
    }

    if status == "PASS":
        print(f"[OK] {full_table_name}: {loaded_row_count} rows loaded (match)")
    else:
        print(f"[WARN] {full_table_name}: {loaded_row_count} rows loaded, expected {raw_row_count}")

    return load_stats


def generate_load_report(load_stats_list: list):
    """
    Generate ODS load report CSV.
    生成 ODS 加载报告 CSV。
    """
    print("[INFO] Generating load report...")

    report_df = pd.DataFrame(load_stats_list)
    report_path = DOCS_DIR / "postgres_ods_load_report.csv"
    report_df.to_csv(report_path, index=False, encoding="utf-8-sig")

    print(f"[OK] Load report generated: {report_path}")

    # Print summary
    # 打印总结
    total_tables = len(load_stats_list)
    passed_tables = sum(1 for s in load_stats_list if s["status"] == "PASS")
    failed_tables = total_tables - passed_tables

    print("=" * 60)
    print("[LOAD SUMMARY]")
    print(f"Total tables: {total_tables}")
    print(f"Passed: {passed_tables}")
    print(f"Failed: {failed_tables}")
    print("=" * 60)

    if failed_tables > 0:
        print("[WARN] Some tables failed row count validation.")
        for s in load_stats_list:
            if s["status"] == "FAIL":
                print(f"  - {s['full_table_name']}: {s['loaded_row_count']} loaded, {s['raw_row_count']} expected")
    else:
        print("[DONE] All ODS tables loaded successfully.")


def main():
    """
    Main entry point for raw CSV to PostgreSQL ODS loading.
    原始 CSV 到 PostgreSQL ODS 加载的主入口。
    """
    print("=" * 60)
    print("[INFO] Loading Raw CSV Files to PostgreSQL ODS Tables")
    print("=" * 60)

    # Validate raw files
    # 验证原始文件
    validate_raw_files()

    # Create database connection
    # 创建数据库连接
    try:
        conn = get_connection()
    except psycopg2.OperationalError as e:
        print("[ERROR] Cannot connect to PostgreSQL.")
        print(f"[ERROR] {e}")
        print("[INFO] Please ensure PostgreSQL is running:")
        print("  docker compose -f docker-compose.postgres.yml up -d")
        sys.exit(1)

    # Setup schemas and tables
    # 设置 schema 和表
    setup_schemas_and_tables(conn)

    # Load each CSV file
    # 加载每个 CSV 文件
    load_stats_list = []

    for csv_file, (schema, table) in RAW_TO_ODS_MAPPING.items():
        try:
            stats = load_csv_to_postgres(conn, csv_file, schema, table)
            load_stats_list.append(stats)
        except Exception as e:
            print(f"[ERROR] Failed to load {csv_file}: {e}")
            conn.rollback()  # Reset transaction state for next tables / 重置事务状态以便后续表继续加载
            load_stats_list.append({
                "csv_file": csv_file,
                "schema": schema,
                "table": table,
                "full_table_name": f"{schema}.{table}",
                "raw_row_count": 0,
                "raw_column_count": 0,
                "loaded_row_count": 0,
                "row_count_match": False,
                "status": "ERROR",
                "loaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })

    # Generate report
    # 生成报告
    generate_load_report(load_stats_list)

    # Close connection
    # 关闭连接
    conn.close()

    print("=" * 60)
    print("[DONE] PostgreSQL ODS loading completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()