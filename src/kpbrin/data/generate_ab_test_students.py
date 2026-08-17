import os
import random
from datetime import date
from kpbrin.data.generate_dummy_students import (
    COURSE_CLO_CATALOG, GRADE_POINTS, GRADE_BASE_SCORE,
    score_to_grade, generate_khs_summary_table, generate_khs_clo_section,
    calculate_ipk, generate_certificate, generate_credential_id, generate_verification_code,
    format_tanggal_id, BULAN_ID
)

OUT_DIR_KHS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "Mahasiswa", "generated_markdown_khs")
OUT_DIR_CERT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "Mahasiswa", "generated_markdown_certificates")
os.makedirs(OUT_DIR_KHS, exist_ok=True)
os.makedirs(OUT_DIR_CERT, exist_ok=True)

# 5 Tracks (Cases)
TRACKS = {
    "Machine Learning": [
        "TensorFlow Developer Certificate",
        "DeepLearning.AI NLP Specialization",
        "Google Data Analytics",
        "Machine Learning Specialization",
        "Generative AI Fundamentals"
    ],
    "Web Development": [
        "AWS Certified Developer - Associate",
        "Meta Front-End Developer",
        "Docker Associate Training",
        "Scrum Fundamentals Certified"
    ],
    "Networking": [
        "CCNA",
        "AWS Cloud Practitioner",
        "Cisco CyberOps Associate",
        "Security+"
    ],
    "Sistem Informasi": [
        "ITIL Foundation",
        "Business Analysis Foundation",
        "Scrum Fundamentals Certified",
        "Project Management Professional (PMP)"
    ],
    "SAP": [
        "SAP Fundamentals",
        "SAP Certified Application Associate",
        "ITIL Foundation"
    ]
}

# New Issuers and Hours for the extra certs not in the original list
EXTRA_CERTS = {
    "AWS Certified Developer - Associate": ("Amazon Web Services (AWS)", 40),
    "Meta Front-End Developer": ("Meta (Coursera)", 80),
    "Project Management Professional (PMP)": ("PMI", 35),
    "SAP Certified Application Associate": ("SAP", 40)
}

def generate_custom_student_khs_data(is_good=True):
    hasil = []
    for course in COURSE_CLO_CATALOG:
        grade = random.choice(["A", "AB"]) if is_good else random.choice(["D", "E", "C"])
        clo_scores = []
        for clo in course["clos"]:
            base = GRADE_BASE_SCORE.get(grade, 60)
            score = base + random.randint(-5, 5)
            score = max(0, min(100, score))
            clo_scores.append({
                "clo_code": clo["clo_code"],
                "clo_desc": clo["clo_desc"],
                "bloom": clo["bloom"] or "-",
                "score": score,
            })
        hasil.append({
            "kode_mk": course.get("kode_mk", "-") or "-",
            "nama_mk": course["nama_mk"],
            "sks": course.get("sks", 3) or 3,
            "semester": course.get("semester", "-"),
            "grade": grade,
            "clo_scores": clo_scores,
        })
    return hasil

def generate_khs(student_name, track, is_good):
    khs_data = generate_custom_student_khs_data(is_good)
    ipk, total_sks = calculate_ipk(khs_data)

    md = f"""# Kartu Hasil Studi (KHS)

## {student_name.replace('_', ' ')}

- Program Studi: Sistem Informasi
- Spesialisasi: {track}
- Total SKS: {total_sks}
- IPK: {ipk:.2f} / 4.00

---

## Ringkasan Nilai per Mata Kuliah

{generate_khs_summary_table(khs_data)}

---

## Rincian Nilai per CLO (Course Learning Outcome)

{generate_khs_clo_section(khs_data)}
---

*Catatan: KHS ini men-cover seluruh mata kuliah pada katalog CLO OBE Sistem
Informasi (versi awal, seluruh mata kuliah disertakan). Nilai akhir per MK
serta skor per-CLO dibangkitkan secara otomatis untuk keperluan simulasi
data.*
"""
    return md

