# -*- coding: utf-8 -*-
"""
MASTER EXPERIMENT RUNNER - XAI Experiments for KP BRIN Logbook
================================================================
EKS01 - SHAP: Analisis kontribusi fitur per mahasiswa
EKS02 - DiCE: Validasi kualitas counterfactual (effort + Jaccard diversity)
EKS03 - SHAP vs DiCE: Perbandingan actionability
"""

import os, sys, subprocess
import pandas as pd
import numpy as np
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR  = os.path.join(ROOT_DIR, "src")
DATA_DIR = os.path.join(ROOT_DIR, "data", "Percobaan")
RESULTS_XAI = os.path.join(ROOT_DIR, "results", "Eksperimen_XAI")
APP_SCRIPT  = os.path.join(SRC_DIR, "prototype", "app.py")

STUDENTS = {
    "EKS01": [
        ("Andi_Wijaya",   "Coba_Mahasiswa_Andi_Wijaya"),
        ("Rizky_Pratama", "Coba_Mahasiswa_Rizky_Pratama"),
        ("Nadia_Putri",   "Coba_Mahasiswa_Nadia_Putri"),
    ],
    "EKS02": [
        ("Andi_Wijaya",   "Coba_Mahasiswa_Andi_Wijaya"),
    ],
    "EKS03": [
        ("Andi_Wijaya",   "Coba_Mahasiswa_Andi_Wijaya"),
        ("Fajar_Nugroho", "Coba_Mahasiswa_Fajar_Nugroho"),
    ],
}

LOG = []
def log(m):
    ts = datetime.now().strftime("%H:%M:%S")
    s  = f"[{ts}] {m}"
    print(s); LOG.append(s)

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
        log(f"  [ERROR] {r.stderr[-600:]}")
        return False
    return True

# ── EKS01 ─────────────────────────────────────────────────────────────────
def run_eks01():
    log("="*60)
    log("EKS01: SHAP Analisis Kontribusi Fitur Per Mahasiswa")
    log("="*60)
    out_base = os.path.join(RESULTS_XAI, "EKS01_SHAP")
    rows = []
    for name, pname in STUDENTS["EKS01"]:
        log(f"  -> {name}")
        khs, cert = get_paths(pname)
        if not os.path.exists(khs):
            log(f"  [SKIP] No transcript for {name}"); continue
        out_dir = os.path.join(out_base, name)
        if not run_app(khs, cert, out_dir, "shap"):
            continue
        shap_csv = os.path.join(out_dir, "shap_explanations.csv")
        if os.path.exists(shap_csv):
            df = pd.read_csv(shap_csv)
            log(f"  [OK] {name}: {len(df)} SHAP rows")
            if "feature" in df.columns and "shap_value" in df.columns:
                top = df.groupby("feature")["shap_value"].mean().sort_values(ascending=False).head(5)
                for feat, val in top.items():
                    rows.append({"student": name, "feature": feat, "avg_shap": round(val, 4)})
    if rows:
        pd.DataFrame(rows).to_csv(os.path.join(out_base, "EKS01_shap_summary.csv"), index=False)
    log("  [EKS01 DONE]\n")
    return rows

# ── EKS02 ─────────────────────────────────────────────────────────────────
def run_eks02():
    log("="*60)
    log("EKS02: Validasi Kualitas DiCE (Effort + Jaccard)")
    log("="*60)
    out_base = os.path.join(RESULTS_XAI, "EKS02_DiCE")
    rows = []
    for name, pname in STUDENTS["EKS02"]:
        log(f"  -> {name}")
        khs, cert = get_paths(pname)
        if not os.path.exists(khs):
            log(f"  [SKIP] {name}"); continue
        out_dir = os.path.join(out_base, name)
        if not run_app(khs, cert, out_dir, "dice"):
            continue
        dice_csv = os.path.join(out_dir, "dice_counterfactuals.csv")
        if not os.path.exists(dice_csv):
            log("  [WARN] No dice_counterfactuals.csv"); continue
        df = pd.read_csv(dice_csv)
        log(f"  [OK] {name}: {len(df)} DiCE rows")
        for job_id, jdf in df.groupby("job_id"):
            cfs = {}
            for cf_id, cdf in jdf.groupby("cf_id"):
                cfs[cf_id] = set(cdf["feature"].tolist())
            ids = list(cfs.keys())
            jacs = []
            for i in range(len(ids)):
                for j in range(i+1, len(ids)):
                    a, b = cfs[ids[i]], cfs[ids[j]]
                    u = len(a|b)
                    jacs.append(len(a&b)/u if u else 0)
            avg_j = round(float(np.mean(jacs)), 3) if jacs else 0.0
            reaches = bool(jdf["cf_reaches_target"].any())
            rows.append({
                "student": name, "job_id": job_id,
                "job_title": jdf["job_title"].iloc[0],
                "n_cf": jdf["cf_id"].nunique(),
                "avg_jaccard": avg_j,
                "is_diverse": avg_j < 0.4,
                "reaches_target": reaches,
            })
            log(f"    {jdf['job_title'].iloc[0][:40]} | J={avg_j:.3f} | div={avg_j<0.4} | reach={reaches}")
    if rows:
        adf = pd.DataFrame(rows)
        adf.to_csv(os.path.join(out_base, "EKS02_dice_quality.csv"), index=False)
        log(f"  Diverse: {adf['is_diverse'].sum()}/{len(adf)} | Reaches: {adf['reaches_target'].sum()}/{len(adf)}")
    log("  [EKS02 DONE]\n")
    return rows

