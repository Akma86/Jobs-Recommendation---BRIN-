import os
import re
import json
import base64
import io
import pandas as pd
from pypdf import PdfReader

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
# KHS extraction (Markdown, Course-level)
# ---------------------------------------------------------------------------
def parse_khs_markdown(md_path):
    rows = []
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    in_course_table = False
    for line in lines:
        if "| No | Kode MK | Nama Mata Kuliah | SKS | Semester | Nilai Akhir |" in line:
            in_course_table = True
            continue
        if not in_course_table:
            continue
        if line.strip() == "---":
            break
        if not line.startswith("|"):
            continue
        if "----" in line:
            continue
        parts = [p.strip() for p in line.strip().split("|")[1:-1]]
        if len(parts) != 6:
            continue
        try:
            rows.append({
                "kode_mk": parts[1],
                "nama_mk": parts[2],
                "sks": int(parts[3]),
                "nilai_huruf": parts[5].upper().strip()
            })
        except Exception:
            continue
    if not rows:
        raise ValueError(f"Gagal menemukan tabel mata kuliah pada markdown: {md_path}")
    df = pd.DataFrame(rows)
    df["grade_weight"] = df["nilai_huruf"].map(GRADE_MAP)
    if df["grade_weight"].isna().any():
        bad = df[df["grade_weight"].isna()]
        print(f"WARNING: {len(bad)} rows had unrecognized grades:")
        print(bad)
        df = df.dropna(subset=["grade_weight"])
    return df

# ---------------------------------------------------------------------------
# KHS extraction (Markdown, CLO-level)
# ---------------------------------------------------------------------------
def parse_khs_md_clo(khs_md_path):
    with open(khs_md_path, encoding="utf-8") as f:
        text = f.read()

    summary_match = re.search(r"## Ringkasan Nilai per Mata Kuliah\n\n(.*?)\n\n---", text, re.DOTALL)
    course_meta = {}
    if summary_match:
        for row in _parse_markdown_table(summary_match.group(1)):
            course_meta[row["Kode MK"]] = {
                "sks": row["SKS"],
                "semester": row["Semester"],
            }

    detail_match = re.search(r"## Rincian Nilai per CLO \(Course Learning Outcome\)\n\n(.*)$", text, re.DOTALL)
    if not detail_match:
        raise ValueError(f"Could not find CLO detail section in {khs_md_path}")
    detail_text = detail_match.group(1)

    header_re = re.compile(r"^(?P<nama_mk>.+?) \((?P<kode_mk>[^)]+)\) - (?P<sks>\d+) SKS - Nilai Akhir: (?P<nilai>\S+)")

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
            continue

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

# ---------------------------------------------------------------------------
# KHS extraction: auto-detect text layer vs scanned (PDF)
# ---------------------------------------------------------------------------
def _has_text_layer(pdf_path):
    reader = PdfReader(pdf_path)
    sample_text = "".join(page.extract_text() or "" for page in reader.pages[:1])
    return len(sample_text.strip()) > 30

def _parse_khs_text_based(pdf_path):
    import pdfplumber
    rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                for row in table:
                    rows.append(row)
    raise NotImplementedError(
        "Text-based KHS table found, but column mapping is institution-specific. "
        "Inspect `rows` here and map to kode_mk/nama_mk/sks/nilai_huruf manually, "
        "or route it through the vision fallback (_parse_khs_vision) instead."
    )

def _pdf_pages_to_base64_images(pdf_path, dpi=200):
    import subprocess
    import tempfile
    import glob

    with tempfile.TemporaryDirectory() as tmpdir:
        prefix = os.path.join(tmpdir, "page")
        subprocess.run(
            ["pdftoppm", "-jpeg", "-r", str(dpi), pdf_path, prefix],
            check=True, capture_output=True,
        )
        image_paths = sorted(glob.glob(prefix + "*"))
        images_b64 = []
        for p in image_paths:
            with open(p, "rb") as f:
                images_b64.append(base64.standard_b64encode(f.read()).decode("utf-8"))
        return images_b64

