# Business Insights Report / 业务洞察报告

> Source data / 数据来源: Olist Brazilian E-Commerce (2016-09 ~ 2018-10)
> Built from / 构建自: `DWD` order detail + `ADS` analysis tables
> Reproduce / 复现: `python scripts/run_pipeline.py` then / 然后 `python scripts/run_analysis_pipeline.py`

This report turns the warehouse output into a business narrative: how the store
performed overall, who the customers are (RFM), what sells (category Pareto), and
where demand and logistics pain concentrate (geography).

本报告将数仓产出转化为业务叙事：整体经营表现、客户是谁（RFM）、什么好卖
（类目帕累托）、需求与物流压力集中在哪里（地域）。

---

## 1. Headline KPIs / 核心指标

These figures come from the built `DWD`/`ADS` layers (`docs/dwd_order_detail_report.csv`,
`dashboard/dashboard_kpi_summary.csv`).

以下数字来自已构建的 `DWD`/`ADS` 层（`docs/dwd_order_detail_report.csv`、
`dashboard/dashboard_kpi_summary.csv`）。

| Metric / 指标 | Value / 数值 |
|---|---:|
| Date range / 数据区间 | 2016-09-04 ~ 2018-10-17 |
| GMV (total payment) / GMV（总支付额） | R$ 16,008,872.12 |
| Order count / 订单数 | 99,441 |
| Unique customers / 唯一客户数 | 96,096 |
| Overall AOV / 整体客单价 | R$ 160.99 |
| Delivered orders / 已送达订单 | 96,476 |
| Avg delivery rate / 平均送达率 | 93.1% |
| Avg late-delivery rate / 平均物流延迟率 | 5.44% |
| Review rate / 评价率 | 99.2% |
| Avg review score / 平均评价分 | 4.09 / 5 |

---

## 2. Overall Performance / 整体经营表现

Over roughly two years the store accumulated **R$ 16.0M GMV** on **99.4K orders**,
with a stable **AOV around R$ 161**. Delivery is reliable (**93% delivered**, only
**5.4% late**) and customer sentiment is healthy (**4.09/5**, review rate **99%**).

在约两年区间内，商店累计 **1600 万雷亚尔 GMV**、**9.94 万笔订单**，
**客单价稳定在 161 雷亚尔左右**。物流可靠（**送达率 93%**、**延迟仅 5.4%**），
客户口碑健康（**4.09/5**，评价率 **99%**）。

Trend detail (daily GMV, 7-day moving average, cumulative curve, day-over-day) is in:

趋势细节（每日 GMV、7 日移动平均、累计曲线、日环比）见：

`dashboard/gmv_trend.png`, `dashboard/cumulative_business_trend.png`,
`dashboard/day_over_day_growth.png`

---

## 3. Customer RFM Segmentation / 客户 RFM 分层

