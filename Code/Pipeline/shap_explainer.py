# -*- coding: utf-8 -*-
"""
shap_explainer.py
=================
Explainability berbasis SHAP untuk pipeline rekomendasi kerja.

LATAR BELAKANG
--------------
Scoring akhir setiap job adalah jumlah linier dari kontribusi per-fitur:

    final_score(job) = sum_k [ grade_weight_k * match_confidence_k * course_job_score_max_k ]
                     + CERT_WEIGHT_GLOBAL * cert_score_max   (jika ada sertifikat)

Karena model ini adalah penjumlahan linier murni, nilai SHAP-nya EKSAK dan
bisa dihitung langsung: phi_k = kontribusi fitur k terhadap final_score.
Kemudian digunakan shap library untuk visualisasi standar (summary, waterfall, dll.)

INPUT (file CSV hasil full_pipeline_certs.py / full_pipeline_subclo.py):
  --matched       pipeline_course_match_log.csv
  --course_agg    course_job_aggregated.csv
  --final         final_recommendations.csv
  --certs         certificates_parsed.csv        (opsional)
  --cert_agg      cert_job_aggregated.csv        (opsional)

OUTPUT:
  shap_values.csv               tabel SHAP value per (job x fitur)
  shap_summary.png              feature importance global (bar)
  shap_beeswarm.png             distribusi SHAP per fitur (beeswarm)
  shap_heatmap.png              heatmap semua job x semua fitur
  shap_waterfall_rank01.png     waterfall job #1
  shap_waterfall_rank02.png     ... dst. (top-N job)

CARA PAKAI:
  # Tanpa sertifikat
  python shap_explainer.py --matched pipeline_course_match_log.csv --course_agg course_job_aggregated.csv --final final_recommendations.csv

  # Dengan sertifikat
  python shap_explainer.py --matched pipeline_course_match_log.csv --course_agg course_job_aggregated.csv --final final_recommendations.csv --certs certificates_parsed.csv --cert_agg cert_job_aggregated.csv

  # Simpan ke folder khusus
  python shap_explainer.py --matched pipeline_course_match_log.csv --course_agg course_job_aggregated.csv --final final_recommendations.csv --out_dir shap_output
"""

import argparse
import os
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

CERT_WEIGHT_GLOBAL = 1.0   # harus sama dengan nilai di full_pipeline_certs.py
TOP_N_WATERFALL    = 5     # jumlah job teratas yang dibuatkan waterfall plot


# ============================================================
# STEP 1 — Build SHAP feature matrix
# ============================================================

def build_shap_matrix(matched_df, course_agg_df, final_df,
                      certs_df=None, cert_agg_df=None):
    """
    Bangun SHAP feature matrix.

    Rows    = job_id (hanya yang masuk final_recommendations)
    Columns = satu kolom per mata kuliah yang di-include + opsional 'Sertifikat'

    Nilai phi_k(job) = grade_weight_k * match_confidence_k * course_job_score_max_k
    Ini adalah nilai SHAP eksak karena scoring adalah penjumlahan linier.

    Returns
    -------
    shap_matrix : pd.DataFrame  shape (n_jobs, n_features)
    base_value  : float         mean(final_score) sebagai baseline SHAP
    job_labels  : pd.Series     job_id -> "JobTitle @ Company"
    """
    job_ids  = final_df["job_id"].tolist()
    included = matched_df[matched_df["included"]].copy()
    included["feature_name"] = included["khs_course"].str.strip()

    # Pivot course_agg: rows=job_id, cols=course_name, vals=score_max
    course_pivot = course_agg_df.pivot_table(
        index="job_id",
        columns="course_name",
        values="course_job_score_max",
        aggfunc="max",
    ).reindex(job_ids).fillna(0.0)

    # Hitung kontribusi SHAP per course per job
    shap_dict = {}
    for _, row in included.iterrows():
        fname  = row["feature_name"]
        mname  = row["matched_course_name"]
        weight = row["grade_weight"] * row["match_confidence"]

        scores = course_pivot[mname] if mname in course_pivot.columns \
                 else pd.Series(0.0, index=job_ids)

        contrib = weight * scores.reindex(job_ids).fillna(0.0)

        # Akumulasi jika dua KHS course di-match ke course yang sama
        shap_dict[fname] = shap_dict[fname] + contrib if fname in shap_dict else contrib

    shap_matrix = pd.DataFrame(shap_dict, index=job_ids)

    # Kolom sertifikat (opsional)
    if cert_agg_df is not None and certs_df is not None and len(cert_agg_df) > 0:
        cert_pivot = cert_agg_df.set_index("job_id")["cert_score_max"].reindex(job_ids).fillna(0.0)

        if "credibility_weight" in certs_df.columns and "cert_id" in certs_df.columns:
            cred_map = certs_df.set_index("cert_id")["credibility_weight"].to_dict()
            best_ids = cert_agg_df.set_index("job_id").get("best_cert_id", pd.Series(dtype=str))
            cred = best_ids.map(cred_map).reindex(job_ids).fillna(1.0)
        else:
            cred = pd.Series(1.0, index=job_ids)

        shap_matrix["[Sertifikat]"] = (CERT_WEIGHT_GLOBAL * cert_pivot * cred).fillna(0.0)

    base_value = final_df["final_score"].mean()

    job_labels = final_df.set_index("job_id").apply(
        lambda r: f"{r['job_title']} @ {r['job_company']}", axis=1
    )

    return shap_matrix, base_value, job_labels


