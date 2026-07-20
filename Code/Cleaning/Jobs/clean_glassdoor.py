"""
Cleaning script - Glassdoor jobs dataset
Input : dataset_glassdoor-jobs-scraper_*.json
Output: glassdoor_clean.csv
"""
import json
import re
import pandas as pd
from bs4 import BeautifulSoup

INPUT_PATH = "/mnt/user-data/uploads/dataset_glassdoor-jobs-scraper_2026-07-06_00-29-17-947.json"
OUTPUT_PATH = "/mnt/user-data/outputs/glassdoor_clean.csv"

# Kolom yang isinya null/kosong 100% di seluruh dataset -> buang
DROP_COLS_ALL_NULL = [
    "job_remote", "job_candidate_numbers", "job_levels",
    "job_shifts_and_schedule_tags", "job_language",
    "job_poster_first_name", "job_poster_last_name",
    "job_poster_linkedin_profile_url", "company_uri_providers",
    "company_size", "company_description", "company_tag_line",
    "company_linkedin_follower_count", "company_industries",
    "company_locations",
]
# Kolom raw/redundant yang tidak perlu dibawa ke output bersih
DROP_COLS_RAW = ["all", "job_description_html", "company_logo"]


def clean_html_text(text):
    if not text:
        return None
    soup = BeautifulSoup(text, "html.parser")
    text = soup.get_text(separator=" ")
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def flatten_location(loc):
    if not isinstance(loc, dict):
        return pd.Series({"location_raw": None, "location_city": None,
                           "location_country": None, "location_zip": None})
    return pd.Series({
        "location_raw": loc.get("unknown"),
        "location_city": (loc.get("city") or "").title() or None,
        "location_country": (loc.get("country") or "").title() or None,
        "location_zip": loc.get("zip"),
    })


def flatten_salary(sal):
    empty = pd.Series({"salary_min": None, "salary_max": None,
                        "salary_currency": None, "salary_period": None,
                        "salary_estimated": None})
    if not isinstance(sal, dict):
        return empty
    mn, mx = sal.get("min"), sal.get("max")
    # Fix data quality bug: banyak record punya min > max (harusnya kebalik)
    if mn is not None and mx is not None and mn > mx:
        mn, mx = mx, mn
    return pd.Series({
        "salary_min": mn,
        "salary_max": mx,
        "salary_currency": sal.get("currency"),
        "salary_period": sal.get("pay_period"),
        "salary_estimated": sal.get("estimated"),
    })


def main():
    with open(INPUT_PATH) as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    # Buang kolom yang tidak berguna
    df = df.drop(columns=[c for c in DROP_COLS_ALL_NULL + DROP_COLS_RAW if c in df.columns])

    # Flatten nested fields
    df = pd.concat([df, df.pop("job_location").apply(flatten_location)], axis=1)
    df = pd.concat([df, df.pop("job_salary").apply(flatten_salary)], axis=1)

    # Bersihkan teks deskripsi
    df["job_description"] = df["job_description"].apply(clean_html_text)

    # job_job_types kadang list -> gabung jadi string
    df["job_job_types"] = df["job_job_types"].apply(
        lambda x: ", ".join(x) if isinstance(x, list) and x else None
    )

    # Normalisasi tanggal
    df["job_posted_date"] = pd.to_datetime(df["job_posted_date"], errors="coerce").dt.date

    # String kosong -> NaN biar konsisten
    df = df.replace(r"^\s*$", pd.NA, regex=True)

    # Dedup berdasarkan job_id, simpan yang pertama
    before = len(df)
    df = df.drop_duplicates(subset="job_id", keep="first")
    print(f"Dedup job_id: {before} -> {len(df)} rows")

    # Reset index & urutkan kolom penting di depan
    front_cols = ["job_id", "job_title", "job_normalized_title", "company_name",
                  "location_city", "location_country", "salary_min", "salary_max",
                  "salary_currency", "salary_period", "job_posted_date"]
    other_cols = [c for c in df.columns if c not in front_cols]
    df = df[front_cols + other_cols]

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} rows -> {OUTPUT_PATH}")
    print(df.isna().sum().sort_values(ascending=False).head(15))


if __name__ == "__main__":
    main()
