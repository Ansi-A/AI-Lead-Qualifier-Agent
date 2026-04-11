from pydantic import BaseModel
from datetime import datetime


class LeadInput(BaseModel):
    name: str
    email: str
    message: str


class LeadResponse(BaseModel):
    id: int
    name: str
    email: str
    message: str
    score: int
    decision: str
    action: str
    response_text: str
    created_at: datetime

    class Config:
        from_attributes = True
