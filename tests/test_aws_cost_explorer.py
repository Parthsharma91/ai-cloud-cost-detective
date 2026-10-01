from unittest.mock import MagicMock, patch

import pytest

from backend.app.aws.cost_explorer import (
    get_daily_costs,
    get_monthly_service_comparison,
    get_service_costs,
    validate_cost_data_provider,
)


@patch("backend.app.aws.cost_explorer.get_cost_data_provider")
@patch("backend.app.aws.cost_explorer.get_cost_explorer_client")
def test_get_service_costs(
    mock_get_client,
    mock_get_provider,
):
    mock_get_provider.return_value = "aws"

    mock_client = MagicMock()

    mock_client.get_cost_and_usage.return_value = {
        "ResultsByTime": [
            {
                "TimePeriod": {
                    "Start": "2026-09-01",
                    "End": "2026-09-29",
                },
                "Groups": [
                    {
                        "Keys": ["Amazon Elastic Compute Cloud"],
                        "Metrics": {
                            "UnblendedCost": {
                                "Amount": "72.30",
                                "Unit": "USD",
                            }
                        },
                    },
                    {
                        "Keys": ["Amazon Simple Storage Service"],
                        "Metrics": {
                            "UnblendedCost": {
                                "Amount": "31.20",
                                "Unit": "USD",
                            }
                        },
                    },
                ],
            }
        ]
    }

    mock_get_client.return_value = mock_client

    costs = get_service_costs(
        "2026-09-01",
        "2026-09-29",
    )

    assert costs == [
        {
            "service": "Amazon Elastic Compute Cloud",
            "cost": 72.30,
        },
        {
            "service": "Amazon Simple Storage Service",
            "cost": 31.20,
        },
    ]

    mock_client.get_cost_and_usage.assert_called_once()


@patch("backend.app.aws.cost_explorer.get_cost_data_provider")
@patch("backend.app.aws.cost_explorer.get_service_costs")
def test_get_monthly_service_comparison(
    mock_get_service_costs,
    mock_get_provider,
):
    mock_get_provider.return_value = "aws"

    mock_get_service_costs.side_effect = [
        [
            {
                "service": "EC2",
                "cost": 72.30,
            },
            {
                "service": "S3",
                "cost": 31.20,
            },
        ],
        [
            {
                "service": "EC2",
                "cost": 55.00,
            },
            {
                "service": "S3",
                "cost": 28.00,
            },
        ],
    ]

    comparison = get_monthly_service_comparison(
        current_start="2026-09-01",
        current_end="2026-09-29",
        previous_start="2026-08-01",
        previous_end="2026-08-31",
    )

    assert comparison == [
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
    ]

    assert mock_get_service_costs.call_count == 2


@patch("backend.app.aws.cost_explorer.get_cost_data_provider")
@patch("backend.app.aws.cost_explorer.get_cost_explorer_client")
def test_get_daily_costs(
    mock_get_client,
    mock_get_provider,
):
    mock_get_provider.return_value = "aws"

    mock_client = MagicMock()

    mock_client.get_cost_and_usage.return_value = {
        "ResultsByTime": [
            {
                "TimePeriod": {
                    "Start": "2026-09-27",
                    "End": "2026-09-28",
                },
                "Total": {
                    "UnblendedCost": {
                        "Amount": "1.25",
                        "Unit": "USD",
                    }
                },
            },
            {
                "TimePeriod": {
                    "Start": "2026-09-28",
                    "End": "2026-09-29",
                },
                "Total": {
                    "UnblendedCost": {
                        "Amount": "2.50",
                        "Unit": "USD",
                    }
                },
            },
        ]
    }

    mock_get_client.return_value = mock_client

    costs = get_daily_costs(
        "2026-09-27",
        "2026-09-29",
    )

    assert costs == [
        {
            "date": "2026-09-27",
            "cost": 1.25,
        },
        {
            "date": "2026-09-28",
            "cost": 2.50,
        },
    ]

    mock_client.get_cost_and_usage.assert_called_once()


def test_validate_cost_data_provider_accepts_aws():
    assert validate_cost_data_provider("aws") == "aws"


def test_validate_cost_data_provider_rejects_invalid_provider():
    with pytest.raises(ValueError, match="Unsupported cost data provider"):
        validate_cost_data_provider("awss")
