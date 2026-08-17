import os
import glob
import subprocess
import pandas as pd
import sys

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.join(root_dir, "src"))

from kpbrin.core.full_pipeline import run_pipeline, JOBS_CSV_PATH, COURSE_CLO_CSV_PATH
from kpbrin.xai.dice_explain import generate_dice_report
from kpbrin.xai.shap_explain import generate_shap_report
from kpbrin.data.parse_input import parse_khs, parse_certificates_for_student

def parse_student_metadata(student_name):
    """
    Extract human name, track code, and type (Bagus/Jelek) from student identifier.
    e.g. 'Siti_Rahma_ML_Bagus' -> ('Siti Rahma', 'ML', 'Bagus')
    """
    student_type = "Bagus" if "_Bagus" in student_name else "Jelek"
    base = student_name.replace("_Bagus", "").replace("_Jelek", "")
    parts = base.split("_")
    
    if len(parts) >= 2:
        track = parts[-1]
        human_name = " ".join(parts[:-1])
    else:
        track = parts[0]
        human_name = parts[0]
        
    return human_name, track, student_type

def main():
    print("==========================================================================")
    print("EKS12: A/B Testing with Structured Before/ & After/ Subfolders")
    print("Full XAI: Recommendations + SHAP Waterfall + Dynamic DiCE Counterfactuals")
    print("==========================================================================")

    khs_dir = os.path.join(root_dir, "data", "Mahasiswa", "generated_markdown_khs")
    certs_dir = os.path.join(root_dir, "data", "Mahasiswa", "generated_markdown_certificates")
    eks12_dir = os.path.join(root_dir, "results", "Eksperimen_XAI", "EKS12_AB_Test")
    os.makedirs(eks12_dir, exist_ok=True)

    khs_files = glob.glob(os.path.join(khs_dir, "*_KHS.md"))
    named_keywords = ["Siti_Rahma", "Rizky_Maulana", "Budi_Santoso", "Bayu_Setiawan", "Andi_Wijaya", "Kevin_Aditya", "Nadia_Putri", "Farhan_Hidayat", "Dewi_Lestari", "Ilham_Saputra"]
    khs_files = [f for f in khs_files if any(k in f for k in named_keywords) and ("_Bagus" in f or "_Jelek" in f)]
    khs_files.sort()
    
    summary_path = os.path.join(eks12_dir, "EKS12_Summary_BeforeAfter.csv")
    dice_summary_path = os.path.join(eks12_dir, "EKS12_DiCE_AllStudents_Summary.csv")
    shap_summary_path = os.path.join(eks12_dir, "EKS12_SHAP_AllStudents_Summary.csv")
    
    # Initialize summary CSVs
    pd.DataFrame(columns=["track", "student_name", "human_name", "type", "phase", "job_id", "job_title", "rank", "final_score"]).to_csv(summary_path, index=False)
    pd.DataFrame(columns=["student_name", "human_name", "track", "type", "phase", "job_id", "job_title", "cf_id", "step_in_cf", "intervention_type", "feature", "detail", "score_delta", "cf_final_score", "cf_reaches_target"]).to_csv(dice_summary_path, index=False)
    pd.DataFrame(columns=["student_name", "human_name", "track", "type", "phase", "job_id", "job_title", "feature", "shap_value", "base_value"]).to_csv(shap_summary_path, index=False)

    for idx, khs_file in enumerate(khs_files, 1):
        filename = os.path.basename(khs_file)
        student_name = filename.replace("_KHS.md", "")
        human_name, track, student_type = parse_student_metadata(student_name)
        
        print(f"\n[{idx}/{len(khs_files)}] Processing Student: {student_name} ({human_name} - {track} [{student_type}])")
        
        student_dir = os.path.join(eks12_dir, student_name)
        before_dir = os.path.join(student_dir, "Before")
        after_dir = os.path.join(student_dir, "After")
        os.makedirs(before_dir, exist_ok=True)
        os.makedirs(after_dir, exist_ok=True)
        
        student_cert_dir = os.path.join(certs_dir, student_name)
        
        # -------------------------------------------------------------
        # PHASE 1: BEFORE (Matkul Saja / No Certificates)
        # -------------------------------------------------------------
        print(f"  >>> [PHASE 1: BEFORE] Parsing KHS & running pipeline...")
        df_khs_parsed = parse_khs(khs_file)
        khs_csv_before = os.path.join(before_dir, "transcript_parsed.csv")
        df_khs_parsed.to_csv(khs_csv_before, index=False)
        
        cwd_orig = os.getcwd()
        os.chdir(before_dir)
        try:
            df_before, job_contribs_before = run_pipeline(
                khs_path=khs_csv_before,
                certs_path=None,
                jobs_path=JOBS_CSV_PATH,
                course_clo_path=COURSE_CLO_CSV_PATH
            )
            df_before.to_csv("recommendations.csv", index=False)
            job_titles_before = dict(zip(df_before["job_id"], df_before["job_title"]))
            top5_job_ids_before = df_before.head(5)["job_id"].tolist()
            
            # SHAP Before
            shap_df_before = generate_shap_report(
                job_contributions=job_contribs_before,
                job_titles=job_titles_before,
                top_job_ids=top5_job_ids_before,
                csv_path="shap_explanations.csv",
                plots_dir="shap_plots",
                n_plots=3
            )
            if not shap_df_before.empty:
                shap_df_before["student_name"] = student_name
                shap_df_before["human_name"] = human_name
                shap_df_before["track"] = track
                shap_df_before["type"] = student_type
                shap_df_before["phase"] = "Before"
                shap_df_before.to_csv(shap_summary_path, mode="a", header=False, index=False)
                
            # DiCE Before
            matched_courses_b = pd.read_csv("pipeline_course_match_log.csv")
            course_agg_b = pd.read_csv("course_job_aggregated.csv")
            dice_df_before = generate_dice_report(
                job_contributions=job_contribs_before,
                job_titles=job_titles_before,
                final_ranking=df_before,
                matched_courses=matched_courses_b,
                course_agg=course_agg_b,
                target_job_ids=top5_job_ids_before,
                top_k=5,
                csv_path="dice_counterfactuals.csv",
                plots_dir="dice_plots",
                n_plots=3,
                max_counterfactuals=3,
                cert_weight_global=1.0
            )
            if not dice_df_before.empty:
                dice_df_before["student_name"] = student_name
                dice_df_before["human_name"] = human_name
                dice_df_before["track"] = track
                dice_df_before["type"] = student_type
                dice_df_before["phase"] = "Before"
                dice_df_before.to_csv(dice_summary_path, mode="a", header=False, index=False)
                
        finally:
            os.chdir(cwd_orig)
            
        # Record Top 5 Before
        top5_b_records = []
        for rank, row in enumerate(df_before.head(5).itertuples(), 1):
            top5_b_records.append({
                "track": track,
                "student_name": student_name,
                "human_name": human_name,
                "type": student_type,
                "phase": "Before",
                "job_id": row.job_id,
                "job_title": row.job_title,
                "rank": rank,
                "final_score": round(row.final_score, 4)
            })
        pd.DataFrame(top5_b_records).to_csv(summary_path, mode="a", header=False, index=False)

        # -------------------------------------------------------------
        # PHASE 2: AFTER (Matkul + 4-5 Assigned Certificates)
        # -------------------------------------------------------------
        print(f"  >>> [PHASE 2: AFTER] Parsing Certificates & running pipeline...")
        khs_csv_after = os.path.join(after_dir, "transcript_parsed.csv")
        df_khs_parsed.to_csv(khs_csv_after, index=False)
        
        df_certs_parsed = parse_certificates_for_student(student_cert_dir)
        certs_csv_after = os.path.join(after_dir, "certificates_parsed.csv")
        df_certs_parsed.to_csv(certs_csv_after, index=False)
        
        os.chdir(after_dir)
        try:
            df_after, job_contribs_after = run_pipeline(
                khs_path=khs_csv_after,
                certs_path=certs_csv_after,
                jobs_path=JOBS_CSV_PATH,
                course_clo_path=COURSE_CLO_CSV_PATH
            )
            df_after.to_csv("recommendations.csv", index=False)
            job_titles_after = dict(zip(df_after["job_id"], df_after["job_title"]))
            top5_job_ids_after = df_after.head(5)["job_id"].tolist()
            
            # SHAP After
            shap_df_after = generate_shap_report(
                job_contributions=job_contribs_after,
                job_titles=job_titles_after,
                top_job_ids=top5_job_ids_after,
                csv_path="shap_explanations.csv",
                plots_dir="shap_plots",
                n_plots=3
            )
            if not shap_df_after.empty:
                shap_df_after["student_name"] = student_name
                shap_df_after["human_name"] = human_name
                shap_df_after["track"] = track
                shap_df_after["type"] = student_type
                shap_df_after["phase"] = "After"
                shap_df_after.to_csv(shap_summary_path, mode="a", header=False, index=False)
                
            # DiCE After
            matched_courses_a = pd.read_csv("pipeline_course_match_log.csv")
            course_agg_a = pd.read_csv("course_job_aggregated.csv")
            dice_df_after = generate_dice_report(
                job_contributions=job_contribs_after,
                job_titles=job_titles_after,
                final_ranking=df_after,
                matched_courses=matched_courses_a,
                course_agg=course_agg_a,
                target_job_ids=top5_job_ids_after,
                top_k=5,
                csv_path="dice_counterfactuals.csv",
                plots_dir="dice_plots",
                n_plots=3,
                max_counterfactuals=3,
                cert_weight_global=1.0
            )
            if not dice_df_after.empty:
                dice_df_after["student_name"] = student_name
                dice_df_after["human_name"] = human_name
                dice_df_after["track"] = track
                dice_df_after["type"] = student_type
                dice_df_after["phase"] = "After"
                dice_df_after.to_csv(dice_summary_path, mode="a", header=False, index=False)
                
        finally:
            os.chdir(cwd_orig)
            
        # Record Top 5 After
        top5_a_records = []
        for rank, row in enumerate(df_after.head(5).itertuples(), 1):
            top5_a_records.append({
                "track": track,
                "student_name": student_name,
                "human_name": human_name,
                "type": student_type,
                "phase": "After",
                "job_id": row.job_id,
                "job_title": row.job_title,
                "rank": rank,
                "final_score": round(row.final_score, 4)
            })
        pd.DataFrame(top5_a_records).to_csv(summary_path, mode="a", header=False, index=False)
        print(f"  [DONE] Completed Before/ & After/ for {student_name}")

    print("\n==========================================================================")
    print("EKS12 COMPLETED SUCCESSFULLY WITH BEFORE & AFTER SUBFOLDERS!")
    print(f"Summary Saved to: {summary_path}")
    print(f"SHAP Summary Saved to: {shap_summary_path}")
    print(f"DiCE Summary Saved to: {dice_summary_path}")
    print("==========================================================================")

if __name__ == "__main__":
    main()