# ============================================================
# STEP 2 — Export CSV
# ============================================================

def export_shap_csv(shap_matrix, base_value, job_labels, final_df,
                    out_path="shap_values.csv"):
    """
    Simpan SHAP values dalam format tidy (long):
      job_id | job_label | final_score | feature | shap_value | shap_abs
    """
    score_map = final_df.set_index("job_id")["final_score"].to_dict()
    records   = []

    for job_id, row in shap_matrix.iterrows():
        label  = job_labels.get(job_id, job_id)
        fscore = score_map.get(job_id, float("nan"))
        for feat, val in row.items():
            records.append({
                "job_id":      job_id,
                "job_label":   label,
                "final_score": fscore,
                "feature":     feat,
                "shap_value":  round(float(val), 5),
                "shap_abs":    round(abs(float(val)), 5),
            })

    df = pd.DataFrame(records)
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"Saved: {out_path}  ({len(df)} rows, {shap_matrix.shape[1]} fitur)")
    return df


# ============================================================
# STEP 3 — Plots
# ============================================================

def _setup_matplotlib():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def plot_summary(shap_matrix, out_path="shap_summary.png"):
    """Bar plot: mean(|SHAP|) per fitur — feature importance global."""
    plt = _setup_matplotlib()
    import matplotlib.pyplot as _plt

    mean_abs = np.abs(shap_matrix.values).mean(axis=0)
    feat_names = shap_matrix.columns.tolist()
    order = np.argsort(mean_abs)  # ascending for horizontal bar (bottom=least)

    fig, ax = _plt.subplots(figsize=(10, max(4, len(feat_names) * 0.45)))
    bars = ax.barh(
        [feat_names[i] for i in order],
        [mean_abs[i]   for i in order],
        color="#457b9d",
    )
    ax.set_xlabel("mean(|SHAP value|)", fontsize=11)
    ax.set_title("SHAP Feature Importance (Global)\nRekomendasi Pekerjaan",
                 fontsize=13, fontweight="bold")
    ax.axvline(0, color="black", linewidth=0.8)
    _plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    _plt.close(fig)
    print(f"Saved: {out_path}")


def plot_beeswarm(shap_matrix, out_path="shap_beeswarm.png"):
    """Beeswarm: distribusi SHAP values per fitur (semua job)."""
    try:
        import shap
    except ImportError:
        print("  SKIP beeswarm: pip install shap  diperlukan")
        return

    plt = _setup_matplotlib()
    import matplotlib.pyplot as _plt

    shap_vals = shap_matrix.values.astype(float)
    feature_names = shap_matrix.columns.tolist()

    try:
        # Versi shap >= 0.42 butuh `data` (feature values) agar beeswarm bisa
        # menghitung warna (high/low). Kita pakai SHAP values itu sendiri sebagai
        # proxy feature values (linear model: phi_k = w_k * x_k, jadi proporsi sama).
        exp = shap.Explanation(
            values=shap_vals,
            base_values=np.zeros(len(shap_matrix)),
            data=shap_vals,
            feature_names=feature_names,
        )
        _plt.figure(figsize=(10, max(5, shap_matrix.shape[1] * 0.5)))
        shap.plots.beeswarm(exp, show=False, max_display=20)
        _plt.title("SHAP Beeswarm — Distribusi Kontribusi per Fitur",
                   fontsize=12, fontweight="bold")
        _plt.tight_layout()
        _plt.savefig(out_path, dpi=150, bbox_inches="tight")
        _plt.close()
        print(f"Saved: {out_path}")
    except Exception as e:
        _plt.close("all")
        print(f"  WARNING: shap.plots.beeswarm gagal ({e})")
        print("  Fallback: membuat beeswarm manual dengan matplotlib...")
        _plot_beeswarm_manual(shap_vals, feature_names, out_path)


