import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
sys.path.append("modules")
from analysis import run_analysis
from summary import generate_summary
from agents import cost_forecasting_agent, risk_alert_agent, anomaly_explanation_agent

st.set_page_config(page_title="ClaimsPulse", page_icon="🏥", layout="wide")

BG    = "#f0f2f6"
CARD  = "#ffffff"
LINE  = "#e2e6ef"
GRN   = "#0ea47a"
BLU   = "#2563eb"
AMB   = "#d97706"
RED   = "#dc2626"
TXT   = "#111827"
MUT   = "#6b7280"
NAV   = "#1e293b"

def T(h=300):
    return dict(
        height=h, margin=dict(t=10,b=10,l=10,r=10),
        paper_bgcolor=CARD, plot_bgcolor=CARD,
        font=dict(family="Inter,sans-serif", color=MUT, size=11),
        xaxis=dict(showgrid=False, linecolor=LINE,
                   tickfont=dict(color=MUT, size=10), zeroline=False),
        yaxis=dict(showgrid=True, gridcolor=LINE, gridwidth=1,
                   linecolor="rgba(0,0,0,0)", zeroline=False,
                   tickfont=dict(color=MUT, size=10),
                   tickprefix="$", tickformat=",.2s"),
        showlegend=False,
        hoverlabel=dict(bgcolor=BG, bordercolor=LINE,
                        font=dict(color=TXT, size=12))
    )

def mk_bar(df, x, y, color=GRN, h=300):
    fig = go.Figure(go.Bar(
        x=df[x], y=df[y],
        marker=dict(color=color, opacity=0.9, line=dict(width=0)),
        hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>"
    ))
    fig.update_layout(**T(h))
    return fig

def mk_line(df, x, y, color=GRN, h=300):
    r,g,b = tuple(int(color.lstrip("#")[i:i+2],16) for i in (0,2,4))
    fig = go.Figure(go.Scatter(
        x=df[x], y=df[y], mode="lines",
        line=dict(color=color, width=2.5),
        fill="tozeroy", fillcolor=f"rgba({r},{g},{b},0.08)",
        hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>"
    ))
    fig.update_layout(**T(h))
    return fig

def html_table(df):
    """Render a pandas DataFrame as a styled HTML table - always visible in dark mode."""
    cols = df.columns.tolist()
    header = "".join(f"<th>{c}</th>" for c in cols)
    rows = ""
    for _, row in df.iterrows():
        cells = "".join(f"<td>{row[c]}</td>" for c in cols)
        rows += f"<tr>{cells}</tr>"
    return f"""
    <div style="overflow-x:auto; margin-top:8px;">
    <table style="width:100%; border-collapse:collapse; font-size:13px;
                  font-family:Inter,sans-serif; color:{TXT};">
      <thead>
        <tr style="border-bottom:2px solid {LINE};">
          {header}
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
    </div>
    <style>
    table th {{
      padding: 10px 14px; text-align:left;
      font-size:11px; font-weight:600; color:{MUT};
      text-transform:uppercase; letter-spacing:0.8px;
      background:{CARD};
    }}
    table td {{
      padding: 9px 14px; border-bottom:1px solid {LINE};
      color:{TXT}; background:{CARD};
    }}
    table tr:hover td {{ background:#f8fafc; }}
    </style>
    """

NB = {"displayModeBar": False}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*, html, body, [class*="css"] {{ font-family:'Inter',sans-serif !important; }}

.stApp, .main,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
section.main > div.block-container {{
    background:{BG} !important;
}}
.block-container {{
    padding:2rem 2.5rem 3rem !important;
    max-width:1380px !important;
}}
#MainMenu, footer, header {{ visibility:hidden; }}
::-webkit-scrollbar {{ width:4px; height:4px; }}
::-webkit-scrollbar-track {{ background:{BG}; }}
::-webkit-scrollbar-thumb {{ background:{LINE}; border-radius:2px; }}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    background:#ffffff; border:1px solid {LINE};
    border-radius:8px; padding:3px; gap:2px; margin-bottom:20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}}
