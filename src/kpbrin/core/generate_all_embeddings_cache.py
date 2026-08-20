# -*- coding: utf-8 -*-
"""
Incremental, checkpointed, high-performance SBERT embedding generator for KP BRIN.
Embeds:
1. All 4,570 jobs (reusing existing 2,102 embeddings + encoding 2,468 new jobs)
2. All 97 academic course CLO profiles
3. Online course catalog
"""

import os
import sys
import time
import hashlib
import json
import torch
import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

ROOT_DIR = r"D:\MAIN DATA\Documents\Semester 6\KP BRIN"
SBERT_MODEL_NAME = "intfloat/multilingual-e5-large"

# Source Paths
JOBS_CSV_PATH = os.path.join(ROOT_DIR, "data", "Pekerjaan", "Processed", "jobs_unified.csv")
COURSE_CLO_PATH = os.path.join(ROOT_DIR, "data", "Mata Kuliah", "course_clo_consolidated.csv")
ONLINE_COURSES_PATH = os.path.join(ROOT_DIR, "data", "Sertifikasi", "online_courses_processed.csv")

# Cache Directories
DATA_CACHE_DIR = os.path.join(ROOT_DIR, "data", ".emb_cache")
SRC_DATASET_CACHE_DIR = os.path.join(ROOT_DIR, "src", "Dataset", ".emb_cache")
CERT_CACHE_DIR = os.path.join(ROOT_DIR, "data", "Sertifikasi", ".emb_cache")
CHECKPOINT_DIR = os.path.join(DATA_CACHE_DIR, "checkpoints")

for d in [DATA_CACHE_DIR, SRC_DATASET_CACHE_DIR, CERT_CACHE_DIR, CHECKPOINT_DIR]:
    os.makedirs(d, exist_ok=True)

OLD_EMB_PATH = os.path.join(DATA_CACHE_DIR, "job_emb_73cf5f3dc24e85ed133aa28745ce51a4.npy")


def file_hash(path: str, chunk_size: int = 1 << 20) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def save_to_locations(filename, data_obj, is_numpy=True, meta_content=None, meta_filename=None, target_dirs=None):
    if target_dirs is None:
        target_dirs = [DATA_CACHE_DIR, SRC_DATASET_CACHE_DIR]
    for d in target_dirs:
        os.makedirs(d, exist_ok=True)
        dest_file = os.path.join(d, filename)
        if is_numpy:
            np.save(dest_file, data_obj)
        if meta_content and meta_filename:
            dest_meta = os.path.join(d, meta_filename)
            with open(dest_meta, "w", encoding="utf-8") as f:
                f.write(meta_content)
        print(f"    [SAVED] -> {dest_file}", flush=True)


