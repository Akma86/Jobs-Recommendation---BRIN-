# -*- coding: utf-8 -*-
"""
High-performance script to clean and merge additional raw LinkedIn job postings
(Sistem Informasi & Jaringan) into data/Pekerjaan/Processed/jobs_unified.csv.
"""

import os
import sys
import re
import glob
import json
import time
import pandas as pd

ROOT_DIR = r"D:\MAIN DATA\Documents\Semester 6\KP BRIN"
RAW_TAMBAHAN_DIR = os.path.join(ROOT_DIR, "data", "Pekerjaan", "Raw tambahan Sistem Informasi & Jaringan")
CLEAN_DIR = os.path.join(ROOT_DIR, "data", "Pekerjaan", "Clean")
PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "Pekerjaan", "Processed")
JOBS_UNIFIED_PATH = os.path.join(PROCESSED_DIR, "jobs_unified.csv")
BACKUP_PATH = os.path.join(PROCESSED_DIR, "jobs_unified_backup_2102.csv")
OUTPUT_CLEAN_TAMBAHAN = os.path.join(CLEAN_DIR, "linkedin_tambahan_clean.csv")

NER_DIR = os.path.join(ROOT_DIR, "src", "kpbrin", "data", "cleaning", "NERExtrcted")
if NER_DIR not in sys.path:
    sys.path.insert(0, NER_DIR)

from skill_vocabulary import SKILL_VOCAB, build_alias_index


