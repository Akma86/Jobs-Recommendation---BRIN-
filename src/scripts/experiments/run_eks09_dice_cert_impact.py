import os
import sys
import subprocess
import pandas as pd
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
DATA_DIR = os.path.join(ROOT_DIR, "data", "Percobaan")
RESULTS_DIR = os.path.join(ROOT_DIR, "results", "Eksperimen_XAI", "EKS09_DiCE_Cert_Impact")
APP_SCRIPT = os.path.join(SRC_DIR, "prototype", "app.py")

STUDENT_DIR = "Coba_Mahasiswa_Fajar_Nugroho"

def log(m):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {m}")

def run_app(khs, cert, out_dir, use_dice=False):
    os.makedirs(out_dir, exist_ok=True)
    cmd = [sys.executable, APP_SCRIPT, "--khs", khs]
    if cert:
        cmd += ["--certs", cert]
        
    if use_dice:
        cmd += ["--xai-mode", "dice"]
    else:
        cmd += ["--skip-xai"]
        
    env = os.environ.copy()
    env["PYTHONPATH"] = SRC_DIR
    log(f"Running command: {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=out_dir, env=env)
    if r.returncode != 0:
        log(f"[ERROR] Pipeline failed with return code {r.returncode}")
        return False
    return True

def create_dummy_cert(output_path, cert_title):
    # Buat dummy description berdasarkan title
    desc_map = {
        "AWS Certified Solutions Architect": "Mampu merancang arsitektur cloud terdistribusi, mengimplementasikan solusi AWS yang aman, dan memahami layanan infrastruktur cloud secara mendalam.",
        "Google Data Analytics Certificate": "Mampu mengumpulkan, membersihkan, dan menganalisis data menggunakan SQL, R, dan Python, serta membuat visualisasi data dengan Tableau.",
        "TensorFlow Developer Certificate": "Mampu membangun model machine learning dan deep learning, mengimplementasikan neural networks, computer vision, dan natural language processing menggunakan TensorFlow.",
        "Certified Ethical Hacker (CEH)": "Mampu melakukan penetration testing, menemukan kerentanan sistem, dan menerapkan praktik cybersecurity untuk melindungi jaringan.",
        "Google UX Design Certificate": "Mampu merancang antarmuka pengguna (UI/UX) yang intuitif, membuat wireframe dan prototipe menggunakan Figma, serta melakukan riset pengguna.",
        "Microsoft Azure Fundamentals (AZ-900)": "Pemahaman fundamental tentang layanan cloud Microsoft Azure, konsep cloud computing, keamanan jaringan, dan manajemen infrastruktur.",
        "CompTIA Security+": "Mampu mengelola keamanan jaringan, mendeteksi ancaman cybersecurity, melakukan mitigasi risiko, dan memahami kriptografi dasar.",
        "PMI Project Management Professional (PMP)": "Mampu mengelola proyek skala besar dengan metode Agile dan Waterfall, merencanakan anggaran, memitigasi risiko, dan memimpin tim lintas fungsi."
    }
    
    desc = desc_map.get(cert_title, f"Sertifikasi profesional di bidang {cert_title} mencakup keahlian teknis tingkat lanjut, praktik terbaik industri, dan implementasi solusi nyata.")
    
    cert_data = [
        "title,issuer,has_assessment,issue_date,description_text,source_file,cert_id",
        f'"{cert_title}",DummyIssuer,True,2026-01-01,"{desc}",dummy_cert.md,cert_0'
    ]
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(cert_data))
    log(f"Created dummy certificate '{cert_title}' at {output_path}")

