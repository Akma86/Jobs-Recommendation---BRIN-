# -*- coding: utf-8 -*-
"""
ABLATION STUDY - runs controlled variants of the pipeline to show each
architectural choice actually matters, rather than being decoration.

Ablations:
  C. WITH vs WITHOUT certificate signal
     Does adding certificates change the final top-K at all, or is the
     KHS signal already dominant enough that certs are cosmetic? If certs
     never change the ranking, that's worth knowing before defending them
     as a meaningful part of the architecture.

(Ablation A & B were removed as they applied to the deprecated sub-CLO architecture)

REQUIREMENTS:
  pip install pandas scipy --break-system-packages

INPUT: same folder as a completed app.py run (needs
course_job_aggregated.csv, pipeline_course_match_log.csv, final_recommendations.csv).

OUTPUT:
  - ablation_C_with_without_certs.csv
  - printed rank-correlation summary for each
"""

import pandas as pd
from scipy.stats import spearmanr
from collections import defaultdict

def top_k_overlap(list_a, list_b, k=10):
    a, b = set(list_a[:k]), set(list_b[:k])
    if k == 0:
        return 0
    return len(a & b) / k

def ablation_c_with_without_certs():
    try:
        with_certs = pd.read_csv("final_recommendations.csv")
    except FileNotFoundError:
        print("\nC) SKIPPED: final_recommendations.csv not found.")
        return None

    try:
        course_agg = pd.read_csv("course_job_aggregated.csv")
        match_log = pd.read_csv("pipeline_course_match_log.csv")
    except FileNotFoundError:
        print("\nC) SKIPPED: missing course_job_aggregated.csv or pipeline_course_match_log.csv")
        return None

    # rebuild the KHS-ONLY score
    khs_only_scores = defaultdict(float)
    job_titles = {}
    included = match_log[match_log["included"]]
    for _, m in included.iterrows():
        weight = m["grade_weight"] * m["match_confidence"]
        course_jobs = course_agg[course_agg["course_name"] == m["matched_course_name"]]
        for _, cj in course_jobs.iterrows():
            khs_only_scores[cj["job_id"]] += weight * cj["course_job_score_max"]
            job_titles[cj["job_id"]] = cj["job_title"]

    khs_only_df = pd.DataFrame([{"job_id": k, "job_title": job_titles[k], "khs_only_score": v}
                                 for k, v in khs_only_scores.items()])

    merged = khs_only_df.merge(with_certs[["job_id", "final_score"]], on="job_id", how="outer").fillna(0)
    merged = merged.sort_values("final_score", ascending=False)
    merged.to_csv("ablation_C_with_without_certs.csv", index=False)

    top10_khs_only = merged.sort_values("khs_only_score", ascending=False).head(10)["job_id"].tolist()
    top10_with_certs = merged.sort_values("final_score", ascending=False).head(10)["job_id"].tolist()
    overlap = top_k_overlap(top10_khs_only, top10_with_certs, k=10)

    rho, _ = spearmanr(merged["khs_only_score"], merged["final_score"])

    print(f"\nC) With vs without certificate signal:")
    print(f"   Top-10 overlap: {overlap:.2f} (1.0 = certs changed nothing in the top 10)")
    print(f"   Overall rank correlation (Spearman): {rho:.3f}")
    if overlap == 1.0:
        print("   -> Certificates did NOT change the top-10 ranking in this run.")
    else:
        print(f"   -> {(1-overlap)*10:.0f} jobs entered/left the top-10 because of certificates.")
    print("   Saved: ablation_C_with_without_certs.csv")
    return merged


def main():
    print("=== ABLATION STUDY ===\n")
    ablation_c_with_without_certs()


if __name__ == "__main__":
    main()
