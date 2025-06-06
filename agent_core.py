import os
from openai import OpenAI
from dotenv import load_dotenv
from prompt_templates import SYSTEM_PROMPT, USER_INSTRUCTION_TEMPLATE

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ======= Tool Functions ======= #

def check_signature(text: str) -> dict:
    is_signed = "yes" if "signature" in text.lower() else "no"
    return {"is_signed": is_signed}

def validate_lease_dates(text: str) -> dict:
    import re
    found_dates = re.findall(r"\b\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4}\b", text)
    return {
        "valid_date_range": True if len(found_dates) >= 2 else False,
        "dates_found": found_dates
    }

def generate_response(is_signed: str, valid_date_range: bool) -> str:
    if is_signed == "yes" and valid_date_range:
        return "✅ Your lease is complete and valid. We will proceed with your account setup."
    elif is_signed == "no":
        return "❌ Your lease is missing a signature. Please sign and re-upload."
    elif not valid_date_range:
        return "❌ Your lease appears to be missing valid date ranges (start and end date)."
    else:
        return "⚠️ Unable to verify your lease. Please check and resubmit."

# ======= Tool Schema Definitions ======= #

tools = [
    {
        "type": "function",
        "function": {
            "name": "check_signature",
            "description": "Check if the lease text contains a signature.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "validate_lease_dates",
            "description": "Validate the lease date range in the text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            }
        }
    },
]

# ======= Function Router ======= #

def run_agent(ticket_id: str, document_text: str):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_INSTRUCTION_TEMPLATE.format(ticket_id=ticket_id)},
            {"role": "user", "content": document_text}
        ],
        tools=tools,
        tool_choice="auto"
    )

    tool_calls = response.choices[0].message.tool_calls
    if not tool_calls:
        return "⚠️ GPT did not call any tools. Please try again."

    # Simulate tool execution
    result_store = {}
    for call in tool_calls:
        name = call.function.name
        args = eval(call.function.arguments)

        if name == "check_signature":
            result_store["check"] = check_signature(**args)
        elif name == "validate_lease_dates":
            result_store["dates"] = validate_lease_dates(**args)

    is_signed = result_store.get("check", {}).get("is_signed", "no")
    valid_date_range = result_store.get("dates", {}).get("valid_date_range", False)

    return generate_response(is_signed, valid_date_range)