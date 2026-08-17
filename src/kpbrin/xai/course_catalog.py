# -*- coding: utf-8 -*-
"""
Course Catalog Loader & Dynamic Matcher for XAI DiCE Counterfactuals
===================================================================
Loads Online Course dataset from Excel/Parquet/CSV, computes platform credibility tiers,
level weights, and dynamically matches relevant online courses to target job postings.
"""

import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from kpbrin.core.issuer_tiers import get_issuer_weight

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
EXCEL_CATALOG_PATH = os.path.join(ROOT_DIR, "data", "Sertifikasi", "Online_Course_clean.xlsx")
PROCESSED_CSV_PATH = os.path.join(ROOT_DIR, "data", "Sertifikasi", "online_courses_processed.csv")
JOBS_CSV_PATH = os.path.join(ROOT_DIR, "data", "Pekerjaan", "Processed", "jobs_unified.csv")

LEVEL_WEIGHTS = {
    "beginner": 0.70,
    "intermediate": 0.85,
    "advanced": 1.00,
    "mixed": 0.80,
    "course": 0.75,
    "specialization": 0.95,
    "degree": 1.00,
}

LEVEL_EFFORTS = {
    "beginner": 2.5,
    "intermediate": 4.0,
    "advanced": 6.0,
    "mixed": 3.5,
    "course": 3.0,
    "specialization": 7.5,
    "degree": 9.0,
}

_CATALOG_CACHE = None
_VECTORIZER_CACHE = None
_MATRIX_CACHE = None
_JOBS_LOOKUP = None


def load_and_preprocess_catalog(force_reload=False):
    """
    Load Online Course dataset from preprocessed CSV if available, else from Excel.
    """
    global _CATALOG_CACHE
    if _CATALOG_CACHE is not None and not force_reload:
        return _CATALOG_CACHE

    if os.path.exists(PROCESSED_CSV_PATH) and not force_reload:
        df_course = pd.read_csv(PROCESSED_CSV_PATH)
    else:
        print(f"[INFO] Loading online course catalog from Excel: {EXCEL_CATALOG_PATH}")
        df_course = pd.read_excel(EXCEL_CATALOG_PATH, sheet_name="Course", header=1)
        df_skill = pd.read_excel(EXCEL_CATALOG_PATH, sheet_name="CourseSkill", header=1)

        # Aggregate skills per course
        skills_by_course = (
            df_skill.groupby("course_id")["normalized_skill"]
            .apply(lambda s: ", ".join(sorted(set(str(x) for x in s.dropna()))))
            .to_dict()
        )
        df_course["skills_text"] = df_course["course_id"].map(skills_by_course).fillna("")

        # Standardize columns
        df_course["course_name"] = df_course["course_name"].fillna("").astype(str).str.strip()
        df_course["platform"] = df_course["platform"].fillna("Unknown").astype(str).str.strip()
        df_course["level"] = df_course["level"].fillna("Beginner").astype(str).str.strip()

        # Compute tier weight
        tier_weights, tier_reasons = [], []
        for p in df_course["platform"]:
            w, r = get_issuer_weight(p)
            tier_weights.append(w)
            tier_reasons.append(r)
        df_course["tier_weight"] = tier_weights
        df_course["tier_reason"] = tier_reasons

        # Compute level weight & effort
        df_course["level_weight"] = df_course["level"].str.lower().map(LEVEL_WEIGHTS).fillna(0.75)
        df_course["effort"] = df_course["level"].str.lower().map(LEVEL_EFFORTS).fillna(3.5)

        # Full text representation for similarity matching
        df_course["full_text"] = (
            df_course["course_name"]
            + " "
            + df_course["platform"]
            + " "
            + df_course["level"]
            + " "
            + df_course["skills_text"]
        )

        df_course.to_csv(PROCESSED_CSV_PATH, index=False)
        print(f"[INFO] Cached processed course catalog to: {PROCESSED_CSV_PATH} ({len(df_course)} courses)")

    _CATALOG_CACHE = df_course
    return _CATALOG_CACHE


