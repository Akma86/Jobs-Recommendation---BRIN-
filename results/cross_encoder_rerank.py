# -*- coding: utf-8 -*-
"""
Cross-Encoder re-ranking on top of SBERT retrieval results. (GPU-FORCED VERSION)

WHY THIS STEP EXISTS:
SBERT (bi-encoder) embeds course profile and job posting SEPARATELY, then
compares vectors. That's fast (good for retrieval over thousands of jobs)
but loses fine-grained interaction between the two texts - which is why we
saw compressed, less discriminative similarity scores (0.78-0.84 range) and
a generic job posting acting as a "hub" matching everything.

A cross-encoder instead feeds the (course_text, job_text) PAIR through the
model TOGETHER in one forward pass, with full cross-attention between them.
This is much more accurate at judging "does this pair actually match" - but
also much slower, since you can't pre-compute embeddings and reuse them
(every pair needs its own forward pass). That's why the standard pattern
(used in the CareerBERT / job-recommendation papers Akmal cited) is:

    SBERT retrieval (fast, top-K candidates)  ->  Cross-Encoder re-rank (slow, accurate, only on top-K)

MODEL: cross-encoder/mmarco-mMiniLMv2-L12-H384-v1
  - Multilingual cross-encoder trained on mMARCO (MS MARCO passage ranking
    translated into 14 languages, INCLUDING Indonesian). Handles the
    Indonesian CLO <-> English job description pairing better than an
    English-only cross-encoder would.
  - Lightweight (~110M params), fast enough to re-rank a few hundred pairs
    even on modest hardware - and now forced onto GPU for speed.

GPU:
  This version FORCES CUDA usage. If no CUDA-capable GPU/driver is detected,
  the script raises an error immediately instead of silently falling back
  to CPU (so you always know for sure which device it ran on).

REQUIREMENTS (run on your machine - needs internet to huggingface.co):
  pip install sentence-transformers pandas --break-system-packages
  # Make sure torch is the CUDA build, e.g.:
  pip install torch --index-url https://download.pytorch.org/whl/cu124 --break-system-packages

INPUT FILES (same folder):
  - course_job_matches.csv  (output of semantic_matching.py: SBERT top-K per course)
  - course_profiles.csv
  - jobs_unified.csv

OUTPUT:
  - course_job_matches_reranked.csv
    (adds `cross_encoder_score` and `rerank` columns; rows sorted by
    course_name then rerank so you can immediately see the new top-K order)

JOIN KEY NOTE:
  This version joins course_job_matches.csv <-> course_profiles.csv on
  `course_name` instead of `course_code`, because the two files use
  different course_code schemes (course_profiles.csv here has plain
  integer codes 0,1,2,... while course_job_matches.csv uses the original
  string codes like "BBK1AAB4"). If your course_profiles.csv has duplicate
  course_name values, only the first matching row is used - check the
  [WARNING] duplicate output if that matters for your data.
"""

import pandas as pd
import torch
from sentence_transformers import CrossEncoder

MODEL_NAME = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
MAX_TEXT_CHARS = 1500  # truncate each side of the pair to keep inference fast
BATCH_SIZE = 64        # RTX 3050 (4GB) handles this easily for a ~110M param model


def truncate(text, max_chars=MAX_TEXT_CHARS):
    if not isinstance(text, str):
        return ""
    return text[:max_chars]


def get_gpu_device():
    """Force CUDA. Raise loudly instead of silently falling back to CPU."""
    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA GPU tidak terdeteksi oleh PyTorch!\n"
            "Cek:\n"
            "  1. Jalankan `nvidia-smi` di terminal - pastikan GPU & driver muncul.\n"
            "  2. Pastikan torch yang terinstall adalah build CUDA, bukan CPU-only:\n"
            "     pip uninstall torch torchvision torchaudio -y\n"
            "     pip install torch --index-url https://download.pytorch.org/whl/cu124 --break-system-packages\n"
            "  3. Cek dengan: python -c \"import torch; print(torch.__version__, torch.cuda.is_available())\""
        )
    device = "cuda"
    print(f"GPU terdeteksi: {torch.cuda.get_device_name(0)}")
    print(f"CUDA version (torch build): {torch.version.cuda}")
    return device


