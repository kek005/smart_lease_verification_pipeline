from PyPDF2 import PdfReader, PdfWriter
import os
import pdfplumber
from openai import OpenAI
from dotenv import load_dotenv
from text_utils import clean_pdf_text, chunk_text
from datetime import datetime
import json

# === Setup ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Extract Selected Pages for Testing ===
def extract_selected_pages(input_pdf, output_pdf, pages_to_keep):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    for page_num in pages_to_keep:
        writer.add_page(reader.pages[page_num - 1])  # 0-based index
    with open(output_pdf, "wb") as f:
        writer.write(f)

extract_selected_pages("uploaded_lease.pdf", "lease_5pages.pdf", [1, 5, 37, 51, 52])

# === Models & Prompt ===
models = ["gpt-4o-mini", "gpt-3.5-turbo"]
pdf_path = "lease_5pages.pdf"

system_prompt = (
    "You are a smart assistant helping to review lease documents page by page.\n\n"
    "For each page, do the following:\n"
    "1. Briefly summarize the content of this page in 2–3 lines.\n\n"
    "2. Determine if this page is expected to contain a visible signature field or box:\n"
    "   - Does it include a space meant for someone to sign?\n"
    "   - Or does it merely reference signing in the future?\n"
    "   - ⚠️ Do NOT count footers or metadata like 'digitally signed by RentCafe'.\n"
    "   - Signature references in document footers should be ignored unless there's an actual form field or box.\n\n"
    "3. Determine if this page includes the lease start and end date:\n"
    "   - If lease dates are present (e.g., move-in/move-out), extract and state them clearly in your response.\n"
    "   - If lease duration or date range is not present but should be, say so.\n"
    "   - If lease dates are not expected here, say that explicitly.\n\n"
    "Be precise and helpful — your answer will guide a downstream document automation system to validate this lease."
)

# === Output Log Setup ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
os.makedirs("ab_traces", exist_ok=True)

def summarize(model_name):
    print(f"\n🔍 MODEL: {model_name}")
    results = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            raw_text = page.extract_text() or ""
            cleaned = clean_pdf_text(raw_text)
            chunks = chunk_text(cleaned, chunk_size=2000)

            for chunk_index, chunk in enumerate(chunks):
                print(f"\n📄 Page {page_num}, Chunk {chunk_index+1}/{len(chunks)}")

                try:
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": chunk}
                        ],
                        temperature=0.3,
                        max_tokens=500
                    )
                    summary = response.choices[0].message.content
                    print(summary)

                except Exception as e:
                    summary = f"[❌ GPT Error]: {e}"
                    print(summary)

                # Append to log
                results.append({
                    "model": model_name,
                    "page": page_num,
                    "chunk_index": chunk_index,
                    "chunk_text": chunk,
                    "summary": summary
                })

    # Save to file
    output_file = f"ab_traces/abtest_{model_name}_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Saved trace to {output_file}")

# === Run both models ===
for model in models:
    summarize(model)