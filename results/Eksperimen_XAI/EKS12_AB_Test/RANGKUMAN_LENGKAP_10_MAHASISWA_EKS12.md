# Rangkuman Komprehensif 10 Mahasiswa — Eksperimen XAI EKS12 (A/B Testing Before vs After)

**Tanggal Evaluasi:** 17 Agustus 2026  
**Lokasi Data:** `results/Eksperimen_XAI/EKS12_AB_Test/`  
**Deskripsi Dokumen:** Rangkuman lengkap terperinci untuk masing-masing dari 10 profil mahasiswa bernama nyata yang mencakup perbandingan Top-5 rekomendasi karir, atribusi fitur SHAP, dan evolusi saran pelatihan DiCE (1.139 kursus online).

---

## 🏆 Ringkasan Eksekutif: 10 Profil Mahasiswa

| No | Mahasiswa | Peminatan | Profil IPK | Sertifikat Dimiliki | Top-1 Before | Top-1 After | Kenaikan Skor (Δ) |
|:---:|---|:---:|:---:|:---:|---|---|:---:|
| 1 | **Siti Rahma** | `ML` | Bagus (IPK ~3.82) | **5 Certs** | Web Developer (HTML,CSS) | Remote (`4.80`) | **AI/ML Engineer (`8.01`)** | **`+3.21`** 🚀 |
| 2 | **Rizky Maulana** | `ML` | Jelek (IPK ~2.03) | **5 Certs** | ES Application Developer II (`3.56`) | **AI/ML Engineer (`5.71`)** | **`+2.15`** 🚀 |
| 3 | **Budi Santoso** | `Web` | Bagus (IPK ~3.82) | **4 Certs** | Web Developer (HTML,CSS) | Remote (`4.80`) | **Junior Frontend Developer (`8.70`)** | **`+3.89`** 🚀 |
| 4 | **Bayu Setiawan** | `Web` | Jelek (IPK ~2.03) | **4 Certs** | ES Application Developer II (`3.56`) | **UI Frontend Developer (`7.19`)** | **`+3.62`** 🚀 |
| 5 | **Andi Wijaya** | `Net` | Bagus (IPK ~3.82) | **4 Certs** | Web Developer (HTML,CSS) | Remote (`4.66`) | **AI/ML Engineer (`8.09`)** | **`+3.43`** 🚀 |
| 6 | **Kevin Aditya** | `Net` | Jelek (IPK ~2.03) | **4 Certs** | ES Application Developer II (`3.15`) | **AI/ML Engineer (`6.31`)** | **`+3.16`** 🚀 |
| 7 | **Nadia Putri** | `SI` | Bagus (IPK ~3.82) | **4 Certs** | Web Developer (HTML,CSS) | Remote (`4.80`) | **Web Developer (HTML,CSS) | Remote (`4.80`)** | **`+0.00`** 🚀 |
| 8 | **Farhan Hidayat** | `SI` | Jelek (IPK ~2.03) | **4 Certs** | ES Application Developer II (`3.15`) | **ES Application Developer II (`3.15`)** | **`+0.00`** 🚀 |
| 9 | **Dewi Lestari** | `SAP` | Bagus (IPK ~3.82) | **6 Certs** | Web Developer (HTML,CSS) | Remote (`4.80`) | **Web Developer (HTML,CSS) | Remote (`4.80`)** | **`+0.00`** 🚀 |
| 10 | **Ilham Saputra** | `SAP` | Jelek (IPK ~2.03) | **6 Certs** | ES Application Developer II (`3.29`) | **ES Application Developer II (`3.29`)** | **`+0.00`** 🚀 |

---

## 1. Siti Rahma — Track: `ML` (Bagus (IPK ~3.82))

### 📜 Daftar 5 Sertifikasi Industri yang Dimiliki:
1. **TensorFlow Developer Certificate** — *TensorFlow / Google* (Tier A (1.0))
2. **DeepLearning.AI NLP Specialization** — *DeepLearning.AI (Coursera)* (Tier A (1.0))
3. **Google Data Analytics** — *Google Career Certificates (Coursera)* (Tier A (1.0))
4. **Machine Learning Specialization** — *DeepLearning.AI & Stanford Online (Coursera)* (Tier A (1.0))
5. **Generative AI Fundamentals** — *Google Cloud Skills Boost* (Tier A (1.0))

### 📊 Tabel Komparasi Top-5 Rekomendasi Karir (Before vs After):
| Peringkat | Lowongan Pekerjaan | Perusahaan | Skor Before (Matkul) | Skor After (+ Certs) | Lonjakan (Δ) | Status Dampak |
|:---:|---|---|:---:|:---:|:---:|---|
| **#1** | **AI/ML Engineer** | Centraprise | `0.00` | `8.01` | **`+8.01`** | 🚀 **Lonjakan Masif** |
| **#2** | **Junior Frontend Developer** | MagicSet | `0.00` | `6.76` | **`+6.76`** | 🚀 **Lonjakan Masif** |
| **#3** | **Machine Learning Engineer** | KTek Resourcing | `-1.01` | `5.17` | **`+6.18`** | 🚀 **Lonjakan Masif** |
| **#4** | **Machine Learning Engineer** | Happy Elements | `-0.09` | `5.01` | **`+5.10`** | 🚀 **Lonjakan Masif** |
| **#5** | **Web Developer (HTML,CSS) | Remote** | Crossing Hurdles | `4.80` | `4.80` | **`+0.00`** | 📌 **Stabil (Dominan Matkul)** |

