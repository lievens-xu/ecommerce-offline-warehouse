"""
Build a self-contained interactive HTML dashboard from the ADS layer.

从 ADS 层构建一个自包含的交互式 HTML 看板。

Reads the daily overview + the three analysis tables (RFM / category / geography)
and renders a single `dashboard/index.html` with inlined data and Chart.js (CDN).
The file opens directly in a browser — no server needed — which makes it ideal for
GitHub Pages or a portfolio link.

读取每日概览与三张分析表（RFM / 类目 / 地域），生成单个 `dashboard/index.html`，
数据内联、图表用 Chart.js（CDN）。文件可直接用浏览器打开、无需服务器，适合
GitHub Pages 或作品集链接。

Input  / 输入: dashboard/dashboard_kpi_summary.csv, data/ads/*.csv
Output / 输出: dashboard/index.html
"""

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
ADS_DIR = ROOT_DIR / "data" / "ads"
DASHBOARD_DIR = ROOT_DIR / "dashboard"
DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = DASHBOARD_DIR / "index.html"


def read_csv_safe(path: Path) -> pd.DataFrame:
    """
    Read a CSV, returning an empty DataFrame (with a warning) if missing.
    读取 CSV；文件缺失时返回空表并告警。
    """
    if not path.exists():
        print(f"[WARN] Missing input, section will be empty: {path}")
        return pd.DataFrame()
    return pd.read_csv(path, low_memory=False)


