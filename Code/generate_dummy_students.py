# -*- coding: utf-8 -*-
"""
Generator CV.md, KHS.md, dan Certificate.md untuk data mahasiswa dummy (Sistem Informasi).

Output:
1. CV.md          -> ringkasan profesional + pengalaman (per mahasiswa) [SAAT INI DI-NONAKTIFKAN]
2. KHS.md         -> Kartu Hasil Studi: seluruh mata kuliah pada katalog CLO,
                     dengan rincian nilai per CLO (bukan cuma nilai akhir MK)
3. Certificate.md (baru) -> Sertifikat pelatihan/kursus dummy, 1 mahasiswa bisa
                     punya lebih dari 1 sertifikat (mengikuti daftar TRACK_CERTS
                     sesuai spesialisasi/track masing-masing mahasiswa).

Catatan:
- Daftar mata kuliah di STUDENTS (di bawah) dipakai HANYA untuk bagian CV
  (kolom "Relevant Coursework"), karena penamaannya beda gaya dengan katalog
  CLO resmi (Tel-U Jakarta).
- KHS di-generate dari COURSE_CLO_CATALOG (seluruh 22 MK + CLO-nya, hasil
  ekstraksi dari Dataset_CLO_OBE_SI_TelUJakarta.xlsx), sesuai permintaan:
  "coba semua mata kuliah dulu" untuk versi pertama ini.
- Generate CV untuk sementara di-comment di main(); yang aktif sekarang
  adalah generate KHS dan generate Certificate.
"""

import os
import random
import string
import datetime

OUT_DIR_CV = "./../Dataset/generated_markdown_cvs"
OUT_DIR_KHS = "./../Dataset/generated_markdown_khs"
OUT_DIR_CERT = "./../Dataset/generated_markdown_certificates"
os.makedirs(OUT_DIR_CV, exist_ok=True)
os.makedirs(OUT_DIR_KHS, exist_ok=True)
os.makedirs(OUT_DIR_CERT, exist_ok=True)

# =====================================================================
# STUDENTS DATA (dipakai untuk generate CV)
# =====================================================================

