import os
import sys
import glob
import io
import tempfile
import contextlib
import traceback

import streamlit as st
import pandas as pd

# ----------------------------------------------------------------------------
# Path setup — mirrors main.py so this file can sit next to it and import the
# same sibling packages (RankingJob, Explainable AI).
# ----------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.dirname(SCRIPT_DIR)
)
)

try:
from kpbrin.core.full_pipeline import run_pipeline, JOBS_CSV_PATH, COURSE_CLO_CSV_PATH, TOP_N_OUTPUT  # type: ignore
from kpbrin.xai.shap_explain import generate_shap_report  # type: ignore
    from narrate_explanations import generate_narrations  # type: ignore
    IMPORT_ERROR = None
except Exception as e:  # pragma: no cover
    IMPORT_ERROR = str(e)
    JOBS_CSV_PATH = ""
    COURSE_CLO_CSV_PATH = ""
    TOP_N_OUTPUT = 10


# ----------------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Career Path Recommender",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# Glassmorphism theme — light, airy, soft-blur glass panels on a pastel
# gradient backdrop. Accent: violet + teal. No dark surfaces anywhere.
# ----------------------------------------------------------------------------
GLASS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

:root {
    --glass-bg: rgba(255, 255, 255, 0.55);
    --glass-bg-strong: rgba(255, 255, 255, 0.72);
    --glass-border: rgba(255, 255, 255, 0.85);
    --glass-shadow: 0 8px 32px rgba(124, 111, 240, 0.18);
    --accent: #7C6FF0;
    --accent-2: #34C7B8;
    --accent-3: #FF8FB1;
    --text-main: #232244;
    --text-muted: #6B6B85;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: var(--text-main);
}

.stApp {
    background: linear-gradient(135deg, #EAF6FF 0%, #F1ECFF 45%, #FDF0FA 100%);
    background-attachment: fixed;
}

h1, h2, h3, .hero-title {
    font-family: 'Poppins', sans-serif !important;
    color: var(--text-main);
}

/* ---- Hero ---- */
.hero-wrap {
    background: var(--glass-bg-strong);
    border: 1px solid var(--glass-border);
    border-radius: 28px;
    padding: 2.2rem 2.4rem;
    box-shadow: var(--glass-shadow);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    margin-bottom: 1.6rem;
}
.hero-title {
    font-size: 2.1rem;
    font-weight: 700;
    margin: 0 0 0.3rem 0;
    background: linear-gradient(90deg, var(--accent), var(--accent-2));
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}
.hero-sub {
    color: var(--text-muted);
    font-size: 1.02rem;
    margin: 0;
}
.hero-badge {
    display: inline-block;
    margin-top: 0.9rem;
    padding: 0.35rem 0.9rem;
    border-radius: 999px;
    background: rgba(124, 111, 240, 0.12);
    color: var(--accent);
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}

/* ---- Glass containers (st.container(border=True)) ---- */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 22px !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: var(--glass-bg) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 22px !important;
    box-shadow: var(--glass-shadow) !important;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    padding: 0.4rem 0.2rem;
}

/* ---- Stepper pills ---- */
.stepper-wrap {
    display: flex;
    gap: 0.9rem;
    align-items: center;
    flex-wrap: wrap;
}
.step-pill {
    flex: 1;
    min-width: 180px;
    background: rgba(255,255,255,0.5);
    border: 1px solid var(--glass-border);
    border-radius: 999px;
    padding: 0.7rem 1.1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-weight: 600;
    color: var(--text-muted);
    box-shadow: 0 4px 14px rgba(124,111,240,0.08);
    transition: all 0.35s ease;
}
.step-pill.active {
    background: linear-gradient(120deg, rgba(124,111,240,0.22), rgba(52,199,184,0.22));
    color: var(--text-main);
    box-shadow: 0 0 0 2px rgba(124,111,240,0.35), 0 6px 20px rgba(124,111,240,0.25);
}
.step-pill.done {
    background: linear-gradient(120deg, rgba(52,199,184,0.28), rgba(124,111,240,0.12));
    color: var(--text-main);
}
.step-icon { font-size: 1.15rem; }

