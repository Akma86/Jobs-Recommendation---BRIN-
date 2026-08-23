# -*- coding: utf-8 -*-
"""
Generator for all 10 Multi-Semester Students (Semester 1 to Semester 8, graduating senior standing)
Across 5 Key Industry Tracks:
1. Machine Learning & AI (Siti Rahma - Unggul vs Rizky Maulana - Perlu Penguatan)
2. Web & Full-Stack Development (Budi Santoso - Unggul vs Bayu Setiawan - Perlu Penguatan)
3. Networking & Cloud Infrastructure (Andi Wijaya - Unggul vs Kevin Aditya - Perlu Penguatan)
4. Sistem Informasi & Business Analyst (Nadia Putri - Unggul vs Farhan Hidayat - Perlu Penguatan)
5. SAP & Enterprise Systems (Dewi Lestari - Unggul vs Ilham Saputra - Perlu Penguatan)

Generates:
- Markdown KHS (.md) with Course summary table and Sub-CLO details across Semesters 1-8
- Transcript CSV (.csv)
- Sub-CLO detailed CSV (_sub_clo_detailed.csv)
- Full Profile JSON (_full_profile.json)
- 5 Industry Certificates (.md) per student
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

GRADE_POINTS = {"A": 4.0, "AB": 3.5, "B": 3.0, "BC": 2.5, "C": 2.0, "D": 1.0, "E": 0.0}

# Base Curriculum across 8 Semesters
CORE_COURSES_8_SEMESTERS = [
    # Semester 1 (18 SKS)
    {"semester": "Semester 1", "kode_mk": "CII1D3", "nama_mk": "Kalkulus", "nama_mk_en": "Calculus", "sks": 3},
    {"semester": "Semester 1", "kode_mk": "CII1A3", "nama_mk": "Algoritma dan Pemrograman", "nama_mk_en": "Algorithm and Programming", "sks": 4},
    {"semester": "Semester 1", "kode_mk": "CII1B3", "nama_mk": "Logika dan Struktur Diskrit", "nama_mk_en": "Discrete Structures and Logic", "sks": 3},
    {"semester": "Semester 1", "kode_mk": "CII1E3", "nama_mk": "Internalisasi Budaya dan Pembentukan Karakter", "nama_mk_en": "Character Building", "sks": 2},
    {"semester": "Semester 1", "kode_mk": "UKI1C2", "nama_mk": "Bahasa Indonesia", "nama_mk_en": "Indonesian Language", "sks": 2},
    {"semester": "Semester 1", "kode_mk": "UCKXADB2", "nama_mk": "Bahasa Inggris", "nama_mk_en": "English", "sks": 2},
    {"semester": "Semester 1", "kode_mk": "UKI1B2", "nama_mk": "Pancasila", "nama_mk_en": "Pancasila Education", "sks": 2},

    # Semester 2 (18 SKS)
    {"semester": "Semester 2", "kode_mk": "CII1F4", "nama_mk": "Algoritma dan Struktur Data", "nama_mk_en": "Algorithms and Data Structures", "sks": 4},
    {"semester": "Semester 2", "kode_mk": "CII1J3", "nama_mk": "Pemrograman Berorientasi Objek", "nama_mk_en": "Object-Oriented Programming", "sks": 3},
    {"semester": "Semester 2", "kode_mk": "CII1G3", "nama_mk": "Matematika Diskrit", "nama_mk_en": "Discrete Mathematics", "sks": 3},
    {"semester": "Semester 2", "kode_mk": "CII1C2", "nama_mk": "Probabilitas dan Statistik", "nama_mk_en": "Probability and Statistics", "sks": 3},
    {"semester": "Semester 2", "kode_mk": "CSI1B3", "nama_mk": "Sistem Basis Data", "nama_mk_en": "Database Systems", "sks": 3},
    {"semester": "Semester 2", "kode_mk": "CII2E3", "nama_mk": "Etika Profesi", "nama_mk_en": "Professional Ethics", "sks": 2},

    # Semester 3 (18 SKS)
    {"semester": "Semester 3", "kode_mk": "CII2F3", "nama_mk": "Sistem Operasi", "nama_mk_en": "Operating Systems", "sks": 3},
    {"semester": "Semester 3", "kode_mk": "CII1GAB3", "nama_mk": "Jaringan Komputer", "nama_mk_en": "Computer Networks", "sks": 3},
    {"semester": "Semester 3", "kode_mk": "CII2D3", "nama_mk": "Pengembangan Aplikasi Website", "nama_mk_en": "Web Application Development", "sks": 3},
    {"semester": "Semester 3", "kode_mk": "CII2EAB3", "nama_mk": "Desain Pengalaman Pengguna", "nama_mk_en": "User Experience Design", "sks": 3},
    {"semester": "Semester 3", "kode_mk": "CII2G3", "nama_mk": "Rekayasa Kebutuhan Perangkat Lunak", "nama_mk_en": "Software Requirements Engineering", "sks": 3},
    {"semester": "Semester 3", "kode_mk": "CII2H2", "nama_mk": "Kepemimpinan dan Komunikasi Interpersonal", "nama_mk_en": "Leadership and Communication", "sks": 3},

    # Semester 4 (18 SKS)
    {"semester": "Semester 4", "kode_mk": "CII3A3", "nama_mk": "Kecerdasan Artifisial dan Penerapannya", "nama_mk_en": "Artificial Intelligence & Applications", "sks": 3},
    {"semester": "Semester 4", "kode_mk": "CII3B3", "nama_mk": "Arsitektur dan Pengembangan Backend", "nama_mk_en": "Backend Architecture & Development", "sks": 3},
    {"semester": "Semester 4", "kode_mk": "CII3C3", "nama_mk": "Keamanan Sistem Informasi", "nama_mk_en": "Information Systems Security", "sks": 3},
    {"semester": "Semester 4", "kode_mk": "CII3EAB3", "nama_mk": "Proyek Perangkat Lunak", "nama_mk_en": "Software Project", "sks": 4},
    {"semester": "Semester 4", "kode_mk": "CII3D3", "nama_mk": "Pengujian dan Implementasi Sistem", "nama_mk_en": "System Testing & Implementation", "sks": 3},
    {"semester": "Semester 4", "kode_mk": "UCKXBDB2", "nama_mk": "Kewirausahaan", "nama_mk_en": "Entrepreneurship", "sks": 2},

    # Semester 5 (18 SKS)
    {"semester": "Semester 5", "kode_mk": "CII4A3", "nama_mk": "Komputasi Awan", "nama_mk_en": "Cloud Computing", "sks": 3},
    {"semester": "Semester 5", "kode_mk": "CII4B3", "nama_mk": "Pengembangan Aplikasi Bergerak", "nama_mk_en": "Mobile Application Development", "sks": 3},
    {"semester": "Semester 5", "kode_mk": "CII4C3", "nama_mk": "Pengolahan Bahasa Alami", "nama_mk_en": "Natural Language Processing", "sks": 3},
    {"semester": "Semester 5", "kode_mk": "CII4D3", "nama_mk": "Manajemen Proyek Tangkas", "nama_mk_en": "Agile Project Management", "sks": 3},
    {"semester": "Semester 5", "kode_mk": "CII4E3", "nama_mk": "Forensika Digital", "nama_mk_en": "Digital Forensics", "sks": 3},
    {"semester": "Semester 5", "kode_mk": "CII4F4", "nama_mk": "Metode Penelitian Dan Penyusunan Karya Ilmiah", "nama_mk_en": "Research Methodology", "sks": 3},

    # Semester 6 (18 SKS) - Upper Specialization
    {"semester": "Semester 6", "kode_mk": "CII5A3", "nama_mk": "Teknologi Machine Learning", "nama_mk_en": "Machine Learning Technology", "sks": 3},
    {"semester": "Semester 6", "kode_mk": "CII5B4", "nama_mk": "Penambangan Data", "nama_mk_en": "Data Mining", "sks": 3},
    {"semester": "Semester 6", "kode_mk": "CII5C3", "nama_mk": "Komputasi Lunak", "nama_mk_en": "Soft Computing", "sks": 3},
    {"semester": "Semester 6", "kode_mk": "CII5D3", "nama_mk": "Pengembangan Sistem dan Operasi", "nama_mk_en": "DevOps & System Operations", "sks": 3},
    {"semester": "Semester 6", "kode_mk": "CII5E2", "nama_mk": "Kerja Praktek dan Pengabdian Masyarakat", "nama_mk_en": "Internship & Community Service", "sks": 3},
    {"semester": "Semester 6", "kode_mk": "CII5F3", "nama_mk": "Teknologi Berkembang", "nama_mk_en": "Emerging Technologies", "sks": 3},

    # Semester 7 (18 SKS) - Advanced Capstone & Specialization
    {"semester": "Semester 7", "kode_mk": "CII6A3", "nama_mk": "Pemodelan dan Analitika Prediktif", "nama_mk_en": "Predictive Modeling and Analytics", "sks": 3},
    {"semester": "Semester 7", "kode_mk": "CII6B3", "nama_mk": "Arsitektur Enterprise", "nama_mk_en": "Enterprise Architecture", "sks": 3},
    {"semester": "Semester 7", "kode_mk": "CII6C3", "nama_mk": "Tata Kelola Keamanan Informasi", "nama_mk_en": "Information Security Governance", "sks": 3},
    {"semester": "Semester 7", "kode_mk": "CII6D3", "nama_mk": "Integrasi Aplikasi Enterprise", "nama_mk_en": "Enterprise Application Integration", "sks": 3},
    {"semester": "Semester 7", "kode_mk": "CII6E3", "nama_mk": "Desain dan Manajemen Jaringan Komputer", "nama_mk_en": "Network Design and Management", "sks": 3},
    {"semester": "Semester 7", "kode_mk": "CII6F3", "nama_mk": "Infrastruktur TI", "nama_mk_en": "IT Infrastructure", "sks": 3},

    # Semester 8 (12 SKS) - Graduating Semester (Final Capstone & Thesis)
    {"semester": "Semester 8", "kode_mk": "CII7A4", "nama_mk": "Capstone Design & Project", "nama_mk_en": "Capstone Design & Project", "sks": 4},
    {"semester": "Semester 8", "kode_mk": "CII7B4", "nama_mk": "Proteksi Aset Informasi", "nama_mk_en": "Information Asset Protection", "sks": 4},
    {"semester": "Semester 8", "kode_mk": "CII7C4", "nama_mk": "Pelatihan dan Sertifikasi", "nama_mk_en": "Training & Certification", "sks": 4},
]

# Track Specific Priority Courses to Give Strong/Weak Grades
TRACK_CORE_MK = {
    "Machine Learning": ["Teknologi Machine Learning", "Kecerdasan Artifisial dan Penerapannya", "Penambangan Data", "Pemodelan dan Analitika Prediktif", "Pengolahan Bahasa Alami", "Probabilitas dan Statistik"],
    "Web Development": ["Pengembangan Aplikasi Website", "Arsitektur dan Pengembangan Backend", "Proyek Perangkat Lunak", "Desain Pengalaman Pengguna", "Pengujian dan Implementasi Sistem", "Pengembangan Sistem dan Operasi"],
    "Networking & Cloud": ["Jaringan Komputer", "Desain dan Manajemen Jaringan Komputer", "Infrastruktur TI", "Komputasi Awan", "Sistem Operasi", "Keamanan Sistem Informasi", "Tata Kelola Keamanan Informasi"],
    "Sistem Informasi & Bisnis": ["Rekayasa Kebutuhan Perangkat Lunak", "Arsitektur Enterprise", "Manajemen Proyek Tangkas", "Desain Pengalaman Pengguna", "Sistem Basis Data", "Integrasi Aplikasi Enterprise"],
    "SAP & Enterprise Systems": ["Arsitektur Enterprise", "Integrasi Aplikasi Enterprise", "Sistem Basis Data", "Manajemen Proyek Tangkas", "Proteksi Aset Informasi", "Sistem Operasi"]
}

STUDENT_PROFILES = [
    # 1. ML Track
    {
        "folder": "Siti_Rahma_ML_Bagus", "name": "Siti Rahma", "nim": "1301201012",
        "major": "S1 Informatika", "track": "Machine Learning", "role": "AI & Machine Learning Specialist",
        "is_good": True, "semesters_active": "Semester 1 - 8 (Lulus Senior)"
    },
    {
        "folder": "Rizky_Maulana_ML_Jelek", "name": "Rizky Maulana", "nim": "1301201045",
        "major": "S1 Informatika", "track": "Machine Learning", "role": "AI & Machine Learning Specialist",
        "is_good": False, "semesters_active": "Semester 1 - 8 (Lulus Senior)"
    },

    # 2. Web Dev Track
    {
        "folder": "Budi_Santoso_Web_Bagus", "name": "Budi Santoso", "nim": "1301202023",
        "major": "S1 Informatika", "track": "Web Development", "role": "Full-Stack Software Engineer",
        "is_good": True, "semesters_active": "Semester 1 - 8 (Lulus Senior)"
    },
    {
        "folder": "Bayu_Setiawan_Web_Jelek", "name": "Bayu Setiawan", "nim": "1301202078",
        "major": "S1 Informatika", "track": "Web Development", "role": "Full-Stack Software Engineer",
        "is_good": False, "semesters_active": "Semester 1 - 8 (Lulus Senior)"
    },

    # 3. Networking Track
    {
        "folder": "Andi_Wijaya_Net_Bagus", "name": "Andi Wijaya", "nim": "1301203034",
        "major": "S1 Informatika", "track": "Networking & Cloud", "role": "Network & Cloud Infrastructure Specialist",
        "is_good": True, "semesters_active": "Semester 1 - 8 (Lulus Senior)"
    },
    {
        "folder": "Kevin_Aditya_Net_Jelek", "name": "Kevin Aditya", "nim": "1301203099",
        "major": "S1 Informatika", "track": "Networking & Cloud", "role": "Network & Cloud Infrastructure Specialist",
        "is_good": False, "semesters_active": "Semester 1 - 8 (Lulus Senior)"
    },

    # 4. SI Track
    {
        "folder": "Nadia_Putri_SI_Bagus", "name": "Nadia Putri", "nim": "1202204015",
        "major": "S1 Sistem Informasi", "track": "Sistem Informasi & Bisnis", "role": "Data / Business Analyst & Enterprise Systems",
        "is_good": True, "semesters_active": "Semester 1 - 8 (Lulus Senior)"
    },
    {
        "folder": "Farhan_Hidayat_SI_Jelek", "name": "Farhan Hidayat", "nim": "1202204067",
        "major": "S1 Sistem Informasi", "track": "Sistem Informasi & Bisnis", "role": "Data / Business Analyst & Enterprise Systems",
        "is_good": False, "semesters_active": "Semester 1 - 8 (Lulus Senior)"
    },

    # 5. SAP Track
    {
        "folder": "Dewi_Lestari_SAP_Bagus", "name": "Dewi Lestari", "nim": "1202205051",
        "major": "S1 Sistem Informasi", "track": "SAP & Enterprise Systems", "role": "SAP & Enterprise Architecture Specialist",
        "is_good": True, "semesters_active": "Semester 1 - 8 (Lulus Senior)"
    },
    {
        "folder": "Ilham_Saputra_SAP_Jelek", "name": "Ilham Saputra", "nim": "1202205082",
        "major": "S1 Sistem Informasi", "track": "SAP & Enterprise Systems", "role": "SAP & Enterprise Architecture Specialist",
        "is_good": False, "semesters_active": "Semester 1 - 8 (Lulus Senior)"
    },
]

TRACK_CERTS = {
    "Machine Learning": [
        {"id": 1, "slug": "tensorflow_developer", "title": "TensorFlow Developer Certificate", "issuer": "Google", "tier": "TIER_A", "tier_weight": 1.0, "hours": 80, "score": "95/100",
         "topics": ["Deep learning with TensorFlow & Keras", "Computer Vision and CNN models", "NLP and sequence models", "Model optimization and transfer learning"],
         "skills": ["TensorFlow", "Deep Learning", "CNN", "NLP", "Python", "Keras"]},
        {"id": 2, "slug": "deeplearning_ai_nlp", "title": "DeepLearning.AI NLP Specialization", "issuer": "DeepLearning.AI", "tier": "TIER_A", "tier_weight": 1.0, "hours": 75, "score": "92/100",
         "topics": ["Sentiment analysis & Word embeddings", "Sequence models & Transformers", "HuggingFace fine-tuning for LLMs", "Modern NLP pipelines"],
         "skills": ["NLP", "Transformers", "BERT", "HuggingFace", "PyTorch", "LLM"]},
        {"id": 3, "slug": "google_data_analytics", "title": "Google Data Analytics Professional Certificate", "issuer": "Google", "tier": "TIER_A", "tier_weight": 1.0, "hours": 65, "score": "90/100",
         "topics": ["Data preparation with SQL and R", "Interactive dashboards in Tableau", "Statistical hypothesis testing", "Data storytelling"],
         "skills": ["SQL", "R", "Tableau", "Data Analytics", "Statistics", "Data Cleaning"]},
        {"id": 4, "slug": "ml_specialization", "title": "Machine Learning Specialization", "issuer": "Stanford Online & DeepLearning.AI", "tier": "TIER_A", "tier_weight": 1.0, "hours": 70, "score": "96/100",
         "topics": ["Supervised algorithms: Linear/Logistic, Trees, SVM", "Unsupervised: K-Means, PCA, Anomaly Detection", "Recommender systems", "Reinforcement learning"],
         "skills": ["Machine Learning", "Scikit-Learn", "Regression", "Clustering", "PCA", "Algorithms"]},
        {"id": 5, "slug": "generative_ai_fundamentals", "title": "Generative AI Fundamentals", "issuer": "Databricks", "tier": "TIER_B", "tier_weight": 0.7, "hours": 40, "score": "88/100",
         "topics": ["LLM architectures and prompt engineering", "Retrieval-Augmented Generation (RAG)", "Vector databases and embeddings", "Responsible AI"],
         "skills": ["Generative AI", "RAG", "Prompt Engineering", "Vector DB", "LangChain"]}
    ],
    "Web Development": [
        {"id": 1, "slug": "meta_front_end_developer", "title": "Meta Front-End Developer Professional Certificate", "issuer": "Meta", "tier": "TIER_A", "tier_weight": 1.0, "hours": 80, "score": "95/100",
         "topics": ["React.js, components, hooks, context API", "Advanced ES6+ JavaScript & REST APIs", "TailwindCSS & responsive design", "Git and Jest testing"],
         "skills": ["React.js", "JavaScript", "HTML5/CSS3", "TailwindCSS", "REST APIs", "Git"]},
        {"id": 2, "slug": "aws_certified_developer", "title": "AWS Certified Developer - Associate", "issuer": "Amazon Web Services (AWS)", "tier": "TIER_A", "tier_weight": 1.0, "hours": 75, "score": "89/100",
         "topics": ["Serverless applications with AWS Lambda & API Gateway", "DynamoDB NoSQL and RDS databases", "CI/CD with AWS CodePipeline", "Cloud security with IAM"],
         "skills": ["AWS", "Lambda", "DynamoDB", "API Gateway", "Cloud Development", "Docker"]},
        {"id": 3, "slug": "backend_expert", "title": "Menjadi Back-End Developer Expert", "issuer": "Dicoding", "tier": "TIER_B", "tier_weight": 0.7, "hours": 90, "score": "94/100",
         "topics": ["Clean Architecture & Domain Driven Design", "RESTful API with Node.js & PostgreSQL", "Message brokers (RabbitMQ) & Redis cache", "JWT authentication & security hardening"],
         "skills": ["Node.js", "Express.js", "PostgreSQL", "Redis", "RabbitMQ", "Clean Architecture"]},
        {"id": 4, "slug": "docker_associate", "title": "Docker Associate Training", "issuer": "Docker", "tier": "TIER_B", "tier_weight": 0.7, "hours": 45, "score": "91/100",
         "topics": ["Containerization and Dockerfile best practices", "Multi-container applications with Docker Compose", "Volume management and networking", "Image registry optimization"],
         "skills": ["Docker", "Docker Compose", "Containers", "DevOps", "Microservices"]},
        {"id": 5, "slug": "scrum_fundamentals", "title": "Scrum Fundamentals Certified (SFC)", "issuer": "SCRUMstudy", "tier": "TIER_B", "tier_weight": 0.7, "hours": 30, "score": "96/100",
         "topics": ["Agile and Scrum framework principles", "Sprint planning, daily scrums, sprint reviews", "User stories, backlog grooming, burndown charts", "Cross-functional team collaboration"],
         "skills": ["Scrum", "Agile", "Sprint Planning", "Jira", "Project Management"]}
    ],
    "Networking & Cloud": [
        {"id": 1, "slug": "cisco_ccna", "title": "Cisco Certified Network Associate (CCNA 200-301)", "issuer": "Cisco Systems", "tier": "TIER_A", "tier_weight": 1.0, "hours": 90, "score": "915/1000",
         "topics": ["Routing & Switching (OSPF, VLANs, Trunking)", "IP Services (DHCP, NAT/PAT, DNS)", "Network Security (ACLs, Port Security)", "Network automation with Python & REST APIs"],
         "skills": ["Cisco IOS", "Routing & Switching", "OSPF", "VLAN", "ACL", "Network Automation"]},
        {"id": 2, "slug": "comptia_network_plus", "title": "CompTIA Network+ (N10-008)", "issuer": "CompTIA", "tier": "TIER_A", "tier_weight": 1.0, "hours": 75, "score": "840/900",
         "topics": ["Network architectures & Ethernet standards", "Network monitoring & traffic analysis (Wireshark)", "Network hardening & VPN tunnels", "Network troubleshooting methodology"],
         "skills": ["TCP/IP", "Network Troubleshooting", "VPN", "Firewalls", "Wireshark", "DNS/DHCP"]},
        {"id": 3, "slug": "aws_advanced_networking", "title": "AWS Certified Advanced Networking - Specialty", "issuer": "Amazon Web Services (AWS)", "tier": "TIER_A", "tier_weight": 1.0, "hours": 85, "score": "88/100",
         "topics": ["Hybrid IT network architecture with AWS Direct Connect", "AWS Transit Gateway & VPC Peering", "Network security with AWS Network Firewall", "Route 53 Resolver and CloudFront CDN"],
         "skills": ["AWS Networking", "VPC", "Direct Connect", "Transit Gateway", "CloudFront", "Route 53"]},
        {"id": 4, "slug": "red_hat_rhcsa", "title": "Red Hat Certified System Administrator (RHCSA)", "issuer": "Red Hat", "tier": "TIER_A", "tier_weight": 1.0, "hours": 80, "score": "285/300",
         "topics": ["Linux system administration & bash scripting", "Configuring network interfaces & firewalld", "Managing storage volumes (LVM)", "Container deployment with Podman and SELinux"],
         "skills": ["Linux", "RHEL", "Bash Scripting", "Firewalld", "LVM", "Podman", "SELinux"]},
        {"id": 5, "slug": "mikrotik_mtcna", "title": "MikroTik Certified Network Associate (MTCNA)", "issuer": "MikroTik", "tier": "TIER_B", "tier_weight": 0.7, "hours": 60, "score": "92/100",
         "topics": ["MikroTik RouterOS & Winbox configuration", "Static routing, DHCP server & client", "Firewall filter rules, NAT masquerade, QoS queues", "Wireless point-to-point & VPN tunnels"],
         "skills": ["MikroTik RouterOS", "Firewall", "NAT", "Bandwidth Management", "VPN", "Routing"]}
    ],
    "Sistem Informasi & Bisnis": [
        {"id": 1, "slug": "systems_analyst_bnsp", "title": "Sertifikasi Profesi Analis Sistem Informasi (Systems Analyst)", "issuer": "BNSP", "tier": "TIER_A", "tier_weight": 1.0, "hours": 80, "score": "Kompeten (A)",
         "topics": ["Business Process Modeling with BPMN 2.0", "System architecture & UML design (Class, Sequence)", "Software Requirements Specification (SRS)", "User Acceptance Testing (UAT) & SDLC"],
         "skills": ["BPMN", "UML", "Systems Analysis", "Requirements Engineering", "SRS", "UAT"]},
        {"id": 2, "slug": "google_project_management", "title": "Google Project Management Professional Certificate", "issuer": "Google", "tier": "TIER_A", "tier_weight": 1.0, "hours": 70, "score": "94/100",
         "topics": ["Project lifecycle, initiation, and project charter", "Agile & Waterfall methodologies, Scrum roles", "Risk management, budgeting, and quality control", "Stakeholder communications"],
         "skills": ["Project Management", "Agile", "Scrum", "Risk Management", "Asana", "Stakeholder Management"]},
        {"id": 3, "slug": "google_data_analytics", "title": "Google Data Analytics Professional Certificate", "issuer": "Google", "tier": "TIER_A", "tier_weight": 1.0, "hours": 65, "score": "91/100",
         "topics": ["SQL querying for business metrics", "Data cleaning & transformation", "Interactive dashboards in Tableau", "Business insights reporting"],
         "skills": ["SQL", "Tableau", "Data Analysis", "Spreadsheets", "Business Intelligence"]},
        {"id": 4, "slug": "itil_foundation", "title": "ITIL 4 Foundation Certificate in IT Service Management", "issuer": "AXELOS", "tier": "TIER_B", "tier_weight": 0.7, "hours": 45, "score": "88/100",
         "topics": ["ITIL Service Value System (SVS)", "Four dimensions of service management", "Service level management, incident & change management", "Continual improvement"],
         "skills": ["ITIL 4", "ITSM", "Service Management", "Incident Management", "Change Management"]},
        {"id": 5, "slug": "business_analysis_foundation", "title": "Business Analysis Foundation", "issuer": "BCS, The Chartered Institute for IT", "tier": "TIER_B", "tier_weight": 0.7, "hours": 40, "score": "89/100",
         "topics": ["Strategic business analysis & GAP analysis", "Business case development & ROI feasibility", "Stakeholder analysis (RACI matrix)", "Requirements elicitation techniques"],
         "skills": ["Business Analysis", "Gap Analysis", "Business Case", "Requirements", "RACI Matrix"]}
    ],
    "SAP & Enterprise Systems": [
        {"id": 1, "slug": "sap_certified_application_associate", "title": "SAP Certified Application Associate - SAP S/4HANA", "issuer": "SAP", "tier": "TIER_A", "tier_weight": 1.0, "hours": 85, "score": "89/100",
         "topics": ["SAP S/4HANA enterprise core architecture", "Business processes in Financials (FI) & Sales (SD)", "Master data configuration and organizational structures", "SAP Fiori user experience"],
         "skills": ["SAP S/4HANA", "SAP ERP", "SAP FI/CO", "SAP SD", "SAP Fiori", "Enterprise Architecture"]},
        {"id": 2, "slug": "sap_analytics_cloud", "title": "SAP Analytics Cloud - Integrated Planning & BI", "issuer": "SAP", "tier": "TIER_A", "tier_weight": 1.0, "hours": 60, "score": "92/100",
         "topics": ["Enterprise data modeling with SAC", "Interactive executive dashboards & digital boardroom", "Augmented analytics with Smart Predict", "Financial planning models in SAP"],
         "skills": ["SAP Analytics Cloud", "BI Dashboards", "Data Modeling", "Smart Predict", "SAP BusinessObjects"]},
        {"id": 3, "slug": "sap_fundamentals", "title": "SAP Enterprise Systems Fundamentals", "issuer": "SAP", "tier": "TIER_B", "tier_weight": 0.7, "hours": 45, "score": "94/100",
         "topics": ["ERP core concepts & integration touchpoints", "Procure-to-pay & Order-to-cash end-to-end cycles", "SAP GUI and navigation essentials", "Enterprise reporting"],
         "skills": ["SAP ERP", "Procure-to-Pay", "Order-to-Cash", "Business Processes", "Enterprise Integration"]},
        {"id": 4, "slug": "itil_foundation", "title": "ITIL 4 Foundation in IT Service Management", "issuer": "AXELOS", "tier": "TIER_B", "tier_weight": 0.7, "hours": 45, "score": "88/100",
         "topics": ["Service desk operations in enterprise IT", "Change enablement & release management", "Service level agreements (SLA)", "ITSM governance"],
         "skills": ["ITIL 4", "ITSM", "Enterprise Governance", "SLA Management"]},
        {"id": 5, "slug": "business_analysis_foundation", "title": "Enterprise Business Analysis Foundation", "issuer": "BCS", "tier": "TIER_B", "tier_weight": 0.7, "hours": 40, "score": "90/100",
         "topics": ["Enterprise architecture alignment with TOGAF", "Business process optimization", "Cost-benefit and feasibility study", "Change management"],
         "skills": ["Enterprise Architecture", "BPM", "Feasibility Study", "TOGAF", "Change Management"]}
    ]
}

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
**{cert['hours']} jam**.

---

## Detail Sertifikat

| Keterangan | Nilai |
|---|---|
| Nama Penerima | {student['name']} |
| Judul Sertifikasi | {cert['title']} |
| Penyelenggara / Issuer | {cert['issuer']} |
| Tanggal Terbit | {format_date_id("2024-06-15")} |
| Berlaku Hingga | {format_date_id("2027-06-15")} |
| Durasi Pelatihan | {cert['hours']} jam |
| Skor Akhir | {cert['score']} |
| ID Kredensial | CERT-{cert['slug'].upper()[:8]}-{random.randint(100000, 999999)} |
| Kode Verifikasi | VER-{random.randint(100000, 999999)} |

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
    print("Generating complete multi-semester datasets (Semesters 1 - 8) for all 10 students across 5 tracks...")
    random.seed(42)

    # 1. Load Sub-CLO Master Catalog
    sub_clo_path = os.path.join(ROOT_DIR, "data", "Mata Kuliah", "sub_clo_profiles.csv")
    df_sub_master = pd.read_csv(sub_clo_path)

    for st in STUDENT_PROFILES:
        st_name = st["name"]
        st_folder = st["folder"]
        st_track = st["track"]
        is_good = st["is_good"]
        priority_mks = TRACK_CORE_MK.get(st_track, [])

        transcript_rows = []
        sub_clo_detailed_rows = []
        courses_json_list = []
        total_pts = 0.0
        total_sks = 0

        for idx, c in enumerate(CORE_COURSES_8_SEMESTERS, 1):
            c_name = c["nama_mk"]
            c_code = c["kode_mk"]
            c_sks = c["sks"]
            c_smt = c["semester"]

            # Determine grade based on student standing (Bagus vs Jelek)
            if is_good:
                grade = "A" if c_name in priority_mks or random.random() < 0.75 else "AB"
            else:
                if c_name in priority_mks:
                    grade = random.choice(["D", "E", "C"])
                else:
                    grade = random.choice(["C", "BC", "B"])

            gp = GRADE_POINTS[grade]
            total_pts += gp * c_sks
            total_sks += c_sks

            # Sub-CLOs
            sub_df = df_sub_master[df_sub_master["course_name"] == c_name]
            if sub_df.empty:
                sub_clos = [
                    {"code": f"CLO-{i+1:02d}", "text": f"Mampu menguasai kompetensi terapan pada {c_name} secara komprehensif.", "bloom": "3 - Apply"}
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
                if grade == "A":
                    base_sc = 93.0
                elif grade == "AB":
                    base_sc = 84.0
                elif grade == "B":
                    base_sc = 76.0
                elif grade == "BC":
                    base_sc = 68.0
                elif grade == "C":
                    base_sc = 60.0
                elif grade == "D":
                    base_sc = 48.0
                else:
                    base_sc = 30.0

                sc = round(base_sc + random.uniform(-3.0, 3.5), 1)
                sc = max(20.0, min(99.0, sc))
                scores.append(sc)

                sub_clo_detailed_rows.append({
                    "nim": st["nim"],
                    "nama_mahasiswa": st_name,
                    "jurusan": st["major"],
                    "semester": c_smt,
                    "kode_mk": c_code,
                    "nama_mk": c_name,
                    "sks": c_sks,
                    "nilai_akhir_mk": grade,
                    "sub_clo_code": s_clo["code"],
                    "sub_clo_text": s_clo["text"],
                    "bloom_taxonomy": s_clo["bloom"],
                    "sub_clo_score": sc,
                    "sub_clo_grade": grade
                })

                course_sub_json.append({
                    "sub_clo_code": s_clo["code"],
                    "sub_clo_text": s_clo["text"],
                    "bloom_taxonomy": s_clo["bloom"],
                    "sub_clo_score": sc,
                    "sub_clo_grade": grade
                })

            avg_score = round(sum(scores) / len(scores), 1) if scores else 80.0

            transcript_rows.append({
                "no": idx,
                "semester": c_smt,
                "kode_mk": c_code,
                "nama_mk": c_name,
                "nama_mk_en": c["nama_mk_en"],
                "sks": c_sks,
                "nilai_huruf": grade,
                "bobot_ipk": gp,
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
                "nilai_huruf": grade,
                "bobot_ipk": gp,
                "skor_rata_sub_clo": avg_score,
                "jumlah_sub_clo": len(sub_clos),
                "sub_clos": course_sub_json
            })

        ipk = round(total_pts / total_sks, 2)
        print(f"Generated: {st_name} ({st_track}) - IPK: {ipk:.2f} | Total SKS: {total_sks}")

        # 1. Transcript CSV
        df_transcript = pd.DataFrame(transcript_rows)
        t_csv_path = os.path.join(MULTI_KHS_DIR, f"{st_folder}_transcript.csv")
        df_transcript.to_csv(t_csv_path, index=False)

        # 2. Sub-CLO Detailed CSV
        df_sub_detailed = pd.DataFrame(sub_clo_detailed_rows)
        s_csv_path = os.path.join(MULTI_KHS_DIR, f"{st_folder}_sub_clo_detailed.csv")
        df_sub_detailed.to_csv(s_csv_path, index=False)

        # 3. Full Profile JSON
        semester_summaries = []
        for smt_num in range(1, 9):
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
                "name": st_name,
                "nim": st["nim"],
                "major": st["major"],
                "role_specialization": st["role"],
                "track": st_track,
                "total_sks": total_sks,
                "cumulative_gpa": ipk,
                "semester_range": "Semester 1 - 8",
                "total_courses": len(CORE_COURSES_8_SEMESTERS),
                "total_sub_clos": len(sub_clo_detailed_rows)
            },
            "semester_summaries": semester_summaries
        }
        json_path = os.path.join(MULTI_KHS_DIR, f"{st_folder}_full_profile.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(full_profile, f, indent=2, ensure_ascii=False)

        # 4. KHS Markdown
        khs_lines = [
            "# Kartu Hasil Studi (KHS)",
            "",
            f"## {st_name}",
            "",
            f"- Program Studi: {st['major']}",
            f"- Spesialisasi: {st['role']}",
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

        for idx, c in enumerate(CORE_COURSES_8_SEMESTERS, 1):
            g = df_transcript.loc[df_transcript["no"] == idx, "nilai_huruf"].values[0]
            khs_lines.append(f"| {idx} | {c['kode_mk']} | {c['nama_mk']} | {c['sks']} | {c['semester']} | {g} |")

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

        khs_md_path = os.path.join(MULTI_KHS_DIR, f"{st_folder}_KHS.md")
        with open(khs_md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(khs_lines))

        # Also write to generated_markdown_khs
        gen_khs_path = os.path.join(ROOT_DIR, "data", "Mahasiswa", "generated_markdown_khs", f"{st_folder}_KHS.md")
        with open(gen_khs_path, "w", encoding="utf-8") as f:
            f.write("\n".join(khs_lines))

        # 5. Certificates Markdown
        st_multi_cert_dir = os.path.join(MULTI_CERT_DIR, st_folder)
        st_gen_cert_dir = os.path.join(GEN_CERT_DIR, st_folder)
        os.makedirs(st_multi_cert_dir, exist_ok=True)
        os.makedirs(st_gen_cert_dir, exist_ok=True)

        certs_list = TRACK_CERTS.get(st_track, [])
        for cert in certs_list:
            md_c = generate_markdown_cert(st, cert)
            fname = f"{st_folder}_Certificate_{cert['id']}_{cert['slug']}.md"
            with open(os.path.join(st_multi_cert_dir, fname), "w", encoding="utf-8") as f:
                f.write(md_c)
            with open(os.path.join(st_gen_cert_dir, fname), "w", encoding="utf-8") as f:
                f.write(md_c)

    print("\nSUCCESS: All 10 multi-semester student profiles & certificates generated!")

if __name__ == "__main__":
    main()
