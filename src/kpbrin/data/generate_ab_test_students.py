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
        "SAP Analytics Cloud",
        "ITIL Foundation",
        "Business Analysis Foundation"
    ]
}

# New Issuers and Hours for the extra certs not in the original list
EXTRA_CERTS = {
    "AWS Certified Developer - Associate": ("Amazon Web Services (AWS)", 40),
    "Meta Front-End Developer": ("Meta (Coursera)", 80),
    "Project Management Professional (PMP)": ("PMI", 35),
    "SAP Certified Application Associate": ("SAP", 40),
    "SAP Analytics Cloud": ("SAP", 30),
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

CERT_TOPICS = {
    "TensorFlow Developer Certificate": [
        "Building and training deep neural networks using TensorFlow and Keras",
        "Image classification and computer vision using Convolutional Neural Networks (CNN)",
        "Natural Language Processing (NLP), tokenization, embeddings, and sequence models",
        "Model optimization, transfer learning, and TensorFlow deployment"
    ],
    "DeepLearning.AI NLP Specialization": [
        "Sentiment analysis and word vector representations (Word2Vec, GloVe)",
        "Sequence-to-sequence models, attention mechanisms, and Transformer architectures",
        "HuggingFace transformer models and fine-tuning for question answering and translation",
        "LLMs and modern NLP application pipelines"
    ],
    "Google Data Analytics": [
        "Data preparation, data cleaning, and statistical processing using SQL and R",
        "Interactive dashboard development using Tableau and Google Data Studio",
        "Data visualization, hypothesis testing, and business reporting",
        "Data-driven decision making and presentation for stakeholders"
    ],
    "Machine Learning Specialization": [
        "Supervised learning algorithms: Linear Regression, Logistic Regression, Decision Trees, SVM",
        "Unsupervised learning: K-Means clustering, PCA, and anomaly detection",
        "Recommender systems, collaborative filtering, and content-based filtering",
        "Deep learning fundamentals and reinforcement learning concepts"
    ],
    "Generative AI Fundamentals": [
        "Foundational principles of Large Language Models (LLMs) and Generative AI",
        "Prompt engineering techniques and context augmentation",
        "Retrieval-Augmented Generation (RAG) architecture and vector search",
        "Responsible AI, bias mitigation, and safety evaluation"
    ],
    "AWS Certified Developer - Associate": [
        "Developing and deploying serverless applications using AWS Lambda and API Gateway",
        "Database management with Amazon DynamoDB and Amazon Aurora",
        "Containerized application deployment on Amazon ECS and EKS",
        "CI/CD pipelines with AWS CodePipeline, CodeBuild, and CloudWatch monitoring"
    ],
    "Meta Front-End Developer": [
        "Modern frontend development with React.js components, hooks, and state management",
        "Responsive web design with HTML5, CSS3, Flexbox, Grid, and Tailwind",
        "Advanced JavaScript (ES6+), asynchronous programming, and DOM manipulation",
        "RESTful API integration, UI/UX prototyping with Figma, and unit testing with Jest"
    ],
    "Docker Associate Training": [
        "Docker containerization fundamentals and multi-stage Dockerfile optimization",
        "Container networking, persistent volume storage, and port mapping",
        "Multi-container application orchestration using Docker Compose",
        "Microservices architecture and container security best practices"
    ],
    "Scrum Fundamentals Certified": [
        "Agile principles, Scrum framework, artifacts, and ceremony management",
        "Sprint planning, daily standups, sprint review, and retrospective facilitation",
        "User story mapping, backlog grooming, and Fibonacci point estimation",
        "Team collaboration and cross-functional agile leadership"
    ],
    "CCNA": [
        "IP routing and switching protocols (OSPF, EIGRP, BGP, Static Routing)",
        "VLAN configuration, inter-VLAN routing, and Spanning Tree Protocol (STP)",
        "Network infrastructure security, Access Control Lists (ACL), and NAT/PAT",
        "Cisco IOS CLI administration, network troubleshooting, and IP services (DHCP, DNS)"
    ],
    "AWS Cloud Practitioner": [
        "AWS Cloud value proposition, global infrastructure regions, and availability zones",
        "Core AWS services: Amazon EC2, Amazon VPC, S3, RDS, and Route 53",
        "Cloud security, AWS Identity and Access Management (IAM), and security groups",
        "Cloud economics, AWS pricing models, billing management, and support tiers"
    ],
    "Cisco CyberOps Associate": [
        "Security Operations Center (SOC) workflows, SIEM tools, and event correlation",
        "Network packet inspection, traffic analysis with Wireshark, and intrusion detection (IDS/IPS)",
        "Endpoint threat detection, malware analysis, and incident response procedures",
        "Security compliance standards (NIST, MITRE ATT&CK framework)"
    ],
    "Security+": [
        "Enterprise network security architecture and defense-in-depth strategies",
        "Threat vectors, vulnerabilities, penetration testing, and vulnerability scanning",
        "Cryptography, Public Key Infrastructure (PKI), TLS/SSL, and secure protocols",
        "Identity and access management, zero trust security model, and risk management"
    ],
    "ITIL Foundation": [
        "IT Service Management (ITSM) principles and Service Value System (SVS)",
        "ITIL 4 guiding principles and 4 dimensions of service management",
        "Key ITSM practices: Incident Management, Problem Management, Change Enablement",
        "Service level management, Continual Improvement, and IT governance"
    ],
    "Business Analysis Foundation": [
        "Business requirement gathering, elicitation, and stakeholder management",
        "Business Process Model and Notation (BPMN 2.0) workflow modeling",
        "Gap analysis, SWOT, feasibility studies, and business case development",
        "Functional and non-functional requirement specification (BRD, FRD)"
    ],
    "Project Management Professional (PMP)": [
        "Project lifecycle management across predictive, Agile, and hybrid methodologies",
        "Work Breakdown Structure (WBS), schedule baseline, and critical path method (CPM)",
        "Project risk management, Earned Value Management (EVM), and budget control",
        "Stakeholder engagement, procurement management, and quality assurance"
    ],
    "SAP Fundamentals": [
        "SAP ERP architecture, business integration, and SAP GUI navigation",
        "Organizational structures and master data in core enterprise modules",
        "Procure-to-Pay (P2P) and Order-to-Cash (O2C) business process execution",
        "Enterprise resource planning concepts and cross-module transactions"
    ],
    "SAP Certified Application Associate": [
        "SAP S/4HANA core business processes and financial management (FI/CO)",
        "Materials Management (MM) and Sales & Distribution (SD) integration",
        "Business partner concept, document splitting, and general ledger accounting",
        "Year-end closing procedures and SAP standard reporting"
    ],
    "SAP Analytics Cloud": [
        "SAP Analytics Cloud (SAC) data modeling, dimensions, and live data connections",
        "Building interactive executive stories, BI dashboards, and KPI visualizations",
        "Augmented analytics: Smart Predict, Smart Insights, and search-driven discovery",
        "Enterprise financial planning and forecasting models"
    ]
}

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

    topics = CERT_TOPICS.get(cert_name, [
        f"Konsep dan prinsip dasar {cert_name}",
        "Studi kasus dan praktik penerapan pada konteks industri nyata",
        "Latihan hands-on / proyek mini sebagai bagian dari penilaian akhir"
    ])
    cakupan_bullets = "\n".join([f"- {t}." for t in topics])

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

{cakupan_bullets}
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