def build_payload() -> dict:
    """
    Assemble the JSON payload the HTML page renders.
    组装 HTML 页面渲染所需的 JSON 数据。
    """
    kpi = read_csv_safe(DASHBOARD_DIR / "dashboard_kpi_summary.csv")
    daily = read_csv_safe(ADS_DIR / "ads_daily_business_overview.csv")
    rfm = read_csv_safe(ADS_DIR / "ads_customer_rfm_segment_summary.csv")
    category = read_csv_safe(ADS_DIR / "ads_product_category_rank.csv")
    geo = read_csv_safe(ADS_DIR / "ads_geo_state_summary.csv")

    payload: dict = {"generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    # KPI cards / KPI 卡片
    if not kpi.empty:
        row = kpi.iloc[0].to_dict()
        payload["kpi"] = {
            "date_range": f"{row.get('start_date', '')} ~ {row.get('end_date', '')}",
            "total_gmv": float(row.get("total_gmv", 0)),
            "total_order_count": int(row.get("total_order_count", 0)),
            "overall_aov": float(row.get("overall_aov", 0)),
            "avg_delivery_rate": float(row.get("average_delivery_rate", 0)),
            "avg_late_delivery_rate": float(row.get("average_late_delivery_rate", 0)),
            "average_review_score": float(row.get("average_review_score", 0)),
        }

    # Daily GMV trend (downsample dates for readability) / 每日 GMV 趋势
    if not daily.empty:
        d = daily.copy()
        d["stat_date"] = d["stat_date"].astype(str)
        payload["daily"] = {
            "dates": d["stat_date"].tolist(),
            "gmv": pd.to_numeric(d["daily_gmv"], errors="coerce").fillna(0).round(2).tolist(),
            "gmv_7d": pd.to_numeric(d.get("gmv_7d_moving_avg", 0), errors="coerce")
            .fillna(0)
            .round(2)
            .tolist(),
        }

    # RFM segments / RFM 分层
    if not rfm.empty:
        r = rfm.sort_values("total_monetary", ascending=False)
        payload["rfm"] = {
            "segments": r["segment"].tolist(),
            "customer_count": r["customer_count"].astype(int).tolist(),
            "customer_pct": pd.to_numeric(r["customer_pct"], errors="coerce").tolist(),
            "total_monetary": pd.to_numeric(r["total_monetary"], errors="coerce").round(2).tolist(),
            "monetary_pct": pd.to_numeric(r["monetary_pct"], errors="coerce").tolist(),
        }

    # Product categories (top 15) + Pareto (top 20) / 商品类目
    if not category.empty:
        c = category.sort_values("revenue_rank")
        top15 = c.head(15)
        top20 = c.head(20)
        payload["category"] = {
            "top_names": top15["category"].tolist(),
            "top_revenue": pd.to_numeric(top15["product_revenue"], errors="coerce").round(2).tolist(),
            "pareto_names": top20["category"].tolist(),
            "pareto_revenue": pd.to_numeric(top20["product_revenue"], errors="coerce").round(2).tolist(),
            "pareto_cumulative": pd.to_numeric(
                top20["cumulative_revenue_share_pct"], errors="coerce"
            ).tolist(),
            "categories_for_80pct": int((c["cumulative_revenue_share_pct"] <= 80).sum()) + 1,
            "total_categories": int(len(c)),
        }

    # Geography (top 12 states) / 地域
    if not geo.empty:
        g = geo.sort_values("gmv_rank").head(12)
        payload["geo"] = {
            "states": g["customer_state"].tolist(),
            "gmv": pd.to_numeric(g["gmv"], errors="coerce").round(2).tolist(),
            "gmv_share_pct": pd.to_numeric(g["gmv_share_pct"], errors="coerce").tolist(),
            "late_delivery_rate": (
                pd.to_numeric(g["late_delivery_rate"], errors="coerce").fillna(0) * 100
            )
            .round(2)
            .tolist(),
            "avg_delivery_days": pd.to_numeric(g["avg_delivery_days"], errors="coerce").tolist(),
        }

    return payload


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>E-commerce Warehouse Dashboard / 电商数仓看板</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
  :root{--bg:#0f172a;--card:#1e293b;--muted:#94a3b8;--text:#e2e8f0;--accent:#38bdf8;}
  *{box-sizing:border-box;}
  body{margin:0;background:var(--bg);color:var(--text);
       font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,"PingFang SC","Microsoft YaHei",sans-serif;}
  header{padding:28px 32px 12px;}
  h1{margin:0;font-size:22px;} .sub{color:var(--muted);font-size:13px;margin-top:6px;}
  .wrap{padding:16px 32px 48px;max-width:1200px;margin:0 auto;}
  .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin:18px 0 26px;}
  .card{background:var(--card);border-radius:12px;padding:16px 18px;border:1px solid #334155;}
  .card .label{color:var(--muted);font-size:12px;} .card .value{font-size:24px;font-weight:600;margin-top:6px;}
  .grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;}
  .panel{background:var(--card);border-radius:12px;padding:18px;border:1px solid #334155;margin-bottom:20px;}
  .panel h2{margin:0 0 4px;font-size:15px;} .panel p{margin:0 0 12px;color:var(--muted);font-size:12px;}
  .full{grid-column:1 / -1;}
  canvas{max-height:340px;}
  footer{color:var(--muted);font-size:12px;text-align:center;padding:20px;}
  @media(max-width:820px){.grid{grid-template-columns:1fr;}}
</style>
</head>
<body>
<header>
  <h1>E-commerce Offline Warehouse — Business Dashboard</h1>
  <div class="sub">电商离线数仓 · 经营看板 &nbsp;|&nbsp; Olist Brazilian E-Commerce &nbsp;|&nbsp; <span id="range"></span></div>
</header>
<div class="wrap">
  <div class="cards" id="cards"></div>
  <div class="panel full">
    <h2>Daily GMV Trend / 每日 GMV 趋势</h2>
    <p>Daily GMV with 7-day moving average / 每日 GMV 与 7 日移动平均</p>
    <canvas id="gmvChart"></canvas>
  </div>
  <div class="grid">
    <div class="panel">
      <h2>RFM Segments — Customers / RFM 分层客户数</h2>
      <p id="rfmSub">Customer distribution across RFM segments</p>
      <canvas id="rfmChart"></canvas>
    </div>
    <div class="panel">
      <h2>Top States by GMV / GMV 前列州</h2>
      <p>Revenue concentration by state / 各州收入集中度</p>
      <canvas id="geoChart"></canvas>
    </div>
    <div class="panel">
      <h2>Top Categories by Revenue / 收入前列类目</h2>
      <p>Top 15 product categories / 前 15 商品类目</p>
      <canvas id="catChart"></canvas>
    </div>
    <div class="panel">
      <h2>Category Pareto / 类目帕累托</h2>
      <p id="paretoSub">Revenue + cumulative share</p>
      <canvas id="paretoChart"></canvas>
    </div>
  </div>
</div>
<footer>Generated by build_html_dashboard.py · <span id="gen"></span></footer>
<script>
const DATA = __PAYLOAD__;
const fmt = n => (n>=1e6? (n/1e6).toFixed(2)+'M' : n>=1e3? (n/1e3).toFixed(1)+'K' : n);
const brl = n => 'R$ ' + fmt(n);
Chart.defaults.color = '#94a3b8'; Chart.defaults.borderColor = '#334155';
const PAL = ['#38bdf8','#34d399','#fbbf24','#f87171','#a78bfa','#f472b6','#22d3ee','#facc15'];

document.getElementById('gen').textContent = DATA.generated_at || '';

// KPI cards
if(DATA.kpi){
  document.getElementById('range').textContent = DATA.kpi.date_range || '';
  const cards = [
    ['GMV', brl(DATA.kpi.total_gmv)],
    ['Orders / 订单', DATA.kpi.total_order_count.toLocaleString()],
    ['AOV / 客单价', brl(DATA.kpi.overall_aov)],
    ['Delivery Rate / 送达率', (DATA.kpi.avg_delivery_rate*100).toFixed(1)+'%'],
    ['Late Rate / 延迟率', (DATA.kpi.avg_late_delivery_rate*100).toFixed(1)+'%'],
    ['Review / 评价', DATA.kpi.average_review_score.toFixed(2)+' / 5'],
  ];
  document.getElementById('cards').innerHTML = cards.map(
    c => `<div class="card"><div class="label">${c[0]}</div><div class="value">${c[1]}</div></div>`
  ).join('');
}

// Daily GMV trend
if(DATA.daily){
  new Chart(document.getElementById('gmvChart'), {
    type:'line',
    data:{labels:DATA.daily.dates, datasets:[
      {label:'Daily GMV', data:DATA.daily.gmv, borderColor:'#38bdf8', backgroundColor:'rgba(56,189,248,.15)', borderWidth:1, pointRadius:0, fill:true},
      {label:'7d Moving Avg', data:DATA.daily.gmv_7d, borderColor:'#fbbf24', borderWidth:2, pointRadius:0}
    ]},
    options:{responsive:true, interaction:{mode:'index',intersect:false},
      scales:{x:{ticks:{maxTicksLimit:12}}, y:{ticks:{callback:v=>fmt(v)}}}}
  });
}

// RFM segments (customers + revenue toggle via two datasets)
if(DATA.rfm){
  document.getElementById('rfmSub').textContent =
    'Customers vs revenue share across ' + DATA.rfm.segments.length + ' segments';
  new Chart(document.getElementById('rfmChart'), {
    type:'bar',
    data:{labels:DATA.rfm.segments, datasets:[
      {label:'Customers', data:DATA.rfm.customer_count, backgroundColor:'#38bdf8'},
      {label:'Revenue (R$)', data:DATA.rfm.total_monetary, backgroundColor:'#a78bfa', yAxisID:'y1'}
    ]},
    options:{responsive:true, indexAxis:'y',
      scales:{x:{ticks:{callback:v=>fmt(v)}}}}
  });
}

// Geography
if(DATA.geo){
  new Chart(document.getElementById('geoChart'), {
    type:'bar',
    data:{labels:DATA.geo.states, datasets:[
      {label:'GMV', data:DATA.geo.gmv, backgroundColor:'#34d399'},
      {label:'Late Delivery %', data:DATA.geo.late_delivery_rate, backgroundColor:'#f87171', yAxisID:'y1'}
    ]},
    options:{responsive:true,
      scales:{y:{ticks:{callback:v=>fmt(v)}},
        y1:{position:'right',grid:{drawOnChartArea:false},ticks:{callback:v=>v+'%'}}}}
  });
}

// Categories top 15
if(DATA.category){
  new Chart(document.getElementById('catChart'), {
    type:'bar',
    data:{labels:DATA.category.top_names, datasets:[
      {label:'Revenue (R$)', data:DATA.category.top_revenue, backgroundColor:'#22d3ee'}
    ]},
    options:{responsive:true, indexAxis:'y', plugins:{legend:{display:false}},
      scales:{x:{ticks:{callback:v=>fmt(v)}}}}
  });
  document.getElementById('paretoSub').textContent =
    DATA.category.categories_for_80pct + ' of ' + DATA.category.total_categories +
    ' categories make up 80% of revenue';
  new Chart(document.getElementById('paretoChart'), {
    data:{labels:DATA.category.pareto_names, datasets:[
      {type:'bar', label:'Revenue', data:DATA.category.pareto_revenue, backgroundColor:'#38bdf8'},
      {type:'line', label:'Cumulative %', data:DATA.category.pareto_cumulative,
       borderColor:'#fbbf24', borderWidth:2, pointRadius:0, yAxisID:'y1'}
    ]},
    options:{responsive:true,
      scales:{y:{ticks:{callback:v=>fmt(v)}},
        y1:{position:'right',min:0,max:105,grid:{drawOnChartArea:false},ticks:{callback:v=>v+'%'}}}}
  });
}
</script>
</body>
</html>
"""


def main() -> None:
    print("[INFO] Building HTML dashboard ...")
    payload = build_payload()
    html = HTML_TEMPLATE.replace("__PAYLOAD__", json.dumps(payload, ensure_ascii=False))
    OUTPUT_FILE.write_text(html, encoding="utf-8")
    print(f"[OK] HTML dashboard generated: {OUTPUT_FILE}")
    print("[DONE] Open dashboard/index.html in a browser.")


if __name__ == "__main__":
    main()
