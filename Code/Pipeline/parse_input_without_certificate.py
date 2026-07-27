import re
import pandas as pd

GRADE_MAP = {"A": 0.85, "AB": 0.80, "B": 0.70, "BC": 0.60, "C": 0.55, "D": 0.50, "E": 0.0}


# ---------------------------------------------------------------------------
# Helper: parse a GitHub-flavored markdown table into list[dict]
# ---------------------------------------------------------------------------
def _parse_markdown_table(table_text):
    lines = [l.strip() for l in table_text.strip().splitlines() if l.strip()]
    if len(lines) < 2:
        return []
    header = [h.strip() for h in lines[0].strip("|").split("|")]
    rows = []
    for line in lines[2:]:  # skip header row + separator row
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != len(header):
            continue
        rows.append(dict(zip(header, cells)))
    return rows


# ---------------------------------------------------------------------------
# CV extraction (from markdown, no AI needed)
# ---------------------------------------------------------------------------
def extract_cv_units(cv_md_path):
    """
    Split a generated CV.md into discrete competency units - one per project,
    internship, or capstone entry under '## Professional Projects'.

    Returns a list of dicts: [{"title": ..., "description": ...}, ...]
    """
    with open(cv_md_path, encoding="utf-8") as f:
        text = f.read()

    match = re.search(
        r"## Professional Projects\n\n(.*?)\n---\n\n## Certifications",
        text, re.DOTALL,
    )
    if not match:
        raise ValueError(f"Could not find 'Professional Projects' section in {cv_md_path}")
    section = match.group(1)

    units = []
    blocks = re.split(r"\n### ", "\n### " + section.strip())
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        title = lines[0].lstrip("#").strip()
        rest = "\n".join(lines[1:]).strip()
        description = re.split(r"\n#### Key Contributions", rest)[0].strip()
        units.append({"title": title, "description": description})
    return units


# ---------------------------------------------------------------------------
# KHS extraction (from markdown, no AI needed) - grain: 1 row = 1 CLO
# ---------------------------------------------------------------------------
def parse_khs_md(khs_md_path):
    """
    Parse a generated KHS.md into a per-CLO grained DataFrame.

    Returns a DataFrame with columns:
        kode_mk, nama_mk, sks, semester, nilai_akhir_mk,
        clo_code, clo_desc, bloom, score, nilai_clo, grade_weight
    """
    with open(khs_md_path, encoding="utf-8") as f:
        text = f.read()

    # 1. sks/semester per course from the summary table
    summary_match = re.search(
        r"## Ringkasan Nilai per Mata Kuliah\n\n(.*?)\n\n---", text, re.DOTALL,
    )
    course_meta = {}
    if summary_match:
        for row in _parse_markdown_table(summary_match.group(1)):
            course_meta[row["Kode MK"]] = {
                "sks": row["SKS"],
                "semester": row["Semester"],
            }

    # 2. per-CLO detail sections
    detail_match = re.search(
        r"## Rincian Nilai per CLO \(Course Learning Outcome\)\n\n(.*)$", text, re.DOTALL,
    )
    if not detail_match:
        raise ValueError(f"Could not find CLO detail section in {khs_md_path}")
    detail_text = detail_match.group(1)

    header_re = re.compile(
        r"^(?P<nama_mk>.+?) \((?P<kode_mk>[^)]+)\) - (?P<sks>\d+) SKS - Nilai Akhir: (?P<nilai>\S+)"
    )

    rows = []
    course_blocks = re.split(r"\n### ", "\n### " + detail_text.strip())
    for block in course_blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        header_line = lines[0].lstrip("#").strip()
        m = header_re.match(header_line)
        if not m:
            continue  # e.g. the trailing "*Catatan: ...*" footer, skip it

        nama_mk = m.group("nama_mk").strip()
        kode_mk = m.group("kode_mk").strip()
        sks = int(m.group("sks"))
        nilai_akhir_mk = m.group("nilai").strip()
        semester = course_meta.get(kode_mk, {}).get("semester")

        table_text = "\n".join(lines[1:])
        for clo_row in _parse_markdown_table(table_text):
            rows.append({
                "kode_mk": kode_mk,
                "nama_mk": nama_mk,
                "sks": sks,
                "semester": semester,
                "nilai_akhir_mk": nilai_akhir_mk,
                "clo_code": clo_row.get("CLO"),
                "clo_desc": clo_row.get("Deskripsi CLO"),
                "bloom": clo_row.get("Bloom Taxonomy"),
                "score": clo_row.get("Skor CLO (0-100)"),
                "nilai_clo": clo_row.get("Nilai CLO"),
            })

    df = pd.DataFrame(rows)
    df["nilai_clo"] = df["nilai_clo"].str.upper().str.strip()
    df["grade_weight"] = df["nilai_clo"].map(GRADE_MAP)
    if df["grade_weight"].isna().any():
        bad = df[df["grade_weight"].isna()]
        print(f"WARNING: {len(bad)} rows had unrecognized grades and were dropped:")
        print(bad)
        df = df.dropna(subset=["grade_weight"])
    return df


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--khs_md", required=True)
    parser.add_argument("--cv_md", required=True)
    parser.add_argument("--out_khs_csv", default="transcript_parsed.csv")
    parser.add_argument("--out_cv_units_csv", default="cv_units_parsed.csv")
    args = parser.parse_args()

    khs_df = parse_khs_md(args.khs_md)
    khs_df.to_csv(args.out_khs_csv, index=False)
    print(f"Saved {len(khs_df)} CLO rows -> {args.out_khs_csv}")

    cv_units = extract_cv_units(args.cv_md)
    cv_units_df = pd.DataFrame(cv_units)
    cv_units_df["cv_unit_id"] = ["cv_unit_" + str(i) for i in range(len(cv_units_df))]
    cv_units_df.to_csv(args.out_cv_units_csv, index=False)
    print(f"Saved {len(cv_units_df)} CV units -> {args.out_cv_units_csv}")