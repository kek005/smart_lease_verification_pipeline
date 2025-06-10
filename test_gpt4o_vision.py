import os
from openai import OpenAI
from dotenv import load_dotenv
from pdf2image import convert_from_path
import base64

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_image_from_pdf(pdf_path, page_number, output_path="signature_page.png"):
    images = convert_from_path(pdf_path, dpi=300, first_page=page_number, last_page=page_number)
    if images:
        images[0].save(output_path, "PNG")
        return output_path
    else:
        raise ValueError(f"Could not extract page {page_number} from PDF.")

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def test_image(image_path):
    base64_image = encode_image_to_base64(image_path)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant helping verify signatures in lease agreements."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Does this document contain a visible handwritten or digital signature?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=300
    )

    return response.choices[0].message.content

# === Run It ===
if __name__ == "__main__":
    pdf_file = "uploaded_lease.pdf"
    output_image = extract_image_from_pdf(pdf_file, page_number=52)
    result = test_image(output_image)

    print("\n[✅ GPT-4o Vision Result]")
    print(result)