def run_eks09():
    log("=" * 60)
    log("EKS09: Dampak Counterfactual DiCE (A/B Testing Sertifikasi)")
    log("=" * 60)
    
    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_before = os.path.join(RESULTS_DIR, "Before_Cert")
    out_after = os.path.join(RESULTS_DIR, "After_Cert")
    
    base_dir = os.path.join(DATA_DIR, STUDENT_DIR)
    khs_path = os.path.join(base_dir, "transcript_parsed.csv")
    
    # 1. Before (With DiCE to get recommendations)
    log("1. Menjalankan pipeline SEBELUM sertifikasi (dengan DiCE)...")
    if not run_app(khs_path, None, out_before, use_dice=True):
        log("[ERROR] Gagal menjalankan pipeline sebelum sertifikasi.")
        return
        
    # 2. Parse DiCE Recommendations
    dice_out_path = os.path.join(out_before, "dice_counterfactuals.csv")
    if not os.path.exists(dice_out_path):
        log(f"[ERROR] File counterfactual tidak ditemukan di {dice_out_path}")
        return
        
    df_dice = pd.read_csv(dice_out_path)
    
    # Cari rekomendasi penambahan sertifikat
    cert_recommendations = df_dice[df_dice["intervention_type"] == "add_certificate"]
    
    if cert_recommendations.empty:
        log("[INFO] Tidak ada rekomendasi sertifikat dari DiCE untuk mahasiswa ini.")
        return
        
    # Cari pasangan job dan sertifikat yang paling masuk akal (semantic match)
    # DiCE secara naif merekomendasikan semua sertifikat dengan bobot +1.5, jadi kita harus pilih yang relevan
    target_rec = None
    for _, rec in cert_recommendations.iterrows():
        j_title = rec["job_title"].lower()
        c_title = rec["feature"].lower()
        if "ai engineer" in j_title and "aws" in c_title:
            target_rec = rec
            break
        elif "machine learning" in j_title or "ml" in j_title:
            if "tensorflow" in c_title:
                target_rec = rec
        elif "data" in j_title and "data" in c_title:
            if target_rec is None:
                target_rec = rec
        elif "developer" in j_title and "aws" in c_title:
            if target_rec is None:
                target_rec = rec
            
    if target_rec is None:
        target_rec = cert_recommendations.iloc[0] # Ambil yang pertama jika tidak ada yang cocok
        
    target_job_id = target_rec["job_id"]
    target_job_title = target_rec["job_title"]
    
    # Feature format: "Sertifikat: AWS Certified Solutions Architect"
    feature_text = target_rec["feature"]
    recommended_cert = feature_text.replace("Sertifikat: ", "").strip()
    
    log(f"DiCE merekomendasikan: '{recommended_cert}' untuk pekerjaan '{target_job_title}' (ID: {target_job_id})")
    
    # 3. Create Dummy Cert based on DiCE recommendation
    dummy_cert_path = os.path.join(RESULTS_DIR, "dice_dummy_certificates.csv")
    create_dummy_cert(dummy_cert_path, recommended_cert)
    
    # 4. After
    log(f"2. Menjalankan pipeline SESUDAH penambahan sertifikasi '{recommended_cert}'...")
    if not run_app(khs_path, dummy_cert_path, out_after, use_dice=False):
        log("[ERROR] Gagal menjalankan pipeline sesudah sertifikasi.")
        return
        
    # 5. Compare
    df_before = pd.read_csv(os.path.join(out_before, "final_recommendations.csv"))
    df_after = pd.read_csv(os.path.join(out_after, "final_recommendations.csv"))
    
    # Analyze the target job
    target_before = df_before[df_before["job_id"] == target_job_id]
    target_after = df_after[df_after["job_id"] == target_job_id]
    
    if target_before.empty:
        score_before = 0.0
        rank_before = ">ALL"
    else:
        score_before = target_before["final_score"].iloc[0]
        rank_before = target_before.index[0] + 1
        
    if target_after.empty:
        score_after = 0.0
        rank_after = ">ALL"
    else:
        score_after = target_after["final_score"].iloc[0]
        rank_after = target_after.index[0] + 1
        
    delta_score = score_after - score_before
    
    log(f"--- Hasil untuk {target_job_title} ---")
    log(f"Sebelum: Peringkat {rank_before}, Skor {score_before:.3f}")
    log(f"Sesudah: Peringkat {rank_after}, Skor {score_after:.3f}")
    log(f"Peningkatan: {delta_score:.3f}")
    
    # Generate Markdown Report
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    md_lines = [
        f"# Eksperimen XAI Sesi 5 - Dampak Counterfactual DiCE",
        f"*Tanggal: {now}*",
        f"*Mahasiswa: {STUDENT_DIR.replace('Coba_Mahasiswa_', '').replace('_', ' ')}*",
        "",
        "## EKS09 — Pengaruh Eksekusi Rekomendasi DiCE",
        "**Tujuan:** Menguji apakah mengikuti saran counterfactual (DiCE) benar-benar memberikan kenaikan skor pada pekerjaan target.",
        "",
        "### Rekomendasi DiCE",
        f"- **Pekerjaan Target:** {target_job_title}",
        f"- **Intervensi Disarankan:** Tambahkan sertifikat '{recommended_cert}'",
        "",
        "### Hasil Perbandingan (Target Job)",
        "| Metrik | Sebelum | Sesudah | Perubahan |",
        "|--------|---------|---------|-----------|",
        f"| **Peringkat** | {rank_before} | {rank_after} | {'Naik' if (isinstance(rank_before, int) and isinstance(rank_after, int) and rank_after < rank_before) else 'Tetap/Turun'} |",
        f"| **Skor** | {score_before:.3f} | {score_after:.3f} | +{delta_score:.3f} |",
        "",
        "### Top 10 Perubahan Keseluruhan",
        "| Pekerjaan | Peringkat Lama | Peringkat Baru | Skor Lama | Skor Baru | Kenaikan Skor |",
        "|-----------|----------------|----------------|-----------|-----------|---------------|"
    ]
    
    comparison = []
    top10_after = df_after.head(10).copy()
    
    for _, row in top10_after.iterrows():
        jid = row["job_id"]
        score_a = row["final_score"]
        title = row["job_title"]
        
        match_b = df_before[df_before["job_id"] == jid]
        if not match_b.empty:
            score_b = match_b["final_score"].iloc[0]
            rank_b = match_b.index[0] + 1
        else:
            score_b = 0.0
            rank_b = ">10"
            
        rank_a = row.name + 1
        delta = score_a - score_b
        
        comparison.append({
            "job_title": title,
            "rank_before": rank_b,
            "rank_after": rank_a,
            "score_before": round(score_b, 3),
            "score_after": round(score_a, 3),
            "score_increase": round(delta, 3),
            "is_target": jid == target_job_id
        })
        
        # Format for markdown
        is_target_marker = " (TARGET)" if jid == target_job_id else ""
        md_lines.append(f"| {title}{is_target_marker} | {rank_b} | {rank_a} | {score_b:.3f} | {score_a:.3f} | +{delta:.3f} |")
        
    comp_df = pd.DataFrame(comparison)
    csv_out = os.path.join(RESULTS_DIR, "EKS09_Before_vs_After.csv")
    comp_df.to_csv(csv_out, index=False)
    log(f"Disimpan: {csv_out}")
        
    if delta_score > 0:
        conclusion = [
            "### Kesimpulan Analisis",
            f"- Sesuai prediksi DiCE, dengan menambahkan sertifikat **{recommended_cert}**, skor kesesuaian untuk pekerjaan **{target_job_title}** meningkat sebesar **{delta_score:.3f}**.",
            "- Counterfactual DiCE (What-If Analysis) terbukti memberikan rekomendasi preskriptif yang benar-benar menaikkan ranking kandidat secara nyata di dalam sistem."
        ]
    else:
        conclusion = [
            "### Kesimpulan Analisis",
            f"- **Temuan Kritis:** DiCE memprediksi bahwa sertifikat **{recommended_cert}** akan menaikkan skor untuk **{target_job_title}**, namun pada kenyataannya skor **TIDAK NAIK** (peningkatan: {delta_score:.3f}).",
            "- Hal ini terjadi karena DiCE menggunakan asumsi heuristik (memberikan estimasi bobot rata-rata +1.5 untuk semua sertifikat baru).",
            "- Sementara itu, *Ranking Pipeline* (TF-IDF/Semantic Matcher) yang sesungguhnya mungkin menilai deskripsi sertifikat dummy tersebut tidak memiliki kesesuaian kata kunci yang cukup (Cosine Similarity = 0) dengan deskripsi pekerjaan spesifik tersebut.",
            "- **Implikasi XAI:** Counterfactual DiCE pada sistem NLP perlu dibuat lebih 'cerdas' agar tidak sekadar menyarankan sertifikat secara membabi buta, melainkan memperhitungkan probabilitas kemiripan teks (text similarity) dari sertifikat terhadap pekerjaan."
        ]
        
    md_lines += conclusion
    
    md_out = os.path.join(RESULTS_DIR, "LOGBOOK_SUMMARY_EKS09.md")
    with open(md_out, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    log(f"Disimpan: {md_out}")
    log("Eksperimen EKS09 selesai.")

if __name__ == "__main__":
    run_eks09()
