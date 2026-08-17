# -*- coding: utf-8 -*-
"""
Fast, Optimized EKS12 A/B Testing Runner with Rich Certificate Topics,
Multi-Stage DiCE (1.139 Courses), and Percentage Narrative Explanations.
"""

import os
import sys
import glob
import time
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from kpbrin.core.full_pipeline import (
    load_khs, load_certificates, match_courses, rank_jobs_for_queries,
    aggregate_certs, aggregate_to_student_level,
    JOBS_CSV_PATH, COURSE_CLO_CSV_PATH, SBERT_MODEL, CROSS_ENCODER_MODEL
)
from kpbrin.core.embedding_cache import load_job_embeddings
from kpbrin.data.parse_input import parse_khs, parse_certificates_for_student
from kpbrin.xai.shap_explain import generate_shap_report, compute_shap_contributions
from kpbrin.xai.dice_explain import generate_dice_report
from kpbrin.xai.narrative_generator import generate_percentage_narrative

def parse_student_metadata(student_name):
    student_type = "Bagus" if "_Bagus" in student_name else "Jelek"
    base = student_name.replace("_Bagus", "").replace("_Jelek", "")
    parts = base.split("_")
    track = parts[-1] if len(parts) >= 2 else parts[0]
    human_name = " ".join(parts[:-1]) if len(parts) >= 2 else parts[0]
    return human_name, track, student_type

