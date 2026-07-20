# -*- coding: utf-8 -*-
"""
FULL PIPELINE v2: KHS + CV -> Job Recommendations, at SUB-CLO granularity.

KEY DIFFERENCE FROM v1 (full_pipeline.py):
v1 matched at COURSE level - one embedding per course (all CLOs mashed
together into one blob of text), so you couldn't tell WHICH part of a
course drove a match.

v2 matches at SUB-CLO level - each sub-CLO (e.g. "CLO01c: Membedakan
jenis-jenis SI dan memberikan contoh aplikatif") gets its OWN embedding,
retrieval, and cross-encoder re-rank against jobs. This directly answers
your advisor's framing: "for each sub-CLO, which jobs are actually a good
fit for THAT specific competency" - not a blurred course-level average.

Course-level and student-level scores are then built by AGGREGATING UP
from the sub-CLO level (see AGGREGATION below), instead of being computed
directly like in v1.

AGGREGATION CHOICE: course_job_score = MAX over that course's sub-CLOs'
cross_encoder_score for a given job (not mean). Rationale: a course
"prepares you" for a job if AT LEAST ONE of its sub-competencies is
strongly relevant - averaging would dilute a strong specific match with
many unrelated sub-CLOs (e.g. a database course has sub-CLOs on both
"SQL query design" AND "ER diagram basics" AND "transaction theory" -
a Data Analyst job matching strongly on the SQL sub-CLO shouldn't be
punished for not matching the transaction-theory sub-CLO). Both MAX and
MEAN are computed and saved, so you can show your advisor the comparison
and justify whichever they prefer.

*** SCOPE NOTE ***
Sub-CLO data currently covers 54 courses (47 from ITS_SI_BRIN, 7 from
TeluSurabaya) out of the full SI course catalog - all from the Sistem
Informasi program, not the student's actual Sains Data program (documented
placeholder limitation from earlier in the project). Courses in the KHS
that don't fuzzy-match any of these 54 will simply be excluded (visible in
the course_match_log output) rather than silently ignored.

REQUIREMENTS (run on your machine - GPU recommended):
  pip install sentence-transformers pandas --break-system-packages

INPUT FILES needed in the same folder:
  - sub_clo_profiles.csv
  - jobs_unified_with_skills.csv
  - skill_vocabulary.py
  - your KHS csv (kode_mk,nama_mk,sks,nilai_huruf)
  - your CV as a .txt file

USAGE:
  python full_pipeline_subclo.py --khs transcript_akmal.csv --cv cv_akmal.txt

OUTPUTS:
  - sub_clo_job_ranking.csv     <- THE key deliverable: per sub-CLO, ranked jobs
  - course_job_aggregated.csv   <- sub-CLO scores rolled up to course level (MAX and MEAN)
  - final_recommendations.csv   <- course scores rolled up to student level + CV fusion
  - pipeline_course_match_log.csv
"""

import argparse
import json
import pandas as pd
import numpy as np
from difflib import SequenceMatcher
from collections import defaultdict
from sentence_transformers import SentenceTransformer, CrossEncoder
from skill_vocabulary import SKILL_VOCAB

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
SBERT_MODEL = "intfloat/multilingual-e5-large"
CROSS_ENCODER_MODEL = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
MATCH_THRESHOLD = 0.55       # course-name fuzzy match confidence cutoff
TOP_K_RETRIEVAL = 15         # SBERT top-K per sub-CLO, before rerank
TOP_K_PER_SUBCLO = 5         # jobs kept per sub-CLO after rerank
FUSION_WEIGHT = 1.5          # weight of CV-skill-overlap bonus
TOP_N_OUTPUT = 15            # final recommendations to output

GRADE_MAP = {"A": 0.85, "AB": 0.80, "B": 0.70, "BC": 0.60, "C": 0.55, "D": 0.50, "E": 0.0}


# ---------------------------------------------------------------------------
# STAGE 1: parse KHS
# ---------------------------------------------------------------------------
def load_khs(path):
    df = pd.read_csv(path)
    df["grade_weight"] = df["nilai_huruf"].str.upper().map(GRADE_MAP)
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
    """subclo_courses: list of unique course_name values in sub_clo_profiles.csv"""
    rows = []
    for _, k in khs.iterrows():
        best_score, best_name = 0, None
        for course_name in subclo_courses:
            s = similarity(k["nama_mk"], course_name)
            if s > best_score:
                best_score, best_name = s, course_name
        rows.append({
            "khs_course": k["nama_mk"],
            "grade_weight": k["grade_weight"],
            "matched_course_name": best_name,
            "match_confidence": round(best_score, 3),
        })
    df = pd.DataFrame(rows)
    df["included"] = df["match_confidence"] >= MATCH_THRESHOLD
    return df


