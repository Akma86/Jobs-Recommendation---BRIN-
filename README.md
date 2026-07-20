# Career Recommendation System

Sistem rekomendasi karier berbasis NLP dan Explainable AI (XAI) yang mencocokkan kompetensi akademik mahasiswa dengan lowongan pekerjaan. Proyek ini dikembangkan sebagai bagian dari program magang di **BRIN (Badan Riset dan Inovasi Nasional)**.

## 📋 Deskripsi

Sistem ini mengintegrasikan data akademik mahasiswa (KHS/transkrip nilai), CV, dan data lowongan kerja hasil scraping untuk menghasilkan rekomendasi karier yang relevan dan dapat dijelaskan (explainable). Inovasi utama dari sistem ini adalah **pemetaan OBE (Outcome-Based Education) ke skill**, yang menerjemahkan capaian pembelajaran mata kuliah (CLO) menjadi representasi kompetensi/skill mahasiswa.

## ✨ Fitur Utama

- **Ekstraksi Data Akademik** — parsing KHS dan RPS/CLO dari file Excel dengan struktur merged-cell (Telkom University format)
- **Skill Extraction (NER)** — dictionary-based Named Entity Recognition terhadap kosakata kanonik berisi 78 skill
- **Vocabulary Expansion** — integrasi dengan ESCO dan O*NET untuk memperkaya kosakata skill
- **Semantic Matching** — menggunakan multilingual E5 embeddings untuk pencocokan makna antara profil mahasiswa dan lowongan kerja
- **Re-ranking** — cross-encoder untuk meningkatkan presisi hasil pencocokan

- **Explainable AI (XAI)** — menjelaskan alasan di balik setiap rekomendasi menggunakan:
  - SHAP (Shapley Values)
  - LIME
  - DiCE (Counterfactual Explanations)

## 🗂️ Sumber Data

- **KHS (transkrip nilai)** mahasiswa
- **CV** mahasiswa
- **Lowongan kerja** hasil scraping dari LinkedIn, Glassdoor, dan RemoteOK
- **RPS/CLO** dari kurikulum Sistem Informasi (Tel-U Jakarta, ITS, dan sumber paraphrase lainnya) — dikonsolidasikan menjadi `Merged_CLO_Dataset.xlsx`

## ⚙️ Arsitektur Pipeline

```
KHS/CV Mahasiswa ─┐
                   ├─► OBE-to-Skill Mapping ─► Student Skill Vector ─┐
RPS/CLO Dataset ───┘                                                 │
                                                                      ├─► E5 Embedding ─► Cross-Encoder Re-ranking ─► Fusion Scoring ─► XAI Explanation ─► Rekomendasi
Lowongan Kerja ──► Skill NER (78-skill vocab + ESCO/O*NET) ─────────┘
```

Orkestrasi end-to-end dijalankan melalui `full_pipeline.py`.

## 🛠️ Tech Stack

- **Bahasa:** Python
- **NLP/Embedding:** Multilingual E5, Cross-Encoder, IndoBERT
- **XAI:** SHAP, LIME, DiCE, Anchors, Integrated Gradients
- **Data Processing:** pandas, openpyxl
- **Sumber Vocabulary:** ESCO, O*NET

## ⚠️ Batasan (Limitations)

- Dataset RPS/CLO yang tersedia mencakup kurikulum **Sistem Informasi**, sementara data transkrip penulis berasal dari **Sains Data** — hal ini diterima sebagai batasan pada tahap prototipe.
- Skill extraction bersifat dictionary-based sehingga cakupannya terbatas pada kosakata kanonik yang telah didefinisikan.

## 🎓 Konteks Proyek

Dikembangkan sebagai bagian dari program magang di BRIN, di bawah bimbingan **Satrio Adi Priyambada**, oleh mahasiswa Program Studi Sains Data, Universitas Telkom.

## 📄 Lisensi

_Akmal Yaasir Fauzaan._
