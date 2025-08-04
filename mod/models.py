from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any
from datetime import datetime

class QueryRequest(BaseModel):
    message: str
    jobId: Optional[str] = None  # Changed to camelCase to match your input
    userId: Optional[str] = None
    chatPlatform: Optional[str] = None
    orgInitiationId: Optional[str] = None  # Keep this if still used elsewhere
    organizationId: Optional[str] = None  # New - from your input
    missing: Optional[str] = None
    incorrect: Optional[str] = None
    chatHistory: Optional[str] = None
    userRole: Optional[str] = None
    chain_company_name: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    FollowupAgent: Optional[str] = None
    applicable: Optional[list] = None   # New
    token: Optional[dict] = None        # New
    active: int

class Intent(BaseModel):
    user_input: str
    app: str
    user_input: str
    action: str
    category: Optional[str]
    data: Dict[str, Any]

    @field_validator("data")
    def validate_applied_date(cls, v):
        applied_date = v.get("appliedDate")
        if applied_date:
            try:
                datetime.strptime(applied_date, "%d-%m-%Y")
            except ValueError:
                raise ValueError(f"appliedDate '{applied_date}' is not in DD-MM-YYYY format or not a real date.")
        return v
class AgentResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    missing: Optional[str] = None
