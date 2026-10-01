from typing import Any

from backend.app.ai.models import (
    AIAnalysisResponse,
    AIFinding,
    AIRecommendation,
)
from backend.app.ai.provider import AIProvider
from backend.app.core.config import get_ai_provider


def build_cost_analysis_prompt(
    question: str,
    investigation_data: dict[str, Any],
) -> str:
    summary = investigation_data.get(
        "summary",
        {},
    )

    total_current_cost = summary.get(
        "total_current_cost",
        0.0,
    )

    total_previous_cost = summary.get(
        "total_previous_cost",
        0.0,
    )

    change_percentage = summary.get(
        "change_percentage",
        0.0,
    )

    return f"""
You are an AWS FinOps and cloud cost analysis assistant.

Analyze the following AWS cost investigation data.

User question:
{question}

AWS COST INVESTIGATION DATA

Total current cost: {total_current_cost}
Total previous cost: {total_previous_cost}
Change percentage: {change_percentage}

Full investigation data:
{investigation_data}

Your analysis should:
1. Identify the main cost drivers.
2. Identify significant cost increases.
3. Explain detected daily cost spikes.
4. Use the provided evidence rather than inventing facts.
5. Provide practical AWS cost optimization recommendations.
6. Clearly distinguish observed data from assumptions.
7. Avoid claiming exact savings unless reliable data is available.

Return a structured analysis containing:
- summary
- findings
- recommendations
- risk_level
""".strip()


def create_mock_ai_analysis(
    question: str,
    investigation_data: dict[str, Any],
) -> dict[str, Any]:
    summary_data = investigation_data.get(
        "summary",
        {},
    )

    total_current_cost = summary_data.get(
        "total_current_cost",
        0.0,
    )

    total_previous_cost = summary_data.get(
        "total_previous_cost",
        0.0,
    )

    change_percentage = summary_data.get(
        "change_percentage",
        0.0,
    )

    service_breakdown = investigation_data.get(
        "service_breakdown",
        [],
    )

    spikes = investigation_data.get(
        "spikes",
        [],
    )

    anomalies = investigation_data.get(
        "anomalies",
        [],
    )

    # Handle the zero-cost edge case explicitly.
    #
    # If both the current and previous periods contain
    # no AWS costs, there are no meaningful cost drivers,
    # causes, anomalies, or optimization recommendations
    # to report.
    if (
        total_current_cost == 0.0
        and total_previous_cost == 0.0
    ):
        return {
            "question": question,
            "summary": (
                "No AWS costs were detected for "
                "the analyzed period."
            ),
            "cost_drivers": [],
            "possible_causes": [],
            "recommendations": [],
            "estimated_savings": {
                "amount": 0.0,
                "currency": "USD",
                "basis": (
                    "No AWS costs were detected, "
                    "so no savings estimate is applicable."
                ),
            },
            "confidence": "high",
        }

    cost_drivers = []

    # Identify the actual highest-cost service.
    if service_breakdown:
        top_service = max(
            service_breakdown,
            key=lambda item: item.get(
                "cost",
                0.0,
            ),
        )

        cost_drivers.append(
            {
                "service": top_service.get(
                    "service",
                    "Unknown",
                ),
                "current_cost": top_service.get(
                    "cost",
                    0.0,
                ),
                "percentage": top_service.get(
                    "percentage",
                    0.0,
                ),
                "change_percentage": top_service.get(
                    "change_percentage",
                    0.0,
                ),
            }
        )

    # Identify the service with the largest absolute increase.
    top_service_by_cost_increase = summary_data.get(
        "top_service_by_cost_increase",
    )

    if top_service_by_cost_increase:
        increase_service = top_service_by_cost_increase.get(
            "service",
            "Unknown",
        )

        # Avoid adding the same service twice.
        existing_services = {
            driver.get("service")
            for driver in cost_drivers
        }

        if increase_service not in existing_services:
            cost_drivers.append(
                {
                    "service": increase_service,
                    "increase": top_service_by_cost_increase.get(
                        "increase",
                        0.0,
                    ),
                }
            )

    possible_causes = []

    if service_breakdown:
        possible_causes.append(
            "Increased usage or consumption of one or more AWS services."
        )

    if anomalies:
        possible_causes.append(
            "Significant service-level cost changes were detected."
        )

    if spikes:
        possible_causes.append(
            "A daily cost spike was detected during the analyzed period."
        )

    summary = (
        f"AWS costs increased from "
        f"${total_previous_cost:.2f} to "
        f"${total_current_cost:.2f}, "
        f"representing a "
        f"{change_percentage:.2f}% change."
    )

    confidence = "medium"

    recommendations = []

    if service_breakdown:
        top_service = max(
            service_breakdown,
            key=lambda item: item.get(
                "cost",
                0.0,
            ),
        )

        service_name = top_service.get(
            "service",
            "the highest-cost service",
        )

        recommendations.append(
            {
                "action": (
                    f"Review usage, sizing, and configuration "
                    f"for {service_name}."
                ),
                "reason": (
                    f"{service_name} is the highest-cost "
                    "service in the analyzed period."
                ),
            }
        )

    # Add a recommendation for the largest percentage increase.
    top_service_by_increase = summary_data.get(
        "top_service_by_increase",
    )

    if top_service_by_increase:
        service_name = top_service_by_increase.get(
            "service",
            "the service",
        )

        service_change = top_service_by_increase.get(
            "change_percentage",
            0.0,
        )

        recommendations.append(
            {
                "action": (
                    f"Investigate the usage increase for "
                    f"{service_name}."
                ),
                "reason": (
                    f"{service_name} increased by "
                    f"{service_change:.2f}% compared with "
                    "the previous period."
                ),
            }
        )

    # Add a recommendation when a daily spike exists.
    if spikes:
        largest_spike = max(
            spikes,
            key=lambda item: item.get(
                "increase_percentage",
                0.0,
            ),
        )

        spike_date = largest_spike.get(
            "date",
            "the detected date",
        )

        spike_cost = largest_spike.get(
            "cost",
            0.0,
        )

        spike_increase = largest_spike.get(
            "increase_percentage",
            0.0,
        )

        recommendations.append(
            {
                "action": (
                    f"Investigate the AWS activity recorded on "
                    f"{spike_date}."
                ),
                "reason": (
                    f"Daily cost reached ${spike_cost:.2f}, "
                    f"which was {spike_increase:.2f}% above "
                    "the calculated average."
                ),
            }
        )

    estimated_savings = {
        "amount": 0.0,
        "currency": "USD",
        "basis": "No reliable savings estimate available.",
    }

    return {
        "question": question,
        "summary": summary,
        "cost_drivers": cost_drivers,
        "possible_causes": possible_causes,
        "recommendations": recommendations,
        "estimated_savings": estimated_savings,
        "confidence": confidence,
    }


