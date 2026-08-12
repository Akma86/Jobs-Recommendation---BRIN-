# Eksperimen XAI Sesi 3 - Sparsity & Robustness
*Tanggal: 2026-08-12 13:48*

## EKS06 — DiCE Sparsity & Feasibility
**Tujuan:** Mengukur apakah saran dari DiCE masuk akal (sparse/sedikit intervensi).

- **Rata-rata intervensi per pekerjaan (Sparsity):** 1.00 langkah
- **Rata-rata effort:** 5.00

**Kesimpulan:** Counterfactual yang dihasilkan sangat *actionable* karena mahasiswa rata-rata hanya perlu melakukan 1-2 langkah (misal: tambah 1 sertifikat atau perbaiki 1 nilai) untuk mencapai target.

## EKS07 — SHAP Robustness
**Tujuan:** Mengukur kestabilan penjelasan SHAP jika ada sedikit *noise* (perubahan nilai pada 3 mata kuliah).

- **Top-3 Feature Overlap setelah noise:** 46.7%

**Kesimpulan:** Penjelasan SHAP cukup sensitif terhadap perubahan, menunjukkan bahwa perubahan kecil pada nilai sangat mempengaruhi rekomendasi global.