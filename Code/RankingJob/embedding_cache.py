# -*- coding: utf-8 -*-
"""
EMBEDDING CACHE - Modul untuk menyimpan dan memuat embedding secara efisien.

Memisahkan logika caching dari pipeline utama agar modular dan bisa dipakai
oleh file lain (misalnya skill_gap_analysis.py atau skrip evaluasi lainnya).

Cara Kerja:
  - Setiap file CSV (jobs, course CLO) di-hash menggunakan MD5.
  - Hash ini digunakan sebagai nama file cache (.npy).
  - Jika cache ada dan hashnya cocok (artinya dataset tidak berubah),
    embedding langsung dimuat dari disk tanpa menghitung ulang.
  - Jika cache tidak ada atau file dataset berubah, embedding dihitung ulang
    lalu disimpan ke cache untuk run berikutnya.

Catatan: Model SBERT harus sudah di-load di luar modul ini dan dioper
ke fungsi-fungsi yang ada di sini, agar model tidak di-load dua kali
jika ada beberapa komponen yang membutuhkannya.
"""

import hashlib
import os

import numpy as np
import pandas as pd

DEFAULT_CACHE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "Dataset", ".emb_cache"
)


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------
def file_hash(path: str, chunk_size: int = 1 << 20) -> str:
    """Hitung MD5 hash dari isi file - dipakai sebagai cache key."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Job Embeddings Cache
# ---------------------------------------------------------------------------
def load_job_embeddings(
    jobs: pd.DataFrame,
    jobs_path: str,
    sbert_model,
    desc_col: str = "description",
    cache_dir: str = DEFAULT_CACHE_DIR,
) -> np.ndarray:
    """
    Muat job embeddings dari cache jika tersedia, atau hitung ulang dan simpan.

    Parameters
    ----------
    jobs : pd.DataFrame
        DataFrame pekerjaan (jobs_unified.csv yang sudah dibaca).
    jobs_path : str
        Path asli ke file jobs_unified.csv - dipakai sebagai kunci cache.
    sbert_model : SentenceTransformer
        Model SBERT yang sudah di-load (jangan load ulang di sini).
    desc_col : str
        Nama kolom deskripsi di jobs DataFrame.
    cache_dir : str
        Direktori untuk menyimpan file cache .npy.

    Returns
    -------
    np.ndarray
        Matrix embedding (n_jobs x embedding_dim), sudah ternormalisasi.
    """
    os.makedirs(cache_dir, exist_ok=True)
    fhash = file_hash(jobs_path)
    cache_emb  = os.path.join(cache_dir, f"job_emb_{fhash}.npy")
    cache_meta = os.path.join(cache_dir, f"job_emb_{fhash}.meta")

    if os.path.exists(cache_emb) and os.path.exists(cache_meta):
        print(f"  [CACHE HIT] Memuat job embeddings dari cache...")
        return np.load(cache_emb)

    print(f"  [CACHE MISS] Menghitung embedding {len(jobs)} pekerjaan, lalu disimpan ke cache...")
    job_texts = (
        "passage: " +
        jobs["title"].fillna("") + ". " +
        jobs[desc_col].fillna("").str.slice(0, 1500)
    )
    job_emb = sbert_model.encode(
        job_texts.tolist(),
        normalize_embeddings=True,
        show_progress_bar=True,
        batch_size=32,
    )
    np.save(cache_emb, job_emb)
    with open(cache_meta, "w", encoding="utf-8") as f:
        f.write(f"jobs_path={jobs_path}\nhash={fhash}\nn_jobs={len(jobs)}\n")
    print(f"  Cache disimpan: {cache_emb}")
    return job_emb


# ---------------------------------------------------------------------------
# Course CLO Embeddings Cache (opsional - 22 course biasanya cepat)
# ---------------------------------------------------------------------------
def load_course_embeddings(
    course_texts: list,
    course_clo_path: str,
    sbert_model,
    prefix: str = "query: ",
    cache_dir: str = DEFAULT_CACHE_DIR,
) -> np.ndarray:
    """
    Muat course CLO embeddings dari cache jika tersedia.
    Berguna jika Anda punya banyak mahasiswa yang semuanya melewati 22 mata kuliah yang sama.

    Parameters
    ----------
    course_texts : list of str
        Teks CLO per mata kuliah (sudah diambil dari course_clo_consolidated.csv).
    course_clo_path : str
        Path asli ke file course_clo_consolidated.csv - untuk kunci cache.
    sbert_model : SentenceTransformer
        Model SBERT yang sudah di-load.
    prefix : str
        Prefix yang ditambahkan ke setiap teks (biasanya "query: ").
    cache_dir : str
        Direktori untuk menyimpan file cache .npy.

    Returns
    -------
    np.ndarray
        Matrix embedding (n_courses x embedding_dim), sudah ternormalisasi.
    """
    os.makedirs(cache_dir, exist_ok=True)
    fhash = file_hash(course_clo_path)
    cache_emb  = os.path.join(cache_dir, f"course_emb_{fhash}.npy")
    cache_meta = os.path.join(cache_dir, f"course_emb_{fhash}.meta")

    if os.path.exists(cache_emb) and os.path.exists(cache_meta):
        print(f"  [CACHE HIT] Memuat course CLO embeddings dari cache...")
        return np.load(cache_emb)

    print(f"  [CACHE MISS] Menghitung embedding {len(course_texts)} course CLO...")
    prefixed = [prefix + t for t in course_texts]
    course_emb = sbert_model.encode(
        prefixed,
        normalize_embeddings=True,
        show_progress_bar=False,
        batch_size=32,
    )
    np.save(cache_emb, course_emb)
    with open(cache_meta, "w", encoding="utf-8") as f:
        f.write(f"course_clo_path={course_clo_path}\nhash={fhash}\nn_courses={len(course_texts)}\n")
    print(f"  Cache disimpan: {cache_emb}")
    return course_emb


# ---------------------------------------------------------------------------
# CLI - Precompute embeddings tanpa harus menjalankan pipeline lengkap
# ---------------------------------------------------------------------------
def main():
    """
    Jalankan file ini secara langsung untuk pre-compute dan menyimpan embedding
    ke cache sebelum menjalankan pipeline pertama kali.

    Usage:
        python embedding_cache.py --jobs "path/to/jobs_unified.csv" \\
                                  --course_clo "path/to/course_clo_consolidated.csv"
    """
    import argparse
    from sentence_transformers import SentenceTransformer

    SBERT_MODEL = "intfloat/multilingual-e5-large"

    parser = argparse.ArgumentParser(description="Pre-compute dan simpan embeddings ke cache")
    parser.add_argument("--jobs",       required=True, help="Path ke jobs_unified.csv")
    parser.add_argument("--course_clo", required=True, help="Path ke course_clo_consolidated.csv")
    parser.add_argument("--cache_dir",  default=DEFAULT_CACHE_DIR, help="Folder untuk menyimpan cache")
    args = parser.parse_args()

    print(f"Loading SBERT model: {SBERT_MODEL}")
    sbert_model = SentenceTransformer(SBERT_MODEL)

    # --- Job Embeddings ---
    print("\n[1/2] Job embeddings:")
    jobs = pd.read_csv(args.jobs)
    desc_col = "description_summary" if "description_summary" in jobs.columns else "description"
    load_job_embeddings(jobs, args.jobs, sbert_model, desc_col, args.cache_dir)

    # --- Course CLO Embeddings ---
    print("\n[2/2] Course CLO embeddings:")
    course_clo = pd.read_csv(args.course_clo)
    course_texts = course_clo["consolidated_clo_text"].fillna("").tolist()
    load_course_embeddings(course_texts, args.course_clo, sbert_model, cache_dir=args.cache_dir)

    print("\n[DONE] Semua embeddings sudah di-cache. Pipeline berikutnya akan berjalan jauh lebih cepat!")


if __name__ == "__main__":
    main()
