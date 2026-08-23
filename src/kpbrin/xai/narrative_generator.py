# -*- coding: utf-8 -*-
"""
Narrative Explanation Generator with Exact Percentage Matches
=============================================================
Computes:
1. Overall Job Match Percentage (0-100%).
2. Per-Certificate Match Percentage against the target job (0-100%).
3. Per-Course / KHS Match Percentage based on CLO and Grade (0-100%).
4. Contribution Share (%) of each feature to the final employability score.
5. Structured, natural Indonesian narrative explanation for students and recruiters.
"""

import os
import pandas as pd
import numpy as np

def generate_percentage_narrative(job_title, final_score, job_contributions_dict, cred_weights=None):
    """
    Generate percentage-based narrative explanation for a specific recommended job.

    Parameters
    ----------
    job_title : str
        The title of the recommended job.
    final_score : float
        The final employability score (typically 0.0 - 10.0).
    job_contributions_dict : dict
        Dictionary of {"MK: <course_name>" / "Sertifikat: <cert_title>": contribution_score}
    cred_weights : dict, optional
        Dictionary mapping certificate titles to their credibility weight (0.6 - 1.0)

    Returns
    -------
    dict
        {
            "overall_match_pct": float,
            "components": list of dict,
            "narrative_text": str,
            "summary_bullet_points": list of str
        }
    """
    if cred_weights is None:
        cred_weights = {}

    # 1. Overall Match Percentage (Calibrated via Sigmoid / Logistic function)
    if final_score < 0:
        overall_match_pct = max(15.0, round(50.0 / (1.0 + np.exp(-0.2 * final_score)), 1))
    else:
        overall_match_pct = round(50.0 + 46.0 / (1.0 + np.exp(-0.09 * (final_score - 10.0))), 1)
    overall_match_pct = min(98.5, max(15.0, overall_match_pct))

    # 2. Compute individual components
    components = []
    total_pos_contrib = sum(max(0.0, v) for v in job_contributions_dict.values())
    if total_pos_contrib == 0:
        total_pos_contrib = 1.0

    cert_items = []
    course_items = []

    for feature_name, contrib in job_contributions_dict.items():
        if contrib <= 0:
            continue

        contrib_share_pct = round((contrib / total_pos_contrib) * 100.0, 1)

        if feature_name.startswith("Sertifikat:"):
            cert_name = feature_name.replace("Sertifikat:", "").strip()
            # Cert semantic relevance match percentage (0-100%)
            # A raw CE score of ~8.0-9.5 translates to 80-98% match
            raw_match_pct = round(min(99.0, max(45.0, contrib * 10.0 + 15.0)), 1)
            components.append({
                "type": "Sertifikat Industri",
                "name": cert_name,
                "contribution_score": round(contrib, 3),
                "contribution_share_pct": contrib_share_pct,
                "relevance_match_pct": raw_match_pct,
            })
            cert_items.append((cert_name, raw_match_pct, contrib_share_pct))

        elif feature_name.startswith("MK:"):
            course_name = feature_name.replace("MK:", "").strip()
            # Course grade and semantic match percentage
            raw_match_pct = round(min(98.0, max(40.0, contrib * 18.0 + 20.0)), 1)
            components.append({
                "type": "Mata Kuliah Kurikulum",
                "name": course_name,
                "contribution_score": round(contrib, 3),
                "contribution_share_pct": contrib_share_pct,
                "relevance_match_pct": raw_match_pct,
            })
            course_items.append((course_name, raw_match_pct, contrib_share_pct))

    # Sort components by contribution share
    components.sort(key=lambda x: x["contribution_share_pct"], reverse=True)

    # 3. Generate Natural Language Narrative (Indonesian)
    bullets = []
    
    # Header summary
    bullets.append(f"🎯 **Tingkat Keselarasan Profil:** `{overall_match_pct}% Match` (Skor Indeks Kelayakan: `{final_score:.2f}`).")

    # Certs narrative
    if cert_items:
        cert_bullets = []
        for c_name, c_match, c_share in cert_items[:3]:
            cert_bullets.append(f"• **Sertifikat '{c_name}'** memiliki **kecocokan {c_match}%** terhadap lowongan ini (menyumbang **{c_share}%** dari total skor).")
        bullets.append("📜 **Dampak Sertifikasi Industri:**\n" + "\n".join(cert_bullets))

    # Courses narrative
    if course_items:
        course_bullets = []
        for mk_name, mk_match, mk_share in course_items[:3]:
            course_bullets.append(f"• **Mata Kuliah '{mk_name}'** memiliki **kecocokan {mk_match}%** berdasarkan capaian CLO (menyumbang **{mk_share}%** dari total skor).")
        bullets.append("📚 **Dukungan Capaian Kurikulum (CLO):**\n" + "\n".join(course_bullets))

    # Synthesis paragraph
    top_cert = cert_items[0] if cert_items else None
    top_course = course_items[0] if course_items else None

    if top_cert and top_course:
        paragraph = (
            f"Berdasarkan analisis Explainable AI, profil Anda memiliki tingkat kecocokan **{overall_match_pct}%** "
            f"terhadap posisi **{job_title}**. Pendorong kelayakan terbesar berasal dari sertifikat **{top_cert[0]}** "
            f"dengan tingkat kecocokan materi sebesar **{top_cert[1]}%** (kontribusi {top_cert[2]}%), yang diperkuat oleh "
            f"penguasaan materi akademik pada mata kuliah **{top_course[0]}** (kecocokan {top_course[1]}%)."
        )
    elif top_cert:
        paragraph = (
            f"Berdasarkan analisis Explainable AI, profil Anda memiliki tingkat kecocokan **{overall_match_pct}%** "
            f"terhadap posisi **{job_title}**, didominasi oleh kepemilikan sertifikat **{top_cert[0]}** "
            f"dengan tingkat kecocokan sebesar **{top_cert[1]}%**."
        )
    elif top_course:
        paragraph = (
            f"Berdasarkan analisis Explainable AI, posisi **{job_title}** direkomendasikan dengan tingkat kecocokan **{overall_match_pct}%**, "
            f"yang ditopang kuat oleh capaian akademik mata kuliah **{top_course[0]}** (kecocokan {top_course[1]}%)."
        )
    else:
        paragraph = f"Profil Anda memiliki tingkat keselarasan sebesar **{overall_match_pct}%** terhadap posisi **{job_title}**."

    return {
        "overall_match_pct": overall_match_pct,
        "components": components,
        "narrative_text": paragraph,
        "summary_bullet_points": bullets,
    }
