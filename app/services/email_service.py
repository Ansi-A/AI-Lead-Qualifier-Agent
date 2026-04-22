import smtplib
from email.message import EmailMessage
from typing import Optional, TYPE_CHECKING

from ..config.settings import GMAIL_EMAIL, GMAIL_APP_PASSWORD


from fastapi import BackgroundTasks
import logging

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, body: str) -> bool:
    """Centralized email sending (used with BackgroundTasks)"""
    try:
        logger.info("sending_email", extra={"to_email": to_email, "subject": subject})
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = GMAIL_EMAIL
        msg["To"] = to_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
            server.send_message(msg)

        logger.info("email_sent", extra={"to_email": to_email, "subject": subject})
        return True
    except Exception as e:
        logger.error("email_failed", extra={"to_email": to_email, "subject": subject, "error": str(e)})
        return False


def send_centralized_email(
    background_tasks: Optional["BackgroundTasks"],
    decision: str,
    lead_email: str,
    lead_name: str,
    response_text: str,
):
    """Centralized email orchestration for leads"""
    subject_map = {
        "accept": "You're a great fit! Next steps",
        "ask_more": "Quick questions about your project",
        "reject": "Update on your request",
    }
    subject = subject_map.get(decision, "Lead update")

    body = f"""Hi {lead_name},

{response_text}

Best,
LeadGate AI"""

    if background_tasks:
        background_tasks.add_task(send_email, lead_email, subject, body)
    else:
        send_email(lead_email, subject, body)