/* ---- Recommendation cards ---- */
.rec-card {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.8rem;
    box-shadow: var(--glass-shadow);
    backdrop-filter: blur(14px);
}
.rec-rank {
    font-size: 0.78rem;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.rec-title { font-size: 1.15rem; font-weight: 700; margin: 0.15rem 0 0.1rem 0; }
.rec-company { color: var(--text-muted); font-size: 0.92rem; margin-bottom: 0.5rem; }
.rec-score {
    display: inline-block;
    background: rgba(52,199,184,0.18);
    color: #1C8A7D;
    border-radius: 999px;
    padding: 0.15rem 0.7rem;
    font-weight: 700;
    font-size: 0.85rem;
}
.rec-why { color: var(--text-main); font-size: 0.95rem; margin-top: 0.5rem; line-height: 1.5; }

/* ---- Buttons ---- */
.stButton > button, .stDownloadButton > button {
    border-radius: 999px !important;
    border: none !important;
    background: linear-gradient(90deg, var(--accent), var(--accent-2)) !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 0.55rem 1.4rem !important;
    box-shadow: 0 6px 18px rgba(124,111,240,0.35) !important;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    filter: brightness(1.06);
}

section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.45);
    backdrop-filter: blur(14px);
}

/* dataframe */
[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
    box-shadow: var(--glass-shadow);
}
</style>
"""
st.markdown(GLASS_CSS, unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Hero
# ----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-wrap">
        <div class="hero-title">🧭 Career Path Recommender</div>
        <p class="hero-sub">Match your transcript and certificates against real job postings,
        then see exactly why each recommendation was made.</p>
        <span class="hero-badge">Ranking · SHAP Explainability · LLM Narration</span>
    </div>
    """,
    unsafe_allow_html=True,
)

if IMPORT_ERROR:
    st.error(
        "Couldn't import the pipeline modules. Make sure this file lives next to "
        "the `RankingJob` and `Explainable AI` folders.\n\n"
        f"Details: {IMPORT_ERROR}"
    )
    st.stop()


# ----------------------------------------------------------------------------
# Sidebar — inputs & options
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 📄 Your data")
    khs_file = st.file_uploader("Transcript (transcript_parsed.csv)", type=["csv"])
    certs_file = st.file_uploader("Certificates (optional)", type=["csv"])

    st.markdown("### ⚙️ Reference data")
    use_default_refs = st.checkbox("Use default jobs / course-CLO files", value=True)
    jobs_file = None
    course_clo_file = None
    if not use_default_refs:
        jobs_file = st.file_uploader("Jobs CSV", type=["csv"], key="jobs")
        course_clo_file = st.file_uploader("Course-CLO CSV", type=["csv"], key="clo")

    st.markdown("### 🧪 Explainability")
    skip_xai = st.toggle("Skip SHAP explainability", value=False)
    narrate = st.toggle("Generate LLM narrations", value=False, disabled=skip_xai)
    if narrate and not os.environ.get("ANTHROPIC_API_KEY"):
        api_key_input = st.text_input("ANTHROPIC_API_KEY", type="password")
        if api_key_input:
            os.environ["ANTHROPIC_API_KEY"] = api_key_input

    run_clicked = st.button("✨ Run pipeline", use_container_width=True)


def _save_upload(uploaded_file, suffix=".csv"):
    if uploaded_file is None:
        return None
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(uploaded_file.getvalue())
    tmp.close()
    return tmp.name


# ----------------------------------------------------------------------------
# Stepper
# ----------------------------------------------------------------------------
def render_stepper(current_step: int, skip_xai: bool, narrate: bool):
    steps = [("🧭", "Ranking"), ("🔍", "SHAP"), ("💬", "Narration")]
    if skip_xai:
        steps[1] = ("🔍", "SHAP (skipped)")
    if not narrate:
        steps[2] = ("💬", "Narration (skipped)")

    html = ['<div class="stepper-wrap">']
    for i, (icon, label) in enumerate(steps):
        cls = "step-pill"
        if i < current_step:
            cls += " done"
        elif i == current_step:
            cls += " active"
        html.append(f'<div class="{cls}"><span class="step-icon">{icon}</span>{label}</div>')
    html.append("</div>")
    return "".join(html)


stepper_slot = st.empty()
stepper_slot.markdown(render_stepper(0, skip_xai, narrate), unsafe_allow_html=True)

log_container = st.container(border=True)
results_container = st.container()


