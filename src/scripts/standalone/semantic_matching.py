# -*- coding: utf-8 -*-
"""
Semantic matching: Course competency profile (from CLO/RPS) <-> Job postings.
"""

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "intfloat/multilingual-e5-large"
TOP_K = 10  # top matching jobs per course

QUERY_PREFIX = "query: "
PASSAGE_PREFIX = "passage: "


def truncate(text, max_chars=2000):
    if not isinstance(text, str):
        return ""
    return text[:max_chars]


def main():
    print(f"Loading model: {MODEL_NAME} ...")
    model = SentenceTransformer(MODEL_NAME)
    print(f"Running on device: {model.device}")

    courses = pd.read_csv("course_profiles.csv")
    jobs = pd.read_csv("jobs_unified.csv")
    print(f"Courses: {len(courses)} | Jobs: {len(jobs)}")

    course_texts = (
        courses["clo_combined_text"].fillna("") + " "
        + courses["skill_technical_list"].fillna("").str.replace(";", ",")
    ).apply(lambda t: QUERY_PREFIX + t)

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

    sim_matrix = course_emb @ job_emb.T

    results = []
    for i, course_row in courses.iterrows():
        sims = sim_matrix[i]
        top_idx = np.argsort(-sims)[:TOP_K]
        for rank, j in enumerate(top_idx, start=1):
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

    print("\n--- Sample: top 3 matches for first course ---")
    sample = out[out["course_code"] == courses.iloc[0]["course_code"]].head(3)
    print(sample[["course_name", "job_title", "similarity"]].to_string(index=False))


if __name__ == "__main__":
    main()
