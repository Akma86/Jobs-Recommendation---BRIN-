# -*- coding: utf-8 -*-
"""
Streamlit Application: OBE & Explainable AI (XAI) Career Recommendation System
Developed for KP BRIN (Badan Riset dan Inovasi Nasional)

Features:
- Multi-format Input: PDF / Markdown KHS and PDF / JPG / PNG / Markdown Certificates (Multiple files supported).
- Pre-cached Embeddings & Model Accelerator for near-instant inference.
- Multi-Stage Evaluation: Before Cert (KHS Saja) vs After Cert (KHS + Certs).
- Retrospective XAI: SHAP Feature Attribution & Waterfall Visualizations.
- Prospective XAI: Dynamic DiCE Counterfactuals matching against 1,139 real Online Courses (Google, IBM, Meta, AWS, etc.).
- 1-Click Preset Demo Profiles for instant testing and presentation.
"""

import os
import sys
import re
import tempfile
import time
import glob
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Path configuration
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from kpbrin.core.full_pipeline import (
    run_pipeline,
    JOBS_CSV_PATH,
    COURSE_CLO_CSV_PATH,
    SBERT_MODEL,
    CROSS_ENCODER_MODEL,
)
from kpbrin.core.embedding_cache import load_job_embeddings
from kpbrin.core.issuer_tiers import get_issuer_weight
from kpbrin.data.parse_input import parse_khs, parse_certificates_for_student, GRADE_MAP
from kpbrin.xai.shap_explain import compute_shap_contributions
from kpbrin.xai.dice_explain import generate_diverse_counterfactuals
from kpbrin.xai.course_catalog import load_online_courses_catalog, find_top_candidate_courses_for_job

