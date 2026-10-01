from typing import Any

import boto3

from backend.app.aws.mock_cost_explorer import (
    get_mock_daily_costs,
    get_mock_previous_service_costs,
    get_mock_service_costs,
)
from backend.app.core.config import (
    get_aws_region,
    get_cost_data_provider,
)


SUPPORTED_COST_DATA_PROVIDERS = {
    "aws",
    "mock",
}

def get_cost_explorer_client():
    return boto3.client(
        "ce",
        region_name=get_aws_region(),
    )


def validate_cost_data_provider(provider: str) -> str:
    if provider not in SUPPORTED_COST_DATA_PROVIDERS:
        raise ValueError(
            f"Unsupported cost data provider: {provider}. "
            f"Supported providers: "
            f"{', '.join(sorted(SUPPORTED_COST_DATA_PROVIDERS))}"
        )

    return provider


def get_service_costs(
    start_date: str,
    end_date: str,
) -> list[dict[str, Any]]:
    provider = validate_cost_data_provider(
        get_cost_data_provider()
    )

    if provider == "mock":
        return get_mock_service_costs()

    client = get_cost_explorer_client()

    response = client.get_cost_and_usage(
        TimePeriod={
            "Start": start_date,
            "End": end_date,
        },
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[
            {
                "Type": "DIMENSION",
                "Key": "SERVICE",
            }
        ],
    )

    service_costs = []

    for result in response["ResultsByTime"]:
        for group in result["Groups"]:
            service_name = group["Keys"][0]

            amount = float(
                group["Metrics"]["UnblendedCost"]["Amount"]
            )

            service_costs.append({
                "service": service_name,
                "cost": round(amount, 2),
            })

    return service_costs


def get_monthly_service_comparison(
    current_start: str,
    current_end: str,
    previous_start: str,
    previous_end: str,
) -> list[dict[str, Any]]:
    provider = validate_cost_data_provider(
        get_cost_data_provider()
    )

    if provider == "mock":
        current_costs = get_mock_service_costs()
        previous_costs = get_mock_previous_service_costs()
    else:
        current_costs = get_service_costs(
            current_start,
            current_end,
        )

        previous_costs = get_service_costs(
            previous_start,
            previous_end,
        )

    current_map = {
        item["service"]: item["cost"]
        for item in current_costs
    }

    previous_map = {
        item["service"]: item["cost"]
        for item in previous_costs
    }

    all_services = set(current_map) | set(previous_map)

    comparison = []

    for service in all_services:
        current_cost = current_map.get(service, 0.0)
        previous_cost = previous_map.get(service, 0.0)

        comparison.append({
            "service": service,
            "current_cost": round(current_cost, 2),
            "previous_cost": round(previous_cost, 2),
        })

    comparison.sort(
        key=lambda item: item["current_cost"],
        reverse=True,
    )

    return comparison


def get_daily_costs(
    start_date: str,
    end_date: str,
) -> list[dict[str, Any]]:
    provider = validate_cost_data_provider(
        get_cost_data_provider()
    )

    if provider == "mock":
        return get_mock_daily_costs()

    client = get_cost_explorer_client()

    response = client.get_cost_and_usage(
        TimePeriod={
            "Start": start_date,
            "End": end_date,
        },
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
    )

    daily_costs = []

    for result in response["ResultsByTime"]:
        amount = float(
            result["Total"]["UnblendedCost"]["Amount"]
        )

        daily_costs.append({
            "date": result["TimePeriod"]["Start"],
            "cost": round(amount, 2),
        })

    return daily_costs

