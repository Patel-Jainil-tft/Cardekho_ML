from pydantic import BaseModel
from typing import Optional, Dict, Any
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

class Intent(BaseModel):
    app: str
    user_input: str
    action: str
    category: Optional[str]
    data: Dict[str, Any]

class AgentResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    missing: Optional[str] = None
