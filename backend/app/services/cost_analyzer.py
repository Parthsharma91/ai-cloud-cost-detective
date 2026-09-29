COST_EPSILON = 0.01


def normalize_cost(value):
    """
    Normalize AWS billing values for application use.

    AWS billing can contain tiny adjustments such as
    0.01 or -0.01. Treat values at or below one cent
    in absolute value as zero.
    """

    if abs(value) <= COST_EPSILON:
        return 0.0

    return round(value, 2)


def analyze_costs(cost_data):
    """
    Analyze AWS cost data and return a summary.
    """

    if not cost_data:
        return {
            "total_current_cost": 0.0,
            "total_previous_cost": 0.0,
            "change_percentage": 0,
            "top_service": None,
            "top_service_by_increase": None,
            "top_service_by_cost_increase": None,
            "service_breakdown": [],
        }

    normalized_data = []

    for item in cost_data:
        normalized_data.append({
            "service": item["service"],
            "current_cost": normalize_cost(
                item["current_cost"]
            ),
            "previous_cost": normalize_cost(
                item["previous_cost"]
            ),
        })

    total_current_cost = sum(
        item["current_cost"]
        for item in normalized_data
    )

    total_previous_cost = sum(
        item["previous_cost"]
        for item in normalized_data
    )

    if total_previous_cost > 0:
        change_percentage = (
            (total_current_cost - total_previous_cost)
            / total_previous_cost
        ) * 100
    else:
        change_percentage = 0

    # Highest meaningful current cost.
    top_service = max(
        normalized_data,
        key=lambda item: item["current_cost"],
    )

    if top_service["current_cost"] > 0:
        top_service_result = {
            "service": top_service["service"],
            "cost": top_service["current_cost"],
        }
    else:
        top_service_result = None

    # Only consider services that actually have
    # previous-period spending AND increased in cost.
    services_with_increase = [
        item
        for item in normalized_data
        if (
            item["previous_cost"] > 0
            and item["current_cost"]
            > item["previous_cost"]
        )
    ]

    if services_with_increase:
        top_service_by_increase = max(
            services_with_increase,
            key=lambda item: (
                (
                    item["current_cost"]
                    - item["previous_cost"]
                )
                / item["previous_cost"]
            ) * 100,
        )

        top_service_by_increase_result = {
            "service": top_service_by_increase["service"],
            "change_percentage": round(
                (
                    (
                        top_service_by_increase["current_cost"]
                        - top_service_by_increase["previous_cost"]
                    )
                    / top_service_by_increase["previous_cost"]
                ) * 100,
                2,
            ),
        }
    else:
        top_service_by_increase_result = None

    # Find the largest meaningful absolute cost increase.
    positive_increases = [
        item
        for item in normalized_data
        if (
            item["previous_cost"] >= 0
            and (
                item["current_cost"]
                - item["previous_cost"]
            ) > COST_EPSILON
        )
    ]

    if positive_increases:
        top_service_by_cost_increase = max(
            positive_increases,
            key=lambda item: (
                item["current_cost"]
                - item["previous_cost"]
            ),
        )

        increase = (
            top_service_by_cost_increase["current_cost"]
            - top_service_by_cost_increase["previous_cost"]
        )

        top_service_by_cost_increase_result = {
            "service": top_service_by_cost_increase["service"],
            "increase": round(increase, 2),
        }
    else:
        top_service_by_cost_increase_result = None

    service_breakdown = []

    for item in normalized_data:

        if total_current_cost > 0:
            percentage = (
                item["current_cost"]
                / total_current_cost
            ) * 100
        else:
            percentage = 0

        if item["previous_cost"] > 0:
            service_change_percentage = (
                (
                    item["current_cost"]
                    - item["previous_cost"]
                )
                / item["previous_cost"]
            ) * 100
        else:
            service_change_percentage = 0

        service_breakdown.append({
            "service": item["service"],
            "cost": normalize_cost(
                item["current_cost"]
            ),
            "previous_cost": normalize_cost(
                item["previous_cost"]
            ),
            "percentage": round(
                percentage,
                2,
            ),
            "change_percentage": round(
                service_change_percentage,
                2,
            ),
        })

    # Rank by absolute cost increase.
    service_breakdown.sort(
        key=lambda item: (
            item["cost"]
            - item["previous_cost"]
        ),
        reverse=True,
    )

    return {
        "total_current_cost": normalize_cost(
            total_current_cost
        ),
        "total_previous_cost": normalize_cost(
            total_previous_cost
        ),
        "change_percentage": round(
            change_percentage,
            2,
        ),
        "top_service": top_service_result,
        "top_service_by_increase": (
            top_service_by_increase_result
        ),
        "top_service_by_cost_increase": (
            top_service_by_cost_increase_result
        ),
        "service_breakdown": service_breakdown,
    }


def detect_cost_spikes(
    daily_costs,
    threshold=1.5,
):
    """
    Detect days where the cost is significantly higher
    than the average daily cost.
    """

    if not daily_costs:
        return []

    average_cost = sum(
        item["cost"]
        for item in daily_costs
    ) / len(daily_costs)

    if average_cost == 0:
        return []

    spikes = []

    for item in daily_costs:
        if item["cost"] >= average_cost * threshold:
            spikes.append({
                "date": item["date"],
                "cost": normalize_cost(
                    item["cost"]
                ),
                "average_cost": normalize_cost(
                    average_cost
                ),
                "increase_percentage": round(
                    (
                        (
                            item["cost"]
                            - average_cost
                        )
                        / average_cost
                    ) * 100,
                    2,
                ),
            })

    return spikes


def detect_service_anomalies(
    service_breakdown,
    threshold=30,
):
    """
    Detect services with a significant percentage increase.
    """

    if not service_breakdown:
        return []

    anomalies = []

    for item in service_breakdown:
        if item["change_percentage"] >= threshold:
            anomalies.append({
                "service": item["service"],
                "cost": normalize_cost(
                    item["cost"]
                ),
                "previous_cost": normalize_cost(
                    item["previous_cost"]
                ),
                "change_percentage": item[
                    "change_percentage"
                ],
            })

    return anomalies