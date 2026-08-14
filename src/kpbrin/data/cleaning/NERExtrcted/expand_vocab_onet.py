# -*- coding: utf-8 -*-
"""
Expand skill_vocabulary.py aliases using the O*NET Technology Skills database.

WHAT THIS DOES:
Downloads O*NET's Technology Skills flat file (real software/tool names
tagged per occupation, sourced from actual employer job postings - this is
exactly the vocabulary gap dictionary-matching struggles with). Filters to
IT/Computer-related O*NET-SOC codes (15-xxxx = Computer & Mathematical,
17-2061 = Computer Hardware Engineers, 11-3021 = Computer/IS Managers).

Then buckets each technology name into one of our 78 canonical skills using
keyword rules, and writes TWO output files:
  1. onet_alias_suggestions.json  - terms successfully bucketed (review, then
     merge into SKILL_VOCAB aliases in skill_vocabulary.py)
  2. onet_unmapped_terms.txt      - terms that didn't match ANY canonical
     skill. This is actually valuable: it may reveal skill categories
     missing from your RPS-derived catalog entirely (e.g. cloud/DevOps
     tools like AWS, Docker, Kubernetes are common in job postings but
     might not exist as a "Skill Domain" in your RPS yet).

REQUIREMENTS: run this on your machine (onetcenter.org is not reachable
from Claude's sandbox).
  pip install requests

USAGE:
  python expand_vocab_onet.py
"""

import re
import json
import requests
from collections import defaultdict
from skill_vocabulary import SKILL_VOCAB

# O*NET 30.3 Technology Skills flat file (tab-delimited)
ONET_TECH_SKILLS_URL = "https://www.onetcenter.org/dl_files/database/db_30_3_text/Software%20Skills.txt"

# SOC code prefixes relevant to Sistem Informasi / Data Science roles
IT_RELEVANT_SOC_PREFIXES = (
    "15-",       # Computer and Mathematical Occupations
    "11-3021",   # Computer and Information Systems Managers
    "17-2061",   # Computer Hardware Engineers
)

# Keyword -> canonical skill bucketing rules.
# (keyword is matched case-insensitively as a substring of the O*NET "Example" text)
# Expanded from real terms found in O*NET's Technology Skills database (IT-relevant SOC codes).
BUCKET_RULES = {
    # Database Systems
    "SQL": ["sql", "mysql", "postgresql", "sql server", "oracle db", "nosql"],
    "Database Design": ["erd", "entity relation", "database design"],
    "Normalization": ["normalization"],
    "Query Optimization": ["query optimiz", "query tuning"],

    # Object-Oriented Programming / Programming & Algorithm
    "Java/Python": ["python", " java", "java\t", "c++", "c#", "kotlin", "swift", "ruby", "perl",
                    "j2ee", "jsp", "servlet", "jms"],
    "Algorithm Design": ["algorithm"],

    # Web Development
    "Web Framework": ["react", "angular", "vue", "node.js", "django", "flask", "spring",
                       "laravel", "ruby on rails"],
    "Backend Development": ["node.js", "django", "flask", "spring boot", "express"],

    # Software Engineering
    "Version Control": ["git", "github", "gitlab", "bitbucket", "subversion"],
    "CI/CD": ["jenkins", "ci/cd", "github actions", "gitlab ci", "circleci", "azure devops"],
    "Software Testing": ["unit testing software", "test automat", "testcomplete", "selenium",
                          "quality assurance", "qa software"],

    # Data Warehouse & BI
    "Dashboard & Reporting": ["tableau", "power bi", "qlik", "looker", "crystal reports",
                              "business intelligence"],
    "ETL Process": ["etl", "informatica", "talend", "airflow", "data integrat"],
    "OLAP": ["olap", "data warehouse", "warehouse miner"],

    # Intelligent Systems
    "Machine Learning": ["tensorflow", "pytorch", "scikit", "machine learning", "keras",
                          "sagemaker"],
    "Neural Network": ["neural network", "deep learning"],
    "AI Application": ["artificial intelligence", "cognitive computing"],

    # Operating Systems
    "Linux Administration": ["linux", "unix", "shell script", "bash", "red hat"],
    "Process Management": ["process management software"],

    # Information Security
    "Cryptography": ["encryption", "cryptography", "pki"],
    "Cybersecurity": ["firewall", "antivirus", "mcafee", "symantec", "vpn", "endpoint protection"],
    "Risk Assessment": ["risk assessment software", "vulnerability assessment",
                        "penetration testing"],
    "Security Audit": ["security auditing software", "iso 27001", "soc 2"],

    # Computer Networking
    "Network Security": ["network security", "firewall software", "vpn software"],
    "TCP/IP Protocol": ["tcp/ip", "domain name system", "dns", "dynamic host configuration",
                        "dhcp"],

    # Enterprise Systems
    "ERP": ["erp", "enterprise resource planning"],
    "SAP/Oracle": ["sap ", "netsuite", "jd edwards", "infor erp", "oracle enterprise"],

    # Enterprise Integration
    "Web Services": ["enterprise application integration", "eai", "web services", "soap"],

    # IT Project Management
    "Agile/Scrum": ["agile", "scrum", "kanban"],
    "WBS & Scheduling": ["microsoft project", "ganttproject", "gantt", "smartsheet",
                        "primavera"],
    "Risk Management": ["risk management software"],

    # IT Governance
    "COBIT": ["cobit"],
    "ITIL": ["itil", "it service management"],
    "IT Performance Audit": ["it audit software", "performance audit"],

    # Enterprise Architecture
    "TOGAF": ["togaf"],
    "EA Framework": ["enterprise architecture"],
    "Architecture Modeling": ["system architect", "popkin system architect"],

    # Systems Analysis & Design
    "UML Modeling": ["unified modeling language", " uml"],
    "Requirements Engineering": ["requirements analysis software", "requirements management",
                                "requirements composer"],

    # Interaction Design
    "UI Prototyping": ["figma", "adobe xd", "sketch", "prototyping software"],
    "Wireframing": ["wireframe"],
    "UX Research": ["user research software"],
    "Usability Testing": ["usability testing software"],
}