💡 **Transformasi Karir Juara 1:**
- **Sebelum Sertifikat (Before):** `Web Developer (HTML,CSS) | Remote` (Skor: `4.80`)
- **Setelah Sertifikat (After):** `AI/ML Engineer` (Skor: `8.01`) ➔ *Kenaikan Total: `+3.21 poin`*

### 🔍 Atribusi Fitur Utama (SHAP Top Features):
- **Sertifikat: TensorFlow Developer Certificate**: Kontribusi `+8.011 poin` terhadap `AI/ML Engineer`

### 🧭 Bimbingan Karir DiCE 2-Tahap (Multi-Stage 1.139 Kursus Riil):
#### A. DiCE Tahap 1 — Saran Kursus Fondasi Awal (Kondisi *Before* / Matkul Saja):
- Untuk `Web Developer (HTML,CSS) | Remote`: Ambil kursus/sertifikasi 'Meta Front-End Developer' [Meta, Beginner] (Relevansi: 0.37, Est. boost: +0.90)
- Untuk `Web Developer (HTML,CSS) | Remote`: Ambil kursus/sertifikasi 'Meta Back-End Developer' [Meta, Beginner] (Relevansi: 0.34, Est. boost: +0.84)
- Untuk `Web Developer (HTML,CSS) | Remote`: Ambil kursus/sertifikasi 'Introduction to Back-End Development' [Meta, Beginner] (Relevansi: 0.32, Est. boost: +0.79)

#### B. DiCE Tahap 2 — Saran Spesialisasi Lanjutan (Kondisi *After* / Setelah Punya Sertifikat):
- Untuk `AI/ML Engineer`: Ambil kursus/sertifikasi 'Digital Transformation Using AI/ML with Google Cloud' [Google Cloud, Beginner] (Relevansi: 0.34, Est. boost: +0.83)
- Untuk `AI/ML Engineer`: Ambil kursus/sertifikasi 'Python for Data Science, AI & Development' [IBM, Beginner] (Relevansi: 0.28, Est. boost: +0.69)
- Untuk `AI/ML Engineer`: Ambil kursus/sertifikasi 'Data Engineering, Big Data and ML on Google Cloud 日本語版' [Google Cloud, Intermediate] (Relevansi: 0.34, Est. boost: +1.02)

---

## 2. Rizky Maulana — Track: `ML` (Jelek (IPK ~2.03))

### 📜 Daftar 5 Sertifikasi Industri yang Dimiliki:
1. **TensorFlow Developer Certificate** — *TensorFlow / Google* (Tier A (1.0))
2. **DeepLearning.AI NLP Specialization** — *DeepLearning.AI (Coursera)* (Tier A (1.0))
3. **Google Data Analytics** — *Google Career Certificates (Coursera)* (Tier A (1.0))
4. **Machine Learning Specialization** — *DeepLearning.AI & Stanford Online (Coursera)* (Tier A (1.0))
5. **Generative AI Fundamentals** — *Google Cloud Skills Boost* (Tier A (1.0))

### 📊 Tabel Komparasi Top-5 Rekomendasi Karir (Before vs After):
| Peringkat | Lowongan Pekerjaan | Perusahaan | Skor Before (Matkul) | Skor After (+ Certs) | Lonjakan (Δ) | Status Dampak |
|:---:|---|---|:---:|:---:|:---:|---|
| **#1** | **AI/ML Engineer** | Centraprise | `0.00` | `5.71` | **`+5.71`** | 🚀 **Lonjakan Masif** |
| **#2** | **Junior Frontend Developer** | MagicSet | `0.00` | `4.82` | **`+4.82`** | 🚀 **Lonjakan Masif** |
| **#3** | **AI/ML Engineer — Job Posting** | Get Hire Technologies Inc. | `-0.41` | `4.12` | **`+4.53`** | 🚀 **Lonjakan Masif** |
| **#4** | **Data Analyst** | Infinite Computer Solutions | `0.00` | `3.74` | **`+3.74`** | 🚀 **Lonjakan Masif** |
| **#5** | **Machine Learning Engineer** | Happy Elements | `-0.06` | `3.58` | **`+3.63`** | 🚀 **Lonjakan Masif** |

💡 **Transformasi Karir Juara 1:**
- **Sebelum Sertifikat (Before):** `ES Application Developer II` (Skor: `3.56`)
- **Setelah Sertifikat (After):** `AI/ML Engineer` (Skor: `5.71`) ➔ *Kenaikan Total: `+2.15 poin`*

### 🔍 Atribusi Fitur Utama (SHAP Top Features):
- **Sertifikat: TensorFlow Developer Certificate**: Kontribusi `+5.708 poin` terhadap `AI/ML Engineer`

### 🧭 Bimbingan Karir DiCE 2-Tahap (Multi-Stage 1.139 Kursus Riil):
#### A. DiCE Tahap 1 — Saran Kursus Fondasi Awal (Kondisi *Before* / Matkul Saja):
- Untuk `ES Application Developer II`: Ambil kursus/sertifikasi 'Foundations of User Experience (UX) Design' [Google, Beginner] (Relevansi: 0.19, Est. boost: +0.48)
- Untuk `ES Application Developer II`: Ambil kursus/sertifikasi 'System Administration and IT Infrastructure Services' [Google, Beginner] (Relevansi: 0.19, Est. boost: +0.46)
- Untuk `ES Application Developer II`: Ambil kursus/sertifikasi 'Cybersecurity Roles, Processes & Operating System Security' [IBM, Beginner] (Relevansi: 0.18, Est. boost: +0.45)

