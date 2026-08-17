# -*- coding: utf-8 -*-
"""
Script to generate an exhaustive, publication-grade markdown summary report
for all 10 students in EKS12 Before vs After Experiment.
"""

import os
import glob
import pandas as pd
import numpy as np

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
BASE_DIR = os.path.join(ROOT_DIR, "results", "Eksperimen_XAI", "EKS12_AB_Test")
OUTPUT_MD = os.path.join(BASE_DIR, "RANGKUMAN_LENGKAP_10_MAHASISWA_EKS12.md")

STUDENTS = [
    # ML Track
    ("Siti Rahma", "ML", "Bagus (IPK ~3.82)", "Siti_Rahma_ML_Bagus"),
    ("Rizky Maulana", "ML", "Jelek (IPK ~2.03)", "Rizky_Maulana_ML_Jelek"),
    # Web Track
    ("Budi Santoso", "Web", "Bagus (IPK ~3.82)", "Budi_Santoso_Web_Bagus"),
    ("Bayu Setiawan", "Web", "Jelek (IPK ~2.03)", "Bayu_Setiawan_Web_Jelek"),
    # Net Track
    ("Andi Wijaya", "Net", "Bagus (IPK ~3.82)", "Andi_Wijaya_Net_Bagus"),
    ("Kevin Aditya", "Net", "Jelek (IPK ~2.03)", "Kevin_Aditya_Net_Jelek"),
    # SI Track
    ("Nadia Putri", "SI", "Bagus (IPK ~3.82)", "Nadia_Putri_SI_Bagus"),
    ("Farhan Hidayat", "SI", "Jelek (IPK ~2.03)", "Farhan_Hidayat_SI_Jelek"),
    # SAP Track
    ("Dewi Lestari", "SAP", "Bagus (IPK ~3.82)", "Dewi_Lestari_SAP_Bagus"),
    ("Ilham Saputra", "SAP", "Jelek (IPK ~2.03)", "Ilham_Saputra_SAP_Jelek"),
]

def format_student_section(idx, name, track, profile, folder_name):
    student_dir = os.path.join(BASE_DIR, folder_name)
    b_rec_path = os.path.join(student_dir, "Before", "recommendations.csv")
    a_rec_path = os.path.join(student_dir, "After", "recommendations.csv")
    b_dice_path = os.path.join(student_dir, "Before", "dice_counterfactuals.csv")
    a_dice_path = os.path.join(student_dir, "After", "dice_counterfactuals.csv")
    a_shap_path = os.path.join(student_dir, "After", "shap_explanations.csv")
    cert_path = os.path.join(student_dir, "After", "certificates_parsed.csv")

    df_b = pd.read_csv(b_rec_path)
    df_a = pd.read_csv(a_rec_path)
    df_b_dice = pd.read_csv(b_dice_path) if os.path.exists(b_dice_path) else pd.DataFrame()
    df_a_dice = pd.read_csv(a_dice_path) if os.path.exists(a_dice_path) else pd.DataFrame()
    df_shap = pd.read_csv(a_shap_path) if os.path.exists(a_shap_path) else pd.DataFrame()
    df_certs = pd.read_csv(cert_path) if os.path.exists(cert_path) else pd.DataFrame()

    lines = []
    lines.append(f"## {idx}. {name} — Track: `{track}` ({profile})")
    lines.append("")
    
    # 1. Certificates List
    lines.append(f"### 📜 Daftar {len(df_certs)} Sertifikasi Industri yang Dimiliki:")
    if not df_certs.empty:
        for c_idx, c_row in df_certs.iterrows():
            tier_str = "Tier A (1.0)" if c_row.get("credibility_weight", 1.0) >= 0.8 else "Tier B (0.8)"
            lines.append(f"{c_idx+1}. **{c_row['title']}** — *{c_row.get('issuer', 'Industry Partner')}* ({tier_str})")
    else:
        lines.append("- *(Tidak memiliki sertifikat)*")
    lines.append("")

    # 2. Comparison Table Before vs After
    lines.append("### 📊 Tabel Komparasi Top-5 Rekomendasi Karir (Before vs After):")
    lines.append("| Peringkat | Lowongan Pekerjaan | Perusahaan | Skor Before (Matkul) | Skor After (+ Certs) | Lonjakan (Δ) | Status Dampak |")
    lines.append("|:---:|---|---|:---:|:---:|:---:|---|")
    
    for rank_a, row_a in enumerate(df_a.head(5).itertuples(), 1):
        job_id = row_a.job_id
        score_a = row_a.final_score
        
        # Match before
        mb = df_b[df_b["job_id"] == job_id]
        score_b = mb.iloc[0]["final_score"] if not mb.empty else 0.0
        delta = score_a - score_b
        
        if delta > 1.5:
            status = "🚀 **Lonjakan Masif**"
        elif delta > 0.3:
            status = "📈 **Meningkat Signifikan**"
        else:
            status = "📌 **Stabil (Dominan Matkul)**"
            
        lines.append(f"| **#{rank_a}** | **{row_a.job_title}** | {row_a.job_company} | `{score_b:.2f}` | `{score_a:.2f}` | **`{delta:+.2f}`** | {status} |")
    lines.append("")

    # 3. Top-1 Transformation Analysis
    top1_before = df_b.iloc[0]
    top1_after = df_a.iloc[0]
    lines.append(f"💡 **Transformasi Karir Juara 1:**")
    lines.append(f"- **Sebelum Sertifikat (Before):** `{top1_before['job_title']}` (Skor: `{top1_before['final_score']:.2f}`)")
    lines.append(f"- **Setelah Sertifikat (After):** `{top1_after['job_title']}` (Skor: `{top1_after['final_score']:.2f}`) ➔ *Kenaikan Total: `{top1_after['final_score'] - top1_before['final_score']:+.2f} poin`*")
    lines.append("")

    # 4. SHAP Feature Attribution
    lines.append("### 🔍 Atribusi Fitur Utama (SHAP Top Features):")
    if not df_shap.empty:
        # Get top features for top 1 job
        top_job_id = top1_after["job_id"]
        shap_sub = df_shap[df_shap["job_id"] == top_job_id].sort_values("shap_value", ascending=False)
        for _, s_row in shap_sub.head(4).iterrows():
            lines.append(f"- **{s_row['feature']}**: Kontribusi `+{s_row['shap_value']:.3f} poin` terhadap `{top1_after['job_title']}`")
    lines.append("")

    # 5. Dual-Stage DiCE Roadmap
    lines.append("### 🧭 Bimbingan Karir DiCE 2-Tahap (Multi-Stage 1.139 Kursus Riil):")
    
    # Stage 1
    lines.append("#### A. DiCE Tahap 1 — Saran Kursus Fondasi Awal (Kondisi *Before* / Matkul Saja):")
    if not df_b_dice.empty:
        for _, d_row in df_b_dice.head(3).iterrows():
            lines.append(f"- Untuk `{d_row['job_title']}`: {d_row['detail']}")
    else:
        lines.append("- *(Tidak ada saran intervensi)*")
    lines.append("")

    # Stage 2
    lines.append("#### B. DiCE Tahap 2 — Saran Spesialisasi Lanjutan (Kondisi *After* / Setelah Punya Sertifikat):")
    if not df_a_dice.empty:
        for _, d_row in df_a_dice.head(3).iterrows():
            lines.append(f"- Untuk `{d_row['job_title']}`: {d_row['detail']}")
    else:
        lines.append("- *(Tidak ada saran intervensi)*")
        
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)