# ---------------------------------------------------------------------------
# STAGE 3: extract CV skills (dictionary matcher)
# ---------------------------------------------------------------------------
def extract_cv_skills(cv_text):
    cv_lower = cv_text.lower()
    found = set()
    for canonical, info in SKILL_VOCAB.items():
        for alias in info["aliases"] + [canonical]:
            if alias.lower() in cv_lower:
                found.add(canonical)
                break
    return sorted(found)


# ---------------------------------------------------------------------------
# STAGE 4: per-sub-CLO SBERT retrieval + cross-encoder rerank
# ---------------------------------------------------------------------------
def rank_jobs_per_subclo(matched_courses, subclo_profiles, jobs, sbert_model, cross_encoder):
    job_texts = ("passage: " + jobs["title"].fillna("") + ". "
                 + jobs["description"].fillna("").str.slice(0, 1500))
    print(f"Embedding {len(jobs)} job postings with SBERT (one-time cost)...")
    job_emb = sbert_model.encode(job_texts.tolist(), normalize_embeddings=True,
                                  show_progress_bar=True, batch_size=32)

    included_course_names = matched_courses[matched_courses["included"]]["matched_course_name"].unique()
    relevant_subclos = subclo_profiles[subclo_profiles["course_name"].isin(included_course_names)]
    print(f"\nProcessing {len(relevant_subclos)} sub-CLOs across {len(included_course_names)} matched courses...")

    all_rows = []
    for i, (_, sc) in enumerate(relevant_subclos.iterrows()):
        query_text = "query: " + str(sc["sub_clo_text"])
        q_emb = sbert_model.encode([query_text], normalize_embeddings=True)[0]

        sims = job_emb @ q_emb
        top_idx = np.argsort(-sims)[:TOP_K_RETRIEVAL]

        pairs = [(str(sc["sub_clo_text"])[:1500],
                  str(jobs.iloc[j]["title"]) + ". " + str(jobs.iloc[j]["description"])[:1500])
                 for j in top_idx]
        ce_scores = cross_encoder.predict(pairs, batch_size=16)

        sub_jobs = jobs.iloc[top_idx].copy()
        sub_jobs["cross_encoder_score"] = ce_scores
        sub_jobs = sub_jobs.sort_values("cross_encoder_score", ascending=False).head(TOP_K_PER_SUBCLO)

        for rank, (_, jr) in enumerate(sub_jobs.iterrows(), start=1):
            all_rows.append({
                "course_name": sc["course_name"],
                "sub_clo_code": sc["sub_clo_code"],
                "sub_clo_text": str(sc["sub_clo_text"])[:150],
                "rank": rank,
                "job_id": jr["job_id"],
                "job_title": jr["title"],
                "job_company": jr["company"],
                "job_source": jr["source"],
                "cross_encoder_score": round(float(jr["cross_encoder_score"]), 4),
                "matched_skills": jr["matched_skills"],
            })

        if (i + 1) % 10 == 0:
            print(f"  processed {i+1}/{len(relevant_subclos)} sub-CLOs...")

    return pd.DataFrame(all_rows)


# ---------------------------------------------------------------------------
# STAGE 5: aggregate sub-CLO scores -> course-level scores
# ---------------------------------------------------------------------------
def aggregate_to_course_level(subclo_ranking):
    agg = (subclo_ranking.groupby(["course_name", "job_id", "job_title", "job_company", "job_source"])
           .agg(course_job_score_max=("cross_encoder_score", "max"),
                course_job_score_mean=("cross_encoder_score", "mean"),
                n_subclo_matched=("sub_clo_code", "count"),
                best_subclo=("sub_clo_code", lambda x: x.iloc[
                    subclo_ranking.loc[x.index, "cross_encoder_score"].values.argmax()]))
           .reset_index())
    return agg


