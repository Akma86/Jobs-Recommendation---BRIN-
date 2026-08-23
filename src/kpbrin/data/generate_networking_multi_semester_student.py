# -*- coding: utf-8 -*-
"""
Generate complete multi-semester student profile & certificates for:
Fajar Ramadhan Pratama (S1 Informatika / Teknik Komputer)
Specialization: Network Engineer & Cloud Infrastructure Specialist

Generates:
1. transcript.csv
2. sub_clo_detailed.csv
3. full_profile.json
4. KHS.md
5. 5 Industry Certificates (.md) matching Cisco, CompTIA, AWS Networking, MikroTik, and Red Hat.
"""

import os
import sys
import json
import random
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = r"D:\MAIN DATA\Documents\Semester 6\KP BRIN"
MULTI_KHS_DIR = os.path.join(ROOT_DIR, "data", "Mahasiswa", "multi_semester_khs")
MULTI_CERT_DIR = os.path.join(MULTI_KHS_DIR, "certificates")
GEN_CERT_DIR = os.path.join(ROOT_DIR, "data", "Mahasiswa", "generated_markdown_certificates")

os.makedirs(MULTI_KHS_DIR, exist_ok=True)
os.makedirs(MULTI_CERT_DIR, exist_ok=True)
os.makedirs(GEN_CERT_DIR, exist_ok=True)

STUDENT = {
    "name": "Fajar Ramadhan Pratama",
    "nim": "1301213088",
    "major": "S1 Informatika",
    "advisor": "Dr. Eng. Ir. Bambang Hermanto, S.T., M.T.",
    "role": "Network Engineer & Cloud Infrastructure Specialist",
    "prefix": "Fajar_Ramadhan_Net",
}

