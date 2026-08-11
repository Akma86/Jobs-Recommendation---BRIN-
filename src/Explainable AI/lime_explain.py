# -*- coding: utf-8 -*-
"""
LIME EXPLANATIONS - Local Interpretable Model-Agnostic Explanations

Menggunakan LIME (LimeTabularExplainer) untuk menjelaskan keputusan
sistem rekomendasi pekerjaan. Sementara SHAP menjelaskan setiap feature
contribution secara global, LIME menjelaskan setiap prediksi secara
lokal (per mahasiswa-pekerjaan) dengan pendekatan surrogate model linear.

METHOD:
  - Setiap job memiliki vektor fitur: kontribusi tiap MK dan Sertifikat
    terhadap skor akhirnya.
  - LIME membuat perturbasi di sekitar data poin tersebut, lalu melatih
    model linear sederhana sebagai "penjelasan" di sekitar titik tersebut.
  - Output: bobot fitur lokal yang menjelaskan MENGAPA skor pekerjaan ini
    tinggi atau rendah untuk mahasiswa ini.

COMPARISON WITH SHAP:
  - SHAP (di shap_explain.py): Pendekatan game-theoretic (Shapley values),
    memiliki jaminan matematis soal fairness, tapi lebih lambat.
  - LIME (di sini): Pendekatan surrogate model, lebih cepat dan intuitif
    bagi pembaca awam, tapi bersifat approksimasi.

REQUIREMENTS:
  pip install lime matplotlib pandas numpy scikit-learn

OUTPUT:
  - lime_explanations.csv: long format: job_id, job_title, feature, lime_weight, intercept
  - lime_plots/: bar chart PNG untuk top N jobs
"""

import os
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")  # headless - aman dipanggil di loop batch tanpa GUI
import matplotlib.pyplot as plt


def compute_lime_contributions(feature_contributions: dict, num_samples: int = 1000):
    """
    Menggunakan LIME untuk menghitung bobot fitur lokal pada satu pekerjaan.

    Parameters
    ----------
    feature_contributions : dict
        {feature_label: contribution_value} - dari aggregate_to_student_level
        contoh: {"MK: Algoritma dan Pemrograman": 0.43, "Sertifikat: AWS": 0.81}
    num_samples : int
        Jumlah perturbasi yang LIME buat (lebih banyak = lebih akurat tapi lebih lambat)

    Returns
    -------
    lime_weights : dict
        {feature_label: lime_weight}
    intercept : float
        Nilai intercept (skor dasar) dari surrogate model linear LIME
    """
    # pyrefly: ignore [missing-import]
    from lime.lime_tabular import LimeTabularExplainer

    feature_names = list(feature_contributions.keys())
    if not feature_names:
        return {}, 0.0

    values = np.array([feature_contributions[f] for f in feature_names], dtype=float)
    n = len(values)

    # Training data: perturbasi acak di sekitar seluruh feature space
    training_data = np.random.uniform(0, values.max() + 1e-9, size=(num_samples, n))
    # Tambahkan titik "zero" (mahasiswa tanpa kompetensi apapun)
    training_data = np.vstack([np.zeros((1, n)), training_data])

    # Model yang "dijelaskan": fungsi penjumlahan linear (sama persis dengan pipeline)
    def predict_fn(X):
        return (X @ values).reshape(-1)

    explainer = LimeTabularExplainer(
        training_data=training_data,
        feature_names=feature_names,
        mode="regression",
        verbose=False,
        discretize_continuous=False,
    )

    # Titik yang mau dijelaskan: mahasiswa ini dengan fitur ini
    instance = values.reshape(1, -1)
    explanation = explainer.explain_instance(
        data_row=instance[0],
        predict_fn=predict_fn,
        num_features=n,
        num_samples=num_samples,
    )

    # Konversi hasil LIME ke dict {feature_name: weight}
    # as_map() mengembalikan {class_index: [(feature_index, weight), ...]}
    # Untuk regresi, kita ambil key 1 (atau key pertama yang tersedia)
    lime_weights = {}
    raw_map = explanation.as_map()
    label_key = list(raw_map.keys())[0]  # regresi hanya punya satu label
    for idx, weight in raw_map[label_key]:
        lime_weights[feature_names[idx]] = round(float(weight), 4)

    intercept = round(float(explanation.intercept[1]), 4)
    return lime_weights, intercept