def main():
    print("==========================================================================")
    print("FAST EKS12 RUNNER: 10 Named Students + Rich Certs + % Narrative Explanations")
    print("==========================================================================")

    t_start = time.time()

    # 1. Load Models & Embeddings
    print(">>> [1/5] Loading SBERT, Cross-Encoder & Job Embeddings...")
    sbert_model = SentenceTransformer(SBERT_MODEL)
    cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL)
    jobs = pd.read_csv(JOBS_CSV_PATH)
    desc_col = "description_summary" if "description_summary" in jobs.columns else "description"
    job_emb = load_job_embeddings(jobs, JOBS_CSV_PATH, sbert_model, desc_col)
    course_clo_profiles = pd.read_csv(COURSE_CLO_CSV_PATH)
    print(f"    Loaded {len(jobs)} jobs and {len(course_clo_profiles)} course CLO profiles.")

    # 2. Pre-match all 22 standard curriculum courses against jobs ONCE
    print(">>> [2/5] Pre-computing Course-to-Job Cross-Encoder Aggregations (One-Time)...")
    sample_khs = pd.read_csv(os.path.join(ROOT_DIR, "data", "Mahasiswa", "generated_markdown_khs", "Siti_Rahma_ML_Bagus_KHS.md")) if False else None
    khs_demo_df = parse_khs(os.path.join(ROOT_DIR, "data", "Mahasiswa", "generated_markdown_khs", "Siti_Rahma_ML_Bagus_KHS.md"))
    available_courses = course_clo_profiles["course_name"].unique()
    matched_all = match_courses(khs_demo_df, available_courses)
    included_courses = matched_all[matched_all["included"]]["matched_course_name"].unique()
    relevant_course_profiles = course_clo_profiles[course_clo_profiles["course_name"].isin(included_courses)]
    
    course_agg_cache = rank_jobs_for_queries(
        relevant_course_profiles, id_col="course_name", text_col="consolidated_clo_text",
        jobs=jobs, job_emb=job_emb, sbert_model=sbert_model, cross_encoder=cross_encoder,
        desc_col=desc_col, extra_cols=(),
    ).rename(columns={"cross_encoder_score": "course_job_score_max"})
    print(f"    [DONE] Course aggregations ready ({len(course_agg_cache)} rows).")

    # 3. Setup Folders
    khs_dir = os.path.join(ROOT_DIR, "data", "Mahasiswa", "generated_markdown_khs")
    certs_dir = os.path.join(ROOT_DIR, "data", "Mahasiswa", "generated_markdown_certificates")
    eks12_dir = os.path.join(ROOT_DIR, "results", "Eksperimen_XAI", "EKS12_AB_Test")
    os.makedirs(eks12_dir, exist_ok=True)

    named_keywords = ["Siti_Rahma", "Rizky_Maulana", "Budi_Santoso", "Bayu_Setiawan", "Andi_Wijaya", "Kevin_Aditya", "Nadia_Putri", "Farhan_Hidayat", "Dewi_Lestari", "Ilham_Saputra"]
    khs_files = sorted([f for f in glob.glob(os.path.join(khs_dir, "*_KHS.md")) if any(k in f for k in named_keywords) and ("_Bagus" in f or "_Jelek" in f)])

    all_summary_rows = []
    student_narratives = {}

    print(f"\n>>> [3/5] Processing 10 Named Students...")
    for idx, khs_file in enumerate(khs_files, 1):
        filename = os.path.basename(khs_file)
        student_name = filename.replace("_KHS.md", "")
        human_name, track, student_type = parse_student_metadata(student_name)
        
        print(f"\n--- [{idx}/10] Student: {human_name} ({track} - {student_type}) ---")
        
        student_dir = os.path.join(eks12_dir, student_name)
        before_dir = os.path.join(student_dir, "Before")
        after_dir = os.path.join(student_dir, "After")
        os.makedirs(before_dir, exist_ok=True)
        os.makedirs(after_dir, exist_ok=True)
        
        student_cert_dir = os.path.join(certs_dir, student_name)
        
        # Parse KHS
        df_khs_parsed = parse_khs(khs_file)
        khs_csv_before = os.path.join(before_dir, "transcript_parsed.csv")
        df_khs_parsed.to_csv(khs_csv_before, index=False)
        
        # Parse Certs
        df_certs_parsed = parse_certificates_for_student(student_cert_dir)
        certs_csv_after = os.path.join(after_dir, "certificates_parsed.csv")
        df_certs_parsed.to_csv(certs_csv_after, index=False)
        
        # Match KHS courses
        khs_loaded = load_khs(khs_csv_before)
        matched_khs = match_courses(khs_loaded, available_courses)
        
        # =========================================================
        # PHASE 1: BEFORE (KHS Alone)
        # =========================================================
        df_before, contribs_before = aggregate_to_student_level(
            matched_courses=matched_khs,
            course_agg=course_agg_cache,
            cert_agg=pd.DataFrame(),
            certs_df=pd.DataFrame()
        )
        df_before.to_csv(os.path.join(before_dir, "recommendations.csv"), index=False)
        job_titles_before = dict(zip(df_before["job_id"], df_before["job_title"]))
        top5_ids_before = df_before.head(5)["job_id"].tolist()
        
        # SHAP & DiCE Before
        cwd = os.getcwd()
        os.chdir(before_dir)
        try:
            generate_shap_report(contribs_before, job_titles_before, top5_ids_before, "shap_explanations.csv", "shap_plots", n_plots=3)
            generate_dice_report(df_before, contribs_before, top_n_jobs=5, n_cfs_per_job=3, csv_path="dice_counterfactuals.csv", plots_dir="dice_plots")
        finally:
            os.chdir(cwd)

        # =========================================================
        # PHASE 2: AFTER (KHS + Rich Certs)
        # =========================================================
        certs_loaded = load_certificates(certs_csv_after)
        if not certs_loaded.empty:
            cert_ranking = rank_jobs_for_queries(
                certs_loaded, id_col="cert_id", text_col="cert_text",
                jobs=jobs, job_emb=job_emb, sbert_model=sbert_model, cross_encoder=cross_encoder,
                desc_col=desc_col, extra_cols=["title"], label_col="title",
            ).rename(columns={"title": "cert_title"})
            cert_ranking.to_csv(os.path.join(after_dir, "cert_job_ranking.csv"), index=False)
            cert_agg = aggregate_certs(cert_ranking, certs_loaded)
            cert_agg.to_csv(os.path.join(after_dir, "cert_job_aggregated.csv"), index=False)
        else:
            cert_agg = pd.DataFrame()

        df_after, contribs_after = aggregate_to_student_level(
            matched_courses=matched_khs,
            course_agg=course_agg_cache,
            cert_agg=cert_agg,
            certs_df=certs_loaded
        )
        df_after.to_csv(os.path.join(after_dir, "recommendations.csv"), index=False)
        job_titles_after = dict(zip(df_after["job_id"], df_after["job_title"]))
        top5_ids_after = df_after.head(5)["job_id"].tolist()

        # SHAP & DiCE After
        os.chdir(after_dir)
        try:
            generate_shap_report(contribs_after, job_titles_after, top5_ids_after, "shap_explanations.csv", "shap_plots", n_plots=3)
            generate_dice_report(df_after, contribs_after, top_n_jobs=5, n_cfs_per_job=3, csv_path="dice_counterfactuals.csv", plots_dir="dice_plots")
        finally:
            os.chdir(cwd)

        # =========================================================
        # PERCENTAGE NARRATIVE EXPLANATIONS
        # =========================================================
        cred_dict = dict(zip(certs_loaded["title"], certs_loaded["credibility_weight"])) if not certs_loaded.empty else {}
        narratives_top5 = []
        for _, row_a in df_after.head(5).iterrows():
            j_id = row_a["job_id"]
            j_title = row_a["job_title"]
            j_score = row_a["final_score"]
            j_contribs = contribs_after.get(j_id, {})
            narrative_obj = generate_percentage_narrative(j_title, j_score, j_contribs, cred_dict)
            narratives_top5.append({
                "job_id": j_id,
                "job_title": j_title,
                "final_score": j_score,
                "narrative": narrative_obj
            })
        student_narratives[student_name] = narratives_top5

        top1_b = df_before.iloc[0]
        top1_a = df_after.iloc[0]
        print(f"    Before Top-1: {top1_b['job_title']} ({top1_b['final_score']:.2f})")
        print(f"    After  Top-1: {top1_a['job_title']} ({top1_a['final_score']:.2f}) [Delta: {top1_a['final_score'] - top1_b['final_score']:+.2f}]")

    print("\n>>> [4/5] Generating Comprehensive Markdown Summary with Percentage Narratives...")
    md_lines = []
    md_lines.append("# Rangkuman Komprehensif 10 Mahasiswa — Eksperimen XAI EKS12 (A/B Testing Before vs After)")
    md_lines.append("")
    md_lines.append("**Tanggal Evaluasi:** 17 Agustus 2026  ")
    md_lines.append("**Lokasi Eksperimen:** `results/Eksperimen_XAI/EKS12_AB_Test/`  ")
    md_lines.append("**Metode XAI:** SHAP Waterfall + Dynamic DiCE 1.139 Kursus Riil + Percentage-Based Narrative Explanations  ")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    md_lines.append("## 🏆 Ringkasan Eksekutif: 10 Profil Mahasiswa")
    md_lines.append("")
    md_lines.append("| No | Mahasiswa | Peminatan | Profil IPK | Sertifikat | Top-1 Before (Matkul Saja) | Top-1 After (+ Sertifikat) | Lonjakan Skor (Δ) |")
    md_lines.append("|:---:|---|:---:|:---:|:---:|---|---|:---:|")

    for idx, khs_file in enumerate(khs_files, 1):
        filename = os.path.basename(khs_file)
        student_name = filename.replace("_KHS.md", "")
        human_name, track, student_type = parse_student_metadata(student_name)
        
        s_dir = os.path.join(eks12_dir, student_name)
        df_b = pd.read_csv(os.path.join(s_dir, "Before", "recommendations.csv"))
        df_a = pd.read_csv(os.path.join(s_dir, "After", "recommendations.csv"))
        df_c = pd.read_csv(os.path.join(s_dir, "After", "certificates_parsed.csv"))
        
        top_b = df_b.iloc[0]
        top_a = df_a.iloc[0]
        delta = top_a["final_score"] - top_b["final_score"]
        
        md_lines.append(f"| {idx} | **{human_name}** | `{track}` | {student_type} | **{len(df_c)} Certs** | {top_b['job_title']} (`{top_b['final_score']:.2f}`) | **{top_a['job_title']} (`{top_a['final_score']:.2f}`)** | **`{delta:+.2f}`** 🚀 |")

    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

    # Detailed Student Breakdown
    for idx, khs_file in enumerate(khs_files, 1):
        filename = os.path.basename(khs_file)
        student_name = filename.replace("_KHS.md", "")
        human_name, track, student_type = parse_student_metadata(student_name)
        
        s_dir = os.path.join(eks12_dir, student_name)
        df_b = pd.read_csv(os.path.join(s_dir, "Before", "recommendations.csv"))
        df_a = pd.read_csv(os.path.join(s_dir, "After", "recommendations.csv"))
        df_c = pd.read_csv(os.path.join(s_dir, "After", "certificates_parsed.csv"))
        df_b_dice = pd.read_csv(os.path.join(s_dir, "Before", "dice_counterfactuals.csv"))
        df_a_dice = pd.read_csv(os.path.join(s_dir, "After", "dice_counterfactuals.csv"))
        
        md_lines.append(f"## {idx}. {human_name} — Track: `{track}` (Profil {student_type})")
        md_lines.append("")
        
        # Certs
        md_lines.append(f"### 📜 Daftar {len(df_c)} Sertifikasi Industri yang Dimiliki:")
        for c_i, c_r in df_c.iterrows():
            tier_lbl = "Tier A (1.0)" if c_r.get("credibility_weight", 1.0) >= 0.8 else "Tier B (0.8)"
            md_lines.append(f"{c_i+1}. **{c_r['title']}** — *{c_r.get('issuer', 'Industry Partner')}* ({tier_lbl})")
        md_lines.append("")

        # Table
        md_lines.append("### 📊 Tabel Komparasi Top-5 Rekomendasi Karir (Before vs After):")
        md_lines.append("| Peringkat | Lowongan Pekerjaan | Perusahaan | Skor Before (Matkul) | Skor After (+ Certs) | Lonjakan (Δ) | Status Dampak |")
        md_lines.append("|:---:|---|---|:---:|:---:|:---:|---|")
        
        for r_i, r_a in enumerate(df_a.head(5).itertuples(), 1):
            j_id = r_a.job_id
            mb = df_b[df_b["job_id"] == j_id]
            sb = mb.iloc[0]["final_score"] if not mb.empty else 0.0
            delta = r_a.final_score - sb
            badge = "🚀 **Lonjakan Masif**" if delta > 1.5 else ("📈 **Meningkat Signifikan**" if delta > 0.3 else "📌 **Stabil (Dominan Matkul)**")
            md_lines.append(f"| **#{r_i}** | **{r_a.job_title}** | {r_a.job_company} | `{sb:.2f}` | `{r_a.final_score:.2f}` | **`{delta:+.2f}`** | {badge} |")
        md_lines.append("")

        # Percentage Narrative Explanations
        top1_narrative = student_narratives[student_name][0]["narrative"]
        md_lines.append(f"### 💬 Narrative Explanation Berbasis Persentase (% Kecocokan):")
        md_lines.append(f"> {top1_narrative['narrative_text']}")
        md_lines.append("")
        md_lines.append("#### 📌 Rincian Persentase Kecocokan Komponen Fitur:")
        for comp in top1_narrative["components"][:5]:
            md_lines.append(f"- **[{comp['type']}] {comp['name']}**: **Kecocokan {comp['relevance_match_pct']}%** terhadap posisi ini (Menyumbang **{comp['contribution_share_pct']}%** dari total skor).")
        md_lines.append("")

        # DiCE 2-Stage
        md_lines.append("### 🧭 Bimbingan Karir DiCE 2-Tahap (Multi-Stage 1.139 Kursus Riil):")
        md_lines.append("#### A. DiCE Tahap 1 — Saran Kursus Fondasi Awal (Kondisi *Before* / Matkul Saja):")
        for _, d_r in df_b_dice.head(3).iterrows():
            md_lines.append(f"- Untuk `{d_r['job_title']}`: {d_r['detail']}")
        md_lines.append("")
        md_lines.append("#### B. DiCE Tahap 2 — Saran Spesialisasi Lanjutan (Kondisi *After* / Setelah Punya Sertifikat):")
        for _, d_r in df_a_dice.head(3).iterrows():
            md_lines.append(f"- Untuk `{d_r['job_title']}`: {d_r['detail']}")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    report_path = os.path.join(eks12_dir, "RANGKUMAN_LENGKAP_10_MAHASISWA_EKS12.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"\n>>> [5/5] SUCCESS! Comprehensive report saved to: {report_path}")
    print(f"    Total execution time: {time.time() - t_start:.2f} seconds.")

if __name__ == "__main__":
    main()
