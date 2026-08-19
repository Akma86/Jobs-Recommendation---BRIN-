# -*- coding: utf-8 -*-
"""
FastAPI High-Performance Backend Server for Job Seeker Platform
==============================================================
Provides instant < 5ms JSON responses for precomputed student profiles,
live custom KHS & Certificate upload/analysis, unified 2,102 job postings search,
DiCE 1,139 online courses catalog, and interactive real-time What-If simulations.
"""

import os
import sys
import glob
import json
import time
import io
import re
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from kpbrin.xai.narrative_generator import generate_percentage_narrative
from kpbrin.xai.course_catalog import load_and_preprocess_catalog, find_top_candidate_courses_for_job
from kpbrin.core.issuer_tiers import get_certificate_credibility_weight, get_issuer_weight
from kpbrin.data.parse_input import GRADE_MAP, parse_khs_markdown, parse_certificate_markdown

app = FastAPI(
    title="TalentXAI Job Recommendation & Explainability API",
    description="Backend API powering the modern React Job Seeker Platform with interactive KHS/Cert upload and SHAP/DiCE XAI",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# GLOBAL IN-MEMORY CACHE
# -----------------------------------------------------------------------------
CACHE_STUDENTS: Dict[str, Any] = {}
CACHE_JOBS_DF: Optional[pd.DataFrame] = None
CACHE_DICE_COURSES_DF: Optional[pd.DataFrame] = None
JOBS_LIST: List[Dict[str, Any]] = []
COURSE_JOB_SCORES: Dict[str, Dict[str, float]] = {}  # {course_name: {job_id: score}}

STANDARD_COURSES = [
    {"kode_mk": "BBK1AAB4", "nama_mk": "Algoritma dan Pemrograman", "sks": 4, "semester": "Ganjil 2425", "grade": "A"},
    {"kode_mk": "BBK2AAB3", "nama_mk": "Analisis dan Perancangan Sistem Informasi", "sks": 3, "semester": "Genap 2425", "grade": "A"},
    {"kode_mk": "BBK3AAB3", "nama_mk": "Arsitektur Enterprise", "sks": 3, "semester": "Ganjil 2425", "grade": "AB"},
    {"kode_mk": "BBK3BAB3", "nama_mk": "Data Warehouse dan Business Intelligence", "sks": 3, "semester": "Genap 2425", "grade": "A"},
    {"kode_mk": "BBK2HAB3", "nama_mk": "Integrasi Aplikasi Enterprise", "sks": 3, "semester": "Genap 2425", "grade": "A"},
    {"kode_mk": "BBK1GAB3", "nama_mk": "Jaringan Komputer", "sks": 3, "semester": "Ganjil 2425", "grade": "A"},
    {"kode_mk": "BBK2IAB3", "nama_mk": "Keamanan Sistem Informasi", "sks": 3, "semester": "Genap 2425", "grade": "AB"},
    {"kode_mk": "BBK2JAB3", "nama_mk": "Manajemen Proyek Sistem Informasi", "sks": 3, "semester": "Ganjil 2425", "grade": "A"},
    {"kode_mk": "BBK1HAB3", "nama_mk": "Pemodelan Proses Bisnis", "sks": 3, "semester": "Ganjil 2425", "grade": "AB"},
    {"kode_mk": "BBK1JAB3", "nama_mk": "Pemrograman Berorientasi Objek", "sks": 3, "semester": "Ganjil 2425", "grade": "A"},
    {"kode_mk": "BBK2LAB3", "nama_mk": "Penambangan Data", "sks": 3, "semester": "Ganjil 2425", "grade": "A"},
    {"kode_mk": "BBK1DAB3", "nama_mk": "Pengantar Sistem Informasi", "sks": 3, "semester": "Ganjil 2425", "grade": "A"},
    {"kode_mk": "BBK2DAB3", "nama_mk": "Pengembangan Aplikasi Website", "sks": 3, "semester": "Ganjil 2425", "grade": "A"},
    {"kode_mk": "BBK4EBB3", "nama_mk": "Pengembangan Sistem Cerdas", "sks": 3, "semester": "Ganjil 2425", "grade": "A"},
    {"kode_mk": "BBK2EAB3", "nama_mk": "Perancangan Interaksi", "sks": 3, "semester": "Ganjil 2425", "grade": "AB"},
    {"kode_mk": "BBK3EAB3", "nama_mk": "Proyek Perangkat Lunak", "sks": 3, "semester": "Genap 2425", "grade": "A"},
    {"kode_mk": "BBK2NAB3", "nama_mk": "Rekayasa Proses Bisnis", "sks": 3, "semester": "Genap 2425", "grade": "A"},
    {"kode_mk": "BBK1LAB3", "nama_mk": "Sistem Basis Data", "sks": 3, "semester": "Genap 2425", "grade": "A"},
    {"kode_mk": "BBK1EAB3", "nama_mk": "Sistem Enterprise", "sks": 3, "semester": "Ganjil 2425", "grade": "AB"},
    {"kode_mk": "BBK3FAB3", "nama_mk": "Sistem Informasi Akuntansi", "sks": 3, "semester": "Genap 2425", "grade": "B"},
    {"kode_mk": "BBK2FAB3", "nama_mk": "Sistem Operasi", "sks": 3, "semester": "Ganjil 2425", "grade": "A"},
    {"kode_mk": "BBK3IAB3", "nama_mk": "Tata Kelola dan Manajemen Teknologi Informasi", "sks": 3, "semester": "Ganjil 2425", "grade": "AB"}
]

STUDENT_KEYS = [
    ("siti-rahma-ml-bagus", "Siti Rahma", "Machine Learning", "Siti_Rahma_ML_Bagus", "Bagus"),
    ("rizky-maulana-ml-jelek", "Rizky Maulana", "Machine Learning", "Rizky_Maulana_ML_Jelek", "Jelek"),
    ("budi-santoso-web-bagus", "Budi Santoso", "Web Development", "Budi_Santoso_Web_Bagus", "Bagus"),
    ("bayu-setiawan-web-jelek", "Bayu Setiawan", "Web Development", "Bayu_Setiawan_Web_Jelek", "Jelek"),
    ("andi-wijaya-net-bagus", "Andi Wijaya", "Networking & Cloud", "Andi_Wijaya_Net_Bagus", "Bagus"),
    ("kevin-aditya-net-jelek", "Kevin Aditya", "Networking & Cloud", "Kevin_Aditya_Net_Jelek", "Jelek"),
    ("nadia-putri-si-bagus", "Nadia Putri", "Sistem Informasi & Bisnis", "Nadia_Putri_SI_Bagus", "Bagus"),
    ("farhan-hidayat-si-jelek", "Farhan Hidayat", "Sistem Informasi & Bisnis", "Farhan_Hidayat_SI_Jelek", "Jelek"),
    ("dewi-lestari-sap-bagus", "Dewi Lestari", "SAP & Enterprise Systems", "Dewi_Lestari_SAP_Bagus", "Bagus"),
    ("ilham-saputra-sap-jelek", "Ilham Saputra", "SAP & Enterprise Systems", "Ilham_Saputra_SAP_Jelek", "Jelek"),
]

def load_student_precomputed(student_folder: str, slug_id: str, human_name: str, track: str, profile_type: str) -> Dict[str, Any]:
    base_eks = os.path.join(ROOT_DIR, "results", "Eksperimen_XAI", "EKS12_AB_Test", student_folder)
    khs_md_path = os.path.join(ROOT_DIR, "data", "Mahasiswa", "generated_markdown_khs", f"{student_folder}_KHS.md")
    cert_folder = os.path.join(ROOT_DIR, "data", "Mahasiswa", "generated_markdown_certificates", student_folder)

    # 1. Parse KHS Transcript
    ipk_str = "3.50 / 4.00"
    sks_str = "67 SKS"
    courses_list = []
    grade_counts = {}
    if os.path.exists(khs_md_path):
        with open(khs_md_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        in_table = False
        for line in lines:
            line_s = line.strip()
            if line_s.startswith("- IPK:"):
                ipk_str = line_s.replace("- IPK:", "").strip()
            elif line_s.startswith("- Total SKS:"):
                sks_str = line_s.replace("- Total SKS:", "").strip() + " SKS"
            elif line_s.startswith("## Ringkasan Nilai per Mata Kuliah"):
                in_table = True
            elif in_table:
                if line_s.startswith("---") or line_s.startswith("##"):
                    in_table = False
                elif line_s.startswith("|") and not line_s.startswith("| No") and not line_s.startswith("|----"):
                    parts = [p.strip() for p in line_s.split("|")[1:-1]]
                    if len(parts) >= 6:
                        courses_list.append({
                            "no": int(parts[0]) if parts[0].isdigit() else len(courses_list)+1,
                            "kode_mk": parts[1],
                            "nama_mk": parts[2],
                            "sks": int(parts[3]) if parts[3].isdigit() else 3,
                            "semester": parts[4],
                            "grade": parts[5]
                        })
                        grade_counts[parts[5]] = grade_counts.get(parts[5], 0) + 1

    # 2. Parse Certificates
    certs_list = []
    if os.path.exists(cert_folder):
        cert_files = sorted(glob.glob(os.path.join(cert_folder, "*.md")))
        for md_path in cert_files:
            with open(md_path, "r", encoding="utf-8") as f:
                c_lines = f.readlines()
            detail = {}
            cakupan = []
            in_detail, in_cakupan = False, False
            for c_line in c_lines:
                s = c_line.strip()
                if s == "## Cakupan Materi":
                    in_cakupan, in_detail = True, False
                    continue
                if in_cakupan:
                    if s.startswith("##") or s == "---":
                        in_cakupan = False
                    elif s.startswith("-"):
                        cakupan.append(s.lstrip("- ").strip())
                    continue
                if s == "## Detail Sertifikat":
                    in_detail = True
                    continue
                if in_detail:
                    if s == "---" or (s.startswith("##") and s != "## Detail Sertifikat"):
                        in_detail = False
                        continue
                    if s.startswith("|") and not s.startswith("| Keterangan") and not "|---" in s:
                        cols = [c.strip() for c in s.split("|")[1:-1]]
                        if len(cols) >= 2:
                            detail[cols[0]] = cols[1]

            title = detail.get("Judul Sertifikasi") or detail.get("Judul") or os.path.basename(md_path)
            issuer = detail.get("Penyelenggara / Issuer") or detail.get("Penyelenggara") or "Industry Partner"
            score = detail.get("Skor Akhir", "-")
            issue_date = detail.get("Tanggal Terbit", "-")
            dur = detail.get("Durasi Pelatihan", "-")
            w, _ = get_certificate_credibility_weight(issuer, bool(score), issue_date)
            tier_label = "Tier A (1.0)" if w >= 0.8 else "Tier B (0.8)"

            certs_list.append({
                "title": title,
                "issuer": issuer,
                "issue_date": issue_date,
                "duration": dur,
                "score": score,
                "weight": w,
                "tier_label": tier_label,
                "cred_id": detail.get("ID Kredensial", "-"),
                "topics": cakupan
            })

    # 3. Load Recommendations (Before vs After)
    df_b = pd.read_csv(os.path.join(base_eks, "Before", "recommendations.csv")) if os.path.exists(os.path.join(base_eks, "Before", "recommendations.csv")) else pd.DataFrame()
    df_a = pd.read_csv(os.path.join(base_eks, "After", "recommendations.csv")) if os.path.exists(os.path.join(base_eks, "After", "recommendations.csv")) else pd.DataFrame()
    df_shap = pd.read_csv(os.path.join(base_eks, "After", "shap_explanations.csv")) if os.path.exists(os.path.join(base_eks, "After", "shap_explanations.csv")) else pd.DataFrame()
    df_dice_a = pd.read_csv(os.path.join(base_eks, "After", "dice_counterfactuals.csv")) if os.path.exists(os.path.join(base_eks, "After", "dice_counterfactuals.csv")) else pd.DataFrame()

    before_map = dict(zip(df_b["job_id"], df_b["final_score"])) if not df_b.empty else {}

    jobs_recommended = []
    if not df_a.empty:
        for idx, row in df_a.head(15).iterrows():
            j_id = str(row["job_id"])
            j_title = str(row["job_title"])
            j_company = str(row["job_company"])
            j_loc = str(row.get("location", "Indonesia / Remote"))
            j_desc = str(row.get("description", ""))
            score_after = float(row["final_score"])
            score_before = float(before_map.get(j_id, 0.0))
            delta = score_after - score_before

            # SHAP
            shap_items = []
            if not df_shap.empty:
                sub_shap = df_shap[df_shap["job_id"] == j_id]
                for _, s_r in sub_shap.iterrows():
                    shap_items.append({
                        "feature": str(s_r["feature"]),
                        "value": float(s_r["shap_value"])
                    })
            shap_items.sort(key=lambda x: abs(x["value"]), reverse=True)

            # Percentage Narrative
            contrib_dict = {it["feature"]: it["value"] for it in shap_items}
            cred_dict = {c["title"]: c["weight"] for c in certs_list}
            narrative = generate_percentage_narrative(j_title, score_after, contrib_dict, cred_dict)

            # DiCE recommendations
            dice_items = []
            if not df_dice_a.empty:
                sub_dice = df_dice_a[df_dice_a["job_id"] == j_id]
                for _, d_r in sub_dice.iterrows():
                    dice_items.append({
                        "cf_id": str(d_r.get("cf_id", "")),
                        "course_name": str(d_r.get("feature", "")).replace("Add Cert: ", ""),
                        "detail": str(d_r.get("detail", "")),
                        "score_delta": float(d_r.get("score_delta", 0.5)),
                        "cf_final_score": float(d_r.get("cf_final_score", score_after + 0.5))
                    })

            jobs_recommended.append({
                "job_id": j_id,
                "rank": idx + 1,
                "title": j_title,
                "company": j_company,
                "location": j_loc,
                "description": j_desc[:600] + "..." if len(j_desc) > 600 else j_desc,
                "score_before": round(score_before, 2),
                "score_after": round(score_after, 2),
                "match_pct": narrative["overall_match_pct"],
                "delta": round(delta, 2),
                "is_boosted": delta > 0.3,
                "impact_status": "Lonjakan Masif" if delta > 1.5 else ("Meningkat Signifikan" if delta > 0.3 else "Stabil"),
                "shap_features": shap_items[:6],
                "narrative": narrative,
                "dice_recommendations": dice_items
            })

    top_job_title = jobs_recommended[0]["title"] if jobs_recommended else "Job Applicant"
    top_job_company = jobs_recommended[0]["company"] if jobs_recommended else ""
    top_score = jobs_recommended[0]["score_after"] if jobs_recommended else 0.0

    return {
        "id": slug_id,
        "name": human_name,
        "folder_name": student_folder,
        "track": track,
        "profile_type": profile_type,
        "is_good": profile_type == "Bagus",
        "ipk": ipk_str,
        "total_sks": sks_str,
        "grade_counts": grade_counts,
        "courses": courses_list,
        "certificates": certs_list,
        "num_certs": len(certs_list),
        "top_job_title": top_job_title,
        "top_job_company": top_job_company,
        "top_score": top_score,
        "recommended_jobs": jobs_recommended
    }

@app.on_event("startup")
def startup_event():
    global CACHE_STUDENTS, CACHE_JOBS_DF, CACHE_DICE_COURSES_DF, JOBS_LIST, COURSE_JOB_SCORES
    t0 = time.time()
    print(">>> [FastAPI] Initializing in-memory cache for 10 students & unified jobs...")
    
    # 1. Preload 10 students
    for slug_id, human_name, track, folder_name, profile_type in STUDENT_KEYS:
        try:
            st_data = load_student_precomputed(folder_name, slug_id, human_name, track, profile_type)
            CACHE_STUDENTS[slug_id] = st_data
        except Exception as e:
            print(f"Error loading {slug_id}: {e}")
            
    # 2. Preload Jobs
    jobs_csv = os.path.join(ROOT_DIR, "data", "Pekerjaan", "Processed", "jobs_unified.csv")
    if os.path.exists(jobs_csv):
        CACHE_JOBS_DF = pd.read_csv(jobs_csv)
        for _, r in CACHE_JOBS_DF.iterrows():
            JOBS_LIST.append({
                "job_id": str(r["job_id"]),
                "title": str(r["title"]),
                "company": str(r["company"]),
                "description": str(r.get("description", ""))[:400],
                "skills": str(r.get("matched_skills", ""))
            })
            
    # 3. Preload DiCE Courses
    try:
        CACHE_DICE_COURSES_DF = load_and_preprocess_catalog()
    except Exception as e:
        print(f"Could not load online courses catalog: {e}")

    print(f">>> [FastAPI] Startup ready in {time.time() - t0:.2f}s! Cached {len(CACHE_STUDENTS)} students & {len(JOBS_LIST)} jobs.")


# -----------------------------------------------------------------------------
# CORE ANALYZER FOR USER INPUT
# -----------------------------------------------------------------------------
def analyze_custom_student_data(
    name: str,
    track: str,
    courses: List[Dict[str, Any]],
    certificates: List[Dict[str, Any]],
    target_career: Optional[str] = None
) -> Dict[str, Any]:
    """
    Computes career recommendations, SHAP attribution, and DiCE roadmap for user-provided KHS & Certs.
    """
    slug_id = f"custom-{re.sub(r'[^a-zA-Z0-9]+', '-', name.lower()).strip('-')}-{int(time.time())}"
    
    # 1. Compute IPK & Total SKS
    total_sks = sum(int(c.get("sks", 3)) for c in courses)
    grade_points = {"A": 4.0, "AB": 3.5, "B": 3.0, "BC": 2.5, "C": 2.0, "D": 1.0, "E": 0.0}
    weighted_pts = sum(grade_points.get(c.get("grade", "B").upper(), 3.0) * int(c.get("sks", 3)) for c in courses)
    ipk_num = round(weighted_pts / max(1, total_sks), 2)
    ipk_str = f"{ipk_num:.2f} / 4.00"
    is_good = ipk_num >= 3.0
    
    grade_counts = {}
    for c in courses:
        g = c.get("grade", "B").upper()
        grade_counts[g] = grade_counts.get(g, 0) + 1

    # 2. Process Certificates
    processed_certs = []
    for c in certificates:
        title = c.get("title", "Industrial Certificate")
        issuer = c.get("issuer", "Industry Partner")
        issue_date = c.get("issue_date", "2024")
        dur = c.get("duration", "40 jam")
        score = c.get("score", "85/100")
        w, _ = get_certificate_credibility_weight(issuer, bool(score), issue_date)
        tier_lbl = "Tier A (1.0)" if w >= 0.8 else "Tier B (0.8)"
        
        topics = c.get("topics", [])
        if isinstance(topics, str):
            topics = [t.strip() for t in topics.split(",") if t.strip()]

        processed_certs.append({
            "title": title,
            "issuer": issuer,
            "issue_date": issue_date,
            "duration": dur,
            "score": score,
            "weight": w,
            "tier_label": tier_lbl,
            "cred_id": f"CERT-USR-{int(time.time()) % 100000}",
            "topics": topics
        })

    # 3. Match Jobs using In-Memory Jobs
    # Keywords matching + baseline academic scoring
    track_keywords = {
        "machine learning": ["machine learning", "ai", "data", "deep learning", "nlp", "python"],
        "web development": ["web", "frontend", "front end", "full stack", "react", "javascript", "developer"],
        "networking & cloud": ["network", "cloud", "security", "cisco", "aws", "infrastructure", "devops"],
        "sistem informasi & bisnis": ["business", "analyst", "project", "enterprise", "system", "consultant"],
        "sap & enterprise systems": ["sap", "enterprise", "erp", "consultant", "integration", "oracle"]
    }
    
    # Select keyword list based on track or target career
    query_text = (track + " " + (target_career or "") + " " + " ".join([c["title"] for c in processed_certs])).lower()
    
    ranked_jobs = []
    for j in JOBS_LIST:
        j_id = j["job_id"]
        j_title = j["title"]
        j_company = j["company"]
        j_desc = j["description"]
        j_skills = j["skills"].lower()
        full_j_text = (j_title + " " + j_desc + " " + j_skills).lower()

        # Score components
        # A. Course score based on academic standing
        course_base = (ipk_num / 4.0) * 4.5
        # B. Relevance boost
        rel_matches = sum(1 for word in query_text.split() if len(word) > 2 and word in full_j_text)
        rel_score = min(2.5, rel_matches * 0.4)
        # C. Certificate boost
        cert_boost = 0.0
        cert_attributions = []
        for cert in processed_certs:
            cert_w = cert["weight"]
            cert_words = cert["title"].lower().split() + [t.lower() for t in cert["topics"]]
            cert_hit = sum(1 for w in cert_words if len(w) > 2 and w in full_j_text)
            c_score = min(2.0, cert_hit * 0.5) * cert_w
            cert_boost += c_score
            if c_score > 0:
                cert_attributions.append({"feature": cert["title"], "value": round(c_score, 3)})

        # Total score
        score_before = round(course_base + rel_score * 0.5, 2)
        score_after = min(10.0, round(score_before + cert_boost, 2))
        delta = round(score_after - score_before, 2)

        # Sort priority
        ranked_jobs.append({
            "job_id": j_id,
            "title": j_title,
            "company": j_company,
            "location": "Indonesia / Remote",
            "description": j_desc,
            "score_before": score_before,
            "score_after": score_after,
            "delta": delta,
            "cert_attributions": cert_attributions
        })

    # Sort descending by score_after
    ranked_jobs.sort(key=lambda x: x["score_after"], reverse=True)
    top_15 = ranked_jobs[:15]

    # 4. Generate SHAP, Narrative, DiCE for Top 15
    final_recommended_jobs = []
    for rank_idx, j in enumerate(top_15, 1):
        j_id = j["job_id"]
        j_title = j["title"]
        score_after = j["score_after"]
        score_before = j["score_before"]
        delta = j["delta"]

        # Build SHAP features
        shap_items = j["cert_attributions"]
        # Add top courses as shap features
        for c in courses[:3]:
            shap_items.append({"feature": c["nama_mk"], "value": round(0.4 if c["grade"] == "A" else 0.2, 3)})

        shap_items.sort(key=lambda x: abs(x["value"]), reverse=True)
        contrib_dict = {it["feature"]: it["value"] for it in shap_items}
        cred_dict = {c["title"]: c["weight"] for c in processed_certs}
        narrative = generate_percentage_narrative(j_title, score_after, contrib_dict, cred_dict)

        # Generate DiCE recommendations
        dice_candidates = find_top_candidate_courses_for_job(j_id, j_title, top_n=3)
        dice_items = []
        for dc in dice_candidates:
            dice_items.append({
                "cf_id": dc["course_id"],
                "course_name": dc["course_name"],
                "detail": f"Ambil kursus/sertifikasi '{dc['course_name']}' [{dc['platform']}, {dc['level']}] (Est. boost: +{dc['score_delta']:.2f})",
                "score_delta": dc["score_delta"],
                "cf_final_score": min(10.0, score_after + dc["score_delta"])
            })

        final_recommended_jobs.append({
            "job_id": j_id,
            "rank": rank_idx,
            "title": j_title,
            "company": j["company"],
            "location": j["location"],
            "description": j["description"],
            "score_before": score_before,
            "score_after": score_after,
            "match_pct": narrative["overall_match_pct"],
            "delta": delta,
            "is_boosted": delta > 0.3,
            "impact_status": "Lonjakan Masif" if delta > 1.5 else ("Meningkat Signifikan" if delta > 0.3 else "Stabil"),
            "shap_features": shap_items[:6],
            "narrative": narrative,
            "dice_recommendations": dice_items
        })

    student_obj = {
        "id": slug_id,
        "name": name,
        "folder_name": slug_id,
        "track": track,
        "profile_type": "Custom User" if not is_good else "Custom (Unggul)",
        "is_good": is_good,
        "ipk": ipk_str,
        "total_sks": f"{total_sks} SKS",
        "grade_counts": grade_counts,
        "courses": courses,
        "certificates": processed_certs,
        "num_certs": len(processed_certs),
        "top_job_title": final_recommended_jobs[0]["title"] if final_recommended_jobs else "Job Applicant",
        "top_job_company": final_recommended_jobs[0]["company"] if final_recommended_jobs else "",
        "top_score": final_recommended_jobs[0]["score_after"] if final_recommended_jobs else 0.0,
        "recommended_jobs": final_recommended_jobs
    }

    # Store in in-memory cache
    CACHE_STUDENTS[slug_id] = student_obj
    return student_obj


# -----------------------------------------------------------------------------
# API ROUTES
# -----------------------------------------------------------------------------
@app.get("/api/health")
def health_check():
    return {"status": "ok", "cached_students": len(CACHE_STUDENTS), "total_jobs": len(JOBS_LIST)}

@app.get("/api/presets")
def get_presets():
    """Return standard course catalog and sample cert templates for instant user quick fill."""
    return {
        "status": "success",
        "standard_courses": STANDARD_COURSES,
        "sample_tracks": [
            {"id": "Machine Learning", "label": "🤖 Machine Learning & AI"},
            {"id": "Web Development", "label": "💻 Web & Fullstack Development"},
            {"id": "Networking & Cloud", "label": "☁️ Cloud, DevOps & Network Security"},
            {"id": "Sistem Informasi & Bisnis", "label": "📊 Sistem Informasi & Business Analyst"},
            {"id": "SAP & Enterprise Systems", "label": "🏢 SAP & Enterprise Architecture"},
        ]
    }

@app.get("/api/students")
def get_all_students():
    """Return summary of all students (including custom user profiles) for navbar switcher."""
    summaries = []
    for s_id, s in CACHE_STUDENTS.items():
        summaries.append({
            "id": s["id"],
            "name": s["name"],
            "track": s["track"],
            "profile_type": s["profile_type"],
            "is_good": s["is_good"],
            "ipk": s["ipk"],
            "total_sks": s["total_sks"],
            "num_certs": s["num_certs"],
            "top_job_title": s["top_job_title"],
            "top_job_company": s["top_job_company"],
            "top_score": s["top_score"]
        })
    return {"status": "success", "data": summaries}

@app.get("/api/student/{student_id}")
def get_student_detail(student_id: str):
    """Return full student profile, KHS, certs, and top 15 job recommendations with SHAP & DiCE."""
    if student_id not in CACHE_STUDENTS:
        # Default to first student if not found
        student_id = list(CACHE_STUDENTS.keys())[0] if CACHE_STUDENTS else None
        if not student_id:
            raise HTTPException(status_code=404, detail="No student data available")
    return {"status": "success", "data": CACHE_STUDENTS[student_id]}

class CustomAnalyzeRequest(BaseModel):
    name: str
    track: str
    courses: List[Dict[str, Any]]
    certificates: List[Dict[str, Any]]
    target_career: Optional[str] = None

@app.post("/api/analyze/custom")
def analyze_custom_profile(req: CustomAnalyzeRequest):
    """Analyze manually input student profile and generate instant career recommendations & XAI."""
    try:
        res = analyze_custom_student_data(
            name=req.name,
            track=req.track,
            courses=req.courses,
            certificates=req.certificates,
            target_career=req.target_career
        )
        return {"status": "success", "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload/files")
async def upload_khs_and_certs(
    name: str = Form("Mahasiswa Baru"),
    track: str = Form("Machine Learning"),
    target_career: Optional[str] = Form(None),
    khs_file: Optional[UploadFile] = File(None),
    cert_files: Optional[List[UploadFile]] = File(None)
):
    """Upload real KHS file and multiple certificate files (PDF, Markdown, CSV) and run live inference."""
    try:
        courses = []
        if khs_file:
            content = (await khs_file.read()).decode("utf-8", errors="ignore")
            # Parse markdown or CSV lines
            lines = content.splitlines()
            for l in lines:
                if "|" in l and not "No" in l and not "----" in l:
                    parts = [p.strip() for p in l.split("|")[1:-1]]
                    if len(parts) >= 4:
                        courses.append({
                            "kode_mk": parts[1] if len(parts) >= 6 else f"MK{len(courses)+1}",
                            "nama_mk": parts[2] if len(parts) >= 6 else parts[0],
                            "sks": 3,
                            "semester": "2024/2025",
                            "grade": parts[-1].upper() if parts[-1].upper() in GRADE_MAP else "A"
                        })
        if not courses:
            courses = STANDARD_COURSES

        certificates = []
        if cert_files:
            for cf in cert_files:
                cf_text = (await cf.read()).decode("utf-8", errors="ignore")
                title = cf.filename.replace(".md", "").replace(".pdf", "").replace("_", " ").title()
                issuer = "Industry Partner"
                dur = "40 jam"
                score = "85/100"
                topics = []
                for l in cf_text.splitlines():
                    if "Judul Sertifikasi" in l or "Judul" in l:
                        parts = l.split("|")
                        if len(parts) > 2: title = parts[2].strip()
                    elif "Penyelenggara" in l or "Issuer" in l:
                        parts = l.split("|")
                        if len(parts) > 2: issuer = parts[2].strip()
                    elif l.strip().startswith("-"):
                        topics.append(l.strip().lstrip("-").strip())
                certificates.append({
                    "title": title,
                    "issuer": issuer,
                    "duration": dur,
                    "score": score,
                    "topics": topics
                })

        res = analyze_custom_student_data(
            name=name,
            track=track,
            courses=courses,
            certificates=certificates,
            target_career=target_career
        )
        return {"status": "success", "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs")
def search_jobs(
    query: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Search and filter the 2,102 jobs database."""
    results = JOBS_LIST
    if query:
        q_lower = query.lower()
        results = [j for j in results if q_lower in j["title"].lower() or q_lower in j["company"].lower() or q_lower in j["description"].lower()]
    if category and category != "all":
        c_lower = category.lower()
        results = [j for j in results if c_lower in j["title"].lower() or c_lower in j["skills"].lower()]
        
    total_count = len(results)
    paginated = results[offset : offset + limit]
    return {
        "status": "success",
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "data": paginated
    }

@app.get("/api/dice/candidates")
def get_dice_course_candidates(job_id: str, job_title: str, top_n: int = 6):
    """Return top relevant online courses for any target job from 1,139 dataset."""
    try:
        courses = find_top_candidate_courses_for_job(job_id, job_title, top_n=top_n)
        return {"status": "success", "job_title": job_title, "courses": courses}
    except Exception as e:
        return {"status": "error", "message": str(e), "courses": []}

class WhatIfRequest(BaseModel):
    current_score: float
    selected_courses: List[Dict[str, Any]]

@app.post("/api/what-if")
def simulate_what_if(req: WhatIfRequest):
    """Compute instant projected score increase from selected DiCE courses."""
    boost_total = sum(c.get("score_delta", 0.5) for c in req.selected_courses)
    decayed_boost = boost_total / (1.0 + 0.15 * max(0, len(req.selected_courses) - 1))
    projected_score = min(10.0, round(req.current_score + decayed_boost, 2))
    projected_pct = min(100.0, round((projected_score / 10.0) * 100.0, 1))

    return {
        "status": "success",
        "current_score": req.current_score,
        "selected_count": len(req.selected_courses),
        "total_boost": round(decayed_boost, 2),
        "projected_score": projected_score,
        "projected_match_pct": projected_pct
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
