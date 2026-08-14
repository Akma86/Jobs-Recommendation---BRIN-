# -*- coding: utf-8 -*-
"""
RUN_EXPERIMENTS.PY - Master script untuk menjalankan semua eksperimen logbook.

Eksperimen yang dijalankan:
  1. Eksperimen 01: Batch Ranking 10 Mahasiswa Dummy
  2. Eksperimen 02: Ablation Study - Pengaruh Sertifikat
  3. Eksperimen 03: Baseline TF-IDF vs Semantic (SBERT+CE)
"""

import os, sys, glob, subprocess, pandas as pd
from datetime import datetime
from scipy.stats import spearmanr

ROOT_DIR  = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(ROOT_DIR)

DATA_DIR        = os.path.join(WORKSPACE, "data")
PERCOBAAN_DIR   = os.path.join(DATA_DIR, "Percobaan")
RESULTS_DIR     = os.path.join(WORKSPACE, "results")
EKS01_DIR       = os.path.join(RESULTS_DIR, "Eksperimen_01_Batch_10_Mahasiswa")
EKS02_DIR       = os.path.join(RESULTS_DIR, "Eksperimen_02_Ablation_Study")
EKS03_DIR       = os.path.join(RESULTS_DIR, "Eksperimen_03_Baseline_vs_Semantic")

PARSE_SCRIPT    = os.path.join(ROOT_DIR, "RankingJob", "parse_input.py")
APP_SCRIPT      = os.path.join(ROOT_DIR, "prototype", "app.py")
BASELINE_SCRIPT = os.path.join(ROOT_DIR, "Skill Gap", "baseline_keyword_matching.py")
ABLATION_SCRIPT = os.path.join(ROOT_DIR, "Skill Gap", "ablation_study.py")

KHS_DIR         = os.path.join(DATA_DIR, "generated_markdown_khs")
CERTS_DIR       = os.path.join(DATA_DIR, "generated_markdown_certificates")
COURSE_CLO_CSV  = os.path.join(DATA_DIR, "Mata Kuliah", "course_clo_consolidated.csv")
JOBS_CSV        = os.path.join(DATA_DIR, "Pekerjaan", "Processed", "jobs_unified.csv")


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def run_eksperimen_01():
    log("=" * 60)
    log("EKSPERIMEN 01: Batch Ranking 10 Mahasiswa Dummy")
    log("=" * 60)
    khs_files = sorted(glob.glob(os.path.join(KHS_DIR, "*_KHS.md")))
    if not khs_files:
        log("ERROR: Tidak ada file KHS di " + KHS_DIR); return pd.DataFrame()

    summary_rows = []
    for khs_file in khs_files:
        name = os.path.basename(khs_file).replace("_KHS.md", "")
        log(f"  -> {name}")
        work_dir = os.path.join(PERCOBAAN_DIR, f"Coba_Mahasiswa_{name}")
        out_dir  = os.path.join(EKS01_DIR, name)
        os.makedirs(work_dir, exist_ok=True); os.makedirs(out_dir, exist_ok=True)

        cert_dir  = os.path.join(CERTS_DIR, name)
        parse_cmd = [sys.executable, PARSE_SCRIPT, "--khs", khs_file]
        if os.path.isdir(cert_dir) and os.listdir(cert_dir):
            parse_cmd += ["--cert_dir", cert_dir]
        r = subprocess.run(parse_cmd, cwd=work_dir, capture_output=True, text=True)
        if r.returncode != 0:
            log(f"     SKIP (parse error): {r.stderr[:150]}"); continue

        khs_csv   = os.path.join(work_dir, "transcript_parsed.csv")
        certs_csv = os.path.join(work_dir, "certificates_parsed.csv")
        env = os.environ.copy(); env["PYTHONPATH"] = ROOT_DIR
        app_cmd = [sys.executable, APP_SCRIPT, "--khs", khs_csv, "--skip-xai"]
        if os.path.exists(certs_csv): app_cmd += ["--certs", certs_csv]
        r = subprocess.run(app_cmd, cwd=out_dir, capture_output=True, text=True, env=env)
        if r.returncode != 0:
            log(f"     SKIP (pipeline error): {r.stderr[:150]}"); continue

        rec_csv = os.path.join(out_dir, "final_recommendations.csv")
        if os.path.exists(rec_csv):
            df = pd.read_csv(rec_csv).head(5)
            for rank, (_, row) in enumerate(df.iterrows(), start=1):
                summary_rows.append({
                    "student_name": name,
                    "has_certificates": os.path.exists(certs_csv),
                    "rank": rank,
                    "job_title": row.get("job_title",""),
                    "job_company": row.get("job_company",""),
                    "final_score": round(float(row.get("final_score",0)), 4),
                })
            log(f"     OK - Top-1: {df.iloc[0]['job_title']}")

    if not summary_rows:
        log("Tidak ada hasil."); return pd.DataFrame()
    summary_df = pd.DataFrame(summary_rows)
    out_path = os.path.join(EKS01_DIR, "summary_all_students.csv")
    summary_df.to_csv(out_path, index=False)
    log(f"  SELESAI -> {out_path} | {summary_df['student_name'].nunique()} mahasiswa")
    return summary_df


