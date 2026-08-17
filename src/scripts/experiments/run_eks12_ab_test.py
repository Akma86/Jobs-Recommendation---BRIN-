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
    print("EKS12: A/B Testing + Full XAI (SHAP Waterfall + Dynamic DiCE Counterfactuals)")
    print("==========================================================================")

    khs_dir = os.path.join(root_dir, "data", "Mahasiswa", "generated_markdown_khs")
    certs_dir = os.path.join(root_dir, "data", "Mahasiswa", "generated_markdown_certificates")
    eks12_dir = os.path.join(root_dir, "results", "Eksperimen_XAI", "EKS12_AB_Test")
    os.makedirs(eks12_dir, exist_ok=True)
    
    parse_script = os.path.join(root_dir, "src", "kpbrin", "data", "parse_input.py")

    khs_files = glob.glob(os.path.join(khs_dir, "*_KHS.md"))
    # Filter only AB test students with full names
    named_keywords = ["Siti_Rahma", "Rizky_Maulana", "Budi_Santoso", "Bayu_Setiawan", "Andi_Wijaya", "Kevin_Aditya", "Nadia_Putri", "Farhan_Hidayat", "Dewi_Lestari", "Ilham_Saputra"]
    khs_files = [f for f in khs_files if any(k in f for k in named_keywords)]
    khs_files.sort()
    
    summary_path = os.path.join(eks12_dir, "EKS12_Summary_ABTest.csv")
    dice_summary_path = os.path.join(eks12_dir, "EKS12_DiCE_AllStudents_Summary.csv")
    shap_summary_path = os.path.join(eks12_dir, "EKS12_SHAP_AllStudents_Summary.csv")
    
    # Initialize summary CSVs
    pd.DataFrame(columns=["track", "student_name", "human_name", "type", "job_title", "final_score"]).to_csv(summary_path, index=False)
    pd.DataFrame(columns=["student_name", "human_name", "track", "type", "job_id", "job_title", "cf_id", "step_in_cf", "intervention_type", "feature", "detail", "score_delta", "cf_final_score", "cf_reaches_target"]).to_csv(dice_summary_path, index=False)
    pd.DataFrame(columns=["student_name", "human_name", "track", "type", "job_id", "job_title", "feature", "shap_value", "base_value"]).to_csv(shap_summary_path, index=False)

    for idx, khs_file in enumerate(khs_files, 1):
        filename = os.path.basename(khs_file)
        student_name = filename.replace("_KHS.md", "")
        human_name, track, student_type = parse_student_metadata(student_name)
        
        print(f"\n[{idx}/{len(khs_files)}] Processing Student: {student_name} ({human_name} - {track} [{student_type}])")
        
        student_dir = os.path.join(eks12_dir, student_name)
        os.makedirs(student_dir, exist_ok=True)
        
        student_cert_dir = os.path.join(certs_dir, student_name)
        
        # 1. Parse KHS and Certificates
        parse_cmd = ["python", parse_script, "--khs", khs_file, "--cert_dir", student_cert_dir]
        subprocess.run(parse_cmd, cwd=student_dir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        khs_csv = os.path.join(student_dir, "transcript_parsed.csv")
        original_certs_csv = os.path.join(student_dir, "certificates_parsed.csv")
        
        # 2. Run Main Recommendation Pipeline
        cwd_orig = os.getcwd()
        os.chdir(student_dir)
        try:
            df_after, job_contributions = run_pipeline(
                khs_path=khs_csv,
                certs_path=original_certs_csv,
                jobs_path=JOBS_CSV_PATH,
                course_clo_path=COURSE_CLO_CSV_PATH
            )
            df_after.to_csv("recommendations.csv", index=False)
            job_titles_dict = dict(zip(df_after["job_id"], df_after["job_title"]))
            top5_job_ids = df_after.head(5)["job_id"].tolist()
            
            # 3. Run SHAP Waterfall Explanations
            print(f"  [XAI SHAP] Generating SHAP waterfall plots for {student_name}...")
            shap_df = generate_shap_report(
                job_contributions=job_contributions,
                job_titles=job_titles_dict,
                top_job_ids=top5_job_ids,
                csv_path="shap_explanations.csv",
                plots_dir="shap_plots",
                n_plots=3
            )
            if not shap_df.empty:
                shap_df["student_name"] = student_name
                shap_df["human_name"] = human_name
                shap_df["track"] = track
                shap_df["type"] = student_type
                shap_df.to_csv(shap_summary_path, mode="a", header=False, index=False)
            
            # 4. Run DiCE Counterfactual Explanations with Dynamic Online Course Catalog
            print(f"  [XAI DiCE] Generating DiCE counterfactuals with Online Course catalog for {student_name}...")
            matched_courses = pd.read_csv("pipeline_course_match_log.csv")
            course_agg = pd.read_csv("course_job_aggregated.csv")
            
            dice_df = generate_dice_report(
                job_contributions=job_contributions,
                job_titles=job_titles_dict,
                final_ranking=df_after,
                matched_courses=matched_courses,
                course_agg=course_agg,
                target_job_ids=top5_job_ids,
                top_k=5,
                csv_path="dice_counterfactuals.csv",
                plots_dir="dice_plots",
                n_plots=3,
                max_counterfactuals=3,
                cert_weight_global=1.0
            )
            
            if not dice_df.empty:
                dice_df["student_name"] = student_name
                dice_df["human_name"] = human_name
                dice_df["track"] = track
                dice_df["type"] = student_type
                dice_df.to_csv(dice_summary_path, mode="a", header=False, index=False)
                
        finally:
            os.chdir(cwd_orig)

        # 5. Save Top 5 Recommendations
        top_jobs = df_after.head(5)
        records = []
        for _, row in top_jobs.iterrows():
            records.append({
                "track": track,
                "student_name": student_name,
                "human_name": human_name,
                "type": student_type, # Bagus / Jelek
                "job_title": row['job_title'],
                "final_score": round(row['final_score'], 4)
            })
            
        df_new = pd.DataFrame(records)
        df_new.to_csv(summary_path, mode="a", header=False, index=False)
        print(f"  [DONE] Completed recommendation, SHAP, & DiCE for {student_name}")

    print("\n==========================================================================")
    print("EKS12 COMPLETED SUCCESSFULLY WITH SHAP & DiCE!")
    print(f"Summary Saved to: {summary_path}")
    print(f"SHAP Summary Saved to: {shap_summary_path}")
    print(f"DiCE Summary Saved to: {dice_summary_path}")
    print("==========================================================================")

if __name__ == "__main__":
    main()