STUDENTS = [

{
    "name": "Budi_Santoso", "track": "Software Engineering",
    "courses": [
        ("Pemrograman Dasar", 4, "A"),
        ("Algoritma dan Struktur Data", 4, "A"),
        ("Pemrograman Web", 3, "AB"),
        ("Perancangan & Pengembangan Perangkat Lunak", 3, "A"),
        ("Rekayasa Kebutuhan Perangkat Lunak", 3, "AB"),
        ("Sistem Basis Data", 3, "A"),
        ("Pengembangan Sistem dan Operasi", 3, "B"),
        ("Manajemen Proyek Tangkas", 2, "AB"),
    ],
    "cv_units": [
        ("E-commerce Order Management System", "Built a full-stack order management web app using Node.js, Express, and PostgreSQL. Implemented RESTful APIs, JWT authentication, and a React frontend with real-time order tracking."),
        ("Internship - Backend Developer at Fintech Startup", "Developed and maintained microservices for a payment processing platform using Java Spring Boot. Wrote unit tests, participated in code reviews, and improved API response time by 30% through query optimization."),
        ("Open Source Contribution - Task Scheduler Library", "Contributed bug fixes and new features to an open source Python task scheduling library on GitHub, including improved cron expression parsing and test coverage."),
        ("Capstone Project - Campus Event Management Platform", "Led a team of 4 to design and build a web platform for managing campus events, including registration, ticketing, and admin dashboard, using Laravel and MySQL."),
    ],
},

{
    "name": "Siti_Rahma", "track": "Data Science / Machine Learning",
    "courses": [
        ("Probabilistik dan Statistika untuk TI", 3, "A"),
        ("Teknologi Machine Learning", 3, "A"),
        ("Pemodelan dan Analitika Prediktif", 3, "A"),
        ("Analitika Data dan Diagnostik", 3, "AB"),
        ("Pengolahan Bahasa Alami", 3, "A"),
        ("Matematika untuk Sistem Informasi", 3, "AB"),
        ("Riset Operasi", 2, "B"),
        ("Sistem Keputusan Berbasis Model", 3, "AB"),
    ],
    "cv_units": [
        ("Customer Churn Prediction Model", "Built a machine learning pipeline in Python (scikit-learn, XGBoost) to predict telecom customer churn, achieving 0.87 AUC-ROC. Handled class imbalance with SMOTE and deployed the model via Flask API."),
        ("Internship - Data Science Intern at E-commerce Company", "Analyzed customer purchase patterns using clustering (K-means) to segment users for targeted marketing campaigns. Built dashboards in Tableau to communicate findings to stakeholders."),
        ("Sentiment Analysis on Indonesian Social Media", "Fine-tuned an IndoBERT model to classify sentiment in Indonesian tweets about public policy, achieving 89% accuracy. Published findings as a university research project."),
        ("Kaggle Competition - Housing Price Prediction", "Ranked top 15% in a Kaggle regression competition using feature engineering and ensemble methods (Random Forest, LightGBM, stacking)."),
    ],
},

{
    "name": "Andi_Wijaya", "track": "Cybersecurity",
    "courses": [
        ("Proteksi Aset Informasi", 3, "A"),
        ("Tata Kelola Keamanan Informasi", 3, "A"),
        ("Forensika Digital", 3, "AB"),
        ("Manajemen Risiko TI", 3, "A"),
        ("Desain dan Manajemen Jaringan Komputer", 3, "AB"),
        ("Infrastruktur TI", 3, "B"),
        ("Tata Kelola dan Audit TI", 2, "AB"),
        ("Jaringan Komputer", 3, "A"),
    ],
    "cv_units": [
        ("Vulnerability Assessment - Campus Web Portal", "Conducted a penetration test on the university's student portal, identifying SQL injection and XSS vulnerabilities using Burp Suite and OWASP ZAP. Delivered a remediation report to IT staff."),
        ("Internship - SOC Analyst at Managed Security Provider", "Monitored security alerts using a SIEM platform, investigated potential incidents, and documented response procedures. Assisted in tuning detection rules to reduce false positives by 20%."),
        ("Digital Forensics Capstone - Ransomware Case Study", "Simulated a ransomware attack in an isolated lab environment and performed forensic analysis of the infected system, including memory dump analysis and timeline reconstruction using Autopsy."),
        ("CTF Team Member - National Cybersecurity Competition", "Competed in a national Capture The Flag competition, solving challenges in web exploitation, cryptography, and reverse engineering; team placed in top 10."),
    ],
},

{
    "name": "Dewi_Lestari", "track": "UX / Product Design",
    "courses": [
        ("Desain Pengalaman Pengguna", 3, "A"),
        ("Design Thinking", 3, "A"),
        ("Rekayasa Kebutuhan Perangkat Lunak", 3, "AB"),
        ("Manajemen Hubungan Pelanggan", 3, "AB"),
        ("Pemrograman Web", 3, "B"),
        ("Manajemen Proyek Tangkas", 2, "A"),
        ("Organisasi dan Fungsional Bisnis", 2, "AB"),
        ("Pengantar Ekonomi dan Bisnis", 2, "B"),
    ],
    "cv_units": [
        ("Mobile Banking App Redesign", "Led a UX research and redesign project for a mobile banking app, conducting 15 user interviews and usability tests. Redesigned the onboarding flow in Figma, reducing task completion time by 40% in follow-up testing."),
        ("Internship - Product Design Intern at Ride-hailing Startup", "Designed wireframes and high-fidelity prototypes for a new driver incentive feature. Collaborated closely with product managers and engineers through daily standups and design critiques."),
        ("Accessibility Audit - University E-learning Platform", "Performed a WCAG 2.1 accessibility audit on the campus e-learning platform, identifying issues for visually impaired users and proposing design fixes adopted by the IT department."),
        ("Design System for Student Organization App", "Built a reusable design system and component library in Figma for a student organization's mobile app, used across three separate feature teams."),
    ],
},

{
    "name": "Rizky_Pratama", "track": "Networking / Infrastructure",
    "courses": [
        ("Jaringan Komputer", 3, "A"),
        ("Desain dan Manajemen Jaringan Komputer", 3, "A"),
        ("Infrastruktur TI", 3, "AB"),
        ("Administrasi Basisdata", 3, "B"),
        ("Manajemen Layanan TI", 3, "AB"),
        ("Pengembangan Sistem dan Operasi", 3, "A"),
        ("Monitoring dan Evaluasi Organisasi TI", 2, "B"),
        ("Tata Kelola dan Audit TI", 2, "AB"),
    ],
    "cv_units": [
        ("Campus Network Redesign Project", "Redesigned the network topology for a campus building, implementing VLAN segmentation, redundant routing with OSPF, and improved wireless coverage - documented in a full network diagram and configuration guide."),
        ("Internship - Network Engineer Intern at ISP", "Assisted in configuring and troubleshooting Cisco routers and switches for enterprise clients. Monitored network uptime using Zabbix and helped resolve latency issues affecting customer SLAs."),
        ("Home Lab - Kubernetes Cluster on Bare Metal", "Built a 3-node Kubernetes cluster at home using Raspberry Pis to learn container orchestration, load balancing, and persistent storage with Longhorn."),
        ("IT Infrastructure Migration to Cloud", "Participated in a university IT project migrating on-premise file servers to AWS, configuring EC2 instances, S3 storage, and IAM policies for access control."),
    ],
},

{
    "name": "Nadia_Putri", "track": "Business Analyst / Enterprise Systems",
    "courses": [
        ("Manajemen Proses Bisnis", 3, "A"),
        ("Sistem Enterprise", 3, "A"),
        ("Arsitektur Enterprise", 3, "AB"),
        ("Perencanaan Strategis SI/TI", 3, "A"),
        ("Manajemen Perubahan Organisasi", 3, "AB"),
        ("Manajemen Rantai Pasok", 3, "B"),
        ("Organisasi dan Fungsional Bisnis", 2, "AB"),
        ("Manajemen Sumber Daya Manusia", 2, "B"),
    ],
    "cv_units": [
        ("SAP Implementation Support - Retail Company", "Assisted in a SAP ERP implementation project for a mid-size retail company, mapping existing procurement processes to SAP MM module workflows and documenting gap analysis."),
        ("Internship - Business Analyst Intern at Manufacturing Firm", "Analyzed the inventory management process and proposed workflow improvements that reduced stock discrepancies by 18%. Presented findings to department heads using process flow diagrams."),
        ("Business Process Reengineering Capstone", "Led a capstone project reengineering the student admission process for the university registrar's office, reducing average processing time from 5 days to 2 days through BPMN-based redesign."),
        ("Supply Chain Analytics Dashboard", "Built a Power BI dashboard for supply chain KPIs (lead time, fill rate, inventory turnover) used by a student-run logistics simulation team."),
    ],
},

{
    "name": "Fajar_Nugroho", "track": "Data Engineering",
    "courses": [
        ("Sistem Basis Data", 3, "A"),
        ("Data Lakehouse", 3, "A"),
        ("Sistem Data-Intensif", 3, "AB"),
        ("Administrasi Basisdata", 3, "A"),
        ("Grafik Pengetahuan", 3, "B"),
        ("Algoritma dan Struktur Data", 4, "AB"),
        ("Infrastruktur TI", 3, "B"),
        ("Riset Operasi", 2, "AB"),
    ],
    "cv_units": [
        ("ETL Pipeline for Marketplace Analytics", "Built an automated ETL pipeline using Apache Airflow and dbt to ingest and transform marketplace transaction data into a Snowflake data warehouse, processing 2M+ rows daily."),
        ("Internship - Data Engineering Intern at Logistics Company", "Designed and optimized SQL queries and Spark jobs for a delivery tracking data pipeline, reducing daily batch processing time from 4 hours to 45 minutes."),
        ("Real-time Streaming Analytics with Kafka", "Built a real-time data streaming project using Apache Kafka and Spark Streaming to process simulated IoT sensor data, with results visualized on a Grafana dashboard."),
        ("Knowledge Graph for Academic Publications", "Constructed a knowledge graph of university research publications using Neo4j, enabling graph-based queries to identify research collaboration patterns across departments."),
    ],
},

{
    "name": "Maya_Anggraini", "track": "IT Governance / Project Management",
    "courses": [
        ("Manajemen Proyek Tangkas", 3, "A"),
        ("Tata Kelola dan Audit TI", 3, "A"),
        ("Manajemen Risiko TI", 3, "AB"),
        ("Manajemen Layanan TI", 3, "A"),
        ("Manajemen Investasi TI", 3, "AB"),
        ("Perencanaan Strategis SI/TI", 3, "B"),
        ("Etika Profesi", 2, "A"),
        ("Etika Teknologi Informasi", 2, "AB"),
    ],
    "cv_units": [
        ("IT Project Management - Campus System Upgrade", "Served as project coordinator for a campus-wide learning management system upgrade, managing the project timeline, stakeholder communication, and risk register using Jira and Agile Scrum ceremonies."),
        ("Internship - PMO Intern at Banking IT Division", "Supported the Project Management Office in tracking project budgets and milestones for 5 concurrent IT projects, and helped prepare steering committee reports."),
        ("IT Governance Framework Assessment", "Conducted a COBIT-based maturity assessment of a simulated organization's IT governance practices as a capstone project, identifying gaps in change management and vendor risk management."),
        ("Agile Transformation Case Study", "Researched and presented a case study on Agile transformation challenges in traditional enterprises, including a proposed roadmap for adopting Scrum in a hypothetical mid-size company."),
    ],
},

{
    "name": "Hendra_Kurniawan", "track": "Full-stack / DevOps",
    "courses": [
        ("Pemrograman Web", 3, "A"),
        ("Perancangan & Pengembangan Perangkat Lunak", 3, "A"),
        ("Pengembangan Sistem dan Operasi", 3, "A"),
        ("Sistem Basis Data", 3, "AB"),
        ("Infrastruktur TI", 3, "AB"),
        ("Algoritma dan Struktur Data", 4, "B"),
        ("Manajemen Proyek Tangkas", 2, "AB"),
        ("Teknologi Berkembang", 2, "B"),
    ],
    "cv_units": [
        ("CI/CD Pipeline for Microservices Platform", "Set up a full CI/CD pipeline using GitHub Actions and Docker for a microservices-based application, automating testing, image builds, and deployment to a Kubernetes cluster on GCP."),
        ("Internship - Full-stack Developer at SaaS Startup", "Built features across the stack using React, Node.js, and PostgreSQL for a project management SaaS product, and helped containerize the application for consistent deployment."),
        ("Infrastructure as Code with Terraform", "Migrated manually-provisioned cloud infrastructure to Terraform-managed IaC for a student project, covering VPC, EC2, RDS, and load balancer configuration."),
        ("Personal Project - Self-hosted Blogging Platform", "Built and deployed a self-hosted blogging platform using Next.js and a headless CMS, with automated deployment via Docker Compose on a VPS."),
    ],
},

{
    "name": "Putri_Ayu", "track": "AI / NLP",
    "courses": [
        ("Pengolahan Bahasa Alami", 3, "A"),
        ("Teknologi Machine Learning", 3, "A"),
        ("Pemodelan Sistem Kognitif", 3, "A"),
        ("Pengantar Teknologi Elektro dan Informatika Cerdas", 2, "AB"),
        ("Pemodelan dan Analitika Preskriptif", 3, "AB"),
        ("Probabilistik dan Statistika untuk TI", 3, "B"),
        ("Grafik Pengetahuan", 3, "AB"),
        ("Teknologi Berkembang", 2, "A"),
    ],
    "cv_units": [
        ("Chatbot for Student Academic Advising", "Built a retrieval-augmented chatbot using LangChain and OpenAI embeddings to answer student questions about course prerequisites and academic policies, deployed as a Telegram bot."),
        ("Internship - NLP Research Intern at AI Lab", "Fine-tuned transformer models for Indonesian named entity recognition, contributing to an internal annotated dataset and achieving a 4-point F1 improvement over the baseline."),
        ("Thesis Research - Text Summarization for News Articles", "Researched abstractive summarization of Indonesian news articles using a fine-tuned mT5 model, evaluated with ROUGE scores against extractive baselines."),
        ("Speech Recognition Mini-Project", "Built a small speech-to-text prototype for Bahasa Indonesia using wav2vec2, fine-tuned on a public Indonesian speech dataset for a course project."),
    ],
},

]


