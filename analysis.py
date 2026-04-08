import pandas as pd
import numpy as np

def run_analysis(df):
    results = {}

    # ── 1. BASIC SUMMARY ──────────────────────────────────────────
    results["total_claims"]    = len(df)
    results["total_cost"]      = round(df["claim_amount"].sum(), 2)
    results["average_cost"]    = round(df["claim_amount"].mean(), 2)
    results["highest_claim"]   = round(df["claim_amount"].max(), 2)
    results["lowest_claim"]    = round(df["claim_amount"].min(), 2)

    # ── 2. COST BY CATEGORY ───────────────────────────────────────
    results["cost_by_category"] = (
        df.groupby("claim_category")["claim_amount"]
        .agg(total_cost="sum", avg_cost="mean", count="count")
        .round(2)
        .sort_values("total_cost", ascending=False)
    )

    # ── 3. COST BY PROVIDER ───────────────────────────────────────
    results["cost_by_provider"] = (
        df.groupby("provider")["claim_amount"]
        .agg(total_cost="sum", avg_cost="mean", count="count")
        .round(2)
        .sort_values("total_cost", ascending=False)
        .head(10)
    )

    # ── 4. MONTHLY COST TREND ─────────────────────────────────────
    df["claim_date"] = pd.to_datetime(df["claim_date"])
    df["year_month"] = df["claim_date"].dt.to_period("M")

    results["monthly_trend"] = (
        df.groupby("year_month")["claim_amount"]
        .sum()
        .round(2)
        .reset_index()
    )
    results["monthly_trend"].columns = ["month", "total_cost"]

    # ── 5. ANOMALY DETECTION ──────────────────────────────────────
    monthly = results["monthly_trend"].copy()
    monthly["mean"]  = monthly["total_cost"].mean()
    monthly["std"]   = monthly["total_cost"].std()
    monthly["upper"] = monthly["mean"] + (2 * monthly["std"])

    results["anomalies"] = monthly[
        monthly["total_cost"] > monthly["upper"]
    ][["month", "total_cost"]].reset_index(drop=True)

    # ── 6. YEARLY SUMMARY ─────────────────────────────────────────
    df["year"] = df["claim_date"].dt.year
    results["yearly_trend"] = (
        df.groupby("year")["claim_amount"]
        .agg(total_cost="sum", claim_count="count")
        .round(2)
        .reset_index()
    )

    return results


if __name__ == "__main__":
    df = pd.read_csv("data/claims.csv")
    results = run_analysis(df)

    print("=" * 50)
    print("📊 CLAIMSPULSE ANALYSIS REPORT")
    print("=" * 50)

    print(f"\n📌 Total Claims    : {results['total_claims']:,}")
    print(f"💰 Total Cost      : ${results['total_cost']:,.2f}")
    print(f"📈 Average Cost    : ${results['average_cost']:,.2f}")
    print(f"🔺 Highest Claim   : ${results['highest_claim']:,.2f}")
    print(f"🔻 Lowest Claim    : ${results['lowest_claim']:,.2f}")

    print("\n── Cost by Category ──")
    print(results["cost_by_category"])

    print("\n── Top 10 Providers by Cost ──")
    print(results["cost_by_provider"])

    print("\n── Anomalous Months (unusually high costs) ──")
    if len(results["anomalies"]) == 0:
        print("No anomalies detected.")
    else:
        print(results["anomalies"])

    print("\n── Yearly Trend ──")
    print(results["yearly_trend"])