def get_course_vectorizer():
    """
    Get or fit TF-IDF vectorizer over course catalog texts (uses disk cache if available).
    """
    global _VECTORIZER_CACHE, _MATRIX_CACHE
    if _VECTORIZER_CACHE is not None and _MATRIX_CACHE is not None:
        return _VECTORIZER_CACHE, _MATRIX_CACHE

    cache_dir = os.path.join(ROOT_DIR, "data", "Sertifikasi", ".emb_cache")
    mat_path = os.path.join(cache_dir, "course_tfidf_matrix.npz")
    vec_path = os.path.join(cache_dir, "course_tfidf_vectorizer.pkl")

    if os.path.exists(mat_path) and os.path.exists(vec_path):
        import scipy.sparse as sp
        import joblib
        _MATRIX_CACHE = sp.load_npz(mat_path)
        _VECTORIZER_CACHE = joblib.load(vec_path)
        return _VECTORIZER_CACHE, _MATRIX_CACHE

    catalog = load_and_preprocess_catalog()
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000, sublinear_tf=True)
    matrix = vectorizer.fit_transform(catalog["full_text"])
    _VECTORIZER_CACHE = vectorizer
    _MATRIX_CACHE = matrix
    return _VECTORIZER_CACHE, _MATRIX_CACHE


def get_job_lookup():
    """
    Get dictionary mapping job_id to job text representation.
    """
    global _JOBS_LOOKUP
    if _JOBS_LOOKUP is not None:
        return _JOBS_LOOKUP

    if os.path.exists(JOBS_CSV_PATH):
        df_jobs = pd.read_csv(JOBS_CSV_PATH)
        df_jobs["combined_text"] = (
            df_jobs["title"].fillna("")
            + " "
            + df_jobs["company"].fillna("")
            + " "
            + df_jobs["matched_skills"].fillna("")
            + " "
            + df_jobs["description"].fillna("")
        )
        _JOBS_LOOKUP = dict(zip(df_jobs["job_id"], df_jobs["combined_text"]))
    else:
        _JOBS_LOOKUP = {}
    return _JOBS_LOOKUP


def find_top_candidate_courses_for_job(job_id, job_title="", top_n=8, min_sim=0.10):
    """
    Find top N relevant online courses for a specific job using dynamic similarity matching,
    platform tier weights, and level multipliers.

    Returns
    -------
    list of dict:
        course_id, course_name, platform, level, similarity, tier_weight, level_weight,
        score_delta, effort
    """
    catalog = load_and_preprocess_catalog()
    vectorizer, matrix = get_course_vectorizer()
    jobs_lookup = get_job_lookup()

    target_text = jobs_lookup.get(job_id, job_title)
    if not target_text:
        target_text = job_title

    job_vec = vectorizer.transform([target_text])
    sims = cosine_similarity(job_vec, matrix)[0]

    # Calculate dynamic score delta: tier_weight * level_weight * sim * scaling_factor
    scaling_factor = 3.5  # maps top cert match to ~1.5 - 3.0 point boost
    score_deltas = catalog["tier_weight"].values * catalog["level_weight"].values * sims * scaling_factor

    top_indices = np.argsort(score_deltas)[::-1]

    results = []
    seen_names = set()
    for idx in top_indices:
        sim = sims[idx]
        if sim < min_sim:
            continue
        c = catalog.iloc[idx]
        c_name = c["course_name"]
        if c_name in seen_names:
            continue
        seen_names.add(c_name)

        delta = round(float(score_deltas[idx]), 4)
        if delta <= 0.1:
            continue

        results.append({
            "course_id": c["course_id"],
            "course_name": c_name,
            "platform": c["platform"],
            "level": c["level"],
            "skills_text": c["skills_text"],
            "similarity": round(float(sim), 4),
            "tier_weight": float(c["tier_weight"]),
            "level_weight": float(c["level_weight"]),
            "score_delta": delta,
            "effort": float(c["effort"]),
        })

        if len(results) >= top_n:
            break

    return results
