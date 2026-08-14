# -*- coding: utf-8 -*-
"""
Expand skill_vocabulary.py aliases using the ESCO API. (v2 - fixed)

WHAT CHANGED FROM v1:
1. Our canonical skill names (e.g. "AIS Design", "Architecture Modeling") are
   internal category labels, not real-world search terms -> ESCO's fuzzy
   text search returned noise. We now search using a cleaner, more literal
   term per skill (SEARCH_TERM_OVERRIDES below).
2. The /search endpoint doesn't populate altLabels -> we now fetch each
   matched skill's full detail via /resource/skill?uri=... to get altLabels.
3. Added a basic relevance filter: skip a match if it shares no words with
   the search term, to cut down on obviously irrelevant results.

REQUIREMENTS: run this on your machine (ec.europa.eu not reachable from
Claude's sandbox).
  pip install requests

USAGE:
  python expand_vocab_esco.py
  -> produces esco_alias_suggestions.json (REVIEW before merging into
     skill_vocabulary.py - ESCO matching is still fuzzy for some terms)
"""

import json
import time
import requests
from skill_vocabulary import SKILL_VOCAB

ESCO_SEARCH_URL = "https://ec.europa.eu/esco/api/search"
ESCO_RESOURCE_URL = "https://ec.europa.eu/esco/api/resource/skill"

# Cleaner, more literal search terms for skills whose canonical name is an
# internal category label rather than a real-world term. Skills not listed
# here just use their own name as the search term.
SEARCH_TERM_OVERRIDES = {
    "AIS Design": "accounting information system",
    "API Design": "application programming interface",
    "Architecture Modeling": "software architecture",
    "Class Design": "object oriented design",
    "Decision Tree/KNN/SVM": "machine learning algorithms",
    "Java/Python": "programming languages",
    "SAP/Oracle": "enterprise resource planning software",
    "Web Framework": "web development framework",
    "BPR Methodology": "business process reengineering",
    "EA Framework": "enterprise architecture",
    "WBS & Scheduling": "project scheduling",
    "Use Case Design": "use case analysis",
    "OOP Principles": "object oriented programming",
}


def search_esco_skill(term, language="en", limit=5):
    params = {"text": term, "type": "skill", "language": language, "limit": limit}
    resp = requests.get(ESCO_SEARCH_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("_embedded", {}).get("results", [])


def fetch_alt_labels(uri, language="en"):
    """Fetch the full skill resource to get altLabels (not present in /search results)."""
    params = {"uri": uri, "language": language}
    resp = requests.get(ESCO_RESOURCE_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    alt_labels = data.get("altLabels", {})
    if isinstance(alt_labels, dict):
        return alt_labels.get(language, [])
    return alt_labels or []


def is_relevant(search_term, preferred_label):
    """Basic filter: keep only matches sharing at least one meaningful word."""
    search_words = {w.lower() for w in search_term.split() if len(w) > 3}
    label_words = {w.lower() for w in preferred_label.split() if len(w) > 3}
    return bool(search_words & label_words) or search_term.lower() in preferred_label.lower()


def main():
    suggestions = {}
    canonical_skills = sorted(SKILL_VOCAB.keys())

    for i, skill in enumerate(canonical_skills):
        search_term = SEARCH_TERM_OVERRIDES.get(skill, skill)
        print(f"[{i+1}/{len(canonical_skills)}] '{skill}' -> searching ESCO for: '{search_term}'")

        try:
            results = search_esco_skill(search_term)
        except requests.exceptions.RequestException as e:
            print(f"  search failed: {e}")
            suggestions[skill] = {"error": str(e)}
            continue

        matches = []
        for item in results:
            preferred_label = item.get("title") or item.get("preferredLabel", "")
            if not is_relevant(search_term, preferred_label):
                continue
            uri = item.get("uri")
            try:
                alt_labels = fetch_alt_labels(uri)
            except requests.exceptions.RequestException:
                alt_labels = []
            matches.append({
                "uri": uri,
                "preferredLabel": preferred_label,
                "altLabels": alt_labels,
            })
            time.sleep(0.2)

        suggestions[skill] = matches
        time.sleep(0.3)

    with open("esco_alias_suggestions.json", "w", encoding="utf-8") as f:
        json.dump(suggestions, f, indent=2, ensure_ascii=False)

    total_aliases = sum(
        len(a.get("altLabels", [])) for v in suggestions.values() if isinstance(v, list) for a in v
    )
    print(f"\nDone. {total_aliases} alternative labels found across all skills.")
    print("Review esco_alias_suggestions.json, then manually add good altLabels")
    print("into SKILL_VOCAB[<skill>]['aliases'] in skill_vocabulary.py")


if __name__ == "__main__":
    main()