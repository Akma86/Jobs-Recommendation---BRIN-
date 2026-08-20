# -*- coding: utf-8 -*-
"""
Generator for real & dummy multi-semester student transcripts (Semester 1 to Semester 6)
based on the real Telkom University S1 Sains Data curriculum from Akmal's KHS transcript.
"""

import os
import sys
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

GRADE_NUM = {"A": 4.0, "AB": 3.5, "B": 3.0, "BC": 2.5, "C": 2.0, "D": 1.0, "E": 0.0}
GRADE_WEIGHT = {"A": 0.85, "AB": 0.80, "B": 0.70, "BC": 0.60, "C": 0.55, "D": 0.50, "E": 0.0}

ROOT_DIR = r"D:\MAIN DATA\Documents\Semester 6\KP BRIN"
OUT_DIR = os.path.join(ROOT_DIR, "data", "Mahasiswa", "multi_semester_khs")
os.makedirs(OUT_DIR, exist_ok=True)

# Master Course List Smt 1 - 6 (42 Mata Kuliah / 117 SKS)
courses = [
    # Semester 1 (18 SKS)
    {"semester": 1, "kode_mk": "CII1D3", "nama_mk": "Kalkulus", "nama_mk_en": "Calculus", "sks": 3},
    {"semester": 1, "kode_mk": "CII1E3", "nama_mk": "Pendidikan Karakter", "nama_mk_en": "Character Building", "sks": 3},
    {"semester": 1, "kode_mk": "CII1B3", "nama_mk": "Logika Matematika", "nama_mk_en": "Mathematical Logic", "sks": 3},
    {"semester": 1, "kode_mk": "CSI1A2", "nama_mk": "Aljabar Linear untuk Sains Data", "nama_mk_en": "Linear Algebra for Data Science", "sks": 2},
    {"semester": 1, "kode_mk": "UKI1B2", "nama_mk": "Pendidikan Pancasila", "nama_mk_en": "Pancasila Education", "sks": 2},
    {"semester": 1, "kode_mk": "CII1A3", "nama_mk": "Pengenalan Pemrograman", "nama_mk_en": "Introduction to Programming", "sks": 3},
    {"semester": 1, "kode_mk": "UKI1C2", "nama_mk": "Bahasa Indonesia", "nama_mk_en": "Indonesian Language", "sks": 2},

    # Semester 2 (14 SKS)
    {"semester": 2, "kode_mk": "UAI1A2", "nama_mk": "Pendidikan Agama dan Etika Islam", "nama_mk_en": "Islamic Religious Education and Ethics", "sks": 2},
    {"semester": 2, "kode_mk": "CII1C2", "nama_mk": "Statistika", "nama_mk_en": "Statistics", "sks": 2},
    {"semester": 2, "kode_mk": "CSI1B3", "nama_mk": "Perancangan dan Implementasi Basis Data", "nama_mk_en": "Database Design and Implementation", "sks": 3},
    {"semester": 2, "kode_mk": "CII1F4", "nama_mk": "Algoritma Pemrograman", "nama_mk_en": "Programming Algorithm", "sks": 4},
    {"semester": 2, "kode_mk": "CII1G3", "nama_mk": "Matematika Diskrit", "nama_mk_en": "Discrete Mathematics", "sks": 3},

    # Semester 3 (26 SKS)
    {"semester": 3, "kode_mk": "CII2A3", "nama_mk": "Organisasi dan Arsitektur Komputer", "nama_mk_en": "Organization and Computer Architecture", "sks": 3},
    {"semester": 3, "kode_mk": "CSI2A3", "nama_mk": "Teori Peluang dan Implementasi", "nama_mk_en": "Probabilistic Theory and Implementation", "sks": 3},
    {"semester": 3, "kode_mk": "CDK2DAB3", "nama_mk": "Pemodelan, Simulasi, dan Optimasi", "nama_mk_en": "Modeling, Simulation and Optimization", "sks": 3},
    {"semester": 3, "kode_mk": "CDK2BAB2", "nama_mk": "Analisis Kompleksitas Algoritma", "nama_mk_en": "Algorithm Complexity Analysis", "sks": 2},
    {"semester": 3, "kode_mk": "UCKXADB2", "nama_mk": "Bahasa Inggris", "nama_mk_en": "English", "sks": 2},
    {"semester": 3, "kode_mk": "CDK2FAB3", "nama_mk": "Kecerdasan Buatan", "nama_mk_en": "Artificial Intelligence", "sks": 3},
    {"semester": 3, "kode_mk": "CDK2CAB3", "nama_mk": "Sistem Manajemen Basis Data", "nama_mk_en": "Database Management System", "sks": 3},
    {"semester": 3, "kode_mk": "CDK2AAB4", "nama_mk": "Struktur Data", "nama_mk_en": "Data Structures", "sks": 4},
    {"semester": 3, "kode_mk": "CDK2EAB3", "nama_mk": "Infrastruktur dan Platform untuk Sains Data", "nama_mk_en": "Infrastructure and Platforms for Data Science", "sks": 3},

    # Semester 4 (20 SKS)
    {"semester": 4, "kode_mk": "CDK2HAB3", "nama_mk": "Interaksi Manusia dan Komputer", "nama_mk_en": "Human and Computer Interaction", "sks": 3},
    {"semester": 4, "kode_mk": "CDK2IAB3", "nama_mk": "Sistem Operasi", "nama_mk_en": "Operating System", "sks": 3},
    {"semester": 4, "kode_mk": "CDK2JAB3", "nama_mk": "Analisa Data", "nama_mk_en": "Data Analysis", "sks": 3},
    {"semester": 4, "kode_mk": "CDK2KAB3", "nama_mk": "Perancangan Aplikasi Sains Data", "nama_mk_en": "Data Science Application Design", "sks": 3},
    {"semester": 4, "kode_mk": "CDK2LAB3", "nama_mk": "Metode Visualisasi Data", "nama_mk_en": "Data Visualization Methods", "sks": 3},
    {"semester": 4, "kode_mk": "CDK2MAB3", "nama_mk": "Pembelajaran Mesin", "nama_mk_en": "Machine Learning", "sks": 3},
    {"semester": 4, "kode_mk": "CDK2GDB2", "nama_mk": "Wawasan Global TIK", "nama_mk_en": "ICT Global Insights", "sks": 2},

    # Semester 5 (20 SKS)
    {"semester": 5, "kode_mk": "CDK3AAB3", "nama_mk": "Manajemen Proyek", "nama_mk_en": "Project Management", "sks": 3},
    {"semester": 5, "kode_mk": "CDK3EAB3", "nama_mk": "Analisis Deret Waktu", "nama_mk_en": "Time Series Analysis", "sks": 3},
    {"semester": 5, "kode_mk": "CDK3CAB3", "nama_mk": "Keamanan Data", "nama_mk_en": "Data Security", "sks": 3},
    {"semester": 5, "kode_mk": "CDK3GAB1", "nama_mk": "Sains Data untuk Masyarakat", "nama_mk_en": "Data Science for Society", "sks": 1},
    {"semester": 5, "kode_mk": "CDK3DAB3", "nama_mk": "Infrastruktur dan Teknologi Big Data", "nama_mk_en": "Big Data Infrastructure and Technology", "sks": 3},
    {"semester": 5, "kode_mk": "CDK3FAB3", "nama_mk": "Rekayasa Sistem Informasi", "nama_mk_en": "Information Systems Engineering", "sks": 3},
    {"semester": 5, "kode_mk": "CDK3BAB4", "nama_mk": "Pemrograman Berorientasi Objek", "nama_mk_en": "Object Oriented Programming", "sks": 4},

    # Semester 6 (19 SKS)
    {"semester": 6, "kode_mk": "UBKXACB2", "nama_mk": "Kewarganegaraan", "nama_mk_en": "Civics", "sks": 2},
    {"semester": 6, "kode_mk": "UCKXBDB2", "nama_mk": "Kewirausahaan", "nama_mk_en": "Entrepreneurship", "sks": 2},
    {"semester": 6, "kode_mk": "CDK3LAB3", "nama_mk": "Rekayasa dan Organisasi Sistem Big Data", "nama_mk_en": "Big Data Systems Engineering and Organization", "sks": 3},
    {"semester": 6, "kode_mk": "CDK3IAB3", "nama_mk": "Penambangan Teks", "nama_mk_en": "Text Mining", "sks": 3},
    {"semester": 6, "kode_mk": "CDK3JAB3", "nama_mk": "Teknologi Cloud Computing untuk Big Data and Data Analytics", "nama_mk_en": "Cloud Computing Technology for Big Data and Data Analytics", "sks": 3},
    {"semester": 6, "kode_mk": "CDK3HAB3", "nama_mk": "Sains Data pada Industri", "nama_mk_en": "Data Science in Industry", "sks": 3},
    {"semester": 6, "kode_mk": "CDK3KAC3", "nama_mk": "Proyek Sains Data (Capstone Project)", "nama_mk_en": "Data Science Project (Capstone Project)", "sks": 3},
]

