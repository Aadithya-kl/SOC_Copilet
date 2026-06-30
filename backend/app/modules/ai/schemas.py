from typing import List, Optional
from pydantic import BaseModel, Field

class Citation(BaseModel):
    id: str = Field(..., description="The ID of the Evidence, Correlation Group, or Timeline Event being cited.")
    type: str = Field(..., description="The type of citation (e.g., 'evidence', 'correlation_group', 'timeline_event').")

class AttackAnalysisResult(BaseModel):
    conclusion: str = Field(..., description="Brief summary of whether this is a successful attack, failed attempt, or benign.")
    confidence: str = Field(..., description="High, Medium, or Low")
    narrative: str = Field(..., description="Detailed step-by-step explanation of the attack chain.")
    citations: List[Citation] = Field(default_factory=list, description="References to deterministic evidence.")

class ContainmentRecommendation(BaseModel):
    action: str = Field(..., description="The containment action to take (e.g., 'Block IP').")
    target: str = Field(..., description="The specific target (e.g., '192.168.1.50').")
    reasoning: str = Field(..., description="Why this action is recommended.")
    citations: List[Citation] = Field(default_factory=list, description="References to deterministic evidence supporting this.")

class RemediationRecommendation(BaseModel):
    action: str = Field(..., description="The remediation action to take (e.g., 'Reset password').")
    target: str = Field(..., description="The specific target (e.g., 'admin_user').")
    reasoning: str = Field(..., description="Why this action is recommended.")
    citations: List[Citation] = Field(default_factory=list, description="References to deterministic evidence supporting this.")

class RecommendationsResult(BaseModel):
    containment: List[ContainmentRecommendation]
    remediation: List[RemediationRecommendation]

class RootCauseAnalysisResult(BaseModel):
    root_cause: str = Field(..., description="The primary reason the incident occurred.")
    vulnerability_exploited: Optional[str] = Field(None, description="Any specific vulnerability exploited.")
    citations: List[Citation] = Field(default_factory=list)

class ExplanationResult(BaseModel):
    explanation: str = Field(..., description="The explanation requested.")
    citations: List[Citation] = Field(default_factory=list)