#### B. DiCE Tahap 2 — Saran Spesialisasi Lanjutan (Kondisi *After* / Setelah Punya Sertifikat):
- Untuk `AI/ML Engineer`: Ambil kursus/sertifikasi 'Digital Transformation Using AI/ML with Google Cloud' [Google Cloud, Beginner] (Relevansi: 0.34, Est. boost: +0.83)
- Untuk `AI/ML Engineer`: Ambil kursus/sertifikasi 'Python for Data Science, AI & Development' [IBM, Beginner] (Relevansi: 0.28, Est. boost: +0.69)
- Untuk `AI/ML Engineer`: Ambil kursus/sertifikasi 'Data Engineering, Big Data and ML on Google Cloud 日本語版' [Google Cloud, Intermediate] (Relevansi: 0.34, Est. boost: +1.02)

---

## 3. Budi Santoso — Track: `Web` (Bagus (IPK ~3.82))

### 📜 Daftar 4 Sertifikasi Industri yang Dimiliki:
1. **AWS Certified Developer - Associate** — *Amazon Web Services (AWS)* (Tier A (1.0))
2. **Meta Front-End Developer** — *Meta (Coursera)* (Tier A (1.0))
3. **Docker Associate Training** — *Docker, Inc.* (Tier A (1.0))
4. **Scrum Fundamentals Certified** — *SCRUMstudy* (Tier A (1.0))

### 📊 Tabel Komparasi Top-5 Rekomendasi Karir (Before vs After):
| Peringkat | Lowongan Pekerjaan | Perusahaan | Skor Before (Matkul) | Skor After (+ Certs) | Lonjakan (Δ) | Status Dampak |
|:---:|---|---|:---:|:---:|:---:|---|
| **#1** | **Junior Frontend Developer** | MagicSet | `0.00` | `8.70` | **`+8.70`** | 🚀 **Lonjakan Masif** |
| **#2** | **Software Engineer** | Harvey Nash | `0.00` | `8.35` | **`+8.35`** | 🚀 **Lonjakan Masif** |
| **#3** | **Software Developer** | Sun Communities & Sun Outdoors | `0.00` | `8.17` | **`+8.17`** | 🚀 **Lonjakan Masif** |
| **#4** | **Software Development Engineer, AWS** | Amazon Web Services (AWS) | `0.00` | `7.91` | **`+7.91`** | 🚀 **Lonjakan Masif** |
| **#5** | **UI Frontend Developer** | Unissant | `1.38` | `5.30` | **`+3.93`** | 🚀 **Lonjakan Masif** |

💡 **Transformasi Karir Juara 1:**
- **Sebelum Sertifikat (Before):** `Web Developer (HTML,CSS) | Remote` (Skor: `4.80`)
- **Setelah Sertifikat (After):** `Junior Frontend Developer` (Skor: `8.70`) ➔ *Kenaikan Total: `+3.89 poin`*

### 🔍 Atribusi Fitur Utama (SHAP Top Features):
- **Sertifikat: AWS Certified Developer - Associate**: Kontribusi `+8.698 poin` terhadap `Junior Frontend Developer`

### 🧭 Bimbingan Karir DiCE 2-Tahap (Multi-Stage 1.139 Kursus Riil):
#### A. DiCE Tahap 1 — Saran Kursus Fondasi Awal (Kondisi *Before* / Matkul Saja):
- Untuk `Web Developer (HTML,CSS) | Remote`: Ambil kursus/sertifikasi 'Meta Front-End Developer' [Meta, Beginner] (Relevansi: 0.37, Est. boost: +0.90)
- Untuk `Web Developer (HTML,CSS) | Remote`: Ambil kursus/sertifikasi 'Meta Back-End Developer' [Meta, Beginner] (Relevansi: 0.34, Est. boost: +0.84)
- Untuk `Web Developer (HTML,CSS) | Remote`: Ambil kursus/sertifikasi 'Introduction to Back-End Development' [Meta, Beginner] (Relevansi: 0.32, Est. boost: +0.79)

#### B. DiCE Tahap 2 — Saran Spesialisasi Lanjutan (Kondisi *After* / Setelah Punya Sertifikat):
- Untuk `Junior Frontend Developer`: Ambil kursus/sertifikasi 'Getting Started with Git and GitHub' [IBM, Beginner] (Relevansi: 0.17, Est. boost: +0.41)
- Untuk `Junior Frontend Developer`: Ambil kursus/sertifikasi 'Google IT Support' [Google, Beginner] (Relevansi: 0.16, Est. boost: +0.38)
- Untuk `Junior Frontend Developer`: Ambil kursus/sertifikasi 'Technical Support Fundamentals' [Google, Beginner] (Relevansi: 0.14, Est. boost: +0.35)

---

## 4. Bayu Setiawan — Track: `Web` (Jelek (IPK ~2.03))

### 📜 Daftar 4 Sertifikasi Industri yang Dimiliki:
1. **AWS Certified Developer - Associate** — *Amazon Web Services (AWS)* (Tier A (1.0))
2. **Meta Front-End Developer** — *Meta (Coursera)* (Tier A (1.0))
3. **Docker Associate Training** — *Docker, Inc.* (Tier A (1.0))
4. **Scrum Fundamentals Certified** — *SCRUMstudy* (Tier A (1.0))