# 38 Courses across Semesters 1 to 6
COURSES_PLAN = [
    # Semester 1 (19 SKS)
    {"semester": "Semester 1", "kode_mk": "CII1D3", "nama_mk": "Kalkulus", "nama_mk_en": "Calculus", "sks": 3, "grade": "A", "gp": 4.0},
    {"semester": "Semester 1", "kode_mk": "CII1A3", "nama_mk": "Algoritma dan Pemrograman", "nama_mk_en": "Algorithm and Programming", "sks": 4, "grade": "A", "gp": 4.0},
    {"semester": "Semester 1", "kode_mk": "CII1B3", "nama_mk": "Logika dan Struktur Diskrit", "nama_mk_en": "Discrete Structures and Logic", "sks": 3, "grade": "A", "gp": 4.0},
    {"semester": "Semester 1", "kode_mk": "CII1E3", "nama_mk": "Internalisasi Budaya dan Pembentukan Karakter", "nama_mk_en": "Character Building", "sks": 2, "grade": "A", "gp": 4.0},
    {"semester": "Semester 1", "kode_mk": "UKI1C2", "nama_mk": "Bahasa Indonesia", "nama_mk_en": "Indonesian Language", "sks": 2, "grade": "A", "gp": 4.0},
    {"semester": "Semester 1", "kode_mk": "UCKXADB2", "nama_mk": "Bahasa Inggris", "nama_mk_en": "English", "sks": 2, "grade": "A", "gp": 4.0},
    {"semester": "Semester 1", "kode_mk": "UKI1B2", "nama_mk": "Pancasila", "nama_mk_en": "Pancasila Education", "sks": 3, "grade": "A", "gp": 4.0},

    # Semester 2 (19 SKS)
    {"semester": "Semester 2", "kode_mk": "CII1F4", "nama_mk": "Algoritma dan Struktur Data", "nama_mk_en": "Algorithms and Data Structures", "sks": 4, "grade": "A", "gp": 4.0},
    {"semester": "Semester 2", "kode_mk": "CII1J3", "nama_mk": "Pemrograman Berorientasi Objek", "nama_mk_en": "Object-Oriented Programming", "sks": 3, "grade": "A", "gp": 4.0},
    {"semester": "Semester 2", "kode_mk": "CII1G3", "nama_mk": "Matematika Diskrit", "nama_mk_en": "Discrete Mathematics", "sks": 3, "grade": "A", "gp": 4.0},
    {"semester": "Semester 2", "kode_mk": "CII1C2", "nama_mk": "Probabilitas dan Statistik", "nama_mk_en": "Probability and Statistics", "sks": 3, "grade": "A", "gp": 4.0},
    {"semester": "Semester 2", "kode_mk": "CSI1B3", "nama_mk": "Sistem Basis Data", "nama_mk_en": "Database Systems", "sks": 3, "grade": "A", "gp": 4.0},
    {"semester": "Semester 2", "kode_mk": "CII2E3", "nama_mk": "Etika Profesi", "nama_mk_en": "Professional Ethics", "sks": 3, "grade": "A", "gp": 4.0},

    # Semester 3 (19 SKS)
    {"semester": "Semester 3", "kode_mk": "CII2F3", "nama_mk": "Sistem Operasi", "nama_mk_en": "Operating Systems", "sks": 3, "grade": "A", "gp": 4.0},
    {"semester": "Semester 3", "kode_mk": "CII1GAB3", "nama_mk": "Jaringan Komputer", "nama_mk_en": "Computer Networks", "sks": 3, "grade": "A", "gp": 4.0},
    {"semester": "Semester 3", "kode_mk": "CII2I3", "nama_mk": "Desain dan Manajemen Jaringan Komputer", "nama_mk_en": "Network Design and Management", "sks": 3, "grade": "A", "gp": 4.0},
    {"semester": "Semester 3", "kode_mk": "CII2J3", "nama_mk": "Infrastruktur TI", "nama_mk_en": "IT Infrastructure", "sks": 3, "grade": "A", "gp": 4.0},
    {"semester": "Semester 3", "kode_mk": "CII2H2", "nama_mk": "Kepemimpinan dan Komunikasi Interpersonal", "nama_mk_en": "Leadership and Communication", "sks": 2, "grade": "A", "gp": 4.0},
    {"semester": "Semester 3", "kode_mk": "CII2D3", "nama_mk": "Pemrograman Web", "nama_mk_en": "Web Programming", "sks": 3, "grade": "A", "gp": 4.0},
    {"semester": "Semester 3", "kode_mk": "CII2K2", "nama_mk": "Administrasi Basisdata", "nama_mk_en": "Database Administration", "sks": 2, "grade": "A", "gp": 4.0},

    # Semester 4 (19 SKS)
    {"semester": "Semester 4", "kode_mk": "CII3C3", "nama_mk": "Keamanan Sistem Informasi", "nama_mk_en": "Information Systems Security", "sks": 3, "grade": "A", "gp": 4.0},
    {"semester": "Semester 4", "kode_mk": "CII3G3", "nama_mk": "Tata Kelola Keamanan Informasi", "nama_mk_en": "Information Security Governance", "sks": 3, "grade": "A", "gp": 4.0},
    {"semester": "Semester 4", "kode_mk": "CII3B3", "nama_mk": "Arsitektur dan Pengembangan Backend", "nama_mk_en": "Backend Architecture & Development", "sks": 3, "grade": "A", "gp": 4.0},
    {"semester": "Semester 4", "kode_mk": "CII3D3", "nama_mk": "Pengujian dan Implementasi Sistem", "nama_mk_en": "System Testing & Implementation", "sks": 3, "grade": "A", "gp": 4.0},
    {"semester": "Semester 4", "kode_mk": "CII3A3", "nama_mk": "Kecerdasan Artifisial dan Penerapannya", "nama_mk_en": "Artificial Intelligence & Applications", "sks": 3, "grade": "AB", "gp": 3.5},
    {"semester": "Semester 4", "kode_mk": "UCKXBDB2", "nama_mk": "Kewirausahaan", "nama_mk_en": "Entrepreneurship", "sks": 4, "grade": "A", "gp": 4.0},

    # Semester 5 (19 SKS)
    {"semester": "Semester 5", "kode_mk": "CII4A3", "nama_mk": "Komputasi Awan", "nama_mk_en": "Cloud Computing", "sks": 3, "grade": "A", "gp": 4.0},
    {"semester": "Semester 5", "kode_mk": "CII4D3", "nama_mk": "Pengembangan Sistem dan Operasi", "nama_mk_en": "DevOps & System Operations", "sks": 3, "grade": "A", "gp": 4.0},
    {"semester": "Semester 5", "kode_mk": "CII4E3", "nama_mk": "Forensika Digital", "nama_mk_en": "Digital Forensics", "sks": 3, "grade": "A", "gp": 4.0},
    {"semester": "Semester 5", "kode_mk": "CII4G3", "nama_mk": "Manajemen Layanan TI", "nama_mk_en": "IT Service Management", "sks": 3, "grade": "A", "gp": 4.0},
    {"semester": "Semester 5", "kode_mk": "CII4H3", "nama_mk": "Manajemen Proyek Tangkas", "nama_mk_en": "Agile Project Management", "sks": 3, "grade": "A", "gp": 4.0},
    {"semester": "Semester 5", "kode_mk": "CII4F4", "nama_mk": "Metode Penelitian Dan Penyusunan Karya Ilmiah", "nama_mk_en": "Research Methodology", "sks": 4, "grade": "A", "gp": 4.0},

    # Semester 6 (19 SKS)
    {"semester": "Semester 6", "kode_mk": "CII5G3", "nama_mk": "Proteksi Aset Informasi", "nama_mk_en": "Information Asset Protection", "sks": 3, "grade": "A", "gp": 4.0},
    {"semester": "Semester 6", "kode_mk": "CII5B4", "nama_mk": "Capstone Design & Project", "nama_mk_en": "Capstone Design & Project", "sks": 4, "grade": "A", "gp": 4.0},
    {"semester": "Semester 6", "kode_mk": "CII5H3", "nama_mk": "Tata Kelola dan Audit TI", "nama_mk_en": "IT Governance and Audit", "sks": 3, "grade": "A", "gp": 4.0},
    {"semester": "Semester 6", "kode_mk": "CII5F3", "nama_mk": "Teknologi Berkembang", "nama_mk_en": "Emerging Technologies", "sks": 3, "grade": "A", "gp": 4.0},
    {"semester": "Semester 6", "kode_mk": "CII5E2", "nama_mk": "Kerja Praktek dan Pengabdian Masyarakat", "nama_mk_en": "Internship & Community Service", "sks": 2, "grade": "A", "gp": 4.0},
    {"semester": "Semester 6", "kode_mk": "CII5I4", "nama_mk": "Pelatihan dan Sertifikasi", "nama_mk_en": "Training & Certification", "sks": 4, "grade": "A", "gp": 4.0},
]