# ----------------------------------------------------------------------------
# Run
# ----------------------------------------------------------------------------
if run_clicked:
    if khs_file is None:
        st.warning("Please upload a transcript CSV before running.")
        st.stop()

    khs_path = _save_upload(khs_file)
    certs_path = _save_upload(certs_file)
    jobs_path = _save_upload(jobs_file) if jobs_file else JOBS_CSV_PATH
    course_clo_path = _save_upload(course_clo_file) if course_clo_file else COURSE_CLO_CSV_PATH

    log_buffer = io.StringIO()
    final_ranking = None
    job_contributions = None
    shap_df = None
    narrated_df = None
    plots_dir = tempfile.mkdtemp(prefix="shap_plots_")

    try:
        # --- Step 1: Ranking ---
        stepper_slot.markdown(render_stepper(0, skip_xai, narrate), unsafe_allow_html=True)
        with st.spinner("Ranking jobs against your profile…"):
            with contextlib.redirect_stdout(log_buffer):
                final_ranking, job_contributions = run_pipeline(
                    khs_path=khs_path,
                    certs_path=certs_path,
                    jobs_path=jobs_path,
                    course_clo_path=course_clo_path,
                )
        final_ranking.head(TOP_N_OUTPUT).to_csv("final_recommendations.csv", index=False)

        # --- Step 2: SHAP ---
        if not skip_xai:
            stepper_slot.markdown(render_stepper(1, skip_xai, narrate), unsafe_allow_html=True)
            with st.spinner("Building SHAP explanations…"):
                top_job_ids = final_ranking.head(TOP_N_OUTPUT)["job_id"].tolist()
                job_titles = dict(zip(final_ranking["job_id"], final_ranking["job_title"]))
                with contextlib.redirect_stdout(log_buffer):
                    generate_shap_report(
                        job_contributions,
                        job_titles,
                        top_job_ids,
                        csv_path="shap_explanations.csv",
                        plots_dir=plots_dir,
                        n_plots=5,
                    )
            shap_df = pd.read_csv("shap_explanations.csv")

            # --- Step 3: Narration ---
            if narrate:
                stepper_slot.markdown(render_stepper(2, skip_xai, narrate), unsafe_allow_html=True)
                with st.spinner("Asking Claude to explain the results in plain language…"):
                    with contextlib.redirect_stdout(log_buffer):
                        narrated_df = generate_narrations(final_ranking, shap_df, backend="anthropic", top_n=5)
                narrated_df.to_csv("final_recommendations_narrated.csv", index=False)
                final_ranking = narrated_df

        stepper_slot.markdown(render_stepper(3, skip_xai, narrate), unsafe_allow_html=True)

    except Exception:
        st.error("The pipeline hit an error. See the log below for details.")
        log_buffer.write("\n" + traceback.format_exc())
        with log_container:
            st.markdown("#### 🪵 Run log")
            st.code(log_buffer.getvalue() or "No output captured.")
        st.stop()

    with log_container:
        st.markdown("#### 🪵 Run log")
        with st.expander("Show pipeline output", expanded=False):
            st.code(log_buffer.getvalue() or "No output captured.")

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------
    with results_container:
        st.markdown("### 🌤️ Top recommendations")

        top5 = final_ranking.head(5)
        for rank, (_, row) in enumerate(top5.iterrows(), start=1):
            why = row.get("llm_narration") if "llm_narration" in row else row.get("explanation", "—")
            st.markdown(
                f"""
                <div class="rec-card">
                    <div class="rec-rank">#{rank} match</div>
                    <div class="rec-title">{row['job_title']}</div>
                    <div class="rec-company">{row.get('job_company', '')}</div>
                    <span class="rec-score">score {row['final_score']:.3f}</span>
                    <div class="rec-why">💬 {why}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("### 📋 Full ranking table")
        full_view = st.container(border=True)
        with full_view:
            st.dataframe(final_ranking.head(TOP_N_OUTPUT), use_container_width=True, hide_index=True)

        dl_col1, dl_col2, dl_col3 = st.columns(3)
        with dl_col1:
            st.download_button(
                "⬇️ final_recommendations.csv",
                data=final_ranking.head(TOP_N_OUTPUT).to_csv(index=False).encode(),
                file_name="final_recommendations.csv",
                mime="text/csv",
                use_container_width=True,
            )
        if shap_df is not None:
            with dl_col2:
                st.download_button(
                    "⬇️ shap_explanations.csv",
                    data=shap_df.to_csv(index=False).encode(),
                    file_name="shap_explanations.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        if narrated_df is not None:
            with dl_col3:
                st.download_button(
                    "⬇️ final_recommendations_narrated.csv",
                    data=narrated_df.to_csv(index=False).encode(),
                    file_name="final_recommendations_narrated.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

        if not skip_xai:
            plot_files = sorted(glob.glob(os.path.join(plots_dir, "*.png")))
            if plot_files:
                st.markdown("### 🔍 SHAP plots")
                cols = st.columns(min(3, len(plot_files)))
                for i, plot_path in enumerate(plot_files):
                    with cols[i % len(cols)]:
                        img_card = st.container(border=True)
                        with img_card:
                            st.image(plot_path, use_column_width=True)

else:
    st.info("Upload your transcript in the sidebar, then hit **Run pipeline** to get started.")