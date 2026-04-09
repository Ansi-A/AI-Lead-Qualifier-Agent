import imaplib
import email
from email.header import decode_header
from email.utils import parseaddr
from dotenv import load_dotenv
import requests
import os
import time
import smtplib
from email.message import EmailMessage
import os

# Load .env file (call this once at the top of each file)
load_dotenv()

# Now use variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

IMAP_SERVER = "imap.gmail.com"
EMAIL = os.getenv("GMAIL_EMAIL")
PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
API_URL = "http://localhost:8000/lead"

STATE_FILE = "last_uid.txt"


def load_last_uid():
    if not os.path.exists(STATE_FILE):
        return 0
    with open(STATE_FILE, "r") as f:
        try:
            return int(f.read().strip())
        except ValueError:
            return 0


def save_last_uid(uid):
    with open(STATE_FILE, "w") as f:
        f.write(str(uid))


def connect():
    while True:
        try:
            mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            mail.login(EMAIL, PASSWORD)
            mail.select("INBOX")
            return mail
        except Exception as e:
            print("Connection failed:", e)
            time.sleep(5)
def get_latest_uid(mail):
    status, data = mail.uid("search", None, "ALL")
    
    if status != "OK" or not data[0]:
        return 0
    return int(data[0].split()[-1])


def fetch_new_emails(mail, last_uid):
    status, data = mail.uid("search", None, f"UID {last_uid+1}:*")
    if status != "OK":
        return [], last_uid

    uids = data[0].split()
    leads = []
    max_uid = last_uid

    for uid in uids:
        uid_int = int(uid)

        if uid_int <= last_uid:
            continue

        status, msg_data = mail.uid("fetch", uid, "(RFC822)")
        if status != "OK":
            continue

        msg = email.message_from_bytes(msg_data[0][1])

        subject = decode_header(msg["Subject"])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode(errors="ignore")

        from_addr = msg["From"]
        name, email_addr = parseaddr(from_addr)
        name = name.strip() if name else ""

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode(errors="ignore")

        leads.append({
            "name": name,
            "email": email_addr,
            "message": f"Subject: {subject}\n\n{body[:500]}"
        })

        if uid_int > max_uid:
            max_uid = uid_int

    return leads, max_uid
def send_email(to_email: str, subject: str, body: str):
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = os.getenv("GMAIL_EMAIL")
        msg["To"] = to_email
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(
                os.getenv("GMAIL_EMAIL"), 
                os.getenv("GMAIL_APP_PASSWORD")
            )
            server.send_message(msg)
        print(f'{to_email}')
        
        
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def process_lead(lead):
    try:
        response = requests.post(API_URL, json=lead, timeout=30)
        if response.status_code == 200:
            print("Processed:", lead["email"])
        else:
            print("API error:", response.status_code)
    except Exception as e:
        print("API error:", e)


if __name__ == "__main__":
    print("Worker started")

    mail = connect()

    last_uid = load_last_uid()

    if last_uid == 0:
        last_uid = get_latest_uid(mail)
        save_last_uid(last_uid)

    print("Starting from UID:", last_uid)

    loop_count = 0

    while True:
        try:
            # reconnect every 5 loops (~50 sec)
            if loop_count % 5 == 0:
                mail = connect()

            leads, new_uid = fetch_new_emails(mail, last_uid)

            print("New emails:", len(leads))

            for lead in leads:
                process_lead(lead)

            if new_uid > last_uid:
                last_uid = new_uid
                save_last_uid(last_uid)

            loop_count += 1
            time.sleep(10)

        except Exception as e:
            print("Worker error:", e)
            time.sleep(15)