def download_technology_skills():
    local_file = "Software Skills.txt"

    try:
        with open(local_file, "r", encoding="utf-8") as f:
            print(f"Using local file: {local_file}")
            return f.read()
    except FileNotFoundError:
        pass

    print(f"Downloading {ONET_TECH_SKILLS_URL} ...")
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    resp = requests.get(ONET_TECH_SKILLS_URL, headers=headers, timeout=60)
    resp.raise_for_status()
    return resp.text


def parse_and_filter(raw_text):
    lines = raw_text.strip().split("\n")
    header = lines[0].split("\t")
    rows = [line.split("\t") for line in lines[1:]]

    filtered = []
    for row in rows:
        if len(row) < 6:
            continue

        soc_code, example, element_id, element_name, hot_tech, in_demand = row[:6]

        if any(soc_code.startswith(p) for p in IT_RELEVANT_SOC_PREFIXES):
            filtered.append({
                "soc_code": soc_code,
                "example": example,
                "commodity_title": element_name,
                "hot_technology": hot_tech.strip() == "Y",
                "in_demand": in_demand.strip() == "Y",
            })

    return filtered


def bucket_terms(filtered_rows):
    bucketed = defaultdict(set)
    unmapped = set()

    unique_examples = {row["example"] for row in filtered_rows}

    for term in unique_examples:
        term_lower = term.lower()
        matched_any = False
        for canonical, keywords in BUCKET_RULES.items():
            if canonical not in SKILL_VOCAB:
                continue  # safety check
            if any(kw in term_lower for kw in keywords):
                bucketed[canonical].add(term)
                matched_any = True
        if not matched_any:
            unmapped.add(term)

    return bucketed, unmapped


def main():
    raw_text = download_technology_skills()
    filtered_rows = parse_and_filter(raw_text)
    print(f"IT-relevant technology skill rows: {len(filtered_rows)}")

    bucketed, unmapped = bucket_terms(filtered_rows)

    suggestions = {k: sorted(v) for k, v in bucketed.items()}
    with open("onet_alias_suggestions.json", "w", encoding="utf-8") as f:
        json.dump(suggestions, f, indent=2, ensure_ascii=False)
    print(f"Bucketed suggestions -> onet_alias_suggestions.json ({sum(len(v) for v in suggestions.values())} terms)")

    with open("onet_unmapped_terms.txt", "w", encoding="utf-8") as f:
        for term in sorted(unmapped):
            f.write(term + "\n")
    print(f"Unmapped terms -> onet_unmapped_terms.txt ({len(unmapped)} terms)")
    print("\nTip: skim onet_unmapped_terms.txt - frequently occurring terms there")
    print("(e.g. cloud/DevOps tools) may indicate a skill category missing from")
    print("your RPS-derived Skill Catalogue entirely, not just a missing alias.")


if __name__ == "__main__":
    main()