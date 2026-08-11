# -*- coding: utf-8 -*-
"""
DICE COUNTERFACTUAL EXPLANATIONS - Diverse Counterfactual Explanations

Mengimplementasikan pendekatan DICE (Diverse Counterfactual Explanations)
yang diadaptasi untuk sistem rekomendasi pekerjaan ini.

DICE menjawab pertanyaan BERBEDA dari SHAP/LIME:
  - SHAP/LIME: "MENGAPA sistem merekomendasikan pekerjaan X?"
  - DICE:      "Perubahan MINIMAL apa pada profil mahasiswa yang membuat
                pekerjaan X masuk ke rekomendasi teratas?"

ADAPTASI UNTUK PROYEK INI:
Karena fungsi skor di sistem ini bersifat LINEAR (tidak ada non-linearitas
seperti pada model deep learning), counterfactual dapat dihitung secara
ANALITIK tanpa perlu melatih surrogate model:

  final_score(job) = Î£_course (grade_weight Ã— match_conf Ã— job_score_course)
                   + Î£_cert   (cert_cred_weight Ã— job_score_cert)

Satu-satunya variabel yang bisa diubah mahasiswa adalah:
  - Nilai mata kuliah (grade_weight: E=0.0, D=0.5, C=0.55, ..., A=0.85)
  - Apakah memiliki sertifikat tertentu (0 atau 1)

CARA KERJA:
  1. Untuk setiap job target (yang belum masuk top-K):
     a. Hitung skor saat ini dan gap ke ambang top-K
     b. Simulasikan: "Jika nilai MK X naik 1 tingkat (B->A), berapa tambahan skor?"
     c. Simulasikan: "Jika mahasiswa menambah sertifikat Y, berapa tambahan skor?"
     d. Susun intervensi dari yang paling efektif (sedikit perubahan, dampak besar)
     e. Tampilkan set counterfactual yang DIVERSE (berbeda-beda kombinasinya)

OUTPUT:
  - dice_counterfactuals.csv: satu baris per counterfactual per job
  - dice_plots/: bar chart perbandingan before/after per job
"""

import os
from itertools import combinations

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Grade ladder yang bisa dinaiki
GRADE_LADDER = {
    0.0: 0.50,
    0.50: 0.55,
    0.55: 0.60,
    0.60: 0.70,
    0.70: 0.80,
    0.80: 0.85,
    0.85: 0.85,
}
GRADE_NAMES = {
    0.0: "E",
    0.50: "D",
    0.55: "C",
    0.60: "BC",
    0.70: "B",
    0.80: "AB",
    0.85: "A",
}


def _grade_up(current_weight: float) -> float:
    """Naik satu tingkat dari grade saat ini."""
    return GRADE_LADDER.get(current_weight, current_weight)


def _compute_course_delta(
    course_label: str,
    grade_weight: float,
    match_conf: float,
    course_agg: pd.DataFrame,
    job_id: str,
) -> float:
    """
    Hitung tambahan skor untuk job_id jika nilai pada course_label naik satu tingkat.
    Delta = (grade_baru - grade_lama) Ã— match_conf Ã— course_job_score_max
    """
    course_name = course_label.replace("MK: ", "")
    job_rows = course_agg[
        (course_agg["course_name"] == course_name) & (course_agg["job_id"] == job_id)
    ]
    if job_rows.empty:
        return 0.0

    course_job_score = float(job_rows.iloc[0]["course_job_score_max"])
    new_grade = _grade_up(grade_weight)
    delta = (new_grade - grade_weight) * match_conf * course_job_score
    return round(delta, 4)