**Method / 方法.** Valid orders are aggregated to `customer_unique_id`. Recency,
Frequency and Monetary are each scored into quintiles (1–5) via a rank-based
`qcut` (robust to ties), then combined into business segments (Champions, Loyal,
Recent, Promising, At Risk, Can't-Lose, Hibernating, Lost).

**方法.** 有效订单聚合到 `customer_unique_id`，对 Recency / Frequency / Monetary
分别用基于 rank 的 `qcut` 打五分位分（对并列稳健），再组合成业务分层（重要价值、
忠诚、新近活跃、有潜力、需挽留、高价值流失预警、沉睡、已流失）。

**Key structural insight / 关键结构性洞察.** With **96,096 unique customers** behind
**99,441 orders**, the marketplace is overwhelmingly **one-time buyers** — repeat
purchasing is rare (a well-known trait of this dataset). Practically:

在 **9.94 万订单** 背后是 **9.61 万唯一客户**，说明平台以 **一次性购买** 为主，
复购非常少（该数据集的公认特征）。这意味着：

- Frequency has very low variance, so segments lean on **Recency** and **Monetary**.
  Frequency 方差极低，因此分层主要依赖 **Recency** 与 **Monetary**。
- The business lever is **acquisition + reactivation**, not loyalty-loop optimization.
  业务抓手是 **拉新 + 唤醒沉睡**，而非复购闭环优化。

**Results / 结果** (snapshot date / 快照日 2018-09-04, 94,990 valid-order customers /
基于有效订单的 94,990 名客户):

| Segment / 分层 | Customers / 客户数 | Share / 占比 | Avg Monetary / 平均金额 | Revenue Share / 收入占比 |
|---|---:|---:|---:|---:|
| Loyal / 忠诚 | 19,109 | 20.1% | R$ 161.7 | 19.6% |
| Champions / 重要价值 | 15,218 | 16.0% | R$ 177.6 | 17.2% |
| Recent / 新近活跃 | 15,180 | 16.0% | R$ 163.9 | 15.8% |
| At Risk / 需挽留 | 11,381 | 12.0% | R$ 170.0 | 12.3% |
| Lost / 已流失 | 11,493 | 12.1% | R$ 159.7 | 11.7% |
| Can't Lose / 高价值预警 | 7,505 | 7.9% | R$ 169.2 | 8.1% |
| Hibernating / 沉睡 | 7,617 | 8.0% | R$ 165.6 | 8.0% |
| Promising / 有潜力 | 7,487 | 7.9% | R$ 154.5 | 7.4% |

The near-flat average monetary across segments (R$ 155–178) confirms the point:
value differences are driven by **recency**, not by heavy repeat spend. High-recency
segments (Champions, Loyal, Recent) already hold **~52% of customers and revenue** —
the priority is keeping them active and reactivating At-Risk / Lost tails.

各分层平均金额几乎持平（R$ 155–178），印证了前述判断：价值差异由 **recency** 驱动，
而非高额复购。高活跃分层（Champions、Loyal、Recent）已占 **约 52% 的客户与收入**——
重点是保持其活跃，并唤醒 At-Risk / Lost 长尾。

**Outputs / 产出:**

- `data/ads/ads_customer_rfm.csv` — customer-level R/F/M scores & segment / 客户级打分与分层
- `data/ads/ads_customer_rfm_segment_summary.csv` — per-segment summary / 分层汇总
- `dashboard/rfm_segment_customers.png`, `dashboard/rfm_segment_monetary.png`

---

## 4. Product Category Analysis / 商品类目分析

**Method / 方法.** Order items are joined to products and the English category
translation, filtered to valid orders, and ranked by product revenue. A cumulative
revenue share column exposes the **Pareto (80/20)** structure.

**方法.** 订单商品关联商品维表与英文类目翻译，过滤为有效订单后按商品收入排名，
累计收入占比列揭示 **帕累托（二八）** 结构。

**Results / 结果.** Across **74 categories**, just **18 categories make up 80% of
revenue** — a clear Pareto structure. Top categories by revenue share:

**结果.** 在 **74 个类目** 中，**仅 18 个类目就贡献了 80% 的收入**——典型的帕累托结构。
收入占比前列类目：

| Rank / 排名 | Category / 类目 | Revenue Share / 收入占比 |
|---:|---|---:|
| 1 | health_beauty / 健康美容 | 9.31% |
| 2 | watches_gifts / 手表礼品 | 8.88% |
| 3 | bed_bath_table / 床品浴室 | 7.68% |
| 4 | sports_leisure / 运动休闲 | 7.26% |
| 5 | computers_accessories / 电脑配件 | 6.70% |

Merchandising and inventory should concentrate on this top tier; the long tail of
~56 categories together contributes only ~20% of revenue.

选品与库存应聚焦头部类目；约 56 个长尾类目合计仅贡献约 20% 的收入。

**Outputs / 产出:**

- `data/ads/ads_product_category_rank.csv` — ranked categories + Pareto share / 类目排名 + 帕累托占比
- `dashboard/product_category_top15_revenue.png` — top-15 by revenue / 收入前 15
- `dashboard/product_category_pareto.png` — revenue bars + cumulative line / 收入柱 + 累计线

---

## 5. Geographic Analysis / 地域分析

**Method / 方法.** The DWD table is aggregated by `customer_state` into GMV, orders,
customers, AOV, delivery rate, late-delivery rate, average delivery days and review
score, then ranked by GMV with a GMV share column.

**方法.** DWD 表按 `customer_state` 汇总 GMV、订单、客户、客单价、送达率、
延迟率、平均送达天数与评价分，按 GMV 排名并给出 GMV 占比列。

**Results / 结果.** Demand is highly concentrated in the Southeast: the **top 3
states hold 62.5% of GMV** — SP **37.35%**, RJ **13.44%**, MG **11.71%**.

**结果.** 需求高度集中在东南部：**前 3 州占 GMV 62.5%**——SP **37.35%**、
RJ **13.44%**、MG **11.71%**。

Cross-referencing revenue against delivery performance exposes the
**demand-vs-logistics tension**: RJ and BA combine high demand with the worst
service — late-delivery rates of **12.1% / 12.2%** and average delivery times of
**14.9 / 18.9 days**, well above SP. These states are the priority for fulfilment
investment.

将收入与物流表现交叉对比,揭示 **需求与物流的张力**:RJ 与 BA 需求高、服务却最差
——延迟率 **12.1% / 12.2%**、平均送达 **14.9 / 18.9 天**,明显高于 SP。这两个州是
履约投入的优先项。

**Outputs / 产出:**

- `data/ads/ads_geo_state_summary.csv`
- `dashboard/geo_top_states_gmv.png`, `dashboard/geo_state_delivery_performance.png`

---

## 6. Takeaways & Recommendations / 结论与建议

1. **Acquisition-led marketplace / 拉新驱动型平台** — one-time buyers dominate;
   invest in acquisition and post-purchase reactivation rather than loyalty loops.
   一次性购买为主；重点投入拉新与购后唤醒，而非复购闭环。
2. **Concentrated revenue / 收入高度集中** — a small set of categories and a few
   states drive most GMV; focus merchandising and fulfilment there.
   少数类目与少数州贡献主要 GMV；选品与履约应聚焦于此。
3. **Protect the delivery advantage / 守住物流优势** — 93% delivery / 4.09 review is
   a strength; watch late-delivery in far, high-GMV states.
   93% 送达、4.09 评价是优势；关注远距离高 GMV 州的延迟风险。

---

## 7. How to Reproduce / 复现方式

```bash
# 1) Core warehouse (Raw -> ODS -> DWD -> DWS -> ADS -> DQ -> charts)
python scripts/run_pipeline.py

# 2) Business-analysis layer (RFM + category + geography)
python scripts/run_analysis_pipeline.py

# 3) Tests
pytest
```

> Note / 说明: All figures in this report are computed from the actual pipeline
> output (verified run: pytest 15 passed, pipeline 7/7 + DQ 96/96, analysis 3/3).
> Re-running the commands above regenerates every CSV and chart referenced here.
> 本报告所有数字均来自真实主流程产出（已验证：pytest 15 通过、主流程 7/7 +
> 数据质量 96/96、分析 3/3）。重新运行上述命令即可再生所有引用的 CSV 与图表。
