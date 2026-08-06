# -*- coding: utf-8 -*-
"""
TRAIN ENSEMBLE RANKER ON HUMAN RATINGS - the upgrade path from "formula
that shap_explainability.py approximates" to "model that actually learned
from human judgment".

CURRENT STATE (shap_explainability.py): the surrogate model is trained to
reproduce final_score, which is itself just your hand-weighted formula. So
SHAP explanations there describe "what drives the FORMULA's output" - useful,
but a little circular, since the formula's weights were chosen by hand, not
learned.

THIS SCRIPT: trains the SAME kind of model (XGBoost, same engineered
features from shap_explainability.py's build_feature_table) but with the
target swapped to REAL HUMAN RATINGS collected via human_validation_template.py.
Once trained, this model's predictions - and the SHAP explanations of it -
describe what a human actually seems to care about when judging fit, which
is a materially different (and stronger) claim than "this is what my formula
computes."

DATA REQUIREMENT - READ THIS FIRST: XGBoost with these ~5-8 features needs
a reasonable number of rated examples to learn anything meaningful rather
than overfitting noise. Rough guidance:
  < 30 ratings   : not enough - this script will warn and refuse to proceed
                   past a basic correlation check
  30-80 ratings  : marginal - trains, but treat results as exploratory,
                   report cross-validated metrics honestly, don't overclaim
  80+ ratings    : reasonable - the model has a real chance of generalizing
Practically: rate multiple students' recommendation lists (via
human_validation_template.py, one per student) and combine them, rather
than trying to squeeze 80 ratings out of one student's job list.

REQUIREMENTS:
  pip install xgboost scikit-learn pandas numpy --break-system-packages

INPUT:
  - one or more rated human_validation_*.xlsx files (--glob)
  - the SAME lower-level pipeline files shap_explainability.py needs:
    course_job_aggregated.csv, pipeline_course_match_log.csv,
    cert_job_aggregated.csv + certificates_parsed.csv (optional)

USAGE:
  python train_ensemble_ranker.py --glob "human_validation_*.xlsx"

OUTPUT:
  - ensemble_ranker_model.json      (saved XGBoost model - reload with
                                       xgb.XGBRegressor().load_model(...))
  - ensemble_ranker_cv_report.txt   cross-validated R^2 / MAE, honestly
                                     reported so you don't overclaim fit
                                     quality with too little data
"""

import argparse
import glob as globmod
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import KFold, cross_val_score

from shap_explainability import build_feature_table, FEATURE_LABELS

MIN_RATINGS_TO_TRAIN = 30


def load_all_ratings(pattern):
    paths = sorted(globmod.glob(pattern))
    if not paths:
        raise FileNotFoundError(f"No files matched pattern: {pattern}")

    frames = []
    for path in paths:
        df = pd.read_excel(path, sheet_name="Validasi", header=2)
        df = df.dropna(subset=["Rating (0-5)", "job_id", "final_score (pipeline)"])
        df = df[pd.to_numeric(df["Rating (0-5)"], errors="coerce").notna()]
        df["source_file"] = path
        frames.append(df[["job_id", "job_title", "Rating (0-5)", "source_file"]])

    combined = pd.concat(frames, ignore_index=True)
    combined["Rating (0-5)"] = combined["Rating (0-5)"].astype(float)
    return combined


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--glob", default="human_validation_*.xlsx",
                         help="Glob pattern matching one or more RATED template files")
    args = parser.parse_args()

    print(f"Loading ratings matching: {args.glob}")
    ratings = load_all_ratings(args.glob)
    print(f"Total rated (job) pairs across all files: {len(ratings)}")

    if len(ratings) < MIN_RATINGS_TO_TRAIN:
        print(f"\nSTOPPING: only {len(ratings)} ratings found, need at least "
              f"{MIN_RATINGS_TO_TRAIN} to train something that isn't just memorizing noise.")
        print("Rate more (job, evidence) pairs first - generate templates for more students")
        print("via human_validation_template.py, or increase --n_per_stratum, then re-run.")
        return

    print("\nLoading pipeline breakdown files to engineer features...")
    course_agg = pd.read_csv("course_job_aggregated.csv")
    match_log = pd.read_csv("pipeline_course_match_log.csv")
    cert_agg, certs_df = None, None
    try:
        cert_agg = pd.read_csv("cert_job_aggregated.csv")
        certs_df = pd.read_csv("certificates_parsed.csv")
    except FileNotFoundError:
        print("(no certificate files found - KHS-only features)")

    features = build_feature_table(ratings.rename(columns={"job_id": "job_id"}),
                                    course_agg, match_log, cert_agg, certs_df)
    data = features.merge(ratings[["job_id", "Rating (0-5)"]], on="job_id", how="inner")
    data = data.drop_duplicates(subset=["job_id"])  # a job rated in multiple files counted once for training

    feature_cols = [c for c in features.columns if c != "job_id"]
    X = data[feature_cols].fillna(0)
    y = data["Rating (0-5)"]

    print(f"\nTraining set: {len(X)} unique rated jobs, {len(feature_cols)} features")
    print(f"Features: {[FEATURE_LABELS.get(c, c) for c in feature_cols]}")

    model = xgb.XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.1,
                              subsample=0.9, random_state=42)

    # cross-validation instead of a single train/test split, since the dataset
    # is small and a single split's score would be noisy and easy to overclaim from
    n_folds = min(5, len(X) // 6) if len(X) >= 30 else 3
    n_folds = max(n_folds, 2)
    cv = KFold(n_splits=n_folds, shuffle=True, random_state=42)
    r2_scores = cross_val_score(model, X, y, cv=cv, scoring="r2")
    mae_scores = -cross_val_score(model, X, y, cv=cv, scoring="neg_mean_absolute_error")

    report_lines = [
        f"Ratings used: {len(X)} (from {ratings['source_file'].nunique()} rated file(s))",
        f"Cross-validation: {n_folds}-fold",
        f"R^2  = {r2_scores.mean():.3f} +/- {r2_scores.std():.3f}  (per-fold: {np.round(r2_scores, 3).tolist()})",
        f"MAE  = {mae_scores.mean():.3f} +/- {mae_scores.std():.3f}  (on a 0-5 rating scale)",
    ]
    print("\n=== Cross-validated fit quality (HONEST report - this is what generalizes) ===")
    for line in report_lines:
        print(line)

    if r2_scores.mean() < 0.3:
        report_lines.append(
            "\nWARNING: R^2 is low. With this few ratings and this feature set, the model is "
            "not reliably predicting human judgment yet. Either collect more ratings, add "
            "features that better capture what raters are reacting to, or continue reporting "
            "the hand-weighted formula (final_score) as the primary system, with this as "
            "exploratory work-in-progress rather than a validated replacement."
        )
        print(report_lines[-1])

    with open("ensemble_ranker_cv_report.txt", "w") as f:
        f.write("\n".join(report_lines))
    print("\nSaved: ensemble_ranker_cv_report.txt")

    # fit on ALL data for the final saved model (CV above already gave the honest
    # generalization estimate - refitting on everything just maximizes use of what
    # little data exists for the model you'll actually use downstream)
    model.fit(X, y)
    model.save_model("ensemble_ranker_model.json")
    print("Saved: ensemble_ranker_model.json")
    print("\nTo explain this model's predictions with SHAP, adapt shap_explainability.py:")
    print("  load this model instead of fitting a fresh surrogate, and run shap.TreeExplainer")
    print("  on it directly - the feature engineering code is already shared via build_feature_table().")


if __name__ == "__main__":
    main()
