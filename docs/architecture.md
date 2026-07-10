# Architecture & Data Lineage / 架构与数据血缘

This document visualizes the warehouse architecture, the data lineage from raw
files to analysis outputs, and the technology stack. The diagrams use Mermaid and
render directly on GitHub.

本文档以图示展示数仓架构、从原始文件到分析产出的数据血缘，以及技术栈。
图表使用 Mermaid，可在 GitHub 上直接渲染。

---

## 1. Layered Architecture / 分层架构

```mermaid
flowchart TD
    RAW["Raw CSV<br/>9 Olist source files"]:::raw
    ODS["ODS<br/>9 tables + loaded_at/dt"]:::ods
    DWD["DWD<br/>dwd_order_detail (~99K rows)"]:::dwd
    DWS["DWS<br/>dws_daily_order_summary"]:::dws
    ADS["ADS<br/>daily business overview"]:::ads
    ANALYSIS["ADS Analysis<br/>RFM · Category · Geography"]:::ads
    DQ["Data Quality Checks"]:::qa
    BI["Charts / Superset / Power BI"]:::bi

    RAW --> ODS --> DWD --> DWS --> ADS
    DWD --> ANALYSIS
    ADS --> BI
    ANALYSIS --> BI
    ODS --> DQ
    DWD --> DQ
    DWS --> DQ
    ADS --> DQ

    classDef raw fill:#E8E8E8,stroke:#888,color:#000
    classDef ods fill:#D6EAF8,stroke:#2E86C1,color:#000
    classDef dwd fill:#D5F5E3,stroke:#28B463,color:#000
    classDef dws fill:#FCF3CF,stroke:#D4AC0D,color:#000
    classDef ads fill:#FADBD8,stroke:#CB4335,color:#000
    classDef qa fill:#E8DAEF,stroke:#8E44AD,color:#000
    classDef bi fill:#D1F2EB,stroke:#17A589,color:#000
```

---

## 2. Multi-Engine Implementation / 多引擎实现

The **same** business logic is implemented across four engines to demonstrate
migration from a local prototype to an enterprise stack. Each is validated against
the Pandas baseline.

**同一套** 业务逻辑在四种引擎上实现，演示从本地原型到企业级技术栈的迁移，
每一套都与 Pandas 基准做校验。

```mermaid
flowchart LR
    subgraph P["Pandas Baseline / 基准"]
        P1["ODS→DWD→DWS→ADS<br/>+ DQ + charts"]
    end
    subgraph S["Spark SQL / 大数据迁移"]
        S1["DWD→DWS→ADS<br/>reuses ODS CSV"]
    end
    subgraph D["PostgreSQL + dbt / 企业数仓"]
        D1["staging→dwd→dws→ads<br/>+ schema tests"]
    end
    subgraph O["Orchestration + BI / 调度与看板"]
        O1["Airflow DAG"]
        O2["Superset · Power BI"]
    end

    P1 -->|"23 checks pass"| S1
    P1 -->|"row/metric parity"| D1
    D1 --> O1 --> O2

    classDef box fill:#F4F6F7,stroke:#5D6D7E,color:#000
    class P1,S1,D1,O1,O2 box
```

---

## 3. Analysis-Layer Lineage / 分析层血缘

```mermaid
flowchart TD
    ODS_ITEMS["ods_order_items"]:::ods
    ODS_PROD["ods_products"]:::ods
    ODS_TRANS["ods_product_category_translation"]:::ods
    ODS_ORDERS["ods_orders"]:::ods
    DWD["dwd_order_detail"]:::dwd

    RFM["ads_customer_rfm<br/>(+ segment summary)"]:::ads
    CAT["ads_product_category_rank"]:::ads
    GEO["ads_geo_state_summary"]:::ads

    DWD --> RFM
    DWD --> GEO
    ODS_ITEMS --> CAT
    ODS_PROD --> CAT
    ODS_TRANS --> CAT
    ODS_ORDERS --> CAT

    RFM --> INSIGHTS["docs/business_insights.md"]:::doc
    CAT --> INSIGHTS
    GEO --> INSIGHTS

    classDef ods fill:#D6EAF8,stroke:#2E86C1,color:#000
    classDef dwd fill:#D5F5E3,stroke:#28B463,color:#000
    classDef ads fill:#FADBD8,stroke:#CB4335,color:#000
    classDef doc fill:#FEF9E7,stroke:#B7950B,color:#000
```

---

## 4. Technology Stack / 技术栈

| Layer / 层 | Tooling / 工具 |
|---|---|
| Storage / 存储 | CSV, PostgreSQL |
| Processing / 处理 | Python + Pandas, PySpark + Spark SQL |
| Modeling / 建模 | dbt (staging → dwd → dws → ads) |
| Orchestration / 调度 | Python pipeline scripts, Apache Airflow |
| Quality / 质量 | Custom DQ checks, dbt schema tests, pytest |
| CI | GitHub Actions (ruff + pytest) |
| BI | matplotlib, Apache Superset, Power BI |