### 📊 Tabel Komparasi Top-5 Rekomendasi Karir (Before vs After):
| Peringkat | Lowongan Pekerjaan | Perusahaan | Skor Before (Matkul) | Skor After (+ Certs) | Lonjakan (Δ) | Status Dampak |
|:---:|---|---|:---:|:---:|:---:|---|
| **#1** | **UI Frontend Developer** | Unissant | `0.81` | `7.19` | **`+6.38`** | 🚀 **Lonjakan Masif** |
| **#2** | **Front End Developer** | Vanda Pharmaceuticals | `0.00` | `6.99` | **`+6.99`** | 🚀 **Lonjakan Masif** |
| **#3** | **Frontend Developer** | InterEx Group | `0.00` | `6.47` | **`+6.47`** | 🚀 **Lonjakan Masif** |
| **#4** | **Front-End Web Developer (Webflow)** | MDAEdge | `0.00` | `6.11` | **`+6.11`** | 🚀 **Lonjakan Masif** |
| **#5** | **Junior Frontend Developer** | MagicSet | `0.00` | `5.04` | **`+5.04`** | 🚀 **Lonjakan Masif** |

💡 **Transformasi Karir Juara 1:**
- **Sebelum Sertifikat (Before):** `ES Application Developer II` (Skor: `3.56`)
- **Setelah Sertifikat (After):** `UI Frontend Developer` (Skor: `7.19`) ➔ *Kenaikan Total: `+3.62 poin`*

### 🔍 Atribusi Fitur Utama (SHAP Top Features):
- **Sertifikat: Meta Front-End Developer**: Kontribusi `+6.376 poin` terhadap `UI Frontend Developer`
- **MK: Pengembangan Aplikasi Website**: Kontribusi `+0.810 poin` terhadap `UI Frontend Developer`

### 🧭 Bimbingan Karir DiCE 2-Tahap (Multi-Stage 1.139 Kursus Riil):
#### A. DiCE Tahap 1 — Saran Kursus Fondasi Awal (Kondisi *Before* / Matkul Saja):
- Untuk `ES Application Developer II`: Ambil kursus/sertifikasi 'Foundations of User Experience (UX) Design' [Google, Beginner] (Relevansi: 0.19, Est. boost: +0.48)
- Untuk `ES Application Developer II`: Ambil kursus/sertifikasi 'System Administration and IT Infrastructure Services' [Google, Beginner] (Relevansi: 0.19, Est. boost: +0.46)
- Untuk `ES Application Developer II`: Ambil kursus/sertifikasi 'Cybersecurity Roles, Processes & Operating System Security' [IBM, Beginner] (Relevansi: 0.18, Est. boost: +0.45)

#### B. DiCE Tahap 2 — Saran Spesialisasi Lanjutan (Kondisi *After* / Setelah Punya Sertifikat):
- Untuk `UI Frontend Developer`: Ambil kursus/sertifikasi 'Meta React Native' [Meta, Beginner] (Relevansi: 0.29, Est. boost: +0.72)
- Untuk `UI Frontend Developer`: Ambil kursus/sertifikasi 'Programming with JavaScript' [Meta, Beginner] (Relevansi: 0.28, Est. boost: +0.69)
- Untuk `UI Frontend Developer`: Ambil kursus/sertifikasi 'Introduction to Web Development with HTML, CSS, JavaScript' [IBM, Beginner] (Relevansi: 0.26, Est. boost: +0.64)

---

## 5. Andi Wijaya — Track: `Net` (Bagus (IPK ~3.82))

### 📜 Daftar 4 Sertifikasi Industri yang Dimiliki:
1. **CCNA** — *Cisco Networking Academy* (Tier A (1.0))
2. **AWS Cloud Practitioner** — *Amazon Web Services (AWS) Training and Certification* (Tier A (1.0))
3. **Cisco CyberOps Associate** — *Cisco Networking Academy* (Tier A (1.0))
4. **Security+** — *CompTIA* (Tier A (1.0))

### 📊 Tabel Komparasi Top-5 Rekomendasi Karir (Before vs After):
| Peringkat | Lowongan Pekerjaan | Perusahaan | Skor Before (Matkul) | Skor After (+ Certs) | Lonjakan (Δ) | Status Dampak |
|:---:|---|---|:---:|:---:|:---:|---|
| **#1** | **AI/ML Engineer** | Centraprise | `0.00` | `8.09` | **`+8.09`** | 🚀 **Lonjakan Masif** |
| **#2** | **WarmPool - AI Practice** | Citius IT Solutions Pvt. Ltd | `0.00` | `7.44` | **`+7.44`** | 🚀 **Lonjakan Masif** |
| **#3** | **Junior Frontend Developer** | MagicSet | `0.00` | `6.81` | **`+6.81`** | 🚀 **Lonjakan Masif** |
| **#4** | **Machine Learning Engineer** | KTek Resourcing | `-0.97` | `5.95` | **`+6.91`** | 🚀 **Lonjakan Masif** |
| **#5** | **Web Developer (HTML,CSS) | Remote** | Crossing Hurdles | `4.66` | `4.66` | **`+0.00`** | 📌 **Stabil (Dominan Matkul)** |

💡 **Transformasi Karir Juara 1:**
- **Sebelum Sertifikat (Before):** `Web Developer (HTML,CSS) | Remote` (Skor: `4.66`)
- **Setelah Sertifikat (After):** `AI/ML Engineer` (Skor: `8.09`) ➔ *Kenaikan Total: `+3.43 poin`*

