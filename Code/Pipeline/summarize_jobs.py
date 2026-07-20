# -*- coding: utf-8 -*-
"""
BERT-based summarization preprocessing for job postings.

WHY THIS STEP: job descriptions (especially LinkedIn) are often long and
padded with boilerplate (benefits, EEO statements, company boilerplate,
application instructions) that dilutes the actual competency signal when
embedded. Summarizing first, THEN embedding, should give SBERT/cross-encoder
a cleaner, more information-dense text to match against.

MODEL: facebook/bart-large-cnn
  - Standard, well-tested abstractive summarization model (trained on
    CNN/DailyMail news summarization, generalizes reasonably well to other
    text). English-only, which is fine since job postings are in English.
  - ~400M params - moderate GPU memory, runs comfortably on most consumer GPUs.

WHERE THIS FITS IN THE PIPELINE:
  jobs_unified_with_skills.csv --[this script]--> jobs_unified_summarized.csv
  Then point full_pipeline_subclo.py at the summarized file instead (see
  USAGE NOTE at the bottom) - it just needs a column with the text to embed.

REQUIREMENTS (run on your machine - GPU recommended, this is the heaviest
model in the whole pipeline in terms of per-item cost):
  pip install transformers torch pandas --break-system-packages

USAGE:
  python summarize_jobs.py
  -> produces jobs_unified_summarized.csv (adds a `description_summary` column)
"""

import pandas as pd
from transformers import pipeline

MODEL_NAME = "facebook/bart-large-cnn"
MAX_INPUT_CHARS = 3000       # BART has a token limit; truncate very long postings first
MIN_LENGTH_TO_SUMMARIZE = 400  # skip summarizing already-short postings (not worth it, adds noise)
SUMMARY_MAX_TOKENS = 130
SUMMARY_MIN_TOKENS = 30
BATCH_SIZE = 8


def main():
    print(f"Loading summarizer: {MODEL_NAME} ...")
    # device=0 uses GPU if available; falls back to CPU automatically if not
    import torch
    device = 0 if torch.cuda.is_available() else -1
    print(f"Using {'GPU' if device == 0 else 'CPU'}")
    summarizer = pipeline("summarization", model=MODEL_NAME, device=device)

    jobs = pd.read_csv("jobs_unified_with_skills.csv")
    print(f"Loaded {len(jobs)} job postings")

    descriptions = jobs["description"].fillna("").astype(str)
    to_summarize_mask = descriptions.str.len() >= MIN_LENGTH_TO_SUMMARIZE

    print(f"{to_summarize_mask.sum()}/{len(jobs)} postings are long enough to summarize "
          f"(>= {MIN_LENGTH_TO_SUMMARIZE} chars); the rest are used as-is.")

    summaries = descriptions.copy()
    texts_to_summarize = descriptions[to_summarize_mask].str.slice(0, MAX_INPUT_CHARS).tolist()

    results = []
    for i in range(0, len(texts_to_summarize), BATCH_SIZE):
        batch = texts_to_summarize[i:i + BATCH_SIZE]
        out = summarizer(batch, max_length=SUMMARY_MAX_TOKENS, min_length=SUMMARY_MIN_TOKENS,
                          do_sample=False, truncation=True)
        results.extend([o["summary_text"] for o in out])
        print(f"  summarized {min(i+BATCH_SIZE, len(texts_to_summarize))}/{len(texts_to_summarize)}")

    summaries.loc[to_summarize_mask] = results
    jobs["description_summary"] = summaries

    jobs.to_csv("jobs_unified_summarized.csv", index=False)
    print(f"\nSaved: jobs_unified_summarized.csv")

    print("\n--- Sample: before vs after ---")
    sample_idx = jobs[to_summarize_mask].index[0]
    print("BEFORE:", jobs.loc[sample_idx, "description"][:400], "...")
    print("\nAFTER: ", jobs.loc[sample_idx, "description_summary"])


if __name__ == "__main__":
    main()
