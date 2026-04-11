from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class LeadInput(BaseModel):
    name: str
    email: str
    message: str


class LeadResponse(BaseModel):
    id: int
    name: str
    email: str
    message: str
    score: Optional[int]
    decision: Optional[str]
    action: Optional[str]
    response_text: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
