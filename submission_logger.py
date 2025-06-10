import json
from datetime import datetime

def log_submission(email, phone, method, ticket_id, result, duration=None):
    log = {
        "timestamp": datetime.now().isoformat(),
        "email": email,
        "phone": phone,
        "method": method,
        "ticket_id": ticket_id,
        "result": result,
        "duration": duration
    }
    with open("submission_log.json", "a") as f:
        f.write(json.dumps(log) + "\n")