# ---------------------------------------------------------------------------
# STAGE 6: aggregate course-level -> student-level, + CV fusion bonus
# ---------------------------------------------------------------------------
def aggregate_to_student_level(matched_courses, course_agg, cv_skills, jobs):
    cv_skill_set = set(cv_skills)
    job_scores = defaultdict(float)
    job_info = {}
    job_explanations = defaultdict(list)

    included = matched_courses[matched_courses["included"]]

    for _, m in included.iterrows():
        weight = m["grade_weight"] * m["match_confidence"]
        course_jobs = course_agg[course_agg["course_name"] == m["matched_course_name"]]

        for _, cj in course_jobs.iterrows():
            job_id = cj["job_id"]
            contribution = weight * cj["course_job_score_max"]  # using MAX aggregation
            job_scores[job_id] += contribution
            job_explanations[job_id].append(
                f"'{m['khs_course']}' (nilai_bobot={m['grade_weight']:.2f}, match={m['match_confidence']:.2f}) "
                f"via sub-CLO terbaik '{cj['best_subclo']}' -> skor={cj['course_job_score_max']:.2f}"
            )
            if job_id not in job_info:
                job_info[job_id] = {
                    "job_title": cj["job_title"],
                    "job_company": cj["job_company"],
                    "job_source": cj["job_source"],
                }

    # CV fusion bonus
    jobs_indexed = jobs.set_index("job_id")
    for job_id in list(job_info.keys()):
        try:
            job_skills = json.loads(jobs_indexed.loc[job_id, "matched_skills"])
        except (KeyError, TypeError, json.JSONDecodeError):
            job_skills = []
        overlap = cv_skill_set & set(job_skills)
        if overlap:
            bonus = FUSION_WEIGHT * len(overlap)
            job_scores[job_id] += bonus
            job_explanations[job_id].append(f"CV skill match (+{bonus:.2f}): {', '.join(sorted(overlap))}")

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
    parser.add_argument("--khs", required=True)
    parser.add_argument("--cv", required=True)
    args = parser.parse_args()

    print("=== Stage 1-2: KHS parsing + course matching ===")
    khs = load_khs(args.khs)
    subclo_profiles = pd.read_csv("sub_clo_profiles.csv")
    available_courses = subclo_profiles["course_name"].unique().tolist()
    matched = match_courses(khs, available_courses)
    matched.to_csv("pipeline_course_match_log.csv", index=False)
    print(matched[["khs_course", "matched_course_name", "match_confidence", "included"]].to_string(index=False))
    n_included = matched["included"].sum()
    print(f"\n{n_included}/{len(matched)} KHS courses matched (confidence >= {MATCH_THRESHOLD})")
    if n_included == 0:
        print("No usable matches - stopping.")
        return

    print("\n=== Stage 3: CV skill extraction ===")
    with open(args.cv, "r", encoding="utf-8") as f:
        cv_text = f.read()
    cv_skills = extract_cv_skills(cv_text)
    print(f"CV skills: {cv_skills}")

    print("\n=== Stage 4: Per-sub-CLO SBERT retrieval + cross-encoder rerank ===")
    jobs = pd.read_csv("jobs_unified_with_skills.csv")
    sbert_model = SentenceTransformer(SBERT_MODEL)
    cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL)
    subclo_ranking = rank_jobs_per_subclo(matched, subclo_profiles, jobs, sbert_model, cross_encoder)
    subclo_ranking.to_csv("sub_clo_job_ranking.csv", index=False)
    print(f"Saved: sub_clo_job_ranking.csv ({len(subclo_ranking)} rows)")

    print("\n=== Stage 5: Aggregating sub-CLO -> course level ===")
    course_agg = aggregate_to_course_level(subclo_ranking)
    course_agg.to_csv("course_job_aggregated.csv", index=False)
    print(f"Saved: course_job_aggregated.csv ({len(course_agg)} rows)")

    print("\n=== Stage 6: Aggregating course -> student level + CV fusion ===")
    final_ranking = aggregate_to_student_level(matched, course_agg, cv_skills, jobs)
    final_ranking.head(TOP_N_OUTPUT).to_csv("final_recommendations.csv", index=False)
    print(f"Saved: final_recommendations.csv (top {TOP_N_OUTPUT})")

    print("\n--- Top 5 preview ---")
    for _, row in final_ranking.head(5).iterrows():
        print(f"\n[{row['final_score']}] {row['job_title']} @ {row['job_company']}")
        print(f"   why: {row['explanation']}")


if __name__ == "__main__":
    main()