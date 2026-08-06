# -*- coding: utf-8 -*-
"""
BASELINE KEYWORD MATCHING - answers "what if we just used TF-IDF?"
(The standard baseline Reyhan and most other papers compare against).

If the semantic pipeline's rankings mostly AGREE with this baseline, that's
actually a bit concerning. If they DIFFER meaningfully - that's your evidence
the added complexity earns its keep.

REQUIREMENTS: pip install scikit-learn pandas --break-system-packages

INPUT FILES:
  - course_clo_consolidated.csv (provided via absolute path argument)
  - jobs_unified_with_skills.csv (provided via absolute path argument)
  - pipeline_course_match_log.csv (which courses are "the student's" - in current folder)
  - final_recommendations.csv (optional, for comparison - in current folder)

OUTPUT:
  - baseline_job_ranking.csv        top jobs per matched course, TF-IDF only
  - baseline_vs_semantic_comparison.csv   (only if final_recommendations.csv exists)
"""

import argparse
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats import spearmanr

TOP_K = 10

def build_baseline_ranking(match_log, course_clo_profiles, jobs):
    matched_courses = match_log[match_log["included"]]["matched_course_name"].unique()
    course_texts = {}
    for course in matched_courses:
        course_row = course_clo_profiles[course_clo_profiles["course_name"] == course]
        if not course_row.empty:
            course_texts[course] = str(course_row.iloc[0]["consolidated_clo_text"])

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
        semantic = pd.read_csv("final_recommendations.csv")
    except FileNotFoundError:
        print("\n(final_recommendations.csv not found - skipping semantic comparison.)")
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
    elif rho > 0.7:
        print("-> HIGH correlation: the two methods mostly agree. Worth checking whether the")
    else:
        print("-> MODERATE correlation: partial agreement, meaningful differences exist.")

    merged.to_csv("baseline_vs_semantic_comparison.csv", index=False)
    print("Saved: baseline_vs_semantic_comparison.csv")
    return merged


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--course_clo_csv", required=True)
    parser.add_argument("--jobs_csv", required=True)
    args = parser.parse_args()

    match_log = pd.read_csv("pipeline_course_match_log.csv")
    course_clo_profiles = pd.read_csv(args.course_clo_csv)
    jobs = pd.read_csv(args.jobs_csv)

    print("Building TF-IDF baseline ranking...")
    baseline_df, sims, courses = build_baseline_ranking(match_log, course_clo_profiles, jobs)
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
