import os
import re
import json
import base64
import io
import pandas as pd
from pypdf import PdfReader

GRADE_MAP = {"A": 0.85, "AB": 0.80, "B": 0.70, "BC": 0.60, "C": 0.55, "D": 0.50, "E": 0.0}
def parse_khs_markdown(md_path):
    """
    Parse generated KHS markdown format and return the same schema as
    parse_khs_pdf():
        kode_mk, nama_mk, sks, nilai_huruf, grade_weight
    """

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

        # stop when transcript table ends
        if line.strip() == "---":
            break

        if not line.startswith("|"):
            continue

        # skip separator row
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
        raise ValueError(
            f"Gagal menemukan tabel mata kuliah pada markdown: {md_path}"
        )

    df = pd.DataFrame(rows)

    df["grade_weight"] = df["nilai_huruf"].map(GRADE_MAP)

    if df["grade_weight"].isna().any():
        bad = df[df["grade_weight"].isna()]
        print(f"WARNING: {len(bad)} rows had unrecognized grades:")
        print(bad)

        df = df.dropna(subset=["grade_weight"])

    return df


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


def extract_cv_units(cv_text, model="claude-sonnet-4-6"):
    """
    Split a CV's free text into discrete competency units - one per project,
    work experience entry, or publication. Each unit becomes its own
    embedding query later on (mirrors how sub-CLOs are individual query
    units on the academic side), instead of treating the whole CV as one
    blurred blob.

    WHY AN LLM CALL INSTEAD OF REGEX/HEADING SPLIT: CV formatting varies
    wildly (bullet styles, section names, date placements). A text-only
    Claude call (no vision needed - CV already has a real text layer) is
    far more robust than hardcoding heading patterns per CV template.

    Requires ANTHROPIC_API_KEY in the environment. This is a plain text
    call (cheap, no images), unlike the KHS vision fallback above.

    Returns a list of dicts: [{"title": ..., "description": ...}, ...]
    """
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


# ---------------------------------------------------------------------------
# KHS extraction: auto-detect text layer vs scanned
# ---------------------------------------------------------------------------
def _has_text_layer(pdf_path):
    reader = PdfReader(pdf_path)
    sample_text = "".join(page.extract_text() or "" for page in reader.pages[:1])
    return len(sample_text.strip()) > 30


def _parse_khs_text_based(pdf_path):
    """For KHS PDFs that DO have a real text layer - use pdfplumber tables."""
    import pdfplumber
    rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                for row in table:
                    rows.append(row)
    # NOTE: this is generic/best-effort - real transcript layouts vary a lot.
    # You will likely need to adjust column indices for your specific format.
    raise NotImplementedError(
        "Text-based KHS table found, but column mapping is institution-specific. "
        "Inspect `rows` here and map to kode_mk/nama_mk/sks/nilai_huruf manually, "
        "or route it through the vision fallback (_parse_khs_vision) instead."
    )


def _pdf_pages_to_base64_images(pdf_path, dpi=200):
    """Rasterize each PDF page to a base64-encoded JPEG using pdftoppm (poppler)."""
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
    """
    Scanned/rasterized KHS PDF -> use Claude vision to read the table and
    return structured JSON. Requires ANTHROPIC_API_KEY in the environment.
    """
    import anthropic

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
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
    """Main entry point: auto-detects strategy and returns a clean DataFrame
    with columns kode_mk, nama_mk, sks, nilai_huruf, grade_weight."""
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
    """
    Unified entry point.
    Supports:
      - .pdf
      - .md
    """

    ext = os.path.splitext(khs_path)[1].lower()

    if ext == ".md":
        print(f"Detected markdown KHS: {khs_path}")
        return parse_khs_markdown(khs_path)

    if ext == ".pdf":
        return parse_khs_pdf(khs_path)

    raise ValueError(
        f"Unsupported KHS format '{ext}'. Expected .pdf or .md"
    )

# ---------------------------------------------------------------------------
# Certificate extraction (vision-based, same reasoning as KHS: certificates
# are visual/design documents, not reliably plain-text-extractable)
# ---------------------------------------------------------------------------
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
    """
    Extract structured fields from a single certificate file (PDF or image).
    Note: this function only extracts CONTENT fields (title, issuer, dates,
    description). Issuer CREDIBILITY weighting is handled separately by
    issuer_tiers.py, kept deliberately decoupled so the credibility judgment
    table can be edited/argued about without touching extraction logic.
    """
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


def extract_certificates_batch(cert_paths):
    """Run extract_certificate over a list of files, skipping ones that fail
    (printing a warning) instead of crashing the whole batch - one badly
    scanned certificate shouldn't block processing the rest."""
    records = []
    for path in cert_paths:
        try:
            print(f"Extracting: {path}")
            records.append(extract_certificate(path))
        except Exception as e:
            print(f"  FAILED ({e}) - skipping this certificate")
    return pd.DataFrame(records)


if __name__ == "__main__":
    import argparse
    import glob as globmod
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--khs",
        required=True,
        help="KHS file (.pdf atau .md)"
    )
    parser.add_argument("--cv_pdf", required=False, default=None, help="Optional - not needed for the KHS-only pipeline")
    parser.add_argument("--cert_dir", required=False, default=None,
                         help="Optional folder containing certificate files (PDF/JPG/PNG), one file per certificate")
    parser.add_argument("--out_khs_csv", default="transcript_parsed.csv")
    parser.add_argument("--out_cv_units_csv", default="cv_units_parsed.csv")
    parser.add_argument("--out_certs_csv", default="certificates_parsed.csv")
    args = parser.parse_args()

    khs_df = parse_khs(args.khs)
    khs_df.to_csv(args.out_khs_csv, index=False)
    print(f"Saved {len(khs_df)} courses -> {args.out_khs_csv}")

    if args.cv_pdf:
        cv_text = extract_cv_text(args.cv_pdf)
        cv_units = extract_cv_units(cv_text)
        cv_units_df = pd.DataFrame(cv_units)
        cv_units_df["cv_unit_id"] = ["cv_unit_" + str(i) for i in range(len(cv_units_df))]
        cv_units_df.to_csv(args.out_cv_units_csv, index=False)
        print(f"Saved {len(cv_units_df)} CV units -> {args.out_cv_units_csv}")
    else:
        print("No --cv_pdf given, skipping CV extraction.")

    if args.cert_dir:
        cert_paths = sorted(
            p for ext in ("*.pdf", "*.jpg", "*.jpeg", "*.png")
            for p in globmod.glob(os.path.join(args.cert_dir, ext))
        )
        print(f"\nFound {len(cert_paths)} certificate files in {args.cert_dir}")
        certs_df = extract_certificates_batch(cert_paths)
        if len(certs_df) > 0:
            certs_df["cert_id"] = ["cert_" + str(i) for i in range(len(certs_df))]
        certs_df.to_csv(args.out_certs_csv, index=False)
        print(f"Saved {len(certs_df)} certificates -> {args.out_certs_csv}")
    else:
        print("No --cert_dir given, skipping certificate extraction.")
