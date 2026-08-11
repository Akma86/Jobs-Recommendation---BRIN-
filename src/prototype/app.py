import os
import sys
import argparse

# Add sibling directories to path to import from them
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR   = os.path.dirname(SCRIPT_DIR)
sys.path.append(os.path.join(CODE_DIR, "RankingJob"))
sys.path.append(os.path.join(CODE_DIR, "Explainable AI"))

# Import from RankingJob
# type: ignore
from full_pipeline import run_pipeline, JOBS_CSV_PATH, COURSE_CLO_CSV_PATH, TOP_N_OUTPUT
# type: ignore
from feature_engineering import build_student_features

# Import from Explainable AI
# type: ignore
from shap_explain import generate_shap_report, generate_shap_domain_report
# type: ignore
from lime_explain import generate_lime_report
# type: ignore
from dice_explain import generate_dice_report, generate_dice_domain_report
# type: ignore
from narrate_explanations import generate_narrations


def main():
    parser = argparse.ArgumentParser(description="Centralized entry point for Ranking and XAI")
    parser.add_argument("--khs",       required=True, help="transcript_parsed.csv from parse_input.py")
    parser.add_argument("--certs",     required=False, default=None, help="certificates_parsed.csv (optional)")
    parser.add_argument("--jobs",      default=JOBS_CSV_PATH)
    parser.add_argument("--course-clo", default=COURSE_CLO_CSV_PATH)
    parser.add_argument("--skip-xai",  action="store_true", help="Skip all XAI generation")
    parser.add_argument("--xai-mode",  default="shap",
                        choices=["shap", "shap-domain", "lime", "dice", "dice-domain", "all"],
                        help=(
                            "Pilih metode XAI yang dijalankan:\n"
                            "  shap        : SHAP per mata kuliah / sertifikat (default)\n"
                            "  shap-domain : SHAP berbasis domain kompetensi terstruktur\n"
                            "  lime        : LIME local explanations per job\n"
                            "  dice        : DICE counterfactual per mata kuliah\n"
                            "  dice-domain : DICE dengan Final Employability Score (persen)\n"
                            "  all         : jalankan semua metode XAI (SHAP + LIME + DiCE)"
                        ))
    parser.add_argument("--narrate",   action="store_true",
                        help="Generate natural language narrations using LLM (requires ANTHROPIC_API_KEY)")
    args = parser.parse_args()

    # -----------------------------------------------------------------------
    # 1. Run the Ranking Pipeline
    # -----------------------------------------------------------------------
    print("======================================================")
    print("=== STARTING RANKING PIPELINE (RankingJob) ===")
    print("======================================================")

    final_ranking, job_contributions = run_pipeline(
        khs_path=args.khs,
        certs_path=args.certs,
        jobs_path=args.jobs,
        course_clo_path=args.course_clo,
    )

    final_ranking.head(TOP_N_OUTPUT).to_csv("final_recommendations.csv", index=False)
    print(f"\n[DONE] Saved: final_recommendations.csv (top {TOP_N_OUTPUT})")

    # -----------------------------------------------------------------------
    # 2. Feature Engineering (selalu dijalankan, ringan dan cepat)
    # -----------------------------------------------------------------------
    import pandas as pd
    khs_df   = pd.read_csv(args.khs)
    certs_df = pd.read_csv(args.certs) if args.certs and os.path.exists(args.certs) else None
    student_features = build_student_features(khs_df, certs_df)

    # -----------------------------------------------------------------------
    # 3. XAI Layer
    # -----------------------------------------------------------------------
    if args.skip_xai:
        print("\nSkipping XAI generation as requested.")
    else:
        top_job_ids = final_ranking.head(TOP_N_OUTPUT)["job_id"].tolist()
        job_titles  = dict(zip(final_ranking["job_id"], final_ranking["job_title"]))
        mode        = args.xai_mode

        # --- SHAP (per MK/sertifikat) ---
        if mode in ("shap", "all"):
            print("\n======================================================")
            print("=== XAI: SHAP (per Mata Kuliah / Sertifikat) ===")
            print("======================================================")
            generate_shap_report(
                job_contributions, job_titles, top_job_ids,
                csv_path="shap_explanations.csv",
                plots_dir="shap_plots",
                n_plots=5,
            )

        # --- LIME (local explanations) ---
        if mode in ("lime", "all"):
            print("\n======================================================")
            print("=== XAI: LIME (Local Interpretable Explanations) ===")
            print("======================================================")
            generate_lime_report(
                job_contributions=job_contributions,
                job_titles=job_titles,
                top_job_ids=top_job_ids,
                csv_path="lime_explanations.csv",
                plots_dir="lime_plots",
                n_plots=5,
            )

        # --- SHAP Domain ---
        if mode in ("shap-domain", "all"):
            print("\n======================================================")
            print("=== XAI: SHAP Domain (IPK & Competency Scores) ===")
            print("======================================================")
            generate_shap_domain_report(
                student_features=student_features,
                job_contributions=job_contributions,
                job_titles=job_titles,
                top_job_ids=top_job_ids,
                csv_path="shap_domain_explanations.csv",
                plots_dir="shap_domain_plots",
                n_plots=5,
            )

        # --- DICE (per MK) ---
        if mode in ("dice", "all"):
            print("\n======================================================")
            print("=== XAI: DICE Counterfactual (per Mata Kuliah) ===")
            print("======================================================")
            import pandas as pd
            course_agg      = pd.read_csv("course_job_aggregated.csv") if os.path.exists("course_job_aggregated.csv") else pd.DataFrame()
            matched_courses = pd.read_csv("pipeline_course_match_log.csv") if os.path.exists("pipeline_course_match_log.csv") else pd.DataFrame()
            if not course_agg.empty and not matched_courses.empty:
                generate_dice_report(
                    job_contributions=job_contributions,
                    job_titles=job_titles,
                    final_ranking=final_ranking,
                    matched_courses=matched_courses,
                    course_agg=course_agg,
                    csv_path="dice_counterfactuals.csv",
                    plots_dir="dice_plots",
                    n_plots=5,
                )

        # --- DICE Domain ---
        if mode in ("dice-domain", "all"):
            print("\n======================================================")
            print("=== XAI: DICE Domain (Per Pekerjaan Spesifik) ===")
            print("======================================================")
            generate_dice_domain_report(
                student_features=student_features,
                final_ranking=final_ranking,
                job_contributions=job_contributions,
                top_k=5,
                csv_path="dice_domain_counterfactuals.csv",
                plots_dir="dice_domain_plots",
                n_plots=3,
            )

        # --- LLM Narration ---
        if args.narrate:
            print("\n======================================================")
            print("=== STARTING LLM NARRATION (Claude) ===")
            print("======================================================")
            if os.path.exists("shap_explanations.csv"):
                shap_df = pd.read_csv("shap_explanations.csv")
            else:
                shap_df = pd.DataFrame()
            narrated_df = generate_narrations(final_ranking, shap_df, backend="anthropic", top_n=5)
            narrated_df.to_csv("final_recommendations_narrated.csv", index=False)
            print("[DONE] Saved: final_recommendations_narrated.csv")
            final_ranking = narrated_df

    # -----------------------------------------------------------------------
    # 4. Print Summary
    # -----------------------------------------------------------------------
    print("\n======================================================")
    print("=== TOP 5 RECOMMENDATIONS ===")
    print("======================================================")
    for _, row in final_ranking.head(5).iterrows():
        print(f"\n[{row['final_score']:.3f}] {row['job_title']} @ {row['job_company']}")
        if "llm_narration" in row:
            print(f"   Why: {row['llm_narration']}")
        else:
            print(f"   Why: {row['explanation']}")


if __name__ == "__main__":
    main()