# Student 1: Dian Puspita Sari (Persona: AI & Machine Learning Specialist)
grades_dian = {
    "CII1D3": "A", "CII1E3": "A", "CII1B3": "A", "CSI1A2": "A", "UKI1B2": "A", "CII1A3": "A", "UKI1C2": "A",
    "UAI1A2": "A", "CII1C2": "A", "CSI1B3": "A", "CII1F4": "A", "CII1G3": "A",
    "CII2A3": "AB", "CSI2A3": "A", "CDK2DAB3": "A", "CDK2BAB2": "A", "UCKXADB2": "A", "CDK2FAB3": "A", "CDK2CAB3": "A", "CDK2AAB4": "A", "CDK2EAB3": "AB",
    "CDK2HAB3": "A", "CDK2IAB3": "AB", "CDK2JAB3": "A", "CDK2KAB3": "A", "CDK2LAB3": "A", "CDK2MAB3": "A", "CDK2GDB2": "A",
    "CDK3AAB3": "AB", "CDK3EAB3": "A", "CDK3CAB3": "A", "CDK3GAB1": "A", "CDK3DAB3": "AB", "CDK3FAB3": "A", "CDK3BAB4": "A",
    "UBKXACB2": "A", "UCKXBDB2": "A", "CDK3LAB3": "AB", "CDK3IAB3": "A", "CDK3JAB3": "AB", "CDK3HAB3": "A", "CDK3KAC3": "A"
}

