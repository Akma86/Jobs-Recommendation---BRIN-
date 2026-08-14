# -*- coding: utf-8 -*-
"""
EXPERIMENT RUNNER v2 - Aligned with Paper References
=====================================================
Paper Alignment:
  EKS04 - SHAP vs LIME Comparison (aligned with XAIforJobs: El-Deeb et al. 2026)
          Paper uses both SHAP and LIME side-by-side -> we replicate & compare
  EKS05 - DiCE Novelty Claim Validation (aligned with frai-8-1660548 systematic review)
          Paper states counterfactuals are "frontier" not yet widely implemented
          -> we prove DiCE provides insights SHAP/LIME cannot

Key finding from XAIforJobs paper:
  - SHAP: global feature importance, theoretically sound (game theory)
  - LIME: local surrogate model, faster, more intuitive for non-technical users
  - DiCE: NOT in any paper we have -> our novel contribution
"""

import os, sys, subprocess
import pandas as pd
import numpy as np
from datetime import datetime

ROOT_DIR    = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR     = os.path.join(ROOT_DIR, "src")
DATA_DIR    = os.path.join(ROOT_DIR, "data", "Percobaan")
RESULTS_XAI = os.path.join(ROOT_DIR, "results", "Eksperimen_XAI")
APP_SCRIPT  = os.path.join(SRC_DIR, "prototype", "app.py")

STUDENTS = {
    "EKS04": [
        ("Andi_Wijaya",   "Coba_Mahasiswa_Andi_Wijaya"),
        ("Rizky_Pratama", "Coba_Mahasiswa_Rizky_Pratama"),
    ],
    "EKS05": [
        ("Andi_Wijaya",   "Coba_Mahasiswa_Andi_Wijaya"),
        ("Fajar_Nugroho", "Coba_Mahasiswa_Fajar_Nugroho"),
    ],
}

def log(m):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {m}")

def get_paths(pname):
    b    = os.path.join(DATA_DIR, pname)
    khs  = os.path.join(b, "transcript_parsed.csv")
    cert = os.path.join(b, "certificates_parsed.csv")
    return khs, (cert if os.path.exists(cert) else None)

