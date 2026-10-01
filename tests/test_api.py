from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "AI Cloud Cost Detective API"


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "ai-cloud-cost-detective"
    assert data["version"] == "0.1.0"


def test_readiness_check():
    response = client.get("/health/ready")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ready"
    assert data["service"] == "ai-cloud-cost-detective"

    assert data["configuration"]["aws_region"] == "eu-north-1"
    assert data["configuration"]["ai_provider"] == "mock"
    assert data["configuration"]["cost_data_provider"] == "mock"


@patch("backend.app.main.get_cost_data_provider")
def test_readiness_check_rejects_invalid_provider(
    mock_get_provider,
):
    mock_get_provider.return_value = "invalid-provider"

    response = client.get("/health/ready")

    assert response.status_code == 503

    data = response.json()

    assert data["detail"]["status"] == "not_ready"
    assert data["detail"]["service"] == "ai-cloud-cost-detective"

    assert (
        "Unsupported cost data provider"
        in data["detail"]["reason"]
    )


def test_cost_summary():
    response = client.get("/costs/summary")

    assert response.status_code == 200

    data = response.json()

    assert "total_current_cost" in data
    assert "total_previous_cost" in data
    assert "change_percentage" in data
    assert "top_service" in data
    assert "service_breakdown" in data


def test_cost_summary_values():
    response = client.get("/costs/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_current_cost"] == 62.40
    assert data["total_previous_cost"] == 31.50
    assert data["change_percentage"] == 98.1

    assert (
        data["top_service"]["service"]
        == "Amazon Elastic Compute Cloud - Compute"
    )

    assert data["top_service"]["cost"] == 42.80


def test_cost_spikes():
    response = client.get("/costs/spikes")

    assert response.status_code == 200

    data = response.json()

    assert "spikes" in data
    assert isinstance(data["spikes"], list)


def test_cost_spikes_detects_september_27():
    response = client.get("/costs/spikes")

    assert response.status_code == 200

    data = response.json()

    spikes = data["spikes"]

    assert len(spikes) >= 1

    spike_dates = [
        spike["date"]
        for spike in spikes
    ]

    assert "2026-09-27" in spike_dates


def test_cost_anomalies():
    response = client.get("/costs/anomalies")

    assert response.status_code == 200

    data = response.json()

    assert "anomalies" in data
    assert isinstance(data["anomalies"], list)


def test_cost_anomalies_detects_services():
    response = client.get("/costs/anomalies")

    assert response.status_code == 200

    data = response.json()

    anomalies = data["anomalies"]

    assert len(anomalies) >= 1

    services = [
        anomaly["service"]
        for anomaly in anomalies
    ]

    assert (
        "Amazon Elastic Compute Cloud - Compute"
        in services
    )


def test_cost_dashboard():
    response = client.get("/costs/dashboard")

    assert response.status_code == 200

    data = response.json()

    assert "period" in data
    assert "summary" in data
    assert "service_breakdown" in data
    assert "daily_costs" in data
    assert "spikes" in data
    assert "anomalies" in data


def test_cost_dashboard_summary():
    response = client.get("/costs/dashboard")

    assert response.status_code == 200

    data = response.json()

    summary = data["summary"]

    assert summary["total_current_cost"] == 62.40
    assert summary["total_previous_cost"] == 31.50
    assert summary["change_percentage"] == 98.1

    assert (
        summary["top_service"]["service"]
        == "Amazon Elastic Compute Cloud - Compute"
    )

    assert summary["top_service"]["cost"] == 42.80

def test_cost_dashboard_daily_costs():
    response = client.get("/costs/dashboard")

    assert response.status_code == 200

    data = response.json()

    daily_costs = data["daily_costs"]

    assert len(daily_costs) == 29

    assert daily_costs[0]["date"] == "2026-09-01"
    assert daily_costs[-1]["date"] == "2026-09-29"


def test_cost_dashboard_spikes():
    response = client.get("/costs/dashboard")

    assert response.status_code == 200

    data = response.json()

    spikes = data["spikes"]

    assert len(spikes) >= 1

    assert any(
        spike["date"] == "2026-09-27"
        for spike in spikes
    )


