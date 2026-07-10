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


SPARK_PIPELINE_STEPS = [
    {
        "step_order": 1,
        "step_name": "Spark DWD Order Detail Building",
        "script": "spark_build_dwd_order_detail.py",
        "description": "Build DWD order detail table using Spark SQL from ODS layer.",
    },
    {
        "step_order": 2,
        "step_name": "Spark DWS Daily Order Summary Building",
        "script": "spark_build_dws_daily_order_summary.py",
        "description": "Build DWS daily order summary table using Spark SQL from Spark DWD.",
    },
    {
        "step_order": 3,
        "step_name": "Spark ADS Daily Business Overview Building",
        "script": "spark_build_ads_daily_business_overview.py",
        "description": "Build ADS daily business overview table using Spark SQL from Spark DWS.",
    },
    {
        "step_order": 4,
        "step_name": "Pandas vs Spark Full Comparison",
        "script": "compare_pandas_spark_outputs.py",
        "description": "Compare all Pandas baseline outputs with Spark SQL migration outputs.",
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
            "status": "FAILED",
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

    # Print stdout and stderr, handling encoding issues on Windows
    def safe_print(text: str) -> None:
        """Print text safely, replacing problematic Unicode characters."""
        # Replace replacement character and other problematic chars
        safe_text = text.replace('�', '?')
        try:
            print(safe_text)
        except UnicodeEncodeError:
            # Fall back to ASCII-safe encoding
            print(safe_text.encode('ascii', errors='replace').decode('ascii'))

    if stdout.strip():
        safe_print(stdout)

    if stderr.strip():
        print("[STDERR]")
        safe_print(stderr)

    status = "SUCCESS" if return_code == 0 else "FAILED"

    if status == "SUCCESS":
        print(f"[OK] Step completed: {step['step_name']}")
    else:
        print(f"[FAILED] Step failed: {step['step_name']}")

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
        "error_message": stderr.strip() if status == "FAILED" else "",
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


def save_pipeline_report(results: list, pipeline_start: str, pipeline_end: str, total_duration: float) -> None:
    """
    Save pipeline run report and latest run log.
    """
    # Add pipeline-level summary row
    report_rows = []

    for result in results:
        report_rows.append({
            "step_order": result["step_order"],
            "step_name": result["step_name"],
            "script": result["script"],
            "status": result["status"],
            "return_code": result["return_code"],
            "start_time": result["start_time"],
            "end_time": result["end_time"],
            "duration_seconds": result["duration_seconds"],
            "description": result["description"],
            "error_message": result["error_message"],
        })

    report_df = pd.DataFrame(report_rows)
    report_path = DOCS_DIR / "spark_pipeline_run_report.csv"
    report_df.to_csv(report_path, index=False, encoding="utf-8-sig")

    # Generate log file
    log_path = DOCS_DIR / "spark_pipeline_latest_run.log"

    with log_path.open("w", encoding="utf-8") as f:
        f.write("Spark SQL Migration Pipeline Log / Spark SQL 迁移主流程日志\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Pipeline start time / 主流程开始时间: {pipeline_start}\n")
        f.write(f"Pipeline end time / 主流程结束时间: {pipeline_end}\n")
        f.write(f"Total duration seconds / 总耗时秒数: {round(total_duration, 2)}\n\n")
        f.write(f"Generated at / 生成时间: {now_str()}\n\n")

        for result in results:
            f.write("=" * 80 + "\n")
            f.write(f"Step {result['step_order']}: {result['step_name']}\n")
            f.write(f"Script / 脚本: {result['script']}\n")
            f.write(f"Status / 状态: {result['status']}\n")
            f.write(f"Return code / 返回码: {result['return_code']}\n")
            f.write(f"Start time / 开始时间: {result['start_time']}\n")
            f.write(f"End time / 结束时间: {result['end_time']}\n")
            f.write(f"Duration seconds / 耗时秒数: {result['duration_seconds']}\n")
            f.write(f"Description / 说明: {result['description']}\n")

            if result["error_message"]:
                f.write(f"\nError message / 错误信息:\n{result['error_message']}\n")

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


def generate_pipeline_summary(results: list, pipeline_start: str, pipeline_end: str, total_duration: float) -> None:
    """
    Generate a bilingual markdown summary for the latest Spark pipeline run.
    """
    summary_path = DOCS_DIR / "spark_pipeline_run_summary.md"

    total_steps = len(results)
    success_steps = sum(1 for item in results if item["status"] == "SUCCESS")
    failed_steps = sum(1 for item in results if item["status"] == "FAILED")
    skipped_steps = sum(1 for item in results if item["status"] == "SKIPPED")

    with summary_path.open("w", encoding="utf-8") as f:
        f.write("# Spark Pipeline Run Summary / Spark 主流程运行总结\n\n")
        f.write(f"Generated at / 生成时间: {now_str()}\n\n")

        # Pipeline timing
        f.write("## 1. Pipeline Timing / 主流程时间\n\n")
        f.write("| Metric / 指标 | Value / 数值 |\n")
        f.write("|---|---|\n")
        f.write(f"| Pipeline start time / 主流程开始时间 | {pipeline_start} |\n")
        f.write(f"| Pipeline end time / 主流程结束时间 | {pipeline_end} |\n")
        f.write(f"| Total duration seconds / 总耗时秒数 | {round(total_duration, 2)} |\n\n")

        # Overall result
        f.write("## 2. Overall Result / 总体结果\n\n")
        f.write("| Metric / 指标 | Value / 数值 |\n")
        f.write("|---|---:|\n")
        f.write(f"| Total steps / 总步骤数 | {total_steps} |\n")
        f.write(f"| Success steps / 成功步骤数 | {success_steps} |\n")
        f.write(f"| Failed steps / 失败步骤数 | {failed_steps} |\n")
        f.write(f"| Skipped steps / 跳过步骤数 | {skipped_steps} |\n\n")

        if failed_steps == 0 and skipped_steps == 0:
            f.write("**All pipeline steps completed successfully.**\n\n")
            f.write("**所有主流程步骤均已成功完成。**\n\n")
        else:
            f.write(f"**{failed_steps} steps failed, {skipped_steps} steps skipped.**\n\n")
            f.write(f"**{failed_steps} 个步骤失败，{skipped_steps} 个步骤跳过。**\n\n")

        # Step details
        f.write("## 3. Step Details / 步骤明细\n\n")
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

        # Failed/Skipped details
        if failed_steps > 0 or skipped_steps > 0:
            f.write("\n## 4. Failed/Skipped Steps Details / 失败/跳过步骤详情\n\n")

            failed_items = [item for item in results if item["status"] == "FAILED"]
            skipped_items = [item for item in results if item["status"] == "SKIPPED"]

            if failed_items:
                f.write("### Failed Steps / 失败步骤\n\n")
                for item in failed_items:
                    f.write(f"- **{item['step_name']}** (Step {item['step_order']})\n")
                    if item["error_message"]:
                        f.write(f"  - Error: {item['error_message']}\n")
                f.write("\n")

            if skipped_items:
                f.write("### Skipped Steps / 跳过步骤\n\n")
                for item in skipped_items:
                    f.write(f"- **{item['step_name']}** (Step {item['step_order']})\n")
                    if item["error_message"]:
                        f.write(f"  - Reason: {item['error_message']}\n")
                f.write("\n")
        else:
            f.write("\n## 4. Failed/Skipped Steps Details / 失败/跳过步骤详情\n\n")
            f.write("No failed or skipped steps.\n\n")
            f.write("无失败或跳过步骤。\n\n")

        # Output files
        f.write("## 5. Output Files / 输出文件\n\n")
        f.write("The detailed report and log files are generated at:\n\n")
        f.write("详细运行报告和日志文件生成在：\n\n")
        f.write("    docs/spark_pipeline_run_report.csv\n")
        f.write("    docs/spark_pipeline_latest_run.log\n\n")

        # Final result
        f.write("## 6. Final Result / 最终结果\n\n")
        if failed_steps == 0 and skipped_steps == 0:
            f.write("```\n[DONE] Spark pipeline completed successfully.\n```\n\n")
            f.write("```\n[DONE] Spark 主流程已成功完成。\n```\n")
        else:
            f.write("```\n[FAILED] Spark pipeline failed.\n```\n\n")
            f.write("```\n[FAILED] Spark 主流程失败。\n```\n")

    print(f"[OK] Pipeline summary generated: {summary_path}")


def print_final_summary(results: list) -> None:
    """
    Print the final pipeline summary to console.
    """
    total_steps = len(results)
    success_steps = sum(1 for item in results if item["status"] == "SUCCESS")
    failed_steps = sum(1 for item in results if item["status"] == "FAILED")
    skipped_steps = sum(1 for item in results if item["status"] == "SKIPPED")

    print("=" * 80)
    print("[PIPELINE SUMMARY]")
    print(f"Total steps: {total_steps}")
    print(f"Success: {success_steps}")
    print(f"Failed: {failed_steps}")
    print(f"Skipped: {skipped_steps}")
    print("=" * 80)

    if failed_steps > 0 or skipped_steps > 0:
        print("\n[FAILED] Spark pipeline failed.")
        print("\nFailed/Skipped steps:")
        for item in results:
            if item["status"] in ["FAILED", "SKIPPED"]:
                print(f"  - Step {item['step_order']}: {item['step_name']} ({item['status']})")
                if item["error_message"]:
                    print(f"    {item['error_message']}")
    else:
        print("\n[DONE] Spark pipeline completed successfully.")


def main() -> None:
    print("=" * 80)
    print("[INFO] Starting Spark SQL Migration Pipeline ...")
    print("=" * 80)
    print(f"[INFO] Project root: {ROOT_DIR}")
    print(f"[INFO] Python executable: {sys.executable}")
    print()

    pipeline_start = now_str()
    start_perf = time.perf_counter()

    results = []
    should_continue = True
    failure_reason = ""

    for step in SPARK_PIPELINE_STEPS:
        if should_continue:
            result = run_one_step(step)
            results.append(result)

            if result["status"] == "FAILED":
                should_continue = False
                failure_reason = f"Skipped because previous step failed: {result['step_name']}"
        else:
            skipped_result = build_skipped_result(step, failure_reason)
            results.append(skipped_result)
            print(f"[SKIPPED] {step['step_name']}")

    pipeline_end = now_str()
    total_duration = time.perf_counter() - start_perf

    save_pipeline_report(results, pipeline_start, pipeline_end, total_duration)
    generate_pipeline_summary(results, pipeline_start, pipeline_end, total_duration)
    print_final_summary(results)

    failed_steps = [item for item in results if item["status"] == "FAILED"]

    if failed_steps:
        print("=" * 80)
        print("[FAILED] Spark pipeline failed.")
        print("Please check docs/spark_pipeline_latest_run.log for details.")
        print("=" * 80)
        sys.exit(1)

    print("=" * 80)
    print("[DONE] Spark pipeline completed successfully.")
    print("=" * 80)


if __name__ == "__main__":
    main()