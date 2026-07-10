# Airflow Orchestration Design / Airflow 调度设计

## 1. Purpose / 目的

This document describes the Airflow orchestration setup for the e-commerce offline data warehouse enterprise stack.

本文档说明电商离线数仓企业级技术栈的 Airflow 调度编排搭建。

Airflow is used to schedule and monitor the complete data warehouse pipeline:

Airflow 用于调度和监控完整数仓主流程：

```text
Check PostgreSQL Connection
    ↓
Load Raw CSV to PostgreSQL ODS
    ↓
dbt Debug (config verification)
    ↓
dbt Run (staging → DWD → DWS → ADS)
    ↓
dbt Test (data quality checks)
    ↓
Compare dbt Outputs vs Pandas Baseline
```

---

## 2. Architecture / 架构

### 2.1 Service Overview / 服务概览

| Service / 服务 | Image / 镜像 | Port / 端口 | Purpose / 用途 |
|---|---|---|---|
| `airflow-webserver` | Custom (extends `apache/airflow:2.10.5`) | `8080` | Web UI for DAG monitoring / DAG 监控 Web 界面 |
| `airflow-scheduler` | Custom (same image) | — | Schedules and executes DAG tasks / 调度和执行 DAG 任务 |
| `airflow-init` | Custom (same image) | — | Initializes Airflow DB and admin user / 初始化 Airflow 数据库和管理员 |

### 2.2 Architecture Diagram / 架构图

```text
┌────────────────── Docker Network ──────────────────┐
│                                                     │
│  ┌─────────────────┐    ┌─────────────────┐         │
│  │ Airflow Webserver│    │Airflow Scheduler │        │
│  │ :8080            │    │                 │        │
│  └────────┬────────┘    └────────┬────────┘         │
│           │                      │                   │
│  ┌────────┴──────────────────────┴────────┐         │
│  │  Project Volume (/opt/airflow/project/) │         │
│  │    ├── scripts/*.py                     │         │
│  │    ├── dbt/ecommerce_warehouse/         │         │
│  │    ├── data/raw/                        │         │
│  │    └── data/ (ODS/DWD/DWS/ADS)          │         │
│  └─────────────────────────────────────────┘         │
│                                                     │
│        host.docker.internal:5433                     │
│                   │                                   │
└───────────────────┼───────────────────────────────────┘
                    │
    ┌───────────────┴──────────────┐
    │  PostgreSQL Container        │
    │  (docker-compose.postgres.yml)│
    │  - Host port: 5433           │
    │  - Internal: 5432            │
    └──────────────────────────────┘
```

### 2.3 Key Design Decisions / 关键设计决策

| Decision / 决策 | Rationale / 理由 |
|---|---|
| **Docker-based Airflow** / Docker 化 Airflow | Avoids native Windows Airflow installation complexity / 避免 Windows 原生安装的复杂性 |
| **Custom Docker image** / 自定义 Docker 镜像 | Adds `dbt-postgres`, `pandas`, `sqlalchemy` to official image / 在官方镜像上添加额外包 |
| **Separate compose file** / 独立的 compose 文件 | Does not modify existing `docker-compose.postgres.yml` / 不修改现有的 PostgreSQL 配置 |
| **host.docker.internal** / Docker 内部主机名 | Airflow containers access host PostgreSQL via Docker gateway / 通过 Docker 网关访问宿主机 PostgreSQL |
| **Mounted project volume** / 挂载项目卷 | Airflow containers run scripts and dbt from the same source files / 运行同一份源文件 |
| **Separate dbt profile** / 独立的 dbt 配置 | Airflow uses `host.docker.internal`; local dev uses `localhost` / 两者互不干扰 |

---

## 3. DAG Design / DAG 设计

### 3.1 DAG Overview / DAG 概览

| Attribute / 属性 | Value / 值 |
|---|---|
| DAG ID | `ecommerce_warehouse_pipeline` |
| Schedule | `None` (manual trigger) / 手动触发 |
| Catchup | `False` |
| Tags | `ecommerce`, `warehouse`, `dbt`, `postgres` |
| Default retries | 1 |
| Retry delay | 5 minutes |