def _plot_beeswarm_manual(shap_vals, feature_names, out_path):
    """Fallback beeswarm manual menggunakan matplotlib strip plot."""
    import matplotlib.pyplot as _plt
    import matplotlib.patches as mpatches

    mean_abs = np.abs(shap_vals).mean(axis=0)
    order = np.argsort(mean_abs)  # ascending (bottom = kurang penting)

    fig, ax = _plt.subplots(figsize=(10, max(5, len(feature_names) * 0.5)))

    for y_pos, feat_idx in enumerate(order):
        vals = shap_vals[:, feat_idx]
        # Jitter kecil agar titik-titik tidak tumpuk
        jitter = np.random.uniform(-0.2, 0.2, size=len(vals))
        colors = ["#e63946" if v >= 0 else "#457b9d" for v in vals]
        ax.scatter(vals, [y_pos + j for j in jitter], c=colors, alpha=0.75, s=40, zorder=3)

    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([feature_names[i] for i in order], fontsize=8)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("SHAP value (phi)", fontsize=11)
    ax.set_title("SHAP Beeswarm (manual) — Distribusi Kontribusi per Fitur",
                 fontsize=12, fontweight="bold")

    red_patch  = mpatches.Patch(color="#e63946", label="Kontribusi positif")
    blue_patch = mpatches.Patch(color="#457b9d", label="Kontribusi negatif")
    ax.legend(handles=[red_patch, blue_patch], loc="lower right", fontsize=8)

    ax.grid(axis="x", linestyle="--", alpha=0.4)
    _plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    _plt.close(fig)
    print(f"Saved (fallback): {out_path}")


def plot_heatmap(shap_matrix, job_labels, out_path="shap_heatmap.png"):
    """Heatmap job x fitur, warna = SHAP value."""
    plt = _setup_matplotlib()
    import matplotlib.pyplot as _plt

    data = shap_matrix.copy()
    data.index = [str(job_labels.get(jid, jid))[:50] for jid in data.index]

    col_order = np.argsort(np.abs(data.values).mean(axis=0))[::-1]
    data = data.iloc[:, col_order]

    n_jobs, n_feat = data.shape
    fig, ax = _plt.subplots(figsize=(max(10, n_feat * 0.9), max(6, n_jobs * 0.5)))
    vmax = max(abs(data.values.min()), abs(data.values.max()), 0.01)
    im = ax.imshow(data.values, aspect="auto", cmap="RdBu_r", vmin=-vmax, vmax=vmax)

    ax.set_xticks(range(n_feat))
    ax.set_xticklabels(data.columns, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(n_jobs))
    ax.set_yticklabels(data.index, fontsize=8)
    ax.set_title("SHAP Heatmap — Kontribusi per Mata Kuliah x Pekerjaan",
                 fontsize=12, fontweight="bold")
    _plt.colorbar(im, ax=ax, label="SHAP value (phi)")
    _plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    _plt.close(fig)
    print(f"Saved: {out_path}")