# =====================================================================
# KATALOG CLO RESMI (dari Dataset_CLO_OBE_SI_TelUJakarta.xlsx)
# Dipakai untuk generate KHS: setiap mata kuliah + daftar CLO-nya.
# =====================================================================

COURSE_CLO_CATALOG = [{'kode_mk': 'BBK1AAB4', 'nama_mk': 'Algoritma dan Pemrograman', 'sks': 4, 'semester': 'Ganjil 2425', 'clos': [{'clo_code': 'CLO-08', 'clo_desc': 'Mampu memahami konsep dasar bidang infokom yang digunakan dalam lingkup disiplin ilmu sistem informasi', 'bloom': '2 - Understand'}, {'clo_code': 'CLO-04', 'clo_desc': 'Mampu menganalisis permasalahan dalam bidang infokom dalam konteks enterprise atau masyarakat', 'bloom': '4 - Analyse'}, {'clo_code': 'CLO-02', 'clo_desc': 'Mampu mengembangkan solusi berbasis sistem informasi menggunakan metodologi pengembangan yang tepat.', 'bloom': '3 - Apply'}]}, {'kode_mk': 'BBK2AAB3', 'nama_mk': 'Analisis dan Perancangan Sistem Informasi', 'sks': 3, 'semester': 'Genap 2425', 'clos': [{'clo_code': 'CLO-03', 'clo_desc': '[PLO01-CLO03] Mampu mengidentifikasi kebutuhan sistem informasi dalam konteks enterprise atau masyarakat', 'bloom': '4 - Analyze'}, {'clo_code': 'CLO-01', 'clo_desc': '[PLO02-CLO01] Mampu membuat perancangan sistem informasi untuk memenuhi kebutuhan organisasi menuju data-driven organization', 'bloom': '3 - Apply'}, {'clo_code': 'CLO-02', 'clo_desc': '[PLO03-CLO02] Mampu menerapkan sikap adaptif dalam berbagai konteks profesional untuk mencapai tujuan bersama', 'bloom': '3 - Apply'}, {'clo_code': 'CLO-04', 'clo_desc': '[PLO08-CLO04] Mampu menggunakan teknik, keahlian, dan perangkat dalam pengembangan aplikasi dan integrasinya dalam konteks kasus nyata', 'bloom': '3 - Apply'}]}, {'kode_mk': 'BBK3AAB3', 'nama_mk': 'Arsitektur Enterprise', 'sks': 3, 'semester': 'Ganjil 2425', 'clos': [{'clo_code': 'CLO-05', 'clo_desc': 'Mampu memodelkan kebutuhan infokom dalam konteks enterprise atau masyarakat', 'bloom': '4 - Analyse'}, {'clo_code': 'CLO-05', 'clo_desc': 'Mampu menggunakan teknik, metode, perangkat lunak terkini untuk menghasilkan solusi di bidang pengelolaan fungsi dan bisnis organisasi dalam konteks kasus nyata', 'bloom': '3 - Apply'}, {'clo_code': 'CLO-06', 'clo_desc': 'Mampu mengusulkan perbaikan arsitektur atau pengelolaan sistem informasi untuk mendukung tujuan organisasi.', 'bloom': '3 - Apply'}]}, {'kode_mk': 'BBK3BAB3', 'nama_mk': 'Data Warehouse dan Business Intelligence', 'sks': 3, 'semester': 'Genap 2425', 'clos': [{'clo_code': 'CLO-05', 'clo_desc': 'Mampu memodelkan kebutuhan infokom dalam konteks enterprise atau masyarakat', 'bloom': 'Apply'}, {'clo_code': 'CLO-08', 'clo_desc': 'Mampu memahami konsep dasar bidang infokom yang digunakan dalam lingkup disiplin ilmu sistem informasi', 'bloom': 'Understand'}, {'clo_code': 'CLO-01', 'clo_desc': 'Mampu membuat perancangan sistem informasi untuk memenuhi kebutuhan organisasi menuju data-driven organization', 'bloom': 'Apply'}, {'clo_code': 'CLO-02', 'clo_desc': 'Mampu mengembangkan solusi berbasis sistem informasi menggunakan metodologi pengembangan yang tepat.', 'bloom': 'Analyse'}, {'clo_code': 'CLO-01', 'clo_desc': 'Mampu menggunakan metode dan perangkat lunak terkini untuk menghasilkan solusi di bidang data dalam konteks kasus nyata', 'bloom': 'Analyse'}]}, {'kode_mk': 'BBK2HAB3', 'nama_mk': 'Integrasi Aplikasi Enterprise', 'sks': 3, 'semester': 'Genap 2425', 'clos': [{'clo_code': 'CLO-03', 'clo_desc': '[PLO01] CLO03 - Mampu mengidentifikasi kebutuhan sistem informasi dalam konteks enterprise atau masyarakat', 'bloom': None}, {'clo_code': 'CLO-03', 'clo_desc': '[PLO08] CLO03 - Mampu menggunakan metode atau perangkat lunak tertentu dalam keilmuan sistem informasi dalam konteks penelitian atau proyek nyata', 'bloom': None}]}, {'kode_mk': 'BBK1GAB3', 'nama_mk': 'Jaringan Komputer', 'sks': 3, 'semester': 'Ganjil 2425', 'clos': [{'clo_code': 'CLO-08', 'clo_desc': 'Mampu memahami konsep dasar bidang infokom yang digunakan dalam lingkup disiplin ilmu sistem informasi', 'bloom': '2.0'}, {'clo_code': 'CLO-09', 'clo_desc': 'Mampu menerapkan perspektif disiplin lain dalam analisis permasalahan infokom', 'bloom': '3.0'}, {'clo_code': 'CLO-02', 'clo_desc': 'Mampu menggunakan teknik atau perangkat dalam bidang infrastruktur teknologi informasi untuk organisasi', 'bloom': '3.0'}]}, {'kode_mk': 'BBK2IAB3', 'nama_mk': 'Keamanan Sistem Informasi', 'sks': 3, 'semester': 'Genap 2425', 'clos': [{'clo_code': 'CLO-03', 'clo_desc': 'Mampu mengidentifikasi kebutuhan sistem informasi dalam konteks enterprise atau masyarakat', 'bloom': 'Analyze,Evaluate'}, {'clo_code': 'CLO-08', 'clo_desc': 'Mampu memahami konsep dasar bidang infokom yang digunakan dalam lingkup disiplin ilmu sistem informasi', 'bloom': 'Analyze,Evaluate'}, {'clo_code': 'CLO-01', 'clo_desc': 'Mampu menggunakan metode dan perangkat lunak terkini untuk menghasilkan solusi di bidang data dalam konteks kasus nyata', 'bloom': None}, {'clo_code': 'CLO-02', 'clo_desc': 'Mampu menggunakan teknik atau perangkat dalam bidang infrastruktur teknologi informasi untuk organisasi', 'bloom': None}]}, {'kode_mk': 'BBK2JAB3', 'nama_mk': 'Manajemen Proyek Sistem Informasi', 'sks': 3, 'semester': 'Ganjil 2425', 'clos': [{'clo_code': 'CLO-01', 'clo_desc': 'Mampu berinisiatif dan bertanggungjawab untuk menyelesaikan berbagai tugas dalam tim', 'bloom': '3 - Apply'}, {'clo_code': 'CLO-02', 'clo_desc': 'Mampu menulis dokumen profesional sesuai dengan konteks profesional', 'bloom': '3 - Apply'}, {'clo_code': 'CLO-03', 'clo_desc': 'Mampu menggunakan metode atau perangkat lunak tertentu dalam keilmuan sistem informasi dalam konteks penelitian atau proyek nyata', 'bloom': '3 - Apply'}, {'clo_code': 'CLO-01', 'clo_desc': 'Mampu memahami prinsip-prinsip manajemen sistem informasi dalam konteks organisasi', 'bloom': '2 - Understand'}, {'clo_code': 'CLO-03', 'clo_desc': 'Mampu menyusun perencanaan dalam konteks sistem informasi menggunakan ilmu dan praktek yang relevan', 'bloom': '3 - Apply'}]}, {'kode_mk': None, 'nama_mk': 'Pemodelan Proses Bisnis', 'sks': 3, 'semester': 'Ganjil 2425', 'clos': [{'clo_code': 'CLO-01', 'clo_desc': 'Mampu menyampaikan ide, informasi, dan argumen secara jelas dan persuasif dalam bentuk lisan di lingkungan profesional.', 'bloom': 'Apply'}, {'clo_code': 'CLO-05', 'clo_desc': 'Mampu menggunakan teknik, metode, perangkat lunak terkini untuk menghasilkan solusi di bidang pengelolaan fungsi dan bisnis organisasi dalam konteks kasus nyata.', 'bloom': 'Apply'}, {'clo_code': 'CLO-02', 'clo_desc': 'Mampu menganalisis prinsip dan fungsi manajemen Sistem Informasi untuk mendukung strategi bisnis.', 'bloom': 'Analyze'}, {'clo_code': 'CLO-04', 'clo_desc': 'Mampu memodelkan penyelenggaraan sistem informasi di konteks organisasi.', 'bloom': 'Apply'}]}, {'kode_mk': 'BBK1JAB3', 'nama_mk': 'Pemrograman Berorientasi Objek', 'sks': 3, 'semester': 'Ganjil 2425', 'clos': [{'clo_code': 'CLO-08', 'clo_desc': 'Mampu memahami konsep dasar bidang infokom yang digunakan dalam lingkup disiplin ilmu sistem informasi', 'bloom': '2 - Understand'}, {'clo_code': 'CLO-03', 'clo_desc': 'Mampu mengimplementasikan solusi berbasis sistem informasi menggunakan metodologi pengembangan yang tepat', 'bloom': '3 - Apply'}, {'clo_code': 'CLO-01', 'clo_desc': 'Mampu menjelaskan konsep-konsep dasar pemrograman berorientasi obyek (sintak dasar, enkapsulasi, inheritance, polimorfisme, abstraksi, dan penanganan eksepsi) dalam pemrograman Java.', 'bloom': '2 - Understand'}, {'clo_code': 'CLO-02', 'clo_desc': 'Mampu menerapkan prinsip-prinsip OOP untuk merancang dan mengimplementasikan kelas dan objek Java dengan menggunakan fitur yang sesuai.', 'bloom': '3 - Apply'}, {'clo_code': 'CLO-03', 'clo_desc': 'Mampu merancang, mengembangkan, dan mendokumentasikan aplikasi Java sederhana secara kolaboratif yang memenuhi kebutuhan pengguna dengan menerapkan prinsip-prinsip OOP secara komprehensif.', 'bloom': None}]}, {'kode_mk': 'BBK2LAB3', 'nama_mk': 'Penambangan Data', 'sks': 3, 'semester': 'Ganjil 2425', 'clos': [{'clo_code': 'CLO-05', 'clo_desc': 'Mampu memodelkan kebutuhan infokom dalam konteks enterprise atau masyarakat', 'bloom': 'Apply'}, {'clo_code': 'CLO-07', 'clo_desc': 'Mampu menerapkan pengetahuan statistika fundamental dalam lingkup ilmu sistem informasi', 'bloom': 'Apply'}, {'clo_code': 'CLO-02', 'clo_desc': 'Mampu mengembangkan solusi berbasis sistem informasi menggunakan metodologi pengembangan yang tepat.', 'bloom': 'Analyse'}, {'clo_code': 'CLO-01', 'clo_desc': 'Mampu menggunakan metode dan perangkat lunak terkini untuk menghasilkan solusi di bidang data dalam konteks kasus nyata', 'bloom': 'Analyse'}]}, {'kode_mk': 'BBK1DAB3', 'nama_mk': 'Pengantar Sistem Informasi', 'sks': 3, 'semester': 'Ganjil 2425', 'clos': [{'clo_code': 'CLO-12', 'clo_desc': 'Mahasiswa mampu menjelaskan peran profesi sistem informasi dalam upaya pembangunan berkelanjutan.', 'bloom': '2 - Understand'}, {'clo_code': 'CLO-01', 'clo_desc': 'Mampu menjelaskan peran dari sistem dan teknologi informasi dalam konteks individu, bisnis, maupun organisasi.', 'bloom': '2 - Understand'}, {'clo_code': 'CLO-02', 'clo_desc': 'Mampu menganalisis nilai dan risiko dari penggunaan sistem dan teknologi informasi.', 'bloom': '2 - Understand'}, {'clo_code': 'CLO-04', 'clo_desc': 'Mampu memodelkan penyelenggaraan sistem informasi di konteks organisasi.', 'bloom': '3 - Apply'}]}, {'kode_mk': 'BBK2DAB3', 'nama_mk': 'Pengembangan Aplikasi Website', 'sks': 3, 'semester': 'Ganjil 2425', 'clos': [{'clo_code': 'CLO-03', 'clo_desc': 'PLO02-CLO03 - Mampu mengimplementasikan solusi berbasis sistem informasi menggunakan metodologi pengembangan yang tepat.', 'bloom': '3 - Apply'}, {'clo_code': 'CLO-04', 'clo_desc': 'PLO08-CLO04 - Mampu menggunakan teknik, keahlian, dan perangkat dalam pengembangan aplikasi dan integrasinya dalam konteks kasus nyata', 'bloom': '3 - Apply'}]}, {'kode_mk': 'BBK4EBB3', 'nama_mk': 'Pengembangan Sistem Cerdas', 'sks': 3, 'semester': 'Ganjil 2425', 'clos': [{'clo_code': 'CLO-1', 'clo_desc': '[PLO01-CLO01] Mampu memahami konsep- konsep dasar sistem cerdas', 'bloom': None}, {'clo_code': 'CLO-4', 'clo_desc': '[PLO02-CLO04] Mampu merancang, membuat arsitektur, dan menerapkan teknik- teknik sistem cerdas pada studi kasus spesifik sbg project based learning', 'bloom': None}, {'clo_code': 'CLO-3', 'clo_desc': '[PLO08-CLO03] Mampu memahami beberapa teknik dasar sistem cerdas utk klasifikasi seperti Decision Tree dan NN', 'bloom': None}, {'clo_code': 'CLO-1', 'clo_desc': '[PLO-1] [PLO1] Mampu menganalisis permasalahan infokom yang komplek, mendefinLisikan, dan memodelkan kebutuhan dalam konteks enterprise Eatau masyarakat dengan menerapkan ilmu dan pengetahuan dalam bidang komputasi, teknologi informasi dan komunikasi, dan disiplin lain yang relevan', 'bloom': None}, {'clo_code': 'CLO-1', 'clo_desc': 'K [CLO-1][PLO01-CLO01] Mampu memahami konsep-konsep dasar sistem cerdas', 'bloom': None}, {'clo_code': 'CLO-4', 'clo_desc': '[PLO-2] [PLO2] Mampu merancang, mengembangkan, mengimplementasikan, dan mengevaluasi solusi berbasis sistem informasi untuk memenuhi kebutuhan organisasi menuju data- driven organization', 'bloom': None}, {'clo_code': 'CLO-4', 'clo_desc': '[CLO-4][PLO02-CLO04] Mampu merancang, membuat arsitektur, dan menerapkan teknik-teknik sistem cerdas pada studi kasus spesifik sbg project based learning', 'bloom': None}, {'clo_code': 'CLO-5', 'clo_desc': '[PLO-8] [PL08] Mampu menggunakan metode, teknik, keahlian, atau perangkat terkini yang diperlukan untuk menghasilkan solusi di bidang sistem informasi, baik dalam konteks praktikum ataupun kasus nyata', 'bloom': None}]}, {'kode_mk': 'BBK2EAB3', 'nama_mk': 'Perancangan Interaksi', 'sks': 3, 'semester': 'Ganjil 2425', 'clos': [{'clo_code': 'CLO-1', 'clo_desc': 'Mampu menjelaskan dasar perancangan interaksi', 'bloom': '2 - Understand'}, {'clo_code': 'CLO-2', 'clo_desc': 'Mampu mengindetifikasi permasalahan dan mendefinisikan kebutuhan sistem', 'bloom': '4 - Analyze'}, {'clo_code': 'CLO-3', 'clo_desc': 'Mampu menerapkan prinsip dan style interaksi dalam setiap proses perancangan interaksi', 'bloom': '3 - Apply'}, {'clo_code': 'CLO-4', 'clo_desc': 'Mampu menguji produk dengan metode pengujian usability', 'bloom': '5 - Evaluate'}, {'clo_code': 'CLO-5', 'clo_desc': 'Mampu mengkomunikasikan hasil perancangan interaksi dalam sebuah forum', 'bloom': '3 - Apply'}]}, {'kode_mk': 'BBK3EAB3', 'nama_mk': 'Proyek Perangkat Lunak', 'sks': 3, 'semester': 'Genap 2425', 'clos': [{'clo_code': 'CLO-1', 'clo_desc': '[PLO01-CLO04] Mampu menganalisis permasalahan dalam bidang infokom dalam konteks enterprise atau masyarakat', 'bloom': None}, {'clo_code': 'CLO-2', 'clo_desc': '[PLO02-CLO04] Mampu mengevaluasi solusi berbasis sistem informasi dengan menggunakan metode yang tepat', 'bloom': None}, {'clo_code': 'CLO-3', 'clo_desc': '[PLO03-CLO01] Mampu berinisiatif dan bertanggungjawab untuk menyelesaikan berbagai tugas dalam tim', 'bloom': None}, {'clo_code': 'CLO-5', 'clo_desc': '[PLO08-CLO03] Mampu menggunakan metode atau perangkat lunak tertentu dalam keilmuan sistem informasi dalam konteks penelitian atau proyek nyata', 'bloom': None}, {'clo_code': 'CLO-1', 'clo_desc': '[PLO-1] [PLO1] Mampu menganalisis permasalahan infokom yang komplek, mendefinisikan, dan memodelkan kebutuhan dalam konteks enterprise atau masyarakat dengan menerapkan ilmu dan pengetahuan dalam bidang komputasi, teknologi informasi dan komunikasi, dan disiplin lain yang relevan', 'bloom': None}, {'clo_code': 'CLO-1', 'clo_desc': '[CLO-1][PLO01-CLO04] Mampu menganalisis permasalahan dalam bidang infokom dalam konteks enterprise atau masyarakat', 'bloom': None}, {'clo_code': 'CLO-4', 'clo_desc': '[PLO-5] [PLO5] Mampu berkomunikasi secara efektif baik lisan maupun tulisan dalam berbagai konteks profesional', 'bloom': None}, {'clo_code': 'CLO-3', 'clo_desc': '[PLO-3] [PLO3] Mampu untuk bekerja secara kolaboratif, proaktif, dan bertanggungjawab dalam tim untuk mencapai tujuan bersama dalam berbagai kontek profesional', 'bloom': None}]}, {'kode_mk': 'BBK2NAB3', 'nama_mk': 'Rekayasa Proses Bisnis', 'sks': 3, 'semester': 'Genap 2425', 'clos': [{'clo_code': 'CLO-1', 'clo_desc': '[PLO01-CLO04] Mampu menganalisis permasalahan dalam bidang infokom dalam konteks enterprise atau masyarakat.', 'bloom': None}, {'clo_code': 'CLO-3', 'clo_desc': '[PLO08-CLO05] Mampu menggunakan teknik, metode, perangkat lunak terkini untuk menghasilkan solusi di bidang pengelolaan fungsi dan bisnis organisasi dalam konteks kasus nyata.', 'bloom': None}, {'clo_code': 'CLO-4', 'clo_desc': '[PLO09-CLO06] Mampu mengusulkan perbaikan arsitektur atau pengelolaan sistem informasi untuk mendukung tujuan organisasi.', 'bloom': None}, {'clo_code': 'CLO-1', 'clo_desc': '[PLO-1] [PLO1] Mampu menganalisis permasalahan infokom yang komplek, mendefinisikan, dan memodelkan kebutuhan dalam konteks enterprise atau masyarakat dengan menerapkan ilmu dan pengetahuan dalam bidang komputasi, teknologi informasi dan komunikasi, dan disiplin lain yang relevan', 'bloom': None}, {'clo_code': 'CLO-1', 'clo_desc': '[CLO-1][PLO01-CLO04] Mampu menganalisis permasalahan dalam bidang infokom dalam konteks enterprise atau masyarakat.', 'bloom': None}, {'clo_code': 'CLO-2', 'clo_desc': '[PLO-5] [PLO5] Mampu berkomunikasi secara efektif baik lisan maupun tulisan dalam berbagai konteks profesional', 'bloom': None}, {'clo_code': 'CLO-4', 'clo_desc': '[PLO-9] [LPLO9] Mampu mendukung penyelenggaraan, Epenggunaan, pengelolaan, evaluasi, dan peningkatan Sistem Informasi untuk mencapai tujuan dan sasaran strategi bisnis dari organisasi.', 'bloom': None}, {'clo_code': 'CLO-4', 'clo_desc': '[CLO-4][PLO09-CLO06] Mampu mengusulkan perbaikan arsitektur atau pengelolaan sistem informasi untuk mendukung tujuan organisasi.', 'bloom': None}]}, {'kode_mk': 'BBK1LAB3', 'nama_mk': 'Sistem Basis Data', 'sks': 3, 'semester': 'Genap 2425', 'clos': [{'clo_code': 'CLO-03', 'clo_desc': 'PLO01-CLO03 - Mampu mengidentifikasi kebutuhan sistem informasi dalam konteks enterprise atau masyarakat', 'bloom': '3-Apply'}, {'clo_code': 'CLO-01', 'clo_desc': 'PLO02-CLO01 - Mampu membuat perancangan sistem informasi untuk memenuhi kebutuhan organisasi menuju data-driven organization', 'bloom': '3-Apply'}, {'clo_code': 'CLO-08', 'clo_desc': 'PLO01-CLO08 - Mampu memahami konsep dasar bidang infokom yang digunakan dalam lingkup disiplin ilmu sistem informasi', 'bloom': '2-Understand'}, {'clo_code': 'CLO-01', 'clo_desc': 'PLO08-CLO01 - Mampu menggunakan metode dan perangkat lunak terkini untuk menghasilkan solusi di bidang data dalam konteks kasus nyata', 'bloom': '3-Apply'}]}, {'kode_mk': 'BBK1EAB3', 'nama_mk': 'Sistem Enterprise', 'sks': 3, 'semester': 'Ganjil 2425', 'clos': [{'clo_code': 'CLO-1', 'clo_desc': '[PLO-9] CLO-1 Mampu memahami prinsip dan fungsi manajemen Sistem Informasi untuk mendukung strategi bisnis', 'bloom': '2 - Understand'}, {'clo_code': 'CLO-2', 'clo_desc': '[PLO-8] CLO-2 Mampu menggunakan teknik, metode, perangkat lunak, atau kakas terkini untuk menghasilkan solusi di bidang sistem informasi dalam konteks kasus nyata', 'bloom': '3 - Apply'}]}, {'kode_mk': 'BBK3FAB3', 'nama_mk': 'Sistem Informasi Akuntansi', 'sks': 3, 'semester': 'Genap 2425', 'clos': [{'clo_code': 'CLO-02', 'clo_desc': 'Mampu menganalisis prinsip dan fungsi manajemen Sistem Informasi untuk mendukung strategi bisnis', 'bloom': None}, {'clo_code': 'CLO-05', 'clo_desc': 'Mampu memodelkan kebutuhan infokom dalam konteks enterprise atau masyarakat', 'bloom': None}, {'clo_code': 'CLO-06', 'clo_desc': 'Mampu menggunakan kakas dalam pengelolaan sistem informasi perusahaan berbasis ERP', 'bloom': None}, {'clo_code': 'CLO-08', 'clo_desc': 'Mampu memahami konsep dasar bidang infokom yang digunakan dalam lingkup disiplin ilmu sistem informasi', 'bloom': None}]}, {'kode_mk': 'BBK2FAB3', 'nama_mk': 'Sistem Operasi', 'sks': 3, 'semester': 'Ganjil 2425', 'clos': [{'clo_code': 'CLO-01', 'clo_desc': 'Mampu merancang, mengembangkan, mengimplementasikan, dan mengevaluasi solusi berbasis sistem informasi untuk memenuhi kebutuhan organisasi menuju data-driven organization', 'bloom': '4 - Analyze'}, {'clo_code': 'CLO-02', 'clo_desc': 'Mampu mengimplementasikan solusi berbasis sistem informasi menggunakan metodologi pengembangan yang tepat', 'bloom': None}, {'clo_code': 'CLO-03', 'clo_desc': 'Mampu menggunakan metode tertentu dalam keilmuan sistem informasi dalam konteks penelitian atau proyek nyata', 'bloom': None}, {'clo_code': 'CLO-04', 'clo_desc': 'Mampu menggunakan teknik, keahlian, dan perangkat dalam pengembangan aplikasi dan integrasinya dalam konteks kasus nyata', 'bloom': '6 - Create'}]}, {'kode_mk': 'BBK3IAB3', 'nama_mk': 'Tata Kelola dan Manajemen Teknologi Informasi', 'sks': 3, 'semester': 'Ganjil 2425', 'clos': [{'clo_code': 'CLO-03', 'clo_desc': 'Mampu menganalisis permasalahan yang kompleks dalam bidang infokom dalam konteks enterprise atau masyarakat', 'bloom': '4 - Analyze'}, {'clo_code': 'CLO-02', 'clo_desc': 'Mampu menggunakan teknik, metode, perangkat lunak, atau kakas terkini untuk menghasilkan solusi di bidang sistem informasi dalam konteks kasus nyata', 'bloom': '3 - Apply'}, {'clo_code': 'CLO-04', 'clo_desc': 'Mampu mengevaluasi kinerja sistem informasi dan mengusulkan perbaikan untuk meningkatkan kontribusi sistem informasi terhadap tujuan bisnis organisasi.', 'bloom': '4 - Analyze'}]}]


