from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from ..database.db import get_db
from ..schemas.lead_schemas import LeadInput, LeadResponse
from fastapi import HTTPException
from ..services.lead_service import (
    filter_lead,
    extract_lead_data,
    score_lead,
    decide_lead,
    generate_response_text,
    save_lead,
)
from ..services.email_service import send_centralized_email
from typing import List


router = APIRouter(prefix="/lead", tags=["leads"])


@router.post("/", response_model=dict)
def process_lead(
    lead: LeadInput,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    try:
        print(f"Processing lead from {lead.email}")

        # Step 1: Filter
        is_valid, reason = filter_lead(lead.message)
        if not is_valid:
            print(f"REJECTED ({reason}): {lead.email}")
            return {
                "analysis": {"intent": "filtered_out"},
                "score": 0,
                "decision": "ignore",
                "action": "do_nothing",
                "filter_reason": reason,
            }
        print(f"Lead passed filter: {lead.email}")

        # Step 2-4: Extract → Score → Decide
        data = extract_lead_data(lead.message)
        score = score_lead(data)
        decision = decide_lead(data, score)

        # Missing fields for followup
        missing = []
        if data.get("budget") is None:
            missing.append("budget")
        if not data.get("intent") or data.get("intent") == "unknown":
            missing.append("intent")

        # Step 5: Response text
        response_text = generate_response_text(
            decision, data, lead.name, lead.message, missing
        )

        # Action mapping
        action = (
            "send_booking_link"
            if decision == "accept"
            else "send_followup_questions"
            if decision == "ask_more"
            else "send_rejection"
        )

        # Step 6: Send email (non-blocking)
        send_centralized_email(
            background_tasks, decision, lead.email, lead.name, response_text
        )

        # Save lead
        save_lead(
            db,
            {
                "name": lead.name,
                "email": lead.email,
                "message": lead.message,
                "score": score,
                "decision": decision,
                "action": action,
                "response_text": response_text,
                "raw_analysis": data,
            },
        )

        return {
            "analysis": data,
            "score": score,
            "decision": decision,
            "action": action,
            "response": response_text,
        }

    except Exception as e:
        print(f"Error processing lead: {e}")
        return {
            "analysis": {"intent": "error"},
            "score": 0,
            "decision": "reject",
            "action": "do_nothing",
            "error": str(e),
        }


# get leads
@router.get("/s", response_model=List[LeadResponse])
def get_leads(db: Session = Depends(get_db)):
    from ..services.lead_service import get_recent_leads

    if not get_recent_leads:
        raise HTTPException(status_code=404, details="Leads not found")
    return get_recent_leads(db)