### 🔍 Atribusi Fitur Utama (SHAP Top Features):
- **Sertifikat: AWS Cloud Practitioner**: Kontribusi `+8.089 poin` terhadap `AI/ML Engineer`

### 🧭 Bimbingan Karir DiCE 2-Tahap (Multi-Stage 1.139 Kursus Riil):
#### A. DiCE Tahap 1 — Saran Kursus Fondasi Awal (Kondisi *Before* / Matkul Saja):
- Untuk `Web Developer (HTML,CSS) | Remote`: Ambil kursus/sertifikasi 'Meta Front-End Developer' [Meta, Beginner] (Relevansi: 0.37, Est. boost: +0.90)
- Untuk `Web Developer (HTML,CSS) | Remote`: Ambil kursus/sertifikasi 'Meta Back-End Developer' [Meta, Beginner] (Relevansi: 0.34, Est. boost: +0.84)
- Untuk `Web Developer (HTML,CSS) | Remote`: Ambil kursus/sertifikasi 'Introduction to Back-End Development' [Meta, Beginner] (Relevansi: 0.32, Est. boost: +0.79)

#### B. DiCE Tahap 2 — Saran Spesialisasi Lanjutan (Kondisi *After* / Setelah Punya Sertifikat):
- Untuk `AI/ML Engineer`: Ambil kursus/sertifikasi 'Digital Transformation Using AI/ML with Google Cloud' [Google Cloud, Beginner] (Relevansi: 0.34, Est. boost: +0.83)
- Untuk `AI/ML Engineer`: Ambil kursus/sertifikasi 'Python for Data Science, AI & Development' [IBM, Beginner] (Relevansi: 0.28, Est. boost: +0.69)
- Untuk `AI/ML Engineer`: Ambil kursus/sertifikasi 'Data Engineering, Big Data and ML on Google Cloud 日本語版' [Google Cloud, Intermediate] (Relevansi: 0.34, Est. boost: +1.02)

---

## 6. Kevin Aditya — Track: `Net` (Jelek (IPK ~2.03))

### 📜 Daftar 4 Sertifikasi Industri yang Dimiliki:
1. **CCNA** — *Cisco Networking Academy* (Tier A (1.0))
2. **AWS Cloud Practitioner** — *Amazon Web Services (AWS) Training and Certification* (Tier A (1.0))
3. **Cisco CyberOps Associate** — *Cisco Networking Academy* (Tier A (1.0))
4. **Security+** — *CompTIA* (Tier A (1.0))

### 📊 Tabel Komparasi Top-5 Rekomendasi Karir (Before vs After):
| Peringkat | Lowongan Pekerjaan | Perusahaan | Skor Before (Matkul) | Skor After (+ Certs) | Lonjakan (Δ) | Status Dampak |
|:---:|---|---|:---:|:---:|:---:|---|
| **#1** | **AI/ML Engineer** | Centraprise | `0.00` | `6.31` | **`+6.31`** | 🚀 **Lonjakan Masif** |
| **#2** | **WarmPool - AI Practice** | Citius IT Solutions Pvt. Ltd | `0.00` | `5.81` | **`+5.81`** | 🚀 **Lonjakan Masif** |
| **#3** | **Junior Frontend Developer** | MagicSet | `0.00` | `5.32` | **`+5.32`** | 🚀 **Lonjakan Masif** |
| **#4** | **Machine Learning Engineer** | KTek Resourcing | `-1.02` | `4.37` | **`+5.39`** | 🚀 **Lonjakan Masif** |
| **#5** | **ES Application Developer II** | University of Houston | `3.15` | `3.15` | **`+0.00`** | 📌 **Stabil (Dominan Matkul)** |

💡 **Transformasi Karir Juara 1:**
- **Sebelum Sertifikat (Before):** `ES Application Developer II` (Skor: `3.15`)
- **Setelah Sertifikat (After):** `AI/ML Engineer` (Skor: `6.31`) ➔ *Kenaikan Total: `+3.16 poin`*

### 🔍 Atribusi Fitur Utama (SHAP Top Features):
- **Sertifikat: AWS Cloud Practitioner**: Kontribusi `+6.310 poin` terhadap `AI/ML Engineer`

### 🧭 Bimbingan Karir DiCE 2-Tahap (Multi-Stage 1.139 Kursus Riil):
#### A. DiCE Tahap 1 — Saran Kursus Fondasi Awal (Kondisi *Before* / Matkul Saja):
- Untuk `ES Application Developer II`: Ambil kursus/sertifikasi 'Foundations of User Experience (UX) Design' [Google, Beginner] (Relevansi: 0.19, Est. boost: +0.48)
- Untuk `ES Application Developer II`: Ambil kursus/sertifikasi 'System Administration and IT Infrastructure Services' [Google, Beginner] (Relevansi: 0.19, Est. boost: +0.46)
- Untuk `ES Application Developer II`: Ambil kursus/sertifikasi 'Cybersecurity Roles, Processes & Operating System Security' [IBM, Beginner] (Relevansi: 0.18, Est. boost: +0.45)