UNIVERSITIES = [
    "Universitas Indonesia",
    "Institut Teknologi Bandung",
    "Universitas Gadjah Mada",
    "Universitas Airlangga",
    "Universitas Padjadjaran",
    "Binus University",
    "Telkom University",
]

LANGUAGES = [
    "Indonesian (Native)",
    "English (Professional Working Proficiency)",
]

TRACK_SKILLS = {
    "Software Engineering": [
        "Java", "Spring Boot", "Node.js", "React", "PostgreSQL",
        "Docker", "Git", "REST API", "Microservices", "Agile Scrum",
    ],
    "Data Science / Machine Learning": [
        "Python", "Scikit-learn", "XGBoost", "Pandas", "NumPy",
        "Tableau", "TensorFlow", "PyTorch", "Machine Learning", "Statistics",
    ],
    "Cybersecurity": [
        "SIEM", "Burp Suite", "OWASP", "Digital Forensics", "Incident Response",
        "Risk Assessment", "Network Security", "Python", "Linux", "Wireshark",
    ],
    "UX / Product Design": [
        "Figma", "Design Thinking", "Wireframing", "Prototyping",
        "User Research", "Usability Testing", "Accessibility", "Design Systems",
    ],
    "Networking / Infrastructure": [
        "Cisco", "Linux", "AWS", "Kubernetes", "Networking",
        "Routing", "VLAN", "Infrastructure", "Zabbix",
    ],
    "Business Analyst / Enterprise Systems": [
        "Business Analysis", "BPMN", "Power BI", "ERP", "SAP",
        "Requirements Gathering", "Stakeholder Management",
    ],
    "Data Engineering": [
        "Apache Airflow", "Spark", "Kafka", "dbt", "Snowflake",
        "SQL", "Python", "Data Warehousing",
    ],
    "IT Governance / Project Management": [
        "COBIT", "ITIL", "Risk Management", "Project Management", "Agile",
        "Scrum", "Jira",
    ],
    "Full-stack / DevOps": [
        "React", "Node.js", "Docker", "Terraform", "Kubernetes",
        "AWS", "CI/CD", "GitHub Actions",
    ],
    "AI / NLP": [
        "PyTorch", "Transformers", "LangChain", "LLMs", "NLP",
        "BERT", "mT5", "Python",
    ],
}