### 3.2 Task Sequence / 任务序列

```text
check_postgres_connection
    │
    ▼
load_raw_to_postgres_ods
    │
    ▼
dbt_debug
    │
    ▼
dbt_run
    │
    ▼
dbt_test
    │
    ▼
compare_dbt_postgres_outputs
```

### 3.3 Task Details / 任务详情

| Task ID | Type / 类型 | Command / 命令 | Working Dir / 工作目录 | Environment / 环境变量 |
|---|---|---|---|---|
| `check_postgres_connection` | `BashOperator` | `python scripts/check_postgres_ods.py` | `/opt/airflow/project` | `POSTGRES_HOST=host.docker.internal` |
| `load_raw_to_postgres_ods` | `BashOperator` | `python scripts/load_raw_to_postgres_ods.py` | `/opt/airflow/project` | `POSTGRES_HOST=host.docker.internal` |
| `dbt_debug` | `BashOperator` | `dbt debug --profiles-dir /opt/airflow/config` | `/opt/airflow/project/dbt/ecommerce_warehouse` | `POSTGRES_HOST=host.docker.internal` |
| `dbt_run` | `BashOperator` | `dbt run --profiles-dir /opt/airflow/config` | `/opt/airflow/project/dbt/ecommerce_warehouse` | `POSTGRES_HOST=host.docker.internal` |
| `dbt_test` | `BashOperator` | `dbt test --profiles-dir /opt/airflow/config` | `/opt/airflow/project/dbt/ecommerce_warehouse` | `POSTGRES_HOST=host.docker.internal` |
| `compare_dbt_postgres_outputs` | `BashOperator` | `python scripts/compare_dbt_postgres_outputs.py` | `/opt/airflow/project` | `POSTGRES_HOST=host.docker.internal` |

---

## 4. PostgreSQL Connection / PostgreSQL 连接

### 4.1 Connection Strategy / 连接策略

| Context / 场景 | Host | Port | Method |
|---|---|---|---|
| **Local development** / 本地开发 | `localhost` | `5433` | Direct host connection |
| **Airflow container** / Airflow 容器 | `host.docker.internal` | `5433` | Docker host gateway env var |

### 4.2 Environment Variables / 环境变量

All Python scripts and the dbt profile support these environment variables:

所有 Python 脚本和 dbt 配置都支持以下环境变量：

| Variable / 变量 | Local Default / 本地默认值 | Airflow Value / Airflow 值 |
|---|---|---|
| `POSTGRES_HOST` | `localhost` | `host.docker.internal` |
| `POSTGRES_PORT` | `5433` | `5433` |
| `POSTGRES_DB` | `ecommerce_warehouse` | `ecommerce_warehouse` |
| `POSTGRES_USER` | `warehouse_user` | `warehouse_user` |
| `POSTGRES_PASSWORD` | `warehouse_pass` | `warehouse_pass` |

### 4.3 Profile Separation / 配置分离

| Profile File / 配置文件 | Used By / 使用者 | Host |
|---|---|---|
| `dbt/ecommerce_warehouse/profiles.yml` | Local dbt development | `localhost:5433` |
| `airflow/config/profiles.yml` | Airflow container dbt | `host.docker.internal:5433` |

---

## 5. File Structure / 文件结构

```text
airflow/
├── .env.example              # Environment variable template / 环境变量模板
├── .env                      # Local Docker environment (gitignored) / 本地 Docker 环境
├── Dockerfile                # Custom Airflow image with dbt-postgres / 自定义镜像
├── requirements.txt          # Python packages for Docker image / Docker 镜像的 Python 包
├── dags/
│   └── ecommerce_warehouse_dag.py   # Main DAG definition / 主 DAG 定义
├── config/
│   ├── profiles.yml.example  # Airflow dbt profile template / Airflow dbt 配置模板
│   └── profiles.yml          # Airflow dbt profile (gitignored) / Airflow dbt 配置
└── logs/                     # Airflow logs (gitignored) / Airflow 日志
```

---

## 6. How to Run / 如何运行

### 6.1 Prerequisites / 前置条件

