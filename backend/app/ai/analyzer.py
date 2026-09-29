from typing import Any

from backend.app.ai.provider import AIProvider

from backend.app.core.config import get_ai_provider

def build_cost_analysis_prompt(
    question: str,
    investigation_data: dict[str, Any],
) -> str:
    """
    Build a structured prompt for the future AI cost analyst.

    The AI receives analyzed AWS cost data only.
    It does not receive AWS credentials or direct AWS access.
    """

    return f"""
You are an AWS FinOps cost analyst.

USER QUESTION:
{question}

AWS COST INVESTIGATION DATA:
{investigation_data}

Analyze the user's question using the available AWS cost data.

Return your response using exactly these sections:

1. Summary
2. Main cost drivers
3. Possible causes
4. Recommended actions
5. Estimated savings opportunity
6. Confidence level

Important rules:
- Use only the provided AWS cost data.
- Do not invent AWS resources.
- Do not claim that a resource exists unless the data supports it.
- Clearly distinguish observed facts from possible causes.
- Do not recommend destructive actions automatically.
- Recommendations should require user approval before execution.
- If the data is insufficient, explicitly say so.
""".strip()


def create_mock_ai_analysis(
    question: str,
    investigation_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Create a deterministic AI-style response for development
    and testing before connecting a real LLM provider.
    """

    summary = investigation_data.get(
        "summary",
        {},
    )

    current_cost = summary.get(
        "total_current_cost",
        0.0,
    )

    previous_cost = summary.get(
        "total_previous_cost",
        0.0,
    )

    change_percentage = summary.get(
        "change_percentage",
        0,
    )

    top_service = summary.get(
        "top_service"
    )

    top_service_by_cost_increase = summary.get(
        "top_service_by_cost_increase"
    )

    anomalies = investigation_data.get(
        "anomalies",
        [],
    )

    spikes = investigation_data.get(
        "spikes",
        [],
    )

    if current_cost == 0 and previous_cost == 0:
        return {
            "summary": (
                "No meaningful AWS spending was detected "
                "for the analyzed periods."
            ),
            "cost_drivers": [],
            "possible_causes": [
                "The account currently has no meaningful "
                "billable usage in the analyzed period."
            ],
            "recommendations": [
                {
                    "action": (
                        "Continue monitoring AWS costs as "
                        "resources are introduced."
                    ),
                    "reason": (
                        "Cost analysis will become more "
                        "meaningful when billable usage exists."
                    ),
                }
            ],
            "estimated_savings": {
                "amount": 0.0,
                "currency": "USD",
                "basis": (
                    "No meaningful current spending "
                    "was detected."
                ),
            },
            "confidence": "high",
            "question": question,
        }

    cost_drivers = []

    if top_service:
        cost_drivers.append({
            "service": top_service["service"],
            "current_cost": top_service["cost"],
            "observation": (
                "This service has the highest "
                "current-period cost."
            ),
        })

    if top_service_by_cost_increase:
        cost_drivers.append({
            "service": top_service_by_cost_increase[
                "service"
            ],
            "increase": top_service_by_cost_increase[
                "increase"
            ],
            "observation": (
                "This service has the largest "
                "absolute cost increase."
            ),
        })

    possible_causes = []

    if change_percentage > 0:
        possible_causes.append(
            "Overall AWS spending increased compared "
            "with the previous period."
        )
    elif change_percentage < 0:
        possible_causes.append(
            "Overall AWS spending decreased compared "
            "with the previous period."
        )
    else:
        possible_causes.append(
            "No significant overall cost change was detected."
        )

    if anomalies:
        possible_causes.append(
            "One or more AWS services exceeded the "
            "configured cost anomaly threshold."
        )

    if spikes:
        possible_causes.append(
            "One or more daily cost spikes were detected."
        )

    recommendations = [
        {
            "action": (
                "Review the highest-cost services "
                "before taking optimization actions."
            ),
            "reason": (
                "Service-level analysis helps identify "
                "where optimization may have the "
                "largest impact."
            ),
        }
    ]

    estimated_savings = {
        "amount": 0.0,
        "currency": "USD",
        "basis": (
            "A reliable savings estimate requires "
            "resource-level usage data."
        ),
    }

    return {
        "summary": (
            f"Current AWS cost is ${current_cost:.2f}, "
            f"compared with ${previous_cost:.2f} in the "
            f"previous period, representing a "
            f"{change_percentage:.2f}% change."
        ),
        "cost_drivers": cost_drivers,
        "possible_causes": possible_causes,
        "recommendations": recommendations,
        "estimated_savings": estimated_savings,
        "confidence": "medium",
        "question": question,
    }


class MockAIProvider(AIProvider):
    """
    Local deterministic AI provider used during development.

    This provider does not make external API calls.
    """

    def analyze(
        self,
        question: str,
        investigation_data: dict[str, Any],
    ) -> dict[str, Any]:
        return create_mock_ai_analysis(
            question=question,
            investigation_data=investigation_data,
        )


def analyze_with_ai(
    question: str,
    investigation_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Run the configured AI provider.

    The application talks to this function instead of
    depending directly on a specific AI vendor.
    """

    provider_name = get_ai_provider()

    if provider_name == "mock":
        provider = MockAIProvider()
    else:
        raise ValueError(
            f"Unsupported AI provider: {provider_name}"
        )

    analysis = provider.analyze(
        question=question,
        investigation_data=investigation_data,
    )

    return {
        "status": "success",
        "provider": provider_name,
        "analysis": analysis,
    }