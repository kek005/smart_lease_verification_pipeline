import pdfplumber

def extract_text_from_pdf(file):
    try:
        with pdfplumber.open(file) as pdf:
            all_text = "\n".join(
                [page.extract_text() for page in pdf.pages if page.extract_text()]
            )
        return all_text.strip()
    except Exception as e:
        return f"⚠️ Error extracting text: {e}"