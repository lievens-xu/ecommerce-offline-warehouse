from pathlib import Path
from datetime import datetime
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data" / "raw"
ODS_DIR = ROOT_DIR / "data" / "ods"
DOCS_DIR = ROOT_DIR / "docs"

ODS_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)


SOURCE_TO_ODS_TABLE = {
    "olist_customers_dataset.csv": "ods_customers",
    "olist_orders_dataset.csv": "ods_orders",
    "olist_order_items_dataset.csv": "ods_order_items",
    "olist_order_payments_dataset.csv": "ods_order_payments",
    "olist_order_reviews_dataset.csv": "ods_order_reviews",
    "olist_products_dataset.csv": "ods_products",
    "olist_sellers_dataset.csv": "ods_sellers",
    "olist_geolocation_dataset.csv": "ods_geolocation",
    "product_category_name_translation.csv": "ods_product_category_translation",
}


def read_csv_safely(file_path: Path) -> pd.DataFrame:
    """
    Read a CSV file with multiple encoding fallbacks.
    """
    encodings = ["utf-8", "utf-8-sig", "latin1"]

    last_error = None
    for encoding in encodings:
        try:
            return pd.read_csv(file_path, encoding=encoding, low_memory=False)
        except Exception as e:
            last_error = e

    raise RuntimeError(f"Failed to read {file_path.name}: {last_error}")


def validate_required_files() -> None:
    """
    Check whether all expected source CSV files exist.
    """
    missing_files = []

    for source_file in SOURCE_TO_ODS_TABLE.keys():
        file_path = RAW_DIR / source_file
        if not file_path.exists():
            missing_files.append(source_file)

    if missing_files:
        missing_text = "\n".join(f"- {file_name}" for file_name in missing_files)
        raise FileNotFoundError(
            f"The following required raw files are missing in {RAW_DIR}:\n{missing_text}"
        )


def load_one_file(source_file: str, ods_table: str, etl_date: str) -> dict:
    """
    Load one raw CSV file into the ODS layer.
    """
    source_path = RAW_DIR / source_file
    output_path = ODS_DIR / f"{ods_table}.csv"

    print(f"[INFO] Loading {source_file} -> {ods_table}.csv")

    df = read_csv_safely(source_path)

    original_row_count = len(df)
    original_column_count = len(df.columns)

    loaded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    df["loaded_at"] = loaded_at
    df["dt"] = etl_date

    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    output_row_count = len(df)
    output_column_count = len(df.columns)

    return {
        "source_file": source_file,
        "ods_table": ods_table,
        "output_file": str(output_path.relative_to(ROOT_DIR)),
        "original_row_count": original_row_count,
        "original_column_count": original_column_count,
        "output_row_count": output_row_count,
        "output_column_count": output_column_count,
        "loaded_at": loaded_at,
        "dt": etl_date,
        "status": "success",
    }


def generate_load_report(load_results: list) -> None:
    """
    Generate a CSV load report for ODS loading.
    """
    report_df = pd.DataFrame(load_results)
    report_path = DOCS_DIR / "ods_load_report.csv"
    report_df.to_csv(report_path, index=False, encoding="utf-8-sig")

    print(f"[OK] ODS load report generated: {report_path}")


def main() -> None:
    """
    Main entry point.
    """
    validate_required_files()

    etl_date = datetime.now().strftime("%Y-%m-%d")
    load_results = []

    for source_file, ods_table in SOURCE_TO_ODS_TABLE.items():
        result = load_one_file(source_file, ods_table, etl_date)
        load_results.append(result)

    generate_load_report(load_results)

    print("[DONE] Raw data has been loaded into the ODS layer.")
    print(f"[DONE] ODS output directory: {ODS_DIR}")


if __name__ == "__main__":
    main()