TRACK_CERTS = {
    "Software Engineering": [
        "Oracle Java Foundations", "AWS Cloud Practitioner", "Scrum Fundamentals Certified",
    ],
    "Data Science / Machine Learning": [
        "Google Data Analytics", "TensorFlow Developer Certificate", "Machine Learning Specialization",
    ],
    "Cybersecurity": [
        "Security+", "Certified Ethical Hacker (Training)", "Cisco CyberOps Associate",
    ],
    "UX / Product Design": [
        "Google UX Design", "Design Thinking Professional",
    ],
    "Networking / Infrastructure": [
        "CCNA", "AWS Cloud Practitioner",
    ],
    "Business Analyst / Enterprise Systems": [
        "SAP Fundamentals", "Business Analysis Foundation",
    ],
    "Data Engineering": [
        "Databricks Fundamentals", "Snowflake Essentials",
    ],
    "IT Governance / Project Management": [
        "ITIL Foundation", "Scrum Fundamentals Certified",
    ],
    "Full-stack / DevOps": [
        "AWS Cloud Practitioner", "Docker Associate Training",
    ],
    "AI / NLP": [
        "DeepLearning.AI NLP Specialization", "Generative AI Fundamentals",
    ],
}

# Issuer resmi per judul sertifikat (dipakai untuk generate Certificate.md)
CERT_ISSUERS = {
    "Oracle Java Foundations": "Oracle University",
    "AWS Cloud Practitioner": "Amazon Web Services (AWS) Training and Certification",
    "Scrum Fundamentals Certified": "SCRUMstudy",
    "Google Data Analytics": "Google Career Certificates (Coursera)",
    "TensorFlow Developer Certificate": "TensorFlow / Google",
    "Machine Learning Specialization": "DeepLearning.AI & Stanford Online (Coursera)",
    "Security+": "CompTIA",
    "Certified Ethical Hacker (Training)": "EC-Council",
    "Cisco CyberOps Associate": "Cisco Networking Academy",
    "Google UX Design": "Google Career Certificates (Coursera)",
    "Design Thinking Professional": "IDEO U",
    "CCNA": "Cisco Networking Academy",
    "SAP Fundamentals": "SAP Learning Hub",
    "Business Analysis Foundation": "International Institute of Business Analysis (IIBA)",
    "Databricks Fundamentals": "Databricks Academy",
    "Snowflake Essentials": "Snowflake University",
    "ITIL Foundation": "AXELOS / PeopleCert",
    "Docker Associate Training": "Docker, Inc.",
    "DeepLearning.AI NLP Specialization": "DeepLearning.AI (Coursera)",
    "Generative AI Fundamentals": "Google Cloud Skills Boost",
}

