# -*- coding: utf-8 -*-
"""
Script to generate pure Student Data Markdown Report for 10 Students
(KHS Transcript, Academic Profile, and Industry Certification Portfolio),
without any Before/After recommendation sections.
"""

import os
import sys
import glob
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from kpbrin.core.issuer_tiers import get_certificate_credibility_weight

BASE_DIR = os.path.join(ROOT_DIR, "results", "Eksperimen_XAI", "EKS12_AB_Test")
KHS_DIR = os.path.join(ROOT_DIR, "data", "Mahasiswa", "generated_markdown_khs")
CERT_DIR = os.path.join(ROOT_DIR, "data", "Mahasiswa", "generated_markdown_certificates")
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

def parse_full_khs(khs_filename):
    khs_path = os.path.join(KHS_DIR, f"{khs_filename}_KHS.md")
    ipk_str = "N/A"
    sks_str = "67 SKS"
    courses = []
    grade_counts = {}
    
    if os.path.exists(khs_path):
        with open(khs_path, "r", encoding="utf-8") as f:
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
                continue
            elif in_table:
                if line_s.startswith("---") or line_s.startswith("##"):
                    in_table = False
                    continue
                if line_s.startswith("|") and not line_s.startswith("| No") and not line_s.startswith("|----"):
                    parts = [p.strip() for p in line_s.split("|")[1:-1]]
                    if len(parts) >= 6:
                        courses.append({
                            "no": parts[0],
                            "kode_mk": parts[1],
                            "nama_mk": parts[2],
                            "sks": parts[3],
                            "semester": parts[4],
                            "grade": parts[5]
                        })
                        g = parts[5]
                        grade_counts[g] = grade_counts.get(g, 0) + 1
    return ipk_str, sks_str, grade_counts, courses

def parse_student_certificates(folder_name):
    student_cert_folder = os.path.join(CERT_DIR, folder_name)
    cert_files = sorted(glob.glob(os.path.join(student_cert_folder, "*.md")))
    certs_data = []

    for md_path in cert_files:
        with open(md_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        detail = {}
        cakupan_lines = []
        in_detail = False
        in_cakupan = False

        for line in lines:
            stripped = line.strip()
            if stripped == "## Cakupan Materi":
                in_cakupan = True
                in_detail = False
                continue
            if in_cakupan:
                if stripped.startswith("##") or stripped == "---":
                    in_cakupan = False
                elif stripped.startswith("-"):
                    cakupan_lines.append(stripped.lstrip("- ").strip())
                continue
            if stripped == "## Detail Sertifikat":
                in_detail = True
                continue
            if in_detail:
                if stripped == "---" or (stripped.startswith("##") and stripped != "## Detail Sertifikat"):
                    in_detail = False
                    continue
                if stripped.startswith("|") and not stripped.startswith("| Keterangan") and not "|---" in stripped:
                    cols = [c.strip() for c in stripped.split("|")[1:-1]]
                    if len(cols) >= 2:
                        detail[cols[0]] = cols[1]

        title = detail.get("Judul Sertifikasi") or detail.get("Judul") or os.path.basename(md_path)
        issuer = detail.get("Penyelenggara / Issuer") or detail.get("Penyelenggara") or "Industry Partner"
        issue_date = detail.get("Tanggal Terbit", "-")
        expiry_date = detail.get("Berlaku Hingga", "-")
        duration = detail.get("Durasi Pelatihan", "-")
        score = detail.get("Skor Akhir", "-")
        cred_id = detail.get("ID Kredensial", "-")

        w, b = get_certificate_credibility_weight(issuer, bool(score), issue_date)
        tier_lbl = "Tier A (Kredibilitas 1.0)" if w >= 0.8 else "Tier B (Kredibilitas 0.8)"

        certs_data.append({
            "title": title,
            "issuer": issuer,
            "issue_date": issue_date,
            "expiry_date": expiry_date,
            "duration": duration,
            "score": score,
            "cred_id": cred_id,
            "weight": w,
            "tier_label": tier_lbl,
            "topics": cakupan_lines
        })

    return certs_data

def format_student_section(idx, name, track, profile, folder_name):
    ipk_val, sks_val, grade_counts, courses = parse_full_khs(folder_name)
    certs_data = parse_student_certificates(folder_name)
    is_good = "Bagus" in profile or "Tinggi" in profile

    lines = []
    lines.append(f"## {idx}. {name} — Peminatan: `{track}` ({profile})")
    lines.append("")

    # 1. Profile & Status
    lines.append("### 📋 Profil & Status Akademik Mahasiswa")
    lines.append(f"> **Nama Mahasiswa:** **{name}**  ")
    lines.append(f"> **Program Studi & Peminatan:** S1 Sistem Informasi — `{track}`  ")
    lines.append(f"> **Total Beban SKS:** {sks_val} (Kurikulum OBE Telkom University)  ")
    lines.append(f"> **Indeks Prestasi Kumulatif (IPK):** **`{ipk_val}`**  ")
    
    if is_good:
        status_badge = "🟢 **Kategori: Akademik Unggul (High Standing)**"
        narrative_desc = (
            f"Mahasiswa memiliki rekam jejak akademik yang **sangat kuat dan konsisten** di kelas. "
            f"Capaian pembelajaran lulusan (CLO) pada mata kuliah inti kurikulum terpenuhi dengan sangat memuaskan, "
            f"didominasi perolehan nilai **A** dan **AB**."
        )
    else:
        status_badge = "🔴 **Kategori: Akademik Rendah / Perlu Penguatan (Low Standing)**"
        narrative_desc = (
            f"Mahasiswa mengalami **kendala akademik pada perkuliahan reguler**, dengan perolehan nilai yang didominasi "
            f"oleh predikat **D**, **E**, dan **C**."
        )

    lines.append(f"> **Status Akademik:** {status_badge}  ")
    if grade_counts:
        grade_summary_str = ", ".join([f"Nilai {k}: {v} MK" for k, v in sorted(grade_counts.items())])
        lines.append(f"> **Distribusi Nilai KHS:** `{grade_summary_str}`  ")
    lines.append("")
    lines.append(f"{narrative_desc}")
    lines.append("")

    # 2. Complete KHS Table
    lines.append("### 📚 Daftar Nilai Mata Kuliah (KHS - Kartu Hasil Studi):")
    lines.append("| No | Kode MK | Nama Mata Kuliah | SKS | Semester | Nilai Akhir |")
    lines.append("|:---:|:---:|---|:---:|:---:|:---:|")
    for c in courses:
        lines.append(f"| {c['no']} | `{c['kode_mk']}` | {c['nama_mk']} | {c['sks']} | {c['semester']} | **{c['grade']}** |")
    lines.append("")

    # 3. Complete Certificates Table & Topic Scopes
    lines.append(f"### 📜 Portofolio {len(certs_data)} Sertifikasi Industri yang Dimiliki:")
    lines.append("| No | Judul Sertifikasi | Penyelenggara / Issuer | Tanggal Terbit | Durasi | Skor Akhir | Kredibilitas |")
    lines.append("|:---:|---|---|:---:|:---:|:---:|:---:|")
    for c_i, cert in enumerate(certs_data, 1):
        lines.append(f"| {c_i} | **{cert['title']}** | {cert['issuer']} | {cert['issue_date']} | {cert['duration']} | `{cert['score']}` | {cert['tier_label']} |")
    lines.append("")

    # Detailed Certificate Topic Breakdown
    lines.append("#### 📌 Rincian Cakupan Materi Teknis per Sertifikat:")
    for c_i, cert in enumerate(certs_data, 1):
        lines.append(f"**{c_i}. {cert['title']}** (*{cert['issuer']}* — ID: `{cert['cred_id']}`):")
        for topic in cert["topics"]:
            lines.append(f"- {topic}")
        lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)

