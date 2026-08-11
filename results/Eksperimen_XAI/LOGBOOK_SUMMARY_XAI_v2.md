# Eksperimen XAI Sesi 2 - Aligned dengan Paper Referensi
*Tanggal: 2026-08-11 14:28*

## Referensi Paper
| Kode | Paper | Relevansi |
|------|-------|-----------|
| P1 | El-Deeb et al. (2026) - XAIforJobs, Procedia CS | SHAP + LIME untuk job recommendation |
| P2 | Tang et al. (2025) - Systematic Review, Frontiers AI | Counterfactual sebagai XAI frontier |
| P3 | Zhang et al. (2025) - Literature Review, Cogent Business | LIME, SHAP dalam rekrutmen |

---

## EKS04 — SHAP vs LIME: Apakah Keduanya Setuju?
*(Aligned dengan P1: XAIforJobs yang menggunakan SHAP + LIME bersamaan)*

**Pertanyaan:** Apakah SHAP dan LIME mengidentifikasi fitur penting yang sama?

| Metrik | Nilai |
|--------|-------|
| Total prediksi dianalisis | 30 |
| Top-1 feature SHAP == LIME | 30/30 (100.0%) |
| Rata-rata top-3 feature overlap | 41.1% |

**Interpretasi:**
- SHAP dan LIME **setuju tinggi** (100.0%) dalam mengidentifikasi fitur terpenting.
- Konsistensi ini mendukung validitas sistem XAI (dua metode berbeda → kesimpulan sama).
- Sejalan dengan P1 (XAIforJobs): kedua metode saling melengkapi, bukan saling bertentangan.

---

## EKS05 — Novelty DiCE: Kontribusi di Luar SHAP & LIME
*(Aligned dengan P2: Counterfactual sebagai frontier XAI yang belum banyak diimplementasi)*

**Klaim:** DiCE memberikan jenis penjelasan yang tidak bisa diberikan SHAP maupun LIME.

| Aspek | SHAP | LIME | DiCE |
|-------|------|------|------|
| Tipe penjelasan | Retrospektif | Retrospektif | **Prospektif** |
| Menjawab 'mengapa skor ini?' | ✅ | ✅ | ❌ |
| Menjawab 'apa yang harus dilakukan?' | ❌ | ❌ | **✅** |
| Memberikan skor kuantitatif setelah intervensi | ❌ | ❌ | **✅** |
| Membuka akses ke pekerjaan baru (beyond top-K) | ❌ | ❌ | **✅** |

**Andi_Wijaya (Kuat (ada sertifikat)):**
- SHAP: *"Sertifikat: AWS Certified Developer - Associate"* adalah kontributor tertinggi
- LIME: *"MK: Algoritma dan Pemrograman"* sebagai penjelasan lokal
- DiCE: Membuka **5 pekerjaan baru** yang bisa dicapai dengan intervensi konkret

**Fajar_Nugroho (Lemah (tanpa sertifikat)):**
- SHAP: *"Sertifikat: Databricks Fundamentals"* adalah kontributor tertinggi
- LIME: *"MK: Algoritma dan Pemrograman"* sebagai penjelasan lokal
- DiCE: Membuka **5 pekerjaan baru** yang bisa dicapai dengan intervensi konkret

**Kesimpulan Novelty:**
Sistem ini mengintegrasikan tiga lapisan XAI yang saling melengkapi:
1. **SHAP** — Menjawab 'mengapa?' (global, teoritis, game theory foundation)
2. **LIME** — Menjawab 'mengapa?' secara lokal (per prediksi, lebih cepat)
3. **DiCE** — Menjawab 'bagaimana meningkatkan diri?' (prospektif, action-oriented)

Kombinasi ketiga ini adalah **kontribusi novel** proyek ini,
melampaui paper P1 (hanya SHAP+LIME) dan paper P2 (tidak ada implementasi DiCE).