# Estimasi durasi kursus/pelatihan per judul sertifikat (jam)
CERT_HOURS = {
    "Oracle Java Foundations": 20,
    "AWS Cloud Practitioner": 25,
    "Scrum Fundamentals Certified": 12,
    "Google Data Analytics": 180,
    "TensorFlow Developer Certificate": 60,
    "Machine Learning Specialization": 100,
    "Security+": 40,
    "Certified Ethical Hacker (Training)": 40,
    "Cisco CyberOps Associate": 70,
    "Google UX Design": 180,
    "Design Thinking Professional": 15,
    "CCNA": 70,
    "SAP Fundamentals": 20,
    "Business Analysis Foundation": 18,
    "Databricks Fundamentals": 10,
    "Snowflake Essentials": 10,
    "ITIL Foundation": 16,
    "Docker Associate Training": 12,
    "DeepLearning.AI NLP Specialization": 60,
    "Generative AI Fundamentals": 10,
}

# =====================================================================
# SKALA NILAI (standar konversi huruf -> bobot & skor dasar per-CLO)
# =====================================================================

GRADE_POINTS = {
    "A": 4.0, "AB": 3.5, "B": 3.0, "BC": 2.5, "C": 2.0, "D": 1.0, "E": 0.0,
}

GRADE_BASE_SCORE = {
    "A": 90, "AB": 85, "B": 80, "BC": 75, "C": 70, "D": 60, "E": 45,
}