def main():
    report = []
    report.append("# Rangkuman Komprehensif 10 Mahasiswa — Eksperimen XAI EKS12 (A/B Testing Before vs After)")
    report.append("")
    report.append("**Tanggal Evaluasi:** 17 Agustus 2026  ")
    report.append("**Lokasi Data:** `results/Eksperimen_XAI/EKS12_AB_Test/`  ")
    report.append("**Deskripsi Dokumen:** Rangkuman lengkap terperinci untuk masing-masing dari 10 profil mahasiswa bernama nyata yang mencakup perbandingan Top-5 rekomendasi karir, atribusi fitur SHAP, dan evolusi saran pelatihan DiCE (1.139 kursus online).")
    report.append("")
    report.append("---")
    report.append("")

    # Executive Table
    report.append("## 🏆 Ringkasan Eksekutif: 10 Profil Mahasiswa")
    report.append("")
    report.append("| No | Mahasiswa | Peminatan | Profil IPK | Sertifikat Dimiliki | Top-1 Before | Top-1 After | Kenaikan Skor (Δ) |")
    report.append("|:---:|---|:---:|:---:|:---:|---|---|:---:|")
    
    for idx, (name, track, profile, folder_name) in enumerate(STUDENTS, 1):
        student_dir = os.path.join(BASE_DIR, folder_name)
        df_b = pd.read_csv(os.path.join(student_dir, "Before", "recommendations.csv"))
        df_a = pd.read_csv(os.path.join(student_dir, "After", "recommendations.csv"))
        cert_p = os.path.join(student_dir, "After", "certificates_parsed.csv")
        num_certs = len(pd.read_csv(cert_p)) if os.path.exists(cert_p) else 0
        
        top_b = df_b.iloc[0]["job_title"]
        top_a = df_a.iloc[0]["job_title"]
        score_b = df_b.iloc[0]["final_score"]
        score_a = df_a.iloc[0]["final_score"]
        
        report.append(f"| {idx} | **{name}** | `{track}` | {profile} | **{num_certs} Certs** | {top_b} (`{score_b:.2f}`) | **{top_a} (`{score_a:.2f}`)** | **`{score_a - score_b:+.2f}`** 🚀 |")

    report.append("")
    report.append("---")
    report.append("")

    # Detailed Student Breakdown
    for idx, (name, track, profile, folder_name) in enumerate(STUDENTS, 1):
        report.append(format_student_section(idx, name, track, profile, folder_name))

    full_text = "\n".join(report)
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"[SUCCESS] Written comprehensive markdown report to: {OUTPUT_MD}")

if __name__ == "__main__":
    main()
