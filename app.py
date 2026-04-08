import streamlit as st
import pandas as pd
import sys
sys.path.append("modules")
from generate_data import load_and_transform
from analysis import run_analysis
from summary import generate_summary

# ── PAGE CONFIG ───────────────────────────────────────────────────
st.set_page_config(
    page_title="ClaimsPulse",
    page_icon="🏥",
    layout="wide"
)

# ── CUSTOM CSS ────────────────────────────────────────────────────
st.markdown("""
    <style>
        .main { background-color: #f8f9fa; }
        .block-container { padding-top: 2rem; }
        h1 { color: #1a1a2e; font-family: Arial, sans-serif; }
        h3 { color: #2c7be5; font-family: Arial, sans-serif; }

        .kpi-card {
            background-color: white;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border-top: 4px solid #2c7be5;
        }
        .kpi-value {
            font-size: 28px;
            font-weight: bold;
            color: #1a1a2e;
            font-family: Arial, sans-serif;
        }
        .kpi-label {
            font-size: 13px;
            color: #6c757d;
            margin-top: 5px;
            font-family: Arial, sans-serif;
        }
        .section-card {
            background-color: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin-bottom: 20px;
        }
        .summary-box {
            background-color: #f0f6ff;
            padding: 25px;
            border-radius: 12px;
            border-left: 6px solid #2c7be5;
            font-size: 16px;
            font-family: Arial, sans-serif;
            color: #1a1a2e;
            line-height: 1.9;
        }
        .anomaly-box {
            background-color: #fff5f5;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #e63946;
            font-family: Arial, sans-serif;
            color: #1a1a2e;
            font-size: 15px;
        }
        footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────
st.markdown("""
    <div style='text-align: center; padding: 10px 0 20px 0;'>
        <h1 style='font-size: 42px;'>🏥 ClaimsPulse</h1>
        <p style='color: #6c757d; font-size: 18px; font-family: Arial;'>
            AI-Powered Executive Decision Support for Insurance Claims
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── LOAD DATA ─────────────────────────────────────────────────────
@st.cache_data
def get_data():
    df = pd.read_csv("data/claims.csv")
    return df

df = get_data()
results = run_analysis(df)

# ── KPI CARDS ─────────────────────────────────────────────────────
st.markdown("### 📌 Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

kpis = [
    ("Total Claims",       f"{results['total_claims']:,}"),
    ("Total Cost",         f"${results['total_cost']/1_000_000:.1f}M"),
    ("Average Cost",       f"${results['average_cost']:,.0f}"),
    ("Highest Claim",      f"${results['highest_claim']:,.0f}"),
    ("Anomalous Months",   f"{len(results['anomalies'])}"),
]

for col, (label, value) in zip([col1,col2,col3,col4,col5], kpis):
    col.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-value'>{value}</div>
            <div class='kpi-label'>{label}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

# ── ROW 1: CATEGORY + PROVIDER ────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💰 Cost by Category")
    cat_df = results["cost_by_category"].reset_index()
    st.bar_chart(cat_df.set_index("claim_category")["total_cost"])
    st.dataframe(cat_df, use_container_width=True)

with col2:
    st.markdown("### 🏥 Top 10 Providers by Cost")
    prov_df = results["cost_by_provider"].reset_index()
    st.bar_chart(prov_df.set_index("provider")["total_cost"])
    st.dataframe(prov_df, use_container_width=True)

st.markdown("---")

# ── MONTHLY TREND ─────────────────────────────────────────────────
st.markdown("### 📈 Monthly Cost Trend")
monthly = results["monthly_trend"].copy()
monthly["month"] = monthly["month"].astype(str)
st.line_chart(monthly.set_index("month")["total_cost"])

st.markdown("---")

# ── YEARLY TREND ──────────────────────────────────────────────────
st.markdown("### 📅 Yearly Cost Trend")
yearly = results["yearly_trend"].copy()
yearly = yearly[yearly["year"] >= 2010]
st.line_chart(yearly.set_index("year")["total_cost"])

st.markdown("---")

# ── ANOMALIES ─────────────────────────────────────────────────────
st.markdown("### 🚨 Anomalous Months")
if len(results["anomalies"]) == 0:
    st.success("✅ No anomalies detected!")
else:
    anomalies = results["anomalies"].copy()
    anomalies["month"] = anomalies["month"].astype(str)
    st.markdown(f"""
        <div class='anomaly-box'>
            ⚠️ <b>{len(anomalies)} months</b> were detected with abnormally 
            high costs compared to the overall average.
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(anomalies, use_container_width=True)

st.markdown("---")

# ── RAW DATA ──────────────────────────────────────────────────────
with st.expander("📂 View Raw Claims Data"):
    st.dataframe(df.head(100), use_container_width=True)

st.markdown("---")

# ── AI SUMMARY ────────────────────────────────────────────────────
st.markdown("### 🤖 AI Executive Summary")
with st.spinner("Generating AI summary, please wait..."):
    summary = generate_summary(results)

summary = summary.replace("`", "").strip()
st.markdown(f"""
    <div class='summary-box'>
        {summary}
    </div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.caption("ClaimsPulse | Synthetic data generated using Synthea | Powered by Qwen via Ollama")