def run_eksperimen_02():
    log("\n" + "=" * 60)
    log("EKSPERIMEN 02: Ablation Study - Pengaruh Sertifikat")
    log("=" * 60)
    ablation_rows = []
    for student_dir in sorted(glob.glob(os.path.join(EKS01_DIR, "*/"))):
        name = os.path.basename(student_dir.rstrip("/\\"))
        req  = ["final_recommendations.csv", "course_job_aggregated.csv", "pipeline_course_match_log.csv"]
        if not all(os.path.exists(os.path.join(student_dir, f)) for f in req):
            log(f"  SKIP {name}: missing files"); continue
        log(f"  -> {name}")
        out_dir = os.path.join(EKS02_DIR, name); os.makedirs(out_dir, exist_ok=True)
        r = subprocess.run([sys.executable, ABLATION_SCRIPT], cwd=student_dir, capture_output=True, text=True)
        if r.returncode != 0:
            log(f"     ERROR: {r.stderr[:150]}"); continue
        abl_csv = os.path.join(student_dir, "ablation_C_with_without_certs.csv")
        if os.path.exists(abl_csv):
            abl_df = pd.read_csv(abl_csv)
            if len(abl_df) > 2:
                rho, pval = spearmanr(abl_df["khs_only_score"], abl_df["final_score"])
                top10_khs  = abl_df.sort_values("khs_only_score", ascending=False).head(10)["job_id"].tolist()
                top10_cert = abl_df.sort_values("final_score", ascending=False).head(10)["job_id"].tolist()
                overlap    = len(set(top10_khs) & set(top10_cert)) / 10
                ablation_rows.append({
                    "student_name":    name,
                    "spearman_rho":    round(rho, 4),
                    "p_value":         round(pval, 6),
                    "top10_overlap":   round(overlap, 2),
                    "certs_changed":   overlap < 1.0,
                    "n_jobs_changed":  round((1-overlap)*10),
                })
                abl_df.to_csv(os.path.join(out_dir, "ablation_C_with_without_certs.csv"), index=False)
                log(f"     rho={rho:.3f}, overlap={overlap:.2f}")

    if not ablation_rows: log("Tidak ada hasil."); return pd.DataFrame()
    abl_summary = pd.DataFrame(ablation_rows)
    out_path = os.path.join(EKS02_DIR, "ablation_summary.csv")
    abl_summary.to_csv(out_path, index=False)
    log(f"  Rata-rata rho: {abl_summary['spearman_rho'].mean():.3f}")
    log(f"  Mahasiswa terpengaruh sertifikat: {abl_summary['certs_changed'].sum()}/{len(abl_summary)}")
    log(f"  SELESAI -> {out_path}")
    return abl_summary


def run_eksperimen_03():
    log("\n" + "=" * 60)
    log("EKSPERIMEN 03: Baseline TF-IDF vs Semantic (SBERT+CE)")
    log("=" * 60)
    baseline_rows = []
    for student_dir in sorted(glob.glob(os.path.join(EKS01_DIR, "*/"))):
        name = os.path.basename(student_dir.rstrip("/\\"))
        req  = ["pipeline_course_match_log.csv", "final_recommendations.csv"]
        if not all(os.path.exists(os.path.join(student_dir, f)) for f in req):
            log(f"  SKIP {name}: missing files"); continue
        log(f"  -> {name}")
        out_dir = os.path.join(EKS03_DIR, name); os.makedirs(out_dir, exist_ok=True)
        r = subprocess.run(
            [sys.executable, BASELINE_SCRIPT, "--course_clo_csv", COURSE_CLO_CSV, "--jobs_csv", JOBS_CSV],
            cwd=student_dir, capture_output=True, text=True
        )
        if r.returncode != 0:
            log(f"     ERROR: {r.stderr[:300]}"); continue
        cmp_csv = os.path.join(student_dir, "baseline_vs_semantic_comparison.csv")
        if os.path.exists(cmp_csv):
            cmp_df = pd.read_csv(cmp_csv)
            if len(cmp_df) >= 3:
                rho, pval = spearmanr(cmp_df["tfidf_similarity"], cmp_df["final_score"])
                agreement = "RENDAH (Semantik jauh lebih unggul)" if rho < 0.3 else ("TINGGI (Mirip baseline)" if rho > 0.7 else "SEDANG (perbedaan bermakna)")
                baseline_rows.append({
                    "student_name":       name,
                    "n_overlapping_jobs": len(cmp_df),
                    "spearman_rho":       round(rho, 4),
                    "p_value":            round(pval, 6),
                    "agreement_level":    agreement,
                })
                cmp_df.to_csv(os.path.join(out_dir, "baseline_vs_semantic_comparison.csv"), index=False)
                bl_csv = os.path.join(student_dir, "baseline_job_ranking.csv")
                if os.path.exists(bl_csv):
                    pd.read_csv(bl_csv).to_csv(os.path.join(out_dir, "baseline_job_ranking.csv"), index=False)
                log(f"     rho={rho:.3f} - {agreement}")

    if not baseline_rows: log("Tidak ada hasil."); return pd.DataFrame()
    bl_summary = pd.DataFrame(baseline_rows)
    out_path = os.path.join(EKS03_DIR, "baseline_vs_semantic_summary.csv")
    bl_summary.to_csv(out_path, index=False)
    log(f"  Rata-rata rho (TF-IDF vs Semantic): {bl_summary['spearman_rho'].mean():.3f}")
    log(f"  SELESAI -> {out_path}")
    return bl_summary


def main():
    print("\n" + "=" * 60)
    print("  MASTER EXPERIMENT RUNNER - Logbook KP BRIN")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    e1 = run_eksperimen_01()
    e2 = run_eksperimen_02()
    e3 = run_eksperimen_03()
    print("\n" + "=" * 60)
    print("  SEMUA EKSPERIMEN SELESAI")
    print(f"  Eks-01: {e1['student_name'].nunique() if not e1.empty else 0} mahasiswa")
    print(f"  Eks-02: {len(e2) if not e2.empty else 0} ablation reports")
    print(f"  Eks-03: {len(e3) if not e3.empty else 0} baseline comparisons")
    print("  Output -> results/Eksperimen_0*/")
    print("=" * 60)

if __name__ == "__main__":
    main()
