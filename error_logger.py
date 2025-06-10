import json
from datetime import datetime

def log_extraction_error(ticket_id, filename, error_detail):
    error_entry = {
        "ticket_id": ticket_id,
        "filename": filename,
        "error": error_detail,
        "timestamp": datetime.utcnow().isoformat()
    }

    with open("error_log.json", "a") as f:
        f.write(json.dumps(error_entry) + "\n")