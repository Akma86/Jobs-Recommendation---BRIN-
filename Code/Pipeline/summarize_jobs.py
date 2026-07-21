import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"

MIN_LENGTH_TO_SUMMARIZE = 400
MAX_INPUT_CHARS = 18000
MAX_NEW_TOKENS = 200

def summarize_text(text, tokenizer, model):
    text = str(text)[:MAX_INPUT_CHARS]

    prompt = f"""
Summarize the following job posting.

Keep:
- Main responsibilities
- Required skills
- Required qualifications
- Technologies and tools

Remove:
- Company marketing
- Benefits
- Repetitive statements
- Legal/disclaimer sections

Write a concise summary.

Job Posting:
{text}
"""

    messages = [
        {
            "role": "system",
            "content": "You are an expert at summarizing job postings."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    formatted_text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(
        formatted_text,
        return_tensors="pt",
        truncation=True,
        max_length=32768
    ).to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            temperature=None,
            top_p=None
        )

    generated = outputs[0][inputs.input_ids.shape[1]:]

    return tokenizer.decode(
        generated,
        skip_special_tokens=True
    ).strip()


def main():
    print(f"Loading {MODEL_NAME} ...")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        device_map="auto"
    )

    jobs = pd.read_csv(
        r"D:\MAIN DATA\Documents\Semester 6\KP BRIN\Dataset\Pekerjaan\Processed\jobs_unified.csv"
    )

    print(f"Loaded {len(jobs)} postings")

    descriptions = jobs["description"].fillna("").astype(str)

    summaries = []

    for i, text in enumerate(descriptions):
        try:
            if len(text) < MIN_LENGTH_TO_SUMMARIZE:
                summaries.append(text)
            else:
                summary = summarize_text(
                    text,
                    tokenizer,
                    model
                )
                summaries.append(summary)

            if (i + 1) % 10 == 0:
                print(f"Processed {i+1}/{len(jobs)}")

        except Exception as e:
            print(f"Failed on row {i}: {e}")
            summaries.append(text[:1000])

    jobs["description_summary"] = summaries

    output_path = "jobs_unified_summarized.csv"

    jobs.to_csv(
        output_path,
        index=False
    )

    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()