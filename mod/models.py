from pydantic import BaseModel
from typing import Optional, Dict, Any

class QueryRequest(BaseModel):
    message: str
    jobid: str
    userId: str
    chatPlatform: str
    orgInitiationId: str
    missing: Optional[str] = None
    incorrect: Optional[str] = None
    chatHistory: Optional[str] = None
    userRole: str
    chain_company_name: str
    region: str
    country: str
    FollowupAgent: Optional[str]

class Intent(BaseModel):
    app: str
    action: str
    category: Optional[str]
    data: Dict[str, Any]

class AgentResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    missing: Optional[str] = None
