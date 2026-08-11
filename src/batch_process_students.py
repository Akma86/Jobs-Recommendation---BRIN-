import os
import glob
import subprocess
import shutil

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    khs_dir = os.path.join(root_dir, "data", "generated_markdown_khs")
    certs_dir = os.path.join(root_dir, "data", "generated_markdown_certificates")
    
    percobaan_dir = os.path.join(root_dir, "data", "Percobaan")
    hasil_dir = os.path.join(root_dir, "results")
    
    # Scripts to run
    parse_script = os.path.join(root_dir, "src", "RankingJob", "parse_input.py")
    app_script = os.path.join(root_dir, "src", "prototype", "app.py")

    os.makedirs(percobaan_dir, exist_ok=True)
    os.makedirs(hasil_dir, exist_ok=True)

    khs_files = glob.glob(os.path.join(khs_dir, "*_KHS.md"))
    
    for khs_file in khs_files:
        filename = os.path.basename(khs_file)
        # Assuming format is "Name_KHS.md"
        student_name = filename.replace("_KHS.md", "")
        print(f"\n==============================================")
        print(f"Processing student: {student_name}")
        print(f"==============================================")

        coba_name = f"Coba_Mahasiswa_{student_name}"
        
        student_percobaan_dir = os.path.join(percobaan_dir, coba_name)
        student_hasil_dir = os.path.join(hasil_dir, coba_name)
        
        os.makedirs(student_percobaan_dir, exist_ok=True)
        os.makedirs(student_hasil_dir, exist_ok=True)

        student_cert_dir = os.path.join(certs_dir, student_name)
        has_certs = os.path.exists(student_cert_dir) and len(os.listdir(student_cert_dir)) > 0

        print(f"1. Parsing inputs...")
        parse_cmd = ["python", parse_script, "--khs", khs_file]
        if has_certs:
            parse_cmd.extend(["--cert_dir", student_cert_dir])
            
        try:
            # Run parse_input in the percobaan dir so CSVs save there
            subprocess.run(parse_cmd, cwd=student_percobaan_dir, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error parsing for {student_name}: {e}")
            continue

        print(f"2. Running pipeline (Ranking only)...")
        khs_csv = os.path.join(student_percobaan_dir, "transcript_parsed.csv")
        certs_csv = os.path.join(student_percobaan_dir, "certificates_parsed.csv")

        app_cmd = ["python", app_script, "--khs", khs_csv, "--skip-xai"]
        if os.path.exists(certs_csv):
            app_cmd.extend(["--certs", certs_csv])
            
        try:
            # Run app in hasil dir so final_recommendations.csv saves there
            subprocess.run(app_cmd, cwd=student_hasil_dir, check=True)
            print(f"✅ Finished processing {student_name}")
        except subprocess.CalledProcessError as e:
            print(f"Error running pipeline for {student_name}: {e}")

if __name__ == "__main__":
    main()
