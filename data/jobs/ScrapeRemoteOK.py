"""
Scraper multi-source untuk job IT & Sistem Informasi (SI).
Sumber (semua public API, gratis, no API key):
  1. RemoteOK   -> https://remoteok.com/api
  2. Remotive   -> https://remotive.com/api/remote-jobs
  3. Arbeitnow  -> https://www.arbeitnow.com/api/job-board-api
  4. Jobicy     -> https://jobicy.com/api/v2/remote-jobs

Auto-loop: script jalan terus, scrape ulang tiap X menit,
dedupe otomatis, berhenti sendiri kalau target tercapai.
"""

import requests
import json
import time
import os

OUTPUT_FILE = "all_jobs.json"
TARGET_COUNT = 1000
INTERVAL_SECONDS = 60 * 15  # jeda antar scrape (15 menit). Ubah sesuai kebutuhan.

IT_KEYWORDS = [
    "developer", "engineer", "software", "web", "frontend", "backend",
    "fullstack", "full stack", "data", "ai", "machine learning", "ml",
    "artificial intelligence", "devops", "cloud", "python", "javascript",
    "react", "node", "sql", "data scientist", "data analyst", "data engineer",
    "cybersecurity", "security", "mobile", "ios", "android", "qa", "sre",
    "infrastructure", "database", "nlp", "computer vision", "golang", "java",
    "ruby", "php", "typescript", "kubernetes", "docker", "aws", "azure", "gcp",
]

SISFO_KEYWORDS = [
    "business analyst", "system analyst", "systems analyst",
    "business systems analyst", "it project manager", "project manager",
    "product manager", "product owner", "scrum master",
    "erp", "sap", "crm", "scm", "enterprise resource planning",
    "customer relationship management", "supply chain",
    "it consultant", "information systems", "information system",
    "it governance", "it audit", "digital transformation",
    "business intelligence", "bi analyst", "bi developer",
    "process analyst", "process improvement", "requirements analyst",
    "solutions architect", "solution architect", "erp consultant",
    "sap consultant", "functional consultant", "technical consultant",
    "ux researcher", "ux designer", "ui/ux", "hci",
    "e-commerce", "ecommerce", "e-business",
    "salesforce", "netsuite", "workday", "oracle ebs",
    "agile coach", "delivery manager", "program manager",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}


# ---------------- FETCHERS PER SOURCE ----------------

