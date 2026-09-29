from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app.core.date_utils import (
    get_current_and_previous_month_periods,
)
from backend.app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "message": "AI Cloud Cost Detective API"
    }


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "ai-cloud-cost-detective"
    assert data["version"] == "0.1.0"


@patch("backend.app.main.get_monthly_service_comparison")
def test_cost_summary(mock_get_costs):
    mock_get_costs.return_value = [
        {
            "service": "EC2",
            "current_cost": 72.30,
            "previous_cost": 55.00,
        },
        {
            "service": "S3",
            "current_cost": 31.20,
            "previous_cost": 28.00,
        },
        {
            "service": "RDS",
            "current_cost": 25.00,
            "previous_cost": 20.00,
        },
    ]

    response = client.get("/costs/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_current_cost"] == 128.50
    assert data["total_previous_cost"] == 103.00
    assert data["change_percentage"] == 24.76

    assert data["top_service"]["service"] == "EC2"
    assert data["top_service"]["cost"] == 72.30

    periods = get_current_and_previous_month_periods()

    mock_get_costs.assert_called_once_with(
        current_start=periods["current_start"],
        current_end=periods["current_end"],
        previous_start=periods["previous_start"],
        previous_end=periods["previous_end"],
    )


@patch("backend.app.main.get_daily_costs")
def test_detect_cost_spikes(mock_get_daily_costs):
    mock_get_daily_costs.return_value = [
        {
            "date": "2026-09-22",
            "cost": 12.00,
        },
        {
            "date": "2026-09-23",
            "cost": 13.00,
        },
        {
            "date": "2026-09-24",
            "cost": 14.00,
        },
        {
            "date": "2026-09-25",
            "cost": 42.00,
        },
        {
            "date": "2026-09-26",
            "cost": 15.00,
        },
    ]

    response = client.get("/costs/spikes")

    assert response.status_code == 200

    data = response.json()

    assert "spikes" in data
    assert len(data["spikes"]) == 1

    assert data["spikes"][0]["date"] == "2026-09-25"
    assert data["spikes"][0]["cost"] == 42.00

    periods = get_current_and_previous_month_periods()

    mock_get_daily_costs.assert_called_once_with(
        start_date=periods["current_start"],
        end_date=periods["current_end"],
    )


@patch("backend.app.main.get_monthly_service_comparison")
def test_cost_anomalies(mock_get_costs):
    mock_get_costs.return_value = [
        {
            "service": "EC2",
            "current_cost": 72.30,
            "previous_cost": 55.00,
        },
        {
            "service": "S3",
            "current_cost": 31.20,
            "previous_cost": 28.00,
        },
        {
            "service": "CloudWatch",
            "current_cost": 8.50,
            "previous_cost": 6.00,
        },
    ]

    response = client.get("/costs/anomalies")

    assert response.status_code == 200

    data = response.json()

    assert "anomalies" in data

    assert len(data["anomalies"]) == 2

    assert data["anomalies"][0]["service"] == "EC2"
    assert data["anomalies"][0]["change_percentage"] == 31.45

    assert data["anomalies"][1]["service"] == "CloudWatch"
    assert data["anomalies"][1]["change_percentage"] == 41.67

    periods = get_current_and_previous_month_periods()

    mock_get_costs.assert_called_once_with(
        current_start=periods["current_start"],
        current_end=periods["current_end"],
        previous_start=periods["previous_start"],
        previous_end=periods["previous_end"],
    )