from backend.app.ai.models import (
    AIAnalysisResponse,
    AIFinding,
    AIRecommendation,
)


def test_ai_finding_model():
    finding = AIFinding(
        service="Amazon EC2",
        issue="Cost increased significantly",
        evidence="$42.80 current vs $20.00 previous",
        change_percentage=114.0,
    )

    assert finding.service == "Amazon EC2"
    assert finding.issue == "Cost increased significantly"
    assert (
        finding.evidence
        == "$42.80 current vs $20.00 previous"
    )
    assert finding.change_percentage == 114.0


def test_ai_recommendation_model():
    recommendation = AIRecommendation(
        action="Review running EC2 instances",
        reason="EC2 is the largest contributor to current spend",
        estimated_savings="Unknown",
        confidence="medium",
    )

    assert (
        recommendation.action
        == "Review running EC2 instances"
    )
    assert (
        recommendation.reason
        == "EC2 is the largest contributor to current spend"
    )
    assert recommendation.estimated_savings == "Unknown"
    assert recommendation.confidence == "medium"


def test_ai_analysis_response_model():
    response = AIAnalysisResponse(
        provider="mock",
        question="Why did my AWS costs increase?",
        summary="AWS costs increased mainly because of EC2.",
        findings=[
            AIFinding(
                service="Amazon EC2",
                issue="Cost increased significantly",
                evidence="$42.80 current vs $20.00 previous",
                change_percentage=114.0,
            )
        ],
        recommendations=[
            AIRecommendation(
                action="Review running EC2 instances",
                reason="EC2 is the largest contributor to current spend",
                estimated_savings="Unknown",
                confidence="medium",
            )
        ],
        risk_level="medium",
    )

    assert response.provider == "mock"
    assert (
        response.question
        == "Why did my AWS costs increase?"
    )
    assert (
        response.summary
        == "AWS costs increased mainly because of EC2."
    )
    assert len(response.findings) == 1
    assert len(response.recommendations) == 1
    assert response.risk_level == "medium"


def test_ai_analysis_response_defaults_lists():
    response = AIAnalysisResponse(
        provider="mock",
        question="Test question",
        summary="Test summary",
        risk_level="low",
    )

    assert response.findings == []
    assert response.recommendations == []