def main():
    report = []
    report.append("# Rangkuman Data Profil 10 Mahasiswa (KHS & Portofolio Sertifikasi Industri)")
    report.append("")
    report.append("**Tanggal Evaluasi:** 18 Agustus 2026  ")
    report.append("**Lokasi Data:** `data/Mahasiswa/`  ")
    report.append("**Deskripsi Dokumen:** Rangkuman komprehensif profil 10 mahasiswa Sistem Informasi mencakup data akademik transkrip nilai KHS (IPK, SKS, daftar nilai per mata kuliah) serta portofolio sertifikasi industri resmi beserta cakupan kompetensi teknisnya.")
    report.append("")
    report.append("---")
    report.append("")

    # Executive Table
    report.append("## 🏆 Ringkasan Eksekutif Data 10 Profil Mahasiswa")
    report.append("")
    report.append("| No | Mahasiswa | Peminatan / Spesialisasi | Status Akademik | IPK | Total SKS | Sertifikat Dimiliki |")
    report.append("|:---:|---|:---:|:---:|:---:|:---:|:---:|")

    for idx, (name, track, profile, folder_name) in enumerate(STUDENTS, 1):
        ipk_val, sks_val, _, _ = parse_full_khs(folder_name)
        certs_data = parse_student_certificates(folder_name)
        status_lbl = "🟢 Akademik Unggul" if "Bagus" in profile else "🔴 Akademik Rendah"
        report.append(f"| {idx} | **{name}** | `{track}` | {status_lbl} | **`{ipk_val}`** | {sks_val} | **{len(certs_data)} Sertifikat** |")

    report.append("")
    report.append("---")
    report.append("")

    # Detailed Breakdown per Student
    for idx, (name, track, profile, folder_name) in enumerate(STUDENTS, 1):
        report.append(format_student_section(idx, name, track, profile, folder_name))

    full_text = "\n".join(report)
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(full_text)

    # Also save to docs
    docs_path = os.path.join(ROOT_DIR, "docs", "EKS12_AB_Test_Summary.md")
    os.makedirs(os.path.dirname(docs_path), exist_ok=True)
    with open(docs_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    print(f"SUCCESS! Clean Student Data Report (No Before/After) saved to:")
    print(f"  1. {OUTPUT_MD}")
    print(f"  2. {docs_path}")

if __name__ == "__main__":
    main()
