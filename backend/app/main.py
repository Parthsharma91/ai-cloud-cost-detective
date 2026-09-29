from fastapi import FastAPI
from pydantic import BaseModel

from backend.app.ai.analyzer import analyze_with_ai
from backend.app.aws.cost_explorer import (
    get_daily_costs,
    get_monthly_service_comparison,
)
from backend.app.core.date_utils import (
    get_current_and_previous_month_periods,
)
from backend.app.services.cost_analyzer import (
    analyze_costs,
    detect_cost_spikes,
    detect_service_anomalies,
)


class AIAnalysisRequest(BaseModel):
    question: str


app = FastAPI(
    title="AI Cloud Cost Detective",
    description="AI-powered AWS cloud cost analysis and optimization platform",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "AI Cloud Cost Detective API"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ai-cloud-cost-detective",
        "version": "0.1.0",
    }


@app.get("/costs/summary")
def cost_summary():
    periods = get_current_and_previous_month_periods()

    cost_data = get_monthly_service_comparison(
        current_start=periods["current_start"],
        current_end=periods["current_end"],
        previous_start=periods["previous_start"],
        previous_end=periods["previous_end"],
    )

    return analyze_costs(cost_data)


@app.get("/costs/spikes")
def cost_spikes():
    periods = get_current_and_previous_month_periods()

    daily_costs = get_daily_costs(
        start_date=periods["current_start"],
        end_date=periods["current_end"],
    )

    return {
        "spikes": detect_cost_spikes(daily_costs)
    }


@app.get("/costs/anomalies")
def cost_anomalies():
    periods = get_current_and_previous_month_periods()

    cost_data = get_monthly_service_comparison(
        current_start=periods["current_start"],
        current_end=periods["current_end"],
        previous_start=periods["previous_start"],
        previous_end=periods["previous_end"],
    )

    analysis = analyze_costs(cost_data)

    anomalies = detect_service_anomalies(
        analysis["service_breakdown"]
    )

    return {
        "anomalies": anomalies
    }


@app.get("/costs/dashboard")
def cost_dashboard():
    periods = get_current_and_previous_month_periods()

    # Fetch monthly service comparison
    cost_data = get_monthly_service_comparison(
        current_start=periods["current_start"],
        current_end=periods["current_end"],
        previous_start=periods["previous_start"],
        previous_end=periods["previous_end"],
    )

    # Analyze overall costs and services
    analysis = analyze_costs(cost_data)

    # Fetch daily costs
    daily_costs = get_daily_costs(
        start_date=periods["current_start"],
        end_date=periods["current_end"],
    )

    # Detect daily cost spikes
    spikes = detect_cost_spikes(daily_costs)

    # Detect service anomalies
    anomalies = detect_service_anomalies(
        analysis["service_breakdown"]
    )

    return {
        "period": periods,
        "summary": {
            "total_current_cost": analysis["total_current_cost"],
            "total_previous_cost": analysis["total_previous_cost"],
            "change_percentage": analysis["change_percentage"],
            "top_service": analysis["top_service"],
            "top_service_by_increase": analysis[
                "top_service_by_increase"
            ],
            "top_service_by_cost_increase": analysis[
                "top_service_by_cost_increase"
            ],
        },
        "service_breakdown": analysis[
            "service_breakdown"
        ],
        "daily_costs": daily_costs,
        "spikes": spikes,
        "anomalies": anomalies,
    }


@app.post("/ai/analyze")
def ai_analyze(request: AIAnalysisRequest):
    periods = get_current_and_previous_month_periods()

    # Fetch monthly service comparison
    cost_data = get_monthly_service_comparison(
        current_start=periods["current_start"],
        current_end=periods["current_end"],
        previous_start=periods["previous_start"],
        previous_end=periods["previous_end"],
    )

    # Analyze overall costs and services
    analysis = analyze_costs(cost_data)

    # Fetch daily costs
    daily_costs = get_daily_costs(
        start_date=periods["current_start"],
        end_date=periods["current_end"],
    )

    # Detect daily cost spikes
    spikes = detect_cost_spikes(daily_costs)

    # Detect service anomalies
    anomalies = detect_service_anomalies(
        analysis["service_breakdown"]
    )

    # Build the complete investigation context
    investigation_data = {
        "period": periods,
        "summary": {
            "total_current_cost": analysis[
                "total_current_cost"
            ],
            "total_previous_cost": analysis[
                "total_previous_cost"
            ],
            "change_percentage": analysis[
                "change_percentage"
            ],
            "top_service": analysis[
                "top_service"
            ],
            "top_service_by_increase": analysis[
                "top_service_by_increase"
            ],
            "top_service_by_cost_increase": analysis[
                "top_service_by_cost_increase"
            ],
        },
        "service_breakdown": analysis[
            "service_breakdown"
        ],
        "daily_costs": daily_costs,
        "spikes": spikes,
        "anomalies": anomalies,
    }

    ai_result = analyze_with_ai(
        question=request.question,
        investigation_data=investigation_data,
    )

    return ai_result