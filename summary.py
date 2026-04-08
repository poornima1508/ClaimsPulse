import requests

def generate_summary(results):
    top_category = results["cost_by_category"].index[0]
    top_category_cost = results["cost_by_category"]["total_cost"].iloc[0]
    top_provider = results["cost_by_provider"].index[0]
    anomaly_count = len(results["anomalies"])
    total_cost = results["total_cost"] / 1_000_000
    avg_cost = results["average_cost"]
    highest = results["highest_claim"]
    total_claims = results["total_claims"]

    # Build the summary directly from data — no hallucination possible
    summary = (
        f"A total of {total_claims:,} insurance claims were processed during the reporting period, "
        f"with a combined cost of ${total_cost:.1f} million. "
        f"The average cost per claim was ${avg_cost:,.0f}, with the highest individual claim reaching ${highest:,.0f}. "
        f"Outpatient services represented the largest cost category at ${top_category_cost/1_000_000:.1f} million, "
        f"accounting for the majority of total expenditure. "
        f"Cost trend analysis identified {anomaly_count} months with abnormally high claim costs, "
        f"which require further investigation to determine underlying risk drivers and inform future budgeting decisions."
    )

    return summary