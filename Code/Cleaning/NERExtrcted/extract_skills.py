# -*- coding: utf-8 -*-
"""
Skill extraction pipeline for job postings (LinkedIn / Glassdoor).

Approach: rule-based PhraseMatcher (spaCy) instead of a trained NER model.
Why: we don't have labeled skill-annotation data for job postings, so a
fine-tuned NER model would need weak/manual labels first. PhraseMatcher on
our curated skill vocabulary (from Dataset_CLO_OBE_SI_TelUJakarta.xlsx) gives
a solid, explainable baseline with zero training cost. It can be swapped
later for a trained model if you build an annotated set.

Output columns added per job posting:
  - matched_skills   : list of canonical skill names (e.g. "SQL", "Machine Learning")
  - matched_domains  : list of unique skill domains those skills belong to
  - skill_count      : number of distinct canonical skills matched
"""

import json
import sys
import pandas as pd
import spacy
from spacy.matcher import PhraseMatcher
from skill_vocabulary import SKILL_VOCAB, build_alias_index


def build_matcher(nlp):
    """Create a PhraseMatcher loaded with every alias, tagged with its canonical skill."""
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    alias_to_canonical = build_alias_index()

    # group patterns by canonical skill so match_id -> canonical skill directly
    canonical_to_aliases = {}
    for alias, canonical in alias_to_canonical.items():
        canonical_to_aliases.setdefault(canonical, []).append(alias)

    for canonical, aliases in canonical_to_aliases.items():
        patterns = [nlp.make_doc(a) for a in aliases]
        matcher.add(canonical, patterns)

    return matcher


def extract_skills_from_text(text, nlp, matcher):
    if not isinstance(text, str) or not text.strip():
        return [], []
    doc = nlp(text)
    matches = matcher(doc)
    canonical_hits = set()
    for match_id, start, end in matches:
        canonical = nlp.vocab.strings[match_id]
        canonical_hits.add(canonical)

    domains = sorted({SKILL_VOCAB[c]["domain"] for c in canonical_hits})
    return sorted(canonical_hits), domains


def process_file(input_path, text_column, output_path, id_column=None, limit=None):
    print(f"Loading {input_path} ...")
    df = pd.read_csv(input_path)
    if limit:
        df = df.head(limit).copy()

    print(f"  rows: {len(df)}, target text column: '{text_column}'")

    nlp = spacy.blank("en")  # tokenizer only, no need for full pretrained pipeline
    matcher = build_matcher(nlp)

    matched_skills_list = []
    matched_domains_list = []
    skill_counts = []

    texts = df[text_column].fillna("").astype(str)
    # nlp.pipe for speed on large volumes (linkedin ~10k rows)
    for doc_skills, doc_domains in (
        extract_skills_from_text(t, nlp, matcher) for t in texts
    ):
        matched_skills_list.append(doc_skills)
        matched_domains_list.append(doc_domains)
        skill_counts.append(len(doc_skills))

    df["matched_skills"] = [json.dumps(s) for s in matched_skills_list]
    df["matched_domains"] = [json.dumps(d) for d in matched_domains_list]
    df["skill_count"] = skill_counts

    df.to_csv(output_path, index=False)
    print(f"  -> saved: {output_path}")
    print(f"  avg skills/job: {sum(skill_counts)/len(skill_counts):.2f}")
    print(f"  jobs with 0 skills matched: {sum(1 for c in skill_counts if c == 0)} / {len(skill_counts)}")
    return df


if __name__ == "__main__":
    # LinkedIn
    process_file(
        input_path="./../../../Dataset/Pekerjaan/Clean/linkedin_clean.csv",
        text_column="descriptionText",
        output_path="./../../../Dataset/Pekerjaan/NERExtracted/linkedin_with_skills.csv",
    )

    # Glassdoor
    process_file(
        input_path="./../../../Dataset/Pekerjaan/Clean/glassdoor_clean.csv",
        text_column="job_description",
        output_path="./../../../Dataset/Pekerjaan/NERExtracted/glassdoor_with_skills.csv",
    )
