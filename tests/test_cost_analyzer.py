from backend.app.services.cost_analyzer import (
    analyze_costs,
    detect_cost_spikes,
    detect_service_anomalies,
)


def test_analyze_costs():
    cost_data = [
        {"service": "EC2", "current_cost": 72.30, "previous_cost": 55.00},
        {"service": "S3", "current_cost": 31.20, "previous_cost": 28.00},
        {"service": "RDS", "current_cost": 25.00, "previous_cost": 20.00},
        {"service": "Lambda", "current_cost": 14.00, "previous_cost": 13.00},
        {"service": "CloudWatch", "current_cost": 8.50, "previous_cost": 6.00},
        {"service": "ECR", "current_cost": 6.20, "previous_cost": 5.00},
        {"service": "DynamoDB", "current_cost": 4.80, "previous_cost": 4.50},
        {"service": "CloudFront", "current_cost": 3.75, "previous_cost": 3.00},
    ]

    result = analyze_costs(cost_data)

    # Overall cost analysis
    assert result["total_current_cost"] == 165.75
    assert result["total_previous_cost"] == 134.50
    assert result["change_percentage"] == 23.23

    # Highest total spending service
    assert result["top_service"]["service"] == "EC2"
    assert result["top_service"]["cost"] == 72.30

    # Highest percentage increase
    assert result["top_service_by_increase"]["service"] == "CloudWatch"
    assert result["top_service_by_increase"]["change_percentage"] == 41.67

    # Largest absolute dollar increase
    assert result["top_service_by_cost_increase"]["service"] == "EC2"
    assert result["top_service_by_cost_increase"]["increase"] == 17.30

    # Service breakdown
    assert len(result["service_breakdown"]) == 8

    # Ranking #1: EC2
    assert result["service_breakdown"][0]["service"] == "EC2"
    assert result["service_breakdown"][0]["cost"] == 72.30
    assert result["service_breakdown"][0]["percentage"] == 43.62
    assert result["service_breakdown"][0]["previous_cost"] == 55.00
    assert result["service_breakdown"][0]["change_percentage"] == 31.45

    # Ranking #2: RDS
    assert result["service_breakdown"][1]["service"] == "RDS"
    assert result["service_breakdown"][1]["cost"] == 25.00

    # Ranking #3: S3
    assert result["service_breakdown"][2]["service"] == "S3"
    assert result["service_breakdown"][2]["cost"] == 31.20

    # Ranking #4: CloudWatch
    assert result["service_breakdown"][3]["service"] == "CloudWatch"
    assert result["service_breakdown"][3]["change_percentage"] == 41.67


def test_detect_cost_spikes():
    daily_costs = [
        {"date": "2026-09-22", "cost": 12.00},
        {"date": "2026-09-23", "cost": 13.00},
        {"date": "2026-09-24", "cost": 14.00},
        {"date": "2026-09-25", "cost": 42.00},
        {"date": "2026-09-26", "cost": 15.00},
    ]

    spikes = detect_cost_spikes(daily_costs)

    assert len(spikes) == 1
    assert spikes[0]["date"] == "2026-09-25"
    assert spikes[0]["cost"] == 42.00
    assert spikes[0]["average_cost"] == 19.20
    assert spikes[0]["increase_percentage"] == 118.75


def test_detect_service_anomalies():
    service_breakdown = [
        {
            "service": "EC2",
            "cost": 72.30,
            "previous_cost": 55.00,
            "percentage": 43.62,
            "change_percentage": 31.45,
        },
        {
            "service": "S3",
            "cost": 31.20,
            "previous_cost": 28.00,
            "percentage": 18.82,
            "change_percentage": 11.43,
        },
        {
            "service": "CloudWatch",
            "cost": 8.50,
            "previous_cost": 6.00,
            "percentage": 5.13,
            "change_percentage": 41.67,
        },
    ]

    anomalies = detect_service_anomalies(service_breakdown)

    assert len(anomalies) == 2

    assert anomalies[0]["service"] == "EC2"
    assert anomalies[0]["change_percentage"] == 31.45

    assert anomalies[1]["service"] == "CloudWatch"
    assert anomalies[1]["change_percentage"] == 41.67


def test_detect_service_anomalies_custom_threshold():
    service_breakdown = [
        {
            "service": "EC2",
            "cost": 72.30,
            "previous_cost": 55.00,
            "percentage": 43.62,
            "change_percentage": 31.45,
        },
        {
            "service": "S3",
            "cost": 31.20,
            "previous_cost": 28.00,
            "percentage": 18.82,
            "change_percentage": 11.43,
        },
    ]

    anomalies = detect_service_anomalies(
        service_breakdown,
        threshold=10
    )

    assert len(anomalies) == 2
    assert anomalies[0]["service"] == "EC2"
    assert anomalies[1]["service"] == "S3"


def test_detect_service_anomalies_empty_input():
    anomalies = detect_service_anomalies([])

    assert anomalies == []