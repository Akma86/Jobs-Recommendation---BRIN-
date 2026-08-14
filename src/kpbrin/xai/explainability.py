import re

# Stopword list ringan Bahasa Indonesia (khusus buat filter kata umum di
# konteks CLO/pekerjaan, bukan daftar lengkap linguistik).
STOPWORDS_ID = {
    "yang", "dan", "di", "ke", "dari", "untuk", "dalam", "pada", "dengan",
    "atau", "ini", "itu", "adalah", "akan", "dapat", "mampu", "serta",
    "secara", "sebagai", "yaitu", "juga", "tersebut", "suatu", "para",
    "oleh", "hingga", "agar", "bagi", "tidak", "ada", "atas", "antara",
    "tiap", "setiap", "maupun", "baik", "seperti", "kepada", "terhadap",
    "sesuai", "berbagai", "beberapa", "dasar", "konsep", "menggunakan",
    "menjelaskan", "memahami", "menerapkan", "menganalisis", "mengembangkan",
    "the", "and", "for", "with", "of", "to", "in", "on", "a", "an",
}


def _tokenize(text):
    words = re.findall(r"[a-zA-Z][a-zA-Z\-]{2,}", str(text).lower())
    return [w for w in words if w not in STOPWORDS_ID]


# ---------------------------------------------------------------------------
# Stage 2: fuzzy course-name matching
# ---------------------------------------------------------------------------
def explain_course_match(khs_course, matched_course_name, confidence, threshold):
    if confidence >= threshold:
        return (f"MK KHS '{khs_course}' dipetakan ke katalog CLO '{matched_course_name}' "
                f"dengan kemiripan nama {confidence:.0%} (ambang batas {threshold:.0%}), "
                f"sehingga ikut dihitung dalam skor rekomendasi.")
    return (f"MK KHS '{khs_course}' paling mirip dengan '{matched_course_name}' "
            f"tapi kemiripan nama hanya {confidence:.0%}, di bawah ambang batas {threshold:.0%}, "
            f"sehingga TIDAK diikutsertakan dalam skor rekomendasi.")


# ---------------------------------------------------------------------------
# Stage 4: retrieval + rerank (dipakai untuk course maupun sertifikat, lewat
# rank_jobs_for_queries di full_pipeline_subclo.py)
# ---------------------------------------------------------------------------
def score_to_label(score, bands=((0.75, "sangat relevan"), (0.55, "relevan"),
                                  (0.35, "cukup relevan"), (0.0, "kurang relevan"))):
    for cutoff, label in bands:
        if score >= cutoff:
            return label
    return bands[-1][1]


def shared_keywords(text_a, text_b, top_n=5):
    """Overlap kata kunci antara dua teks - dipakai murni untuk grounding
    penjelasan (bukan untuk scoring), sehingga matching tetap semantik."""
    tokens_a = set(_tokenize(text_a))
    tokens_b_ordered = _tokenize(text_b)
    shared = tokens_a.intersection(tokens_b_ordered)
    seen = []
    for w in tokens_b_ordered:
        if w in shared and w not in seen:
            seen.append(w)
        if len(seen) >= top_n:
            break
    return seen


def explain_semantic_match(unit_label, unit_text, job_title, job_desc, score):
    label = score_to_label(score)
    kw = shared_keywords(unit_text, f"{job_title}. {job_desc}")
    if kw:
        kw_str = ", ".join(kw)
        return (f"'{unit_label}' dinilai {label} (skor rerank={score:.2f}) terhadap lowongan "
                f"'{job_title}', dengan kesamaan istilah pada: {kw_str}.")
    return (f"'{unit_label}' dinilai {label} (skor rerank={score:.2f}) terhadap lowongan "
            f"'{job_title}' secara semantik, meski tidak ada istilah eksplisit yang identik.")


# ---------------------------------------------------------------------------
# Stage 5/6: kontribusi ke skor akhir (merangkai penjelasan dari stage
# sebelumnya, bukan membangun ulang dari nol)
# ---------------------------------------------------------------------------
def explain_khs_contribution(khs_course, grade_weight, match_confidence, stage4_explanation, contribution):
    return (f"KHS '{khs_course}' (bobot nilai={grade_weight:.2f} x kecocokan nama MK={match_confidence:.2f}): "
            f"{stage4_explanation} => kontribusi ke skor akhir = {contribution:.2f}")


def explain_cert_contribution(cert_title, credibility_weight, credibility_breakdown, stage4_explanation, contribution):
    breakdown_txt = f" ({credibility_breakdown})" if credibility_breakdown else ""
    return (f"Sertifikat '{cert_title}' (kredibilitas={credibility_weight:.2f}{breakdown_txt}): "
            f"{stage4_explanation} => kontribusi ke skor akhir = {contribution:.2f}")