class MockAIProvider(AIProvider):
    def analyze(
        self,
        question: str,
        investigation_data: dict[str, Any],
    ) -> AIAnalysisResponse:
        legacy_analysis = create_mock_ai_analysis(
            question=question,
            investigation_data=investigation_data,
        )

        findings = []

        anomalies = investigation_data.get(
            "anomalies",
            [],
        )

        spikes = investigation_data.get(
            "spikes",
            [],
        )

        # Finding: highest-cost service.
        for driver in legacy_analysis["cost_drivers"]:
            service = driver.get(
                "service",
                "Unknown",
            )

            current_cost = driver.get(
                "current_cost",
                0.0,
            )

            increase = driver.get("increase")

            if increase is not None:
                evidence = (
                    f"${increase:.2f} increase identified "
                    f"for {service}."
                )

                issue = (
                    "The service has the largest absolute "
                    "cost increase in the investigation data."
                )

                change_percentage = None

            else:
                percentage = driver.get(
                    "percentage",
                    0.0,
                )

                service_change = driver.get(
                    "change_percentage",
                    0.0,
                )

                evidence = (
                    f"${current_cost:.2f} current cost, "
                    f"{percentage:.2f}% of total spend, "
                    f"with a {service_change:.2f}% change."
                )

                issue = (
                    "The service is the largest current "
                    "cost contributor."
                )

                change_percentage = service_change

            findings.append(
                AIFinding(
                    service=service,
                    issue=issue,
                    evidence=evidence,
                    change_percentage=change_percentage,
                )
            )

        # Findings: service-level anomalies.
        existing_services = {
            finding.service
            for finding in findings
        }

        for anomaly in anomalies:
            service = anomaly.get(
                "service",
                "Unknown",
            )

            if service in existing_services:
                continue

            findings.append(
                AIFinding(
                    service=service,
                    issue=(
                        "The service experienced a significant "
                        "cost increase."
                    ),
                    evidence=(
                        f"${anomaly.get('cost', 0.0):.2f} current cost "
                        f"versus ${anomaly.get('previous_cost', 0.0):.2f} "
                        f"previous cost."
                    ),
                    change_percentage=anomaly.get(
                        "change_percentage",
                        0.0,
                    ),
                )
            )

        # Finding: daily cost spike.
        for spike in spikes:
            findings.append(
                AIFinding(
                    service="Daily AWS Spend",
                    issue=(
                        "A significant daily cost spike "
                        "was detected."
                    ),
                    evidence=(
                        f"{spike.get('date', 'Unknown date')}: "
                        f"${spike.get('cost', 0.0):.2f} daily cost "
                        f"versus ${spike.get('average_cost', 0.0):.2f} "
                        f"average, a "
                        f"{spike.get('increase_percentage', 0.0):.2f}% increase."
                    ),
                    change_percentage=spike.get(
                        "increase_percentage",
                        0.0,
                    ),
                )
            )

        recommendations = []

        for recommendation in legacy_analysis[
            "recommendations"
        ]:
            recommendations.append(
                AIRecommendation(
                    action=recommendation["action"],
                    reason=recommendation["reason"],
                    estimated_savings="Unknown",
                    confidence=legacy_analysis["confidence"],
                )
            )

        change_percentage = investigation_data.get(
            "summary",
            {},
        ).get(
            "change_percentage",
            0.0,
        )

        if change_percentage >= 50:
            risk_level = "high"
        elif change_percentage >= 20:
            risk_level = "medium"
        else:
            risk_level = "low"

        return AIAnalysisResponse(
            provider="mock",
            question=question,
            summary=legacy_analysis["summary"],
            findings=findings,
            recommendations=recommendations,
            risk_level=risk_level,
        )


def analyze_with_ai(
    question: str,
    investigation_data: dict[str, Any],
) -> dict[str, Any]:
    provider_name = get_ai_provider()

    providers = {
        "mock": MockAIProvider(),
    }

    if provider_name not in providers:
        raise ValueError(
            f"Unsupported AI provider: {provider_name}. "
            f"Supported providers: "
            f"{', '.join(sorted(providers))}"
        )

    provider = providers[provider_name]

    structured_result = provider.analyze(
        question=question,
        investigation_data=investigation_data,
    )

    legacy_analysis = create_mock_ai_analysis(
        question=question,
        investigation_data=investigation_data,
    )

    return {
        "status": "success",
        "provider": provider_name,
        "analysis": legacy_analysis,
        "structured_analysis": structured_result.model_dump(),
    }