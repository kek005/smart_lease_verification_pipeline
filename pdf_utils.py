import pdfplumber
from pdf2image import convert_from_path
import re
from datetime import datetime
import os

# === 1. Extract All Text ===
def extract_text_from_pdf(file):
    try:
        with pdfplumber.open(file) as pdf:
            all_text = "\n".join(
                [page.extract_text() for page in pdf.pages if page.extract_text()]
            )
        return all_text.strip()
    except Exception as e:
        return f"⚠️ Error extracting text: {e}"

# === 2. Detect Which Page Has a Signature ===
def find_signature_page(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and re.search(r"sign(ed|ature)", text, re.IGNORECASE):
                    return i + 1  # 1-based index for pdf2image
    except Exception as e:
        print(f"⚠️ Error scanning pages for signature: {e}")
    return None

# === 3. Extract That Page as an Image ===
def extract_signature_image(file_path, page_number, output=None):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("outputs", exist_ok=True)

        if output is None:
            output = os.path.join("outputs", f"signature_page_p{page_number}_{timestamp}.png")

        images = convert_from_path(file_path, first_page=page_number, last_page=page_number)
        images[0].save(output, "PNG")
        return output

    except Exception as e:
        print(f"⚠️ Error extracting image from page {page_number}: {e}")
        return None