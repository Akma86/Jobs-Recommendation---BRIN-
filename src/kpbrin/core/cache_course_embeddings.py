# -*- coding: utf-8 -*-
"""
Cache pre-computed SBERT and TF-IDF embeddings for the 1,139 Online Courses dataset.
"""

import os
import sys
import numpy as np
import pandas as pd
import scipy.sparse as sp
import joblib
from sentence_transformers import SentenceTransformer

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from kpbrin.xai.course_catalog import load_and_preprocess_catalog, get_course_vectorizer
from kpbrin.core.full_pipeline import SBERT_MODEL

def main():
    cert_dir = os.path.join(ROOT_DIR, "data", "Sertifikasi")
    cache_dir = os.path.join(cert_dir, ".emb_cache")
    os.makedirs(cache_dir, exist_ok=True)

    print(">>> Loading Online Course Catalog (1,139 courses)...")
    catalog = load_and_preprocess_catalog()
    print(f"    Loaded {len(catalog)} online courses.")

    # 1. Cache TF-IDF
    vec, mat = get_course_vectorizer()
    tfidf_mat_path = os.path.join(cache_dir, "course_tfidf_matrix.npz")
    tfidf_vec_path = os.path.join(cache_dir, "course_tfidf_vectorizer.pkl")
    sp.save_npz(tfidf_mat_path, mat)
    joblib.dump(vec, tfidf_vec_path)
    print(f"    [SAVED] TF-IDF Matrix & Vectorizer -> {cache_dir}")

    # 2. Compute & Cache SBERT Dense Embeddings
    print(">>> Computing SBERT embeddings for 1,139 online courses...")
    sbert = SentenceTransformer(SBERT_MODEL)
    
    course_texts = []
    for _, row in catalog.iterrows():
        c_name = str(row.get("course_name", "")).strip()
        platform = str(row.get("platform", "")).strip()
        level = str(row.get("level", "Beginner")).strip()
        skills = str(row.get("skills_text", "")).strip()
        text = f"passage: {c_name} by {platform} ({level}). Skills: {skills}"
        course_texts.append(text)
        
    course_embs = sbert.encode(course_texts, normalize_embeddings=True, show_progress_bar=False)
    emb_path = os.path.join(cache_dir, "course_sbert_emb.npy")
    np.save(emb_path, course_embs)
    print(f"    [SAVED] SBERT Embeddings -> {emb_path} (Shape: {course_embs.shape})")
    print(">>> ALL COURSE CACHES GENERATED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
