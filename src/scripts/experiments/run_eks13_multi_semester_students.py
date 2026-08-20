# -*- coding: utf-8 -*-
"""
EKS13: Multi-Semester XAI Evaluation Experiment (Semester 1 - 6)
Evaluating 2 Representative Majors:
1. Arya Pratama Putra - S1 Informatika (Full-Stack & Cloud Architecture)
2. Nabila Putri Maharani - S1 Sistem Informasi (Data / Business Analyst & Enterprise Systems)

Evaluates:
- Condition A (Before: 6 Semesters Academic KHS with Sub-CLO profiles)
- Condition B (After : Academic KHS + 5 Role-Specific Tier A/B Industry Certificates)
- Full XAI Suite: SHAP Feature Attribution, DiCE 1,139 Course Recommendations, and Percentage-Based Narratives
"""

import os
import sys
import time
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

ROOT_DIR = r"D:\MAIN DATA\Documents\Semester 6\KP BRIN"
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from sentence_transformers import SentenceTransformer, CrossEncoder
from kpbrin.core.full_pipeline import (
    load_khs, load_certificates, match_courses, rank_jobs_for_queries,
    aggregate_certs, aggregate_to_student_level,
    JOBS_CSV_PATH, COURSE_CLO_CSV_PATH, SBERT_MODEL, CROSS_ENCODER_MODEL
)
from kpbrin.core.embedding_cache import load_job_embeddings
from kpbrin.data.parse_input import parse_khs, parse_certificates_for_student
from kpbrin.xai.shap_explain import generate_shap_report
from kpbrin.xai.dice_explain import generate_dice_report
from kpbrin.xai.narrative_generator import generate_percentage_narrative

COURSE_AGG_CACHE_FILE = os.path.join(ROOT_DIR, "data", ".emb_cache", "course_to_job_cross_encoder_cache.csv")