def fetch_remoteok():
    try:
        resp = requests.get("https://remoteok.com/api", headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        jobs = [item for item in data if isinstance(item, dict) and "position" in item]
        return [
            {
                "id": f"remoteok_{j.get('id')}",
                "name": j.get("position") or j.get("title"),
                "company": j.get("company"),
                "skills": ", ".join(j.get("tags", [])),
                "description": (j.get("description") or "").strip(),
                "location": j.get("location"),
                "url": j.get("url"),
                "source": "RemoteOK",
            }
            for j in jobs
        ]
    except Exception as e:
        print(f"[RemoteOK] gagal fetch: {e}")
        return []


def fetch_remotive():
    try:
        resp = requests.get("https://remotive.com/api/remote-jobs", headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        jobs = data.get("jobs", [])
        return [
            {
                "id": f"remotive_{j.get('id')}",
                "name": j.get("title"),
                "company": j.get("company_name"),
                "skills": j.get("category", ""),
                "description": (j.get("description") or "").strip(),
                "location": j.get("candidate_required_location"),
                "url": j.get("url"),
                "source": "Remotive",
            }
            for j in jobs
        ]
    except Exception as e:
        print(f"[Remotive] gagal fetch: {e}")
        return []


def fetch_arbeitnow():
    try:
        resp = requests.get("https://www.arbeitnow.com/api/job-board-api", headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        jobs = data.get("data", [])
        return [
            {
                "id": f"arbeitnow_{j.get('slug')}",
                "name": j.get("title"),
                "company": j.get("company_name"),
                "skills": ", ".join(j.get("tags", [])),
                "description": (j.get("description") or "").strip(),
                "location": j.get("location"),
                "url": j.get("url"),
                "source": "Arbeitnow",
            }
            for j in jobs
        ]
    except Exception as e:
        print(f"[Arbeitnow] gagal fetch: {e}")
        return []


def fetch_jobicy():
    try:
        resp = requests.get("https://jobicy.com/api/v2/remote-jobs?count=200", headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        jobs = data.get("jobs", [])
        return [
            {
                "id": f"jobicy_{j.get('id')}",
                "name": j.get("jobTitle"),
                "company": j.get("companyName"),
                "skills": ", ".join(j.get("jobIndustry", []) or []),
                "description": (j.get("jobExcerpt") or "").strip(),
                "location": j.get("jobGeo"),
                "url": j.get("url"),
                "source": "Jobicy",
            }
            for j in jobs
        ]
    except Exception as e:
        print(f"[Jobicy] gagal fetch: {e}")
        return []


SOURCES = [fetch_remoteok, fetch_remotive, fetch_arbeitnow, fetch_jobicy]


# ---------------- FILTER & KLASIFIKASI ----------------

def match_keywords(text: str, keywords: list) -> bool:
    text = text.lower()
    return any(kw.lower() in text for kw in keywords)


def is_it_related(job: dict) -> bool:
    text = (job.get("name") or "") + " " + (job.get("skills") or "")
    return match_keywords(text, IT_KEYWORDS)


def is_sisfo_related(job: dict) -> bool:
    text = (
        (job.get("name") or "") + " " +
        (job.get("skills") or "") + " " +
        (job.get("description") or "")
    )
    return match_keywords(text, SISFO_KEYWORDS)


def classify_job(job: dict) -> str:
    it_match = is_it_related(job)
    sisfo_match = is_sisfo_related(job)
    if it_match and sisfo_match:
        return "IT & SI"
    elif it_match:
        return "IT"
    elif sisfo_match:
        return "SI"
    return "Lainnya"


# ---------------- PENYIMPANAN ----------------

def load_existing(filename=OUTPUT_FILE) -> dict:
    if not os.path.exists(filename):
        return {}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {j["id"]: j for j in data if j.get("id") is not None}
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_to_json(jobs_dict: dict, filename=OUTPUT_FILE):
    jobs_list = list(jobs_dict.values())
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(jobs_list, f, ensure_ascii=False, indent=2)


# ---------------- SATU SIKLUS SCRAPE ----------------

def scrape_once():
    all_raw = []
    for fetch_fn in SOURCES:
        jobs = fetch_fn()
        print(f"  -> {fetch_fn.__name__}: {len(jobs)} job diambil")
        all_raw.extend(jobs)
        time.sleep(1)  # jeda antar sumber, sopan ke server

    new_matches = {}
    for j in all_raw:
        if is_it_related(j) or is_sisfo_related(j):
            j["category"] = classify_job(j)
            if j.get("id") is not None:
                new_matches[j["id"]] = j

    existing = load_existing()
    before = len(existing)
    existing.update(new_matches)
    after = len(existing)

    save_to_json(existing)

    counts = {}
    for j in existing.values():
        counts[j["category"]] = counts.get(j["category"], 0) + 1

    print(f"  Job IT/SI match di run ini      : {len(new_matches)}")
    print(f"  Job baru ditambahkan             : {after - before}")
    print(f"  Total job unik terkumpul sekarang: {after}")
    print(f"  Ringkasan kategori kumulatif     : {counts}")

    return after


# ---------------- AUTO LOOP ----------------

def main():
    print(f"Target: {TARGET_COUNT} job. Interval scrape: {INTERVAL_SECONDS//60} menit.")
    print("Tekan Ctrl+C kapan aja buat stop manual.\n")

    round_num = 1
    while True:
        print(f"=== Round {round_num} ===")
        total = scrape_once()
        print()

        if total >= TARGET_COUNT:
            print(f"✅ Target {TARGET_COUNT} job tercapai! Total akhir: {total}")
            break

        sisa = TARGET_COUNT - total
        print(f"⚠️  Baru {total} job, butuh {sisa} lagi. Nunggu {INTERVAL_SECONDS//60} menit sebelum scrape ulang...\n")

        try:
            time.sleep(INTERVAL_SECONDS)
        except KeyboardInterrupt:
            print("\nDihentikan manual oleh user.")
            break

        round_num += 1


if __name__ == "__main__":
    main()