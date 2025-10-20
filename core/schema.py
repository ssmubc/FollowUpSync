from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class Decision(BaseModel):
    text: str
    rationale: Optional[str] = None
    owners: List[str] = []

class ActionItem(BaseModel):
    title: str
    owner: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[str] = Field(default="Medium", pattern="Low|Medium|High")
    notes: Optional[str] = None
    source_quote: Optional[str] = None

class Risk(BaseModel):
    text: str
    severity: Optional[str] = Field(default="Medium", pattern="Low|Medium|High")
    mitigation: Optional[str] = None

class ExtractionResult(BaseModel):
    run_id: str
    decisions: List[Decision]
    action_items: List[ActionItem]
    risks: List[Risk]
    summary_md: str