def _parse_khs_vision(pdf_path, model="claude-sonnet-4-6"):
    import anthropic
    client = anthropic.Anthropic()
    images_b64 = _pdf_pages_to_base64_images(pdf_path)

    content = []
    for img_b64 in images_b64:
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": "image/jpeg", "data": img_b64},
        })
    content.append({
        "type": "text",
        "text": (
            "This is a Telkom University academic transcript (KHS/Daftar Nilai Hasil Studi). "
            "Extract EVERY course row from the 'Mata Kuliah yang Lulus' table across all pages. "
            "Respond with ONLY a JSON array (no markdown fences, no commentary), where each "
            "element has exactly these keys: "
            '"kode_mk" (course code), "nama_mk" (course name in Indonesian), '
            '"sks" (credit hours, as a number), "nilai_huruf" (letter grade, one of '
            'A, AB, B, BC, C, D, E). Do not include header rows or the SKS total row.'
        ),
    })

    response = client.messages.create(
        model=model,
        max_tokens=4000,
        messages=[{"role": "user", "content": content}],
    )

    raw_text = "".join(block.text for block in response.content if block.type == "text")
    raw_text = re.sub(r"^```json\s*|\s*```$", "", raw_text.strip())
    records = json.loads(raw_text)
    return pd.DataFrame(records)

def parse_khs_pdf(pdf_path):
    if _has_text_layer(pdf_path):
        print(f"'{pdf_path}' has a real text layer - using pdfplumber (no API needed).")
        df = _parse_khs_text_based(pdf_path)
    else:
        print(f"'{pdf_path}' appears to be scanned/rasterized - using Claude vision (needs ANTHROPIC_API_KEY).")
        df = _parse_khs_vision(pdf_path)

    df["nilai_huruf"] = df["nilai_huruf"].str.upper().str.strip()
    df["grade_weight"] = df["nilai_huruf"].map(GRADE_MAP)
    if df["grade_weight"].isna().any():
        bad = df[df["grade_weight"].isna()]
        print(f"WARNING: {len(bad)} rows had unrecognized grades and were dropped:")
        print(bad)
        df = df.dropna(subset=["grade_weight"])
    return df

def parse_khs(khs_path):
    ext = os.path.splitext(khs_path)[1].lower()
    if ext == ".md":
        print(f"Detected markdown KHS: {khs_path}")
        with open(khs_path, "r", encoding="utf-8") as f:
            content = f.read()
        if "## Rincian Nilai per CLO" in content:
            print("Detected CLO-level details in Markdown. Extracting at CLO granularity.")
            return parse_khs_md_clo(khs_path)
        else:
            print("No CLO-level details found. Extracting at Course granularity.")
            return parse_khs_markdown(khs_path)
    if ext == ".pdf":
        return parse_khs_pdf(khs_path)
    raise ValueError(f"Unsupported KHS format '{ext}'. Expected .pdf or .md")