def plot_waterfall(shap_matrix, base_value, job_labels, final_df,
                   job_id, out_path):
    """Waterfall plot: kontribusi per fitur untuk satu job."""
    plt = _setup_matplotlib()
    import matplotlib.pyplot as _plt

    if job_id not in shap_matrix.index:
        print(f"  WARNING: {job_id} tidak ada di shap_matrix, skip.")
        return

    vals      = shap_matrix.loc[job_id].values.astype(float)
    fnames    = shap_matrix.columns.tolist()
    order     = np.argsort(np.abs(vals))[::-1][:15]
    vals_s    = vals[order]
    names_s   = [fnames[i] for i in order]

    row_final = final_df.set_index("job_id").loc[job_id]
    final_score = float(row_final["final_score"])
    job_label   = str(job_labels.get(job_id, job_id))

    fig, ax = _plt.subplots(figsize=(11, max(5, len(names_s) * 0.6)))
    colors = ["#e63946" if v >= 0 else "#457b9d" for v in vals_s[::-1]]
    bars = ax.barh(names_s[::-1], vals_s[::-1], color=colors)

    for bar, v in zip(bars, vals_s[::-1]):
        ax.text(
            bar.get_width() + (0.02 if v >= 0 else -0.02),
            bar.get_y() + bar.get_height() / 2,
            f"{v:+.3f}", va="center",
            ha="left" if v >= 0 else "right",
            fontsize=8.5,
        )

    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Kontribusi SHAP (phi)", fontsize=11)
    ax.set_title(
        f"SHAP Waterfall\n{job_label}\n"
        f"base = {base_value:.3f}  ->  final_score = {final_score:.3f}",
        fontsize=10, fontweight="bold",
    )
    _plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    _plt.close(fig)
    print(f"Saved: {out_path}")


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="SHAP explainer untuk pipeline rekomendasi pekerjaan."
    )
    parser.add_argument("--matched",    default="pipeline_course_match_log.csv",
                        help="pipeline_course_match_log.csv")
    parser.add_argument("--course_agg", default="course_job_aggregated.csv",
                        help="course_job_aggregated.csv")
    parser.add_argument("--final",      default="final_recommendations.csv",
                        help="final_recommendations.csv")
    parser.add_argument("--certs",      default=None,
                        help="(Opsional) certificates_parsed.csv")
    parser.add_argument("--cert_agg",   default=None,
                        help="(Opsional) cert_job_aggregated.csv")
    parser.add_argument("--top_n",  type=int, default=TOP_N_WATERFALL,
                        help=f"Jumlah job teratas untuk waterfall plot (default={TOP_N_WATERFALL})")
    parser.add_argument("--out_dir", default=".",
                        help="Folder output (default: folder saat ini)")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    def out(filename):
        return os.path.join(args.out_dir, filename)

    # ── Load ──────────────────────────────────────────────────────────────────
    print("=== Loading pipeline CSVs ===")
    matched_df    = pd.read_csv(args.matched)
    course_agg_df = pd.read_csv(args.course_agg)
    final_df      = pd.read_csv(args.final)
    certs_df      = pd.read_csv(args.certs)    if args.certs    else None
    cert_agg_df   = pd.read_csv(args.cert_agg) if args.cert_agg else None

    print(f"  {len(final_df)} jobs di final_recommendations")
    print(f"  {matched_df['included'].sum()} / {len(matched_df)} mata kuliah included")
    if certs_df is not None:
        print(f"  {len(certs_df)} sertifikat")

    # ── Build SHAP matrix ────────────────────────────────────────────────────
    print("\n=== Building SHAP feature matrix ===")
    shap_matrix, base_value, job_labels = build_shap_matrix(
        matched_df, course_agg_df, final_df,
        certs_df=certs_df, cert_agg_df=cert_agg_df,
    )
    print(f"  Shape: {shap_matrix.shape}  ({shap_matrix.shape[0]} jobs x {shap_matrix.shape[1]} fitur)")
    print(f"  Base value (mean final_score): {base_value:.4f}")

    # ── Export CSV ───────────────────────────────────────────────────────────
    print("\n=== Exporting SHAP CSV ===")
    export_shap_csv(shap_matrix, base_value, job_labels, final_df,
                    out_path=out("shap_values.csv"))

    # ── Plots ────────────────────────────────────────────────────────────────
    print("\n=== Generating plots ===")

    plot_summary(shap_matrix, out_path=out("shap_summary.png"))

    try:
        plot_beeswarm(shap_matrix, out_path=out("shap_beeswarm.png"))
    except Exception as e:
        print(f"  WARNING: beeswarm gagal sepenuhnya ({e}) - skip")

    plot_heatmap(shap_matrix, job_labels, out_path=out("shap_heatmap.png"))

    top_job_ids = final_df.head(args.top_n)["job_id"].tolist()
    for rank, job_id in enumerate(top_job_ids, start=1):
        plot_waterfall(
            shap_matrix, base_value, job_labels, final_df,
            job_id=job_id,
            out_path=out(f"shap_waterfall_rank{rank:02d}.png"),
        )

    # ── Console summary ──────────────────────────────────────────────────────
    print("\n=== Top 10 Fitur (mean |SHAP|) ===")
    importance = shap_matrix.abs().mean().sort_values(ascending=False)
    for feat, val in importance.head(10).items():
        print(f"  {val:6.4f}  {feat}")

    print(f"\nDone. Semua output di: {os.path.abspath(args.out_dir)}")


if __name__ == "__main__":
    main()
