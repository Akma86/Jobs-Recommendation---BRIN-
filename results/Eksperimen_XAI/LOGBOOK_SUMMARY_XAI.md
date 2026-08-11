# Ringkasan Eksperimen XAI - Logbook KP BRIN
*Tanggal: 2026-08-11 13:45*

---

## EKS01 — SHAP: Kontribusi Fitur Per Mahasiswa

| Mahasiswa | Feature Tertinggi | Avg SHAP |
|-----------|-------------------|---------|
| Andi_Wijaya | Sertifikat: AWS Certified Developer - Associate | 5.9921 |
| Rizky_Pratama | Sertifikat: AWS Cloud Practitioner | 7.4479 |
| Nadia_Putri | MK: Pengembangan Aplikasi Website | 2.9097 |

**Interpretasi:** MK bernilai tinggi pada domain relevan memberikan kontribusi SHAP terbesar.

---

## EKS02 — DiCE: Validasi Kualitas Counterfactual

| Metrik | Nilai |
|--------|-------|
| Total pekerjaan | 5 |
| CF diverse (Jaccard < 0.4) | 5/5 |
| Rata-rata Jaccard Similarity | 0.0 |
| CF mencapai target | 5/5 |

**Interpretasi:** Jaccard < 0.4 = CF benar-benar berbeda strategi → mahasiswa mendapat pilihan nyata.

---

## EKS03 — SHAP vs DiCE: Actionability

| Mahasiswa | Profil | SHAP Top Feature | DiCE Top Intervensi | Actionable Jobs |
|-----------|--------|------------------|---------------------|-----------------|
| Andi_Wijaya | Kuat (ada sertifikat) | Sertifikat: AWS Certified Developer | Sertifikat: AWS Certified Solutions | 5 |
| Fajar_Nugroho | Lemah (tanpa sertifikat) | Sertifikat: Databricks Fundamentals | Sertifikat: AWS Certified Solutions | 5 |

**Interpretasi:**
- **SHAP** = retrospektif, menjelaskan *mengapa* skor saat ini ada.
- **DiCE** = prospektif, memberikan *langkah konkret* untuk meningkatkan peluang.
- Keduanya komplementer dan sebaiknya disajikan bersamaan kepada mahasiswa.

---

## Kesimpulan
Sistem XAI SHAP + DiCE terbukti berjalan dengan baik pada 10 mahasiswa dummy.
Upgrade DiCE (effort cost + Jaccard diversity) menghasilkan counterfactual yang lebih realistis dan beragam.