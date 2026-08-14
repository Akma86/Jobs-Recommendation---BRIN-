import os
import glob
import subprocess
import pandas as pd
import time

def main():
    print("============================================================")
    print("EKS10: Batch DiCE Counterfactuals (Before vs After) for ALL Students")
    print("============================================================")

    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    khs_dir = os.path.join(root_dir, "data", "generated_markdown_khs")
    certs_dir = os.path.join(root_dir, "data", "generated_markdown_certificates")
    
    # We will run the pipeline in a dedicated temp folder per student to avoid clashes
    eks10_dir = os.path.join(root_dir, "results", "Eksperimen_XAI", "EKS10_AllMahasiswa")
    os.makedirs(eks10_dir, exist_ok=True)
    
    parse_script = os.path.join(root_dir, "src", "RankingJob", "parse_input.py")
    app_script = os.path.join(root_dir, "src", "RankingJob", "full_pipeline.py") # fallback? Wait no, I restored app.py!
    # Let me use app_script as src/prototype/app.py because it exists now
    app_script = os.path.join(root_dir, "src", "prototype", "app.py")

    khs_files = glob.glob(os.path.join(khs_dir, "*_KHS.md"))
    
    summary_path = os.path.join(eks10_dir, "EKS10_Summary.csv")
    if not os.path.exists(summary_path):
        pd.DataFrame(columns=["student_name", "target_job", "recommended_cert", "rank_before", "rank_after", "score_before", "score_after", "score_increase"]).to_csv(summary_path, index=False)

    for idx, khs_file in enumerate(khs_files, 1):
        filename = os.path.basename(khs_file)
        student_name = filename.replace("_KHS.md", "")
        print(f"\n[{idx}/{len(khs_files)}] Processing Student: {student_name}")
        
        student_dir = os.path.join(eks10_dir, student_name)
        os.makedirs(student_dir, exist_ok=True)
        
        # Check if already processed in summary
        df_summary = pd.read_csv(summary_path)
        if student_name in df_summary['student_name'].values:
            print(f"  [INFO] Skipping {student_name}, already in summary.")
            continue
            
        student_cert_dir = os.path.join(certs_dir, student_name)
        has_certs = os.path.exists(student_cert_dir) and len(os.listdir(student_cert_dir)) > 0
        
        # 1. Parsing Inputs
        parse_cmd = ["python", parse_script, "--khs", khs_file]
        if has_certs:
            parse_cmd.extend(["--cert_dir", student_cert_dir])
            
        subprocess.run(parse_cmd, cwd=student_dir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        khs_csv = os.path.join(student_dir, "transcript_parsed.csv")
        original_certs_csv = os.path.join(student_dir, "certificates_parsed.csv")
        
        # 2. Phase 1: BEFORE (Run DiCE)
        print(f"  -> Running Phase 1 (Before) with DiCE XAI...")
        app_cmd_before = ["python", app_script, "--khs", khs_csv, "--xai-mode", "dice"]
        if os.path.exists(original_certs_csv):
            app_cmd_before.extend(["--certs", original_certs_csv])
            
        subprocess.run(app_cmd_before, cwd=student_dir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        before_recs_file = os.path.join(student_dir, "final_recommendations.csv")
        dice_cf_file = os.path.join(student_dir, "dice_counterfactuals.csv")
        
        if not os.path.exists(before_recs_file) or not os.path.exists(dice_cf_file):
            print(f"  [ERROR] Pipeline failed to generate outputs for {student_name}.")
            continue
            
        df_before = pd.read_csv(before_recs_file)
        df_dice = pd.read_csv(dice_cf_file)
        
        # 3. Extract Best Intervention
        target_job_id = None
        target_job_title = None
        recommended_cert = None
        
        for _, row in df_dice.iterrows():
            if row['intervention_type'] == 'add_certificate':
                target_job_id = row['job_id']
                target_job_title = row['job_title']
                recommended_cert = row['feature'].replace("Sertifikat: ", "")
                break
                
        if not recommended_cert:
            print(f"  [WARN] No certificate intervention found for {student_name}.")
            continue
            
        print(f"  -> DiCE Target Job: {target_job_title}")
        print(f"  -> DiCE Recommendation: Add '{recommended_cert}'")
        
        # Determine Before Rank and Score
        try:
            rank_before = df_before.index[df_before['job_id'] == target_job_id].tolist()[0] + 1
            score_before = df_before[df_before['job_id'] == target_job_id].iloc[0]['final_score']
        except IndexError:
            rank_before = -1
            score_before = 0.0
            
        # 4. Create Dummy Certificate combined with original
        dummy_certs_csv = os.path.join(student_dir, "dummy_certificates.csv")
        
        if os.path.exists(original_certs_csv):
            df_certs = pd.read_csv(original_certs_csv)
        else:
            df_certs = pd.DataFrame(columns=["title", "issuer"])
            
        new_row = pd.DataFrame([{"title": recommended_cert, "issuer": "DummyIssuer (DiCE Sim)"}])
        df_certs = pd.concat([df_certs, new_row], ignore_index=True)
        df_certs.to_csv(dummy_certs_csv, index=False)
        
        # 5. Phase 2: AFTER
        print(f"  -> Running Phase 2 (After) with new dummy certificate...")
        app_cmd_after = ["python", app_script, "--khs", khs_csv, "--certs", dummy_certs_csv, "--skip-xai"]
        subprocess.run(app_cmd_after, cwd=student_dir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        after_recs_file = os.path.join(student_dir, "final_recommendations.csv")
        df_after = pd.read_csv(after_recs_file)
        
        try:
            rank_after = df_after.index[df_after['job_id'] == target_job_id].tolist()[0] + 1
            score_after = df_after[df_after['job_id'] == target_job_id].iloc[0]['final_score']
        except IndexError:
            rank_after = -1
            score_after = 0.0
            
        score_increase = score_after - score_before
        
        print(f"  -> Result: Score {score_before:.3f} -> {score_after:.3f} (+{score_increase:.3f})")
        
        new_row = pd.DataFrame([{
            "student_name": student_name,
            "target_job": target_job_title,
            "recommended_cert": recommended_cert,
            "rank_before": rank_before,
            "rank_after": rank_after,
            "score_before": score_before,
            "score_after": score_after,
            "score_increase": round(score_increase, 4)
        }])
        new_row.to_csv(summary_path, mode="a", header=False, index=False)
        print(f"  [DONE] Saved result for {student_name}")

    print("\n============================================================")
    print(f"[DONE] All students processed!")
    print("============================================================")

if __name__ == "__main__":
    main()
