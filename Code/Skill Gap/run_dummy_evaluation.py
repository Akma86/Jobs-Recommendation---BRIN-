# -*- coding: utf-8 -*-
"""
MULTI-STUDENT EVALUATION - runs the full pipeline across all 10 dummy
students (generate_dummy_students.py) and produces a summary table so you
can sanity-check: does a "Cybersecurity" track student get cybersecurity
jobs recommended, does "UX / Product Design" get design jobs, etc.?
"""

import os
import shutil
import subprocess
import sys
import pandas as pd

TRACK_KEYWORDS = {
    "Software Engineering": ["software", "developer", "engineer", "backend", "full stack", "full-stack"],
    "Data Science / Machine Learning": ["data scientist", "machine learning", "ml engineer", "data analyst", "ai"],
    "Cybersecurity": ["security", "cyber", "soc", "penetration", "infosec"],
    "UX / Product Design": ["design", "ux", "ui", "product designer"],
    "Networking / Infrastructure": ["network", "infrastructure", "cloud", "devops", "sysadmin"],
    "Business Analyst / Enterprise Systems": ["business analyst", "erp", "sap", "consultant"],
    "Data Engineering": ["data engineer", "etl", "pipeline", "analytics engineer"],
    "IT Governance / Project Management": ["project manager", "governance", "pmo", "scrum master", "it manager"],
    "Full-stack / DevOps": ["devops", "full stack", "full-stack", "sre", "platform engineer"],
    "AI / NLP": ["ai", "nlp", "machine learning", "research engineer", "ml engineer"],
}


def generate_all_dummy_files(dummy_script_path, out_dir):
    sys.path.insert(0, os.path.dirname(os.path.abspath(dummy_script_path)))
    import generate_dummy_students as gen

    per_student_dirs = {}
    for student in gen.STUDENTS:
        student_dir = os.path.join(out_dir, student["name"])
        khs_dir = os.path.join(student_dir, "khs")
        cert_dir = os.path.join(student_dir, "certs")
        os.makedirs(khs_dir, exist_ok=True)
        os.makedirs(cert_dir, exist_ok=True)

        khs_text = gen.generate_khs(student)
        khs_path = os.path.join(khs_dir, f"{student['name']}_KHS.md")
        with open(khs_path, "w", encoding="utf-8") as f:
            f.write(khs_text)

        for cert_filename, cert_text in gen.generate_all_certificates_for_student(student):
            with open(os.path.join(cert_dir, cert_filename), "w", encoding="utf-8") as f:
                f.write(cert_text)

        per_student_dirs[student["name"]] = {
            "track": student["track"], "khs_path": khs_path, "cert_dir": cert_dir,
        }
    return per_student_dirs


def run_pipeline_for_student(name, khs_path, cert_dir, work_dir, root_dir):
    student_work = os.path.join(work_dir, name)
    os.makedirs(student_work, exist_ok=True)

    # 1. Parse Input
    parse_input_script = os.path.join(root_dir, "RankingJob", "parse_input.py")
    subprocess.run(
        [sys.executable, parse_input_script, "--khs", os.path.abspath(khs_path),
         "--cert_dir", os.path.abspath(cert_dir)],
        cwd=student_work, check=True,
    )
    
    # 2. Run App (Ranking only)
    app_script = os.path.join(root_dir, "prototype", "app.py")
    subprocess.run(
        [sys.executable, app_script, "--khs", "transcript_parsed.csv",
         "--certs", "certificates_parsed.csv", "--skip-xai"],
        cwd=student_work, check=True,
    )

    result_path = os.path.join(student_work, "final_recommendations.csv")
    return pd.read_csv(result_path) if os.path.exists(result_path) else None


def check_track_relevance(track, top_titles):
    keywords = TRACK_KEYWORDS.get(track, [])
    titles_lower = " | ".join(top_titles).lower()
    hits = [kw for kw in keywords if kw in titles_lower]
    return len(hits) > 0, hits


def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dummy_script = os.path.join(root_dir, "generate_dummy_students.py")
    
    if not os.path.exists(dummy_script):
        print(f"ERROR: {dummy_script} not found.")
        return

    print("Generating KHS.md + Certificate.md for all 10 dummy students...")
    student_dirs = generate_all_dummy_files(dummy_script, out_dir="dummy_eval_data")

    summary_rows = []
    for name, info in student_dirs.items():
        print(f"\n=== Running pipeline for {name} ({info['track']}) ===")
        try:
            result = run_pipeline_for_student(name, info["khs_path"], info["cert_dir"], "dummy_eval_runs", root_dir)
        except subprocess.CalledProcessError as e:
            print(f"  FAILED: {e}")
            summary_rows.append({"student": name, "track": info["track"], "status": "ERROR",
                                  "top_5_jobs": "", "track_relevant": None, "matched_keywords": ""})
            continue

        if result is None or len(result) == 0:
            summary_rows.append({"student": name, "track": info["track"], "status": "NO_RECOMMENDATIONS",
                                  "top_5_jobs": "", "track_relevant": None, "matched_keywords": ""})
            continue

        top5 = result.sort_values("final_score", ascending=False).head(5)["job_title"].tolist()
        relevant, hits = check_track_relevance(info["track"], top5)
        summary_rows.append({
            "student": name, "track": info["track"], "status": "OK",
            "top_5_jobs": " | ".join(top5),
            "track_relevant": relevant, "matched_keywords": ", ".join(hits),
        })

    summary = pd.DataFrame(summary_rows)
    summary.to_csv("dummy_evaluation_summary.csv", index=False)
    print("\n\n=== FINAL SUMMARY ===")
    print(summary[["student", "track", "status", "track_relevant"]].to_string(index=False))
    n_relevant = summary["track_relevant"].sum()
    n_total = summary["status"].eq("OK").sum()
    print(f"\n{n_relevant}/{n_total} students got at least one track-relevant job in their top 5.")
    print("Saved: dummy_evaluation_summary.csv (full detail incl. actual job titles)")


if __name__ == "__main__":
    main()