def main():
    print("=" * 85)
    print("EXPERIMENT EKS13: MULTI-SEMESTER CAREER INTELLIGENCE & XAI EVALUATION")
    print("=" * 85)

    t_start = time.time()

    # 1. Load SBERT, Cross-Encoder & Job Dataset (4,570 unified jobs)
    print("\n[Step 1/5] Memuat Model SBERT, Cross-Encoder & Database 4.570 Lowongan...")
    sbert_model = SentenceTransformer(SBERT_MODEL)
    sbert_model.max_seq_length = 256
    cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL)

    jobs = pd.read_csv(JOBS_CSV_PATH)
    desc_col = "description_summary" if "description_summary" in jobs.columns else "description"
    job_emb = load_job_embeddings(jobs, JOBS_CSV_PATH, sbert_model, desc_col)
    course_clo_profiles = pd.read_csv(COURSE_CLO_CSV_PATH)
    print(f"  ✓ Berhasil memuat {len(jobs)} lowongan dan {len(course_clo_profiles)} profil CLO kurikulum.")

    # 2. Precompute / Load Course-to-Job Matching Cache
    available_courses = course_clo_profiles["course_name"].unique()
    relevant_course_profiles = course_clo_profiles[course_clo_profiles["course_name"].isin(available_courses)]

    if os.path.exists(COURSE_AGG_CACHE_FILE):
        print(f"\n[Step 2/5] [CACHE HIT] Memuat Course Aggregations dari cache...")
        course_agg_cache = pd.read_csv(COURSE_AGG_CACHE_FILE)
        print(f"  ✓ Course aggregation cache siap instan ({len(course_agg_cache)} rows).")
    else:
        print("\n[Step 2/5] Pra-komputasi Cross-Encoder Course-to-Job Matching...")
        t0 = time.time()
        course_agg_cache = rank_jobs_for_queries(
            relevant_course_profiles, id_col="course_name", text_col="consolidated_clo_text",
            jobs=jobs, job_emb=job_emb, sbert_model=sbert_model, cross_encoder=cross_encoder,
            desc_col=desc_col, extra_cols=(),
        ).rename(columns={"cross_encoder_score": "course_job_score_max"})
        course_agg_cache.to_csv(COURSE_AGG_CACHE_FILE, index=False)
        print(f"  ✓ Course aggregation cache tersimpan dalam {time.time() - t0:.2f} detik ({len(course_agg_cache)} kecocokan).")

    # 3. Setup Target Students and Output Folders
    eks13_dir = os.path.join(ROOT_DIR, "results", "Eksperimen_XAI", "EKS13_Multi_Semester_Test")
    khs_dir = os.path.join(ROOT_DIR, "data", "Mahasiswa", "multi_semester_khs")
    certs_dir = os.path.join(ROOT_DIR, "data", "Mahasiswa", "multi_semester_khs", "certificates")
    os.makedirs(eks13_dir, exist_ok=True)

    target_students = [
        {
            "name": "Arya Pratama Putra",
            "nim": "1301213012",
            "major": "S1 Informatika",
            "role": "Full-Stack Software Engineer & Cloud Architecture",
            "prefix": "Arya_Pratama_Putra_Informatika",
            "khs_file": os.path.join(khs_dir, "Arya_Pratama_Putra_Informatika_KHS.md"),
            "cert_dir": os.path.join(certs_dir, "Arya_Pratama_Putra_Informatika")
        },
        {
            "name": "Nabila Putri Maharani",
            "nim": "1202210088",
            "major": "S1 Sistem Informasi",
            "role": "Data / Business Analyst & Enterprise Systems Specialist",
            "prefix": "Nabila_Putri_Maharani_SI",
            "khs_file": os.path.join(khs_dir, "Nabila_Putri_Maharani_SI_KHS.md"),
            "cert_dir": os.path.join(certs_dir, "Nabila_Putri_Maharani_SI")
        }
    ]

    all_summary_results = []
    all_narratives = {}

    print("\n[Step 3/5] Mengeksekusi Eksperimen A/B Testing untuk 2 Mahasiswa...")
    for idx, st in enumerate(target_students, 1):
        st_name = st["name"]
        st_prefix = st["prefix"]
        st_major = st["major"]
        st_role = st["role"]
        
        print(f"\n================================================================================")
        print(f"[{idx}/2] Evaluasi: {st_name} ({st_major})")
        print(f"       Role Peminatan: {st_role}")
        print(f"================================================================================")

        st_out_dir = os.path.join(eks13_dir, st_prefix)
        before_dir = os.path.join(st_out_dir, "Before")
        after_dir = os.path.join(st_out_dir, "After")
        os.makedirs(before_dir, exist_ok=True)
        os.makedirs(after_dir, exist_ok=True)

        # Parse KHS
        df_khs_parsed = parse_khs(st["khs_file"])
        khs_csv_before = os.path.join(before_dir, "transcript_parsed.csv")
        df_khs_parsed.to_csv(khs_csv_before, index=False)

        # Parse Certificates
        df_certs_parsed = parse_certificates_for_student(st["cert_dir"])
        certs_csv_after = os.path.join(after_dir, "certificates_parsed.csv")
        df_certs_parsed.to_csv(certs_csv_after, index=False)

        # Match KHS courses
        khs_loaded = load_khs(khs_csv_before)
        matched_khs = match_courses(khs_loaded, available_courses)

        # -------------------------------------------------------------
        # PHASE 1: BEFORE (Semester 1-6 KHS Alone)
        # -------------------------------------------------------------
        print("  -> Menjalankan Kondisi A (Before: KHS Multi-Semester Saja)...")
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
            generate_dice_report(
                job_contributions=contribs_before,
                job_titles=job_titles_before,
                final_ranking=df_before,
                matched_courses=matched_khs,
                course_agg=course_agg_cache,
                top_k=5,
                csv_path="dice_counterfactuals.csv",
                plots_dir="dice_plots",
                n_plots=3,
                max_counterfactuals=3
            )
        finally:
            os.chdir(cwd)

        # -------------------------------------------------------------
        # PHASE 2: AFTER (KHS + 5 Industry Certificates)
        # -------------------------------------------------------------
        print("  -> Menjalankan Kondisi B (After: KHS + 5 Sertifikat Industri)...")
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
            generate_dice_report(
                job_contributions=contribs_after,
                job_titles=job_titles_after,
                final_ranking=df_after,
                matched_courses=matched_khs,
                course_agg=course_agg_cache,
                top_k=5,
                csv_path="dice_counterfactuals.csv",
                plots_dir="dice_plots",
                n_plots=3,
                max_counterfactuals=3
            )
        finally:
            os.chdir(cwd)

        # -------------------------------------------------------------
        # PHASE 3: PERCENTAGE NARRATIVE EXPLANATIONS
        # -------------------------------------------------------------
        print("  -> Meng-generate Penjelasan Naratif XAI Berbasis Persentase...")
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
        all_narratives[st_name] = narratives_top5

        top1_b = df_before.iloc[0]
        top1_a = df_after.iloc[0]
        delta_top1 = top1_a["final_score"] - top1_b["final_score"]

        print(f"  [RESULT] Top-1 Before: {top1_b['job_title']} (Skor: {top1_b['final_score']:.2f})")
        print(f"  [RESULT] Top-1 After : {top1_a['job_title']} (Skor: {top1_a['final_score']:.2f}) [Lonjakan: {delta_top1:+.2f}]")

        student_summary = {
            "student_name": st_name,
            "nim": st["nim"],
            "major": st_major,
            "role": st_role,
            "top1_before_title": top1_b["job_title"],
            "top1_before_score": top1_b["final_score"],
            "top1_after_title": top1_a["job_title"],
            "top1_after_score": top1_a["final_score"],
            "top1_delta": delta_top1,
            "top5_before": df_before.head(5)[["job_id", "job_title", "final_score"]].to_dict(orient="records"),
            "top5_after": df_after.head(5)[["job_id", "job_title", "final_score"]].to_dict(orient="records")
        }
        all_summary_results.append(student_summary)

    # 4. Generate Comprehensive Markdown Reports
    print("\n[Step 4/5] Menyusun Laporan Komprehensif Eksperimen EKS13...")
    md_lines = []
    md_lines.append("# Rangkuman Evaluasi Eksperimen XAI EKS13: Mahasiswa Multi-Semester (Informatika vs Sistem Informasi)")
    md_lines.append("")
    md_lines.append("**Tanggal Evaluasi:** 20 Agustus 2026  ")
    md_lines.append("**Direktori Hasil:** `results/Eksperimen_XAI/EKS13_Multi_Semester_Test/`  ")
    md_lines.append("**Dataset Lowongan:** 4.570 Lowongan Terintegrasi (LinkedIn & Glassdoor)  ")
    md_lines.append("**Metode Evaluasi:** A/B Testing (*Before: KHS Multi-Semester Smt 1-6* vs *After: KHS + 5 Sertifikat Industri*)  ")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    md_lines.append("## 1. Ringkasan Perbandingan Before vs After (Top-1 Job Recommendation)")
    md_lines.append("")
    md_lines.append("| Mahasiswa | Program Studi | Target Role Peminatan | Top-1 Rekomendasi (Before) | Skor Before | Top-1 Rekomendasi (After) | Skor After | Lonjakan Skor (Delta) |")
    md_lines.append("|:---|:---|:---|:---|:---:|:---|:---:|:---:|")
    for s in all_summary_results:
        md_lines.append(f"| **{s['student_name']}** | {s['major']} | {s['role']} | {s['top1_before_title']} | {s['top1_before_score']:.2f} | **{s['top1_after_title']}** | **{s['top1_after_score']:.2f}** | **{s['top1_delta']:+.2f}** |")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

    for s in all_summary_results:
        st_name = s["student_name"]
        md_lines.append(f"## Detail Evaluasi: {st_name} ({s['major']})")
        md_lines.append(f"- **NIM**             : {s['nim']}")
        md_lines.append(f"- **Peminatan Karir** : **{s['role']}**")
        md_lines.append(f"- **Status Studi**    : Semester 1 s/d Semester 6 (Lulus 114 SKS)")
        md_lines.append("")
        md_lines.append(f"### Perbandingan Top-5 Rekomendasi Lowongan Kerja")
        md_lines.append("")
        md_lines.append("| Rank | Kondisi A: Before (KHS Multi-Semester Saja) | Skor A | Kondisi B: After (KHS + 5 Sertifikat Industri) | Skor B |")
        md_lines.append("|:---:|:---|:---:|:---|:---:|")
        for r_idx in range(5):
            b_item = s["top5_before"][r_idx]
            a_item = s["top5_after"][r_idx]
            md_lines.append(f"| #{r_idx+1} | {b_item['job_title']} | {b_item['final_score']:.2f} | **{a_item['job_title']}** | **{a_item['final_score']:.2f}** |")
        md_lines.append("")
        
        md_lines.append(f"### Penjelasan Naratif XAI Berbasis Persentase (Top-3 Rekomendasi)")
        md_lines.append("")
        narratives = all_narratives.get(st_name, [])
        for n_idx, n_item in enumerate(narratives[:3], 1):
            n_data = n_item["narrative"]
            md_lines.append(f"#### Rekomendasi #{n_idx}: {n_item['job_title']} (Skor Keseluruhan: {n_item['final_score']:.2f} | Keselarasan: {n_data['overall_match_pct']}%)")
            md_lines.append(f"- **Ringkasan Naratif:** {n_data['narrative_text']}")
            if n_data.get("summary_bullet_points"):
                md_lines.append("- **Poin-Poin Kontributor Utama:**")
                for bp in n_data["summary_bullet_points"]:
                    md_lines.append(f"  - {bp}")
            md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    report_content = "\n".join(md_lines)
    
    # Save report to results and docs
    res_report_path = os.path.join(eks13_dir, "EKS13_Multi_Semester_Summary.md")
    docs_report_path = os.path.join(ROOT_DIR, "docs", "EKS13_Multi_Semester_Summary.md")
    
    with open(res_report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    with open(docs_report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"  ✓ Laporan tersimpan di: {res_report_path}")
    print(f"  ✓ Laporan tersimpan di: {docs_report_path}")

    print("\n" + "=" * 85)
    print(f"EKSPERIMEN EKS13 SELESAI SUKSES! (Total Waktu: {time.time() - t_start:.2f} detik)")
    print("=" * 85)


if __name__ == "__main__":
    main()
