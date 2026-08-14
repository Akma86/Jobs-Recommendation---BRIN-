import os
import sys
import pandas as pd
import json

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)
)
from kpbrin.core.full_pipeline import run_pipeline

def main():
    khs_path = os.path.join(ROOT_DIR, "data", "Percobaan", "Coba_Mahasiswa_Andi_Wijaya", "transcript_parsed.csv")
    certs_path = os.path.join(ROOT_DIR, "data", "Percobaan", "Coba_Mahasiswa_Andi_Wijaya", "certificates_parsed.csv")
    
    print("Menjalankan pipeline untuk mendapatkan data sebelum SHAP...")
    
    # Run pipeline
    final_ranking, job_contributions = run_pipeline(
        khs_path=khs_path,
        certs_path=certs_path,
    )
from kpbrin.data.feature_engineering import build_student_features
from kpbrin.xai.shap_explain import _build_domain_contributions
from kpbrin.data.feature_engineering import _classify_course

    khs_df = pd.read_csv(khs_path)
    certs_df = pd.read_csv(certs_path)
    student_features = build_student_features(khs_df, certs_df)
    
    # Get top 5 jobs
    top_jobs = final_ranking.head(5)["job_id"].tolist()
    
    # Bikin mapping domain otomatis
    all_courses = set()
    for contribs in job_contributions.values():
        for label in contribs:
            if label.startswith("MK: "):
                all_courses.add(label.replace("MK: ", ""))
    domain_to_courses = {c: _classify_course(c) for c in all_courses}
    
    # Convert job_contributions into DOMAIN level rows
    rows = []
    for job_id in top_jobs:
        job_title = final_ranking[final_ranking["job_id"] == job_id]["job_title"].iloc[0]
        
        # INI DIA MAGISNYA: Konversi dari MK mentah ke IPK, Skill, Cert
        domain_contribs = _build_domain_contributions(
            student_features, job_contributions, job_id, domain_to_courses
        )
        
        for feature, score in domain_contribs.items():
            rows.append({
                "job_id": job_id,
                "job_title": job_title,
                "feature_name": feature,
                "pre_shap_score": score
            })
            
    df = pd.DataFrame(rows)
    out_csv = os.path.join(ROOT_DIR, "dataset_sebelum_shap.csv")
    df.to_csv(out_csv, index=False)
    print(f"Data berhasil disimpan ke: {out_csv}")
    
if __name__ == "__main__":
    main()
