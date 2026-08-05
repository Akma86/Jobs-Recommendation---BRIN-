import argparse
import pandas as pd
import numpy as np
from difflib import SequenceMatcher
from collections import defaultdict
from sentence_transformers import SentenceTransformer, CrossEncoder

# pyrefly: ignore [missing-import]
from issuer_tiers import get_certificate_credibility_weight

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
SBERT_MODEL = "intfloat/multilingual-e5-large"
CROSS_ENCODER_MODEL = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
MATCH_THRESHOLD = 0.55       # course-name fuzzy match confidence cutoff
TOP_K_RETRIEVAL = 15         # SBERT top-K per query unit (course/cert), before rerank
TOP_K_PER_UNIT = 5           # jobs kept per query unit after rerank
TOP_N_OUTPUT = 15            # final recommendations to output
CERT_WEIGHT_GLOBAL = 1.0     # relative weight of the certificate signal vs the KHS signal

JOBS_CSV_PATH = r"D:\MAIN DATA\Documents\Semester 6\KP BRIN\Dataset\Pekerjaan\Processed\jobs_unified.csv"
# course_clo_consolidated.csv is produced by consolidate_subclo.py (1 row per
# course_name, with a consolidated_clo_text paraphrasing all of its sub-CLOs).
# Matching is now done at the course level, not per individual sub-CLO.
COURSE_CLO_CSV_PATH = r"D:\MAIN DATA\Documents\Semester 6\KP BRIN\Dataset\Mata Kuliah\course_clo_consolidated.csv"

GRADE_MAP = {"A": 0.85, "AB": 0.80, "B": 0.70, "BC": 0.60, "C": 0.55, "D": 0.50, "E": 0.0}


# ---------------------------------------------------------------------------
# STAGE 1: parse KHS
# ---------------------------------------------------------------------------
def load_khs(path):
    df = pd.read_csv(path)

    required_cols = ["kode_mk", "nama_mk"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in {path}: {missing}")

    if "grade_weight" not in df.columns:
        if "nilai_huruf" not in df.columns:
            raise ValueError(f"{path} needs either 'grade_weight' or 'nilai_huruf' column")
        df["nilai_huruf"] = df["nilai_huruf"].str.upper().str.strip()
        df["grade_weight"] = df["nilai_huruf"].map(GRADE_MAP)
        if df["grade_weight"].isna().any():
            bad = df[df["grade_weight"].isna()]["nilai_huruf"].unique()
            raise ValueError(f"Unrecognized grade values: {bad}")

    return df

# ---------------------------------------------------------------------------
# Load certificates + compute credibility weight per certificate
# ---------------------------------------------------------------------------
def load_certificates(path):
    if not path:
        return pd.DataFrame()
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
# STAGE 2: fuzzy match KHS courses to available courses (course_clo_consolidated.csv)
# ---------------------------------------------------------------------------
def similarity(a, b):
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()


def match_courses(khs, available_course_names):
    rows = []
    for _, k in khs.iterrows():
        best_score, best_name = 0, None
        for course_name in available_course_names:
            s = similarity(k["nama_mk"], course_name)
            if s > best_score:
                best_score, best_name = s, course_name
        rows.append({
            "kode_mk": k["kode_mk"],
            "khs_course": k["nama_mk"],
            "grade_weight": k["grade_weight"],
            "matched_course_name": best_name,
            "match_confidence": round(best_score, 3),
        })
    df = pd.DataFrame(rows)
    df["included"] = df["match_confidence"] >= MATCH_THRESHOLD
    return df


# ---------------------------------------------------------------------------
# Retrieval+rerank for a set of query units. Generic over id_col/text_col so
# it can be reused for course-level queries (course_name / consolidated_clo_text)
# and certificate-level queries (cert_id / cert_text) alike.
# ---------------------------------------------------------------------------
def rank_jobs_for_queries(query_df, id_col, text_col, jobs, job_emb, sbert_model, cross_encoder,
                           desc_col="description", extra_cols=()):
    """query_df needs columns [id_col, text_col] + extra_cols to carry through."""
    rows = []
    for i, (_, q) in enumerate(query_df.iterrows()):
        query_text = "query: " + str(q[text_col])
        q_emb = sbert_model.encode([query_text], normalize_embeddings=True)[0]

        sims = job_emb @ q_emb
        top_idx = np.argsort(-sims)[:TOP_K_RETRIEVAL]

        pairs = [(str(q[text_col])[:1500],
                  str(jobs.iloc[j]["title"]) + ". " + str(jobs.iloc[j][desc_col])[:1500])
                 for j in top_idx]
        ce_scores = cross_encoder.predict(pairs, batch_size=16)

        sub_jobs = jobs.iloc[top_idx].copy()
        sub_jobs["cross_encoder_score"] = ce_scores
        sub_jobs = sub_jobs.sort_values("cross_encoder_score", ascending=False).head(TOP_K_PER_UNIT)

        for rank, (_, jr) in enumerate(sub_jobs.iterrows(), start=1):
            row = {c: q[c] for c in extra_cols}
            row.update({
                id_col: q[id_col],
                "rank": rank,
                "job_id": jr["job_id"],
                "job_title": jr["title"],
                "job_company": jr["company"],
                "job_source": jr["source"],
                "cross_encoder_score": round(float(jr["cross_encoder_score"]), 4),
            })
            rows.append(row)

        if (i + 1) % 10 == 0:
            print(f"  processed {i+1}/{len(query_df)}...")

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Course-level retrieval+rerank. Each course already has exactly ONE query
# text (consolidated_clo_text from consolidate_subclo.py), so this is just
# rank_jobs_for_queries() at the course granularity, with the score column
# renamed to course_job_score_max for compatibility with the student-level
# aggregation step below (which used to consume a MAX-aggregated sub-CLO
# score of the same name).
# ---------------------------------------------------------------------------
def match_courses_to_jobs(course_clo_df, jobs, job_emb, sbert_model, cross_encoder, desc_col="description"):
    ranking = rank_jobs_for_queries(
        course_clo_df, id_col="course_name", text_col="consolidated_clo_text",
        jobs=jobs, job_emb=job_emb, sbert_model=sbert_model, cross_encoder=cross_encoder,
        desc_col=desc_col, extra_cols=(),
    )
    return ranking.rename(columns={"cross_encoder_score": "course_job_score_max"})

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
                                   "cert_id", "cert_title", "cross_encoder_score", "weighted_score"]]
    return best.rename(columns={"weighted_score": "cert_score_max", "cert_id": "best_cert_id",
                                 "cert_title": "best_cert_title"})


