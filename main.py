from fastapi import Depends, FastAPI
from groq import Groq
import os
import json
from email_utils import send_email

from database import get_db, Base, engine
from config import save_lead
import models, schema
from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

Base.metadata.create_all(bind=engine)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

executor = ThreadPoolExecutor(max_workers=2)

app = FastAPI()


client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def call_llm(prompt: str):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def is_business_inquiry(message: str):
    message = message.strip()

    if not message or len(message) < 10:
        return False, "Empty or too short (less than 10 chars)"

    message_lower = message.lower()

    spam_patterns = [
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

    for pattern in spam_patterns:
        if pattern in message_lower:
            return False, f"Spam/newsletter detected: '{pattern}'"

    return "uncertain", "Need AI to determine"


def ai_intent_filter(message: str):
    prompt = f"""
    Analyze this message. Is it a genuine business inquiry from someone seeking services?
    
    Return ONLY valid JSON:
    {{
        "is_inquiry": true/false,
        "confidence": "high/medium/low",
        "reason": "short explanation"
    }}
    
    Message: {message}
    """

    try:
        response = call_llm(prompt)
        response = response.replace("```json", "").replace("```", "").strip()
        result = json.loads(response)

        if result.get("is_inquiry"):
            return True, f"AI: {result.get('reason')}"
        else:
            return False, f"AI rejected: {result.get('reason')}"

    except Exception as e:
        return True, f"AI error ({e}), processing to be safe"


@app.post("/lead")
def process_lead(lead: schema.LeadInput, db: Session = Depends(get_db)):
    try:
        message = lead.message.strip()

        filter_result, filter_reason = is_business_inquiry(message)

        if filter_result == False:
            print(f"REJECTED ({filter_reason}): {lead.email}")
            return {
                "analysis": {
                    "intent": "filtered_out",
                    "budget": None,
                    "urgency": "low",
                },
                "score": 0,
                "decision": "ignore",
                "action": "do_nothing",
                "response": "",
                "filter_reason": filter_reason,
            }

        if filter_result == "uncertain":
            print(f"Uncertain, using AI filter for: {lead.email}")
            is_inquiry, ai_reason = ai_intent_filter(message)

            if not is_inquiry:
                print(f"AI REJECTED ({ai_reason}): {lead.email}")
                return {
                    "analysis": {
                        "intent": "filtered_out",
                        "budget": None,
                        "urgency": "low",
                    },
                    "score": 0,
                    "decision": "ignore",
                    "action": "do_nothing",
                    "response": "",
                    "filter_reason": ai_reason,
                }

            print(f"AI ACCEPTED: {lead.email}")

        print(f"Processing qualified lead: {lead.email}")

        prompt = f"""
        You are an AI extraction system.

        Extract structured data from the message.

        Rules:

        - intent:
            - Identify what the user likely wants (e.g. SaaS development, website, automation)
            - If unclear, infer the MOST PROBABLE intent from context
            - Only return "unknown" if absolutely impossible

        - budget:
            - Extract numeric value if mentioned
            - If "under 200", return 200
            - If missing → null

        - urgency:
            - high → urgent / ASAP
            - medium → soon / flexible
            - low → no clear urgency

        Return ONLY valid JSON.

        Format:
        {{
        "intent": "string",
        "budget": number or null,
        "urgency": "low|medium|high"
        }}

        Message: {lead.message}
        """

        raw_text = call_llm(prompt)

        raw_text = raw_text.replace("```json", "").replace("```", "").strip()
        if not raw_text:
            raise ValueError("Empty LLM response")

        parsed = json.loads(raw_text)

        required_fields = ["intent", "budget", "urgency"]
        for field in required_fields:
            if field not in parsed:
                raise ValueError(f"Missing field: {field}")

        score = 0

        if parsed.get("intent") and parsed["intent"] != "unknown":
            score += 3
        else:
            score += 1

        budget = parsed.get("budget")
        if budget is not None:
            if budget >= 1000:
                score += 3
            elif budget >= 500:
                score += 2
            else:
                score += 0

        urgency = parsed.get("urgency")
        if urgency == "high":
            score += 3
        elif urgency == "medium":
            score += 2
        else:
            score += 1

        score = min(score, 10)

        missing_fields = []

        if parsed.get("budget") is None:
            missing_fields.append("budget")

        if not parsed.get("intent") or parsed["intent"] == "unknown":
            missing_fields.append("intent")

        if parsed.get("urgency") is None:
            missing_fields.append("urgency")

        if not parsed.get("intent") or parsed["intent"] == "unknown":
            decision = "ask_more"

        elif budget is not None:
            if budget < 300:
                decision = "reject"
            elif budget < 800:
                if score >= 5:
                    decision = "ask_more"
                else:
                    decision = "reject"
            else:
                if score < 5:
                    decision = "reject"
                elif 5 <= score <= 6:
                    decision = "ask_more"
                else:
                    decision = "accept"
        else:
            decision = "ask_more"

        if decision == "accept":
            action = "send_booking_link"
        elif decision == "ask_more":
            action = "send_followup_questions"
        else:
            action = "send_rejection"

        if action == "send_booking_link":
            response_text = "Thank you for your interest! Based on your message, it sounds like we could be a great fit. We will get you soon!!!"
            email_body = f"""Hi {lead.name},

{response_text}

Best regards,
LeadGate AI"""
            send_email(lead.email, "You're a fit! Book your call", email_body)

        elif action == "send_followup_questions":
            followup_prompt = f"""
            You are an expert sales assistant.

            Known extracted data:
            {parsed}

            Missing information:
            {missing_fields}

            Budget status:
            {"low" if budget and budget < 800 else "acceptable"}

            Original message:
            {lead.message}

            Ask 2-3 precise follow-up questions.

            Rules:
            - Ask ONLY what is needed
            - If budget is low → ask if flexible
            - If budget missing → ask directly
            - If intent or urgency missing → ask for clarification
            - Be concise and professional

            Return plain text only.
            """

            response_text = call_llm(followup_prompt)

            email_body = f"""Hi {lead.name},

{response_text}

Best regards,
LeadGate AI"""
            send_email(lead.email, "A few questions about your project", email_body)

        else:
            response_text = (
                "Thank you for reaching out. At the moment, this is not the right fit."
            )

            email_body = f"""Hi {lead.name},

{response_text}

Best regards,
LeadGate AI"""
            send_email(lead.email, "Update on your request", email_body)

        lead_data = {
            "name": lead.name,
            "email": lead.email,
            "message": lead.message,
            "score": score,
            "decision": decision,
            "action": action,
            "response_text": response_text,
            "raw_analysis": parsed,
        }
        save_lead(db, lead_data)

        return {
            "analysis": parsed,
            "score": score,
            "decision": decision,
            "action": action,
            "response": response_text,
        }

    except Exception as e:
        return {
            "analysis": {"intent": "unknown", "budget": None, "urgency": "low"},
            "score": 1,
            "decision": "reject",
            "action": "send_rejection",
            "response": "Something went wrong while processing the request.",
            "error": str(e),
        }


@app.get("/leads", response_model=list[schema.LeadResponse])
def get_leads(db: Session = Depends(get_db)):
    leads = (
        db.query(models.Lead).order_by(models.Lead.created_at.desc()).limit(10).all()
    )
    return leads