def generate_interventions(
    job_id: str,
    job_title: str,
    current_score: float,
    threshold_score: float,
    job_contributions: dict,
    matched_courses: pd.DataFrame,
    course_agg: pd.DataFrame,
    cert_avg_score: float = 1.5,
    cert_weight_global: float = 1.0,
) -> list:
    """
    Hasilkan daftar intervensi yang terurut dari yang paling efektif.

    Returns
    -------
    list of dict, masing-masing berisi:
        intervention_type : "improve_grade" | "add_certificate"
        feature           : label MK atau nama sertifikat
        detail            : deskripsi perubahan (e.g. "B -> A")
        score_delta       : tambahan skor akibat intervensi ini
        new_total_score   : skor total setelah intervensi
        gap_closed_pct    : persentase gap yang tertutup
    """
    gap = threshold_score - current_score
    if gap <= 0:
        return []  # sudah di atas threshold

    interventions = []
    contributions = job_contributions.get(job_id, {})

    # --- Intervensi 1: Naik Nilai MK ---
    course_lookup = matched_courses.set_index("matched_course_name")
    for label, contrib in contributions.items():
        if not label.startswith("MK: "):
            continue
        course_name = label.replace("MK: ", "")
        if course_name not in course_lookup.index:
            continue

        row = course_lookup.loc[course_name]
        grade_weight = float(row["grade_weight"])
        match_conf = float(row["match_confidence"])

        if grade_weight >= 0.85:
            continue  # sudah A, tidak bisa naik lagi

        delta = _compute_course_delta(
            label, grade_weight, match_conf, course_agg, job_id
        )
        if delta <= 0:
            continue

        current_grade = GRADE_NAMES.get(grade_weight, str(grade_weight))
        new_grade = GRADE_NAMES.get(_grade_up(grade_weight), "A")

        interventions.append(
            {
                "intervention_type": "improve_grade",
                "feature": label,
                "detail": f"{current_grade} -> {new_grade}",
                "score_delta": delta,
                "new_total_score": round(current_score + delta, 3),
                "gap_closed_pct": (
                    round(min(delta / gap, 1.0) * 100, 1) if gap > 0 else 100.0
                ),
            }
        )

    # --- Intervensi 2: Tambah Sertifikat ---
    # Estimasi kontribusi sertifikat baru = cert_weight_global Ã— cert_avg_score
    # (tidak ada data aktual karena sertifikatnya belum ada)
    has_certs = [
        k.replace("Sertifikat: ", "")
        for k in contributions
        if k.startswith("Sertifikat: ")
    ]
    suggested_certs = [
        ("AWS Certified Solutions Architect", "cloud, arsitektur, infrastruktur"),
        ("Google Data Analytics Certificate", "data, analitik, SQL, Python"),
        ("TensorFlow Developer Certificate", "machine learning, AI, TensorFlow"),
        ("Certified Ethical Hacker (CEH)", "cybersecurity, penetration testing"),
        ("Google UX Design Certificate", "UI/UX, desain, Figma"),
        ("Microsoft Azure Fundamentals (AZ-900)", "cloud, Azure, infrastruktur"),
        ("CompTIA Security+", "keamanan jaringan, cybersecurity"),
        ("PMI Project Management Professional (PMP)", "manajemen proyek, agile"),
    ]
    for cert_name, cert_domain in suggested_certs:
        if cert_name in has_certs:
            continue  # sudah punya
        delta = cert_weight_global * cert_avg_score
        interventions.append(
            {
                "intervention_type": "add_certificate",
                "feature": f"Sertifikat: {cert_name}",
                "detail": f"Tambahkan sertifikasi baru (estimasi kontribusi: {delta:.2f})",
                "score_delta": round(delta, 4),
                "new_total_score": round(current_score + delta, 3),
                "gap_closed_pct": (
                    round(min(delta / gap, 1.0) * 100, 1) if gap > 0 else 100.0
                ),
            }
        )

    # Urutkan dari delta terbesar
    interventions.sort(key=lambda x: x["score_delta"], reverse=True)
    return interventions


