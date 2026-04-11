from imap_tools import MailBox, AND
import requests
import os
import time
from dotenv import load_dotenv
from datetime import date, timedelta

load_dotenv()

EMAIL = os.getenv("GMAIL_EMAIL")
PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

API_URL = "http://localhost:8000/lead"


def process_lead(lead):
    try:
        res = requests.post(API_URL, json=lead, timeout=30)
        if res.status_code == 200:
            print("Processed:", lead["email"])
            return True
        else:
            print("API error:", res.status_code)
            return False
    except Exception as e:
        print("Request failed:", e)
        return False


def fetch_and_process():
    cutoff_date = date.today() - timedelta(days=15)

    with MailBox("imap.gmail.com").login(EMAIL, PASSWORD, "INBOX") as mailbox:
        for msg in mailbox.fetch(
            AND(seen=False, date_gte=cutoff_date), reverse=True, limit=50
        ):
            try:
                name = msg.from_values.name or ""
                email_addr = msg.from_values.email or ""

                lead = {
                    "name": name,
                    "email": email_addr,
                    "message": f"Subject: {msg.subject}\n\n{msg.text[:500]}",
                }

                print("New lead:", email_addr)

                process_lead(lead)

                mailbox.flag(msg.uid, "\\Seen", True)

            except Exception as e:
                print("Processing error:", e)


if __name__ == "__main__":
    print("Worker started (imap-tools version)")

    while True:
        try:
            fetch_and_process()
            time.sleep(30)
        except Exception as e:
            print("Worker error:", e)
            time.sleep(15)