.stTabs [data-baseweb="tab"] {{
    border-radius:6px; padding:8px 22px; font-size:13px; font-weight:500;
    color:{MUT} !important; background:transparent !important; border:none !important;
}}
.stTabs [aria-selected="true"] {{
    background:{BG} !important; color:{TXT} !important;
    border:1px solid {LINE} !important;
}}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {{ display:none !important; }}

/* ── Metric cards ── */
[data-testid="stMetric"] {{
    background:{CARD} !important;
    border:1px solid {LINE} !important;
    border-top:2px solid {GRN} !important;
    border-radius:12px !important;
    padding:18px 20px !important;
}}
[data-testid="stMetricLabel"] p {{
    font-size:11px !important; font-weight:600 !important;
    color:{MUT} !important; text-transform:uppercase !important;
    letter-spacing:0.9px !important;
}}
[data-testid="stMetricValue"] {{
    font-family:'JetBrains Mono',monospace !important;
    font-size:26px !important; font-weight:500 !important;
    color:{TXT} !important;
}}
[data-testid="column"]:last-child [data-testid="stMetric"] {{
    border-top:2px solid {RED} !important;
}}
[data-testid="column"]:last-child [data-testid="stMetricValue"] {{
    color:{RED} !important;
}}

/* ── Selectbox ── */
[data-baseweb="select"] > div {{
    background:{CARD} !important; border:1px solid {LINE} !important;
    border-radius:8px !important; color:{TXT} !important;
}}
[data-baseweb="popover"], ul[data-baseweb="menu"] {{
    background:{CARD} !important; border:1px solid {LINE} !important;
}}
li[role="option"] {{ color:{TXT} !important; }}
li[role="option"]:hover {{ background:{LINE} !important; }}

/* ── Number input ── */
[data-testid="stNumberInput"] input {{
    background:{CARD} !important; border:1px solid {LINE} !important;
    color:{TXT} !important; border-radius:8px !important;
}}

/* ── Spinner ── */
.stSpinner > div {{ color:{GRN} !important; }}

/* ── Caption ── */
small, .stCaption p {{ color:{MUT} !important; font-size:11px !important; }}

/* ── Header ── */
.topbar {{
    display:flex; align-items:center; justify-content:space-between;
    padding:16px 24px; margin-bottom:20px;
    background:#ffffff;
    border:1px solid {LINE};
    border-radius:12px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}}
.brand {{ display:flex; align-items:center; gap:13px; }}
.logo {{
    width:44px; height:44px; border-radius:11px;
    background:linear-gradient(135deg,{GRN},{BLU});
    display:flex; align-items:center; justify-content:center;
    font-size:21px; box-shadow:0 4px 20px rgba(0,212,170,0.22);
}}
.brand-name {{ font-size:21px; font-weight:700; color:{TXT}; letter-spacing:-0.4px; }}
.brand-name em {{ color:{GRN}; font-style:normal; }}
.brand-sub {{ font-size:12px; color:{MUT}; margin-top:2px; }}
.topbar-right {{ display:flex; align-items:center; gap:22px; }}
.hst {{ text-align:right; }}
.hst-v {{
    font-family:'JetBrains Mono',monospace !important;
    font-size:18px; font-weight:500; color:{TXT}; line-height:1;
}}
.hst-l {{
    font-size:10px; color:{MUT};
    text-transform:uppercase; letter-spacing:0.9px; margin-top:3px;
}}
.sep {{ width:1px; height:30px; background:{LINE}; }}
.live {{
    display:inline-flex; align-items:center; gap:7px;
    background:#ecfdf5; border:1px solid #6ee7b7;
    border-radius:20px; padding:6px 15px;
    font-size:11px; font-weight:600; color:{GRN}; letter-spacing:1px;
}}
.live-dot {{
    width:7px; height:7px; border-radius:50%;
    background:{GRN}; box-shadow:0 0 7px {GRN};
    animation:lp 1.8s ease-in-out infinite;
}}
@keyframes lp {{ 0%,100%{{opacity:1;transform:scale(1)}} 50%{{opacity:.3;transform:scale(.8)}} }}