def generate_diverse_counterfactuals(
    interventions: list,
    current_score: float,
    threshold_score: float,
    max_counterfactuals: int = 3,
    max_interventions_per_cf: int = 3,
) -> list:
    """
    Dari daftar intervensi yang tersedia, buat set counterfactual yang DIVERSE:
    setiap counterfactual adalah kombinasi intervensi yang berbeda-beda.

    Returns
    -------
    list of dict:
        cf_id          : nomor counterfactual (1, 2, 3, ...)
        steps          : list intervensi yang dilakukan
        total_delta    : total tambahan skor
        final_score    : skor akhir setelah semua langkah
        reaches_target : apakah skor akhir >= threshold?
    """
    gap = threshold_score - current_score
    counterfactuals = []

    # Greedy: ambil kombinasi terkecil yang menutup gap
    for n_steps in range(1, min(max_interventions_per_cf + 1, len(interventions) + 1)):
        for combo in combinations(range(len(interventions)), n_steps):
            steps = [interventions[i] for i in combo]
            total_delta = sum(s["score_delta"] for s in steps)
            cf = {
                "cf_id": len(counterfactuals) + 1,
                "steps": steps,
                "total_delta": round(total_delta, 4),
                "final_score": round(current_score + total_delta, 3),
                "reaches_target": (current_score + total_delta) >= threshold_score,
            }
            counterfactuals.append(cf)

            if len(counterfactuals) >= max_counterfactuals * 3:
                break

        if len(counterfactuals) >= max_counterfactuals * 3:
            break

    # Pilih yang paling diverse: prioritaskan yang mencapai target, lalu yang paling sedikit langkah
    reachable = [cf for cf in counterfactuals if cf["reaches_target"]]
    not_reachable = [cf for cf in counterfactuals if not cf["reaches_target"]]

    if reachable:
        selected = sorted(reachable, key=lambda cf: len(cf["steps"]))[
            :max_counterfactuals
        ]
    else:
        selected = sorted(not_reachable, key=lambda cf: -cf["total_delta"])[
            :max_counterfactuals
        ]

    for i, cf in enumerate(selected, start=1):
        cf["cf_id"] = i

    return selected


