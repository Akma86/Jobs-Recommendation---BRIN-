import os

import numpy as np
import shap

import matplotlib
matplotlib.use("Agg")  # headless - aman dipanggil di loop batch tanpa GUI
import matplotlib.pyplot as plt


def compute_shap_contributions(feature_contributions: dict, cap_nsamples: int = 2048):
    """
    feature_contributions: {feature_label: contribution_value}, sudah dihitung
    di aggregate_to_student_level (mis. "MK: Algoritma dan Pemrograman" -> 0.43,
    "Sertifikat (agregat)" -> 0.81).

    Returns: (shap_dict, base_value)
        shap_dict: {feature_label: shap_value}
        base_value: skor dasar tanpa kompetensi apapun (selalu 0.0 di sini,
                    tapi dihitung via SHAP, bukan diasumsikan)
    """
    feature_names = list(feature_contributions.keys())
    if not feature_names:
        return {}, 0.0

    values = np.array([feature_contributions[f] for f in feature_names], dtype=float)

    def f(mask_matrix):
        return mask_matrix @ values

    background = np.zeros((1, len(values)))
    explainer = shap.KernelExplainer(f, background)

    n = len(values)
    nsamples = min(2 ** n, cap_nsamples)  # enumerasi penuh selama jumlah fitur masih kecil
    shap_values = explainer.shap_values(np.ones((1, n)), nsamples=nsamples, silent=True)[0]

    return dict(zip(feature_names, shap_values)), float(explainer.expected_value)


def plot_shap_waterfall(shap_dict, base_value, job_title, save_path, max_display=10):
    """Waterfall chart kontribusi tiap MK/sertifikat ke skor akhir, buat
    dilampirkan di laporan. Dibuat manual pakai matplotlib (bukan
    shap.plots.waterfall) supaya reliable dipanggil headless/batch untuk
    banyak job sekaligus tanpa terikat versi API shap.plots.*."""
    if not shap_dict:
        return

    items = sorted(shap_dict.items(), key=lambda kv: abs(kv[1]), reverse=True)[:max_display]
    labels = [k for k, _ in items][::-1]
    vals = [v for _, v in items][::-1]

    cum = base_value
    lefts = []
    for v in vals:
        lefts.append(cum)
        cum += v
    final_score = base_value + sum(shap_dict.values())

    colors = ["#2E7D32" if v >= 0 else "#C62828" for v in vals]

    fig, ax = plt.subplots(figsize=(8, 0.5 * len(vals) + 2))
    ax.barh(labels, vals, left=lefts, color=colors)
    ax.axvline(base_value, color="gray", linestyle="--", linewidth=1, label=f"base={base_value:.2f}")
    for i, (l, v) in enumerate(zip(lefts, vals)):
        ax.text(l + v / 2, i, f"{v:+.2f}", va="center", ha="center", fontsize=8, color="white")
    ax.set_title(f"Kontribusi SHAP terhadap skor rekomendasi\n'{job_title}' (skor akhir={final_score:.2f})")
    ax.set_xlabel("Kontribusi terhadap skor akhir")
    ax.legend(loc="lower right", fontsize=8)
    plt.tight_layout()

    out_dir = os.path.dirname(save_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    plt.savefig(save_path, dpi=150)
    plt.close(fig)


def generate_shap_report(job_contributions: dict, job_titles: dict, top_job_ids,
                          csv_path="shap_explanations.csv", plots_dir="shap_plots",
                          n_plots=5):
    """
    job_contributions: {job_id: {feature_label: contribution_value}}
    job_titles: {job_id: job_title}
    top_job_ids: list job_id yang mau di-generate SHAP-nya (biasanya top-N
                 dari final_recommendations.csv)

    Output:
        csv_path   -> long format: job_id, job_title, feature, shap_value, base_value
        plots_dir/ -> waterfall PNG untuk n_plots job teratas
    """
    import pandas as pd

    rows = []
    for rank, job_id in enumerate(top_job_ids, start=1):
        contributions = job_contributions.get(job_id, {})
        shap_dict, base_value = compute_shap_contributions(contributions)
        job_title = job_titles.get(job_id, str(job_id))

        for feature, sv in shap_dict.items():
            rows.append({
                "job_id": job_id,
                "job_title": job_title,
                "feature": feature,
                "shap_value": round(float(sv), 4),
                "base_value": round(base_value, 4),
            })

        if rank <= n_plots:
            plot_path = os.path.join(plots_dir, f"shap_waterfall_{rank:02d}_{job_id}.png")
            plot_shap_waterfall(shap_dict, base_value, job_title, plot_path)

    df = pd.DataFrame(rows)
    df.to_csv(csv_path, index=False)
    print(f"Saved: {csv_path} ({len(df)} rows)")
    if n_plots:
        print(f"Saved waterfall plots for top {min(n_plots, len(top_job_ids))} jobs -> {plots_dir}/")
    return df
