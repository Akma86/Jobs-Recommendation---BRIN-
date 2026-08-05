TIER_WEIGHTS = {
    "TIER_A": 1.0,
    "TIER_B": 0.7,
    "TIER_C": 0.5,
    "TIER_D": 0.3,  # fallback for unrecognized issuers
}

ISSUER_TIERS = {
    "TIER_A": [
        "google", "aws", "amazon web services", "microsoft", "ibm", "meta",
        "nvidia", "databricks", "oracle", "cisco", "salesforce",
        "bnsp", "lsp",  # Indonesian national professional certification body
        "kominfo",       # Ministry of Communication and Informatics (govt-issued)
    ],
    "TIER_B": [
        "dicoding",          # widely recognized in Indonesia, MSIB-partnered
        "dqlab",
        "data science indonesia",
        "coursera",           # only when NOT already caught by a Tier A partner name above
        "datacamp",
        "udacity",
        "edx",
        "hackerrank",
        "linkedin learning",
    ],
    "TIER_C": [
        "udemy", "skillshare", "udemy business", "codecademy",
    ],
}


def get_issuer_weight(issuer_name):
    """
    Case-insensitive substring match against ISSUER_TIERS. Checks Tier A
    first (most specific/high-value names), then B, then C. Falls back to
    Tier D weight if nothing matches.

    NOTE: order matters for overlapping names - e.g. a cert that says
    "Google via Coursera" will match Tier A ("google") before it gets a
    chance to match Tier B ("coursera"), since Tier A is checked first.
    This is intentional: the actual content-provider (Google) matters more
    than the hosting platform (Coursera).
    """
    if not isinstance(issuer_name, str):
        return TIER_WEIGHTS["TIER_D"], "TIER_D (unrecognized/missing issuer)"

    name_lower = issuer_name.lower()
    for tier in ["TIER_A", "TIER_B", "TIER_C"]:
        for keyword in ISSUER_TIERS[tier]:
            if keyword in name_lower:
                return TIER_WEIGHTS[tier], f"{tier} (matched '{keyword}')"

    return TIER_WEIGHTS["TIER_D"], "TIER_D (issuer not in lookup table - unverified)"


# ---------------------------------------------------------------------------
# Composite credibility weight: issuer tier x assessment x recency
# ---------------------------------------------------------------------------
# WHY THESE TWO EXTRA FACTORS: issuer tier alone only captures "who could be
# trusted to run a rigorous program in general" - it says nothing about
# whether THIS SPECIFIC certificate reflects verified competency (vs just
# showing up) or whether the skills are still current. Both are objective,
# checkable from the certificate itself (unlike issuer prestige, which is
# a judgment call) - so they're kept as separate multipliers rather than
# folded into the subjective tier table.

ASSESSMENT_BONUS = 1.0       # multiplier when has_assessment == True
NO_ASSESSMENT_PENALTY = 0.7  # multiplier when has_assessment == False (attendance-only)
UNKNOWN_ASSESSMENT_PENALTY = 0.85  # multiplier when has_assessment couldn't be determined

RECENCY_HALF_LIFE_YEARS = 3.0  # a cert loses half its recency weight every N years
                                 # (tech/tools skills age faster than e.g. a formal degree -
                                 #  adjust per field if defending a different domain)


def get_recency_weight(issue_date_str, reference_date=None):
    """
    Exponential decay by certificate age: weight = 0.5 ** (age_years / half_life).
    Missing/unparseable dates get weight 1.0 (benefit of the doubt - NOT
    penalized for missing metadata, only for being verifiably OLD), but this
    is flagged in the reason string so you can audit which certs are being
    trusted "blind" on recency.
    """
    import datetime
    reference_date = reference_date or datetime.date.today()

    if not isinstance(issue_date_str, str) or not issue_date_str.strip():
        return 1.0, "no issue_date - assumed recent (unverified)"

    parsed = None
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            parsed = datetime.datetime.strptime(issue_date_str.strip(), fmt).date()
            break
        except ValueError:
            continue
    if parsed is None:
        return 1.0, f"unparseable issue_date '{issue_date_str}' - assumed recent (unverified)"

    age_years = (reference_date - parsed).days / 365.25
    if age_years < 0:
        return 1.0, "issue_date is in the future - treated as recent"

    weight = 0.5 ** (age_years / RECENCY_HALF_LIFE_YEARS)
    return round(weight, 3), f"{age_years:.1f} years old"


def get_certificate_credibility_weight(issuer_name, has_assessment, issue_date_str):
    """
    Composite weight combining all three factors. Returns (weight, breakdown_dict)
    so the pipeline can show a full explanation, not just a number.
    """
    issuer_w, issuer_reason = get_issuer_weight(issuer_name)

    if has_assessment is True:
        assess_w, assess_reason = ASSESSMENT_BONUS, "has assessment/exam/project"
    elif has_assessment is False:
        assess_w, assess_reason = NO_ASSESSMENT_PENALTY, "attendance-only, no assessment"
    else:
        assess_w, assess_reason = UNKNOWN_ASSESSMENT_PENALTY, "assessment status unknown"

    recency_w, recency_reason = get_recency_weight(issue_date_str)

    total = round(issuer_w * assess_w * recency_w, 4)
    breakdown = {
        "issuer_weight": issuer_w, "issuer_reason": issuer_reason,
        "assessment_weight": assess_w, "assessment_reason": assess_reason,
        "recency_weight": recency_w, "recency_reason": recency_reason,
        "total_credibility_weight": total,
    }
    return total, breakdown


if __name__ == "__main__":
    # quick smoke test
    test_issuers = ["Google Cloud", "PT Dicoding Indonesia", "Udemy", "Seminar Nasional Kampus X", "AWS"]
    for name in test_issuers:
        weight, reason = get_issuer_weight(name)
        print(f"{name!r:40s} -> weight={weight}  ({reason})")

    print("\n--- composite example ---")
    total, breakdown = get_certificate_credibility_weight("Google Cloud", True, "2024-06-01")
    print(f"Google Cloud, assessed, mid-2024: total={total}")
    print(breakdown)
    total, breakdown = get_certificate_credibility_weight("Seminar Kampus", False, "2021-01-01")
    print(f"\nRandom seminar, no assessment, 2021: total={total}")
    print(breakdown)