def plot_lime_bar(lime_weights, intercept, job_title, save_path, max_display=10):
    """
    Bar chart horizontal yang menunjukkan kontribusi tiap MK/sertifikat
    menurut LIME surrogate model.

    Warna hijau = kontribusi positif (mendorong skor naik)
    Warna merah = kontribusi negatif (menurunkan skor)
    """
    if not lime_weights:
        return

    # Urutkan dari kontribusi terbesar
    items = sorted(lime_weights.items(), key=lambda kv: abs(kv[1]), reverse=True)[:max_display]
    labels = [k for k, _ in items][::-1]
    vals = [v for _, v in items][::-1]
    colors = ["#1B5E20" if v >= 0 else "#B71C1C" for v in vals]

    fig, ax = plt.subplots(figsize=(9, 0.5 * len(vals) + 2.5))
    bars = ax.barh(labels, vals, color=colors, edgecolor="white", linewidth=0.5)
    ax.axvline(0, color="gray", linestyle="-", linewidth=0.8)

    # Anotasi nilai di ujung bar
    for bar, v in zip(bars, vals):
        x_pos = bar.get_x() + bar.get_width() + (0.005 if v >= 0 else -0.005)
        ha = "left" if v >= 0 else "right"
        ax.text(x_pos, bar.get_y() + bar.get_height() / 2,
                f"{v:+.3f}", va="center", ha=ha, fontsize=8, color="black")

    ax.set_title(
        f"Penjelasan LIME: Kontribusi Lokal tiap Kompetensi\n'{job_title}' (intercept={intercept:.2f})",
        fontsize=10, pad=10,
    )
    ax.set_xlabel("Bobot LIME (kontribusi lokal terhadap skor prediksi)")
    ax.tick_params(axis="y", labelsize=8)
    plt.tight_layout()

    out_dir = os.path.dirname(save_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    plt.savefig(save_path, dpi=150)
    plt.close(fig)


def generate_lime_report(
    job_contributions: dict,
    job_titles: dict,
    top_job_ids: list,
    csv_path: str = "lime_explanations.csv",
    plots_dir: str = "lime_plots",
    n_plots: int = 5,
    num_samples: int = 1000,
):
    """
    Fungsi utama yang dipanggil dari app.py atau streamlitApp.py.

    Parameters
    ----------
    job_contributions : dict
        {job_id: {feature_label: contribution_value}}
        - sama persis dengan objek yang dihasilkan oleh run_pipeline() di full_pipeline.py
    job_titles : dict
        {job_id: job_title}
    top_job_ids : list
        Daftar job_id yang akan di-generate LIME-nya (biasanya top-N rekomendasi)
    csv_path : str
        Path untuk menyimpan hasil CSV (format panjang: 1 baris per feature per job)
    plots_dir : str
        Direktori untuk menyimpan plot bar chart PNG
    n_plots : int
        Jumlah job teratas yang dibuatkan plot-nya
    num_samples : int
        Jumlah perturbasi LIME (lebih banyak = lebih akurat tapi lebih lambat)

    Returns
    -------
    pd.DataFrame
        DataFrame berisi semua penjelasan LIME dalam format panjang
    """
    rows = []
    for rank, job_id in enumerate(top_job_ids, start=1):
        contributions = job_contributions.get(job_id, {})
        if not contributions:
            continue

        job_title = job_titles.get(job_id, str(job_id))
        print(f"  [{rank}/{len(top_job_ids)}] LIME for: {job_title}")

        lime_weights, intercept = compute_lime_contributions(contributions, num_samples=num_samples)

        for feature, weight in lime_weights.items():
            rows.append({
                "job_id": job_id,
                "job_title": job_title,
                "feature": feature,
                "lime_weight": weight,
                "intercept": intercept,
            })

        if rank <= n_plots:
            plot_path = os.path.join(plots_dir, f"lime_bar_{rank:02d}_{job_id}.png")
            plot_lime_bar(lime_weights, intercept, job_title, plot_path)

    df = pd.DataFrame(rows)
    if not df.empty:
        df.to_csv(csv_path, index=False)
        print(f"Saved: {csv_path} ({len(df)} rows)")
        if n_plots:
            print(f"Saved bar plots for top {min(n_plots, len(top_job_ids))} jobs -> {plots_dir}/")
    else:
        print("No LIME results to save (no job contributions found).")

    return df


# ---------------------------------------------------------------------------
# CLI entry point - bisa dijalankan standalone untuk pengujian
# ---------------------------------------------------------------------------
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run LIME on an existing pipeline output")
    parser.add_argument("--contributions_csv", required=True,
                        help="CSV file dengan kolom: job_id, job_title, feature, contribution "
                             "(bisa dibuat dari final_recommendations + shap_explanations)")
    parser.add_argument("--out_csv", default="lime_explanations.csv")
    parser.add_argument("--out_plots_dir", default="lime_plots")
    parser.add_argument("--n_plots", type=int, default=5)
    parser.add_argument("--num_samples", type=int, default=1000)
    args = parser.parse_args()

    # Load contributions dari CSV
    df = pd.read_csv(args.contributions_csv)
    required_cols = {"job_id", "job_title", "feature", "contribution"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"contributions_csv harus punya kolom: {required_cols}. "
                         f"Kolom yang ada: {set(df.columns)}")

    job_contributions = {}
    job_titles = {}
    for job_id, group in df.groupby("job_id"):
        job_titles[job_id] = group.iloc[0]["job_title"]
        job_contributions[job_id] = dict(zip(group["feature"], group["contribution"]))

    top_job_ids = list(job_titles.keys())[:15]  # top 15 jobs

    print("=== LIME EXPLANATIONS ===\n")
    generate_lime_report(
        job_contributions=job_contributions,
        job_titles=job_titles,
        top_job_ids=top_job_ids,
        csv_path=args.out_csv,
        plots_dir=args.out_plots_dir,
        n_plots=args.n_plots,
        num_samples=args.num_samples,
    )


if __name__ == "__main__":
    main()