# Distribusi nilai MK yang di-generate untuk KHS (semua mahasiswa dianggap
# berprestasi baik, jadi dibobotkan ke arah A/AB/B). Bisa diubah sesuai
# kebutuhan (mis. dibedakan per-track) di iterasi berikutnya.
GRADE_CHOICES = ["A", "AB", "B", "BC", "C"]
GRADE_WEIGHTS = [0.35, 0.35, 0.20, 0.07, 0.03]


def random_gpa():
    return round(random.uniform(3.35, 3.95), 2)


def random_course_grade():
    return random.choices(GRADE_CHOICES, weights=GRADE_WEIGHTS, k=1)[0]


def generate_clo_score(course_grade):
    """Skor per-CLO = skor dasar dari nilai akhir MK, + jitter kecil,
    dibatasi 0-100."""
    base = GRADE_BASE_SCORE.get(course_grade, 75)
    score = base + random.randint(-7, 7)
    return max(0, min(100, score))


def score_to_grade(score):
    if score >= 85:
        return "A"
    elif score >= 80:
        return "AB"
    elif score >= 75:
        return "B"
    elif score >= 70:
        return "BC"
    elif score >= 65:
        return "C"
    elif score >= 50:
        return "D"
    return "E"


# =====================================================================
# GENERATOR CV (SAAT INI DI-NONAKTIFKAN DI main(), fungsi tetap disimpan)
# =====================================================================

def generate_summary(student, gpa):
    return f"""
Final-year Information Systems student specializing in {student['track']}.
Strong academic performance with GPA {gpa:.2f}/4.00 and practical experience
through internships, capstone projects, research activities, and technical
projects. Demonstrated ability to work collaboratively in multidisciplinary
teams while delivering technology solutions that address real-world business
problems.

Experienced in software development lifecycle, problem solving, stakeholder
communication, and modern technology practices relevant to the {student['track']}
domain. Interested in pursuing professional opportunities that combine
technical excellence, innovation, and continuous learning.
"""


def generate_organization_section():
    return """
## Leadership & Organizational Experience

### Information Systems Student Association
**Technology Division Coordinator (2023 - 2024)**

- Coordinated technology initiatives for student activities.
- Managed small project teams consisting of 5-10 members.
- Organized workshops related to software engineering and digital literacy.
- Collaborated with university stakeholders on technology-related events.

### University Technology Community
**Active Member**

- Participated in hackathons and technical competitions.
- Contributed to peer learning sessions and mentoring activities.
"""


def generate_achievement_section():
    return """
## Achievements

- Dean's List for multiple academic semesters.
- Top participant in university innovation competition.
- Selected presenter in faculty project showcase.
- Recognized for outstanding contribution in student projects.
"""


def generate_course_table(courses):
    rows = []
    rows.append("| Course | Credits | Grade |")
    rows.append("|----------|---------|---------|")
    for course_name, sks, grade in courses:
        rows.append(f"| {course_name} | {sks} | {grade} |")
    return "\n".join(rows)


def generate_cv(student):

    university = random.choice(UNIVERSITIES)
    gpa = random_gpa()

    skills = TRACK_SKILLS.get(student["track"], [])
    certs = TRACK_CERTS.get(student["track"], [])

    md = f"""# {student['name'].replace('_', ' ')}

## Professional Summary

{generate_summary(student, gpa)}

---

## Education

### Bachelor of Information Systems

**{university}**

- GPA: {gpa:.2f}/4.00
- Expected Graduation: 2025
- Specialization: {student['track']}

### Relevant Coursework

{generate_course_table(student['courses'])}

---

## Technical Skills

"""

    for skill in skills:
        md += f"- {skill}\n"

    md += "\n---\n\n## Professional Projects\n\n"

    for title, desc in student["cv_units"]:
        md += f"### {title}\n\n"
        md += f"{desc}\n\n"
        md += """
#### Key Contributions

- Participated in project planning and technical implementation.
- Applied best practices in software development and documentation.
- Collaborated with stakeholders and project team members.
- Conducted testing, validation, and continuous improvements.

#### Outcomes

- Improved understanding of real-world technology challenges.
- Demonstrated ability to deliver functional solutions.
- Strengthened communication and teamwork capabilities.

"""

    md += "\n---\n\n## Certifications\n\n"
    for cert in certs:
        md += f"- {cert}\n"
    md += "\n"

    md += generate_organization_section()
    md += "\n"
    md += generate_achievement_section()

    md += """

---

## Languages

- Indonesian (Native)
- English (Professional Working Proficiency)

---

## Career Interests

- Technology Consulting
- Digital Transformation
- Software Engineering
- Data-Driven Decision Making
- Innovation and Product Development

---

## References

Available upon request.
"""

    return md