def generate_custom_certificate(student_name, track, cert_name, cert_index):
    # Retrieve issuer & hours
    from kpbrin.data.generate_dummy_students import CERT_ISSUERS, CERT_HOURS, random_issue_date
    issuer = CERT_ISSUERS.get(cert_name)
    hours = CERT_HOURS.get(cert_name)
    if not issuer:
        issuer, hours = EXTRA_CERTS.get(cert_name, ("Professional Certification Body", 20))
        
    issue_date = random_issue_date()
    valid_years = random.choice([2, 3])
    try:
        expiry_date = issue_date.replace(year=issue_date.year + valid_years)
    except ValueError:
        expiry_date = issue_date.replace(year=issue_date.year + valid_years, day=28)
        
    credential_id = generate_credential_id(student_name, cert_name)
    verification_code = generate_verification_code()
    score = random.randint(78, 99)
    full_name = student_name.replace("_", " ")

    md = f"""# Sertifikat Penyelesaian

---

## {cert_name}

Diberikan kepada:

### **{full_name}**

Program studi Sistem Informasi, spesialisasi {track}, telah berhasil
menyelesaikan seluruh materi dan penilaian pada program **"{cert_name}"**
yang diselenggarakan oleh **{issuer}**, dengan total durasi pelatihan
**{hours} jam**.

---

## Detail Sertifikat

| Keterangan | Nilai |
|---|---|
| Nama Penerima | {full_name} |
| Judul Sertifikasi | {cert_name} |
| Penyelenggara / Issuer | {issuer} |
| Tanggal Terbit | {format_tanggal_id(issue_date)} |
| Berlaku Hingga | {format_tanggal_id(expiry_date)} |
| Durasi Pelatihan | {hours} jam |
| Skor Akhir | {score}/100 |
| ID Kredensial | {credential_id} |
| Kode Verifikasi | {verification_code} |

---

## Cakupan Materi

- Konsep dan prinsip dasar {cert_name}.
- Studi kasus dan praktik penerapan pada konteks industri nyata.
- Latihan hands-on / proyek mini sebagai bagian dari penilaian akhir.
- Evaluasi akhir (ujian/proyek) dengan nilai kelulusan minimum yang telah terpenuhi.

---

*Sertifikat ini adalah dokumen simulasi/dummy yang dibangkitkan secara otomatis
untuk keperluan pengujian sistem, bukan sertifikat resmi dari {issuer}.
Verifikasi keaslian dapat dicek menggunakan ID Kredensial di atas pada
platform penyelenggara terkait.*
"""
    return md

STUDENT_PAIRS = {
    "Machine Learning": {
        "good": "Siti_Rahma_ML_Bagus",
        "bad": "Rizky_Maulana_ML_Jelek",
        "track_code": "ML",
    },
    "Web Development": {
        "good": "Budi_Santoso_Web_Bagus",
        "bad": "Bayu_Setiawan_Web_Jelek",
        "track_code": "Web",
    },
    "Networking": {
        "good": "Andi_Wijaya_Net_Bagus",
        "bad": "Kevin_Aditya_Net_Jelek",
        "track_code": "Net",
    },
    "Sistem Informasi": {
        "good": "Nadia_Putri_SI_Bagus",
        "bad": "Farhan_Hidayat_SI_Jelek",
        "track_code": "SI",
    },
    "SAP": {
        "good": "Dewi_Lestari_SAP_Bagus",
        "bad": "Ilham_Saputra_SAP_Jelek",
        "track_code": "SAP",
    },
}

def main():
    print("Generating A/B Test Students with Real Names & Tracks...")

    for track, pair_info in STUDENT_PAIRS.items():
        certs = TRACKS.get(track, [])
        
        student_good = pair_info["good"]
        student_bad = pair_info["bad"]
        
        # Student 1: Good Grades
        khs_good = generate_khs(student_good, track, is_good=True)
        with open(os.path.join(OUT_DIR_KHS, f"{student_good}_KHS.md"), "w", encoding="utf-8") as f:
            f.write(khs_good)
            
        student_good_cert_dir = os.path.join(OUT_DIR_CERT, student_good)
        os.makedirs(student_good_cert_dir, exist_ok=True)
        for i, cert in enumerate(certs, 1):
            cert_content = generate_custom_certificate(student_good, track, cert, i)
            slug = cert.lower().replace(" ", "_").replace("-", "").replace("/", "").replace("(", "").replace(")", "")
            with open(os.path.join(student_good_cert_dir, f"{student_good}_Certificate_{i}_{slug}.md"), "w", encoding="utf-8") as f:
                f.write(cert_content)
                
        # Student 2: Bad Grades
        khs_bad = generate_khs(student_bad, track, is_good=False)
        with open(os.path.join(OUT_DIR_KHS, f"{student_bad}_KHS.md"), "w", encoding="utf-8") as f:
            f.write(khs_bad)
            
        student_bad_cert_dir = os.path.join(OUT_DIR_CERT, student_bad)
        os.makedirs(student_bad_cert_dir, exist_ok=True)
        for i, cert in enumerate(certs, 1):
            cert_content = generate_custom_certificate(student_bad, track, cert, i)
            slug = cert.lower().replace(" ", "_").replace("-", "").replace("/", "").replace("(", "").replace(")", "")
            with open(os.path.join(student_bad_cert_dir, f"{student_bad}_Certificate_{i}_{slug}.md"), "w", encoding="utf-8") as f:
                f.write(cert_content)
                
        print(f"Generated A/B pair for {track}: {student_good} vs {student_bad} ({len(certs)} certs each)")

if __name__ == "__main__":
    main()