# ---------------------------------------------------------------------------
# Final aggregation: KHS signal (per-course, consolidated) + optional certificate signal
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
                f"KHS: '{m['khs_course']}' (nilai={m['grade_weight']:.2f}, match={m['match_confidence']:.2f}) "
                f"-> skor kecocokan MK={cj['course_job_score_max']:.2f}"
            )
            if job_id not in job_info:
                job_info[job_id] = {"job_title": cj["job_title"], "job_company": cj["job_company"],
                                     "job_source": cj["job_source"]}

    if not certs_df.empty and "cert_id" in certs_df.columns:
        cred_map = certs_df.set_index("cert_id")["credibility_weight"].to_dict()
    else:
        cred_map = {}

    if not cert_agg.empty:
        for _, row in cert_agg.iterrows():
            job_id = row["job_id"]
            contribution = CERT_WEIGHT_GLOBAL * row["cert_score_max"]
            job_scores[job_id] += contribution
            cred = cred_map.get(row["best_cert_id"], 0.0)
            job_explanations[job_id].append(
                f"Sertifikat: '{row['best_cert_title']}' (kredibilitas={cred:.2f}, "
                f"relevansi={row['cross_encoder_score']:.2f}) -> kontribusi={contribution:.2f}"
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
    parser.add_argument("--certs", required=False, default=None, help="certificates_parsed.csv from parse_input.py (optional)")
    parser.add_argument("--jobs", default=JOBS_CSV_PATH, help="path to jobs_unified_with_skills.csv")
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
    print(matched[["khs_course", "matched_course_name", "match_confidence", "included"]].to_string(index=False))
    n_included = matched["included"].sum()
    print(f"\n{n_included}/{len(matched)} KHS courses matched (confidence >= {MATCH_THRESHOLD})")
    if n_included == 0:
        print("No usable matches - stopping.")
        return

    certs_df = pd.DataFrame()
    if args.certs:
        print("\n=== Stage 2b: Loading certificates + computing credibility weights ===")
        certs_df = load_certificates(args.certs)
        if len(certs_df) == 0:
            print("No certificates found - nothing to add on top of the KHS signal.")
    else:
        print("\n=== Stage 2b: Skipping certificates (no --certs provided) ===")

    print("\n=== Stage 3: Embedding job postings ===")
    jobs = pd.read_csv(args.jobs)
    desc_col = "description_summary" if "description_summary" in jobs.columns else "description"
    print(f"Using job text column: '{desc_col}' (run summarize_jobs.py first for the summarized version)")
    sbert_model = SentenceTransformer(SBERT_MODEL)
    cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL)
    job_texts = ("passage: " + jobs["title"].fillna("") + ". " + jobs[desc_col].fillna("").str.slice(0, 1500))
    job_emb = sbert_model.encode(job_texts.tolist(), normalize_embeddings=True, show_progress_bar=True, batch_size=32)

    print("\n=== Stage 4a: Per-course retrieval + rerank ===")
    included_course_names = matched[matched["included"]]["matched_course_name"].unique()
    relevant_courses = course_clo_profiles[course_clo_profiles["course_name"].isin(included_course_names)]
    course_agg = match_courses_to_jobs(
        relevant_courses, jobs=jobs, job_emb=job_emb,
        sbert_model=sbert_model, cross_encoder=cross_encoder, desc_col=desc_col,
    )
    course_agg.to_csv("course_job_aggregated.csv", index=False)
    print(f"Saved: course_job_aggregated.csv ({len(course_agg)} rows)")

    cert_agg = pd.DataFrame()
    if not certs_df.empty:
        print("\n=== Stage 4b: Per-certificate retrieval + rerank ===")
        cert_ranking = rank_jobs_for_queries(
            certs_df, id_col="cert_id", text_col="cert_text",
            jobs=jobs, job_emb=job_emb, sbert_model=sbert_model, cross_encoder=cross_encoder,
            desc_col=desc_col, extra_cols=["title"],
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
