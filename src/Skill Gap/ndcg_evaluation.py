# -*- coding: utf-8 -*-
"""
nDCG@K EVALUATION - closes the gap in your evaluation suite (you already
have Spearman/Pearson via human_validation_template.py's `analyze` command;
this adds the ranking-quality metric Reyhan also reported).

WHAT IT MEASURES (recap from the walkthrough): given a set of (job, human
rating) pairs, does ordering jobs by the pipeline's final_score put the
BEST jobs at the top - not just "does the similarity number roughly
correlate" (that's what Spearman/Pearson already check), but specifically
"if a user only looks at the top-K, are those really the best K options."

WHY HUMAN RATINGS AS GROUND TRUTH (not a synthetic soft-label like Reyhan's):
Reyhan needed soft labels because he was evaluating on thousands of pairs -
manual rating at that scale isn't feasible, so he built an automatic
labeling process and separately validated it against human judgment. You're
evaluating on the much smaller set you already hand-rate via
human_validation_template.py, so you can use those ratings AS the ground
truth directly - no soft-label construction step needed. This is arguably
a MORE trustworthy ground truth than a bootstrapped soft label, precisely
because there's no automatic-labeling step to separately validate.

REQUIREMENTS: pip install pandas numpy --break-system-packages

USAGE:
  python ndcg_evaluation.py --file human_validation_template.xlsx
  # or average across multiple rated files (e.g. one per dummy student):
  python ndcg_evaluation.py --glob "human_validation_*.xlsx"
"""

import argparse
import glob as globmod
import numpy as np
import pandas as pd


def dcg_at_k(relevances_in_rank_order, k):
    """relevances_in_rank_order: relevance scores already sorted by the
    ranking being evaluated (model order or ideal order), position 0 first."""
    relevances = np.asarray(relevances_in_rank_order[:k], dtype=float)
    if len(relevances) == 0:
        return 0.0
    discounts = np.log2(np.arange(2, len(relevances) + 2))  # i=1..k -> log2(i+1)
    return float(np.sum(relevances / discounts))


def ndcg_at_k(df, score_col="final_score", relevance_col="Rating (0-5)", k=10):
    """df: one 'query' worth of (job, model_score, human_relevance) rows."""
    model_order = df.sort_values(score_col, ascending=False)[relevance_col].tolist()
    ideal_order = df.sort_values(relevance_col, ascending=False)[relevance_col].tolist()

    dcg = dcg_at_k(model_order, k)
    idcg = dcg_at_k(ideal_order, k)
    return dcg / idcg if idcg > 0 else np.nan


def load_rated_file(path):
    df = pd.read_excel(path, sheet_name="Validasi", header=2)
    df = df.dropna(subset=["Rating (0-5)", "job_id", "final_score (pipeline)"])
    df = df[pd.to_numeric(df["Rating (0-5)"], errors="coerce").notna()]
    df = df[pd.to_numeric(df["final_score (pipeline)"], errors="coerce").notna()]
    df = df.rename(columns={"final_score (pipeline)": "final_score"})
    df["Rating (0-5)"] = df["Rating (0-5)"].astype(float)
    df["final_score"] = df["final_score"].astype(float)
    return df


def evaluate_one_file(path):
    df = load_rated_file(path)
    if len(df) < 3:
        print(f"{path}: only {len(df)} rated rows - too few for a meaningful nDCG, skipping.")
        return None

    results = {}
    for k in [1, 5, 10]:
        if len(df) < k and k > 1:
            continue  # don't report nDCG@10 if there aren't even 10 rated jobs
        results[f"nDCG@{k}"] = round(ndcg_at_k(df, k=k), 4)

    print(f"\n{path} (n={len(df)} rated pairs):")
    for metric, value in results.items():
        print(f"  {metric} = {value}")
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default=None, help="single rated .xlsx file")
    parser.add_argument("--glob", default=None, help="glob pattern for multiple rated .xlsx files (averages results)")
    args = parser.parse_args()

    if args.glob:
        paths = sorted(globmod.glob(args.glob))
    elif args.file:
        paths = [args.file]
    else:
        paths = ["human_validation_template.xlsx"]

    if not paths:
        print("No files matched. Rate a human_validation_template.xlsx first "
              "(see human_validation_template.py).")
        return

    all_results = []
    for path in paths:
        r = evaluate_one_file(path)
        if r:
            all_results.append(r)

    if len(all_results) > 1:
        print(f"\n=== Average across {len(all_results)} rated files ===")
        keys = set().union(*[r.keys() for r in all_results])
        for k in sorted(keys):
            vals = [r[k] for r in all_results if k in r]
            print(f"  {k} = {np.mean(vals):.4f} (n={len(vals)} files)")

    print("\nNote: nDCG close to 1.0 means the pipeline's final_score ranking already")
    print("puts the jobs a human considers best near the top - the ordering is trustworthy")
    print("even in cases where Spearman/Pearson (which check the raw score values, not just")
    print("rank order) might be lower.")


if __name__ == "__main__":
    main()
