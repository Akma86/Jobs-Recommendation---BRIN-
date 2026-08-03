# -*- coding: utf-8 -*-
"""
ABLATION STUDY - runs controlled variants of the pipeline to show each
architectural choice actually matters, rather than being decoration.

Three ablations, each isolating one design decision:

  A. SBERT-ONLY vs SBERT+CROSS-ENCODER
     Does reranking change the top-K meaningfully, or would raw SBERT
     similarity alone have given basically the same answer? (We already
     saw qualitative evidence of this earlier - a generic "Software"
     posting dominated SBERT-only rankings until cross-encoder reranking
     fixed it - this ablation quantifies that across the whole matched set.)

  B. MAX vs MEAN aggregation (sub-CLO -> course)
     Does using MAX (one strong sub-CLO match is enough) vs MEAN
     (all sub-CLOs must be relevant on average) change which courses
     "win" for a given job? This directly tests the design justification
     written into aggregate_subclo_to_course()'s docstring.

  C. WITH vs WITHOUT certificate signal
     Does adding certificates change the final top-K at all, or is the
     KHS signal already dominant enough that certs are cosmetic? If certs
     never change the ranking, that's worth knowing before defending them
     as a meaningful part of the architecture.

REQUIREMENTS:
  pip install sentence-transformers pandas scipy --break-system-packages
  (needs the same models as the main pipeline - run this locally, not in
  a constrained sandbox)

INPUT: same folder as a completed full_pipeline_certs.py run (needs
sub_clo_job_ranking.csv, course_job_aggregated.csv, cert_job_aggregated.csv,
pipeline_course_match_log.csv, jobs_unified_with_skills.csv).

OUTPUT:
  - ablation_A_sbert_vs_crossencoder.csv
  - ablation_B_max_vs_mean.csv
  - ablation_C_with_without_certs.csv
  - printed rank-correlation summary for each
"""

import pandas as pd
import numpy as np
from scipy.stats import spearmanr
from collections import defaultdict


def top_k_overlap(list_a, list_b, k=10):
    a, b = set(list_a[:k]), set(list_b[:k])
    return len(a & b) / k


def ablation_a_sbert_vs_crossencoder():
    """Compares ranking-by-raw-SBERT-similarity vs ranking-by-cross-encoder-score,
    using the SAME retrieved candidate pool (sub_clo_job_ranking.csv already
    only contains jobs that survived SBERT retrieval - this reranks that same
    pool two different ways, isolating just the reranking step's effect)."""
    df = pd.read_csv("sub_clo_job_ranking.csv")
    if "similarity" not in df.columns:
        print("A) SKIPPED: sub_clo_job_ranking.csv doesn't have a raw SBERT 'similarity' "
              "column in this run - only cross_encoder_score was saved. Re-run the main "
              "pipeline with a version that also logs pre-rerank similarity to enable this.")
        return None

    results = []
    for course, group in df.groupby("course_name"):
        by_sbert = group.sort_values("similarity", ascending=False)["job_title"].tolist()
        by_ce = group.sort_values("cross_encoder_score", ascending=False)["job_title"].tolist()
        overlap = top_k_overlap(by_sbert, by_ce, k=min(5, len(group)))
        results.append({"course_name": course, "n_candidates": len(group),
                         "top5_overlap_sbert_vs_ce": round(overlap, 2)})

    out = pd.DataFrame(results)
    out.to_csv("ablation_A_sbert_vs_crossencoder.csv", index=False)
    avg_overlap = out["top5_overlap_sbert_vs_ce"].mean()
    print(f"A) SBERT-only vs SBERT+CrossEncoder: avg top-5 overlap = {avg_overlap:.2f} "
          f"(1.0 = rerank changed nothing, 0.0 = rerank changed everything)")
    print("   Saved: ablation_A_sbert_vs_crossencoder.csv")
    return out


def ablation_b_max_vs_mean():
    df = pd.read_csv("sub_clo_job_ranking.csv")

    max_agg = (df.groupby(["course_name", "job_id", "job_title"])["cross_encoder_score"]
               .max().reset_index(name="score_max"))
    mean_agg = (df.groupby(["course_name", "job_id", "job_title"])["cross_encoder_score"]
                .mean().reset_index(name="score_mean"))

    results = []
    for course in df["course_name"].unique():
        m1 = max_agg[max_agg["course_name"] == course].sort_values("score_max", ascending=False)
        m2 = mean_agg[mean_agg["course_name"] == course].sort_values("score_mean", ascending=False)
        overlap = top_k_overlap(m1["job_title"].tolist(), m2["job_title"].tolist(), k=min(5, len(m1)))
        results.append({"course_name": course, "n_jobs": len(m1), "top5_overlap_max_vs_mean": round(overlap, 2)})

    out = pd.DataFrame(results)
    out.to_csv("ablation_B_max_vs_mean.csv", index=False)
    avg_overlap = out["top5_overlap_max_vs_mean"].mean()
    print(f"\nB) MAX vs MEAN aggregation: avg top-5 overlap = {avg_overlap:.2f}")
    print("   Saved: ablation_B_max_vs_mean.csv")
    return out


def ablation_c_with_without_certs():
    try:
        with_certs = pd.read_csv("final_recommendations_full.csv")  # produced by full_pipeline_certs.py, includes cert signal
    except FileNotFoundError:
        print("\nC) SKIPPED: final_recommendations_full.csv not found.")
        return None

    try:
        course_agg = pd.read_csv("course_job_aggregated.csv")
        match_log = pd.read_csv("pipeline_course_match_log.csv")
    except FileNotFoundError:
        print("\nC) SKIPPED: missing course_job_aggregated.csv or pipeline_course_match_log.csv")
        return None

    # rebuild the KHS-ONLY score (i.e. what full_pipeline_subclo.py alone would have produced)
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
        print("   -> Certificates did NOT change the top-10 ranking in this run. Either the KHS")
        print("      signal already dominates, or CERT_WEIGHT_GLOBAL is too low to matter - worth")
        print("      checking both before claiming certs are a meaningful part of the system.")
    else:
        print(f"   -> {(1-overlap)*10:.0f} jobs entered/left the top-10 because of certificates.")
    print("   Saved: ablation_C_with_without_certs.csv")
    return merged


def main():
    print("=== ABLATION STUDY ===\n")
    ablation_a_sbert_vs_crossencoder()
    ablation_b_max_vs_mean()
    ablation_c_with_without_certs()


if __name__ == "__main__":
    main()