# Student 2: Reza Pratama Kurnia (Persona: Big Data & Cloud Engineering Specialist)
grades_reza = {
    "CII1D3": "A", "CII1E3": "AB", "CII1B3": "AB", "CSI1A2": "AB", "UKI1B2": "A", "CII1A3": "A", "UKI1C2": "A",
    "UAI1A2": "A", "CII1C2": "AB", "CSI1B3": "A", "CII1F4": "A", "CII1G3": "AB",
    "CII2A3": "A", "CSI2A3": "AB", "CDK2DAB3": "B", "CDK2BAB2": "AB", "UCKXADB2": "A", "CDK2FAB3": "AB", "CDK2CAB3": "A", "CDK2AAB4": "A", "CDK2EAB3": "A",
    "CDK2HAB3": "AB", "CDK2IAB3": "A", "CDK2JAB3": "AB", "CDK2KAB3": "AB", "CDK2LAB3": "B", "CDK2MAB3": "B", "CDK2GDB2": "A",
    "CDK3AAB3": "A", "CDK3EAB3": "B", "CDK3CAB3": "A", "CDK3GAB1": "A", "CDK3DAB3": "A", "CDK3FAB3": "A", "CDK3BAB4": "A",
    "UBKXACB2": "A", "UCKXBDB2": "A", "CDK3LAB3": "A", "CDK3IAB3": "AB", "CDK3JAB3": "A", "CDK3HAB3": "AB", "CDK3KAC3": "A"
}