/* ── Section heading ── */
.sh {{
    display:flex; align-items:center; justify-content:space-between;
    padding-bottom:10px; margin:4px 0 14px 0;
    border-bottom:1px solid {LINE};
}}
.sh-t {{
    font-size:11px; font-weight:600; color:{MUT};
    text-transform:uppercase; letter-spacing:1.2px;
}}
.sh-b {{
    font-size:10px; color:{MUT};
    background:#f1f5f9; border:1px solid {LINE};
    border-radius:4px; padding:2px 9px; font-weight:500;
    text-transform:none; letter-spacing:0;
}}

/* ── AI block ── */
.ai {{
    background:linear-gradient(135deg,rgba(14,164,122,.05),rgba(37,99,235,.03));
    border:1px solid rgba(14,164,122,.2); border-radius:10px;
    padding:18px 22px; margin-bottom:22px; position:relative;
}}
.ai::after {{
    content:''; position:absolute; top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,{GRN},{BLU},transparent);
    border-radius:10px 10px 0 0;
}}
.ai-lbl {{
    font-size:9.5px; font-weight:700; letter-spacing:1.8px;
    text-transform:uppercase; color:{GRN};
    display:flex; align-items:center; gap:7px; margin-bottom:11px;
}}
.ai-dot {{ width:5px; height:5px; border-radius:50%; background:{GRN}; box-shadow:0 0 5px {GRN}; }}
.ai-txt {{ font-size:14px; line-height:1.85; font-weight:400; color:#374151; }}

/* ── Alert ── */
.alrt {{
    background:#fef2f2; border:1px solid #fecaca;
    border-left:3px solid {RED}; border-radius:8px;
    padding:11px 16px; margin-bottom:9px;
    font-size:13px; color:#991b1b; line-height:1.5;
}}

/* ── Agent bar ── */
.agbar {{
    background:#f0fdf4; border:1px solid #bbf7d0;
    border-radius:8px; padding:12px 17px; margin-bottom:20px;
    font-size:13px; color:#166534;
}}
.agbar b {{ color:#15803d; }}

/* ── Footer ── */
.ft {{
    text-align:center; color:{MUT}; font-size:11.5px;
    padding:20px 0 6px; border-top:1px solid {LINE}; margin-top:30px;
}}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load():
    return pd.read_csv("data/claims.csv")

df      = load()
results = run_analysis(df)

# ── Top bar ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="topbar">
  <div class="brand">
    <div class="logo">🏥</div>
    <div>
      <div class="brand-name">Claims<em>Pulse</em></div>
      <div class="brand-sub">Healthcare Insurance Analytics &nbsp;·&nbsp; Executive Decision Platform</div>
    </div>
  </div>
  <div class="topbar-right">
    <div class="hst">
      <div class="hst-v">{results['total_claims']:,}</div>
      <div class="hst-l">Total Claims</div>
    </div>
    <div class="sep"></div>
    <div class="hst">
      <div class="hst-v">${results['total_cost']/1e6:.1f}M</div>
      <div class="hst-l">Total Spend</div>
    </div>
    <div class="sep"></div>
    <div class="live"><div class="live-dot"></div>LIVE</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI row ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:grid; grid-template-columns:repeat(5,1fr); gap:14px; margin-bottom:20px;">
  <div style="background:#fff; border:1px solid {LINE}; border-top:3px solid {GRN};
              border-radius:10px; padding:16px 20px;">
    <div style="font-size:10.5px; font-weight:600; color:{MUT}; text-transform:uppercase;
                letter-spacing:0.9px; margin-bottom:8px;">Total Claims</div>
    <div style="font-family:'JetBrains Mono',monospace; font-size:26px;
                font-weight:600; color:{TXT};">{results['total_claims']:,}</div>
  </div>
  <div style="background:#fff; border:1px solid {LINE}; border-top:3px solid {BLU};
              border-radius:10px; padding:16px 20px;">
    <div style="font-size:10.5px; font-weight:600; color:{MUT}; text-transform:uppercase;
                letter-spacing:0.9px; margin-bottom:8px;">Total Spend</div>
    <div style="font-family:'JetBrains Mono',monospace; font-size:26px;
                font-weight:600; color:{TXT};">${results['total_cost']/1e6:.2f}M</div>
  </div>
  <div style="background:#fff; border:1px solid {LINE}; border-top:3px solid {AMB};
              border-radius:10px; padding:16px 20px;">
    <div style="font-size:10.5px; font-weight:600; color:{MUT}; text-transform:uppercase;
                letter-spacing:0.9px; margin-bottom:8px;">Avg Cost / Claim</div>
    <div style="font-family:'JetBrains Mono',monospace; font-size:26px;
                font-weight:600; color:{TXT};">${results['average_cost']:,.0f}</div>
  </div>
  <div style="background:#fff; border:1px solid {LINE}; border-top:3px solid {AMB};
              border-radius:10px; padding:16px 20px;">
    <div style="font-size:10.5px; font-weight:600; color:{MUT}; text-transform:uppercase;
                letter-spacing:0.9px; margin-bottom:8px;">Peak Claim</div>
    <div style="font-family:'JetBrains Mono',monospace; font-size:26px;
                font-weight:600; color:{TXT};">${results['highest_claim']:,.0f}</div>
  </div>
  <div style="background:#fff; border:1px solid {LINE}; border-top:3px solid {RED};
              border-radius:10px; padding:16px 20px;">
    <div style="font-size:10.5px; font-weight:600; color:{MUT}; text-transform:uppercase;
                letter-spacing:0.9px; margin-bottom:8px;">Anomalous Months</div>
    <div style="font-family:'JetBrains Mono',monospace; font-size:26px;
                font-weight:600; color:{RED};">{len(results['anomalies'])}</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1,tab2,tab3,tab4,tab5 = st.tabs([
    "📊  Overview","📈  Trends","🔮  Predictions","⚠️  Risk & Anomalies","📂  Raw Data"
])

# ═══════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════
with tab1:
    summary = generate_summary(results)
    st.markdown(f"""
    <div class="ai">
      <div class="ai-lbl"><div class="ai-dot"></div>AI Executive Summary &nbsp;·&nbsp; Qwen via Ollama</div>
      <div class="ai-txt">{summary}</div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown('<div class="sh"><span class="sh-t">Cost by Claim Category</span><span class="sh-b">Total Spend</span></div>', unsafe_allow_html=True)
        cat = results["cost_by_category"].reset_index()
        st.plotly_chart(mk_bar(cat,"claim_category","total_cost",GRN,280), use_container_width=True, config=NB)
        t = cat.copy()
        t.columns = ["Category","Total Cost","Avg Cost","Claims"]
        t["Total Cost"] = t["Total Cost"].apply(lambda x: f"${x:,.0f}")
        t["Avg Cost"]   = t["Avg Cost"].apply(lambda x: f"${x:,.0f}")
        st.markdown(html_table(t), unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="sh"><span class="sh-t">Top 10 Providers by Spend</span><span class="sh-b">Billing Volume</span></div>', unsafe_allow_html=True)
        prov = results["cost_by_provider"].reset_index()
        fp = mk_bar(prov,"provider","total_cost",BLU,280)
        fp.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fp, use_container_width=True, config=NB)
        p = prov.copy()
        p.columns = ["Provider","Total Cost","Avg Cost","Claims"]
        p["Total Cost"] = p["Total Cost"].apply(lambda x: f"${x:,.0f}")
        p["Avg Cost"]   = p["Avg Cost"].apply(lambda x: f"${x:,.0f}")
        st.markdown(html_table(p), unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# TAB 2 — TRENDS
# ═══════════════════════════════════════════════
with tab2:
    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown('<div class="sh"><span class="sh-t">Monthly Cost Trend</span><span class="sh-b">All Time</span></div>', unsafe_allow_html=True)
        m = results["monthly_trend"].copy()
        m["month"] = m["month"].astype(str)
        st.plotly_chart(mk_line(m,"month","total_cost",GRN,300), use_container_width=True, config=NB)

    with c2:
        st.markdown('<div class="sh"><span class="sh-t">Yearly Cost Trend</span><span class="sh-b">2010–Present</span></div>', unsafe_allow_html=True)
        y = results["yearly_trend"].copy()
        y = y[y["year"]>=2010].copy()
        y["year"] = y["year"].astype(str)
        st.plotly_chart(mk_line(y,"year","total_cost",BLU,300), use_container_width=True, config=NB)

    st.markdown('<div class="sh" style="margin-top:12px"><span class="sh-t">Yearly Summary</span><span class="sh-b">Full History</span></div>', unsafe_allow_html=True)
    yt = results["yearly_trend"].sort_values("year", ascending=False).copy()
    yt.columns = ["Year","Total Cost","Claim Count"]
    yt["Total Cost"] = yt["Total Cost"].apply(lambda x: f"${x:,.0f}")
    st.markdown(html_table(yt), unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# TAB 3 — PREDICTIONS
# ═══════════════════════════════════════════════
with tab3:
    forecast_df, historical_df, score, recommendation = cost_forecasting_agent(df)
    st.markdown(f"""
    <div class="agbar">
      🤖 &nbsp;<b>Forecasting Agent</b> &nbsp;·&nbsp;
      R² Accuracy: <b>{score}%</b> &nbsp;·&nbsp; {recommendation}
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown('<div class="sh"><span class="sh-t">Historical — Last 5 Years</span><span class="sh-b">Actual</span></div>', unsafe_allow_html=True)
        st.plotly_chart(mk_line(historical_df,"month","actual_cost",GRN,280), use_container_width=True, config=NB)

    with c2:
        st.markdown('<div class="sh"><span class="sh-t">Predicted — Next 6 Months</span><span class="sh-b">Forecast</span></div>', unsafe_allow_html=True)
        st.plotly_chart(mk_bar(forecast_df,"Month","Predicted Cost",AMB,220), use_container_width=True, config=NB)
        fd = forecast_df.copy()
        fd["Predicted Cost"] = fd["Predicted Cost"].apply(lambda x: f"${x:,.0f}")
        st.markdown(html_table(fd), unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# TAB 4 — RISK & ANOMALIES
# ═══════════════════════════════════════════════
with tab4:
    risk_df, alerts = risk_alert_agent(df)

    if alerts:
        st.markdown('<div class="sh"><span class="sh-t">Active Risk Alerts</span><span class="sh-b">High Priority</span></div>', unsafe_allow_html=True)
        for a in alerts[:5]:
            clean = a.replace("**", "<b>", 1).replace("**", "</b>", 1)
            st.markdown(f'<div class="alrt">{clean}</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown('<div class="sh"><span class="sh-t">Provider Risk Scoring</span><span class="sh-b">All Providers</span></div>', unsafe_allow_html=True)
        rd = risk_df.copy()
        for col in ["Avg Cost","Total Cost","Max Claim"]:
            if col in rd.columns:
                rd[col] = rd[col].apply(lambda x: f"${x:,.0f}")
        st.markdown(html_table(rd), unsafe_allow_html=True)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        rc = risk_df["Risk Level"].value_counts().reset_index()
        rc.columns = ["Risk Level","Count"]
        cmap = {"🔴 High Risk":RED,"🟡 Medium Risk":AMB,"🟢 Low Risk":GRN}
        fd2 = go.Figure(go.Pie(
            labels=rc["Risk Level"], values=rc["Count"], hole=0.6,
            marker=dict(colors=[cmap.get(l,BLU) for l in rc["Risk Level"]],
                        line=dict(color=BG,width=3)),
            textinfo="percent+label",
            textfont=dict(size=11,color=MUT),
            hovertemplate="<b>%{label}</b><br>%{value} providers<extra></extra>"
        ))
        fd2.update_layout(
            height=200, margin=dict(t=8,b=8,l=8,r=8),
            paper_bgcolor=CARD, plot_bgcolor=CARD, showlegend=False,
            font=dict(family="Inter,sans-serif",color=MUT),
            annotations=[dict(text="Risk Mix",x=0.5,y=0.5,
                              font=dict(size=12,color=MUT),showarrow=False)]
        )
        st.plotly_chart(fd2, use_container_width=True, config=NB)

    with c2:
        anomalies = results["anomalies"].copy()
        anomalies["month"] = anomalies["month"].astype(str)

        st.markdown('<div class="sh"><span class="sh-t">AI Anomaly Analysis</span><span class="sh-b">Qwen via Ollama</span></div>', unsafe_allow_html=True)
        with st.spinner("Analyzing anomalies..."):
            explanation = anomaly_explanation_agent(anomalies, results)

        st.markdown(f"""
        <div class="ai" style="margin-bottom:14px">
          <div class="ai-lbl"><div class="ai-dot"></div>AI Insight</div>
          <div class="ai-txt">{explanation}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f'<div class="alrt">⚠️ &nbsp;{len(anomalies)} months flagged above 2σ threshold</div>', unsafe_allow_html=True)

        if len(anomalies) > 0:
            ma = results["monthly_trend"].copy()
            ma["month"] = ma["month"].astype(str)
            upper = ma["total_cost"].mean() + 2*ma["total_cost"].std()
            fa = go.Figure()
            fa.add_trace(go.Scatter(x=ma["month"],y=ma["total_cost"],mode="lines",
                line=dict(color=BLU,width=1.5),
                hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>"))
            fa.add_trace(go.Scatter(x=anomalies["month"],y=anomalies["total_cost"],mode="markers",
                marker=dict(color=RED,size=9,line=dict(color=TXT,width=1.5)),
                hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>"))
            fa.add_hline(y=upper,line_dash="dot",line_color=AMB,line_width=1.2,
                annotation_text="2σ",annotation_font_color=AMB,annotation_font_size=10)
            lyt = T(230); lyt["showlegend"]=False
            fa.update_layout(**lyt)
            st.plotly_chart(fa, use_container_width=True, config=NB)

        ad = anomalies.copy()
        ad["total_cost"] = ad["total_cost"].apply(lambda x: f"${x:,.0f}")
        ad.columns = ["Month","Total Cost"]
        st.markdown(html_table(ad), unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# TAB 5 — RAW DATA
# ═══════════════════════════════════════════════
with tab5:
    st.markdown('<div class="sh"><span class="sh-t">Claims Explorer</span><span class="sh-b">Interactive Filter</span></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:14px; margin-bottom:16px;">
      <div>
        <div style="font-size:11px; font-weight:600; color:{MUT}; text-transform:uppercase;
                    letter-spacing:0.8px; margin-bottom:6px;">Category</div>
      </div>
      <div>
        <div style="font-size:11px; font-weight:600; color:{MUT}; text-transform:uppercase;
                    letter-spacing:0.8px; margin-bottom:6px;">Provider</div>
      </div>
      <div>
        <div style="font-size:11px; font-weight:600; color:{MUT}; text-transform:uppercase;
                    letter-spacing:0.8px; margin-bottom:6px;">Min Claim Amount ($)</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    f1,f2,f3 = st.columns(3)
    with f1:
        sel_cat  = st.selectbox("Category",["All"]+sorted(df["claim_category"].unique().tolist()), label_visibility="collapsed")
    with f2:
        sel_prov = st.selectbox("Provider",["All"]+sorted(df["provider"].unique().tolist()), label_visibility="collapsed")
    with f3:
        min_amt  = st.number_input("Min Claim Amount ($)",value=0,step=100, label_visibility="collapsed")

    filt = df.copy()
    if sel_cat  != "All": filt = filt[filt["claim_category"]==sel_cat]
    if sel_prov != "All": filt = filt[filt["provider"]==sel_prov]
    filt = filt[filt["claim_amount"]>=min_amt]

    st.caption(f"Showing {min(100,len(filt)):,} of {len(filt):,} matching records")

    raw = filt.head(100).copy()
    raw["claim_date"] = pd.to_datetime(raw["claim_date"]).dt.strftime("%Y-%m-%d")
    raw["claim_amount"] = raw["claim_amount"].apply(lambda x: f"${x:,.0f}")
    # Drop redundant columns
    raw = raw[["claim_id","claim_date","provider","claim_category","claim_amount"]]
    raw.columns = ["Claim ID","Date","Provider","Category","Amount"]
    st.markdown(html_table(raw), unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ft">
  ClaimsPulse &nbsp;·&nbsp; Synthetic data via Synthea &nbsp;·&nbsp;
  AI powered by Qwen via Ollama &nbsp;·&nbsp; Built with Streamlit & Python
</div>
""", unsafe_allow_html=True)