#### B. DiCE Tahap 2 — Saran Spesialisasi Lanjutan (Kondisi *After* / Setelah Punya Sertifikat):
- Untuk `AI/ML Engineer`: Ambil kursus/sertifikasi 'Digital Transformation Using AI/ML with Google Cloud' [Google Cloud, Beginner] (Relevansi: 0.34, Est. boost: +0.83)
- Untuk `AI/ML Engineer`: Ambil kursus/sertifikasi 'Python for Data Science, AI & Development' [IBM, Beginner] (Relevansi: 0.28, Est. boost: +0.69)
- Untuk `AI/ML Engineer`: Ambil kursus/sertifikasi 'Data Engineering, Big Data and ML on Google Cloud 日本語版' [Google Cloud, Intermediate] (Relevansi: 0.34, Est. boost: +1.02)

---

## 7. Nadia Putri — Track: `SI` (Bagus (IPK ~3.82))

### 📜 Daftar 4 Sertifikasi Industri yang Dimiliki:
1. **ITIL Foundation** — *AXELOS / PeopleCert* (Tier A (1.0))
2. **Business Analysis Foundation** — *International Institute of Business Analysis (IIBA)* (Tier A (1.0))
3. **Scrum Fundamentals Certified** — *SCRUMstudy* (Tier A (1.0))
4. **Project Management Professional (PMP)** — *PMI* (Tier A (1.0))

### 📊 Tabel Komparasi Top-5 Rekomendasi Karir (Before vs After):
| Peringkat | Lowongan Pekerjaan | Perusahaan | Skor Before (Matkul) | Skor After (+ Certs) | Lonjakan (Δ) | Status Dampak |
|:---:|---|---|:---:|:---:|:---:|---|
| **#1** | **Web Developer (HTML,CSS) | Remote** | Crossing Hurdles | `4.80` | `4.80` | **`+0.00`** | 📌 **Stabil (Dominan Matkul)** |
| **#2** | **ES Application Developer II** | University of Houston | `4.66` | `4.66` | **`+0.00`** | 📌 **Stabil (Dominan Matkul)** |
| **#3** | **Machine Learning (ML) Engineer** | Vectara | `3.63` | `3.63` | **`+0.00`** | 📌 **Stabil (Dominan Matkul)** |
| **#4** | **Web Apps Developer** | Halvik | `2.98` | `2.98` | **`+0.00`** | 📌 **Stabil (Dominan Matkul)** |
| **#5** | **UX Designer** | MDAEdge | `2.87` | `2.87` | **`+0.00`** | 📌 **Stabil (Dominan Matkul)** |

💡 **Transformasi Karir Juara 1:**
- **Sebelum Sertifikat (Before):** `Web Developer (HTML,CSS) | Remote` (Skor: `4.80`)
- **Setelah Sertifikat (After):** `Web Developer (HTML,CSS) | Remote` (Skor: `4.80`) ➔ *Kenaikan Total: `+0.00 poin`*

### 🔍 Atribusi Fitur Utama (SHAP Top Features):
- **MK: Pengembangan Aplikasi Website**: Kontribusi `+4.804 poin` terhadap `Web Developer (HTML,CSS) | Remote`

### 🧭 Bimbingan Karir DiCE 2-Tahap (Multi-Stage 1.139 Kursus Riil):
#### A. DiCE Tahap 1 — Saran Kursus Fondasi Awal (Kondisi *Before* / Matkul Saja):
- Untuk `Web Developer (HTML,CSS) | Remote`: Ambil kursus/sertifikasi 'Meta Front-End Developer' [Meta, Beginner] (Relevansi: 0.37, Est. boost: +0.90)
- Untuk `Web Developer (HTML,CSS) | Remote`: Ambil kursus/sertifikasi 'Meta Back-End Developer' [Meta, Beginner] (Relevansi: 0.34, Est. boost: +0.84)
- Untuk `Web Developer (HTML,CSS) | Remote`: Ambil kursus/sertifikasi 'Introduction to Back-End Development' [Meta, Beginner] (Relevansi: 0.32, Est. boost: +0.79)

#### B. DiCE Tahap 2 — Saran Spesialisasi Lanjutan (Kondisi *After* / Setelah Punya Sertifikat):
- Untuk `Web Developer (HTML,CSS) | Remote`: Ambil kursus/sertifikasi 'Meta Front-End Developer' [Meta, Beginner] (Relevansi: 0.37, Est. boost: +0.90)
- Untuk `Web Developer (HTML,CSS) | Remote`: Ambil kursus/sertifikasi 'Meta Back-End Developer' [Meta, Beginner] (Relevansi: 0.34, Est. boost: +0.84)
- Untuk `Web Developer (HTML,CSS) | Remote`: Ambil kursus/sertifikasi 'Introduction to Back-End Development' [Meta, Beginner] (Relevansi: 0.32, Est. boost: +0.79)

---

## 8. Farhan Hidayat — Track: `SI` (Jelek (IPK ~2.03))

### 📜 Daftar 4 Sertifikasi Industri yang Dimiliki:
1. **ITIL Foundation** — *AXELOS / PeopleCert* (Tier A (1.0))
2. **Business Analysis Foundation** — *International Institute of Business Analysis (IIBA)* (Tier A (1.0))
3. **Scrum Fundamentals Certified** — *SCRUMstudy* (Tier A (1.0))
4. **Project Management Professional (PMP)** — *PMI* (Tier A (1.0))

