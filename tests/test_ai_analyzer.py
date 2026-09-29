from backend.app.ai.analyzer import (
    analyze_with_ai,
    build_cost_analysis_prompt,
    create_mock_ai_analysis,
)


def test_build_cost_analysis_prompt():
    investigation_data = {
        "summary": {
            "total_current_cost": 100.00,
            "total_previous_cost": 80.00,
            "change_percentage": 25.00,
        }
    }

    prompt = build_cost_analysis_prompt(
        question="Why did my AWS cost increase?",
        investigation_data=investigation_data,
    )

    assert "Why did my AWS cost increase?" in prompt
    assert "AWS COST INVESTIGATION DATA" in prompt
    assert "100.0" in prompt
    assert "80.0" in prompt
    assert "25.0" in prompt


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
        question="Why did my AWS cost increase?",
        investigation_data=investigation_data,
    )

    assert result["question"] == "Why did my AWS cost increase?"
    assert result["confidence"] == "high"
    assert result["cost_drivers"] == []
    assert result["estimated_savings"]["amount"] == 0.0


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

    assert len(result["cost_drivers"]) == 2

    assert result["cost_drivers"][0]["service"] == "EC2"
    assert result["cost_drivers"][0]["current_cost"] == 72.30

    assert result["cost_drivers"][1]["service"] == "EC2"
    assert result["cost_drivers"][1]["increase"] == 17.30

    assert len(result["possible_causes"]) == 2


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

    analysis = result["analysis"]

    assert analysis["question"] == (
        "Show me my AWS cost situation."
    )
    assert "summary" in analysis
    assert "cost_drivers" in analysis
    assert "possible_causes" in analysis
    assert "recommendations" in analysis
    assert "estimated_savings" in analysis
    assert "confidence" in analysis