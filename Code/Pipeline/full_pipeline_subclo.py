import argparse
import pandas as pd
import numpy as np
from difflib import SequenceMatcher
from collections import defaultdict
from sentence_transformers import SentenceTransformer, CrossEncoder

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
SBERT_MODEL = "intfloat/multilingual-e5-large"
CROSS_ENCODER_MODEL = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
MATCH_THRESHOLD = 0.55       # course-name fuzzy match confidence cutoff
TOP_K_RETRIEVAL = 15         # SBERT top-K per query unit, before rerank
TOP_K_PER_UNIT = 5           # jobs kept per query unit after rerank
CV_WEIGHT = 1.0              # relative weight of CV signal vs RPS signal
TOP_N_OUTPUT = 15            # final recommendations to output

GRADE_MAP = {"A": 0.85, "AB": 0.80, "B": 0.70, "BC": 0.60, "C": 0.55, "D": 0.50, "E": 0.0}


# ---------------------------------------------------------------------------
# STAGE 1: parse KHS
# ---------------------------------------------------------------------------
def load_khs(path):
    df = pd.read_csv(path)

    required_cols = [
        "kode_mk",
        "nama_mk",
        "clo_code",
        "clo_desc",
        "grade_weight"
    ]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing columns in transcript_parsed.csv: {missing}"
        )

    return df


# ---------------------------------------------------------------------------
# STAGE 2: fuzzy match KHS courses to available sub-CLO courses
# ---------------------------------------------------------------------------
def similarity(a, b):
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()


def match_courses(khs, subclo_courses):
    rows = []
    for _, k in khs.iterrows():
        best_score, best_name = 0, None
        for course_name in subclo_courses:
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
# Shared retrieval+rerank routine - used for BOTH sub-CLOs and CV units,
# since they're now treated identically (symmetric design).
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
# Aggregation helpers
# ---------------------------------------------------------------------------
def aggregate_subclo_to_course(subclo_ranking):
    agg = (subclo_ranking.groupby(["course_name", "job_id", "job_title", "job_company", "job_source"])
           .agg(course_job_score_max=("cross_encoder_score", "max"),
                n_subclo_matched=("sub_clo_code", "count"))
           .reset_index())
    return agg


def aggregate_cv_units(cv_unit_ranking):
    """MAX over all CV units per job - one strong project/experience match is enough."""
    agg = (cv_unit_ranking.groupby(["job_id"])
           .agg(cv_score_max=("cross_encoder_score", "max"),
                best_cv_unit=("cv_unit_id", lambda x: x.iloc[
                    cv_unit_ranking.loc[x.index, "cross_encoder_score"].values.argmax()]))
           .reset_index())
    return agg