# =====================================================================
# GENERATOR KHS: nilai per mata kuliah + rincian per CLO
# =====================================================================

def generate_student_khs_data(catalog=COURSE_CLO_CATALOG):
    """Generate nilai (akhir MK + per-CLO) untuk SEMUA mata kuliah di katalog.
    Return list of dict per course, siap dipakai untuk markdown & IPK."""
    hasil = []
    for course in catalog:
        grade = random_course_grade()
        clo_scores = []
        for clo in course["clos"]:
            score = generate_clo_score(grade)
            clo_scores.append({
                "clo_code": clo["clo_code"],
                "clo_desc": clo["clo_desc"],
                "bloom": clo["bloom"] or "-",
                "score": score,
            })
        hasil.append({
            "kode_mk": course["kode_mk"] or "-",
            "nama_mk": course["nama_mk"],
            "sks": course["sks"] or 3,
            "semester": course["semester"],
            "grade": grade,
            "clo_scores": clo_scores,
        })
    return hasil


def generate_khs_summary_table(khs_data):
    rows = []
    rows.append("| No | Kode MK | Nama Mata Kuliah | SKS | Semester | Nilai Akhir |")
    rows.append("|----|---------|-------------------|-----|----------|-------------|")
    for i, c in enumerate(khs_data, start=1):
        rows.append(
            f"| {i} | {c['kode_mk']} | {c['nama_mk']} | {c['sks']} | {c['semester']} | {c['grade']} |"
        )
    return "\n".join(rows)


def generate_khs_clo_section(khs_data):
    md = ""
    for c in khs_data:
        md += f"### {c['nama_mk']} ({c['kode_mk']}) - {c['sks']} SKS - Nilai Akhir: {c['grade']}\n\n"
        md += "| CLO | Deskripsi CLO | Bloom Taxonomy | Skor CLO (0-100) | Nilai CLO |\n"
        md += "|-----|---------------|-----------------|-------------------|-----------|\n"
        for clo in c["clo_scores"]:
            desc = clo["clo_desc"].replace("|", "/")
            md += (
                f"| {clo['clo_code']} | {desc} | {clo['bloom']} | "
                f"{clo['score']} | {score_to_grade(clo['score'])} |\n"
            )
        md += "\n"
    return md


def calculate_ipk(khs_data):
    total_bobot = 0.0
    total_sks = 0
    for c in khs_data:
        sks = c["sks"] or 3
        total_bobot += GRADE_POINTS.get(c["grade"], 0.0) * sks
        total_sks += sks
    if total_sks == 0:
        return 0.0, 0
    return round(total_bobot / total_sks, 2), total_sks


def generate_khs(student):
    khs_data = generate_student_khs_data()
    ipk, total_sks = calculate_ipk(khs_data)

    md = f"""# Kartu Hasil Studi (KHS)

## {student['name'].replace('_', ' ')}

- Program Studi: Sistem Informasi
- Spesialisasi: {student['track']}
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


# =====================================================================
# GENERATOR CERTIFICATE (BARU): sertifikat pelatihan/kursus dummy.
# Satu mahasiswa bisa punya lebih dari 1 sertifikat (mengikuti daftar
# TRACK_CERTS sesuai spesialisasi/track masing-masing).
# =====================================================================

def generate_credential_id(student_name, cert_name):
    """Bangkitkan ID kredensial acak yang cukup unik & terlihat realistis."""
    prefix = "".join(w[0] for w in cert_name.split() if w[0].isalnum()).upper()[:4]
    rand_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"CERT-{prefix}-{rand_part}"


def generate_verification_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=12))


def random_issue_date():
    """Tanggal terbit acak antara Jan 2023 - Des 2025."""
    start = datetime.date(2023, 1, 1)
    end = datetime.date(2025, 12, 31)
    delta_days = (end - start).days
    return start + datetime.timedelta(days=random.randint(0, delta_days))


BULAN_ID = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember",
}


def format_tanggal_id(d):
    return f"{d.day} {BULAN_ID[d.month]} {d.year}"


def generate_certificate(student, cert_name, cert_index):
    """Generate satu file sertifikat (markdown) untuk satu mahasiswa +
    satu judul sertifikasi/pelatihan."""

    issuer = CERT_ISSUERS.get(cert_name, "Professional Certification Body")
    hours = CERT_HOURS.get(cert_name, random.choice([10, 12, 15, 20, 25, 40]))
    issue_date = random_issue_date()
    # Sertifikat berlaku 2-3 tahun sejak terbit (khas sertifikasi vendor/profesional)
    valid_years = random.choice([2, 3])
    expiry_date = issue_date.replace(year=issue_date.year + valid_years)
    credential_id = generate_credential_id(student["name"], cert_name)
    verification_code = generate_verification_code()
    score = random.randint(78, 99)
    full_name = student["name"].replace("_", " ")

    md = f"""# Sertifikat Penyelesaian

---

## {cert_name}

Diberikan kepada:

### **{full_name}**

Program studi Sistem Informasi, spesialisasi {student['track']}, telah berhasil
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


def generate_all_certificates_for_student(student):
    """Generate semua sertifikat (>=1) untuk satu mahasiswa sesuai track-nya,
    kembalikan list of (filename, content)."""
    cert_names = TRACK_CERTS.get(student["track"], [])
    results = []
    for idx, cert_name in enumerate(cert_names, start=1):
        content = generate_certificate(student, cert_name, idx)
        # slug nama sertifikat untuk nama file
        slug = (
            cert_name.lower()
            .replace(" / ", "-")
            .replace(" ", "_")
            .replace("(", "")
            .replace(")", "")
        )
        filename = f"{student['name']}_Certificate_{idx}_{slug}.md"
        results.append((filename, content))
    return results


def main():

    for student in STUDENTS:

        # 1. Generate CV -> DI-NONAKTIFKAN sementara sesuai permintaan
        # cv_text = generate_cv(student)
        # cv_filename = os.path.join(OUT_DIR_CV, f"{student['name']}_CV.md")
        # with open(cv_filename, "w", encoding="utf-8") as f:
        #     f.write(cv_text)
        # print(f"Generated: {cv_filename}")

        # 2. Generate KHS
        khs_text = generate_khs(student)
        khs_filename = os.path.join(OUT_DIR_KHS, f"{student['name']}_KHS.md")
        with open(khs_filename, "w", encoding="utf-8") as f:
            f.write(khs_text)
        print(f"Generated: {khs_filename}")

        # 3. Generate Certificate(s) - 1 mahasiswa bisa lebih dari 1 sertifikat
        for cert_filename, cert_text in generate_all_certificates_for_student(student):
            cert_path = os.path.join(OUT_DIR_CERT, cert_filename)
            with open(cert_path, "w", encoding="utf-8") as f:
                f.write(cert_text)
            print(f"Generated: {cert_path}")

    total_certs = sum(len(TRACK_CERTS.get(s["track"], [])) for s in STUDENTS)
    print(f"\nDone. Generated {len(STUDENTS)} KHS(s) and {total_certs} certificate(s).")


if __name__ == "__main__":
    main()