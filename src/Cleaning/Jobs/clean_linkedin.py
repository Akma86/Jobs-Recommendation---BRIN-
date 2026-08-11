"""
Cleaning script - LinkedIn jobs dataset
Input : dataset_linkedin-jobs-scraper_*.json
Output: linkedin_clean.csv
"""
import json
import re
import pandas as pd

INPUT_PATH = "/mnt/user-data/uploads/dataset_linkedin-jobs-scraper_2026-07-05_08-42-26-705.json"
OUTPUT_PATH = "/mnt/user-data/outputs/linkedin_clean.csv"

# Kolom kosong 100% atau tidak berguna untuk analisis
DROP_COLS = [
    "benefits", "applyUrl", "companyLogo", "trackingId", "refId",
    "inputUrl", "descriptionHtml",  # descriptionText sudah cukup, html redundant
]

SALARY_RE = re.compile(
    r"\$?([\d,]+(?:\.\d+)?)\s*/?\s*(yr|hr|hour|year)?\s*-\s*\$?([\d,]+(?:\.\d+)?)\s*/?\s*(yr|hr|hour|year)?",
    re.IGNORECASE,
)


def parse_salary(s):
    empty = pd.Series({"salary_min": None, "salary_max": None, "salary_period": None})
    if not s or not isinstance(s, str):
        return empty
    m = SALARY_RE.search(s)
    if not m:
        return empty
    mn = float(m.group(1).replace(",", ""))
    mx = float(m.group(3).replace(",", ""))
    period_raw = (m.group(2) or m.group(4) or "").lower()
    period = "yearly" if period_raw in ("yr", "year") else ("hourly" if period_raw in ("hr", "hour") else None)
    if mn > mx:
        mn, mx = mx, mn
    return pd.Series({"salary_min": mn, "salary_max": mx, "salary_period": period})


def flatten_address(addr):
    empty = pd.Series({"company_city": None, "company_region": None, "company_country": None})
    if not isinstance(addr, dict):
        return empty
    return pd.Series({
        "company_city": addr.get("addressLocality"),
        "company_region": addr.get("addressRegion"),
        "company_country": addr.get("addressCountry"),
    })


def clean_text(t):
    if not t or not isinstance(t, str):
        return None
    t = re.sub(r"&amp;", "&", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t or None


def main():
    with open(INPUT_PATH) as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df = df.drop(columns=[c for c in DROP_COLS if c in df.columns])

    df = pd.concat([df, df.pop("salary").apply(parse_salary)], axis=1)
    df = pd.concat([df, df.pop("companyAddress").apply(flatten_address)], axis=1)

    df["descriptionText"] = df["descriptionText"].apply(clean_text)
    df["postedAt"] = pd.to_datetime(df["postedAt"], errors="coerce").dt.date
    df["applicantsCount"] = pd.to_numeric(df["applicantsCount"], errors="coerce")

    # industries/jobFunction bisa multi-value dipisah koma, biarkan sbg string (sudah rapi)
    df = df.replace(r"^\s*$", pd.NA, regex=True)

    before = len(df)
    df = df.drop_duplicates(subset="id", keep="first")
    print(f"Dedup id: {before} -> {len(df)} rows")

    front_cols = ["id", "title", "companyName", "location", "company_city",
                  "company_country", "salary_min", "salary_max", "salary_period",
                  "seniorityLevel", "employmentType", "postedAt"]
    other_cols = [c for c in df.columns if c not in front_cols]
    df = df[front_cols + other_cols]

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} rows -> {OUTPUT_PATH}")
    print(df.isna().sum().sort_values(ascending=False).head(15))


if __name__ == "__main__":
    main()