def main():
    device = get_gpu_device()

    print(f"\nLoading cross-encoder: {MODEL_NAME} ke {device} ...")
    model = CrossEncoder(MODEL_NAME, device=device)

    matches = pd.read_csv("course_job_matches.csv")
    # NOTE: joining on course_name instead of course_code, because
    # course_code in course_profiles.csv (plain integers 0,1,2,...) does NOT
    # match the course_code scheme used in course_job_matches.csv (e.g.
    # "BBK1AAB4"). course_name is the field that's consistent across both
    # files, so we use that as the join key instead.
    courses = pd.read_csv("course_profiles.csv").set_index("course_name")
    jobs = pd.read_csv("jobs_unified.csv").set_index("job_id")

    # --- sanity check: make sure every course_name / job_id in matches
    # actually exists in course_profiles.csv / jobs_unified.csv before we
    # start building pairs. Mismatched IDs (typo, missing row, extra
    # whitespace, casing) are dropped instead of crashing mid-run.
    courses.index = courses.index.astype(str).str.strip()
    jobs.index = jobs.index.astype(str).str.strip()
    matches["course_name"] = matches["course_name"].astype(str).str.strip()
    matches["job_id"] = matches["job_id"].astype(str).str.strip()

    # if course_profiles.csv has duplicate course_name rows, keep the first
    # one so .loc lookups don't break
    if courses.index.duplicated().any():
        dupes = sorted(set(courses.index[courses.index.duplicated()]))
        print(f"[WARNING] {len(dupes)} course_name duplikat di course_profiles.csv, ambil baris pertama: {dupes}")
        courses = courses[~courses.index.duplicated(keep="first")]

    missing_courses = sorted(set(matches["course_name"]) - set(courses.index))
    missing_jobs = sorted(set(matches["job_id"]) - set(jobs.index))

    if missing_courses:
        print(f"\n[WARNING] {len(missing_courses)} course_name di matches tapi TIDAK ada di course_profiles.csv:")
        print(f"  {missing_courses}")
    if missing_jobs:
        print(f"\n[WARNING] {len(missing_jobs)} job_id di matches tapi TIDAK ada di jobs_unified.csv:")
        print(f"  {missing_jobs}")

    before = len(matches)
    matches = matches[
        ~matches["course_name"].isin(missing_courses) & ~matches["job_id"].isin(missing_jobs)
    ].reset_index(drop=True)
    dropped = before - len(matches)
    if dropped:
        print(f"\n[INFO] {dropped}/{before} baris di-skip karena ID tidak cocok. Sisa: {len(matches)} baris.\n")

    print(f"Re-ranking {len(matches)} (course, job) pairs...")

    pairs = []
    for _, row in matches.iterrows():
        course_text = truncate(courses.loc[row["course_name"], "clo_combined_text"])
        job_row = jobs.loc[row["job_id"]]
        job_text = truncate(str(job_row["title"]) + ". " + str(job_row["description"]))
        pairs.append((course_text, job_text))

    scores = model.predict(pairs, show_progress_bar=True, batch_size=BATCH_SIZE)
    matches["cross_encoder_score"] = scores

    # re-rank within each course by the new cross-encoder score
    matches["rerank"] = (
        matches.groupby("course_name")["cross_encoder_score"]
        .rank(method="first", ascending=False)
        .astype(int)
    )

    matches = matches.sort_values(["course_name", "rerank"])
    matches.to_csv("course_job_matches_reranked.csv", index=False)
    print("Saved: course_job_matches_reranked.csv")

    # sanity check: how much did the ranking actually change vs SBERT-only order?
    changed = (matches["rank"] != matches["rerank"]).sum()
    print(f"\nRows where cross-encoder changed the SBERT rank: {changed}/{len(matches)}")

    print("\n--- Sample: first course, old rank vs new rerank ---")
    first_course = matches["course_name"].iloc[0]
    sample = matches[matches["course_name"] == first_course][
        ["course_name", "job_title", "similarity", "rank", "cross_encoder_score", "rerank"]
    ].sort_values("rerank")
    print(sample.to_string(index=False))

    print(f"\nSelesai. Device yang dipakai: {device} ({torch.cuda.get_device_name(0)})")


if __name__ == "__main__":
    main()