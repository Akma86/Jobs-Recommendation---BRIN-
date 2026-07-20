"""
Cleaning script - RemoteOK jobs dataset
Input : remoteok_jobs.json
Output: remoteok_clean.csv
"""
import json
import re
import pandas as pd
import ftfy
from bs4 import BeautifulSoup

INPUT_PATH = "/mnt/user-data/uploads/remoteok_jobs.json"
OUTPUT_PATH = "/mnt/user-data/outputs/remoteok_clean.csv"

# Boilerplate anti-spam RemoteOK yang sering nempel di akhir description
SPAM_PATTERN = re.compile(
    r"Please mention the word.*$", re.IGNORECASE | re.DOTALL
)


def fix_and_clean_text(html_text):
    if not html_text or not isinstance(html_text, str):
        return None
    # Perbaiki mojibake (double-encoded UTF-8, misal teks Arab jadi karakter aneh)
    text = ftfy.fix_text(html_text)
    # Buang HTML tags
    soup = BeautifulSoup(text, "html.parser")
    text = soup.get_text(separator=" ")
    # Buang boilerplate spam RemoteOK
    text = SPAM_PATTERN.sub("", text)
    # Rapikan whitespace
    text = re.sub(r"\xa0", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def fix_location(loc):
    if not loc or not isinstance(loc, str) or not loc.strip():
        return "Remote / Not specified"
    return ftfy.fix_text(loc).strip()


def clean_skills(skills):
    if not skills or not isinstance(skills, str):
        return None
    parts = [s.strip() for s in skills.split(",") if s.strip()]
    return ", ".join(sorted(set(parts), key=parts.index)) or None


def main():
    with open(INPUT_PATH) as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    df["description"] = df["description"].apply(fix_and_clean_text)
    df["location"] = df["location"].apply(fix_location)
    df["skills"] = df["skills"].apply(clean_skills)
    df["name"] = df["name"].apply(lambda x: ftfy.fix_text(x).strip() if isinstance(x, str) else x)
    df["company"] = df["company"].apply(lambda x: ftfy.fix_text(x).strip() if isinstance(x, str) else x)

    before = len(df)
    df = df.drop_duplicates(subset="id", keep="first")
    print(f"Dedup id: {before} -> {len(df)} rows")

    front_cols = ["id", "name", "company", "location", "skills"]
    other_cols = [c for c in df.columns if c not in front_cols]
    df = df[front_cols + other_cols]

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} rows -> {OUTPUT_PATH}")
    print(df.isna().sum().sort_values(ascending=False))


if __name__ == "__main__":
    main()
