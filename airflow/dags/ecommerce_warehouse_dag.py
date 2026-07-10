"""
E-Commerce Warehouse Pipeline DAG
电商数仓主流程 DAG

This DAG orchestrates the complete enterprise data warehouse pipeline:
该 DAG 编排完整的企业级数仓主流程：

1. Check PostgreSQL connection / 检查 PostgreSQL 连接
2. Load raw CSV to PostgreSQL ODS tables / 加载原始 CSV 数据到 PostgreSQL ODS 表
3. Verify dbt project configuration / 验证 dbt 项目配置
4. Run dbt models (staging → DWD → DWS → ADS) / 运行 dbt 模型
5. Run dbt data tests / 运行 dbt 数据测试
6. Compare dbt outputs with Pandas baseline / 比较 dbt 输出与 Pandas 基准
"""

from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator


# Project paths inside the Airflow container / Airflow 容器内的项目路径
PROJECT_ROOT = "/opt/airflow/project"
SCRIPTS_DIR = f"{PROJECT_ROOT}/scripts"
DBT_PROJECT_DIR = f"{PROJECT_ROOT}/dbt/ecommerce_warehouse"
DBT_PROFILES_DIR = "/opt/airflow/config"

# Default arguments / 默认参数
default_args = {
    "owner": "warehouse_admin",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(2024, 1, 1),
}

# Environment variables for PostgreSQL connection from Airflow container
# Airflow 容器中 PostgreSQL 连接的环境变量
POSTGRES_ENV = {
    "POSTGRES_HOST": "host.docker.internal",
    "POSTGRES_PORT": "5433",
    "POSTGRES_DB": "ecommerce_warehouse",
    "POSTGRES_USER": "warehouse_user",
    "POSTGRES_PASSWORD": "warehouse_pass",
}

# dbt environment (inherits POSTGRES_* env vars for profiles.yml Jinja)
# dbt 环境（继承 POSTGRES_* 环境变量供 profiles.yml Jinja 使用）
DBT_ENV = {
    **POSTGRES_ENV,
    "DBT_PROFILES_DIR": DBT_PROFILES_DIR,
    # dbt is installed in /home/airflow/.local/bin, ensure it's in PATH
    # dbt 安装于 /home/airflow/.local/bin，确保其在 PATH 中
    "PATH": "/home/airflow/.local/bin:/usr/local/bin:/usr/bin:/bin",
}

dag = DAG(
    dag_id="ecommerce_warehouse_pipeline",
    default_args=default_args,
    description="E-Commerce Data Warehouse: ODS → dbt → DWD → DWS → ADS",
    # Manual trigger by default; can be changed to schedule
    # 默认手动触发；可改为定时调度
    schedule_interval=None,
    catchup=False,
    tags=["ecommerce", "warehouse", "dbt", "postgres"],
)


task_check_postgres = BashOperator(
    task_id="check_postgres_connection",
    bash_command=f"cd {PROJECT_ROOT} && python {SCRIPTS_DIR}/check_postgres_ods.py",
    env=POSTGRES_ENV,
    dag=dag,
)

task_load_raw_to_ods = BashOperator(
    task_id="load_raw_to_postgres_ods",
    bash_command=f"cd {PROJECT_ROOT} && python {SCRIPTS_DIR}/load_raw_to_postgres_ods.py",
    env=POSTGRES_ENV,
    dag=dag,
)

task_dbt_debug = BashOperator(
    task_id="dbt_debug",
    bash_command=(
        f"cd {DBT_PROJECT_DIR} && "
        f"dbt debug --connection --profiles-dir {DBT_PROFILES_DIR}"
    ),
    env=DBT_ENV,
    dag=dag,
)

task_dbt_run = BashOperator(
    task_id="dbt_run",
    bash_command=(
        f"cd {DBT_PROJECT_DIR} && "
        f"dbt run --profiles-dir {DBT_PROFILES_DIR}"
    ),
    env=DBT_ENV,
    dag=dag,
)

task_dbt_test = BashOperator(
    task_id="dbt_test",
    bash_command=(
        f"cd {DBT_PROJECT_DIR} && "
        f"dbt test --profiles-dir {DBT_PROFILES_DIR}"
    ),
    env=DBT_ENV,
    dag=dag,
)

task_compare_outputs = BashOperator(
    task_id="compare_dbt_postgres_outputs",
    bash_command=f"cd {PROJECT_ROOT} && python {SCRIPTS_DIR}/compare_dbt_postgres_outputs.py",
    env=POSTGRES_ENV,
    dag=dag,
)


# Task dependencies / 任务依赖关系
# check_postgres → load_raw → dbt_debug → dbt_run → dbt_test → compare
task_check_postgres >> task_load_raw_to_ods
task_load_raw_to_ods >> task_dbt_debug
task_dbt_debug >> task_dbt_run
task_dbt_run >> task_dbt_test
task_dbt_test >> task_compare_outputs