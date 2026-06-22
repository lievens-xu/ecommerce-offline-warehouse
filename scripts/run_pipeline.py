from pathlib import Path
from datetime import datetime
import subprocess
import sys
import time
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT_DIR / "scripts"
DOCS_DIR = ROOT_DIR / "docs"

DOCS_DIR.mkdir(parents=True, exist_ok=True)


PIPELINE_STEPS = [
    {
        "step_order": 1,
        "step_name": "Raw Data Profiling",
        "script": "check_raw_data.py",
        "description": "Profile raw CSV files and generate raw data profiling reports.",
    },
    {
        "step_order": 2,
        "step_name": "Raw to ODS Loading",
        "script": "load_raw_to_ods.py",
        "description": "Load raw CSV files into the ODS layer with technical fields.",
    },
    {
        "step_order": 3,
        "step_name": "DWD Order Detail Building",
        "script": "build_dwd_order_detail.py",
        "description": "Build the DWD order-level detail wide table.",
    },
    {
        "step_order": 4,
        "step_name": "DWS Daily Order Summary Building",
        "script": "build_dws_daily_order_summary.py",
        "description": "Build the DWS daily order summary table.",
    },
    {
        "step_order": 5,
        "step_name": "ADS Daily Business Overview Building",
        "script": "build_ads_daily_business_overview.py",
        "description": "Build the ADS dashboard-ready daily business overview table.",
    },
    {
        "step_order": 6,
        "step_name": "Data Quality Checks",
        "script": "run_data_quality_checks.py",
        "description": "Run data quality checks across ODS, DWD, DWS, ADS, and cross-layer metrics.",
    },
    {
        "step_order": 7,
        "step_name": "Dashboard Chart Building",
        "script": "build_dashboard_charts.py",
        "description": "Generate dashboard charts and KPI summary from the ADS layer.",
    },
]