### 📊 Tabel Komparasi Top-5 Rekomendasi Karir (Before vs After):
| Peringkat | Lowongan Pekerjaan | Perusahaan | Skor Before (Matkul) | Skor After (+ Certs) | Lonjakan (Δ) | Status Dampak |
|:---:|---|---|:---:|:---:|:---:|---|
| **#1** | **ES Application Developer II** | University of Houston | `3.15` | `3.15` | **`+0.00`** | 📌 **Stabil (Dominan Matkul)** |
| **#2** | **Machine Learning (ML) Engineer** | Vectara | `2.35` | `2.35` | **`+0.00`** | 📌 **Stabil (Dominan Matkul)** |
| **#3** | **AI/ML Engineer** | Centraprise | `0.00` | `2.18` | **`+2.18`** | 🚀 **Lonjakan Masif** |
| **#4** | **Machine Learning Engineer** | KTek Resourcing | `0.21` | `2.10` | **`+1.88`** | 🚀 **Lonjakan Masif** |
| **#5** | **Junior Frontend Developer** | MagicSet | `0.00` | `1.99` | **`+1.99`** | 🚀 **Lonjakan Masif** |

💡 **Transformasi Karir Juara 1:**
- **Sebelum Sertifikat (Before):** `ES Application Developer II` (Skor: `3.15`)
- **Setelah Sertifikat (After):** `ES Application Developer II` (Skor: `3.15`) ➔ *Kenaikan Total: `+0.00 poin`*

### 🔍 Atribusi Fitur Utama (SHAP Top Features):
- **MK: Integrasi Aplikasi Enterprise**: Kontribusi `+3.152 poin` terhadap `ES Application Developer II`

### 🧭 Bimbingan Karir DiCE 2-Tahap (Multi-Stage 1.139 Kursus Riil):
#### A. DiCE Tahap 1 — Saran Kursus Fondasi Awal (Kondisi *Before* / Matkul Saja):
- Untuk `ES Application Developer II`: Ambil kursus/sertifikasi 'Foundations of User Experience (UX) Design' [Google, Beginner] (Relevansi: 0.19, Est. boost: +0.48)
- Untuk `ES Application Developer II`: Ambil kursus/sertifikasi 'System Administration and IT Infrastructure Services' [Google, Beginner] (Relevansi: 0.19, Est. boost: +0.46)
- Untuk `ES Application Developer II`: Ambil kursus/sertifikasi 'Cybersecurity Roles, Processes & Operating System Security' [IBM, Beginner] (Relevansi: 0.18, Est. boost: +0.45)

#### B. DiCE Tahap 2 — Saran Spesialisasi Lanjutan (Kondisi *After* / Setelah Punya Sertifikat):
- Untuk `ES Application Developer II`: Ambil kursus/sertifikasi 'Foundations of User Experience (UX) Design' [Google, Beginner] (Relevansi: 0.19, Est. boost: +0.48)
- Untuk `ES Application Developer II`: Ambil kursus/sertifikasi 'System Administration and IT Infrastructure Services' [Google, Beginner] (Relevansi: 0.19, Est. boost: +0.46)
- Untuk `ES Application Developer II`: Ambil kursus/sertifikasi 'Cybersecurity Roles, Processes & Operating System Security' [IBM, Beginner] (Relevansi: 0.18, Est. boost: +0.45)

---

## 9. Dewi Lestari — Track: `SAP` (Bagus (IPK ~3.82))

### 📜 Daftar 6 Sertifikasi Industri yang Dimiliki:
1. **SAP Fundamentals** — *SAP Learning Hub* (Tier A (1.0))
2. **SAP Certified Application Associate** — *SAP* (Tier A (1.0))
3. **ITIL Foundation** — *AXELOS / PeopleCert* (Tier A (1.0))
4. **SAP Analytics Cloud** — *SAP* (Tier A (1.0))
5. **ITIL Foundation** — *AXELOS / PeopleCert* (Tier A (1.0))
6. **Business Analysis Foundation** — *International Institute of Business Analysis (IIBA)* (Tier A (1.0))

### 📊 Tabel Komparasi Top-5 Rekomendasi Karir (Before vs After):
| Peringkat | Lowongan Pekerjaan | Perusahaan | Skor Before (Matkul) | Skor After (+ Certs) | Lonjakan (Δ) | Status Dampak |
|:---:|---|---|:---:|:---:|:---:|---|
| **#1** | **Web Developer (HTML,CSS) | Remote** | Crossing Hurdles | `4.80` | `4.80` | **`+0.00`** | 📌 **Stabil (Dominan Matkul)** |
| **#2** | **ES Application Developer II** | University of Houston | `4.66` | `4.66` | **`+0.00`** | 📌 **Stabil (Dominan Matkul)** |
| **#3** | **Machine Learning (ML) Engineer** | Vectara | `3.63` | `3.63` | **`+0.00`** | 📌 **Stabil (Dominan Matkul)** |
| **#4** | **Web Apps Developer** | Halvik | `2.98` | `2.98` | **`+0.00`** | 📌 **Stabil (Dominan Matkul)** |
| **#5** | **UX Designer** | MDAEdge | `2.87` | `2.87` | **`+0.00`** | 📌 **Stabil (Dominan Matkul)** |

💡 **Transformasi Karir Juara 1:**
- **Sebelum Sertifikat (Before):** `Web Developer (HTML,CSS) | Remote` (Skor: `4.80`)
- **Setelah Sertifikat (After):** `Web Developer (HTML,CSS) | Remote` (Skor: `4.80`) ➔ *Kenaikan Total: `+0.00 poin`*

### 🔍 Atribusi Fitur Utama (SHAP Top Features):
- **MK: Pengembangan Aplikasi Website**: Kontribusi `+4.804 poin` terhadap `Web Developer (HTML,CSS) | Remote`

