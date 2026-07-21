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
TOP_K_RETRIEVAL = 15         # SBERT top-K per sub-CLO, before rerank
TOP_K_PER_UNIT = 5           # jobs kept per sub-CLO after rerank
TOP_N_OUTPUT = 15            # final recommendations to output
JOBS_CSV_PATH = "D:\MAIN DATA\Documents\Semester 6\KP BRIN\Dataset\Pekerjaan\Processed\jobs_unified.csv"  # edit if your file lives elsewhere

GRADE_MAP = {"A": 0.85, "AB": 0.80, "B": 0.70, "BC": 0.60, "C": 0.55, "D": 0.50, "E": 0.0}


# ---------------------------------------------------------------------------
# STAGE 1: parse KHS
# ---------------------------------------------------------------------------
def load_khs(path):
    """
    Expects the transcript_parsed.csv format produced by parse_input.py:
    kode_mk, nama_mk, sks, nilai_huruf (grade_weight is computed here if
    not already present - no need to pre-supply it, and no clo_code/clo_desc
    columns belong in a transcript file, those live in sub_clo_profiles.csv).
    """
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
# Retrieval+rerank for a set of query units (sub-CLOs here; kept generic so
# a CV-unit stream can be added back later by calling this again).
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
# Aggregation: sub-CLO -> course (MAX - one strong sub-CLO match is enough)
# ---------------------------------------------------------------------------
def aggregate_subclo_to_course(subclo_ranking):
    agg = (subclo_ranking.groupby(["course_name", "job_id", "job_title", "job_company", "job_source"])
           .agg(course_job_score_max=("cross_encoder_score", "max"),
                n_subclo_matched=("sub_clo_code", "count"))
           .reset_index())
    return agg


# ---------------------------------------------------------------------------
# STAGE FINAL: aggregate course-level -> student-level (KHS signal only)
# ---------------------------------------------------------------------------
def aggregate_to_student_level(matched_courses, course_agg):
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
    parser.add_argument("--jobs", default=JOBS_CSV_PATH, help="path to jobs_unified_with_skills.csv")
    args = parser.parse_args()

    print("=== Stage 1-2: KHS parsing + course matching ===")
    khs = load_khs(args.khs)
    khs_courses = khs.groupby(["kode_mk", "nama_mk"], as_index=False).agg({"grade_weight": "mean"})

    subclo_profiles = pd.read_csv("D:\MAIN DATA\Documents\Semester 6\KP BRIN\Dataset\Mata Kuliah\sub_clo_profiles.csv")  # normal header row, no manual renaming needed
    available_courses = subclo_profiles["course_name"].unique().tolist()

    matched = match_courses(khs_courses, available_courses)
    matched.to_csv("pipeline_course_match_log.csv", index=False)
    print(matched[["khs_course", "matched_course_name", "match_confidence", "included"]].to_string(index=False))
    n_included = matched["included"].sum()
    print(f"\n{n_included}/{len(matched)} KHS courses matched (confidence >= {MATCH_THRESHOLD})")
    if n_included == 0:
        print("No usable matches - stopping.")
        return

    print("\n=== Stage 3: Embedding job postings ===")
    jobs = pd.read_csv(args.jobs)
    desc_col = "description_summary" if "description_summary" in jobs.columns else "description"
    print(f"Using job text column: '{desc_col}' (run summarize_jobs.py first for the summarized version)")
    sbert_model = SentenceTransformer(SBERT_MODEL)
    cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL)
    job_texts = ("passage: " + jobs["title"].fillna("") + ". " + jobs[desc_col].fillna("").str.slice(0, 1500))
    job_emb = sbert_model.encode(job_texts.tolist(), normalize_embeddings=True, show_progress_bar=True, batch_size=32)

    print("\n=== Stage 4: Per-sub-CLO retrieval + rerank ===")
    included_course_names = matched[matched["included"]]["matched_course_name"].unique()
    relevant_subclos = subclo_profiles[subclo_profiles["course_name"].isin(included_course_names)]
    subclo_ranking = rank_jobs_for_queries(
        relevant_subclos, id_col="sub_clo_code", text_col="sub_clo_text",
        jobs=jobs, job_emb=job_emb, sbert_model=sbert_model, cross_encoder=cross_encoder,
        desc_col=desc_col, extra_cols=["course_name"],
    )
    subclo_ranking.to_csv("sub_clo_job_ranking.csv", index=False)
    print(f"Saved: sub_clo_job_ranking.csv ({len(subclo_ranking)} rows)")

    print("\n=== Stage 5: Aggregating sub-CLO -> course ===")
    course_agg = aggregate_subclo_to_course(subclo_ranking)
    course_agg.to_csv("course_job_aggregated.csv", index=False)

    print("\n=== Stage 6: Aggregating to student level ===")
    final_ranking = aggregate_to_student_level(matched, course_agg)
    final_ranking.head(TOP_N_OUTPUT).to_csv("final_recommendations.csv", index=False)
    print(f"Saved: final_recommendations.csv (top {TOP_N_OUTPUT})")

    print("\n--- Top 5 preview ---")
    for _, row in final_ranking.head(5).iterrows():
        print(f"\n[{row['final_score']}] {row['job_title']} @ {row['job_company']}")
        print(f"   why: {row['explanation']}")


if __name__ == "__main__":
    main()