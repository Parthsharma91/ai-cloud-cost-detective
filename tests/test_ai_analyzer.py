from backend.app.ai.analyzer import (
    analyze_with_ai,
    build_cost_analysis_prompt,
    create_mock_ai_analysis,
)


def test_build_cost_analysis_prompt():
    investigation_data = {
        "summary": {
            "total_current_cost": 165.75,
            "total_previous_cost": 134.50,
            "change_percentage": 23.23,
        },
        "service_breakdown": [],
        "daily_costs": [],
        "spikes": [],
        "anomalies": [],
    }

    prompt = build_cost_analysis_prompt(
        question="Why did my AWS cost increase?",
        investigation_data=investigation_data,
    )

    assert "Why did my AWS cost increase?" in prompt
    assert "165.75" in prompt
    assert "134.5" in prompt
    assert "23.23" in prompt
    assert "AWS FinOps" in prompt


def test_create_mock_ai_analysis_zero_cost():
    investigation_data = {
        "summary": {
            "total_current_cost": 0.0,
            "total_previous_cost": 0.0,
            "change_percentage": 0,
        },
        "service_breakdown": [],
        "daily_costs": [],
        "spikes": [],
        "anomalies": [],
    }

    result = create_mock_ai_analysis(
        question="Show me my AWS cost situation.",
        investigation_data=investigation_data,
    )

    assert result["question"] == "Show me my AWS cost situation."

    assert (
        result["summary"]
        == "No AWS costs were detected for the analyzed period."
    )

    assert result["cost_drivers"] == []
    assert result["possible_causes"] == []
    assert result["recommendations"] == []

    assert result["estimated_savings"]["amount"] == 0.0
    assert result["estimated_savings"]["currency"] == "USD"

    assert result["confidence"] == "high"


def test_create_mock_ai_analysis_with_costs():
    investigation_data = {
        "summary": {
            "total_current_cost": 165.75,
            "total_previous_cost": 134.50,
            "change_percentage": 23.23,
            "top_service": {
                "service": "EC2",
                "cost": 72.30,
            },
            "top_service_by_cost_increase": {
                "service": "EC2",
                "increase": 17.30,
            },
        },
        "service_breakdown": [
            {
                "service": "EC2",
                "cost": 72.30,
                "previous_cost": 55.00,
                "percentage": 43.62,
                "change_percentage": 31.45,
            }
        ],
        "daily_costs": [],
        "spikes": [],
        "anomalies": [
            {
                "service": "EC2",
                "cost": 72.30,
                "previous_cost": 55.00,
                "change_percentage": 31.45,
            }
        ],
    }

    result = create_mock_ai_analysis(
        question="Why did my AWS cost increase?",
        investigation_data=investigation_data,
    )

    assert result["question"] == "Why did my AWS cost increase?"

    assert "$165.75" in result["summary"]
    assert "$134.50" in result["summary"]
    assert "23.23%" in result["summary"]

    # EC2 is both the highest-cost service and
    # the largest absolute cost increase, so it
    # should appear only once.
    assert len(result["cost_drivers"]) == 1
    assert result["cost_drivers"][0]["service"] == "EC2"
    assert result["cost_drivers"][0]["current_cost"] == 72.30

    assert len(result["possible_causes"]) >= 1
    assert len(result["recommendations"]) >= 1
    assert result["confidence"] == "medium"


def test_analyze_with_ai_response_structure():
    investigation_data = {
        "summary": {
            "total_current_cost": 0.0,
            "total_previous_cost": 0.0,
            "change_percentage": 0,
        },
        "service_breakdown": [],
        "daily_costs": [],
        "spikes": [],
        "anomalies": [],
    }

    result = analyze_with_ai(
        question="Show me my AWS cost situation.",
        investigation_data=investigation_data,
    )

    assert result["status"] == "success"
    assert result["provider"] == "mock"
    assert "analysis" in result
    assert "structured_analysis" in result

    assert result["structured_analysis"]["provider"] == "mock"
    assert (
        result["structured_analysis"]["question"]
        == "Show me my AWS cost situation."
    )


def test_analyze_with_ai_contains_structured_analysis():
    investigation_data = {
        "summary": {
            "total_current_cost": 165.75,
            "total_previous_cost": 134.50,
            "change_percentage": 23.23,
        },
        "service_breakdown": [
            {
                "service": "EC2",
                "cost": 72.30,
                "previous_cost": 55.00,
                "percentage": 43.62,
                "change_percentage": 31.45,
            }
        ],
        "daily_costs": [],
        "spikes": [],
        "anomalies": [],
    }

    result = analyze_with_ai(
        question="Why did my AWS cost increase?",
        investigation_data=investigation_data,
    )

    structured_analysis = result["structured_analysis"]

    assert structured_analysis["provider"] == "mock"
    assert (
        structured_analysis["question"]
        == "Why did my AWS cost increase?"
    )
    assert "summary" in structured_analysis
    assert "findings" in structured_analysis
    assert "recommendations" in structured_analysis
    assert "risk_level" in structured_analysis


def test_structured_analysis_contains_finding():
    investigation_data = {
        "summary": {
            "total_current_cost": 165.75,
            "total_previous_cost": 134.50,
            "change_percentage": 23.23,
        },
        "service_breakdown": [
            {
                "service": "EC2",
                "cost": 72.30,
                "previous_cost": 55.00,
                "percentage": 43.62,
                "change_percentage": 31.45,
            }
        ],
        "daily_costs": [],
        "spikes": [],
        "anomalies": [],
    }

    result = analyze_with_ai(
        question="Why did my AWS cost increase?",
        investigation_data=investigation_data,
    )

    findings = result["structured_analysis"]["findings"]

    assert len(findings) >= 1
    assert findings[0]["service"] == "EC2"
    assert "issue" in findings[0]
    assert "evidence" in findings[0]