# -*- coding: utf-8 -*-
"""
Semantic matching: Course competency profile (from CLO/RPS) <-> Job postings.

APPROACH: no dictionary/skill-alias mapping needed. We embed the course's
combined CLO text and each job posting's description into the same vector
space using a multilingual sentence embedding model, then rank jobs by
cosine similarity. This directly captures semantic relatedness even when
the exact words differ (and even across Indonesian <-> English, since the
model is multilingual).

MODEL: intfloat/multilingual-e5-large
  - Strong multilingual semantic retrieval performance (covers Indonesian
    and English in the same space).
  - Designed for asymmetric retrieval: short "query" text matched against
    longer "passage" text - which fits our case well (CLO course profile
    is the query, job description is the passage).
  - ~560M params - very manageable on a consumer GPU (few GB VRAM).
  - If your GPU is small/slow, swap to "intfloat/multilingual-e5-base"
    (moderate quality drop, much faster) or
    "intfloat/multilingual-e5-small" (fastest, still cross-lingual capable).

REQUIREMENTS (run on your machine - needs GPU + internet to huggingface.co,
neither of which the Claude sandbox has):
  pip install sentence-transformers pandas torch --break-system-packages
  (torch will auto-detect your GPU if CUDA is installed)

INPUT FILES (already prepared for you, place in the same folder):
  - course_profiles.csv   (21 rows: one combined CLO text per course)
  - jobs_unified.csv      (2,102 rows: linkedin + glassdoor postings)

OUTPUT:
  - course_job_matches.csv : top-K matching jobs per course, with similarity score
"""

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "intfloat/multilingual-e5-large"
TOP_K = 10  # top matching jobs per course

# E5 models expect these literal prefixes on the text - this is part of how
# the model was trained, not optional formatting.
QUERY_PREFIX = "query: "
PASSAGE_PREFIX = "passage: "


def truncate(text, max_chars=2000):
    """Job descriptions can be very long; truncate to keep embedding fast
    and avoid diluting the signal with boilerplate (benefits, legal text, etc.)
    that tends to appear at the end of postings."""
    if not isinstance(text, str):
        return ""
    return text[:max_chars]


def main():
    print(f"Loading model: {MODEL_NAME} ...")
    model = SentenceTransformer(MODEL_NAME)
    # Uses GPU automatically if available (model.device will show cuda if so)
    print(f"Running on device: {model.device}")

    courses = pd.read_csv("course_profiles.csv")
    jobs = pd.read_csv("jobs_unified.csv")
    print(f"Courses: {len(courses)} | Jobs: {len(jobs)}")

    # Build query texts: combine CLO text with skill labels for extra signal
    course_texts = (
        courses["clo_combined_text"].fillna("") + " "
        + courses["skill_technical_list"].fillna("").str.replace(";", ",")
    ).apply(lambda t: QUERY_PREFIX + t)

    # Build passage texts: title + description (title carries strong signal)
    job_texts = (
        jobs["title"].fillna("") + ". " + jobs["description"].fillna("").apply(truncate)
    ).apply(lambda t: PASSAGE_PREFIX + t)

    print("Embedding course profiles...")
    course_emb = model.encode(
        course_texts.tolist(), normalize_embeddings=True, show_progress_bar=True, batch_size=8
    )

    print("Embedding job postings (this is the slow part, ~2k rows)...")
    job_emb = model.encode(
        job_texts.tolist(), normalize_embeddings=True, show_progress_bar=True, batch_size=32
    )

    # cosine similarity (embeddings are normalized, so dot product = cosine sim)
    sim_matrix = course_emb @ job_emb.T  # shape: (n_courses, n_jobs)

    results = []
    for i, course_row in courses.iterrows():
        sims = sim_matrix[i]
        top_idx = np.argsort(-sims)[:TOP_K]
        for rank, j in enumerate(top_idx, start=1       ):
            results.append({
                "course_code": course_row["course_code"],
                "course_name": course_row["course_name"],
                "rank": rank,
                "similarity": round(float(sims[j]), 4),
                "job_id": jobs.iloc[j]["job_id"],
                "job_title": jobs.iloc[j]["title"],
                "job_company": jobs.iloc[j]["company"],
                "job_source": jobs.iloc[j]["source"],
            })

    out = pd.DataFrame(results)
    out.to_csv("course_job_matches.csv", index=False)
    print(f"\nSaved: course_job_matches.csv ({len(out)} rows)")

    # quick sanity print
    print("\n--- Sample: top 3 matches for first course ---")
    sample = out[out["course_code"] == courses.iloc[0]["course_code"]].head(3)
    print(sample[["course_name", "job_title", "similarity"]].to_string(index=False))


if __name__ == "__main__":
    main()
