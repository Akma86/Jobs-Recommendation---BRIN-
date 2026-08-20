# TalentXAI - AI-Powered Job Recommendation & Explainable Career Intelligence

Sistem rekomendasi karir cerdas berbasis **Outcome-Based Education (OBE)**, **Portofolio Sertifikasi Industri Berbobot Kredibilitas (Tier A/B)**, dan **Explainable AI (SHAP & DiCE Multi-Stage)** yang mengintegrasikan model neural *Sentence-BERT Cross-Encoder* dengan antarmuka web modern layaknya platform pencari kerja profesional (*LinkedIn Jobs / Glints*).

Proyek ini dikembangkan sebagai bagian dari program magang riset di **Badan Riset dan Inovasi Nasional (BRIN)**.

---

## 🏛️ Arsitektur & Tech Stack

`	ext
[ Frontend: React + Vite + Lucide Icons ] (Port 3000)
                  │  HTTP REST API (< 5ms)
                  ▼
[ Backend: FastAPI High-Performance Server ] (Port 8000)
                  │
   ┌──────────────┴───────────────────────────────────────┐
   │                                                      │
[ In-Memory Caching Engine ]            [ Core AI & XAI Pipelines ]
- 10 Student Profiles (KHS + Certs)     - Multilingual E5 / SBERT Embeddings
- 4,570 Unified Job Postings            - Cross-Encoder Neural Re-Ranking
- 1,139 Online Courses (DiCE)           - SHAP Feature Attribution
                                        - Dynamic DiCE Counterfactuals
`

### Tech Stack:
- **Frontend:** React 18, Vite, Lucide Icons, Canvas Confetti, Modern CSS Design System.
- **Backend API:** FastAPI, Uvicorn, Pydantic.
- **AI & NLP Engine:** PyTorch, Sentence-Transformers (intfloat/multilingual-e5-large), HuggingFace Cross-Encoder (cross-encoder/mmarco-mMiniLMv2-L12-H384-v1).
- **Explainable AI (XAI):** SHAP (Shapley Additive exPlanations), DiCE (Diverse Counterfactual Explanations), Percentage-Based Narrative Generator.

---

## 📁 Struktur Direktori Repositori

`	ext
Jobs-Recommendation---BRIN-/
├── api_server.py                    # High-Performance FastAPI Backend Server
├── streamlit_app.py                 # Streamlit Prototype Application
├── requirements.txt                 # Python Dependencies
├── README.md                        # Dokumentasi Proyek
│
├── data/                            # Dataset & Profil Mahasiswa
│   ├── Mahasiswa/                   # KHS Markdown & Sertifikat Resmi (10 Mahasiswa)
│   ├── Mata Kuliah/                 # RPS & Konsolidasi CLO (97 Mata Kuliah)
│   ├── Pekerjaan/                   # Database 4.570 Lowongan Kerja Unified (LinkedIn, Glassdoor)
│   └── Sertifikasi/                 # Katalog 1.139 Kursus DiCE & Bobot Kredibilitas
│
├── docs/                            # Laporan Evaluasi & Literatur Riset
│   ├── images/                      # Diagram & Dokumentasi Visual
│   ├── papers/                      # Paper Referensi Riset BRIN
│   └── EKS12_AB_Test_Summary.md     # Rangkuman Evaluasi Eksperimen XAI
│
├── frontend/                        # Modern React + Vite Web Application
│   ├── src/
│   │   ├── components/              # Navbar, JobCard, JobDetailDrawer, Modals
│   │   ├── App.jsx                  # Main Interactive Dashboard
│   │   ├── index.css                # Professional CSS Design System
│   │   └── main.jsx                 # React Entry Point
│   ├── package.json
│   └── vite.config.js
│
├── results/                         # Hasil Eksperimen XAI (EKS01 s/d EKS12)
│   └── Eksperimen_XAI/
│       └── EKS12_AB_Test/           # Hasil A/B Testing 10 Mahasiswa (Before & After)
│
└── src/                             # Modular Python Core Library (kpbrin)
    ├── kpbrin/
    │   ├── core/                    # Pipeline, Embeddings, Caching, Issuer Tiers
    │   ├── data/                    # Parsers, Scraping, Cleaning & Skill Extractors
    │   ├── prototype/               # Streamlit UI Components
    │   ├── skill_gap/               # Skill Gap & Evaluation Modules
    │   └── xai/                     # SHAP, DiCE Engine, & Narrative Explanations
    └── scripts/                     # Automation & Fast Runner Scripts
`

---

## 🚀 Panduan Menjalankan Sistem

### 1. Menjalankan Backend FastAPI
`ash
python -m uvicorn api_server:app --host 127.0.0.1 --port 8000
`
Backend akan aktif di http://127.0.0.1:8000 (Waktu respon < 5ms dengan in-memory caching).

### 2. Menjalankan Frontend React (Job Seeker Portal)
`ash
cd frontend
npm install
npm run dev
`
Akses web aplikasi di peramban pada **http://127.0.0.1:3000**.

### 3. (Opsional) Menjalankan Streamlit Prototype
`ash
streamlit run streamlit_app.py
`

---

## ⭐ Fitur-Fitur Utama

1. **⚡ Lightning-Fast Career Matching (< 5ms):** Pemuatan instan seluruh profil mahasiswa dan ribuan data lowongan pekerjaan.
2. **💼 Real Job Seeker Experience:** Split-pane interface dengan feed lowongan, badge persentase kecocokan (95% Match), delta lonjakan sertifikat (+3.33), estimasi gaji, lokasi, dan bookmark.
3. **💬 Percentage-Based Narrative Explanations:** Penjelasan kecocokan berbasis bahasa alami Bahasa Indonesia yang menjabarkan tingkat keselarasan materi per sertifikat dan mata kuliah kurikulum.
4. **📊 SHAP Feature Attribution:** Grafik batang interaktif kontribusi positif/negatif masing-masing fitur terhadap skor kelayakan.
5. **🎯 Multi-Stage DiCE Learning Roadmap:** Rekomendasi kursus online riil (Google, AWS, Meta, IBM, Stanford) dari 1.139 katalog untuk menjembatani kesenjangan kompetensi (*skill gap*).
6. **🔄 Interactive What-If Simulator:** Simulasi interaktif perubahan skor secara langsung (*real-time*) saat mahasiswa mencentang sertifikasi target.
7. **🧭 Target Dream Career Explorer:** Penjelajah profesi impian untuk memetakan jalur karir dari 4.570 lowongan pekerjaan.

---

## 👥 Tim & Pembimbing
- **Pengembang:** Akmal Yaasir Fauzaan (Universitas Telkom)
- **Pembimbing Riset:** Satrio Adi Priyambada (Badan Riset dan Inovasi Nasional - BRIN)
