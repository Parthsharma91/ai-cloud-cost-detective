from typing import Any


def get_mock_service_costs() -> list[dict[str, Any]]:
    return [
        {
            "service": "Amazon Elastic Compute Cloud - Compute",
            "cost": 42.80,
        },
        {
            "service": "Amazon Simple Storage Service",
            "cost": 8.40,
        },
        {
            "service": "AmazonCloudWatch",
            "cost": 5.20,
        },
        {
            "service": "AWS Lambda",
            "cost": 3.60,
        },
        {
            "service": "AWS Data Transfer",
            "cost": 2.40,
        },
    ]


def get_mock_previous_service_costs() -> list[dict[str, Any]]:
    return [
        {
            "service": "Amazon Elastic Compute Cloud - Compute",
            "cost": 20.00,
        },
        {
            "service": "Amazon Simple Storage Service",
            "cost": 7.00,
        },
        {
            "service": "AmazonCloudWatch",
            "cost": 2.00,
        },
        {
            "service": "AWS Lambda",
            "cost": 1.00,
        },
        {
            "service": "AWS Data Transfer",
            "cost": 1.50,
        },
    ]


def get_mock_daily_costs() -> list[dict[str, Any]]:
    return [
        {"date": "2026-09-01", "cost": 1.20},
        {"date": "2026-09-02", "cost": 1.40},
        {"date": "2026-09-03", "cost": 1.30},
        {"date": "2026-09-04", "cost": 1.50},
        {"date": "2026-09-05", "cost": 1.40},
        {"date": "2026-09-06", "cost": 1.60},
        {"date": "2026-09-07", "cost": 1.50},
        {"date": "2026-09-08", "cost": 1.70},
        {"date": "2026-09-09", "cost": 1.60},
        {"date": "2026-09-10", "cost": 1.80},
        {"date": "2026-09-11", "cost": 1.70},
        {"date": "2026-09-12", "cost": 1.90},
        {"date": "2026-09-13", "cost": 1.80},
        {"date": "2026-09-14", "cost": 1.70},
        {"date": "2026-09-15", "cost": 1.90},
        {"date": "2026-09-16", "cost": 1.80},
        {"date": "2026-09-17", "cost": 1.70},
        {"date": "2026-09-18", "cost": 1.90},
        {"date": "2026-09-19", "cost": 1.80},
        {"date": "2026-09-20", "cost": 1.70},
        {"date": "2026-09-21", "cost": 1.90},
        {"date": "2026-09-22", "cost": 1.80},
        {"date": "2026-09-23", "cost": 1.70},
        {"date": "2026-09-24", "cost": 1.90},
        {"date": "2026-09-25", "cost": 1.80},
        {"date": "2026-09-26", "cost": 1.70},
        {"date": "2026-09-27", "cost": 4.80},
        {"date": "2026-09-28", "cost": 1.90},
        {"date": "2026-09-29", "cost": 1.80},
    ]