def plot_dice_counterfactual(
    job_title: str,
    current_score: float,
    threshold_score: float,
    counterfactuals: list,
    save_path: str,
):
    """
    Plot barchart yang menunjukkan setiap counterfactual:
    - Skor saat ini (garis merah)
    - Threshold top-K (garis hijau)
    - Skor setelah setiap counterfactual (bar biru)
    """
    if not counterfactuals:
        return

    fig, ax = plt.subplots(figsize=(9, max(3, len(counterfactuals) * 1.5 + 2)))

    cf_labels = [
        f"CF-{cf['cf_id']}\n({', '.join(s['feature'].split(': ')[-1][:20] for s in cf['steps'])})"
        for cf in counterfactuals
    ]
    cf_scores = [cf["final_score"] for cf in counterfactuals]
    colors = [
        "#2E7D32" if cf["reaches_target"] else "#F57F17" for cf in counterfactuals
    ]

    bars = ax.barh(cf_labels, cf_scores, color=colors, edgecolor="white", linewidth=0.5)
    ax.axvline(
        current_score,
        color="#C62828",
        linestyle="--",
        linewidth=1.5,
        label=f"Skor saat ini ({current_score:.2f})",
    )
    ax.axvline(
        threshold_score,
        color="#1B5E20",
        linestyle="-",
        linewidth=1.5,
        label=f"Target top-K ({threshold_score:.2f})",
    )

    for bar, score in zip(bars, cf_scores):
        ax.text(
            bar.get_width() + 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{score:.2f}",
            va="center",
            ha="left",
            fontsize=9,
        )

    ax.set_title(
        f"Counterfactual DICE: Intervensi untuk '{job_title}'\n"
        f"Hijau = mencapai target, Kuning = belum mencapai target",
        fontsize=10,
        pad=10,
    )
    ax.set_xlabel("Skor rekomendasi setelah intervensi")
    ax.legend(loc="lower right", fontsize=8)
    plt.tight_layout()

    out_dir = os.path.dirname(save_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    plt.savefig(save_path, dpi=150)
    plt.close(fig)


def generate_dice_report(
    job_contributions: dict,
    job_titles: dict,
    final_ranking: pd.DataFrame,
    matched_courses: pd.DataFrame,
    course_agg: pd.DataFrame,
    target_job_ids: list = None,
    top_k: int = 5,
    csv_path: str = "dice_counterfactuals.csv",
    plots_dir: str = "dice_plots",
    n_plots: int = 5,
    max_counterfactuals: int = 3,
    cert_weight_global: float = 1.0,
):
    """
    Fungsi utama yang dipanggil dari app.py atau streamlitApp.py.

    Parameters
    ----------
    job_contributions : dict
        {job_id: {feature_label: contribution_value}} - dari run_pipeline()
    job_titles : dict
        {job_id: job_title}
    final_ranking : pd.DataFrame
        Output final dari run_pipeline() (kolom: job_id, final_score, job_title, ...)
    matched_courses : pd.DataFrame
        pipeline_course_match_log.csv (kolom: matched_course_name, grade_weight, match_confidence)
    course_agg : pd.DataFrame
        course_job_aggregated.csv (kolom: course_name, job_id, course_job_score_max)
    target_job_ids : list, optional
        Job mana yang ingin dianalisis counterfactual-nya. Default: job di luar top_k.
    top_k : int
        Berapa job teratas yang menjadi "target" masuk. Default: 5.
    csv_path, plots_dir, n_plots, max_counterfactuals, cert_weight_global : ...
        Konfigurasi output.

    Returns
    -------
    pd.DataFrame
        DataFrame berisi semua counterfactual dalam format panjang
    """
    ranked = final_ranking.sort_values("final_score", ascending=False).reset_index(
        drop=True
    )
    threshold_score = (
        float(ranked.iloc[top_k - 1]["final_score"]) if len(ranked) >= top_k else 0.0
    )

    # Tentukan job yang mau di-generate counterfactual-nya
    if target_job_ids is None:
        # Default: job yang tepat di luar top-K (peringkat K+1 sampai K+n_plots)
        target_job_ids = ranked.iloc[top_k : top_k + n_plots]["job_id"].tolist()

    rows = []
    for rank, job_id in enumerate(target_job_ids, start=1):
        job_title = job_titles.get(job_id, str(job_id))
        score_row = ranked[ranked["job_id"] == job_id]
        if score_row.empty:
            continue
        current_score = float(score_row.iloc[0]["final_score"])

        print(
            f"  [{rank}/{len(target_job_ids)}] DICE for: {job_title} (score={current_score:.2f}, target={threshold_score:.2f})"
        )

        interventions = generate_interventions(
            job_id=job_id,
            job_title=job_title,
            current_score=current_score,
            threshold_score=threshold_score,
            job_contributions=job_contributions,
            matched_courses=matched_courses,
            course_agg=course_agg,
            cert_weight_global=cert_weight_global,
        )

        counterfactuals = generate_diverse_counterfactuals(
            interventions=interventions,
            current_score=current_score,
            threshold_score=threshold_score,
            max_counterfactuals=max_counterfactuals,
        )

        for cf in counterfactuals:
            for step_idx, step in enumerate(cf["steps"], start=1):
                rows.append(
                    {
                        "job_id": job_id,
                        "job_title": job_title,
                        "current_score": current_score,
                        "threshold_score": threshold_score,
                        "cf_id": cf["cf_id"],
                        "step_in_cf": step_idx,
                        "intervention_type": step["intervention_type"],
                        "feature": step["feature"],
                        "detail": step["detail"],
                        "score_delta": step["score_delta"],
                        "cf_final_score": cf["final_score"],
                        "cf_reaches_target": cf["reaches_target"],
                    }
                )

        if rank <= n_plots:
            plot_path = os.path.join(plots_dir, f"dice_cf_{rank:02d}_{job_id}.png")
            plot_dice_counterfactual(
                job_title, current_score, threshold_score, counterfactuals, plot_path
            )

    df = pd.DataFrame(rows)
    if not df.empty:
        df.to_csv(csv_path, index=False)
        print(f"Saved: {csv_path} ({len(df)} rows)")
        if n_plots:
            print(
                f"Saved DICE plots for top {min(n_plots, len(target_job_ids))} jobs -> {plots_dir}/"
            )
    else:
        print("No DICE counterfactuals generated.")

    return df


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate DICE counterfactual explanations"
    )
    parser.add_argument("--final_recommendations", default="final_recommendations.csv")
    parser.add_argument("--course_match_log", default="pipeline_course_match_log.csv")
    parser.add_argument("--course_agg", default="course_job_aggregated.csv")
    parser.add_argument(
        "--shap_csv",
        default="shap_explanations.csv",
        help="Digunakan untuk mengambil job_contributions dari CSV",
    )
    parser.add_argument("--top_k", type=int, default=5)
    parser.add_argument("--out_csv", default="dice_counterfactuals.csv")
    parser.add_argument("--out_plots_dir", default="dice_plots")
    parser.add_argument("--n_plots", type=int, default=5)
    args = parser.parse_args()

    final_ranking = pd.read_csv(args.final_recommendations)
    matched_courses = pd.read_csv(args.course_match_log)
    course_agg = pd.read_csv(args.course_agg)

    # Rekonstruksi job_contributions dari shap_explanations.csv
    # (kolom: job_id, job_title, feature, shap_value) - kita pakai sebagai proxy contributions
    job_contributions = {}
    job_titles = {}
    if os.path.exists(args.shap_csv):
        shap_df = pd.read_csv(args.shap_csv)
        for job_id, grp in shap_df.groupby("job_id"):
            job_titles[job_id] = grp.iloc[0]["job_title"]
            job_contributions[job_id] = dict(zip(grp["feature"], grp["shap_value"]))
    else:
        # Fallback: baca langsung dari final_ranking explanation
        for _, row in final_ranking.iterrows():
            jid = row["job_id"]
            job_titles[jid] = row["job_title"]
            job_contributions[jid] = {}

    print("=== DICE COUNTERFACTUAL EXPLANATIONS ===\n")
    generate_dice_report(
        job_contributions=job_contributions,
        job_titles=job_titles,
        final_ranking=final_ranking,
        matched_courses=matched_courses,
        course_agg=course_agg,
        top_k=args.top_k,
        csv_path=args.out_csv,
        plots_dir=args.out_plots_dir,
        n_plots=args.n_plots,
    )


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# DOMAIN-LEVEL DICE - berbasis feature vector terstruktur
# ---------------------------------------------------------------------------

