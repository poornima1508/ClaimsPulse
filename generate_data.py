import pandas as pd
import os

def load_and_transform():
    # Load Synthea files
    encounters = pd.read_csv("output/csv/encounters.csv")
    providers  = pd.read_csv("output/csv/providers.csv")

    # Merge provider names into encounters
    encounters = encounters.merge(
        providers[["Id", "NAME"]],
        left_on="PROVIDER",
        right_on="Id",
        how="left"
    )

    # Map encounter type to claim category
    category_map = {
        "emergency"    : "Emergency",
        "inpatient"    : "Surgery",
        "ambulatory"   : "Outpatient",
        "outpatient"   : "Outpatient",
        "wellness"     : "Preventive Care",
        "urgentcare"   : "Emergency",
        "virtual"      : "Mental Health",
        "home"         : "Mental Health",
        "snf"          : "Outpatient",
    }

    encounters["claim_category"] = (
        encounters["ENCOUNTERCLASS"]
        .str.lower()
        .map(category_map)
        .fillna("Outpatient")
    )

    # Build final claims dataset
    claims = pd.DataFrame({
        "claim_id"       : ["CLM-" + str(i+1).zfill(4)
                            for i in range(len(encounters))],
        "claim_date"     : pd.to_datetime(
                            encounters["START"]).dt.strftime("%Y-%m-%d"),
        "provider"       : encounters["NAME"].fillna("Unknown Provider"),
        "claim_category" : encounters["claim_category"],
        "claim_amount"   : encounters["TOTAL_CLAIM_COST"].round(2)
    })

    # Remove rows with missing amounts
    claims = claims.dropna(subset=["claim_amount"]).reset_index(drop=True)

    # Save to data folder
    os.makedirs("data", exist_ok=True)
    claims.to_csv("data/claims.csv", index=False)

    print(f"✅ Claims dataset created: {len(claims)} records")
    print(f"\nSample:\n{claims.head()}")
    print(f"\nCategories:\n{claims['claim_category'].value_counts()}")
    print(f"\nTotal Cost: ${claims['claim_amount'].sum():,.2f}")

    return claims

if __name__ == "__main__":
    load_and_transform()