CERTIFICATES_DATA = [
    {
        "id": 1,
        "slug": "cisco_ccna_200_301",
        "title": "Cisco Certified Network Associate (CCNA 200-301)",
        "issuer": "Cisco Systems",
        "tier": "TIER_A",
        "tier_weight": 1.0,
        "issue_date": "2024-07-15",
        "expiry_date": "2027-07-15",
        "duration_hours": 90,
        "score": "915/1000",
        "credential_id": "CERT-CSCO-CCNA-9948102A",
        "verification_code": "CSCO-VER-882104",
        "topics": [
            "Network fundamentals, IP routing (OSPFv2), and layer 2 switching (VLANs, 802.1Q trunking, EtherChannel).",
            "IP services: DHCP snooping, DNS, NAT/PAT, NTP, and SNMP configuration.",
            "Security fundamentals: Port security, dynamic ARP inspection, access control lists (ACLs), and wireless security (WPA3).",
            "Network automation and programmability using REST APIs, JSON data formats, Python, and Cisco DNA Center."
        ],
        "skills": ["Cisco IOS", "Routing & Switching", "OSPF", "VLAN", "Subnetting", "Network Security", "ACL", "NAT", "Network Automation"]
    },
    {
        "id": 2,
        "slug": "comptia_network_plus",
        "title": "CompTIA Network+ (N10-008)",
        "issuer": "CompTIA",
        "tier": "TIER_A",
        "tier_weight": 1.0,
        "issue_date": "2024-09-10",
        "expiry_date": "2027-09-10",
        "duration_hours": 75,
        "score": "840/900",
        "credential_id": "CERT-COMP-NET-7719203B",
        "verification_code": "COMP-VER-440192",
        "topics": [
            "Network architectures, Ethernet standards, wireless technologies (Wi-Fi 6), and fiber optic connectivity.",
            "Network operations, traffic analysis, performance monitoring (SNMP, NetFlow, Syslog), and disaster recovery.",
            "Network defense: Firewalls, IDS/IPS, VPN tunnels (IPsec/OpenVPN), zero trust network access (ZTNA), and hardening.",
            "Comprehensive troubleshooting methodologies for physical, data link, network, and application layer issues."
        ],
        "skills": ["Network Troubleshooting", "TCP/IP", "OSI Model", "DNS/DHCP", "VPN", "Firewalls", "Network Monitoring", "Wireshark"]
    },
    {
        "id": 3,
        "slug": "aws_certified_advanced_networking",
        "title": "AWS Certified Advanced Networking - Specialty",
        "issuer": "Amazon Web Services (AWS)",
        "tier": "TIER_A",
        "tier_weight": 1.0,
        "issue_date": "2024-11-05",
        "expiry_date": "2027-11-05",
        "duration_hours": 85,
        "score": "88/100",
        "credential_id": "CERT-AWS-ANS-5529104C",
        "verification_code": "AWS-VER-119382",
        "topics": [
            "Designing and implementing scalable, highly available hybrid IT network architectures on AWS cloud.",
            "Advanced routing architectures with AWS Transit Gateway, Direct Connect (DX), VPC Peering, and VPN CloudHub.",
            "Network security and edge protection: AWS Network Firewall, Route 53 Resolver, CloudFront, and AWS Shield DDoS mitigation.",
            "Network automation with AWS CloudFormation, Transit Gateway Network Manager, and VPC Flow Logs telemetry."
        ],
        "skills": ["AWS Cloud Networking", "VPC", "Direct Connect", "Transit Gateway", "Network Security", "Route 53", "CloudFront"]
    },
    {
        "id": 4,
        "slug": "mikrotik_mtcna",
        "title": "MikroTik Certified Network Associate (MTCNA)",
        "issuer": "MikroTik",
        "tier": "TIER_B",
        "tier_weight": 0.7,
        "issue_date": "2024-04-20",
        "expiry_date": "2027-04-20",
        "duration_hours": 60,
        "score": "92/100",
        "credential_id": "CERT-MTK-MTCNA-3381901D",
        "verification_code": "MTK-VER-774910",
        "topics": [
            "MikroTik RouterOS installation, Winbox GUI navigation, CLI management, and license configurations.",
            "Configuring DHCP server, client, and relay; DNS cache; and static routing with gateway failover.",
            "Stateful packet inspection firewall (filter rules, NAT/masquerade, mangle) and bandwidth management with Simple Queues.",
            "Point-to-point wireless networking, bridge setup, hotspot gateway, and secure PPTP/L2TP/SSTP VPN tunnels."
        ],
        "skills": ["MikroTik RouterOS", "Bandwidth Management", "Firewall", "NAT", "PPPoE", "VPN", "Routing", "QoS"]
    },
    {
        "id": 5,
        "slug": "red_hat_rhcsa",
        "title": "Red Hat Certified System Administrator (RHCSA)",
        "issuer": "Red Hat",
        "tier": "TIER_A",
        "tier_weight": 1.0,
        "issue_date": "2024-10-18",
        "expiry_date": "2027-10-18",
        "duration_hours": 80,
        "score": "285/300",
        "credential_id": "CERT-RHT-RHCSA-1102948E",
        "verification_code": "RHT-VER-993821",
        "topics": [
            "Linux system administration, bash shell scripting, systemd service and socket unit management.",
            "Configuring network interfaces (NetworkManager, nmcli), static IP, hostname resolution, and firewalld rules.",
            "Managing storage volumes: LVM partition creation, resizing, Stratis, and NFS/Samba network share mounting.",
            "Deploying and managing containerized network services using Podman and enforcing mandatory access controls with SELinux."
        ],
        "skills": ["Linux", "RHEL", "System Administration", "Bash Scripting", "Networking", "Firewalld", "LVM", "Podman", "SELinux"]
    }
]