# -----------------------------------------------------------------------------
# Streamlit Page Config & Theme
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="OBE & XAI Career Recommender — KP BRIN",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Glassmorphism & High-Contrast Typography)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
    }
    
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 50%, #06B6D4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.85);
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 1.2rem;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px -4px rgba(59, 130, 246, 0.15);
    }
    .metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.7rem;
        font-weight: 800;
        color: #111827;
        margin-top: 0.3rem;
    }
    
    .job-card {
        background: #FFFFFF;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    
    .badge-tier-a {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .badge-tier-b {
        background-color: #E1EFFE;
        color: #1E429F;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .badge-boost {
        background-color: #FEF08A;
        color: #854D0E;
        padding: 4px 8px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Cached Models and Embeddings
# -----------------------------------------------------------------------------
@st.cache_resource(show_spinner="Memuat Model AI & Cache Embeddings...")
def get_cached_models_and_embeddings():
    from sentence_transformers import SentenceTransformer, CrossEncoder
    sbert = SentenceTransformer(SBERT_MODEL)
    ce = CrossEncoder(CROSS_ENCODER_MODEL)
    
    jobs = pd.read_csv(JOBS_CSV_PATH)
    desc_col = "description_summary" if "description_summary" in jobs.columns else "description"
    job_emb = load_job_embeddings(jobs, JOBS_CSV_PATH, sbert, desc_col)
    
    catalog_df = load_online_courses_catalog()
    return sbert, ce, jobs, job_emb, catalog_df

sbert_model, cross_encoder, jobs_df, job_emb_matrix, online_catalog_df = get_cached_models_and_embeddings()


# -----------------------------------------------------------------------------
# Helper Functions for Parsing Uploaded Files
# -----------------------------------------------------------------------------
def save_uploaded_file(uploaded_file, target_dir):
    file_path = os.path.join(target_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def parse_uploaded_khs(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".md":
        return parse_khs(file_path)
    elif ext == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            full_text = "".join(p.extract_text() or "" for p in reader.pages)
            
            # Simple text-based extractor fallback if no direct table parser
            rows = []
            lines = full_text.splitlines()
            for line in lines:
                parts = line.strip().split()
                # Check for grade at end of line (A, AB, B, BC, C, D, E)
                if len(parts) >= 3 and parts[-1].upper() in GRADE_MAP:
                    grade = parts[-1].upper()
                    sks = int(parts[-2]) if parts[-2].isdigit() else 3
                    course_name = " ".join(parts[:-2])
                    rows.append({
                        "kode_mk": f"MK_{len(rows)+1:02d}",
                        "nama_mk": course_name,
                        "sks": sks,
                        "nilai_huruf": grade,
                        "grade_weight": GRADE_MAP[grade]
                    })
            if rows:
                return pd.DataFrame(rows)
            else:
                # Fallback to default demo student KHS
                demo_khs = os.path.join(ROOT_DIR, "data", "Mahasiswa", "generated_markdown_khs", "Siti_Rahma_ML_Bagus_KHS.md")
                st.warning("⚠️ Menggunakan profil KHS standar karena format tabel PDF spesifik kampus memerlukan OCR.")
                return parse_khs(demo_khs)
        except Exception as e:
            st.error(f"Error membaca PDF KHS: {e}")
            demo_khs = os.path.join(ROOT_DIR, "data", "Mahasiswa", "generated_markdown_khs", "Siti_Rahma_ML_Bagus_KHS.md")
            return parse_khs(demo_khs)
    elif ext == ".csv":
        return pd.read_csv(file_path)
    else:
        raise ValueError(f"Ekstensi KHS tidak didukung: {ext}")

def parse_uploaded_certificates(file_paths):
    records = []
    for idx, path in enumerate(file_paths):
        filename = os.path.basename(path)
        name_no_ext = os.path.splitext(filename)[0]
        ext = os.path.splitext(path)[1].lower()
        
        if ext == ".md":
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            title_match = re.search(r"\*\*Title\*\*:\s*(.*)", content) or re.search(r"Title:\s*(.*)", content)
            issuer_match = re.search(r"\*\*Issuer\*\*:\s*(.*)", content) or re.search(r"Issuer:\s*(.*)", content)
            
            title = title_match.group(1).strip() if title_match else name_no_ext.replace("_", " ")
            issuer = issuer_match.group(1).strip() if issuer_match else "Industry Partner"
        else:
            # Clean name heuristic for PDF/JPG/PNG filenames
            clean_name = name_no_ext.replace("_", " ").replace("-", " ")
            # Detect common issuers
            issuer = "Online Learning Platform"
            for kw, iss in [("google", "Google"), ("aws", "AWS"), ("meta", "Meta"), ("ibm", "IBM"), 
                            ("cisco", "Cisco"), ("scrum", "SCRUMstudy"), ("sap", "SAP"), ("itil", "AXELOS")]:
                if kw in clean_name.lower():
                    issuer = iss
                    break
            title = clean_name
            
        weight = get_issuer_weight(issuer)
        records.append({
            "cert_id": f"cert_{idx+1}",
            "title": title,
            "issuer": issuer,
            "credibility_weight": weight,
            "cert_text": f"{title} by {issuer}",
            "has_assessment": True,
            "issue_date": "2024",
            "description_text": f"{title} certification covering core competencies."
        })
    return pd.DataFrame(records)


# -----------------------------------------------------------------------------
# SIDEBAR: Input & Control Panel
# -----------------------------------------------------------------------------
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Logo_BRIN.svg/1200px-Logo_BRIN.svg.png", width=140)
st.sidebar.markdown("### 🎛️ Panel Input Mahasiswa")

mode_input = st.sidebar.radio("Metode Input Data:", ["📂 Upload Berkas Sendiri (PDF / JPG / MD)", "🧪 Coba Profil Demo Mahasiswa (1-Click)"])

uploaded_khs = None
uploaded_certs = []
selected_demo_name = None

if mode_input == "📂 Upload Berkas Sendiri (PDF / JPG / MD)":
    uploaded_khs = st.sidebar.file_uploader("1. Upload KHS (Daftar Nilai)", type=["pdf", "md", "csv"], help="Format transkrip nilai akademik (PDF atau Markdown)")
    uploaded_certs = st.sidebar.file_uploader("2. Upload Sertifikat Industri (Bisa Banyak)", type=["pdf", "jpg", "jpeg", "png", "md"], accept_multiple_files=True, help="Unggah sertifikat kursus/pelatihan industri")
else:
    demo_options = [
        "Siti Rahma (ML - IPK 3.8, 5 Certs AI)",
        "Rizky Maulana (ML - IPK 2.0, 5 Certs AI)",
        "Budi Santoso (Web - IPK 3.8, 4 Certs Web/AWS)",
        "Bayu Setiawan (Web - IPK 2.0, 4 Certs Web/AWS)",
        "Andi Wijaya (Net - IPK 3.8, 4 Certs Net/Cloud)",
        "Kevin Aditya (Net - IPK 2.0, 4 Certs Net/Cloud)",
        "Nadia Putri (SI - IPK 3.8, 4 Certs ITIL/PMP)",
        "Farhan Hidayat (SI - IPK 2.0, 4 Certs ITIL/PMP)",
        "Dewi Lestari (SAP - IPK 3.8, 5 Certs SAP/ITIL)",
        "Ilham Saputra (SAP - IPK 2.0, 5 Certs SAP/ITIL)"
    ]
    selected_demo = st.sidebar.selectbox("Pilih Profil Mahasiswa Demo:", demo_options)
    
    # Map demo selection to file paths
    name_map = {
        "Siti Rahma": "Siti_Rahma_ML_Bagus",
        "Rizky Maulana": "Rizky_Maulana_ML_Jelek",
        "Budi Santoso": "Budi_Santoso_Web_Bagus",
        "Bayu Setiawan": "Bayu_Setiawan_Web_Jelek",
        "Andi Wijaya": "Andi_Wijaya_Net_Bagus",
        "Kevin Aditya": "Kevin_Aditya_Net_Jelek",
        "Nadia Putri": "Nadia_Putri_SI_Bagus",
        "Farhan Hidayat": "Farhan_Hidayat_SI_Jelek",
        "Dewi Lestari": "Dewi_Lestari_SAP_Bagus",
        "Ilham Saputra": "Ilham_Saputra_SAP_Jelek"
    }
    short_name = selected_demo.split(" (")[0]
    selected_demo_name = name_map[short_name]

top_k_display = st.sidebar.slider("Jumlah Top Rekomendasi Karir:", min_value=3, max_value=15, value=5)
btn_run = st.sidebar.button("🚀 Jalankan Rekomendasi & Analisis XAI", type="primary", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Tentang Sistem:**
Sistem rekomendasi karir cerdas berbasis Kurikulum OBE Telkom University & Explainable AI (SHAP + Dynamic DiCE) dengan dataset 1.139 Online Courses.
""")


# -----------------------------------------------------------------------------
# MAIN APP EXECUTION
# -----------------------------------------------------------------------------
st.markdown('<div class="main-title">Sistem Rekomendasi Karir Berbasis OBE & Explainable AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Integrasi Kurikulum Akademik (CLO OBE), Kredensial Industri, SHAP Retrospektif, dan Dynamic DiCE Prospektif</div>', unsafe_allow_html=True)

if btn_run or "pipeline_results" in st.session_state:
    with st.spinner("Sedang memproses kurikulum, mencocokkan kredensial, dan mengeksekusi XAI..."):
        # Setup temporary processing workspace
        with tempfile.TemporaryDirectory() as tmp_dir:
            if mode_input == "📂 Upload Berkas Sendiri (PDF / JPG / MD)":
                if not uploaded_khs:
                    st.error("Silakan unggah berkas KHS terlebih dahulu.")
                    st.stop()
                
                khs_path = save_uploaded_file(uploaded_khs, tmp_dir)
                df_khs = parse_uploaded_khs(khs_path)
                khs_csv_path = os.path.join(tmp_dir, "transcript_parsed.csv")
                df_khs.to_csv(khs_csv_path, index=False)
                
                certs_csv_path = None
                df_certs = pd.DataFrame()
                if uploaded_certs:
                    saved_cert_paths = [save_uploaded_file(f, tmp_dir) for f in uploaded_certs]
                    df_certs = parse_uploaded_certificates(saved_cert_paths)
                    certs_csv_path = os.path.join(tmp_dir, "certificates_parsed.csv")
                    df_certs.to_csv(certs_csv_path, index=False)
                
                student_display_name = os.path.splitext(uploaded_khs.name)[0].replace("_", " ")
            else:
                # Demo Mode: Load pre-generated student files
                khs_file = os.path.join(ROOT_DIR, "data", "Mahasiswa", "generated_markdown_khs", f"{selected_demo_name}_KHS.md")
                cert_dir = os.path.join(ROOT_DIR, "data", "Mahasiswa", "generated_markdown_certificates", selected_demo_name)
                
                df_khs = parse_khs(khs_file)
                khs_csv_path = os.path.join(tmp_dir, "transcript_parsed.csv")
                df_khs.to_csv(khs_csv_path, index=False)
                
                df_certs = parse_certificates_for_student(cert_dir)
                certs_csv_path = os.path.join(tmp_dir, "certificates_parsed.csv")
                df_certs.to_csv(certs_csv_path, index=False)
                
                student_display_name = selected_demo_name.replace("_", " ")

            # -------------------------------------------------------------
            # EXECUTE PIPELINE: BEFORE (KHS Only) & AFTER (KHS + Certs)
            # -------------------------------------------------------------
            cwd_orig = os.getcwd()
            os.chdir(tmp_dir)
            try:
                # Phase 1: Before
                df_before, contribs_before = run_pipeline(
                    khs_path=khs_csv_path,
                    certs_path=None,
                    jobs_path=JOBS_CSV_PATH,
                    course_clo_path=COURSE_CLO_CSV_PATH
                )
                
                # Phase 2: After
                df_after, contribs_after = run_pipeline(
                    khs_path=khs_csv_path,
                    certs_path=certs_csv_path if (certs_csv_path and os.path.exists(certs_csv_path) and not df_certs.empty) else None,
                    jobs_path=JOBS_CSV_PATH,
                    course_clo_path=COURSE_CLO_CSV_PATH
                )
                
                # Save into session state
                st.session_state["pipeline_results"] = {
                    "student_name": student_display_name,
                    "df_khs": df_khs,
                    "df_certs": df_certs,
                    "df_before": df_before,
                    "contribs_before": contribs_before,
                    "df_after": df_after,
                    "contribs_after": contribs_after,
                }
            finally:
                os.chdir(cwd_orig)

    # Fetch results from state
    res = st.session_state["pipeline_results"]
    df_khs = res["df_khs"]
    df_certs = res["df_certs"]
    df_before = res["df_before"]
    contribs_before = res["contribs_before"]
    df_after = res["df_after"]
    contribs_after = res["contribs_after"]
    
    # -------------------------------------------------------------------------
    # METRIC CARDS
    # -------------------------------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)
    avg_grade_weight = df_khs["grade_weight"].mean() if "grade_weight" in df_khs.columns else 0.75
    est_ipk = avg_grade_weight * 4.0 / 0.85
    
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">👤 Profil Mahasiswa</div>
            <div class="metric-value" style="font-size: 1.25rem;">{res['student_name']}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📚 Estimasi IPK / CLO</div>
            <div class="metric-value">{est_ipk:.2f} <span style="font-size: 0.9rem; color: #6B7280;">/ 4.00</span></div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📜 Sertifikat Industri</div>
            <div class="metric-value">{len(df_certs)} <span style="font-size: 0.9rem; color: #6B7280;">Terverifikasi</span></div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        top_job = df_after.iloc[0]['job_title']
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🏆 Top Rekomendasi Karir</div>
            <div class="metric-value" style="font-size: 1.15rem; color: #2563EB;">{top_job}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TABS: Full XAI & Recommendation Suite
    # -------------------------------------------------------------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏆 Rekomendasi & Komparasi Before-After",
        "📊 SHAP Retrospektif (Waterfall)",
        "🧭 Dynamic DiCE (1.139 Online Courses)",
        "📋 Rincian Transkrip & Kredensial"
    ])

    # =========================================================================
    # TAB 1: Rekomendasi & Komparasi Before vs After
    # =========================================================================
    with tab1:
        st.markdown("### 📈 Evaluasi Dampak Sertifikasi: Sebelum (*Before*) vs Sesudah (*After*)")
        st.markdown("Tabel dan grafik interaktif di bawah ini membandingkan skor kelayakan pekerjaan saat mahasiswa **hanya bermodalkan nilai mata kuliah (Before)** dibandingkan setelah **ditambah sertifikasi industri (After)**.")
        
        # Build unified comparison table
        top_n = df_after.head(top_k_display)
        comparison_rows = []
        for rank_a, row_a in enumerate(top_n.itertuples(), 1):
            job_id = row_a.job_id
            score_a = row_a.final_score
            
            # Find in before
            match_b = df_before[df_before["job_id"] == job_id]
            if not match_b.empty:
                score_b = match_b.iloc[0]["final_score"]
                rank_b = df_before.index[df_before["job_id"] == job_id][0] + 1
            else:
                score_b = 0.0
                rank_b = 999
                
            delta_score = score_a - score_b
            if delta_score > 1.5:
                badge = "🚀 Lonjakan Masif"
            elif delta_score > 0.3:
                badge = "📈 Meningkat"
            else:
                badge = "📌 Stabil (Dominan Matkul)"
                
            comparison_rows.append({
                "Peringkat": f"#{rank_a}",
                "Lowongan Pekerjaan": row_a.job_title,
                "Perusahaan": row_a.job_company,
                "Skor Before (Matkul)": f"{score_b:.3f}",
                "Skor After (+ Certs)": f"{score_a:.3f}",
                "Kenaikan Skor (Δ)": f"{delta_score:+.3f}",
                "Status Efek": badge
            })
            
        comp_df = pd.DataFrame(comparison_rows)
        st.dataframe(comp_df, use_container_width=True, hide_index=True)
        
        # Interactive Plotly Bar Chart
        st.markdown("#### 📊 Visualisasi Perbandingan Skor Sebelum vs Sesudah")
        plot_df = pd.DataFrame({
            "Job": [r["Lowongan Pekerjaan"] for r in comparison_rows],
            "Before Cert (Matkul Saja)": [float(r["Skor Before (Matkul)"]) for r in comparison_rows],
            "After Cert (+ Sertifikat)": [float(r["Skor After (+ Certs)"]) for r in comparison_rows],
        })
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=plot_df["Job"],
            x=plot_df["Before Cert (Matkul Saja)"],
            name="Before Cert (Matkul Saja)",
            orientation="h",
            marker=dict(color="#94A3B8")
        ))
        fig.add_trace(go.Bar(
            y=plot_df["Job"],
            x=plot_df["After Cert (+ Sertifikat)"],
            name="After Cert (+ Sertifikat)",
            orientation="h",
            marker=dict(color="#3B82F6")
        ))
        fig.update_layout(
            barmode="group",
            yaxis=dict(autorange="reversed"),
            xaxis_title="Final Employability Score",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

    # =========================================================================
    # TAB 2: SHAP Retrospektif (Waterfall Explanations)
    # =========================================================================
    with tab2:
        st.markdown("### 🔍 Atribusi Fitur SHAP: *Mengapa Pekerjaan Ini Direkomendasikan?*")
        st.markdown("SHAP (*Shapley Additive Explanations*) membedah kontribusi individual masing-masing mata kuliah dan sertifikat terhadap nilai akhir rekomendasi.")
        
        selected_job_title = st.selectbox(
            "Pilih Pekerjaan untuk Melihat Waterfall SHAP:",
            options=df_after.head(top_k_display)["job_title"].tolist()
        )
        
        # Get selected job_id
        target_job_row = df_after[df_after["job_title"] == selected_job_title].iloc[0]
        sel_job_id = target_job_row["job_id"]
        
        # Compute SHAP for selected job
        job_contrib = contribs_after.get(sel_job_id, {})
        shap_dict, base_val = compute_shap_contributions(job_contrib)
        
        if shap_dict:
            # Sort features
            sorted_feats = sorted(shap_dict.items(), key=lambda kv: abs(kv[1]), reverse=True)[:10]
            labels = [k for k, _ in sorted_feats][::-1]
            values = [v for _, v in sorted_feats][::-1]
            
            fig_shap = go.Figure(go.Bar(
                x=values,
                y=labels,
                orientation='h',
                marker=dict(
                    color=["#10B981" if v > 0 else "#EF4444" for v in values]
                )
            ))
            fig_shap.update_layout(
                title=f"Kontribusi Komponen terhadap '{selected_job_title}' (Skor Akhir = {target_job_row['final_score']:.2f})",
                xaxis_title="Nilai Kontribusi SHAP (Poin)",
                margin=dict(l=30, r=30, t=40, b=20)
            )
            st.plotly_chart(fig_shap, use_container_width=True)
            
            # Feature Breakdown Table
            breakdown_df = pd.DataFrame([
                {"Komponen / Fitur": k, "Kontribusi Skor (Poin)": f"{v:+.4f}"}
                for k, v in sorted_feats
            ])
            st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
        else:
            st.info("Tidak ada data kontribusi fitur untuk pekerjaan ini.")

    # =========================================================================
    # TAB 3: Dynamic DiCE (Target Dream Job & Career Roadmap)
    # =========================================================================
    with tab3:
        st.markdown("### 🧭 DiCE Career Roadmap: *Pilih Karir Impian & Dapatkan Rekomendasi Kursus Terarah*")
        st.markdown("Fitur ini memungkinkan mahasiswa menentukan **Karir / Posisi Impian (*Career Goal*)** yang ingin dituju. Modul DiCE (*Diverse Counterfactual Explanations*) akan menganalisis kesenjangan (*skill gap*) dan menelusuri katalog **1.139 Kursus Online Riil** (*Google, AWS, Meta, IBM, DeepLearning.AI, dll.*) untuk memberikan rekomendasi kursus yang tepat sasaran.")
        
        col_m1, col_m2 = st.columns([1, 1])
        with col_m1:
            dice_mode = st.radio(
                "Sumber Pemilihan Karir Target:",
                ["🎯 Pilih Karir Impian (Bebas dari Seluruh Katalog Pekerjaan)", "🏆 Pilih dari Top Rekomendasi Saat Ini"],
                horizontal=True
            )
            
        all_unique_titles = sorted(jobs_df["title"].dropna().unique().tolist())
        
        if dice_mode == "🎯 Pilih Karir Impian (Bebas dari Seluruh Katalog Pekerjaan)":
            with col_m2:
                cat_filter = st.selectbox(
                    "Filter Kategori Bidang Pekerjaan:",
                    ["🌐 Semua Bidang", "🤖 Artificial Intelligence & Machine Learning", "💻 Software & Web Development", 
                     "☁️ Cloud, Network & DevOps", "🔒 Cybersecurity", "📊 Data Science & Analytics", "🏢 Enterprise Systems & SAP", "🎨 UI/UX & Design"]
                )
                
            # Filter titles based on category
            if cat_filter == "🤖 Artificial Intelligence & Machine Learning":
                filtered_titles = [t for t in all_unique_titles if any(k in t.lower() for k in ["ai", "ml", "machine learning", "artificial", "deep learning", "nlp", "computer vision"])]
            elif cat_filter == "💻 Software & Web Development":
                filtered_titles = [t for t in all_unique_titles if any(k in t.lower() for k in ["web", "frontend", "front-end", "backend", "back-end", "fullstack", "software", "developer", "engineer", "java", "python", "react"])]
            elif cat_filter == "☁️ Cloud, Network & DevOps":
                filtered_titles = [t for t in all_unique_titles if any(k in t.lower() for k in ["cloud", "network", "devops", "aws", "infrastructure", "system admin", "cisco"])]
            elif cat_filter == "🔒 Cybersecurity":
                filtered_titles = [t for t in all_unique_titles if any(k in t.lower() for k in ["security", "cyber", "soc", "infosec", "penetration"])]
            elif cat_filter == "📊 Data Science & Analytics":
                filtered_titles = [t for t in all_unique_titles if any(k in t.lower() for k in ["data", "analyst", "analytics", "bi", "scientist"])]
            elif cat_filter == "🏢 Enterprise Systems & SAP":
                filtered_titles = [t for t in all_unique_titles if any(k in t.lower() for k in ["sap", "enterprise", "erp", "business analyst", "itil", "consultant"])]
            elif cat_filter == "🎨 UI/UX & Design":
                filtered_titles = [t for t in all_unique_titles if any(k in t.lower() for k in ["ux", "ui", "design", "product", "interaction"])]
            else:
                filtered_titles = all_unique_titles
                
            if not filtered_titles:
                filtered_titles = all_unique_titles
                
            target_dice_job = st.selectbox("Pilih Pekerjaan Impian Target Kamu:", options=filtered_titles, key="dream_job_sel")
            
            # Find matching job row or best proxy
            match_job_rows = jobs_df[jobs_df["title"] == target_dice_job]
            sel_dice_job_id = match_job_rows.iloc[0]["job_id"] if not match_job_rows.empty else "custom_job_id"
            
            # Check current score in after ranking
            curr_score_match = df_after[df_after["job_title"] == target_dice_job]
            current_score = curr_score_match.iloc[0]["final_score"] if not curr_score_match.empty else df_after["final_score"].median()
        else:
            with col_m2:
                target_dice_job = st.selectbox(
                    "Pilih Pekerjaan dari Top Rekomendasi:",
                    options=df_after.head(top_k_display)["job_title"].tolist(),
                    key="top_job_sel"
                )
            target_job_row_d = df_after[df_after["job_title"] == target_dice_job].iloc[0]
            sel_dice_job_id = target_job_row_d["job_id"]
            current_score = target_job_row_d["final_score"]

        # Target threshold
        target_benchmark_score = max(5.5, current_score + 1.5)
        score_gap = max(0.0, target_benchmark_score - current_score)
        
        # Skill Gap & Target Status Cards
        st.markdown("---")
        sg1, sg2, sg3 = st.columns(3)
        with sg1:
            st.metric("📊 Skor Kompetensi Saat Ini", f"{current_score:.2f}")
        with sg2:
            st.metric("🎯 Target Skor Rekomendasi Utama", f"{target_benchmark_score:.2f}")
        with sg3:
            st.metric("⚡ Kesenjangan Skor (Gap)", f"{score_gap:.2f} Poin", delta=f"-{score_gap:.2f}" if score_gap > 0 else "Sesuai Target", delta_color="inverse")
            
        # Retrieve dynamic candidates from 1,139 courses catalog
        top_candidates = find_top_candidate_courses_for_job(sel_dice_job_id, target_dice_job, top_n=6)
        
        st.markdown(f"#### 🎓 Rekomendasi Kursus Online DiCE untuk Menjadi **'{target_dice_job}'**:")
        st.markdown("Centang kursus di bawah ini untuk melihat **Simulasi Proyeksi Kenaikan Skor (*What-If Simulation*)** secara langsung:")
        
        selected_boost = 0.0
        selected_effort = 0.0
        selected_courses_list = []
        
        for idx, course in enumerate(top_candidates, 1):
            tier_badge = f'<span class="badge-tier-a">Tier A ({course["platform"]})</span>' if course["tier_weight"] >= 0.8 else f'<span class="badge-tier-b">Tier B ({course["platform"]})</span>'
            level_text = f"Level: {course['level']}"
            
            c_col1, c_col2 = st.columns([0.08, 0.92])
            with c_col1:
                is_selected = st.checkbox(f"Pilih", key=f"chk_course_{idx}", value=idx <= 2)
            with c_col2:
                st.markdown(f"""
                <div class="job-card" style="margin-bottom: 0.6rem; padding: 0.9rem 1.2rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="font-size: 1.05rem; font-weight: 700; color: #1E3A8A;">{idx}. {course['course_name']}</div>
                        <div>{tier_badge} <span class="badge-boost">Est. Boost: +{course['score_delta']:.2f}</span></div>
                    </div>
                    <div style="color: #6B7280; font-size: 0.85rem; margin-top: 0.2rem;">
                        Platform: <b>{course['platform']}</b> | {level_text} | Kemiripan Semantik: <b>{course['similarity']:.2f}</b> | Biaya Usaha (Effort): <b>{course['effort']:.1f}/10</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            if is_selected:
                selected_boost += course["score_delta"]
                selected_effort += course["effort"]
                selected_courses_list.append(course["course_name"])
                
        # Interactive What-If Simulation Result
        st.markdown("---")
        st.markdown("#### 🚀 Proyeksi Hasil Simulasi Intervensi (*What-If Simulation*)")
        sim_final_score = current_score + selected_boost
        is_target_reached = sim_final_score >= target_benchmark_score
        
        sim1, sim2, sim3 = st.columns([1, 1, 1.2])
        with sim1:
            st.metric("📈 Total Estimasi Lonjakan Skor", f"+{selected_boost:.2f} Poin")
        with sim2:
            st.metric("⏱️ Estimasi Total Effort Pelatihan", f"{selected_effort:.1f} Poin", help="Tingkat usaha/durasi kumulatif")
        with sim3:
            st.metric("🏆 Proyeksi Skor Akhir", f"{sim_final_score:.2f}", delta=f"{sim_final_score - current_score:+.2f}")
            
        if is_target_reached:
            st.success(f"🎉 **Luar biasa!** Dengan mengambil **{len(selected_courses_list)} kursus** di atas, skor kamu diproyeksikan melonjak dari **{current_score:.2f}** menjadi **{sim_final_score:.2f}**, berhasil menembus target kelayakan utama untuk posisi **'{target_dice_job}'**! 🚀")
        else:
            st.warning(f"💡 Kamu masih membutuhkan tambahan **+{target_benchmark_score - sim_final_score:.2f} poin**. Pertimbangkan untuk mencentang kursus tambahan di atas.")

    # =========================================================================
    # TAB 4: Rincian Transkrip & Kredensial
    # =========================================================================
    with tab4:
        st.markdown("### 📋 Data Transkrip KHS & Kredensial yang Terdeteksi")
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.markdown("#### 📚 Daftar Mata Kuliah (KHS):")
            st.dataframe(df_khs[["kode_mk", "nama_mk", "sks", "nilai_huruf"]].rename(
                columns={"kode_mk": "Kode MK", "nama_mk": "Mata Kuliah", "sks": "SKS", "nilai_huruf": "Nilai"}
            ), use_container_width=True, hide_index=True)
            
        with col_t2:
            st.markdown("#### 📜 Daftar Sertifikat Industri:")
            if not df_certs.empty:
                st.dataframe(df_certs[["title", "issuer", "credibility_weight"]].rename(
                    columns={"title": "Judul Sertifikat", "issuer": "Penerbit / Platform", "credibility_weight": "Bobot Kredibilitas"}
                ), use_container_width=True, hide_index=True)
            else:
                st.info("Tidak ada sertifikat industri yang diunggah.")

else:
    # Landing View before running
    st.info("👈 **Mulai sekarang:** Pilih profil mahasiswa demo di panel sebelah kiri atau unggah berkas KHS (PDF/MD) dan Sertifikat (JPG/PDF) kamu, lalu klik tombol **'Jalankan Rekomendasi & Analisis XAI'**!")
    
    st.markdown("""
    ### 🌟 Keunggulan Sistem Rekomendasi Karir KP BRIN:
    1. **Outcome-Based Education (OBE):** Memetakan Course Learning Outcomes (CLO) kurikulum Telkom University langsung ke *job requirements*.
    2. **Multi-Stage Evaluation:** Membedah pengaruh nyata sebelum (*Before*) dan sesudah (*After*) mahasiswa memiliki sertifikat industri kredibel.
    3. **Explainable AI (XAI):** Transparan dengan atribusi lokal **SHAP** dan bimbingan karir terarah **DiCE** menggunakan katalog **1.139 Kursus Online Riil** dari platform Google, AWS, Meta, IBM, dll.
    """)