# Real Akmal Transcript data
grades_akmal = {
    "CII1D3": "A", "CII1E3": "A", "CII1B3": "A", "CSI1A2": "A", "UKI1B2": "A", "CII1A3": "A", "UKI1C2": "A",
    "UAI1A2": "A", "CII1C2": "A", "CSI1B3": "A", "CII1F4": "A", "CII1G3": "A",
    "CII2A3": "A", "CSI2A3": "A", "CDK2DAB3": "AB", "CDK2BAB2": "B", "UCKXADB2": "A", "CDK2FAB3": "AB", "CDK2CAB3": "AB", "CDK2AAB4": "AB", "CDK2EAB3": "A",
    "CDK2HAB3": "A", "CDK2IAB3": "A", "CDK2JAB3": "B", "CDK2KAB3": "AB", "CDK2LAB3": "B", "CDK2MAB3": "AB", "CDK2GDB2": "A",
    "CDK3AAB3": "AB", "CDK3EAB3": "AB", "CDK3CAB3": "A", "CDK3GAB1": "A", "CDK3DAB3": "B", "CDK3FAB3": "AB", "CDK3BAB4": "AB",
    "UBKXACB2": "A", "UCKXBDB2": "A", "CDK3LAB3": "A", "CDK3IAB3": "A", "CDK3JAB3": "A", "CDK3HAB3": "A", "CDK3KAC3": "A"
}

students = [
    {
        "nim": "103052300008",
        "nama": "Akmal Yaasir Fauzaan",
        "file_prefix": "Akmal_Yaasir_Fauzaan",
        "prodi": "S1 Sains Data",
        "fakultas": "Informatika",
        "universitas": "Telkom University",
        "dosen_wali": "IYK / I WAYAN PALTON ANUWIKSA",
        "track": "Data Science & Machine Learning Specialist",
        "grades": grades_akmal,
    },
    {
        "nim": "103052300012",
        "nama": "Dian Puspita Sari",
        "file_prefix": "Dian_Puspita_Sari",
        "prodi": "S1 Sains Data",
        "fakultas": "Informatika",
        "universitas": "Telkom University",
        "dosen_wali": "RND / RATNA NUR DIANA",
        "track": "Artificial Intelligence & Predictive Modeling Specialist",
        "grades": grades_dian,
    },
    {
        "nim": "103052300045",
        "nama": "Reza Pratama Kurnia",
        "file_prefix": "Reza_Pratama_Kurnia",
        "prodi": "S1 Sains Data",
        "fakultas": "Informatika",
        "universitas": "Telkom University",
        "dosen_wali": "ADW / AGUS DWI WICAKSONO",
        "track": "Big Data Infrastructure & Cloud Computing Specialist",
        "grades": grades_reza,
    },
]


