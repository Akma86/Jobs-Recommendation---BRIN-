# -*- coding: utf-8 -*-
"""
narrate_explanations.py

Layer paling akhir dari XAI: mengubah hasil penjelasan terstruktur (template
explanation + SHAP values) yang SUDAH dihasilkan full_pipeline_subclo.py
atau full_pipeline_certs.py menjadi narasi kalimat natural pakai decoder LLM.

File ini BERDIRI SENDIRI - tidak mengimpor atau mengubah apapun dari
full_pipeline_subclo.py / full_pipeline_certs.py. Ia hanya membaca 2 file
CSV yang sudah mereka hasilkan:
    - final_recommendations.csv   (job_id, final_score, job_title, job_company,
                                    job_source, explanation)
    - shap_explanations.csv       (job_id, job_title, feature, shap_value, base_value)

PENTING (desain anti-halusinasi):
LLM di sini HANYA berperan sebagai paraphraser/narrator di atas fakta yang
sudah dihitung sebelumnya (skor, kontribusi SHAP, penjelasan template) -
BUKAN sumber penalaran baru. System prompt secara eksplisit melarang LLM
menambahkan alasan yang tidak ada di data, supaya narasi yang dihasilkan
tetap faithful ke perhitungan matematis aslinya (bukan LLM ngarang bebas).

Backend LLM (switchable via --backend):
    anthropic  -> Claude API (kualitas terbaik, butuh ANTHROPIC_API_KEY)
    local_hf   -> Decoder LLM open-source lokal, offline (default: Qwen2.5-3B-Instruct)

Cara pakai:
    # Backend Claude API
    export ANTHROPIC_API_KEY=sk-ant-xxxx
    python narrate_explanations.py --backend anthropic \
        --final final_recommendations.csv --shap shap_explanations.csv

    # Backend decoder LLM lokal (offline, gratis)
    pip install transformers torch accelerate
    python narrate_explanations.py --backend local_hf \
        --final final_recommendations.csv --shap shap_explanations.csv

Dependency per backend (install sesuai backend yang dipakai saja):
    anthropic  -> pip install anthropic
    local_hf   -> pip install transformers torch accelerate
"""

import argparse
import os

import pandas as pd

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"   # narasi = task ringan (paraphrase), cukup Haiku
GEMINI_MODEL = "gemini-2.5-flash"               # model gemini yang cepat
LOCAL_HF_MODEL = "Qwen/Qwen2.5-3B-Instruct"     # decoder LLM open-source, kuat di Bahasa Indonesia
TOP_N_NARRATE = 5           # cuma narasiin top-N job (biar hemat biaya/waktu compute)
TOP_K_SHAP_FEATURES = 3     # jumlah fitur SHAP teratas yang ditunjukkan ke LLM

SYSTEM_PROMPT = (
    "Anda adalah asisten yang menjelaskan hasil rekomendasi karir kepada mahasiswa. "
    "Anda HANYA boleh menarasikan fakta, angka, dan penjelasan yang diberikan di bawah "
    "menjadi kalimat yang natural dan mudah dipahami dalam Bahasa Indonesia.\n\n"
    "ATURAN KETAT:\n"
    "1. JANGAN menambahkan alasan, kompetensi, atau klaim apapun yang tidak ada di data "
    "yang diberikan.\n"
    "2. JANGAN mengubah urutan kepentingan (kontributor dengan nilai lebih tinggi = "
    "lebih berpengaruh terhadap rekomendasi ini, dan itu harus tercermin di narasi).\n"
    "3. Tulis 2-4 kalimat, nada positif tapi jujur, fokus ke 2-3 kontributor terbesar.\n"
    "4. Jangan sebut istilah teknis seperti 'SHAP', 'skor cross-encoder', atau 'embedding' "
    "ke pengguna akhir - terjemahkan jadi bahasa awam (mis. 'kontribusi terbesar', "
    "'paling relevan dengan kompetensi kamu').\n"
    "5. Output HANYA narasinya, tanpa heading, tanpa embel-embel lain."
)


