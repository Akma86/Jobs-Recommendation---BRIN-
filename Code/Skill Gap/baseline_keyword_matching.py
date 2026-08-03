# -*- coding: utf-8 -*-
"""
BASELINE: naive TF-IDF keyword matching, for comparison against the
semantic (SBERT + cross-encoder) pipeline.

WHY THIS MATTERS FOR YOUR REPORT: "we used a fancy semantic model" isn't
convincing on its own - you need to show it actually beats the simple
approach. This baseline mimics what a traditional ATS keyword-matcher does
(the exact thing your latar belakang / proposal criticizes): TF-IDF vectors
+ cosine similarity, no understanding of meaning, no synonyms, no context.

If the semantic pipeline's rankings mostly AGREE with this baseline, that's
actually a bit concerning (why pay the extra compute cost for cross-encoder
reranking if a free baseline gives the same answer?). If they DIFFER
meaningfully - especially in cases where the baseline clearly misses
synonyms/context that the semantic model catches - that's your evidence
the added complexity earns its keep.

REQUIREMENTS: pip install scikit-learn pandas --break-system-packages
  (no GPU, no downloads needed - runs instantly, even in a constrained sandbox)

INPUT FILES:
  - sub_clo_profiles.csv
  - jobs_unified_with_skills.csv
  - pipeline_course_match_log.csv   (which courses are "the student's")

OUTPUT:
  - baseline_job_ranking.csv        top jobs per matched course, TF-IDF only
  - baseline_vs_semantic_comparison.csv   (only if final_recommendations_full.csv
                                            exists - overlap/rank-correlation report)
"""

import argparse
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats import spearmanr

TOP_K = 10


def build_baseline_ranking(match_log, subclo_profiles, jobs):
    matched_courses = match_log[match_log["included"]]["matched_course_name"].unique()
    course_texts = {}
    for course in matched_courses:
        subclos = subclo_profiles[subclo_profiles["course_name"] == course]
        course_texts[course] = " ".join(subclos["sub_clo_text"].dropna().tolist())

    if len(course_texts) == 0:
        raise ValueError("No matched courses found - run the main pipeline first.")

    job_texts = (jobs["title"].fillna("") + ". " + jobs["description"].fillna("")).tolist()
    corpus = list(course_texts.values()) + job_texts

    vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
    tfidf = vectorizer.fit_transform(corpus)

    n_courses = len(course_texts)
    course_vecs = tfidf[:n_courses]
    job_vecs = tfidf[n_courses:]

    sims = cosine_similarity(course_vecs, job_vecs)  # shape (n_courses, n_jobs)

    rows = []
    for i, course in enumerate(course_texts.keys()):
        top_idx = np.argsort(-sims[i])[:TOP_K]
        for rank, j in enumerate(top_idx, start=1):
            rows.append({
                "course_name": course, "rank": rank,
                "job_id": jobs.iloc[j]["job_id"], "job_title": jobs.iloc[j]["title"],
                "tfidf_similarity": round(float(sims[i, j]), 4),
            })
    return pd.DataFrame(rows), sims, list(course_texts.keys())


def compare_to_semantic(baseline_df):
    try:
        semantic = pd.read_csv("final_recommendations_full.csv")
    except FileNotFoundError:
        print("\n(final_recommendations_full.csv not found - skipping semantic comparison. "
              "Run full_pipeline_subclo.py / full_pipeline_certs.py first to enable this.)")
        return None

    baseline_job_scores = baseline_df.groupby("job_id")["tfidf_similarity"].max().reset_index()
    merged = baseline_job_scores.merge(semantic[["job_id", "final_score"]], on="job_id", how="inner")

    if len(merged) < 3:
        print(f"\nOnly {len(merged)} overlapping jobs between baseline and semantic results - "
              "too few to compute a meaningful correlation.")
        return merged

    rho, pval = spearmanr(merged["tfidf_similarity"], merged["final_score"])
    print(f"\n=== Baseline (TF-IDF) vs Semantic (SBERT+CE) ===")
    print(f"Overlapping jobs compared: {len(merged)}")
    print(f"Spearman correlation: rho={rho:.3f} (p={pval:.4f})")
    if rho < 0.3:
        print("-> LOW correlation: the two methods disagree substantially. Worth inspecting")
        print("   specific cases where semantic ranks a job highly but TF-IDF doesn't (or vice")
        print("   versa) - that's concrete evidence for your report of what semantic matching")
        print("   catches that keyword matching misses.")
    elif rho > 0.7:
        print("-> HIGH correlation: the two methods mostly agree. Worth checking whether the")
        print("   semantic pipeline is adding real value here, or whether these particular")
        print("   course/job texts happen to share enough vocabulary that TF-IDF gets close.")
    else:
        print("-> MODERATE correlation: partial agreement, meaningful differences exist.")

    merged.to_csv("baseline_vs_semantic_comparison.csv", index=False)
    print("Saved: baseline_vs_semantic_comparison.csv")
    return merged


def main():
    match_log = pd.read_csv("pipeline_course_match_log.csv")
    subclo_profiles = pd.read_csv("sub_clo_profiles.csv")
    jobs = pd.read_csv("jobs_unified_with_skills.csv")

    print("Building TF-IDF baseline ranking...")
    baseline_df, sims, courses = build_baseline_ranking(match_log, subclo_profiles, jobs)
    baseline_df.to_csv("baseline_job_ranking.csv", index=False)
    print(f"Saved: baseline_job_ranking.csv ({len(baseline_df)} rows across {len(courses)} courses)")

    print("\n--- Sample: top 3 baseline matches per course ---")
    for course in courses[:3]:
        sub = baseline_df[baseline_df["course_name"] == course].head(3)
        print(f"\n{course}:")
        print(sub[["job_title", "tfidf_similarity"]].to_string(index=False))

    compare_to_semantic(baseline_df)


if __name__ == "__main__":
    main()
