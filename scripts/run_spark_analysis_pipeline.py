"""
Run the Spark SQL business-analysis pipeline (RFM, category, geography).

运行 Spark SQL 业务分析主流程（RFM、类目、地域）。

Spark counterpart of scripts/run_analysis_pipeline.py. Each step builds a
*_spark.csv and writes a Pandas-vs-Spark comparison report. Run the Spark core
pipeline first: python scripts/run_spark_pipeline.py

scripts/run_analysis_pipeline.py 的 Spark 版本。每步产出 *_spark.csv 并写入
Pandas 与 Spark 对比报告。请先运行 Spark 核心主流程：
    python scripts/run_spark_pipeline.py
"""

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT_DIR / "scripts"

SPARK_ANALYSIS_STEPS = [
    {"step_order": 1, "step_name": "Spark Customer RFM", "script": "spark_build_ads_customer_rfm.py"},
    {"step_order": 2, "step_name": "Spark Product Category Rank", "script": "spark_build_ads_product_category_rank.py"},
    {"step_order": 3, "step_name": "Spark Geo State Summary", "script": "spark_build_ads_geo_state_summary.py"},
]


def run_step(step: dict) -> dict:
    """Run one Spark analysis step as a subprocess. 以子进程运行一个 Spark 分析步骤。"""
    script_path = SCRIPTS_DIR / step["script"]
    start = time.perf_counter()

    print("=" * 80)
    print(f"[STEP {step['step_order']}] {step['step_name']} ({step['script']})")
    print("=" * 80)

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.stdout.strip():
        print(result.stdout)
    if result.stderr.strip():
        print("[STDERR]")
        print(result.stderr)

    status = "PASS" if result.returncode == 0 else "FAIL"
    print(f"[{status}] {step['step_name']}")
    return {
        "step_order": step["step_order"],
        "step_name": step["step_name"],
        "script": step["script"],
        "status": status,
        "duration_seconds": round(time.perf_counter() - start, 2),
    }


def main() -> None:
    print("[INFO] Starting Spark business-analysis pipeline ...")
    print(f"[INFO] Project root: {ROOT_DIR}")

    results = []
    for step in SPARK_ANALYSIS_STEPS:
        result = run_step(step)
        results.append(result)
        if result["status"] == "FAIL":
            print(f"[FAIL] Stopping: {step['step_name']} failed.")
            break

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")

    print("=" * 80)
    print("[SPARK ANALYSIS PIPELINE SUMMARY]")
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total steps: {len(results)} | Passed: {passed} | Failed: {failed}")
    print("=" * 80)

    if failed:
        sys.exit(1)
    print("[DONE] Spark business-analysis pipeline completed successfully.")


if __name__ == "__main__":
    main()