def main():
    print("=" * 80)
    print("GENERATING MULTI-SEMESTER KHS DATASETS (SEMESTER 1 - 6)")
    print("=" * 80)

    for s in students:
        rows = []
        total_points = 0.0
        total_sks = 0

        for c in courses:
            g = s["grades"].get(c["kode_mk"], "A")
            sks = c["sks"]
            am = GRADE_NUM[g]
            gw = GRADE_WEIGHT[g]
            total_points += am * sks
            total_sks += sks
            rows.append({
                "semester": c["semester"],
                "kode_mk": c["kode_mk"],
                "nama_mk": c["nama_mk"],
                "nama_mk_en": c["nama_mk_en"],
                "sks": sks,
                "nilai_huruf": g,
                "angka_mutu": am,
                "grade_weight": gw,
            })

        ipk = total_points / total_sks
        df_student = pd.DataFrame(rows)

        # 1. Save CSV
        csv_path = os.path.join(OUT_DIR, f"{s['file_prefix']}_transcript.csv")
        df_student.to_csv(csv_path, index=False)

        # 2. Save Markdown
        md_lines = [
            f"# DAFTAR NILAI HASIL STUDI MAHASISWA",
            f"**{s['universitas']} - Fakultas {s['fakultas']}**\n",
            f"- **NIM**: `{s['nim']}`",
            f"- **Nama**: **{s['nama']}**",
            f"- **Program Studi**: {s['prodi']}",
            f"- **Dosen Wali**: {s['dosen_wali']}",
            f"- **Spesialisasi**: {s['track']}",
            f"- **Total SKS Diselesaikan**: {total_sks} SKS",
            f"- **Indeks Prestasi Kumulatif (IPK)**: **{ipk:.2f}** / 4.00\n",
            "---",
        ]

        for smt in range(1, 7):
            smt_df = df_student[df_student["semester"] == smt]
            smt_sks = smt_df["sks"].sum()
            smt_ips = (smt_df["angka_mutu"] * smt_df["sks"]).sum() / smt_sks
            md_lines.append(f"\n### 📚 Semester {smt} ({smt_sks} SKS - IPS: {smt_ips:.2f})")
            md_lines.append("| No | Kode MK | Nama Mata Kuliah | Course Name (EN) | SKS | Nilai | Bobot |")
            md_lines.append("|:---|:---|:---|:---|:---:|:---:|:---:|")
            for i, r in smt_df.reset_index().iterrows():
                md_lines.append(
                    f"| {i+1} | {r['kode_mk']} | {r['nama_mk']} | {r['nama_mk_en']} | {r['sks']} | **{r['nilai_huruf']}** | {r['angka_mutu']:.1f} |"
                )

        md_lines.append("\n---")
        md_lines.append("### 🏆 Ringkasan Kelulusan per Tingkat")
        t1_df = df_student[df_student["semester"].isin([1, 2])]
        t2_df = df_student[df_student["semester"].isin([3, 4])]
        t3_df = df_student[df_student["semester"].isin([5, 6])]

        t1_sks = t1_df["sks"].sum()
        t1_ipk = (t1_df["angka_mutu"] * t1_df["sks"]).sum() / t1_sks
        t2_sks = t2_df["sks"].sum()
        t2_ipk = (t2_df["angka_mutu"] * t2_df["sks"]).sum() / t2_sks
        t3_sks = t3_df["sks"].sum()
        t3_ipk = (t3_df["angka_mutu"] * t3_df["sks"]).sum() / t3_sks

        md_lines.append(f"- **Tingkat I (Semester 1 - 2)**: {t1_sks} SKS | IPK: {t1_ipk:.2f}")
        md_lines.append(f"- **Tingkat II (Semester 3 - 4)**: {t2_sks} SKS | IPK: {t2_ipk:.2f}")
        md_lines.append(f"- **Tingkat III (Semester 5 - 6)**: {t3_sks} SKS | IPK: {t3_ipk:.2f}")
        md_lines.append(f"- **Total Kumulatif**: **{total_sks} SKS** | **IPK: {ipk:.2f}**\n")

        md_path = os.path.join(OUT_DIR, f"{s['file_prefix']}_KHS.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        print(f"✓ Generated: {s['nama']} (IPK: {ipk:.2f} - {total_sks} SKS)")
        print(f"  -> CSV : {csv_path}")
        print(f"  -> MD  : {md_path}\n")

    print("=" * 80)
    print("SUCCESS: All multi-semester student transcripts generated!")
    print("=" * 80)


if __name__ == "__main__":
    main()
