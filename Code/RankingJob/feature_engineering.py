# -*- coding: utf-8 -*-
"""
FEATURE ENGINEERING - Mengubah KHS + Sertifikasi menjadi vektor fitur terstruktur
untuk keperluan XAI (SHAP domain-level dan DICE counterfactual).

Fitur yang dihasilkan:
  - ipk                  : IPK mahasiswa (0.0 – 4.0)
  - jumlah_sertifikasi   : Total sertifikat yang dimiliki (integer)
  - data_competency      : Rata-rata bobot nilai MK domain Data (0.0 – 1.0)
  - programming_competency : Rata-rata bobot nilai MK domain Programming (0.0 – 1.0)
  - business_competency  : Rata-rata bobot nilai MK domain Business (0.0 – 1.0)
  - security_competency  : Rata-rata bobot nilai MK domain Security (0.0 – 1.0)
  - infra_competency     : Rata-rata bobot nilai MK domain Infrastruktur (0.0 – 1.0)

PEMETAAN DOMAIN:
  Dilakukan via keyword matching pada nama mata kuliah (case-insensitive).
  Setiap MK masuk ke domain yang pertama kali cocok.
"""

import argparse
import os
import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Pemetaan Domain -> Keywords pada nama MK (order matters: pertama cocok, dipakai)
# ---------------------------------------------------------------------------
DOMAIN_KEYWORDS = {
    "data": [
        "penambangan data", "data warehouse", "business intelligence",
        "sistem basis data", "basis data", "analitik", "statistik",
        "data science", "big data", "data mining",
    ],
    "programming": [
        "algoritma", "pemrograman", "pengembangan aplikasi",
        "pengembangan sistem cerdas", "kecerdasan buatan", "machine learning",
        "rekayasa perangkat lunak", "proyek perangkat lunak",
        "perancangan interaksi", "ui", "ux", "web",
    ],
    "business": [
        "pemodelan proses bisnis", "rekayasa proses bisnis",
        "manajemen proyek", "arsitektur enterprise", "analisis dan perancangan",
        "sistem informasi akuntansi", "tata kelola", "manajemen teknologi",
        "pengantar sistem informasi", "sistem enterprise",
    ],
    "security": [
        "keamanan", "security", "kriptografi", "forensik digital",
    ],
    "infra": [
        "jaringan komputer", "jaringan", "sistem operasi",
        "integrasi aplikasi", "cloud", "infrastruktur",
    ],
}


def _classify_course(course_name: str) -> str | None:
    """
    Tentukan domain dari nama mata kuliah.
    Kembalikan None jika tidak cocok ke domain manapun.
    """
    name_lower = course_name.lower()
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(kw in name_lower for kw in keywords):
            return domain
    return None


def _compute_ipk(khs_df: pd.DataFrame) -> float:
    """
    Hitung IPK dari grade_weight dan SKS.
    Jika kolom SKS tidak ada, pakai rata-rata sederhana grade_weight per MK.
    """
    # Ambil satu baris per MK (hindari duplikasi karena banyak CLO per MK)
    per_mk = khs_df.drop_duplicates(subset=["kode_mk", "nama_mk"]) if "kode_mk" in khs_df.columns \
             else khs_df.drop_duplicates(subset=["nama_mk"])

    if "sks" in per_mk.columns:
        per_mk = per_mk.copy()
        per_mk["sks"] = pd.to_numeric(per_mk["sks"], errors="coerce").fillna(3)
        # IPK = Σ(grade_weight × 4 × sks) / Σsks  → skala 4.0
        total_sks = per_mk["sks"].sum()
        if total_sks == 0:
            return 0.0
        weighted_sum = (per_mk["grade_weight"] * 4.0 * per_mk["sks"]).sum()
        return round(float(weighted_sum / total_sks), 2)
    else:
        # Fallback: rata-rata grade_weight × 4
        return round(float(per_mk["grade_weight"].mean() * 4.0), 2)


def _compute_domain_score(khs_df: pd.DataFrame, domain: str) -> float:
    """
    Rata-rata grade_weight untuk MK yang termasuk domain tertentu.
    Diperhitungkan satu nilai per MK (bukan per CLO).
    """
    # Satu baris per MK
    per_mk = khs_df.drop_duplicates(subset=["nama_mk"])
    domain_mk = per_mk[per_mk["nama_mk"].apply(lambda n: _classify_course(n) == domain)]

    if domain_mk.empty:
        return 0.0
    return round(float(domain_mk["grade_weight"].mean()), 4)


def build_student_features(
    khs_df: pd.DataFrame,
    certs_df: pd.DataFrame = None,
) -> dict:
    """
    Bangun student feature vector dari KHS dan sertifikat.

    Parameters
    ----------
    khs_df : pd.DataFrame
        transcript_parsed.csv — hasil parse_input.py
    certs_df : pd.DataFrame, optional
        certificates_parsed.csv — bisa None jika tidak ada sertifikat

    Returns
    -------
    dict: {feature_name: value}
    """
    features = {}

    # IPK
    features["ipk"] = _compute_ipk(khs_df)

    # Jumlah Sertifikasi
    if certs_df is not None and not certs_df.empty:
        features["jumlah_sertifikasi"] = int(len(certs_df))
    else:
        features["jumlah_sertifikasi"] = 0

    # Domain Competency Scores
    for domain in ["data", "programming", "business", "security", "infra"]:
        features[f"{domain}_competency"] = _compute_domain_score(khs_df, domain)

    return features


def build_student_features_from_files(khs_path: str, certs_path: str = None) -> dict:
    """Wrapper yang membaca file CSV langsung."""
    khs_df = pd.read_csv(khs_path)
    certs_df = pd.read_csv(certs_path) if certs_path and os.path.exists(certs_path) else None
    return build_student_features(khs_df, certs_df)


def features_to_dataframe(features: dict, student_name: str = "mahasiswa") -> pd.DataFrame:
    """Konversi dict fitur ke DataFrame satu baris (mudah disimpan ke CSV)."""
    row = {"student": student_name}
    row.update(features)
    return pd.DataFrame([row])


def print_feature_summary(features: dict):
    """Print ringkasan fitur ke terminal."""
    print("\n=== Student Feature Vector ===")
    print(f"  IPK                   : {features['ipk']:.2f} / 4.00")
    print(f"  Jumlah Sertifikasi    : {features['jumlah_sertifikasi']}")
    print(f"  Data Competency       : {features['data_competency']:.3f}  ({features['data_competency']*100:.1f}%)")
    print(f"  Programming Competency: {features['programming_competency']:.3f}  ({features['programming_competency']*100:.1f}%)")
    print(f"  Business Competency   : {features['business_competency']:.3f}  ({features['business_competency']*100:.1f}%)")
    print(f"  Security Competency   : {features['security_competency']:.3f}  ({features['security_competency']*100:.1f}%)")
    print(f"  Infra Competency      : {features['infra_competency']:.3f}  ({features['infra_competency']*100:.1f}%)")


# ---------------------------------------------------------------------------
# CLI standalone
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Compute student domain competency features")
    parser.add_argument("--khs",   required=True, help="transcript_parsed.csv")
    parser.add_argument("--certs", default=None,  help="certificates_parsed.csv (optional)")
    parser.add_argument("--out",   default="student_features.csv", help="Output CSV path")
    args = parser.parse_args()

    features = build_student_features_from_files(args.khs, args.certs)
    print_feature_summary(features)

    df = features_to_dataframe(features)
    df.to_csv(args.out, index=False)
    print(f"\nSaved: {args.out}")


if __name__ == "__main__":
    main()