# ---------------------------------------------------------------------------
# CV extraction (plain text layer - no AI needed)
# ---------------------------------------------------------------------------
def extract_cv_text(cv_pdf_path):
    reader = PdfReader(cv_pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    if len(text.strip()) < 50:
        raise ValueError(
            f"CV PDF '{cv_pdf_path}' produced almost no text - it may be scanned/image-based. "
            "Consider adding a vision-based fallback similar to the KHS parser below."
        )
    return text

def extract_cv_units_ai(cv_text, model="claude-sonnet-4-6"):
    import anthropic
    client = anthropic.Anthropic()
    prompt = (
        "Below is the raw text of a CV/resume. Split it into discrete competency "
        "units - one per work experience entry, project, or publication (skip "
        "generic sections like contact info, education, and skills lists - those "
        "aren't individual units). For each unit, write a short title and a "
        "description combining what was done and any technologies/methods "
        "mentioned, in the CV's own words as much as possible.\n\n"
        "Respond with ONLY a JSON array (no markdown fences, no commentary), "
        'where each element has keys "title" and "description".\n\n'
        f"CV TEXT:\n\"\"\"\n{cv_text}\n\"\"\""
    )
    response = client.messages.create(
        model=model,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    raw_text = "".join(block.text for block in response.content if block.type == "text")
    raw_text = re.sub(r"^```json\s*|\s*```$", "", raw_text.strip())
    return json.loads(raw_text)

def extract_cv_units_md(cv_md_path):
    with open(cv_md_path, encoding="utf-8") as f:
        text = f.read()

    match = re.search(r"## Professional Projects\n\n(.*?)\n---\n\n## Certifications", text, re.DOTALL)
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
# Certificate extraction
# ---------------------------------------------------------------------------
BULAN_EN = {
    "Januari": "01", "Februari": "02", "Maret": "03", "April": "04",
    "Mei": "05", "Juni": "06", "Juli": "07", "Agustus": "08",
    "September": "09", "Oktober": "10", "November": "11", "Desember": "12",
}

def _parse_tanggal_id(tgl_str):
    parts = tgl_str.strip().split()
    if len(parts) == 3:
        day, month_id, year = parts
        month = BULAN_EN.get(month_id)
        if month:
            return f"{year}-{month}-{int(day):02d}"
    return None

def parse_certificate_markdown(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    in_detail = False
    detail = {}
    cakupan_lines = []
    in_cakupan = False

    for line in lines:
        stripped = line.strip()
        if stripped == "## Cakupan Materi":
            in_cakupan = True
            in_detail = False
            continue
        if in_cakupan:
            if stripped.startswith("##") or stripped == "---":
                in_cakupan = False
            elif stripped.startswith("-"):
                cakupan_lines.append(stripped.lstrip("- ").strip())
            continue
        if stripped == "## Detail Sertifikat":
            in_detail = True
            continue
        if not in_detail:
            continue
        if stripped == "---" or (stripped.startswith("##") and stripped != "## Detail Sertifikat"):
            in_detail = False
            continue
        if not stripped.startswith("|"):
            continue
        if "|---" in stripped:
            continue
        cols = [c.strip() for c in stripped.split("|")[1:-1]]
        if len(cols) < 2:
            continue
        key, val = cols[0], cols[1]
        detail[key] = val

    title = detail.get("Judul Sertifikasi") or detail.get("Judul") or os.path.basename(md_path)
    issuer = detail.get("Penyelenggara / Issuer") or detail.get("Penyelenggara") or detail.get("Issuer")
    raw_date = detail.get("Tanggal Terbit", "")
    issue_date = _parse_tanggal_id(raw_date) or raw_date or None
    has_assessment = bool(detail.get("Skor Akhir"))

    if cakupan_lines:
        description_text = f"{title}. " + " ".join(cakupan_lines)
    else:
        description_text = title

    return {
        "title": title,
        "issuer": issuer,
        "has_assessment": has_assessment,
        "issue_date": issue_date,
        "description_text": description_text,
        "source_file": os.path.basename(md_path),
    }


CERT_EXTRACTION_PROMPT = """This image is a certificate (sertifikat pelatihan/kursus/kompetisi/webinar/sertifikasi).
Extract the following fields and respond with ONLY a JSON object (no markdown fences, no commentary):

{
  "title": "the course/training/competition/certification name",
  "issuer": "the organization name that issued it, as printed on the certificate",
  "has_assessment": true or false (does the certificate indicate passing an exam, quiz, project, or competition placement - as opposed to just attendance/participation),
  "issue_date": "YYYY-MM-DD if fully determinable, else YYYY-MM, else YYYY, else null",
  "description_text": "any text on the certificate describing the skills, topics, or scope covered - verbatim if short, otherwise a factual paraphrase. If the certificate has no descriptive text beyond the title, repeat the title here."
}

Do not fabricate details not visible on the certificate. If a field truly cannot be determined, use null.
"""

def extract_certificate(cert_path, model="claude-sonnet-4-6"):
    import anthropic
    client = anthropic.Anthropic()

    if cert_path.lower().endswith(".pdf"):
        images_b64 = _pdf_pages_to_base64_images(cert_path)
        media_type = "image/jpeg"
    else:
        with open(cert_path, "rb") as f:
            images_b64 = [base64.standard_b64encode(f.read()).decode("utf-8")]
        ext = cert_path.lower().rsplit(".", 1)[-1]
        media_type = f"image/{'jpeg' if ext in ('jpg', 'jpeg') else ext}"

    content = [{"type": "image", "source": {"type": "base64", "media_type": media_type, "data": img}}
               for img in images_b64]
    content.append({"type": "text", "text": CERT_EXTRACTION_PROMPT})

    response = client.messages.create(model=model, max_tokens=1000,
                                       messages=[{"role": "user", "content": content}])
    raw_text = "".join(block.text for block in response.content if block.type == "text")
    raw_text = re.sub(r"^```json\s*|\s*```$", "", raw_text.strip())
    result = json.loads(raw_text)
    result["source_file"] = os.path.basename(cert_path)
    return result

def parse_certificate(cert_path, model="claude-sonnet-4-6"):
    ext = os.path.splitext(cert_path)[1].lower()
    if ext == ".md":
        print(f"Detected markdown certificate: {cert_path}")
        return parse_certificate_markdown(cert_path)
    return extract_certificate(cert_path, model=model)

def extract_certificates_batch(cert_paths, model="claude-sonnet-4-6"):
    records = []
    for path in cert_paths:
        try:
            print(f"Extracting: {path}")
            records.append(parse_certificate(path, model=model))
        except Exception as e:
            print(f"  FAILED ({e}) - skipping this certificate")
    return pd.DataFrame(records)

def parse_certificates_for_student(student_cert_dir, model="claude-sonnet-4-6"):
    import glob as globmod
    cert_paths = sorted(
        p for ext in ("*.md", "*.pdf", "*.jpg", "*.jpeg", "*.png")
        for p in globmod.glob(os.path.join(student_cert_dir, ext))
    )
    print(f"Found {len(cert_paths)} certificate file(s) in: {student_cert_dir}")
    df = extract_certificates_batch(cert_paths, model=model)
    if len(df) > 0:
        df["cert_id"] = ["cert_" + str(i) for i in range(len(df))]
    return df


if __name__ == "__main__":
    import argparse
    import glob as globmod
    parser = argparse.ArgumentParser()
    parser.add_argument("--khs", required=True, help="KHS file (.pdf atau .md)")
    parser.add_argument("--cv_pdf", required=False, default=None, help="CV file in PDF format (Uses AI)")
    parser.add_argument("--cv_md", required=False, default=None, help="CV file in MD format (Uses Regex)")
    parser.add_argument("--cert_dir", required=False, default=None, help="Directory containing certificates")
    parser.add_argument("--out_khs_csv", default="transcript_parsed.csv")
    parser.add_argument("--out_cv_units_csv", default="cv_units_parsed.csv")
    parser.add_argument("--out_certs_csv", default="certificates_parsed.csv")
    args = parser.parse_args()

    khs_df = parse_khs(args.khs)
    khs_df.to_csv(args.out_khs_csv, index=False)
    if "clo_code" in khs_df.columns:
        print(f"Saved {len(khs_df)} CLO rows -> {args.out_khs_csv}")
    else:
        print(f"Saved {len(khs_df)} courses -> {args.out_khs_csv}")

    cv_units_df = None
    if args.cv_md:
        cv_units = extract_cv_units_md(args.cv_md)
        cv_units_df = pd.DataFrame(cv_units)
    elif args.cv_pdf:
        cv_text = extract_cv_text(args.cv_pdf)
        cv_units = extract_cv_units_ai(cv_text)
        cv_units_df = pd.DataFrame(cv_units)
    else:
        print("No --cv_pdf or --cv_md given, skipping CV extraction.")

    if cv_units_df is not None:
        cv_units_df["cv_unit_id"] = ["cv_unit_" + str(i) for i in range(len(cv_units_df))]
        cv_units_df.to_csv(args.out_cv_units_csv, index=False)
        print(f"Saved {len(cv_units_df)} CV units -> {args.out_cv_units_csv}")

    if args.cert_dir:
        certs_df = parse_certificates_for_student(args.cert_dir)
        certs_df.to_csv(args.out_certs_csv, index=False)
        print(f"Saved {len(certs_df)} certificates -> {args.out_certs_csv}")
    else:
        print("No --cert_dir given, skipping certificate extraction.")