def now_str() -> str:
    """
    Return current timestamp as string.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def run_one_step(step: dict) -> dict:
    """
    Run one pipeline step as a subprocess.
    """
    script_path = SCRIPTS_DIR / step["script"]

    start_time = now_str()
    start_perf = time.perf_counter()

    if not script_path.exists():
        end_time = now_str()
        duration_seconds = round(time.perf_counter() - start_perf, 2)

        return {
            "step_order": step["step_order"],
            "step_name": step["step_name"],
            "script": step["script"],
            "status": "FAIL",
            "return_code": -1,
            "start_time": start_time,
            "end_time": end_time,
            "duration_seconds": duration_seconds,
            "description": step["description"],
            "error_message": f"Script not found: {script_path}",
            "stdout": "",
            "stderr": "",
        }

    print("=" * 80)
    print(f"[STEP {step['step_order']}] {step['step_name']}")
    print(f"[INFO] Running script: {step['script']}")
    print("=" * 80)

    completed_process = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    end_time = now_str()
    duration_seconds = round(time.perf_counter() - start_perf, 2)

    stdout = completed_process.stdout or ""
    stderr = completed_process.stderr or ""
    return_code = completed_process.returncode

    if stdout.strip():
        print(stdout)

    if stderr.strip():
        print("[STDERR]")
        print(stderr)

    status = "PASS" if return_code == 0 else "FAIL"

    if status == "PASS":
        print(f"[OK] Step completed: {step['step_name']}")
    else:
        print(f"[FAIL] Step failed: {step['step_name']}")

    return {
        "step_order": step["step_order"],
        "step_name": step["step_name"],
        "script": step["script"],
        "status": status,
        "return_code": return_code,
        "start_time": start_time,
        "end_time": end_time,
        "duration_seconds": duration_seconds,
        "description": step["description"],
        "error_message": stderr.strip() if status == "FAIL" else "",
        "stdout": stdout,
        "stderr": stderr,
    }


def build_skipped_result(step: dict, reason: str) -> dict:
    """
    Build a skipped step result when previous step failed.
    """
    current_time = now_str()

    return {
        "step_order": step["step_order"],
        "step_name": step["step_name"],
        "script": step["script"],
        "status": "SKIPPED",
        "return_code": "",
        "start_time": current_time,
        "end_time": current_time,
        "duration_seconds": 0,
        "description": step["description"],
        "error_message": reason,
        "stdout": "",
        "stderr": "",
    }


def save_pipeline_report(results: list) -> None:
    """
    Save pipeline run report and latest run log.
    """
    report_columns = [
        "step_order",
        "step_name",
        "script",
        "status",
        "return_code",
        "start_time",
        "end_time",
        "duration_seconds",
        "description",
        "error_message",
    ]

    report_df = pd.DataFrame(results)
    report_path = DOCS_DIR / "pipeline_run_report.csv"
    report_df[report_columns].to_csv(report_path, index=False, encoding="utf-8-sig")

    log_path = DOCS_DIR / "pipeline_latest_run.log"

    with log_path.open("w", encoding="utf-8") as f:
        f.write("E-commerce Offline Data Warehouse Pipeline Log\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Generated at: {now_str()}\n\n")

        for result in results:
            f.write("=" * 80 + "\n")
            f.write(f"Step {result['step_order']}: {result['step_name']}\n")
            f.write(f"Script: {result['script']}\n")
            f.write(f"Status: {result['status']}\n")
            f.write(f"Return code: {result['return_code']}\n")
            f.write(f"Start time: {result['start_time']}\n")
            f.write(f"End time: {result['end_time']}\n")
            f.write(f"Duration seconds: {result['duration_seconds']}\n")
            f.write(f"Description: {result['description']}\n")

            if result["error_message"]:
                f.write(f"\nError message:\n{result['error_message']}\n")

            if result["stdout"]:
                f.write("\nSTDOUT:\n")
                f.write(result["stdout"])
                f.write("\n")

            if result["stderr"]:
                f.write("\nSTDERR:\n")
                f.write(result["stderr"])
                f.write("\n")

            f.write("\n")

    print(f"[OK] Pipeline report generated: {report_path}")
    print(f"[OK] Pipeline log generated: {log_path}")


def generate_pipeline_summary(results: list) -> None:
    """
    Generate a bilingual markdown summary for the latest pipeline run.
    """
    summary_path = DOCS_DIR / "pipeline_run_summary.md"

    total_steps = len(results)
    passed_steps = sum(1 for item in results if item["status"] == "PASS")
    failed_steps = sum(1 for item in results if item["status"] == "FAIL")
    skipped_steps = sum(1 for item in results if item["status"] == "SKIPPED")
    total_duration = round(sum(float(item["duration_seconds"]) for item in results), 2)

    with summary_path.open("w", encoding="utf-8") as f:
        f.write("# Pipeline Run Summary / 主流程运行总结\n\n")

        f.write("## 1. Overall Result / 总体结果\n\n")
        f.write("| Metric / 指标 | Value / 数值 |\n")
        f.write("|---|---:|\n")
        f.write(f"| Total steps / 总步骤数 | {total_steps} |\n")
        f.write(f"| Passed steps / 通过步骤数 | {passed_steps} |\n")
        f.write(f"| Failed steps / 失败步骤数 | {failed_steps} |\n")
        f.write(f"| Skipped steps / 跳过步骤数 | {skipped_steps} |\n")
        f.write(f"| Total duration seconds / 总耗时秒数 | {total_duration} |\n\n")

        f.write("## 2. Step Details / 步骤明细\n\n")
        f.write("| Order / 顺序 | Step / 步骤 | Script / 脚本 | Status / 状态 | Duration / 耗时秒 |\n")
        f.write("|---:|---|---|---|---:|\n")

        for item in results:
            f.write(
                f"| {item['step_order']} "
                f"| {item['step_name']} "
                f"| `{item['script']}` "
                f"| {item['status']} "
                f"| {item['duration_seconds']} |\n"
            )

        f.write("\n## 3. Output Files / 输出文件\n\n")
        f.write("The detailed report and log files are generated at:\n\n")
        f.write("详细运行报告和日志文件生成在：\n\n")
        f.write("    docs/pipeline_run_report.csv\n")
        f.write("    docs/pipeline_latest_run.log\n\n")

        if failed_steps == 0:
            f.write("All pipeline steps completed successfully.\n\n")
            f.write("所有主流程步骤均已成功完成。\n")
        else:
            f.write("Some pipeline steps failed. Please check the detailed log file.\n\n")
            f.write("部分主流程步骤失败，请查看详细日志文件。\n")

    print(f"[OK] Pipeline summary generated: {summary_path}")


def main() -> None:
    print("[INFO] Starting e-commerce offline data warehouse pipeline ...")
    print(f"[INFO] Project root: {ROOT_DIR}")
    print(f"[INFO] Python executable: {sys.executable}")

    results = []
    should_continue = True
    failure_reason = ""

    for step in PIPELINE_STEPS:
        if should_continue:
            result = run_one_step(step)
            results.append(result)

            if result["status"] == "FAIL":
                should_continue = False
                failure_reason = f"Skipped because previous step failed: {result['step_name']}"
        else:
            skipped_result = build_skipped_result(step, failure_reason)
            results.append(skipped_result)
            print(f"[SKIPPED] {step['step_name']}")

    save_pipeline_report(results)
    generate_pipeline_summary(results)

    failed_steps = [item for item in results if item["status"] == "FAIL"]

    print("=" * 80)
    print("[PIPELINE SUMMARY]")
    print(f"Total steps: {len(results)}")
    print(f"Passed steps: {sum(1 for item in results if item['status'] == 'PASS')}")
    print(f"Failed steps: {sum(1 for item in results if item['status'] == 'FAIL')}")
    print(f"Skipped steps: {sum(1 for item in results if item['status'] == 'SKIPPED')}")
    print("=" * 80)

    if failed_steps:
        print("[FAIL] Pipeline failed. Please check docs/pipeline_latest_run.log")
        sys.exit(1)

    print("[DONE] Pipeline completed successfully.")


if __name__ == "__main__":
    main()