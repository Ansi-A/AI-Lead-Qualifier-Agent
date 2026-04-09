from datetime import datetime

from pydantic import BaseModel


class LeadInput(BaseModel):
    name: str
    email: str  
    message: str
    
class LeadResponse(BaseModel):
    id: int
    name: str
    email: str
    message: str
    score: int | None = None
    decision: str | None = None
    action: str | None = None
    response_text: str | None = None
    raw_analysis: dict | None = None
    created_at: datetime | None = None  # Changed from str to datetime
    
    class Config:
        from_attributes = True