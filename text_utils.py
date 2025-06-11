import os
import re
import json
import streamlit as st
from openai import OpenAI
from datetime import datetime
import pdfplumber

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ======= Smart Truncator =======

def smart_truncate(text: str, max_tokens: int = 8000) -> str:
    max_chars = max_tokens * 4
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[...Document truncated for processing due to size limits...]"


def chunk_text(text: str, chunk_size: int = 2000) -> list:
    """
    Splits cleaned text into chunks of max `chunk_size` characters.
    """
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# ======= Summarizer with Trace + Safety =======

def summarize_chunks(pdf_path: str, chunk_size: int = 2000):
    with pdfplumber.open(pdf_path) as pdf:
        page_count = len(pdf.pages)
        summaries = []
        trace_data = []

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        trace_file = os.path.join("traces", f"trace_summary_{timestamp}.json")

        for page_num, page in enumerate(pdf.pages, start=1):
            raw_text = page.extract_text() or ""
            cleaned = clean_pdf_text(raw_text)
            chunks = chunk_text(cleaned, chunk_size)

            for chunk_index, chunk in enumerate(chunks):
                print(f"[📄] Summarizing Page {page_num}, Chunk {chunk_index+1}/{len(chunks)}")

                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are a smart assistant helping to review lease documents page by page.\n\n"
                                    "For each page, do the following:\n"
                                    "1. Briefly summarize the content of this page in 2–3 lines.\n\n"
                                    "2. Determine if this page is expected to contain a visible signature field or box:\n"
                                    "   - Does it include a space meant for someone to sign?\n"
                                    "   - Or does it merely reference signing in the future?\n"
                                    "   - If no visual signature field is expected, say so clearly.\n\n"
                                    "3. Determine if this page includes the lease start and end date:\n"
                                    "   - If lease dates are present (e.g., move-in/move-out), extract and state them clearly in your response.\n"
                                    "   - If lease duration or date range is not present but should be, say so.\n"
                                    "   - If lease dates are not expected here, say that explicitly.\n\n"
                                    "Be precise and helpful — your answer will guide a downstream document automation system to validate this lease."
                                )
                            },
                            {"role": "user", "content": chunk}
                        ],
                        temperature=0.3,
                        max_tokens=400
                    )
                    summary = response.choices[0].message.content
                except Exception as e:
                    print(f"[❌] GPT failed on Page {page_num}, Chunk {chunk_index+1}: {e}")
                    summary = "[⚠️ GPT failed to summarize this chunk.]"

                summaries.append(summary)

                # === Log the trace ===
                trace_data.append({
                    "page": page_num,
                    "chunk_index": chunk_index,
                    "chunk_text": chunk,
                    "summary": summary
                })

        # === Save the trace file ===
        os.makedirs("traces", exist_ok=True)
        with open(trace_file, "w") as f:
            json.dump(trace_data, f, indent=2)

        print(f"[🧾] Full summary trace written to {trace_file}")
        return "\n".join(summaries), trace_file



# ======= Text Cleaner =======

def clean_pdf_text(text: str) -> str:
    # Collapse multiple line breaks
    text = re.sub(r"\n{2,}", "\n", text)

    # Remove header/footer repetition patterns (very common in leases)
    text = re.sub(r"(?i)page \d+ of \d+", "", text)
    text = re.sub(r"(continued on next page)", "", text, flags=re.IGNORECASE)

    # Remove watermark-like repeating text (often PDF layer artifacts)
    text = re.sub(r"\b(?:Document|Signature|Timestamp|MediaBox|CropBox).*\n", "", text)

    # Remove long whitespace runs
    text = re.sub(r"[ \t]{2,}", " ", text)

    # Optional: remove page numbers or page headers
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)

    # Remove non-informative uppercase lines (often noise in scans)
    text = re.sub(r"^[A-Z\s]{15,}$", "", text, flags=re.MULTILINE)

    print(text)  # optional debug

    return text.strip()