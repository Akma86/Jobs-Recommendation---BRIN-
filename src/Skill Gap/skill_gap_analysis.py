# -*- coding: utf-8 -*-
"""
SKILL GAP ANALYSIS - the "inverse" of the main recommendation pipeline.

The main pipeline answers: "given this student's courses/certs, which jobs
fit?" This script answers the complementary question the proposal promised:
"given ONE target job, which specific competencies is this student missing,
and what evidence do they already have?"

METHOD:
  1. Take a target job's description and break it into discrete, atomic
     requirement statements using Claude (mirrors the requirement-extraction
     step Reyhan's CareerSync uses with Gemini - same idea, same reason:
     raw job postings bury 2-3 real requirements inside boilerplate/HR
     filler text, so extracting atomic statements first makes each one a
     clean, comparable unit).
  2. Build the student's "evidence corpus": every matched sub-CLO text +
     every certificate's text (title + description). This is exactly the
     same evidence used by the main pipeline, just re-embedded as passages
     to search AGAINST instead of queries to search WITH.
  3. For each requirement statement, find its best-matching evidence via
     SBERT + cross-encoder (same retrieve-then-rerank pattern as the main
     pipeline, just pointed in the opposite direction).
  4. Requirements whose best match scores above GAP_THRESHOLD are
     "covered" (cite the evidence). Requirements below it are "gaps" -
     these are what the student should be told to work on.

REQUIREMENTS:
  pip install anthropic sentence-transformers pandas --break-system-packages
  export ANTHROPIC_API_KEY=sk-ant-...

INPUT FILES needed in the same folder:
  - sub_clo_profiles.csv
  - pipeline_course_match_log.csv   (from a full_pipeline_subclo.py /
                                       full_pipeline_certs.py run - tells us
                                       which courses are "the student's")
  - certificates_parsed.csv          (optional)
  - jobs_unified_with_skills.csv     (to look up the target job's description)

USAGE:
  python skill_gap_analysis.py --job_id li_1234567890
  # or, for a job not in the dataset:
  python skill_gap_analysis.py --job_title "Data Analyst" --job_description "..."

OUTPUT:
  - skill_gap_report.csv   one row per requirement statement, with
                            covered/gap status, best evidence, and score
"""

import argparse
import json
import re
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder

SBERT_MODEL = "intfloat/multilingual-e5-large"
CROSS_ENCODER_MODEL = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
GAP_THRESHOLD = 2.0  # cross-encoder score below this = treated as a gap (tune after seeing real score distributions)

REQUIREMENT_EXTRACTION_PROMPT = """Below is a job posting. Extract every distinct, atomic
requirement or qualification it asks for - one requirement per item (skills,
tools, experience level, education, domain knowledge). Skip boilerplate
(benefits, "we encourage you to apply", EEO statements, application
instructions) - those aren't requirements.

Respond with ONLY a JSON array of strings (no markdown fences, no commentary).

JOB POSTING:
\"\"\"
{job_text}
\"\"\""""


def extract_requirements(job_title, job_description, model="claude-sonnet-4-6"):
    import anthropic
    client = anthropic.Anthropic()
    prompt = REQUIREMENT_EXTRACTION_PROMPT.format(job_text=f"{job_title}\n\n{job_description}"[:6000])
    response = client.messages.create(model=model, max_tokens=1500,
                                       messages=[{"role": "user", "content": prompt}])
    raw = "".join(b.text for b in response.content if b.type == "text")
    raw = re.sub(r"^```json\s*|\s*```$", "", raw.strip())
    return json.loads(raw)


