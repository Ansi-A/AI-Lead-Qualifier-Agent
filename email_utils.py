import smtplib
import os
from email.message import EmailMessage


def send_email(to_email: str, subject: str, body: str):
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = os.getenv("GMAIL_EMAIL")
        msg["To"] = to_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(os.getenv("GMAIL_EMAIL"), os.getenv("GMAIL_APP_PASSWORD"))
            server.send_message(msg)

        print(f"Email sent to {to_email}")
        return True

    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
