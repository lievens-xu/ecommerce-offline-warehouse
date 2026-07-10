"""
Run the business-analysis pipeline (RFM, product category, geography).

运行业务分析主流程（RFM、商品类目、地域）。

These analyses sit on top of the core DWD/ODS layers and produce ADS-level
marketing and merchandising views. Run the core pipeline first:
    python scripts/run_pipeline.py

以下分析构建在核心 DWD/ODS 层之上，产出 ADS 级的营销与商品分析视图。
请先运行核心主流程：
    python scripts/run_pipeline.py
"""

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT_DIR / "scripts"
DOCS_DIR = ROOT_DIR / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)


ANALYSIS_STEPS = [
    {
        "step_order": 1,
        "step_name": "Customer RFM Segmentation",
        "script": "build_ads_customer_rfm.py",
    },
    {
        "step_order": 2,
        "step_name": "Product Category Ranking",
        "script": "build_ads_product_category_rank.py",
    },
    {
        "step_order": 3,
        "step_name": "Geographic State Summary",
        "script": "build_ads_geo_state_summary.py",
    },
]


def run_step(step: dict) -> dict:
    """
    Run one analysis step as a subprocess.
    以子进程方式运行一个分析步骤。
    """
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
    print("[INFO] Starting business-analysis pipeline ...")
    print(f"[INFO] Project root: {ROOT_DIR}")

    results = []
    for step in ANALYSIS_STEPS:
        result = run_step(step)
        results.append(result)
        if result["status"] == "FAIL":
            print(f"[FAIL] Stopping: {step['step_name']} failed.")
            break

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")

    print("=" * 80)
    print("[ANALYSIS PIPELINE SUMMARY]")
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total steps: {len(results)} | Passed: {passed} | Failed: {failed}")
    print("=" * 80)

    if failed:
        sys.exit(1)
    print("[DONE] Business-analysis pipeline completed successfully.")


if __name__ == "__main__":
    main()