# ---------------------------------------------------------------------------
# STAGE FINAL: aggregate course-level + CV-level -> student-level
# ---------------------------------------------------------------------------
def aggregate_to_student_level(matched_courses, course_agg, cv_agg, cv_unit_ranking):
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
                f"'{m['khs_course']}' (nilai_bobot={m['grade_weight']:.2f}, match={m['match_confidence']:.2f}) "
                f"-> skor sub-CLO terbaik={cj['course_job_score_max']:.2f}"
            )
            if job_id not in job_info:
                job_info[job_id] = {"job_title": cj["job_title"], "job_company": cj["job_company"],
                                     "job_source": cj["job_source"]}

    # CV signal
    cv_unit_titles = cv_unit_ranking.set_index("cv_unit_id")["cv_unit_title"].to_dict() \
        if "cv_unit_title" in cv_unit_ranking.columns else {}
    for _, cv_row in cv_agg.iterrows():
        job_id = cv_row["job_id"]
        contribution = CV_WEIGHT * cv_row["cv_score_max"]
        job_scores[job_id] += contribution
        unit_label = cv_unit_titles.get(cv_row["best_cv_unit"], cv_row["best_cv_unit"])
        job_explanations[job_id].append(
            f"CV project '{unit_label}' -> skor={cv_row['cv_score_max']:.2f}"
        )
        if job_id not in job_info:
            match = cv_unit_ranking[cv_unit_ranking["job_id"] == job_id].iloc[0]
            job_info[job_id] = {"job_title": match["job_title"], "job_company": match["job_company"],
                                 "job_source": match["job_source"]}

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
# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--khs", required=True, help="transcript_parsed.csv from parse_input.py")
    parser.add_argument("--cv_units", required=True, help="cv_units_parsed.csv from parse_input.py")
    args = parser.parse_args()

    print("=== Stage 1-2: KHS parsing + course matching ===")
    khs = load_khs(args.khs)

    khs_courses = (
        khs.groupby(
            ["kode_mk", "nama_mk"],
            as_index=False
        )
        .agg({
            "grade_weight": "mean"
        })
    )
    
    # --- PENYESUAIAN DI SINI ---
    subclo_headers = ["course_name", "sub_clo_code", "sub_clo_text", "source_file"]
    subclo_profiles = pd.read_csv("sub_clo_profiles.csv", header=None, names=subclo_headers)
    # ---------------------------

    available_courses = subclo_profiles["course_name"].unique().tolist()
    matched = match_courses(
        khs_courses,
        available_courses
    )
    matched.to_csv("pipeline_course_match_log.csv", index=False)
    print(matched[["khs_course", "matched_course_name", "match_confidence", "included"]].to_string(index=False))
    n_included = matched["included"].sum()
    print(f"\n{n_included}/{len(matched)} KHS courses matched (confidence >= {MATCH_THRESHOLD})")
    if n_included == 0:
        print("No usable matches - stopping.")
        return

    cv_units = pd.read_csv(args.cv_units)
    cv_units["cv_unit_text"] = cv_units["title"].fillna("") + ". " + cv_units["description"].fillna("")
    print(f"\nCV units loaded: {len(cv_units)}")
    print(cv_units[["title"]].to_string(index=False))

    print("\n=== Stage 3: Embedding job postings (shared across both streams) ===")
    jobs = pd.read_csv("D:\MAIN DATA\Documents\Semester 6\KP BRIN\Experiment Disini Dulu AJa\jobs_unified_with_skills.csv")
    desc_col = "description_summary" if "description_summary" in jobs.columns else "description"
    print(f"Using job text column: '{desc_col}' (run summarize_jobs.py first for the summarized version)")
    sbert_model = SentenceTransformer(SBERT_MODEL)
    cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL)
    job_texts = ("passage: " + jobs["title"].fillna("") + ". " + jobs[desc_col].fillna("").str.slice(0, 1500))
    job_emb = sbert_model.encode(job_texts.tolist(), normalize_embeddings=True, show_progress_bar=True, batch_size=32)

    print("\n=== Stage 4a: Per-sub-CLO retrieval + rerank ===")
    included_course_names = matched[matched["included"]]["matched_course_name"].unique()
    relevant_subclos = subclo_profiles[subclo_profiles["course_name"].isin(included_course_names)]
    subclo_ranking = rank_jobs_for_queries(
        relevant_subclos, id_col="sub_clo_code", text_col="sub_clo_text",
        jobs=jobs, job_emb=job_emb, sbert_model=sbert_model, cross_encoder=cross_encoder,
        desc_col=desc_col, extra_cols=["course_name"],
    )
    subclo_ranking.to_csv("sub_clo_job_ranking.csv", index=False)
    print(f"Saved: sub_clo_job_ranking.csv ({len(subclo_ranking)} rows)")

    print("\n=== Stage 4b: Per-CV-unit retrieval + rerank ===")
    cv_unit_ranking = rank_jobs_for_queries(
        cv_units, id_col="cv_unit_id", text_col="cv_unit_text",
        jobs=jobs, job_emb=job_emb, sbert_model=sbert_model, cross_encoder=cross_encoder,
        desc_col=desc_col, extra_cols=["title"],
    )
    cv_unit_ranking = cv_unit_ranking.rename(columns={"title": "cv_unit_title"})
    cv_unit_ranking.to_csv("cv_unit_job_ranking.csv", index=False)
    print(f"Saved: cv_unit_job_ranking.csv ({len(cv_unit_ranking)} rows)")

    print("\n=== Stage 5: Aggregating sub-CLO -> course, CV units -> single signal ===")
    course_agg = aggregate_subclo_to_course(subclo_ranking)
    course_agg.to_csv("course_job_aggregated.csv", index=False)
    cv_agg = aggregate_cv_units(cv_unit_ranking)

    print("\n=== Stage 6: Aggregating to student level (RPS signal + CV signal) ===")
    final_ranking = aggregate_to_student_level(matched, course_agg, cv_agg, cv_unit_ranking)
    final_ranking.head(TOP_N_OUTPUT).to_csv("final_recommendations.csv", index=False)
    print(f"Saved: final_recommendations.csv (top {TOP_N_OUTPUT})")

    print("\n--- Top 5 preview ---")
    for _, row in final_ranking.head(5).iterrows():
        print(f"\n[{row['final_score']}] {row['job_title']} @ {row['job_company']}")
        print(f"   why: {row['explanation']}")


if __name__ == "__main__":
    main()