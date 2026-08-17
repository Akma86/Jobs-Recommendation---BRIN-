# -*- coding: utf-8 -*-
"""
Exhaustive Markdown Report Generator for all 10 Students in EKS12
with Exact Student Profile Summaries (Academic Standing, IPK, Grade Distributions),
Percentage-Based Narrative Explanations, SHAP Attribution, and Multi-Stage DiCE Roadmap.
"""

import os
import sys
import glob
import pandas as pd
import numpy as np

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from kpbrin.xai.narrative_generator import generate_percentage_narrative

BASE_DIR = os.path.join(ROOT_DIR, "results", "Eksperimen_XAI", "EKS12_AB_Test")
KHS_DIR = os.path.join(ROOT_DIR, "data", "Mahasiswa", "generated_markdown_khs")
OUTPUT_MD = os.path.join(BASE_DIR, "RANGKUMAN_LENGKAP_10_MAHASISWA_EKS12.md")

STUDENTS = [
    # ML Track
    ("Siti Rahma", "Machine Learning", "Bagus (IPK Tinggi)", "Siti_Rahma_ML_Bagus"),
    ("Rizky Maulana", "Machine Learning", "Jelek (IPK Rendah)", "Rizky_Maulana_ML_Jelek"),
    # Web Track
    ("Budi Santoso", "Web Development", "Bagus (IPK Tinggi)", "Budi_Santoso_Web_Bagus"),
    ("Bayu Setiawan", "Web Development", "Jelek (IPK Rendah)", "Bayu_Setiawan_Web_Jelek"),
    # Net Track
    ("Andi Wijaya", "Networking & Cloud", "Bagus (IPK Tinggi)", "Andi_Wijaya_Net_Bagus"),
    ("Kevin Aditya", "Networking & Cloud", "Jelek (IPK Rendah)", "Kevin_Aditya_Net_Jelek"),
    # SI Track
    ("Nadia Putri", "Sistem Informasi & Bisnis", "Bagus (IPK Tinggi)", "Nadia_Putri_SI_Bagus"),
    ("Farhan Hidayat", "Sistem Informasi & Bisnis", "Jelek (IPK Rendah)", "Farhan_Hidayat_SI_Jelek"),
    # SAP Track
    ("Dewi Lestari", "SAP & Enterprise Systems", "Bagus (IPK Tinggi)", "Dewi_Lestari_SAP_Bagus"),
    ("Ilham Saputra", "SAP & Enterprise Systems", "Jelek (IPK Rendah)", "Ilham_Saputra_SAP_Jelek"),
]

