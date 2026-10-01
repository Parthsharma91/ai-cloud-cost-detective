from pydantic import BaseModel, Field


class AIFinding(BaseModel):
    service: str
    issue: str
    evidence: str
    change_percentage: float | None = None


class AIRecommendation(BaseModel):
    action: str
    reason: str
    estimated_savings: str
    confidence: str


class AIAnalysisResponse(BaseModel):
    provider: str
    question: str
    summary: str
    findings: list[AIFinding] = Field(default_factory=list)
    recommendations: list[AIRecommendation] = Field(
        default_factory=list
    )
    risk_level: str