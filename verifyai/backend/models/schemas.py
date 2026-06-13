from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class VerdictEnum(str, Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    MISLEADING = "MISLEADING"
    UNVERIFIABLE = "UNVERIFIABLE"
    PARTIALLY_TRUE = "PARTIALLY_TRUE"

class Claim(BaseModel):
    id: str
    text: str
    sub_claims: Optional[List['Claim']] = []
    verdict: Optional[VerdictEnum] = None
    confidence: Optional[float] = None
    evidence: Optional[List[str]] = []

class Source(BaseModel):
    url: str
    title: str
    credibility_score: float
    snippet: str
    domain: str

class AgentEvent(BaseModel):
    agent: str
    status: str  # "thinking" | "done" | "error"
    message: str
    data: Optional[dict] = None

class InvestigationResult(BaseModel):
    original_text: str
    cleaned_text: str
    detected_language: str
    language_name: str
    claims: List[Claim]
    sources: List[Source]
    overall_verdict: VerdictEnum
    confidence_score: float
    verdict_summary: str
    timeline: List[dict]
    is_whatsapp_forward: bool
    shareable_card_data: dict

class InvestigationRequest(BaseModel):
    text: Optional[str] = None
    image_base64: Optional[str] = None