def clean_text(t):
    """Clean text by fixing HTML entities, stripping extra spaces and control chars."""
    if not t or not isinstance(t, str):
        return ""
    t = re.sub(r"&amp;", "&", t)
    t = re.sub(r"&lt;", "<", t)
    t = re.sub(r"&gt;", ">", t)
    t = re.sub(r"&quot;", '"', t)
    t = re.sub(r"&#39;", "'", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def build_fast_skill_matcher():
    """Build single combined regex pattern for high throughput."""
    alias_map = build_alias_index()
    sorted_aliases = sorted(alias_map.keys(), key=len, reverse=True)
    # Ensure word boundaries: (?<!\w)(alias1|alias2|...)(?!\w)
    pattern = re.compile(
        r"(?<!\w)(" + "|".join(re.escape(k) for k in sorted_aliases) + r")(?!\w)",
        re.IGNORECASE,
    )
    return pattern, alias_map


def main():
    start_time = time.time()
    print("=" * 75, flush=True)
    print("1. MEMBACA FILE RAW TAMBAHAN...", flush=True)
    print("=" * 75, flush=True)
    raw_files = glob.glob(os.path.join(RAW_TAMBAHAN_DIR, "*.csv"))
    if not raw_files:
        raise FileNotFoundError(f"Tidak ditemukan file CSV di {RAW_TAMBAHAN_DIR}")

    raw_dfs = []
    for f in sorted(raw_files):
        df_temp = pd.read_csv(f)
        print(f"  [READ] {os.path.basename(f)}: {len(df_temp)} baris, {len(df_temp.columns)} kolom", flush=True)
        raw_dfs.append(df_temp)

    comb_raw = pd.concat(raw_dfs, ignore_index=True)
    print(f"\nTotal baris mentah gabungan: {len(comb_raw)}", flush=True)

    # 2. Cleaning & Deduplication
    print("\n" + "=" * 75, flush=True)
    print("2. PEMBERSIHAN DATA & DEDUPLIKASI...", flush=True)
    print("=" * 75, flush=True)

    comb_raw = comb_raw.dropna(subset=["id"])
    comb_raw["id"] = comb_raw["id"].astype(str).str.strip()

    before_dedup = len(comb_raw)
    comb_raw = comb_raw.drop_duplicates(subset=["id"], keep="first")
    print(f"  Deduplikasi ID internal: {before_dedup} -> {len(comb_raw)} baris ({before_dedup - len(comb_raw)} duplikat dihapus)", flush=True)

    comb_raw["title"] = comb_raw["title"].apply(clean_text)
    comb_raw["company"] = comb_raw["companyName"].apply(clean_text)
    comb_raw["company"] = comb_raw["company"].replace("", "Unknown Company").fillna("Unknown Company")
    comb_raw["description"] = comb_raw["descriptionText"].apply(clean_text)

    valid_mask = (comb_raw["title"].str.len() > 0) & (comb_raw["description"].str.len() > 20)
    valid_df = comb_raw[valid_mask].copy()
    print(f"  Validasi kelengkapan teks: {len(comb_raw)} -> {len(valid_df)} baris valid", flush=True)

    # 3. Ekstraksi Skill
    print("\n" + "=" * 75, flush=True)
    print("3. EKSTRAKSI SKILL (TAXONOMY OBE / RPS)...", flush=True)
    print("=" * 75, flush=True)
    pat, alias_map = build_fast_skill_matcher()
    print(f"  Pola regex skill matcher dikompilasi ({len(alias_map)} alias)", flush=True)

    matched_skills_list = []
    skill_counts = []
    for desc in valid_df["description"]:
        if not desc:
            matched = []
        else:
            raw_hits = pat.findall(desc)
            matched = sorted({alias_map[h.lower()] for h in raw_hits})
        matched_skills_list.append(json.dumps(matched))
        skill_counts.append(len(matched))

    valid_df["matched_skills"] = matched_skills_list
    valid_df["source"] = "linkedin"
    valid_df["job_id"] = "li_" + valid_df["id"]

    print(f"  Rata-rata skill per lowongan: {sum(skill_counts)/len(skill_counts):.2f}", flush=True)
    print(f"  Lowongan dengan >=1 skill: {sum(1 for c in skill_counts if c > 0)} / {len(skill_counts)} ({sum(1 for c in skill_counts if c > 0)/len(skill_counts)*100:.1f}%)", flush=True)

    os.makedirs(CLEAN_DIR, exist_ok=True)
    valid_df.to_csv(OUTPUT_CLEAN_TAMBAHAN, index=False)
    print(f"  [SAVED] Clean tambahan -> {OUTPUT_CLEAN_TAMBAHAN}", flush=True)

    target_cols = ["job_id", "source", "title", "company", "description", "matched_skills"]
    new_unified_df = valid_df[target_cols].copy()

    # 4. Penggabungan dengan dataset existing
    print("\n" + "=" * 75, flush=True)
    print("4. PENGGABUNGAN KE JOBS_UNIFIED.CSV...", flush=True)
    print("=" * 75, flush=True)

    if os.path.exists(JOBS_UNIFIED_PATH):
        existing_df = pd.read_csv(JOBS_UNIFIED_PATH)
        print(f"  Dataset existing: {len(existing_df)} baris", flush=True)

        if not os.path.exists(BACKUP_PATH):
            existing_df.to_csv(BACKUP_PATH, index=False)
            print(f"  [BACKUP] Berhasil membuat backup di {BACKUP_PATH}", flush=True)

        combined_final = pd.concat([existing_df, new_unified_df], ignore_index=True)
        before_final_dedup = len(combined_final)
        combined_final = combined_final.drop_duplicates(subset=["job_id"], keep="first")
        print(f"  Total setelah penggabungan & dedup: {before_final_dedup} -> {len(combined_final)} baris", flush=True)
    else:
        combined_final = new_unified_df
        print(f"  Dataset baru dibuat: {len(combined_final)} baris", flush=True)

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    combined_final.to_csv(JOBS_UNIFIED_PATH, index=False)
    print(f"  [SUCCESS] Berhasil disimpan -> {JOBS_UNIFIED_PATH}", flush=True)

    # 5. Summary & Statistik Akhir
    print("\n" + "=" * 75, flush=True)
    print("5. RINGKASAN DATASET AKHIR:", flush=True)
    print("=" * 75, flush=True)
    print(combined_final.info(), flush=True)
    print("\nDistribusi Source:", flush=True)
    print(combined_final["source"].value_counts(), flush=True)
    print(f"\nEksekusi selesai dalam {time.time() - start_time:.2f} detik.", flush=True)
    print("=" * 75, flush=True)


if __name__ == "__main__":
    main()
