import argparse
import pandas as pd
from collections import defaultdict

from full_pipeline_subclo import (
    SBERT_MODEL, CROSS_ENCODER_MODEL, TOP_N_OUTPUT, JOBS_CSV_PATH, COURSE_CLO_CSV_PATH,
    load_khs, match_courses, rank_jobs_for_queries, match_courses_to_jobs,
)
from issuer_tiers import get_certificate_credibility_weight
from sentence_transformers import SentenceTransformer, CrossEncoder
from explainability import explain_khs_contribution, explain_cert_contribution

CERT_WEIGHT_GLOBAL = 1.0  # relative weight of the certificate signal vs the KHS signal


# ---------------------------------------------------------------------------
# Load certificates + compute credibility weight per certificate
# ---------------------------------------------------------------------------
def load_certificates(path):
    df = pd.read_csv(path)
    if len(df) == 0:
        return df

    weights, breakdowns = [], []
    for _, row in df.iterrows():
        w, b = get_certificate_credibility_weight(
            row.get("issuer"), row.get("has_assessment"), row.get("issue_date")
        )
        weights.append(w)
        breakdowns.append(b)

    df["credibility_weight"] = weights
    df["credibility_breakdown"] = breakdowns
    df["cert_text"] = df["title"].fillna("") + ". " + df["description_text"].fillna("")

    print("\nCertificate credibility weights:")
    print(df[["title", "issuer", "credibility_weight"]].to_string(index=False))
    return df


# ---------------------------------------------------------------------------
# Aggregate cert-level rankings -> single per-job signal
# ---------------------------------------------------------------------------
def aggregate_certs(cert_ranking, certs_df):
    """MAX over (credibility_weight * cross_encoder_score) per job."""
    cred_map = certs_df.set_index("cert_id")["credibility_weight"].to_dict()
    cert_ranking = cert_ranking.copy()
    cert_ranking["weighted_score"] = cert_ranking.apply(
        lambda r: r["cross_encoder_score"] * cred_map.get(r["cert_id"], 0.0), axis=1
    )

    idx = cert_ranking.groupby("job_id")["weighted_score"].idxmax()
    best = cert_ranking.loc[idx, ["job_id", "job_title", "job_company", "job_source",
                                   "cert_id", "cert_title", "cross_encoder_score", "weighted_score",
                                   "explanation"]]
    return best.rename(columns={"weighted_score": "cert_score_max", "cert_id": "best_cert_id",
                                 "cert_title": "best_cert_title"})