def build_evidence_corpus(match_log, subclo_profiles, certs_df=None):
    """Every matched sub-CLO + every certificate becomes one evidence passage."""
    evidence = []
    matched_courses = match_log[match_log["included"]]["matched_course_name"]
    for course_name in matched_courses:
        subclos = subclo_profiles[subclo_profiles["course_name"] == course_name]
        for _, sc in subclos.iterrows():
            evidence.append({
                "evidence_id": sc["sub_clo_id"],
                "evidence_type": "sub-CLO akademik",
                "evidence_label": f"{course_name} ({sc['sub_clo_code']})",
                "evidence_text": sc["sub_clo_text"],
            })

    if certs_df is not None and len(certs_df) > 0:
        for _, c in certs_df.iterrows():
            evidence.append({
                "evidence_id": c["cert_id"],
                "evidence_type": "sertifikat",
                "evidence_label": c["title"],
                "evidence_text": f"{c['title']}. {c.get('description_text', '')}",
            })

    return pd.DataFrame(evidence)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_id", default=None, help="job_id from jobs_unified_with_skills.csv")
    parser.add_argument("--job_title", default=None, help="Manual job title (if not using --job_id)")
    parser.add_argument("--job_description", default=None, help="Manual job description (if not using --job_id)")
    parser.add_argument("--certs", default="certificates_parsed.csv")
    args = parser.parse_args()

    if args.job_id:
        jobs = pd.read_csv("jobs_unified_with_skills.csv")
        job_row = jobs[jobs["job_id"] == args.job_id].iloc[0]
        job_title, job_description = job_row["title"], job_row["description"]
    elif args.job_title and args.job_description:
        job_title, job_description = args.job_title, args.job_description
    else:
        parser.error("Provide either --job_id, or both --job_title and --job_description")

    print(f"Target job: {job_title}")
    print("Extracting atomic requirement statements via Claude...")
    requirements = extract_requirements(job_title, job_description)
    print(f"  -> {len(requirements)} requirements extracted")
    for r in requirements:
        print(f"   - {r}")

    print("\nBuilding student evidence corpus...")
    match_log = pd.read_csv("pipeline_course_match_log.csv")
    subclo_profiles = pd.read_csv("sub_clo_profiles.csv")
    try:
        certs_df = pd.read_csv(args.certs)
    except FileNotFoundError:
        certs_df = None
        print("  (no certificates file found - academic evidence only)")

    evidence = build_evidence_corpus(match_log, subclo_profiles, certs_df)
    print(f"  -> {len(evidence)} evidence items (sub-CLOs + certificates)")
    if len(evidence) == 0:
        print("No evidence available - can't run gap analysis. Run the main pipeline first.")
        return

    print("\nEmbedding evidence + matching each requirement...")
    sbert_model = SentenceTransformer(SBERT_MODEL)
    cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL)

    evidence_texts = ("passage: " + evidence["evidence_text"].fillna("")).tolist()
    evidence_emb = sbert_model.encode(evidence_texts, normalize_embeddings=True, show_progress_bar=True)

    results = []
    for req in requirements:
        q_emb = sbert_model.encode(["query: " + req], normalize_embeddings=True)[0]
        sims = evidence_emb @ q_emb
        top_idx = np.argsort(-sims)[:5]  # rerank only the top-5 candidates for this requirement

        pairs = [(req, evidence.iloc[i]["evidence_text"][:1000]) for i in top_idx]
        ce_scores = cross_encoder.predict(pairs)
        best_local = int(np.argmax(ce_scores))
        best_idx = top_idx[best_local]
        best_score = float(ce_scores[best_local])

        results.append({
            "requirement": req,
            "status": "COVERED" if best_score >= GAP_THRESHOLD else "GAP",
            "best_evidence_score": round(best_score, 3),
            "best_evidence_type": evidence.iloc[best_idx]["evidence_type"],
            "best_evidence_label": evidence.iloc[best_idx]["evidence_label"],
        })

    report = pd.DataFrame(results)
    report.to_csv("skill_gap_report.csv", index=False)

    n_covered = (report["status"] == "COVERED").sum()
    n_gap = (report["status"] == "GAP").sum()
    print(f"\n=== Ringkasan: {n_covered}/{len(report)} requirement TERPENUHI, {n_gap}/{len(report)} GAP ===")
    print("\nGAP (perlu ditingkatkan):")
    for _, row in report[report["status"] == "GAP"].iterrows():
        print(f"  - {row['requirement']}")
    print("\nCOVERED (sudah punya bukti):")
    for _, row in report[report["status"] == "COVERED"].iterrows():
        print(f"  - {row['requirement']}  <-  {row['best_evidence_type']}: {row['best_evidence_label']}")

    print("\nSaved: skill_gap_report.csv")


if __name__ == "__main__":
    main()