def build_prompt(row, shap_rows):
    top_features = shap_rows.sort_values("shap_value", ascending=False).head(TOP_K_SHAP_FEATURES)
    feature_lines = "\n".join(
        f"- {r['feature']}: kontribusi={r['shap_value']:.2f}" for _, r in top_features.iterrows()
    ) or "- (tidak ada rincian kontributor)"

    return (
        f"Lowongan: {row['job_title']} di {row['job_company']}\n"
        f"Skor akhir rekomendasi: {row['final_score']:.2f}\n\n"
        f"Kontributor utama (diurutkan dari paling berpengaruh, sudah divalidasi lewat SHAP):\n"
        f"{feature_lines}\n\n"
        f"Penjelasan detail per kontributor (jangan diulang mentah-mentah, cukup jadi rujukan fakta):\n"
        f"{row['explanation']}\n\n"
        "Tulis narasinya sekarang."
    )


# ---------------------------------------------------------------------------
# BACKEND 1: Claude API
# ---------------------------------------------------------------------------
def narrate_with_anthropic(prompt, model=ANTHROPIC_MODEL):
    import anthropic

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY belum di-set. export ANTHROPIC_API_KEY=sk-ant-xxxx")
    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=model, max_tokens=300, system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


# ---------------------------------------------------------------------------
# BACKEND 2: Decoder LLM lokal (open-source, offline)
# ---------------------------------------------------------------------------
_local_model_cache = {}


def _get_local_model(model_name=LOCAL_HF_MODEL):
    if model_name not in _local_model_cache:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch

        print(f"  Loading local decoder LLM: {model_name} (sekali saja, di-cache)...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto",
        )
        _local_model_cache[model_name] = (tokenizer, model)
    return _local_model_cache[model_name]


def narrate_with_local_hf(prompt, model_name=LOCAL_HF_MODEL):
    import torch

    tokenizer, model = _get_local_model(model_name)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output_ids = model.generate(
            **inputs, max_new_tokens=250, do_sample=True, temperature=0.4, top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
        )
    generated = output_ids[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(generated, skip_special_tokens=True).strip()


# ---------------------------------------------------------------------------
# BACKEND 3: Gemini API
# ---------------------------------------------------------------------------
def narrate_with_gemini(prompt, model=GEMINI_MODEL):
    import google.generativeai as genai
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY belum di-set.")
    
    genai.configure(api_key=api_key)
    
    # Gunakan system instruction jika didukung, atau gabung ke prompt
    model_instance = genai.GenerativeModel(
        model_name=model,
        system_instruction=SYSTEM_PROMPT
    )
    
    import time
    time.sleep(10) # delay to avoid 429 rate limit
    response = model_instance.generate_content(prompt)
    return response.text.strip()


BACKENDS = {
    "anthropic": narrate_with_anthropic,
    "local_hf": narrate_with_local_hf,
    "gemini": narrate_with_gemini,
}


# ---------------------------------------------------------------------------
# ORCHESTRATION
# ---------------------------------------------------------------------------
def generate_narrations(final_df, shap_df, backend="anthropic", top_n=TOP_N_NARRATE):
    narrate_fn = BACKENDS[backend]

    top_jobs = final_df.sort_values("final_score", ascending=False).head(top_n).copy()
    narrations = []
    for i, (_, row) in enumerate(top_jobs.iterrows(), start=1):
        shap_rows = shap_df[shap_df["job_id"] == row["job_id"]]
        prompt = build_prompt(row, shap_rows)
        print(f"[{i}/{len(top_jobs)}] Narasi buat: {row['job_title']} (backend={backend})")
        narrations.append(narrate_fn(prompt))

    top_jobs["llm_narration"] = narrations
    return top_jobs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--final", default="final_recommendations.csv",
                         help="output dari full_pipeline_subclo.py atau full_pipeline_certs.py")
    parser.add_argument("--shap", default="shap_explanations.csv",
                         help="output dari generate_shap_report (dipanggil di dalam pipeline)")
    parser.add_argument("--backend", choices=list(BACKENDS.keys()), default="anthropic")
    parser.add_argument("--top-n", type=int, default=TOP_N_NARRATE)
    parser.add_argument("--output", default="final_recommendations_narrated.csv")
    args = parser.parse_args()

    final_df = pd.read_csv(args.final)
    shap_df = pd.read_csv(args.shap)

    result = generate_narrations(final_df, shap_df, backend=args.backend, top_n=args.top_n)
    result.to_csv(args.output, index=False)
    print(f"\nSaved: {args.output}")

    print("\n--- Preview ---")
    for _, row in result.iterrows():
        print(f"\n[{row['final_score']:.2f}] {row['job_title']} @ {row['job_company']}")
        print(f"   {row['llm_narration']}")


if __name__ == "__main__":
    main()