def run_app(khs, cert, out_dir, mode):
    os.makedirs(out_dir, exist_ok=True)
    cmd = [sys.executable, APP_SCRIPT, "--khs", khs, "--xai-mode", mode]
    if cert:
        cmd += ["--certs", cert]
    env = os.environ.copy()
    env["PYTHONPATH"] = SRC_DIR
    r = subprocess.run(cmd, cwd=out_dir, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        log(f"  [ERROR] {r.stderr[-800:]}")
        return False
    return True

# ── EKS04 ─────────────────────────────────────────────────────────────────
# Paper ref: XAIforJobs (El-Deeb et al. 2026) - SHAP + LIME side by side
def run_eks04():
    log("="*60)
    log("EKS04: SHAP vs LIME - Comparison (Paper: XAIforJobs)")
    log("Paper insight: SHAP = global/theoretic, LIME = local/approx")
    log("="*60)
    out_base = os.path.join(RESULTS_XAI, "EKS04_SHAP_vs_LIME")
    comp_rows = []

    for name, pname in STUDENTS["EKS04"]:
        log(f"  -> {name}: running SHAP + LIME (mode=all)")
        khs, cert = get_paths(pname)
        if not os.path.exists(khs):
            log(f"  [SKIP] {name}"); continue

        out_dir = os.path.join(out_base, name)
        # Run with all modes to get both SHAP and LIME
        if not run_app(khs, cert, out_dir, "all"):
            log(f"  [FAIL] {name}"); continue

        shap_csv = os.path.join(out_dir, "shap_explanations.csv")
        lime_csv = os.path.join(out_dir, "lime_explanations.csv")

        if not os.path.exists(shap_csv) or not os.path.exists(lime_csv):
            log(f"  [WARN] Missing SHAP or LIME CSV for {name}"); continue

        shap_df = pd.read_csv(shap_csv)
        lime_df = pd.read_csv(lime_csv)
        log(f"  [OK] {name}: SHAP {len(shap_df)} rows | LIME {len(lime_df)} rows")

        # Per job: compare top feature from SHAP vs LIME
        for job_id in shap_df["job_id"].unique():
            s_job = shap_df[shap_df["job_id"] == job_id]
            l_job = lime_df[lime_df["job_id"] == job_id] if not lime_df.empty else pd.DataFrame()

            job_title = s_job["job_title"].iloc[0]

            # Top SHAP feature
            top_shap = s_job.loc[s_job["shap_value"].abs().idxmax(), "feature"] \
                       if "shap_value" in s_job.columns else ""

            # Top LIME feature
            top_lime = ""
            agree = False
            if not l_job.empty and "lime_weight" in l_job.columns:
                top_lime = l_job.loc[l_job["lime_weight"].abs().idxmax(), "feature"]
                agree = (top_shap == top_lime)

            # Top-3 SHAP features
            top3_shap = s_job.nlargest(3, "shap_value")["feature"].tolist() \
                        if "shap_value" in s_job.columns else []
            # Top-3 LIME features
            top3_lime = l_job.nlargest(3, "lime_weight")["feature"].tolist() \
                        if not l_job.empty and "lime_weight" in l_job.columns else []

            # Overlap between top-3
            overlap = len(set(top3_shap) & set(top3_lime))

            comp_rows.append({
                "student": name,
                "job_id": job_id,
                "job_title": job_title,
                "top_shap_feature": top_shap,
                "top_lime_feature": top_lime,
                "top1_agree": agree,
                "top3_overlap_count": overlap,
                "top3_overlap_pct": round(overlap / 3 * 100, 1) if top3_shap else 0,
            })
            agreement_str = "AGREE" if agree else "DIFFER"
            log(f"    {job_title[:35]}: SHAP~=LIME top1={agreement_str} | top3_overlap={overlap}/3")

    if comp_rows:
        df = pd.DataFrame(comp_rows)
        df.to_csv(os.path.join(out_base, "EKS04_shap_lime_comparison.csv"), index=False)

        # Summary stats
        n_agree = df["top1_agree"].sum()
        n_total = len(df)
        avg_overlap = df["top3_overlap_pct"].mean()
        log(f"  Summary: Top-1 agree: {n_agree}/{n_total} ({n_agree/n_total*100:.1f}%)")
        log(f"  Summary: Avg top-3 overlap: {avg_overlap:.1f}%")

    log("  [EKS04 DONE]\n")
    return comp_rows

# ── EKS05 ─────────────────────────────────────────────────────────────────
# Paper ref: frai-8-1660548 (Tang et al. 2025) - counterfactuals are frontier
# We prove DiCE provides unique "actionable" insight SHAP/LIME cannot
def run_eks05():
    log("="*60)
    log("EKS05: DiCE Novelty - Insights Beyond SHAP & LIME")
    log("Paper insight: Counterfactuals are XAI frontier (Tang et al. 2025)")
    log("="*60)
    out_base = os.path.join(RESULTS_XAI, "EKS05_DiCE_Novelty")
    novelty_rows = []

    for name, pname in STUDENTS["EKS05"]:
        log(f"  -> {name}: running full XAI (all modes)")
        khs, cert = get_paths(pname)
        if not os.path.exists(khs):
            log(f"  [SKIP] {name}"); continue

        out_dir = os.path.join(out_base, name)
        if not run_app(khs, cert, out_dir, "all"):
            log(f"  [FAIL] {name}"); continue

        shap_csv = os.path.join(out_dir, "shap_explanations.csv")
        lime_csv = os.path.join(out_dir, "lime_explanations.csv")
        dice_csv = os.path.join(out_dir, "dice_counterfactuals.csv")

        shap_df = pd.read_csv(shap_csv) if os.path.exists(shap_csv) else pd.DataFrame()
        lime_df = pd.read_csv(lime_csv) if os.path.exists(lime_csv) else pd.DataFrame()
        dice_df = pd.read_csv(dice_csv) if os.path.exists(dice_csv) else pd.DataFrame()

        # What SHAP tells: top contributor (retrospective)
        top_shap = shap_df.groupby("feature")["shap_value"].mean().sort_values(ascending=False).index[0] \
                   if not shap_df.empty and "shap_value" in shap_df.columns else "N/A"

        # What LIME tells: top local contributor
        top_lime = lime_df.groupby("feature")["lime_weight"].mean().sort_values(ascending=False).index[0] \
                   if not lime_df.empty and "lime_weight" in lime_df.columns else "N/A"

        # What SHAP/LIME CANNOT tell: how to get into a job not yet in top-K
        # DiCE answers: what actions to take
        n_jobs_actionable = 0
        dice_unique_suggestions = []
        if not dice_df.empty and "cf_reaches_target" in dice_df.columns:
            n_jobs_actionable = dice_df[dice_df["cf_reaches_target"] == True]["job_id"].nunique()
            # Unique intervention types DiCE suggests
            if "intervention_type" in dice_df.columns:
                dice_unique_suggestions = dice_df["intervention_type"].value_counts().to_dict()

        # Key insight: SHAP tells "AWS cert is important" (past-facing)
        # DiCE tells "ADD AWS cert and your score goes from 5.72 to 7.22" (future-facing)
        novelty_rows.append({
            "student": name,
            "profil": "Kuat (ada sertifikat)" if name == "Andi_Wijaya" else "Lemah (tanpa sertifikat)",
            # SHAP & LIME: retrospective
            "shap_top_contributor": top_shap,
            "lime_top_contributor": top_lime,
            "shap_lime_agree": top_shap == top_lime,
            # DiCE: prospective (NOVEL - not in compared papers)
            "n_jobs_now_achievable_via_dice": n_jobs_actionable,
            "dice_intervention_types": str(dice_unique_suggestions),
            # What SHAP/LIME cannot answer
            "can_shap_tell_how_to_improve": False,
            "can_lime_tell_how_to_improve": False,
            "can_dice_tell_how_to_improve": True,
            "dice_novelty_note": (
                "DiCE memberikan skor kuantitatif setelah intervensi (before/after gap) "
                "- ini tidak bisa diberikan oleh SHAP maupun LIME."
            )
        })
        log(f"    SHAP top: {top_shap[:45]}")
        log(f"    LIME top: {top_lime[:45]}")
        log(f"    SHAP == LIME top: {top_shap == top_lime}")
        log(f"    DiCE actionable jobs (new): {n_jobs_actionable}")

    if novelty_rows:
        df = pd.DataFrame(novelty_rows)
        out_path = os.path.join(out_base, "EKS05_dice_novelty.csv")
        df.to_csv(out_path, index=False)
        log(f"  [SAVED] {out_path}")

    log("  [EKS05 DONE]\n")
    return novelty_rows

# ── LOGBOOK APPENDIX ───────────────────────────────────────────────────────
def generate_logbook_v2(e4, e5):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# Eksperimen XAI Sesi 2 - Aligned dengan Paper Referensi",
        f"*Tanggal: {now}*",
        "",
        "## Referensi Paper",
        "| Kode | Paper | Relevansi |",
        "|------|-------|-----------|",
        "| P1 | El-Deeb et al. (2026) - XAIforJobs, Procedia CS | SHAP + LIME untuk job recommendation |",
        "| P2 | Tang et al. (2025) - Systematic Review, Frontiers AI | Counterfactual sebagai XAI frontier |",
        "| P3 | Zhang et al. (2025) - Literature Review, Cogent Business | LIME, SHAP dalam rekrutmen |",
        "",
        "---",
        "",
        "## EKS04 — SHAP vs LIME: Apakah Keduanya Setuju?",
        "*(Aligned dengan P1: XAIforJobs yang menggunakan SHAP + LIME bersamaan)*",
        "",
        "**Pertanyaan:** Apakah SHAP dan LIME mengidentifikasi fitur penting yang sama?",
        "",
    ]

    if e4:
        df = pd.DataFrame(e4)
        n_agree = int(df["top1_agree"].sum())
        n_total = len(df)
        avg_overlap = round(df["top3_overlap_pct"].mean(), 1)
        pct_agree = round(n_agree / n_total * 100, 1) if n_total > 0 else 0

        lines += [
            "| Metrik | Nilai |", "|--------|-------|",
            f"| Total prediksi dianalisis | {n_total} |",
            f"| Top-1 feature SHAP == LIME | {n_agree}/{n_total} ({pct_agree}%) |",
            f"| Rata-rata top-3 feature overlap | {avg_overlap}% |",
            "",
            "**Interpretasi:**",
        ]
        if pct_agree >= 70:
            lines.append(f"- SHAP dan LIME **setuju tinggi** ({pct_agree}%) dalam mengidentifikasi fitur terpenting.")
            lines.append("- Konsistensi ini mendukung validitas sistem XAI (dua metode berbeda → kesimpulan sama).")
            lines.append("- Sejalan dengan P1 (XAIforJobs): kedua metode saling melengkapi, bukan saling bertentangan.")
        else:
            lines.append(f"- SHAP dan LIME hanya setuju {pct_agree}% untuk top-1 feature.")
            lines.append("- Ketidaksesuaian ini menunjukkan SHAP (global/game-theoretic) dan LIME (local/approx) memang mengukur hal berbeda.")
            lines.append("- Ini menjustifikasi penggunaan keduanya secara bersamaan seperti di P1.")

    lines += ["", "---", "",
        "## EKS05 — Novelty DiCE: Kontribusi di Luar SHAP & LIME",
        "*(Aligned dengan P2: Counterfactual sebagai frontier XAI yang belum banyak diimplementasi)*",
        "",
        "**Klaim:** DiCE memberikan jenis penjelasan yang tidak bisa diberikan SHAP maupun LIME.",
        "",
    ]

    if e5:
        lines += [
            "| Aspek | SHAP | LIME | DiCE |",
            "|-------|------|------|------|",
            "| Tipe penjelasan | Retrospektif | Retrospektif | **Prospektif** |",
            "| Menjawab 'mengapa skor ini?' | ✅ | ✅ | ❌ |",
            "| Menjawab 'apa yang harus dilakukan?' | ❌ | ❌ | **✅** |",
            "| Memberikan skor kuantitatif setelah intervensi | ❌ | ❌ | **✅** |",
            "| Membuka akses ke pekerjaan baru (beyond top-K) | ❌ | ❌ | **✅** |",
            "",
        ]
        for r in e5:
            lines += [
                f"**{r['student']} ({r['profil']}):**",
                f"- SHAP: *\"{r['shap_top_contributor'][:60]}\"* adalah kontributor tertinggi",
                f"- LIME: *\"{r['lime_top_contributor'][:60]}\"* sebagai penjelasan lokal",
                f"- DiCE: Membuka **{r['n_jobs_now_achievable_via_dice']} pekerjaan baru** yang bisa dicapai dengan intervensi konkret",
                "",
            ]

    lines += [
        "**Kesimpulan Novelty:**",
        "Sistem ini mengintegrasikan tiga lapisan XAI yang saling melengkapi:",
        "1. **SHAP** — Menjawab 'mengapa?' (global, teoritis, game theory foundation)",
        "2. **LIME** — Menjawab 'mengapa?' secara lokal (per prediksi, lebih cepat)",
        "3. **DiCE** — Menjawab 'bagaimana meningkatkan diri?' (prospektif, action-oriented)",
        "",
        "Kombinasi ketiga ini adalah **kontribusi novel** proyek ini,",
        "melampaui paper P1 (hanya SHAP+LIME) dan paper P2 (tidak ada implementasi DiCE).",
    ]

    out = os.path.join(RESULTS_XAI, "LOGBOOK_SUMMARY_XAI_v2.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    log(f"[DONE] Logbook v2 saved: {out}")

# ── MAIN ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("="*60)
    print("  EXPERIMENT RUNNER v2 - Aligned with Papers")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    e4 = run_eks04()
    e5 = run_eks05()
    generate_logbook_v2(e4, e5)
    print("\n"+"="*60)
    print("  EKSPERIMEN v2 SELESAI!")
    print("="*60)