# ---------------------------------------------------------------------------
# Final aggregation: KHS signal (per-course, consolidated) + certificate signal
# -> student level
# ---------------------------------------------------------------------------
def aggregate_to_student_level(matched_courses, course_agg, cert_agg, certs_df):
    job_scores = defaultdict(float)
    job_info = {}
    job_explanations = defaultdict(list)

    included = matched_courses[matched_courses["included"]]
    for _, m in included.iterrows():
        weight = m["grade_weight"] * m["match_confidence"]
        course_jobs = course_agg[course_agg["course_name"] == m["matched_course_name"]]
        for _, cj in course_jobs.iterrows():
            job_id = cj["job_id"]
            contribution = weight * cj["course_job_score_max"]
            job_scores[job_id] += contribution
            job_explanations[job_id].append(
                explain_khs_contribution(
                    m["khs_course"], m["grade_weight"], m["match_confidence"],
                    cj["explanation"], contribution,
                )
            )
            if job_id not in job_info:
                job_info[job_id] = {"job_title": cj["job_title"], "job_company": cj["job_company"],
                                     "job_source": cj["job_source"]}

    cred_map = certs_df.set_index("cert_id")["credibility_weight"].to_dict()
    breakdown_map = certs_df.set_index("cert_id")["credibility_breakdown"].to_dict()
    for _, row in cert_agg.iterrows():
        job_id = row["job_id"]
        contribution = CERT_WEIGHT_GLOBAL * row["cert_score_max"]
        job_scores[job_id] += contribution
        cred = cred_map.get(row["best_cert_id"], 0.0)
        breakdown = breakdown_map.get(row["best_cert_id"], "")
        job_explanations[job_id].append(
            explain_cert_contribution(
                row["best_cert_title"], cred, breakdown, row["explanation"], contribution,
            )
        )
        if job_id not in job_info:
            job_info[job_id] = {"job_title": row["job_title"], "job_company": row["job_company"],
                                 "job_source": row["job_source"]}

    rows = []
    for job_id, score in job_scores.items():
        rows.append({
            "job_id": job_id,
            "final_score": round(score, 3),
            "job_title": job_info[job_id]["job_title"],
            "job_company": job_info[job_id]["job_company"],
            "job_source": job_info[job_id]["job_source"],
            "explanation": " | ".join(job_explanations[job_id]),
        })
    return pd.DataFrame(rows).sort_values("final_score", ascending=False)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--khs", required=True, help="transcript_parsed.csv from parse_input.py")
    parser.add_argument("--certs", required=True, help="certificates_parsed.csv from parse_input.py")
    parser.add_argument("--jobs", default=JOBS_CSV_PATH)
    parser.add_argument("--course-clo", default=COURSE_CLO_CSV_PATH,
                         help="path to course_clo_consolidated.csv from consolidate_subclo.py")
    args = parser.parse_args()

    print("=== Stage 1-2: KHS parsing + course matching ===")
    khs = load_khs(args.khs)
    khs_courses = khs.groupby(["kode_mk", "nama_mk"], as_index=False).agg({"grade_weight": "mean"})
    course_clo_profiles = pd.read_csv(args.course_clo)  # 1 row per course_name, consolidated_clo_text column
    available_courses = course_clo_profiles["course_name"].unique().tolist()
    matched = match_courses(khs_courses, available_courses)
    matched.to_csv("pipeline_course_match_log.csv", index=False)
    n_included = matched["included"].sum()
    print(f"{n_included}/{len(matched)} KHS courses matched")

    print("\n=== Stage 2b: Loading certificates + computing credibility weights ===")
    certs_df = load_certificates(args.certs)
    if len(certs_df) == 0:
        print("No certificates found - nothing to add on top of the KHS signal.")

    print("\n=== Stage 3: Embedding job postings ===")
    jobs = pd.read_csv(args.jobs)
    desc_col = "description_summary" if "description_summary" in jobs.columns else "description"
    sbert_model = SentenceTransformer(SBERT_MODEL)
    cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL)
    job_texts = ("passage: " + jobs["title"].fillna("") + ". " + jobs[desc_col].fillna("").str.slice(0, 1500))
    job_emb = sbert_model.encode(job_texts.tolist(), normalize_embeddings=True, show_progress_bar=True, batch_size=32)

    print("\n=== Stage 4a: Per-course retrieval + rerank (KHS signal) ===")
    included_course_names = matched[matched["included"]]["matched_course_name"].unique()
    relevant_courses = course_clo_profiles[course_clo_profiles["course_name"].isin(included_course_names)]
    course_agg = match_courses_to_jobs(
        relevant_courses, jobs=jobs, job_emb=job_emb,
        sbert_model=sbert_model, cross_encoder=cross_encoder, desc_col=desc_col,
    )
    course_agg.to_csv("course_job_aggregated.csv", index=False)
    print(f"Saved: course_job_aggregated.csv ({len(course_agg)} rows)")

    cert_agg = pd.DataFrame()
    if len(certs_df) > 0:
        print("\n=== Stage 4b: Per-certificate retrieval + rerank ===")
        cert_ranking = rank_jobs_for_queries(
            certs_df, id_col="cert_id", text_col="cert_text",
            jobs=jobs, job_emb=job_emb, sbert_model=sbert_model, cross_encoder=cross_encoder,
            desc_col=desc_col, extra_cols=["title"], label_col="title",
        )
        cert_ranking = cert_ranking.rename(columns={"title": "cert_title"})
        cert_ranking.to_csv("cert_job_ranking.csv", index=False)
        print(f"Saved: cert_job_ranking.csv ({len(cert_ranking)} rows)")

        print("\n=== Stage 5: Aggregating certificates -> single signal ===")
        cert_agg = aggregate_certs(cert_ranking, certs_df)
        cert_agg.to_csv("cert_job_aggregated.csv", index=False)

    print("\n=== Stage 6: Final aggregation (KHS + certificate signal) ===")
    final_ranking = aggregate_to_student_level(matched, course_agg, cert_agg, certs_df)
    final_ranking.head(TOP_N_OUTPUT).to_csv("final_recommendations.csv", index=False)
    print(f"Saved: final_recommendations.csv (top {TOP_N_OUTPUT})")

    print("\n--- Top 5 preview ---")
    for _, row in final_ranking.head(5).iterrows():
        print(f"\n[{row['final_score']}] {row['job_title']} @ {row['job_company']}")
        print(f"   why: {row['explanation']}")


if __name__ == "__main__":
    main()
