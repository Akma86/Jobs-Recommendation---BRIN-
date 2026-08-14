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

def main():
    print("============================================================")
    print("EKS12: A/B Testing (Good Grades vs Bad Grades + Same Certs)")
    print("============================================================")

    khs_dir = os.path.join(root_dir, "data", "Mahasiswa", "generated_markdown_khs")
    certs_dir = os.path.join(root_dir, "data", "Mahasiswa", "generated_markdown_certificates")
    eks12_dir = os.path.join(root_dir, "results", "Eksperimen_XAI", "EKS12_AB_Test")
    os.makedirs(eks12_dir, exist_ok=True)
    
    parse_script = os.path.join(root_dir, "src", "kpbrin", "data", "parse_input.py")

    khs_files = glob.glob(os.path.join(khs_dir, "*_KHS.md"))
    # Filter only AB test students
    khs_files = [f for f in khs_files if "_Bagus" in f or "_Jelek" in f]
    
    summary_path = os.path.join(eks12_dir, "EKS12_Summary_ABTest.csv")
    if not os.path.exists(summary_path):
        pd.DataFrame(columns=["track", "student_name", "type", "job_title", "final_score"]).to_csv(summary_path, index=False)

    for idx, khs_file in enumerate(khs_files, 1):
        filename = os.path.basename(khs_file)
        student_name = filename.replace("_KHS.md", "")
        track = student_name.split("_")[0]
        student_type = student_name.split("_")[1]
        
        print(f"\n[{idx}/{len(khs_files)}] Processing Student: {student_name}")
        
        student_dir = os.path.join(eks12_dir, student_name)
        os.makedirs(student_dir, exist_ok=True)
        
        df_summary = pd.read_csv(summary_path)
        if student_name in df_summary['student_name'].values:
            print(f"  [INFO] Skipping {student_name}, already processed.")
            continue
            
        student_cert_dir = os.path.join(certs_dir, student_name)
        
        parse_cmd = ["python", parse_script, "--khs", khs_file, "--cert_dir", student_cert_dir]
        subprocess.run(parse_cmd, cwd=student_dir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        khs_csv = os.path.join(student_dir, "transcript_parsed.csv")
        original_certs_csv = os.path.join(student_dir, "certificates_parsed.csv")
        
        cwd_orig = os.getcwd()
        os.chdir(student_dir)
        try:
            df_after, _ = run_pipeline(khs_path=khs_csv, certs_path=original_certs_csv, jobs_path=JOBS_CSV_PATH, course_clo_path=COURSE_CLO_CSV_PATH)
            df_after.to_csv("recommendations.csv", index=False)
        finally:
            os.chdir(cwd_orig)

        top_jobs = df_after.head(5)
        records = []
        for _, row in top_jobs.iterrows():
            records.append({
                "track": track,
                "student_name": student_name,
                "type": student_type, # Bagus / Jelek
                "job_title": row['job_title'],
                "final_score": round(row['final_score'], 4)
            })
            
        df_new = pd.DataFrame(records)
        df_new.to_csv(summary_path, mode="a", header=not os.path.exists(summary_path) or os.stat(summary_path).st_size==0, index=False)
        print(f"  [DONE] Saved result for {student_name}")

if __name__ == "__main__":
    main()
