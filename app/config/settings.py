import os
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()

# Environment variables
DATABASE_URL: str = os.getenv("DATABASE_URL")
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
GMAIL_EMAIL: str = os.getenv("GMAIL_EMAIL")
GMAIL_APP_PASSWORD: str = os.getenv("GMAIL_APP_PASSWORD")

# Lead filtering constants
SPAM_PATTERNS: List[str] = [
    "unsubscribe",
    "newsletter",
    "digest",
    "weekly update",
    "password reset",
    "verify your",
    "confirm your",
    "receipt",
    "invoice",
    "order confirmation",
    "track your",
    "shipping",
    "delivery",
    "no-reply",
    "noreply",
    "do-not-reply",
    "linkedin",
    "twitter notification",
    "facebook alert",
    "mailer-daemon",
    "delivery status",
    "failure notice",
]

# Budget thresholds
BUDGET_REJECT_THRESHOLD: int = 300
BUDGET_ASK_MORE_THRESHOLD: int = 800

# Default LLM fallback
LLM_FALLBACK: Dict[str, Any] = {"intent": "unknown", "budget": None, "urgency": "low"}