def extract_khs_metadata(khs_filename):
    khs_path = os.path.join(KHS_DIR, f"{khs_filename}_KHS.md")
    ipk_str = "N/A"
    sks_str = "67 SKS"
    grade_counts = {}
    
    if os.path.exists(khs_path):
        with open(khs_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            line_s = line.strip()
            if line_s.startswith("- IPK:"):
                ipk_str = line_s.replace("- IPK:", "").strip()
            elif line_s.startswith("- Total SKS:"):
                sks_str = line_s.replace("- Total SKS:", "").strip() + " SKS"
            elif line_s.startswith("|") and not line_s.startswith("| No") and not line_s.startswith("|----"):
                parts = [p.strip() for p in line_s.split("|")[1:-1]]
                if len(parts) >= 6:
                    g = parts[5]
                    grade_counts[g] = grade_counts.get(g, 0) + 1
    return ipk_str, sks_str, grade_counts

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

    ipk_val, sks_val, grade_counts = extract_khs_metadata(folder_name)
    is_good = "Bagus" in profile or "Tinggi" in profile

    lines = []
    lines.append(f"## {idx}. {name} — Track: `{track}` ({profile})")
    lines.append("")
    
    # 1. Detailed Student Profile & Academic Summary
    lines.append("### 📋 Ringkasan Profil & Status Akademik Mahasiswa:")
    lines.append(f"> **Nama Lengkap:** {name}  ")
    lines.append(f"> **Program Studi & Spesialisasi:** S1 Sistem Informasi — `{track}`  ")
    lines.append(f"> **Total Beban SKS:** {sks_val} (Katalog Kurikulum OBE Telkom University)  ")
    lines.append(f"> **Indeks Prestasi Kumulatif (IPK):** **`{ipk_val}`**  ")
    
    if is_good:
        status_badge = "🟢 **Kategori Akademik: Berprestasi Sangat Baik (High Academic Standing)**"
        narrative_profile = (
            f"Mahasiswa memiliki rekam jejak akademik yang **sangat kuat dan konsisten** di kelas. "
            f"Capaian pembelajaran lulusan (CLO) pada mata kuliah inti kurikulum terpenuhi dengan sangat memuaskan, "
            f"didominasi perolehan nilai **A** dan **AB**. Penguasaan teori dan fundamental teknologi sistem informasi "
            f"memberikan sinyal akademik yang kokoh pada fase *Before*."
        )
    else:
        status_badge = "🔴 **Kategori Akademik: Perlu Peningkatan / Kinerja Rendah (Low Academic Standing)**"
        narrative_profile = (
            f"Mahasiswa mengalami **kendala akademik pada perkuliahan reguler**, dengan perolehan nilai yang didominasi "
            f"oleh predikat **D**, **E**, dan sebagian **C**. Pada fase *Before*, sinyal akademik kurikulum bernilai rendah "
            f"sehingga rekomendasi karir awalnya memiliki skor kelayakan rendah atau mendekati nol. Profil ini menjadi "
            f"studi kasus utama untuk menguji apakah kepemilikan sertifikasi industri dapat menjadi *compensatory booster*."
        )
        
    lines.append(f"> **Status Evaluasi:** {status_badge}  ")
    if grade_counts:
        grade_summary_str = ", ".join([f"Nilai {k}: {v} MK" for k, v in sorted(grade_counts.items())])
        lines.append(f"> **Distribusi Nilai KHS:** `{grade_summary_str}`  ")
    lines.append("")
    lines.append(f"{narrative_profile}")
    lines.append("")

    # 2. Certificates List
    lines.append(f"### 📜 Portofolio {len(df_certs)} Sertifikasi Industri yang Dimiliki:")
    if not df_certs.empty:
        for c_idx, c_row in df_certs.iterrows():
            tier_str = "Tier A (Kredibilitas 1.0)" if c_row.get("credibility_weight", 1.0) >= 0.8 else "Tier B (Kredibilitas 0.8)"
            lines.append(f"{c_idx+1}. **{c_row['title']}** — *{c_row.get('issuer', 'Industry Partner')}* ({tier_str})")
    else:
        lines.append("- *(Tidak memiliki sertifikat)*")
    lines.append("")

    # 3. Recommendations Table BEFORE (KHS Only)
    lines.append("### 🔴 Rekomendasi Karir Fase BEFORE (Hanya Nilai KHS Mata Kuliah / Tanpa Sertifikat):")
    lines.append("| Peringkat | Lowongan Pekerjaan | Perusahaan | Skor Kelayakan (0-10) | Keselarasan Profil (%) | Status |")
    lines.append("|:---:|---|---|:---:|:---:|:---:|")
    for r_b_i, r_b in enumerate(df_b.head(5).itertuples(), 1):
        pct_b = min(100.0, max(0.0, (r_b.final_score / 10.0) * 100.0))
        lines.append(f"| **#{r_b_i}** | **{r_b.job_title}** | {r_b.job_company} | `{r_b.final_score:.2f}` | `{pct_b:.1f}%` | 📚 Murni Kurikulum KHS |")
    lines.append("")

    # 4. Recommendations Table AFTER (KHS + Certs)
    lines.append("### 🟢 Rekomendasi Karir Fase AFTER (Setelah Penambahan Sertifikasi Industri):")
    lines.append("| Peringkat | Lowongan Pekerjaan | Perusahaan | Skor Kelayakan (0-10) | Keselarasan Profil (%) | Lonjakan Skor (Δ) | Status |")
    lines.append("|:---:|---|---|:---:|:---:|:---:|:---:|")
    for r_a_i, r_a in enumerate(df_a.head(5).itertuples(), 1):
        j_id = r_a.job_id
        mb = df_b[df_b["job_id"] == j_id]
        score_b = mb.iloc[0]["final_score"] if not mb.empty else 0.0
        delta = r_a.final_score - score_b
        pct_a = min(100.0, max(0.0, (r_a.final_score / 10.0) * 100.0))
        badge = "🚀 Lonjakan Masif" if delta > 1.5 else ("📈 Meningkat" if delta > 0.3 else "📌 Stabil")
        lines.append(f"| **#{r_a_i}** | **{r_a.job_title}** | {r_a.job_company} | `{r_a.final_score:.2f}` | `{pct_a:.1f}%` | **`{delta:+.2f}`** | {badge} |")
    lines.append("")

    # 5. Comparison Table Before vs After
    lines.append("### 📊 Tabel Komparasi Efek Peringkat Rekomendasi (Before vs After):")
    lines.append("| Peringkat After | Lowongan Pekerjaan | Perusahaan | Skor Before (Matkul) | Skor After (+ Certs) | Lonjakan (Δ) | Dampak Sertifikat |")
    lines.append("|:---:|---|---|:---:|:---:|:---:|---|")
    
    for rank_a, row_a in enumerate(df_a.head(5).itertuples(), 1):
        job_id = row_a.job_id
        score_a = row_a.final_score
        
        # Match before
        mb = df_b[df_b["job_id"] == job_id]
        score_b = mb.iloc[0]["final_score"] if not mb.empty else 0.0
        delta = score_a - score_b
        
        if delta > 1.5:
            status = "🚀 **Lonjakan Masif (Didorong Kuat Sertifikat)**"
        elif delta > 0.3:
            status = "📈 **Meningkat Signifikan**"
        else:
            status = "📌 **Stabil (Dominan Nilai Matkul)**"
            
        lines.append(f"| **#{rank_a}** | **{row_a.job_title}** | {row_a.job_company} | `{score_b:.2f}` | `{score_a:.2f}` | **`{delta:+.2f}`** | {status} |")
    lines.append("")

    # 4. Top-1 Transformation Analysis
    top1_before = df_b.iloc[0]
    top1_after = df_a.iloc[0]
    lines.append(f"💡 **Transformasi Karir Rekomendasi Utama (#1):**")
    lines.append(f"- **Sebelum Sertifikat (Before / KHS Saja):** `{top1_before['job_title']}` di *{top1_before['job_company']}* (Skor: `{top1_before['final_score']:.2f}`)")
    lines.append(f"- **Setelah Sertifikat (After / KHS + Certs):** `{top1_after['job_title']}` di *{top1_after['job_company']}* (Skor: `{top1_after['final_score']:.2f}`) ➔ *Kenaikan Total: `{top1_after['final_score'] - top1_before['final_score']:+.2f} poin`*")
    lines.append("")

    # 5. Percentage-based Narrative Explanations
    lines.append("### 💬 Narrative Explanation Berbasis Persentase (% Kecocokan):")
    top_job_id = top1_after["job_id"]
    top_job_title = top1_after["job_title"]
    top_score = top1_after["final_score"]

    contrib_dict = {}
    if not df_shap.empty:
        shap_sub = df_shap[df_shap["job_id"] == top_job_id]
        for _, s_r in shap_sub.iterrows():
            contrib_dict[s_r["feature"]] = float(s_r["shap_value"])
    
    if not df_certs.empty and "credibility_weight" in df_certs.columns:
        cred_dict = dict(zip(df_certs["title"], df_certs["credibility_weight"]))
    else:
        cred_dict = {t: 0.9 for t in df_certs["title"]} if not df_certs.empty else {}
    narrative_obj = generate_percentage_narrative(top_job_title, top_score, contrib_dict, cred_dict)

    lines.append(f"> {narrative_obj['narrative_text']}")
    lines.append("")
    lines.append("#### 📌 Rincian Persentase Kecocokan per Komponen Fitur:")
    for comp in narrative_obj["components"][:5]:
        lines.append(f"- **[{comp['type']}] {comp['name']}**: **Kecocokan {comp['relevance_match_pct']}%** terhadap posisi ini (Menyumbang **{comp['contribution_share_pct']}%** dari total skor).")
    lines.append("")

    # 6. Dual-Stage DiCE Roadmap
    lines.append("### 🧭 Bimbingan Karir DiCE 2-Tahap (Multi-Stage 1.139 Kursus Riil):")
    
    # Stage 1
    lines.append("#### A. DiCE Tahap 1 — Saran Kursus Fondasi Awal (Kondisi *Before* / Matkul Saja):")
    if not df_b_dice.empty:
        for _, d_row in df_b_dice.head(3).iterrows():
            lines.append(f"- Untuk lowongan `{d_row['job_title']}`: {d_row['detail']}")
    else:
        lines.append("- *(Tidak ada saran intervensi)*")
    lines.append("")

    # Stage 2
    lines.append("#### B. DiCE Tahap 2 — Saran Spesialisasi Lanjutan (Kondisi *After* / Setelah Punya Sertifikat):")
    if not df_a_dice.empty:
        for _, d_row in df_a_dice.head(3).iterrows():
            lines.append(f"- Untuk lowongan `{d_row['job_title']}`: {d_row['detail']}")
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
    report.append("**Tanggal Evaluasi:** 18 Agustus 2026  ")
    report.append("**Lokasi Data:** `results/Eksperimen_XAI/EKS12_AB_Test/`  ")
    report.append("**Metode XAI:** SHAP Feature Attribution + Dynamic DiCE 1.139 Kursus Riil + **Percentage-Based Narrative Explanations**  ")
    report.append("")
    report.append("---")
    report.append("")

    # Executive Table
    report.append("## 🏆 Ringkasan Eksekutif: 10 Profil Mahasiswa")
    report.append("")
    report.append("| No | Mahasiswa | Peminatan | Status Akademik | IPK | Sertifikat | Top-1 Before (Matkul Saja) | Top-1 After (+ Sertifikat) | Kenaikan Skor (Δ) |")
    report.append("|:---:|---|:---:|:---:|:---:|:---:|---|---|:---:|")
    
    for idx, (name, track, profile, folder_name) in enumerate(STUDENTS, 1):
        student_dir = os.path.join(BASE_DIR, folder_name)
        df_b = pd.read_csv(os.path.join(student_dir, "Before", "recommendations.csv"))
        df_a = pd.read_csv(os.path.join(student_dir, "After", "recommendations.csv"))
        cert_p = os.path.join(student_dir, "After", "certificates_parsed.csv")
        num_certs = len(pd.read_csv(cert_p)) if os.path.exists(cert_p) else 0
        
        ipk_val, _, _ = extract_khs_metadata(folder_name)
        status_lbl = "🟢 Unggul" if "Bagus" in profile else "🔴 Rendah"
        
        top_b = df_b.iloc[0]["job_title"]
        top_a = df_a.iloc[0]["job_title"]
        score_b = df_b.iloc[0]["final_score"]
        score_a = df_a.iloc[0]["final_score"]
        delta = score_a - score_b
        
        report.append(f"| {idx} | **{name}** | `{track}` | {status_lbl} | `{ipk_val}` | **{num_certs} Certs** | {top_b} (`{score_b:.2f}`) | **{top_a} (`{score_a:.2f}`)** | **`{delta:+.2f}`** 🚀 |")

    report.append("")
    report.append("---")
    report.append("")

    # Detailed Student Breakdown
    for idx, (name, track, profile, folder_name) in enumerate(STUDENTS, 1):
        report.append(format_student_section(idx, name, track, profile, folder_name))

    full_text = "\n".join(report)
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(full_text)
    
    docs_path = os.path.join(ROOT_DIR, "docs", "EKS12_AB_Test_Summary.md")
    os.makedirs(os.path.dirname(docs_path), exist_ok=True)
    with open(docs_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    print(f"SUCCESS! Comprehensive 10-Student Report with Profile Summaries saved to:")
    print(f"  1. {OUTPUT_MD}")
    print(f"  2. {docs_path}")

if __name__ == "__main__":
    main()
