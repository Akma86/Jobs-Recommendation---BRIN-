# -*- coding: utf-8 -*-
"""
Generate 5 dummy industry certificates per student matching their roles:
1. Arya Pratama Putra (S1 Informatika) -> Software Engineer / Full-Stack & Cloud Developer
2. Nabila Putri Maharani (S1 Sistem Informasi) -> Business / Data Analyst & Enterprise Systems Specialist

Formats adhere strictly to parse_certificate_markdown specifications in parse_input.py.
"""

import os
import sys
import json
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = r"D:\MAIN DATA\Documents\Semester 6\KP BRIN"
CERT_GEN_DIR = os.path.join(ROOT_DIR, "data", "Mahasiswa", "generated_markdown_certificates")
MULTI_KHS_DIR = os.path.join(ROOT_DIR, "data", "Mahasiswa", "multi_semester_khs")
MULTI_CERT_DIR = os.path.join(MULTI_KHS_DIR, "certificates")

os.makedirs(CERT_GEN_DIR, exist_ok=True)
os.makedirs(MULTI_CERT_DIR, exist_ok=True)

STUDENTS_CERTS = [
    {
        "student_name": "Arya Pratama Putra",
        "nim": "1301213012",
        "major": "S1 Informatika",
        "role": "Full-Stack Software Engineer & Cloud Architecture",
        "folder_name": "Arya_Pratama_Putra_Informatika",
        "certificates": [
            {
                "id": 1,
                "slug": "aws_solutions_architect_associate",
                "title": "AWS Certified Solutions Architect - Associate",
                "issuer": "Amazon Web Services (AWS)",
                "tier": "TIER_A",
                "tier_weight": 1.0,
                "issue_date": "2024-08-15",
                "expiry_date": "2027-08-15",
                "duration_hours": 80,
                "score": "89/100",
                "credential_id": "CERT-AWS-SAA-8492019A",
                "verification_code": "AWS-VER-992147",
                "topics": [
                    "Design resilient, high-performing, and secure architectures on AWS cloud.",
                    "Multi-tier application deployment using Amazon EC2, ECS, AWS Lambda, and RDS.",
                    "VPC networking, security groups, IAM role policies, and CloudWatch monitoring.",
                    "Cost optimization, disaster recovery strategies, and storage management (S3, EFS, EBS)."
                ],
                "skills": ["AWS Cloud", "Microservices", "EC2", "S3", "Lambda", "RDS", "VPC", "Cloud Architecture"]
            },
            {
                "id": 2,
                "slug": "google_professional_cloud_developer",
                "title": "Google Professional Cloud Developer",
                "issuer": "Google Cloud",
                "tier": "TIER_A",
                "tier_weight": 1.0,
                "issue_date": "2024-11-20",
                "expiry_date": "2026-11-20",
                "duration_hours": 70,
                "score": "92/100",
                "credential_id": "CERT-GCP-PCD-7738291B",
                "verification_code": "GCP-VER-338190",
                "topics": [
                    "Building highly scalable and available cloud-native applications on Google Cloud Platform.",
                    "Containerization with Docker and orchestration using Google Kubernetes Engine (GKE).",
                    "Continuous integration and continuous deployment (CI/CD) pipelines with Cloud Build.",
                    "Implementing serverless backend architectures with Cloud Run and Cloud Functions."
                ],
                "skills": ["Google Cloud", "Kubernetes", "Docker", "GKE", "CI/CD", "Cloud Run", "Serverless"]
            },
            {
                "id": 3,
                "slug": "meta_front_end_developer",
                "title": "Meta Front-End Developer Professional Certificate",
                "issuer": "Meta",
                "tier": "TIER_A",
                "tier_weight": 1.0,
                "issue_date": "2024-05-10",
                "expiry_date": "2027-05-10",
                "duration_hours": 65,
                "score": "95/100",
                "credential_id": "CERT-META-FED-5541908C",
                "verification_code": "META-VER-441209",
                "topics": [
                    "Modern frontend development with React.js, component lifecycle, hooks, and context API.",
                    "Advanced JavaScript (ES6+), asynchronous programming, and RESTful API integration.",
                    "Responsive UI design, CSS architecture, TailwindCSS, and accessibility (a11y) standards.",
                    "Version control collaboration with Git and GitHub, unit testing with Jest."
                ],
                "skills": ["React.js", "JavaScript", "HTML5/CSS3", "REST APIs", "Git", "Jest", "UI/UX"]
            },
            {
                "id": 4,
                "slug": "dicoding_backend_developer_expert",
                "title": "Menjadi Back-End Developer Expert",
                "issuer": "Dicoding",
                "tier": "TIER_B",
                "tier_weight": 0.7,
                "issue_date": "2024-03-25",
                "expiry_date": "2027-03-25",
                "duration_hours": 90,
                "score": "96/100",
                "credential_id": "CERT-DCD-BDE-1029481D",
                "verification_code": "DCD-VER-882194",
                "topics": [
                    "Designing robust backend architectures following Clean Architecture and Domain-Driven Design.",
                    "Building RESTful APIs with Node.js, Express/Hapi, and PostgreSQL with database migrations.",
                    "Message broker integration (RabbitMQ), caching with Redis, and automated CI testing.",
                    "Security hardening: JWT authentication, rate limiting, and SQL injection prevention."
                ],
                "skills": ["Node.js", "Express.js", "Clean Architecture", "PostgreSQL", "Redis", "RabbitMQ", "JWT"]
            },
            {
                "id": 5,
                "slug": "cka_certified_kubernetes_administrator",
                "title": "Certified Kubernetes Administrator (CKA)",
                "issuer": "Linux Foundation / CNCF",
                "tier": "TIER_A",
                "tier_weight": 1.0,
                "issue_date": "2025-01-18",
                "expiry_date": "2028-01-18",
                "duration_hours": 75,
                "score": "88/100",
                "credential_id": "CERT-CNCF-CKA-6619028E",
                "verification_code": "CKA-VER-771920",
                "topics": [
                    "Kubernetes cluster architecture, installation, configuration, and multi-node setup.",
                    "Workloads management, deployments, daemonsets, and statefulsets configuration.",
                    "Cluster networking, ingress controllers, network policies, and persistent storage management.",
                    "Troubleshooting cluster components, node failures, and security auditing."
                ],
                "skills": ["Kubernetes", "DevOps", "Containers", "Ingress", "Storage", "Linux", "Troubleshooting"]
            }
        ]
    },
    {
        "student_name": "Nabila Putri Maharani",
        "nim": "1202210088",
        "major": "S1 Sistem Informasi",
        "role": "Data / Business Analyst & Enterprise Systems Specialist",
        "folder_name": "Nabila_Putri_Maharani_SI",
        "certificates": [
            {
                "id": 1,
                "slug": "google_data_analytics_professional",
                "title": "Google Data Analytics Professional Certificate",
                "issuer": "Google",
                "tier": "TIER_A",
                "tier_weight": 1.0,
                "issue_date": "2024-04-12",
                "expiry_date": "2027-04-12",
                "duration_hours": 70,
                "score": "94/100",
                "credential_id": "CERT-GDA-9182301A",
                "verification_code": "GDA-VER-662910",
                "topics": [
                    "End-to-end data analysis lifecycle: data asking, preparing, processing, analyzing, and sharing.",
                    "Advanced SQL queries: subqueries, window functions, aggregation, and joining multi-table schemas.",
                    "Data visualization and dynamic business storytelling with Tableau and spreadsheets.",
                    "Statistical analysis and predictive data programming using R and tidyverse packages."
                ],
                "skills": ["SQL", "Data Analytics", "Tableau", "R Programming", "Data Cleaning", "Data Visualization"]
            },
            {
                "id": 2,
                "slug": "microsoft_power_bi_data_analyst",
                "title": "Microsoft Certified: Power BI Data Analyst Associate",
                "issuer": "Microsoft",
                "tier": "TIER_A",
                "tier_weight": 1.0,
                "issue_date": "2024-07-28",
                "expiry_date": "2026-07-28",
                "duration_hours": 60,
                "score": "91/100",
                "credential_id": "CERT-MSFT-PL300-449102B",
                "verification_code": "MSFT-VER-119283",
                "topics": [
                    "Preparing and transforming complex data sources using Power Query and ETL transformations.",
                    "Designing dimensional data models (Star schema, Snowflake schema) with DAX calculations.",
                    "Developing executive KPI dashboards, row-level security (RLS), and automated report refreshes.",
                    "Deploying and managing workspaces, datasets, and apps in Power BI Service."
                ],
                "skills": ["Power BI", "DAX", "Data Modeling", "Business Intelligence", "Power Query", "Dashboards"]
            },
            {
                "id": 3,
                "slug": "ibm_data_engineering_professional",
                "title": "IBM Data Engineering Professional Certificate",
                "issuer": "IBM",
                "tier": "TIER_A",
                "tier_weight": 1.0,
                "issue_date": "2024-09-14",
                "expiry_date": "2027-09-14",
                "duration_hours": 85,
                "score": "89/100",
                "credential_id": "CERT-IBM-DEP-8830192C",
                "verification_code": "IBM-VER-772910",
                "topics": [
                    "Enterprise data engineering foundations, Relational and NoSQL database management.",
                    "Building robust ETL and data pipelines with Python, SQL, and Apache Airflow.",
                    "Big Data processing with Apache Spark and data warehousing architectures.",
                    "Data governance, metadata management, and pipeline orchestration."
                ],
                "skills": ["Data Engineering", "Apache Airflow", "Data Warehousing", "ETL", "Apache Spark", "NoSQL"]
            },
            {
                "id": 4,
                "slug": "google_project_management_professional",
                "title": "Google Project Management Professional Certificate",
                "issuer": "Google",
                "tier": "TIER_A",
                "tier_weight": 1.0,
                "issue_date": "2024-11-05",
                "expiry_date": "2027-11-05",
                "duration_hours": 65,
                "score": "93/100",
                "credential_id": "CERT-GPM-3391028D",
                "verification_code": "GPM-VER-552914",
                "topics": [
                    "Initiating, planning, executing, and closing complex technology and business projects.",
                    "Agile and Scrum methodologies: sprint planning, backlog refinement, and daily standups.",
                    "Risk management, budgeting, stakeholder communication, and project documentation.",
                    "Project tracking and collaboration using Jira, Asana, and Confluence."
                ],
                "skills": ["Project Management", "Agile", "Scrum", "Jira", "Risk Management", "Stakeholder Management"]
            },
            {
                "id": 5,
                "slug": "bnsp_systems_analyst_professional",
                "title": "Sertifikasi Profesi Analis Sistem Informasi (Systems Analyst)",
                "issuer": "BNSP",
                "tier": "TIER_A",
                "tier_weight": 1.0,
                "issue_date": "2025-01-10",
                "expiry_date": "2028-01-10",
                "duration_hours": 60,
                "score": "90/100",
                "credential_id": "CERT-BNSP-SYSA-7719208E",
                "verification_code": "BNSP-VER-220194",
                "topics": [
                    "Business process analysis, modeling, and optimization using BPMN 2.0 standards.",
                    "Formulating Software Requirements Specifications (SRS) and System Architecture Documents (SAD).",
                    "Object-Oriented Analysis and Design (OOAD) using UML (Use Case, Activity, Sequence, Class Diagrams).",
                    "Feasibility study analysis, system integration planning, and user acceptance testing (UAT)."
                ],
                "skills": ["Systems Analysis", "BPMN", "UML", "Requirements Engineering", "Enterprise Systems", "SDLC"]
            }
        ]
    }
]