DOMAIN_STEP_SIZE = {
    "ipk": 0.25,
    "jumlah_sertifikasi": 1,
    "data_competency": 0.10,
    "programming_competency": 0.10,
    "business_competency": 0.10,
    "security_competency": 0.10,
    "infra_competency": 0.10,
}

DOMAIN_STEP_LABEL = {
    "ipk": "Tingkatkan IPK sebesar {step:.2f} poin",
    "jumlah_sertifikasi": "Tambahkan {step:.0f} sertifikasi baru",
    "data_competency": "Tingkatkan Data Competency Score sebesar {pct:.0f}%",
    "programming_competency": "Tingkatkan Programming Competency Score sebesar {pct:.0f}%",
    "business_competency": "Tingkatkan Business Competency Score sebesar {pct:.0f}%",
    "security_competency": "Tingkatkan Security Competency Score sebesar {pct:.0f}%",
    "infra_competency": "Tingkatkan Infra Competency Score sebesar {pct:.0f}%",
}

DOMAIN_CONCRETE_TIPS = {
    "data_competency": [
        "Pelajari SQL & Python untuk analisis data",
        "Ambil Google Data Analytics Certificate",
        "Ikut kursus ETL / Data Engineering",
    ],
    "programming_competency": [
        "Pelajari framework web (React, Django, dll)",
        "Ikut bootcamp Machine Learning",
        "Tambah proyek coding di GitHub",
    ],
    "business_competency": [
        "Pelajari BPMN dan tools ERP",
        "Ambil PMP atau ITIL certification",
        "Ikut magang di bidang IT Governance",
    ],
    "security_competency": [
        "Ambil CompTIA Security+ atau CEH",
        "Pelajari ethical hacking dan pentesting",
        "Ikut kursus Cisco CyberOps",
    ],
    "infra_competency": [
        "Ambil AWS / Azure / GCP Fundamentals",
        "Pelajari Docker dan Kubernetes",
        "Ikut kursus Linux Administration",
    ],
    "jumlah_sertifikasi": [
        "Ambil sertifikat industri yang relevan dengan target karir Anda"
    ],
    "ipk": ["Fokus pada mata kuliah inti di semester berikutnya"],
}


def _compute_employability_score_pct(features, weights=None):
    if weights is None:
        weights = {
            "ipk": 0.15,
            "jumlah_sertifikasi": 0.10,
            "data_competency": 0.20,
            "programming_competency": 0.20,
            "business_competency": 0.15,
            "security_competency": 0.10,
            "infra_competency": 0.10,
        }
    score = 0.0
    score += weights["ipk"] * min(features.get("ipk", 0.0) / 4.0, 1.0)
    score += weights["jumlah_sertifikasi"] * min(
        features.get("jumlah_sertifikasi", 0) / 5.0, 1.0
    )
    for d in [
        "data_competency",
        "programming_competency",
        "business_competency",
        "security_competency",
        "infra_competency",
    ]:
        score += weights[d] * min(features.get(d, 0.0), 1.0)
    return round(score * 100, 1)