def test_cost_dashboard_anomalies():
    response = client.get("/costs/dashboard")

    assert response.status_code == 200

    data = response.json()

    anomalies = data["anomalies"]

    assert len(anomalies) >= 1


@patch("backend.app.main.analyze_with_ai")
def test_ai_analyze(mock_analyze):
    mock_analyze.return_value = {
        "provider": "mock",
        "question": "Why did my AWS costs increase?",
        "analysis": "EC2 costs increased significantly.",
    }

    response = client.post(
        "/ai/analyze",
        json={
            "question": "Why did my AWS costs increase?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["provider"] == "mock"
    assert (
        data["question"]
        == "Why did my AWS costs increase?"
    )
    assert (
        data["analysis"]
        == "EC2 costs increased significantly."
    )

    mock_analyze.assert_called_once()


@patch("backend.app.main.analyze_with_ai")
def test_ai_analyze_receives_investigation_data(
    mock_analyze,
):
    mock_analyze.return_value = {
        "provider": "mock",
        "question": "Why is EC2 expensive?",
        "analysis": "EC2 is the largest cost.",
    }

    response = client.post(
        "/ai/analyze",
        json={
            "question": "Why is EC2 expensive?"
        },
    )

    assert response.status_code == 200

    mock_analyze.assert_called_once()

    call_kwargs = mock_analyze.call_args.kwargs

    assert (
        call_kwargs["question"]
        == "Why is EC2 expensive?"
    )

    investigation_data = call_kwargs[
        "investigation_data"
    ]

    assert "period" in investigation_data
    assert "summary" in investigation_data
    assert "service_breakdown" in investigation_data
    assert "daily_costs" in investigation_data
    assert "spikes" in investigation_data
    assert "anomalies" in investigation_data


def test_ai_analyze_requires_question():
    response = client.post(
        "/ai/analyze",
        json={},
    )

    assert response.status_code == 422


def test_ai_analyze_rejects_invalid_question_type():
    response = client.post(
        "/ai/analyze",
        json={
            "question": 123,
        },
    )

    assert response.status_code == 422


def test_ai_analyze_accepts_empty_question():
    with patch(
        "backend.app.main.analyze_with_ai"
    ) as mock_analyze:
        mock_analyze.return_value = {
            "provider": "mock",
            "question": "",
            "analysis": "No question provided.",
        }

        response = client.post(
            "/ai/analyze",
            json={
                "question": "",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["question"] == ""


def test_cost_summary_service_breakdown():
    response = client.get("/costs/summary")

    assert response.status_code == 200

    data = response.json()

    service_breakdown = data["service_breakdown"]

    assert isinstance(service_breakdown, list)
    assert len(service_breakdown) == 5

    services = [
        item["service"]
        for item in service_breakdown
    ]

    assert (
        "Amazon Elastic Compute Cloud - Compute"
        in services
    )

    assert (
        "Amazon Simple Storage Service"
        in services
    )


def test_cost_summary_contains_percentage_changes():
    response = client.get("/costs/summary")

    assert response.status_code == 200

    data = response.json()

    service_breakdown = data["service_breakdown"]

    for service in service_breakdown:
        assert "service" in service
        assert "cost" in service
        assert "previous_cost" in service
        assert "percentage" in service

def test_cost_summary_top_service_by_cost_increase():
    response = client.get("/costs/summary")

    assert response.status_code == 200

    data = response.json()

    assert (
        data["top_service_by_cost_increase"]["service"]
        == "Amazon Elastic Compute Cloud - Compute"
    )

    assert (
        data["top_service_by_cost_increase"]["increase"]
        == 22.8
    )


def test_cost_summary_top_service_by_percentage_increase():
    response = client.get("/costs/summary")

    assert response.status_code == 200

    data = response.json()

    assert (
        data["top_service_by_increase"]["service"]
        == "AWS Lambda"
    )

    assert (
        data["top_service_by_increase"]["change_percentage"]
        == 260.0
    )

def test_cost_dashboard_period():
    response = client.get("/costs/dashboard")

    assert response.status_code == 200

    data = response.json()

    period = data["period"]

    assert "current_start" in period
    assert "current_end" in period
    assert "previous_start" in period
    assert "previous_end" in period


def test_unknown_endpoint_returns_404():
    response = client.get("/does-not-exist")

    assert response.status_code == 404