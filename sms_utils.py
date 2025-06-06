from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()
account_sid = os.getenv("TWILIO_SID")
auth_token = os.getenv("TWILIO_TOKEN")
from_number = os.getenv("TWILIO_NUMBER")

client = Client(account_sid, auth_token)

def send_sms(to, body):
    try:
        client.messages.create(
            body=body,
            from_=from_number,
            to=to
        )
        return True
    except Exception as e:
        print(f"SMS failed: {e}")
        return False
