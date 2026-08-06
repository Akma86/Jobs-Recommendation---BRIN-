import os
import glob
import subprocess

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    hasil_dir = os.path.join(root_dir, "Hasil Percobaan")
    
    ablation_script = os.path.join(root_dir, "Code", "Skill Gap", "ablation_study.py")
    baseline_script = os.path.join(root_dir, "Code", "Skill Gap", "baseline_keyword_matching.py")
    
    course_clo_csv = os.path.join(root_dir, "Dataset", "Mata Kuliah", "course_clo_consolidated.csv")
    jobs_csv = os.path.join(root_dir, "Dataset", "Pekerjaan", "Processed", "jobs_unified.csv")

    student_dirs = glob.glob(os.path.join(hasil_dir, "Coba_Mahasiswa_*"))
    
    for student_dir in student_dirs:
        student_name = os.path.basename(student_dir)
        print(f"\n==============================================")
        print(f"Running Evaluations for: {student_name}")
        print(f"==============================================")

        eval_dir = os.path.join(student_dir, "Evaluasi")
        os.makedirs(eval_dir, exist_ok=True)
        
        # We need to copy the match log and the aggregated csv to the eval dir, or 
        # tell the scripts where to find them. The scripts look in CWD.
        # So we can just copy them temporarily or run the scripts from student_dir and move the output.
        # Actually, if we run the scripts from student_dir, we don't need to copy anything, 
        # then we can just move the output CSVs into Evaluasi.
        
        print("1. Running Ablation Study (C)")
        try:
            subprocess.run(["python", ablation_script], cwd=student_dir, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running ablation for {student_name}: {e}")

        print("2. Running Baseline Keyword Matching")
        try:
            subprocess.run(["python", baseline_script, "--course_clo_csv", course_clo_csv, "--jobs_csv", jobs_csv], cwd=student_dir, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running baseline for {student_name}: {e}")

        # Move the outputs to Evaluasi
        output_files = [
            "ablation_C_with_without_certs.csv",
            "baseline_job_ranking.csv",
            "baseline_vs_semantic_comparison.csv"
        ]
        
        for f in output_files:
            src = os.path.join(student_dir, f)
            if os.path.exists(src):
                dst = os.path.join(eval_dir, f)
                # os.replace handles overwrite automatically
                os.replace(src, dst)
        
        print(f"[DONE] Finished evaluations for {student_name}. Results saved to Evaluasi folder.")

if __name__ == "__main__":
    main()
