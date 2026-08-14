import os
import glob
import subprocess
import pandas as pd
import sys

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
)
from kpbrin.core.full_pipeline import run_pipeline, JOBS_CSV_PATH, COURSE_CLO_CSV_PATH

def main():
    print("============================================================")
    print("EKS11: Impact of Real Certificates (Matkul vs Matkul + Certs)")
    print("============================================================")

    khs_dir = os.path.join(root_dir, "data", "generated_markdown_khs")
    certs_dir = os.path.join(root_dir, "data", "generated_markdown_certificates")
    eks11_dir = os.path.join(root_dir, "results", "Eksperimen_XAI", "EKS11_RealCertImpact")
    os.makedirs(eks11_dir, exist_ok=True)
    
    parse_script = os.path.join(root_dir, "src", "RankingJob", "parse_input.py")

    khs_files = glob.glob(os.path.join(khs_dir, "*_KHS.md"))
    
    summary_path = os.path.join(eks11_dir, "EKS11_Summary_AllStudents.csv")
    if not os.path.exists(summary_path):
        pd.DataFrame(columns=["student_name", "job_title", "rank_matkul_saja", "score_matkul_saja", "rank_matkul_dan_cert", "score_matkul_dan_cert", "score_increase"]).to_csv(summary_path, index=False)

    for idx, khs_file in enumerate(khs_files, 1):
        filename = os.path.basename(khs_file)
        student_name = filename.replace("_KHS.md", "")
        print(f"\n[{idx}/{len(khs_files)}] Processing Student: {student_name}")
        
        student_dir = os.path.join(eks11_dir, student_name)
        os.makedirs(student_dir, exist_ok=True)
        
        df_summary = pd.read_csv(summary_path)
        if student_name in df_summary['student_name'].values:
            print(f"  [INFO] Skipping {student_name}, already in summary.")
            continue
            
        student_cert_dir = os.path.join(certs_dir, student_name)
        has_certs = os.path.exists(student_cert_dir) and len(os.listdir(student_cert_dir)) > 0
        
        parse_cmd = ["python", parse_script, "--khs", khs_file]
        if has_certs:
            parse_cmd.extend(["--cert_dir", student_cert_dir])
            
        subprocess.run(parse_cmd, cwd=student_dir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        khs_csv = os.path.join(student_dir, "transcript_parsed.csv")
        original_certs_csv = os.path.join(student_dir, "certificates_parsed.csv")
        
        print(f"  -> Phase 1: Matkul Saja")
        cwd_orig = os.getcwd()
        os.chdir(student_dir)
        try:
            df_before, _ = run_pipeline(khs_path=khs_csv, certs_path=None, jobs_path=JOBS_CSV_PATH, course_clo_path=COURSE_CLO_CSV_PATH)
            df_before.to_csv("recommendations_matkul_saja.csv", index=False)
        finally:
            os.chdir(cwd_orig)
        
        if not has_certs or not os.path.exists(original_certs_csv):
            print(f"  [INFO] {student_name} has no certificates. After = Before.")
            df_after = df_before.copy()
            df_after.to_csv(os.path.join(student_dir, "recommendations_matkul_dan_cert.csv"), index=False)
        else:
            print(f"  -> Phase 2: Matkul + Semua Sertifikat")
            cwd_orig = os.getcwd()
            os.chdir(student_dir)
            try:
                df_after, _ = run_pipeline(khs_path=khs_csv, certs_path=original_certs_csv, jobs_path=JOBS_CSV_PATH, course_clo_path=COURSE_CLO_CSV_PATH)
                df_after.to_csv("recommendations_matkul_dan_cert.csv", index=False)
            finally:
                os.chdir(cwd_orig)

        top_jobs = df_before.head(5)['job_id'].tolist()
        records = []
        for rank_b, job_id in enumerate(top_jobs, 1):
            row_before = df_before[df_before['job_id'] == job_id].iloc[0]
            score_b = row_before['final_score']
            job_title = row_before['job_title']
            
            row_after_list = df_after[df_after['job_id'] == job_id]
            if len(row_after_list) > 0:
                row_after = row_after_list.iloc[0]
                rank_a = df_after.index[df_after['job_id'] == job_id][0] + 1
                score_a = row_after['final_score']
            else:
                rank_a = -1
                score_a = 0.0
                
            score_inc = score_a - score_b
            records.append({
                "student_name": student_name,
                "job_title": job_title,
                "rank_matkul_saja": rank_b,
                "score_matkul_saja": round(score_b, 4),
                "rank_matkul_dan_cert": rank_a,
                "score_matkul_dan_cert": round(score_a, 4),
                "score_increase": round(score_inc, 4)
            })
            
        df_new = pd.DataFrame(records)
        df_new.to_csv(summary_path, mode="a", header=not os.path.exists(summary_path) or os.stat(summary_path).st_size==0, index=False)
        print(f"  [DONE] Saved result for {student_name}")

if __name__ == "__main__":
    main()