def format_date_id(date_str):
    months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
              "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    y, m, d = date_str.split("-")
    return f"{int(d)} {months[int(m)-1]} {y}"

def generate_markdown_cert(student, cert):
    topics_md = "\n".join([f"- {t}" for t in cert["topics"]])
    skills_str = ", ".join(cert["skills"])
    
    md = f"""# Sertifikat Penyelesaian

---

## {cert['title']}

Diberikan kepada:

### **{student['student_name']}**

Program studi Sistem Informasi, spesialisasi {student['role']}, telah berhasil
menyelesaikan seluruh materi dan penilaian pada program **"{cert['title']}"**
yang diselenggarakan oleh **{cert['issuer']}**, dengan total durasi pelatihan
**{cert['duration_hours']} jam**.

---

## Detail Sertifikat

| Keterangan | Nilai |
|---|---|
| Nama Penerima | {student['student_name']} |
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
    all_summary_rows = []
    
    for st in STUDENTS_CERTS:
        st_name = st["student_name"]
        st_folder = st["folder_name"]
        
        st_cert_gen_dir = os.path.join(CERT_GEN_DIR, st_folder)
        st_multi_cert_dir = os.path.join(MULTI_CERT_DIR, st_folder)
        os.makedirs(st_cert_gen_dir, exist_ok=True)
        os.makedirs(st_multi_cert_dir, exist_ok=True)
        
        for c in st["certificates"]:
            md_content = generate_markdown_cert(st, c)
            file_name = f"{st_folder}_Certificate_{c['id']}_{c['slug']}.md"
            
            p1 = os.path.join(st_cert_gen_dir, file_name)
            p2 = os.path.join(st_multi_cert_dir, file_name)
            
            with open(p1, "w", encoding="utf-8") as f:
                f.write(md_content)
            with open(p2, "w", encoding="utf-8") as f:
                f.write(md_content)
                
            summary_row = {
                "nim": st["nim"],
                "student_name": st_name,
                "major": st["major"],
                "role": st["role"],
                "cert_id": c["id"],
                "cert_title": c["title"],
                "issuer": c["issuer"],
                "tier": c["tier"],
                "tier_weight": c["tier_weight"],
                "issue_date": c["issue_date"],
                "expiry_date": c["expiry_date"],
                "duration_hours": c["duration_hours"],
                "score": c["score"],
                "credential_id": c["credential_id"],
                "skills": ", ".join(c["skills"])
            }
            all_summary_rows.append(summary_row)

    csv_summary_path = os.path.join(MULTI_CERT_DIR, "certificates_summary.csv")
    df_summary = pd.DataFrame(all_summary_rows)
    df_summary.to_csv(csv_summary_path, index=False)
    print("Certificates successfully generated and aligned with parse_certificate_markdown!")

if __name__ == "__main__":
    main()