def main():
    total_start = time.time()
    print("=" * 80, flush=True)
    print("MEMULAI GENERASI CACHE EMBEDDING UNTUK JOBS & MATA KULIAH", flush=True)
    print("=" * 80, flush=True)

    # 1. Load SBERT Model
    print("\n[Step 1/4] Memuat model SBERT (intfloat/multilingual-e5-large)...", flush=True)
    t0 = time.time()
    from sentence_transformers import SentenceTransformer
    torch.set_num_threads(os.cpu_count() or 8)
    sbert = SentenceTransformer(SBERT_MODEL_NAME, local_files_only=True)
    sbert.max_seq_length = 256
    print(f"  [OK] SBERT Model siap dalam {time.time() - t0:.2f} detik (max_seq_length=256).\n", flush=True)

    # 2. Course CLO Embeddings Cache (97 courses)
    print("[Step 2/4] Menghitung Embedding Mata Kuliah / CLO (course_clo_consolidated.csv)...", flush=True)
    if os.path.exists(COURSE_CLO_PATH):
        clo_df = pd.read_csv(COURSE_CLO_PATH)
        clo_hash = file_hash(COURSE_CLO_PATH)
        n_courses = len(clo_df)
        print(f"  - Total mata kuliah : {n_courses}")
        print(f"  - MD5 Hash file     : {clo_hash}")

        clo_texts = [
            "query: " + str(t) for t in clo_df["consolidated_clo_text"].fillna("").tolist()
        ]
        t0 = time.time()
        course_embs = sbert.encode(
            clo_texts,
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=32,
        )
        print(f"  [OK] Selesai encoding CLO dalam {time.time() - t0:.2f} detik (Shape: {course_embs.shape})", flush=True)

        clo_emb_filename = f"course_emb_{clo_hash}.npy"
        clo_meta_filename = f"course_emb_{clo_hash}.meta"
        clo_meta_content = f"course_clo_path={COURSE_CLO_PATH}\nhash={clo_hash}\nn_courses={n_courses}\n"

        print("  - Menyimpan cache CLO ke direktori...", flush=True)
        save_to_locations(
            filename=clo_emb_filename,
            data_obj=course_embs,
            is_numpy=True,
            meta_content=clo_meta_content,
            meta_filename=clo_meta_filename,
            target_dirs=[DATA_CACHE_DIR, SRC_DATASET_CACHE_DIR]
        )
    else:
        print(f"  [SKIP] File {COURSE_CLO_PATH} tidak ditemukan.")

    # 3. Online Courses / Sertifikasi Embeddings Cache (1,139 courses)
    print("\n[Step 3/4] Memastikan Embedding Katalog Online Courses / Sertifikasi...", flush=True)
    if os.path.exists(ONLINE_COURSES_PATH):
        import scipy.sparse as sp
        import joblib
        from sklearn.feature_extraction.text import TfidfVectorizer

        df_online = pd.read_csv(ONLINE_COURSES_PATH)
        n_online = len(df_online)
        print(f"  - Total online courses : {n_online}")

        # TF-IDF
        vec = TfidfVectorizer(stop_words="english", max_features=5000, sublinear_tf=True)
        mat = vec.fit_transform(df_online["full_text"].fillna(""))
        sp.save_npz(os.path.join(CERT_CACHE_DIR, "course_tfidf_matrix.npz"), mat)
        joblib.dump(vec, os.path.join(CERT_CACHE_DIR, "course_tfidf_vectorizer.pkl"))
        print(f"  [OK] TF-IDF Matrix & Vectorizer tersimpan di {CERT_CACHE_DIR}", flush=True)

        # SBERT Embeddings
        online_texts = []
        for _, row in df_online.iterrows():
            c_name = str(row.get("course_name", "")).strip()
            platform = str(row.get("platform", "")).strip()
            level = str(row.get("level", "Beginner")).strip()
            skills = str(row.get("skills_text", "")).strip()
            text = f"passage: {c_name} by {platform} ({level}). Skills: {skills}"
            online_texts.append(text)

        t0 = time.time()
        online_embs = sbert.encode(
            online_texts,
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=32,
        )
        online_emb_path = os.path.join(CERT_CACHE_DIR, "course_sbert_emb.npy")
        np.save(online_emb_path, online_embs)
        print(f"  [OK] Online course SBERT embeddings ({online_embs.shape}) tersimpan dalam {time.time() - t0:.2f} detik.", flush=True)

    # 4. Job Embeddings Cache (4,570 jobs with Incremental Encoding)
    print("\n[Step 4/4] Menghitung Embedding Pekerjaan (jobs_unified.csv)...", flush=True)
    if not os.path.exists(JOBS_CSV_PATH):
        raise FileNotFoundError(f"File jobs_unified.csv tidak ditemukan di {JOBS_CSV_PATH}")

    jobs_df = pd.read_csv(JOBS_CSV_PATH)
    jobs_hash = file_hash(JOBS_CSV_PATH)
    n_jobs = len(jobs_df)
    print(f"  - Total pekerjaan : {n_jobs}")
    print(f"  - MD5 Hash file   : {jobs_hash}")

    desc_col = "description_summary" if "description_summary" in jobs_df.columns else "description"
    job_texts = (
        "passage: " +
        jobs_df["title"].fillna("") + ". " +
        jobs_df[desc_col].fillna("").astype(str).str.slice(0, 1500)
    ).tolist()

    # Cek apakah ada base embedding (2102 data lama)
    has_base = os.path.exists(OLD_EMB_PATH)
    if has_base:
        old_embs = np.load(OLD_EMB_PATH)
        n_old = len(old_embs)
        print(f"  - [REUSE] Memuat {n_old} embedding lama dari {os.path.basename(OLD_EMB_PATH)}...")
    else:
        old_embs = None
        n_old = 0

    checkpoint_file = os.path.join(CHECKPOINT_DIR, f"new_jobs_emb_{jobs_hash}.npy")
    if os.path.exists(checkpoint_file):
        new_embs = np.load(checkpoint_file)
        print(f"  - [CHECKPOINT] Melanjutkan dari checkpoint: {len(new_embs)} data baru sudah dihitung.", flush=True)
        start_idx = n_old + len(new_embs)
    else:
        new_embs_list = []
        start_idx = n_old

    if start_idx < n_jobs:
        remaining_texts = job_texts[start_idx:]
        print(f"  - Meng-encode {len(remaining_texts)} lowongan baru (dari indeks {start_idx} ke {n_jobs})...", flush=True)
        
        chunk_size = 200
        total_chunks = (len(remaining_texts) + chunk_size - 1) // chunk_size
        collected_embs = [new_embs] if os.path.exists(checkpoint_file) else []

        t_job_start = time.time()
        for c_idx in range(total_chunks):
            c_start = c_idx * chunk_size
            c_end = min(c_start + chunk_size, len(remaining_texts))
            chunk_texts = remaining_texts[c_start:c_end]
            
            t_chunk = time.time()
            chunk_embs = sbert.encode(
                chunk_texts,
                normalize_embeddings=True,
                show_progress_bar=False,
                batch_size=32,
            )
            collected_embs.append(chunk_embs)
            
            # Save checkpoint
            current_new = np.vstack(collected_embs)
            np.save(checkpoint_file, current_new)
            
            elapsed = time.time() - t_job_start
            done_count = start_idx + c_end
            pct = (done_count / n_jobs) * 100
            print(f"    Chunk {c_idx+1}/{total_chunks} ({len(chunk_texts)} jobs) selesai dalam {time.time()-t_chunk:.2f}s | Progress: {done_count}/{n_jobs} ({pct:.1f}%)", flush=True)

        final_new_embs = np.vstack(collected_embs)
    else:
        final_new_embs = new_embs

    # Gabungkan base (2102) + new (2468) -> (4570, 1024)
    if old_embs is not None and len(old_embs) > 0:
        all_job_embs = np.vstack([old_embs, final_new_embs])
    else:
        all_job_embs = final_new_embs

    print(f"\n  [OK] Seluruh job embeddings lengkap! Shape akhir: {all_job_embs.shape}", flush=True)

    job_emb_filename = f"job_emb_{jobs_hash}.npy"
    job_meta_filename = f"job_emb_{jobs_hash}.meta"
    job_meta_content = f"jobs_path={JOBS_CSV_PATH}\nhash={jobs_hash}\nn_jobs={n_jobs}\n"

    print("  - Menyimpan cache file pekerjaan ke direktori...", flush=True)
    save_to_locations(
        filename=job_emb_filename,
        data_obj=all_job_embs,
        is_numpy=True,
        meta_content=job_meta_content,
        meta_filename=job_meta_filename,
        target_dirs=[DATA_CACHE_DIR, SRC_DATASET_CACHE_DIR]
    )

    # Cleanup checkpoint jika sudah sukses
    if os.path.exists(checkpoint_file):
        try:
            os.remove(checkpoint_file)
        except Exception:
            pass

    print("\n" + "=" * 80, flush=True)
    print(f"[DONE] SEMUA CACHE EMBEDDING BERHASIL DIPERBARUI! (Total Waktu: {time.time() - total_start:.2f} detik)", flush=True)
    print("=" * 80, flush=True)


if __name__ == "__main__":
    main()