### 🧭 Bimbingan Karir DiCE 2-Tahap (Multi-Stage 1.139 Kursus Riil):
#### A. DiCE Tahap 1 — Saran Kursus Fondasi Awal (Kondisi *Before* / Matkul Saja):
- Untuk `Web Developer (HTML,CSS) | Remote`: Ambil kursus/sertifikasi 'Meta Front-End Developer' [Meta, Beginner] (Relevansi: 0.37, Est. boost: +0.90)
- Untuk `Web Developer (HTML,CSS) | Remote`: Ambil kursus/sertifikasi 'Meta Back-End Developer' [Meta, Beginner] (Relevansi: 0.34, Est. boost: +0.84)
- Untuk `Web Developer (HTML,CSS) | Remote`: Ambil kursus/sertifikasi 'Introduction to Back-End Development' [Meta, Beginner] (Relevansi: 0.32, Est. boost: +0.79)

#### B. DiCE Tahap 2 — Saran Spesialisasi Lanjutan (Kondisi *After* / Setelah Punya Sertifikat):
- Untuk `Web Developer (HTML,CSS) | Remote`: Ambil kursus/sertifikasi 'Meta Front-End Developer' [Meta, Beginner] (Relevansi: 0.37, Est. boost: +0.90)
- Untuk `Web Developer (HTML,CSS) | Remote`: Ambil kursus/sertifikasi 'Meta Back-End Developer' [Meta, Beginner] (Relevansi: 0.34, Est. boost: +0.84)
- Untuk `Web Developer (HTML,CSS) | Remote`: Ambil kursus/sertifikasi 'Introduction to Back-End Development' [Meta, Beginner] (Relevansi: 0.32, Est. boost: +0.79)

---

## 10. Ilham Saputra — Track: `SAP` (Jelek (IPK ~2.03))

### 📜 Daftar 6 Sertifikasi Industri yang Dimiliki:
1. **SAP Fundamentals** — *SAP Learning Hub* (Tier A (1.0))
2. **SAP Certified Application Associate** — *SAP* (Tier A (1.0))
3. **ITIL Foundation** — *AXELOS / PeopleCert* (Tier A (1.0))
4. **SAP Analytics Cloud** — *SAP* (Tier A (1.0))
5. **ITIL Foundation** — *AXELOS / PeopleCert* (Tier A (1.0))
6. **Business Analysis Foundation** — *International Institute of Business Analysis (IIBA)* (Tier A (1.0))

### 📊 Tabel Komparasi Top-5 Rekomendasi Karir (Before vs After):
| Peringkat | Lowongan Pekerjaan | Perusahaan | Skor Before (Matkul) | Skor After (+ Certs) | Lonjakan (Δ) | Status Dampak |
|:---:|---|---|:---:|:---:|:---:|---|
| **#1** | **ES Application Developer II** | University of Houston | `3.29` | `3.29` | **`+0.00`** | 📌 **Stabil (Dominan Matkul)** |
| **#2** | **Web Developer (HTML,CSS) | Remote** | Crossing Hurdles | `2.83` | `2.83` | **`+0.00`** | 📌 **Stabil (Dominan Matkul)** |
| **#3** | **Machine Learning (ML) Engineer** | Vectara | `2.56` | `2.56` | **`+0.00`** | 📌 **Stabil (Dominan Matkul)** |
| **#4** | **Research Associate** | University of Southern California | `0.00` | `2.32` | **`+2.32`** | 🚀 **Lonjakan Masif** |
| **#5** | **Junior Frontend Developer** | MagicSet | `0.00` | `1.92` | **`+1.92`** | 🚀 **Lonjakan Masif** |

💡 **Transformasi Karir Juara 1:**
- **Sebelum Sertifikat (Before):** `ES Application Developer II` (Skor: `3.29`)
- **Setelah Sertifikat (After):** `ES Application Developer II` (Skor: `3.29`) ➔ *Kenaikan Total: `+0.00 poin`*

### 🔍 Atribusi Fitur Utama (SHAP Top Features):
- **MK: Integrasi Aplikasi Enterprise**: Kontribusi `+3.289 poin` terhadap `ES Application Developer II`

### 🧭 Bimbingan Karir DiCE 2-Tahap (Multi-Stage 1.139 Kursus Riil):
#### A. DiCE Tahap 1 — Saran Kursus Fondasi Awal (Kondisi *Before* / Matkul Saja):
- Untuk `ES Application Developer II`: BC -> B
- Untuk `ES Application Developer II`: Ambil kursus/sertifikasi 'Foundations of User Experience (UX) Design' [Google, Beginner] (Relevansi: 0.19, Est. boost: +0.48)
- Untuk `ES Application Developer II`: Ambil kursus/sertifikasi 'System Administration and IT Infrastructure Services' [Google, Beginner] (Relevansi: 0.19, Est. boost: +0.46)

#### B. DiCE Tahap 2 — Saran Spesialisasi Lanjutan (Kondisi *After* / Setelah Punya Sertifikat):
- Untuk `ES Application Developer II`: BC -> B
- Untuk `ES Application Developer II`: Ambil kursus/sertifikasi 'Foundations of User Experience (UX) Design' [Google, Beginner] (Relevansi: 0.19, Est. boost: +0.48)
- Untuk `ES Application Developer II`: Ambil kursus/sertifikasi 'System Administration and IT Infrastructure Services' [Google, Beginner] (Relevansi: 0.19, Est. boost: +0.46)

---