```powershell
# Ensure PostgreSQL is running / 确保 PostgreSQL 运行中
docker compose -f docker-compose.postgres.yml ps
```

### 6.2 Build and Start Airflow / 构建和启动 Airflow

```powershell
# Step 1: Build custom Airflow image / 构建自定义 Airflow 镜像
docker compose -f docker-compose.airflow.yml build

# Step 2: Initialize Airflow database and create admin user / 初始化数据库和管理员
docker compose -f docker-compose.airflow.yml up airflow-init

# Step 3: Start Airflow services / 启动 Airflow 服务
docker compose -f docker-compose.airflow.yml up -d

# Step 4: Verify services are running / 验证服务运行
docker compose -f docker-compose.airflow.yml ps
```

### 6.3 Access Airflow Web UI / 访问 Airflow Web 界面

```
URL: http://localhost:8080
Username: admin
Password: admin
```

### 6.4 Trigger DAG / 触发 DAG

```powershell
# Via command line / 通过命令行
docker compose -f docker-compose.airflow.yml exec airflow-webserver airflow dags trigger ecommerce_warehouse_pipeline

# Via Web UI: Open http://localhost:8080 → DAGs → toggle On → Trigger DAG
```

### 6.5 Monitor DAG / 监控 DAG

```powershell
# List DAGs / 列出 DAG
docker compose -f docker-compose.airflow.yml exec airflow-webserver airflow dags list

# List DAG runs / 列出 DAG 运行记录
docker compose -f docker-compose.airflow.yml exec airflow-webserver airflow dags list-runs -d ecommerce_warehouse_pipeline

# View task logs / 查看任务日志
docker compose -f docker-compose.airflow.yml logs airflow-scheduler
docker compose -f docker-compose.airflow.yml logs airflow-webserver
```

### 6.6 Stop Airflow / 停止 Airflow

```powershell
docker compose -f docker-compose.airflow.yml down
```

To reset Airflow completely (reset database):

完全重置 Airflow：

```powershell
docker compose -f docker-compose.airflow.yml down -v
Remove-Item -Recurse -Force airflow/logs/* -ErrorAction SilentlyContinue
```

---

## 7. DAG Task Dependencies / DAG 任务依赖

```text
check_postgres_connection
         │
         ▼
load_raw_to_postgres_ods
         │
         ▼
     dbt_debug
         │
         ▼
      dbt_run
         │
         ▼
     dbt_test
         │
         ▼
compare_dbt_postgres_outputs
```

Each task depends on the previous task completing successfully.

每个任务依赖前一个任务成功完成。

- If `check_postgres_connection` fails → pipeline stops (PostgreSQL not available)
- 如果 `check_postgres_connection` 失败 → 主流程停止（PostgreSQL 不可用）
- If `load_raw_to_postgres_ods` fails → pipeline stops (no ODS data for dbt)
- 如果 `load_raw_to_postgres_ods` 失败 → 主流程停止（dbt 无数据可转换）
- If `dbt_debug` fails → pipeline stops (dbt configuration issue)
- 如果 `dbt_debug` 失败 → 主流程停止（dbt 配置问题）
- If `dbt_run` fails → dbt_test and comparison are skipped
- 如果 `dbt_run` 失败 → 跳过 dbt_test 和比较
- If `dbt_test` fails → comparison still runs (validation can review failures)
- 如果 `dbt_test` 失败 → 比较仍会运行（可审查失败）

---

## 8. Files Not Modified / 未修改的文件

The following files remain unchanged during Phase 3:

以下文件在 Phase 3 中保持不变：

