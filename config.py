from sqlalchemy.orm import Session
import models


def save_lead(db: Session, lead_data: dict):
    db_lead = models.Lead(**lead_data)
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead.id


"""def get_recent_leads(db: Session, limit=10):
    return (
        db.query(models.Lead)
        .order_by(models.Lead.created_at.desc())
        .limit(limit)
        .all()
    )"""