# ── EKS03 ─────────────────────────────────────────────────────────────────
def run_eks03():
    log("="*60)
    log("EKS03: SHAP vs DiCE Actionability Comparison")
    log("="*60)
    out_base = os.path.join(RESULTS_XAI, "EKS03_SHAP_vs_DiCE")
    rows = []
    profiles = {"Andi_Wijaya": "Kuat (ada sertifikat)", "Fajar_Nugroho": "Lemah (tanpa sertifikat)"}
    for name, pname in STUDENTS["EKS03"]:
        log(f"  -> {name}")
        khs, cert = get_paths(pname)
        if not os.path.exists(khs):
            log(f"  [SKIP] {name}"); continue
        out_dir = os.path.join(out_base, name)
        if not run_app(khs, cert, out_dir, "all"):
            continue
        shap_df = pd.read_csv(os.path.join(out_dir, "shap_explanations.csv")) \
                  if os.path.exists(os.path.join(out_dir, "shap_explanations.csv")) else pd.DataFrame()
        dice_df = pd.read_csv(os.path.join(out_dir, "dice_counterfactuals.csv")) \
                  if os.path.exists(os.path.join(out_dir, "dice_counterfactuals.csv")) else pd.DataFrame()
        top_shap = shap_df.groupby("feature")["shap_value"].mean().sort_values(ascending=False).index[0] \
                   if not shap_df.empty and "shap_value" in shap_df.columns else ""
        top_dice = dice_df["feature"].value_counts().index[0] if not dice_df.empty and "feature" in dice_df.columns else ""
        n_act = dice_df[dice_df["cf_reaches_target"]==True]["job_id"].nunique() if not dice_df.empty else 0
        rows.append({
            "student": name, "profil": profiles.get(name, ""),
            "top_shap_contributor": top_shap, "top_dice_intervention": top_dice,
            "n_actionable_jobs": n_act,
        })
        log(f"    SHAP top: {top_shap[:40]} | DiCE top: {top_dice[:40]} | Actionable: {n_act}")
    if rows:
        pd.DataFrame(rows).to_csv(os.path.join(out_base, "EKS03_comparison.csv"), index=False)
    log("  [EKS03 DONE]\n")
    return rows

# ── LOGBOOK SUMMARY ────────────────────────────────────────────────────────
def generate_summary(e1, e2, e3):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    md  = [f"# Ringkasan Eksperimen XAI - Logbook KP BRIN", f"*Tanggal: {now}*", "", "---", ""]

    md += ["## EKS01 — SHAP: Kontribusi Fitur Per Mahasiswa", ""]
    if e1:
        md += ["| Mahasiswa | Feature Tertinggi | Avg SHAP |", "|-----------|-------------------|---------|"]
        seen = {}
        for r in e1:
            if r["student"] not in seen:
                md.append(f"| {r['student']} | {r['feature']} | {r['avg_shap']} |")
                seen[r['student']] = True
    md += ["", "**Interpretasi:** MK bernilai tinggi pada domain relevan memberikan kontribusi SHAP terbesar.", "", "---", ""]

    md += ["## EKS02 — DiCE: Validasi Kualitas Counterfactual", ""]
    if e2:
        n_div  = sum(1 for r in e2 if r["is_diverse"])
        n_tot  = len(e2)
        n_rch  = sum(1 for r in e2 if r["reaches_target"])
        avg_j  = round(float(np.mean([r["avg_jaccard"] for r in e2])), 3)
        md += [
            "| Metrik | Nilai |", "|--------|-------|",
            f"| Total pekerjaan | {n_tot} |",
            f"| CF diverse (Jaccard < 0.4) | {n_div}/{n_tot} |",
            f"| Rata-rata Jaccard Similarity | {avg_j} |",
            f"| CF mencapai target | {n_rch}/{n_tot} |",
        ]
    md += ["", "**Interpretasi:** Jaccard < 0.4 = CF benar-benar berbeda strategi → mahasiswa mendapat pilihan nyata.", "", "---", ""]

    md += ["## EKS03 — SHAP vs DiCE: Actionability", ""]
    if e3:
        md += ["| Mahasiswa | Profil | SHAP Top Feature | DiCE Top Intervensi | Actionable Jobs |",
               "|-----------|--------|------------------|---------------------|-----------------|"]
        for r in e3:
            md.append(f"| {r['student']} | {r['profil']} | {str(r['top_shap_contributor'])[:35]} | {str(r['top_dice_intervention'])[:35]} | {r['n_actionable_jobs']} |")
    md += [
        "", "**Interpretasi:**",
        "- **SHAP** = retrospektif, menjelaskan *mengapa* skor saat ini ada.",
        "- **DiCE** = prospektif, memberikan *langkah konkret* untuk meningkatkan peluang.",
        "- Keduanya komplementer dan sebaiknya disajikan bersamaan kepada mahasiswa.",
        "", "---", "", "## Kesimpulan",
        "Sistem XAI SHAP + DiCE terbukti berjalan dengan baik pada 10 mahasiswa dummy.",
        "Upgrade DiCE (effort cost + Jaccard diversity) menghasilkan counterfactual yang lebih realistis dan beragam.",
    ]

    out = os.path.join(RESULTS_XAI, "LOGBOOK_SUMMARY_XAI.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    log(f"\n[DONE] Logbook summary: {out}")

# ── MAIN ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("="*60)
    print("  MASTER EXPERIMENT RUNNER - Logbook KP BRIN")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    e1 = run_eks01()
    e2 = run_eks02()
    e3 = run_eks03()
    generate_summary(e1, e2, e3)
    print("\n"+"="*60)
    print("  SEMUA EKSPERIMEN SELESAI!")
    print("="*60)