```text
README.md                                  # Updated in final phase only
scripts/run_pipeline.py                    # Pandas baseline, unchanged
scripts/run_spark_pipeline.py              # Spark migration, unchanged
scripts/check_raw_data.py                  # Pandas baseline, unchanged
scripts/load_raw_to_ods.py                 # Pandas baseline, unchanged
scripts/build_dwd_order_detail.py          # Pandas baseline, unchanged
scripts/build_dws_daily_order_summary.py   # Pandas baseline, unchanged
scripts/build_ads_daily_business_overview.py # Pandas baseline, unchanged
scripts/run_data_quality_checks.py         # Pandas baseline, unchanged
scripts/build_dashboard_charts.py          # Pandas baseline, unchanged
scripts/spark_build_dwd_order_detail.py    # Spark migration, unchanged
scripts/spark_build_dws_daily_order_summary.py  # Spark migration, unchanged
scripts/spark_build_ads_daily_business_overview.py # Spark migration, unchanged
scripts/compare_pandas_spark_outputs.py    # Spark migration, unchanged
scripts/run_spark_pipeline.py              # Spark migration, unchanged
docker-compose.postgres.yml                # PostgreSQL, unchanged
dbt/ecommerce_warehouse/profiles.yml       # Local dbt profile, unchanged
dbt/ecommerce_warehouse/models/*           # dbt models, unchanged
```

---

## 9. Comparison: Three Pipelines / 三条主流程对比

After Phase 3, the project has three fully operational pipeline options:

Phase 3 完成后，项目有三个可运行的主流程选项：

| Pipeline / 主流程 | Run Command / 运行命令 | Engine / 引擎 | Storage / 存储 | Scheduling / 调度 |
|---|---|---|---|---|
| **Pandas Baseline** | `python scripts/run_pipeline.py` | Python / Pandas | Local CSV | Manual |
| **Spark Migration** | `python scripts/run_spark_pipeline.py` | PySpark / Spark SQL | Local CSV | Manual |
| **Enterprise Stack** | Airflow DAG trigger | dbt + PostgreSQL | PostgreSQL Tables | Airflow (manual or scheduled) |

---

## 10. Troubleshooting / 故障排查

### 10.1 Airflow cannot connect to PostgreSQL / Airflow 无法连接 PostgreSQL

```powershell
# Check PostgreSQL is running / 检查 PostgreSQL 运行状态
docker compose -f docker-compose.postgres.yml ps

# Test connection from inside Airflow container / 从 Airflow 容器内测试连接
docker compose -f docker-compose.airflow.yml exec airflow-webserver python -c "
import psycopg2
conn = psycopg2.connect(host='host.docker.internal', port=5433, dbname='ecommerce_warehouse', user='warehouse_user', password='warehouse_pass')
print('OK')
conn.close()
"
```

### 10.2 Airflow Init Fails / 初始化失败

```powershell
# Reset and retry / 重置并重试
docker compose -f docker-compose.airflow.yml down -v
docker compose -f docker-compose.airflow.yml up airflow-init
```

### 10.3 DAG Not Visible in Web UI / DAG 在 Web 界面不可见

```powershell
# Check DAG list from command line / 从命令行检查 DAG 列表
docker compose -f docker-compose.airflow.yml exec airflow-webserver airflow dags list

# Check scheduler logs / 检查调度器日志
docker compose -f docker-compose.airflow.yml logs airflow-scheduler
```

### 10.4 dbt Debug Fails in Airflow / dbt Debug 在 Airflow 中失败

Check that `airflow/config/profiles.yml` exists and contains the correct `host.docker.internal` host.

检查 `airflow/config/profiles.yml` 是否存在且包含正确的 `host.docker.internal` 主机地址。

```powershell
docker compose -f docker-compose.airflow.yml exec airflow-webserver cat /opt/airflow/config/profiles.yml
```

---

## 11. Summary / 总结

This phase adds Apache Airflow as the orchestration layer for the enterprise warehouse stack.

本阶段为企级数仓技术栈添加 Apache Airflow 作为调度编排层。

Key achievements / 关键成果：

1. **Docker-based Airflow** / Docker 化 Airflow: Separate compose file, custom image with dbt-postgres
2. **DAG with full pipeline** / 完整主流程 DAG: 6 sequenced tasks covering ODS loading → dbt transformation → validation
3. **Clean separation** / 清晰分离: Local dev (localhost) and Airflow (host.docker.internal) use separate profiles
4. **No modifications** / 无修改: All existing Pandas, Spark, PostgreSQL, and dbt files remain unchanged
5. **Manual trigger** / 手动触发: DAG runs on demand; can be changed to scheduled in the future