def generate_dice_domain_report(
    student_features,
    final_ranking,
    job_contributions,
    top_k=5,
    n_counterfactuals=3,
    csv_path="dice_domain_counterfactuals.csv",
    plots_dir="dice_domain_plots",
    n_plots=3,
):
    """DICE counterfactual berbasis domain feature vector untuk spesifik job."""
    import os
    import pandas as pd
    import matplotlib.pyplot as plt

    # 1. Tentukan target_score = skor dari pekerjaan peringkat top-K
    ranked = final_ranking.sort_values("final_score", ascending=False).reset_index(
        drop=True
    )
    if len(ranked) >= top_k:
        target_score = float(ranked.iloc[top_k - 1]["final_score"])
    else:
        target_score = (
            float(ranked.iloc[-1]["final_score"]) if not ranked.empty else 0.0
        )

    # 2. Ambil pekerjaan di luar top-K (sebagai target simulasi kita)
    out_of_top_k = (
        ranked.iloc[top_k : top_k + n_plots] if len(ranked) > top_k else ranked.head(0)
    )

    if out_of_top_k.empty:
        print(
            "  Semua pekerjaan masuk top-K, tidak ada counterfactual yang perlu digenerate."
        )
        return pd.DataFrame()

    from feature_engineering import _classify_course  # type: ignore

    all_rows = []

    print("\n  --- DICE Domain Counterfactuals (Per-Job) ---")

    for rank_idx, row in out_of_top_k.iterrows():
        job_id = row["job_id"]
        job_title = row["job_title"]
        current_score = float(row["final_score"])

        # Gap yang harus dikejar
        gap = target_score - current_score
        if gap <= 0:
            continue

        print(
            f"\n  Target Pekerjaan: {job_title} (Skor: {current_score:.2f} | Butuh: {target_score:.2f} | Gap: {gap:.2f})"
        )

        # 3. Hitung 'Domain Sensitivity' untuk pekerjaan ini
        raw_contribs = job_contributions.get(job_id, {})
        domain_totals = {
            "data_competency": 0.0,
            "programming_competency": 0.0,
            "business_competency": 0.0,
            "security_competency": 0.0,
            "infra_competency": 0.0,
        }

        cert_total = 0.0

        for label, contrib in raw_contribs.items():
            if label.startswith("MK: "):
                course_name = label.replace("MK: ", "")
                domain = _classify_course(course_name)
                if domain and f"{domain}_competency" in domain_totals:
                    domain_totals[f"{domain}_competency"] += contrib
            elif label.startswith("Sertifikat: "):
                cert_total += contrib

        # Estimasi kontribusi jika ambil 1 sertifikat (berbasis rata-rata kontribusi sertifikat,
        # atau heuristic 1.50 jika belum punya sertifikat sama sekali)
        avg_cert_contrib = cert_total / max(
            student_features.get("jumlah_sertifikasi", 1), 1
        )
        if avg_cert_contrib == 0.0:
            avg_cert_contrib = 1.50  # fallback heuristic

        # 4. Generate single steps
        single_steps = []
        for feat_key, step in DOMAIN_STEP_SIZE.items():
            current_val = student_features.get(feat_key, 0.0)

            if feat_key == "ipk":
                continue  # Kita abaikan IPK karena IPK dampaknya terlalu global dan lambat perubahannya

            if feat_key == "jumlah_sertifikasi":
                delta_score = avg_cert_contrib * step
                label = DOMAIN_STEP_LABEL[feat_key].format(step=step, pct=step)
            else:
                # Untuk domain kompetensi
                new_val = min(current_val + step, 1.0)
                if new_val <= current_val + 1e-6:
                    continue

                # Sensitivitas: Jika nilai saat ini X menyumbang Y,
                # maka kenaikan Z diproyeksikan menyumbang (Z/X)*Y.
                # Jika X = 0 (belum ada MK diambil di domain ini),
                # fallback ke asumsi: ambil 1 MK bernilai A (0.85) menyumbang rata-rata 1.0 poin
                if current_val > 0.01:
                    delta_score = (step / current_val) * domain_totals[feat_key]
                else:
                    delta_score = (step / 0.85) * 1.0  # Heuristic 1.0 poin per MK A

                pct_step = step * 100
                label = DOMAIN_STEP_LABEL[feat_key].format(step=step, pct=pct_step)

            single_steps.append(
                {
                    "feat_key": feat_key,
                    "label": label,
                    "delta_score": round(delta_score, 3),
                    "reaches_target": current_score + delta_score >= target_score,
                    "concrete_tips": DOMAIN_CONCRETE_TIPS.get(feat_key, []),
                }
            )

        single_steps.sort(key=lambda x: -x["delta_score"])

        # 5. Build counterfactuals
        counterfactuals = []

        # Best single step
        if single_steps:
            counterfactuals.append(
                {
                    "cf_id": 1,
                    "steps": [single_steps[0]],
                    "total_delta": single_steps[0]["delta_score"],
                    "final_score": current_score + single_steps[0]["delta_score"],
                    "reaches_target": single_steps[0]["reaches_target"],
                }
            )

        # Kombinasi 2 steps jika belum capai target
        if (
            not any(cf["reaches_target"] for cf in counterfactuals)
            and len(single_steps) >= 2
        ):
            combined_delta = (
                single_steps[0]["delta_score"] + single_steps[1]["delta_score"]
            )
            counterfactuals.append(
                {
                    "cf_id": 2,
                    "steps": [single_steps[0], single_steps[1]],
                    "total_delta": combined_delta,
                    "final_score": current_score + combined_delta,
                    "reaches_target": current_score + combined_delta >= target_score,
                }
            )

        # Save to rows and print
        for cf in counterfactuals:
            steps_str = " + ".join(s["label"] for s in cf["steps"])
            status = "(masuk Top-K)" if cf["reaches_target"] else "(belum cukup)"
            print(f"    CF-{cf['cf_id']}: {steps_str}")
            print(f"           Skor Proyeksi: {cf['final_score']:.2f} {status}")

            for i, step in enumerate(cf["steps"], start=1):
                all_rows.append(
                    {
                        "job_id": job_id,
                        "job_title": job_title,
                        "current_score": current_score,
                        "target_score": target_score,
                        "cf_id": cf["cf_id"],
                        "step_in_cf": i,
                        "intervention": step["label"],
                        "feature": step["feat_key"],
                        "projected_score": cf["final_score"],
                        "reaches_target": cf["reaches_target"],
                        "concrete_tips": " | ".join(step.get("concrete_tips", [])),
                    }
                )

        # Plot for this job
        if n_plots > 0 and counterfactuals:
            os.makedirs(plots_dir, exist_ok=True)
            labels = [
                " + ".join(s["label"] for s in cf["steps"]) for cf in counterfactuals
            ]
            labels = [l[:40] + "..." if len(l) > 40 else l for l in labels]
            scores = [cf["final_score"] for cf in counterfactuals]
            colors = [
                "#2E7D32" if cf["reaches_target"] else "#F57F17"
                for cf in counterfactuals
            ]

            fig, ax = plt.subplots(figsize=(10, max(3, len(counterfactuals) * 1.5 + 1)))
            bars = ax.barh(labels, scores, color=colors, edgecolor="white")
            ax.axvline(
                current_score,
                color="#C62828",
                linestyle="--",
                linewidth=1.5,
                label=f"Skor Saat Ini ({current_score:.2f})",
            )
            ax.axvline(
                target_score,
                color="#1B5E20",
                linestyle="-",
                linewidth=1.5,
                label=f"Target Top-{top_k} ({target_score:.2f})",
            )

            # Set xlim slightly beyond target_score
            max_plot_score = max(target_score, max(scores, default=0)) * 1.2
            ax.set_xlim(0, max_plot_score)

            for bar, score in zip(bars, scores):
                ax.text(
                    bar.get_width() + 0.05,
                    bar.get_y() + bar.get_height() / 2,
                    f"{score:.2f}",
                    va="center",
                    ha="left",
                    fontsize=9,
                )

            ax.set_title(
                f"DICE Domain: Rekomendasi Peningkatan untuk '{job_title}'",
                fontsize=10,
                pad=10,
            )
            ax.set_xlabel("Job Match Score")
            ax.legend(loc="lower right", fontsize=8)
            plt.tight_layout()
            plot_path = os.path.join(
                plots_dir, f"dice_domain_{rank_idx:02d}_{job_id}.png"
            )
            plt.savefig(plot_path, dpi=150)
            plt.close(fig)

    df = pd.DataFrame(all_rows)
    if not df.empty:
        df.to_csv(csv_path, index=False)
        print(f"\n  Saved: {csv_path} ({len(df)} rows)")

    return df