def format_date_id(date_str):
    months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
              "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    y, m, d = date_str.split("-")
    return f"{int(d)} {months[int(m)-1]} {y}"

def generate_markdown_cert(student, cert):
    topics_md = "\n".join([f"- {t}" for t in cert["topics"]])
    md = f"""# Sertifikat Penyelesaian

---

## {cert['title']}

Diberikan kepada:

### **{student['name']}**

Program studi {student['major']}, spesialisasi {student['role']}, telah berhasil
menyelesaikan seluruh materi dan penilaian pada program **"{cert['title']}"**
yang diselenggarakan oleh **{cert['issuer']}**, dengan total durasi pelatihan
**{cert['duration_hours']} jam**.

---

## Detail Sertifikat

| Keterangan | Nilai |
|---|---|
| Nama Penerima | {student['name']} |
| Judul Sertifikasi | {cert['title']} |
| Penyelenggara / Issuer | {cert['issuer']} |
| Tanggal Terbit | {format_date_id(cert['issue_date'])} |
| Berlaku Hingga | {format_date_id(cert['expiry_date'])} |
| Durasi Pelatihan | {cert['duration_hours']} jam |
| Skor Akhir | {cert['score']} |
| ID Kredensial | {cert['credential_id']} |
| Kode Verifikasi | {cert['verification_code']} |

---

## Cakupan Materi

{topics_md}
- Evaluasi akhir (ujian/proyek) dengan nilai kelulusan minimum yang telah terpenuhi.

---

*Sertifikat ini adalah dokumen simulasi/dummy yang dibangkitkan secara otomatis
untuk keperluan pengujian sistem, bukan sertifikat resmi dari {cert['issuer']}.
Verifikasi keaslian dapat dicek menggunakan ID Kredensial di atas pada
platform penyelenggara terkait.*
"""
    return md

def main():
    print("Generating complete multi-semester profile & certificates for Fajar Ramadhan Pratama...")
    random.seed(42)

    # 1. Load Sub-CLO Master Catalog
    sub_clo_path = os.path.join(ROOT_DIR, "data", "Mata Kuliah", "sub_clo_profiles.csv")
    df_sub_master = pd.read_csv(sub_clo_path)

    transcript_rows = []
    sub_clo_detailed_rows = []
    courses_json_list = []

    total_pts = 0.0
    total_sks = 0

    for idx, c in enumerate(COURSES_PLAN, 1):
        c_name = c["nama_mk"]
        c_code = c["kode_mk"]
        c_sks = c["sks"]
        c_grade = c["grade"]
        c_gp = c["gp"]
        c_smt = c["semester"]

        total_pts += c_gp * c_sks
        total_sks += c_sks

        # Lookup sub-CLOs
        sub_df = df_sub_master[df_sub_master["course_name"] == c_name]
        if sub_df.empty:
            # Fallback sub-CLO
            sub_clos = [
                {"code": f"CLO-{i+1:02d}", "text": f"Mampu menguasai kompetensi dasar dan terapan pada {c_name} secara komprehensif.", "bloom": "3 - Apply"}
                for i in range(3)
            ]
        else:
            sub_clos = []
            for _, r_sub in sub_df.iterrows():
                sub_clos.append({
                    "code": str(r_sub["sub_clo_code"]),
                    "text": str(r_sub["sub_clo_text"]),
                    "bloom": "3 - Apply" if "mampu" in str(r_sub["sub_clo_text"]).lower() else "2 - Understand"
                })

        scores = []
        course_sub_json = []
        for s_clo in sub_clos:
            base_score = 92.0 if c_grade == "A" else 83.0
            sc = round(base_score + random.uniform(-3.5, 4.5), 1)
            sc = max(75.0, min(99.0, sc))
            scores.append(sc)

            sub_clo_detailed_rows.append({
                "nim": STUDENT["nim"],
                "nama_mahasiswa": STUDENT["name"],
                "jurusan": STUDENT["major"],
                "semester": c_smt,
                "kode_mk": c_code,
                "nama_mk": c_name,
                "sks": c_sks,
                "nilai_akhir_mk": c_grade,
                "sub_clo_code": s_clo["code"],
                "sub_clo_text": s_clo["text"],
                "bloom_taxonomy": s_clo["bloom"],
                "sub_clo_score": sc,
                "sub_clo_grade": c_grade
            })

            course_sub_json.append({
                "sub_clo_code": s_clo["code"],
                "sub_clo_text": s_clo["text"],
                "bloom_taxonomy": s_clo["bloom"],
                "sub_clo_score": sc,
                "sub_clo_grade": c_grade
            })

        avg_score = round(sum(scores) / len(scores), 1) if scores else 90.0

        transcript_rows.append({
            "no": idx,
            "semester": c_smt,
            "kode_mk": c_code,
            "nama_mk": c_name,
            "nama_mk_en": c["nama_mk_en"],
            "sks": c_sks,
            "nilai_huruf": c_grade,
            "bobot_ipk": c_gp,
            "skor_rata_sub_clo": avg_score,
            "jumlah_sub_clo": len(sub_clos)
        })

        courses_json_list.append({
            "no": idx,
            "semester": c_smt,
            "kode_mk": c_code,
            "nama_mk": c_name,
            "nama_mk_en": c["nama_mk_en"],
            "sks": c_sks,
            "nilai_huruf": c_grade,
            "bobot_ipk": c_gp,
            "skor_rata_sub_clo": avg_score,
            "jumlah_sub_clo": len(sub_clos),
            "sub_clos": course_sub_json
        })

    ipk = round(total_pts / total_sks, 2)
    print(f"Total SKS: {total_sks}, IPK: {ipk:.2f}")

    # 1. Save Transcript CSV
    df_transcript = pd.DataFrame(transcript_rows)
    t_csv_path = os.path.join(MULTI_KHS_DIR, f"{STUDENT['prefix']}_transcript.csv")
    df_transcript.to_csv(t_csv_path, index=False)
    print(f"✓ Saved transcript CSV: {t_csv_path}")

    # 2. Save Sub-CLO Detailed CSV
    df_sub_detailed = pd.DataFrame(sub_clo_detailed_rows)
    s_csv_path = os.path.join(MULTI_KHS_DIR, f"{STUDENT['prefix']}_sub_clo_detailed.csv")
    df_sub_detailed.to_csv(s_csv_path, index=False)
    print(f"✓ Saved sub-CLO detailed CSV ({len(df_sub_detailed)} sub-CLOs): {s_csv_path}")

    # 3. Save Full Profile JSON
    semester_summaries = []
    for smt_num in range(1, 7):
        smt_str = f"Semester {smt_num}"
        smt_courses = [c for c in courses_json_list if c["semester"] == smt_str]
        smt_sks = sum(c["sks"] for c in smt_courses)
        smt_pts = sum(c["bobot_ipk"] * c["sks"] for c in smt_courses)
        ips = round(smt_pts / max(1, smt_sks), 2)
        semester_summaries.append({
            "semester": smt_str,
            "sks_semester": smt_sks,
            "ips_semester": ips,
            "courses": smt_courses
        })

    full_profile = {
        "metadata": {
            "name": STUDENT["name"],
            "nim": STUDENT["nim"],
            "major": STUDENT["major"],
            "advisor": STUDENT["advisor"],
            "role_specialization": STUDENT["role"],
            "total_sks": total_sks,
            "cumulative_gpa": ipk,
            "semester_range": "Semester 1 - 6",
            "total_courses": len(COURSES_PLAN),
            "total_sub_clos": len(sub_clo_detailed_rows)
        },
        "semester_summaries": semester_summaries
    }
    json_path = os.path.join(MULTI_KHS_DIR, f"{STUDENT['prefix']}_full_profile.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(full_profile, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved full profile JSON: {json_path}")

    # 4. Save KHS.md
    khs_lines = [
        "# Kartu Hasil Studi (KHS)",
        "",
        f"## {STUDENT['name']}",
        "",
        f"- Program Studi: {STUDENT['major']}",
        f"- Spesialisasi: {STUDENT['role']}",
        f"- Total SKS: {total_sks}",
        f"- IPK: {ipk:.2f} / 4.00",
        "",
        "---",
        "",
        "## Ringkasan Nilai per Mata Kuliah",
        "",
        "| No | Kode MK | Nama Mata Kuliah | SKS | Semester | Nilai Akhir |",
        "|----|---------|-------------------|-----|----------|-------------|"
    ]

    for idx, c in enumerate(COURSES_PLAN, 1):
        khs_lines.append(f"| {idx} | {c['kode_mk']} | {c['nama_mk']} | {c['sks']} | {c['semester']} | {c['grade']} |")

    khs_lines.append("")
    khs_lines.append("---")
    khs_lines.append("")
    khs_lines.append("## Rincian Nilai per CLO (Course Learning Outcome)")
    khs_lines.append("")

    for c in courses_json_list:
        khs_lines.append(f"### {c['nama_mk']} ({c['kode_mk']}) - {c['sks']} SKS - Nilai Akhir: {c['nilai_huruf']}")
        khs_lines.append("")
        khs_lines.append("| CLO | Deskripsi CLO | Bloom Taxonomy | Skor CLO (0-100) | Nilai CLO |")
        khs_lines.append("|:---|:---|:---|:---:|:---:|")
        for sc in c["sub_clos"]:
            khs_lines.append(f"| {sc['sub_clo_code']} | {sc['sub_clo_text']} | {sc['bloom_taxonomy']} | {sc['sub_clo_score']:.1f} | {sc['sub_clo_grade']} |")
        khs_lines.append("")

    khs_md_path = os.path.join(MULTI_KHS_DIR, f"{STUDENT['prefix']}_KHS.md")
    with open(khs_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(khs_lines))
    print(f"✓ Saved KHS markdown: {khs_md_path}")

    # 5. Generate Certificates Markdown
    st_multi_cert_dir = os.path.join(MULTI_CERT_DIR, STUDENT["prefix"])
    st_gen_cert_dir = os.path.join(GEN_CERT_DIR, STUDENT["prefix"])
    os.makedirs(st_multi_cert_dir, exist_ok=True)
    os.makedirs(st_gen_cert_dir, exist_ok=True)

    for cert in CERTIFICATES_DATA:
        md_c = generate_markdown_cert(STUDENT, cert)
        fname = f"{STUDENT['prefix']}_Certificate_{cert['id']}_{cert['slug']}.md"
        with open(os.path.join(st_multi_cert_dir, fname), "w", encoding="utf-8") as f:
            f.write(md_c)
        with open(os.path.join(st_gen_cert_dir, fname), "w", encoding="utf-8") as f:
            f.write(md_c)
        print(f"  ✓ Generated Cert #{cert['id']}: {cert['title']}")

    print("\nSUCCESS: All student data & certificates generated successfully!")

if __name__ == "__main__":
    main()
