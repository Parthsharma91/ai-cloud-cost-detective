import { useEffect, useState } from "react";

import {
  Activity,
  AlertTriangle,
  BarChart3,
  Bot,
  ChevronRight,
  DollarSign,
  LayoutDashboard,
  Lock,
  RefreshCw,
  Settings,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";


const API_BASE_URL = 
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const DATA_SOURCE =
  import.meta.env.VITE_COST_DATA_PROVIDER || "mock";


function formatCurrency(value) {
  return `$${Number(value || 0).toFixed(2)}`;
}


function formatPercentage(value) {
  const number = Number(value || 0);

  if (number > 0) {
    return `+${number.toFixed(1)}%`;
  }

  return `${number.toFixed(1)}%`;
}


function App() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  const [activePage, setActivePage] = useState(
    "dashboard"
  );

  const [question, setQuestion] = useState(
    "Why did my AWS cost increase?"
  );

  const [aiResult, setAiResult] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);


  async function loadDashboard() {
    try {
      setError(null);

      const response = await fetch(
        `${API_BASE_URL}/costs/dashboard`
      );

      if (!response.ok) {
        throw new Error(
          `Backend returned ${response.status}`
        );
      }

      const data = await response.json();

      setDashboard(data);
    } catch (err) {
      setError(
        err.message ||
          "Unable to connect to the backend."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }


  async function runAIAnalysis() {
  if (!question.trim()) {
    return;
  }

  try {
    setAiLoading(true);
    setAiResult(null);

    const response = await fetch(
      `${API_BASE_URL}/ai/analyze`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question.trim(),
        }),
      }
    );

    if (!response.ok) {
      throw new Error(
        `AI analysis failed with status ${response.status}`
      );
    }

    const data = await response.json();

    setAiResult({
    ...data,
    ...data.structured_analysis,
    });
  } catch (err) {
    setAiResult({
      provider: "error",
      question: question.trim(),
      summary:
        err.message ||
        "Unable to run AI analysis.",
      findings: [],
      recommendations: [],
      risk_level: "unknown",
    });
  } finally {
    setAiLoading(false);
  }
}


  useEffect(() => {
    loadDashboard();
  }, []);


  function navigate(page) {
    setActivePage(page);
  }


  function handleRefresh() {
    setRefreshing(true);
    loadDashboard();
  }


  if (loading) {
    return (
      <div className="app-loading">
        <div className="loading-spinner" />
        <p>Loading AWS cost intelligence...</p>
      </div>
    );
  }


  if (error && !dashboard) {
    return (
      <div className="app-error">

        <div className="error-icon">
          <AlertTriangle size={28} />
        </div>

        <h1>
          Unable to load dashboard
        </h1>

        <p>{error}</p>


        <button
          className="refresh-button"
          onClick={loadDashboard}
        >
          <RefreshCw size={16} />
          Retry
        </button>

      </div>
    );
  }


  const summary = dashboard?.summary || {};

  const currentCost =
    summary.total_current_cost || 0;

  const previousCost =
    summary.total_previous_cost || 0;

  const changePercentage =
    summary.change_percentage || 0;

  const topService =
    summary.top_service;

  const topServiceByIncrease =
    summary.top_service_by_increase;

  const topServiceByCostIncrease =
    summary.top_service_by_cost_increase;

  const serviceData =
    dashboard?.service_breakdown || [];

  const anomalies =
    dashboard?.anomalies || [];

  const spikes =
    dashboard?.spikes || [];

  const dailyCosts =
    dashboard?.daily_costs || [];


  function renderDashboard() {
  return (
    <>
      <header className="topbar">

        <div>
          <p className="eyebrow">
            OVERVIEW
          </p>

          <h1>
            Cost Intelligence Dashboard
          </h1>

          <p className="page-description">
            Monitor AWS spending, detect anomalies,
            and investigate cost changes.
          </p>
        </div>

        <div>
          <span className="confidence-badge">
            {DATA_SOURCE === "aws"
              ? "🔵 AWS Cost Explorer"
              : "🟢 Demo / Mock"}
          </span>

          <button
            className="refresh-button"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw
              size={16}
              className={
                refreshing
                  ? "spinning"
                  : ""
              }
            />

            {refreshing
              ? "Refreshing..."
              : "Refresh"}
          </button>
        </div>

      </header>


      <section className="metric-grid">

        <div
          className="metric-card clickable-card"
          onClick={() =>
            navigate("analysis")
          }
        >

          <div className="metric-card-header">
            <span>
              Current Cost
            </span>

            <div className="metric-icon">
              <DollarSign size={18} />
            </div>
          </div>

          <div className="metric-value">
            {formatCurrency(currentCost)}
          </div>

          <div className="metric-meta">
            Current billing period
          </div>

        </div>


        <div
          className="metric-card clickable-card"
          onClick={() =>
            navigate("analysis")
          }
        >

          <div className="metric-card-header">
            <span>
              Previous Cost
            </span>

            <div className="metric-icon">
              <BarChart3 size={18} />
            </div>
          </div>

          <div className="metric-value">
            {formatCurrency(previousCost)}
          </div>

          <div className="metric-meta">
            Previous billing period
          </div>

        </div>


        <div
          className="metric-card clickable-card"
          onClick={() =>
            navigate("analysis")
          }
        >

          <div className="metric-card-header">
            <span>
              Top Service
            </span>

            <div className="metric-icon">
              <TrendingUp size={18} />
            </div>
          </div>

          <div className="metric-value metric-value-small">
            {topService
              ? topService.service
              : "None"}
          </div>

          <div className="metric-meta">
            {topService
              ? formatCurrency(
                  topService.cost
                )
              : "$0.00"}
          </div>

        </div>


        <div
          className="metric-card clickable-card"
          onClick={() =>
            navigate("anomalies")
          }
        >

          <div className="metric-card-header">
            <span>
              Anomalies
            </span>

            <div className="metric-icon warning">
              <AlertTriangle size={18} />
            </div>
          </div>

          <div className="metric-value">
            {anomalies.length}
          </div>

          <div className="metric-meta">
            Detected cost anomalies
          </div>

        </div>

      </section>


      <section className="dashboard-grid">

        <div className="panel">

          <div className="panel-header">

            <div>
              <p className="panel-label">
                SERVICE SPENDING
              </p>

              <h2>
                Current AWS costs
              </h2>
            </div>

            <button
              className="panel-link"
              onClick={() =>
                navigate("analysis")
              }
            >
              View analysis
              <ChevronRight size={15} />
            </button>

          </div>


          <div className="service-list">

            {serviceData.map(
              (item) => {

                const width =
                  currentCost > 0
                    ? (
                        item.cost /
                        currentCost
                      ) * 100
                    : 0;

                return (
                  <div
                    className="service-row clickable-service"
                    key={item.service}
                    onClick={() =>
                      navigate("analysis")
                    }
                  >

                    <div className="service-bar-info">

                      <span>
                        {item.service}
                      </span>

                      <strong>
                        {formatCurrency(
                          item.cost
                        )}
                      </strong>

                    </div>

                    <div className="service-bar-track">

                      <div
                        className="service-bar-fill"
                        style={{
                          width: `${Math.min(
                            width,
                            100
                          )}%`,
                        }}
                      />

                    </div>

                  </div>
                );
              }
            )}

          </div>

        </div>


        <div className="panel">

          <div className="panel-header">

            <div>
              <p className="panel-label">
                INTELLIGENCE
              </p>

              <h2>
                Cost signals
              </h2>
            </div>

            <Activity size={20} />

          </div>


          <div className="intelligence-list">

            <div
              className="intelligence-item clickable-item"
              onClick={() =>
                navigate("analysis")
              }
            >

              <div className="intelligence-icon">
                <TrendingUp size={17} />
              </div>

              <div>
                <span>
                  Overall spending
                </span>

                <strong>
                  {formatPercentage(
                    changePercentage
                  )}
                </strong>

                <p>
                  Compared with previous period
                </p>
              </div>

            </div>


            <div
              className="intelligence-item clickable-item"
              onClick={() =>
                navigate("analysis")
              }
            >

              <div className="intelligence-icon">
                <DollarSign size={17} />
              </div>

              <div>
                <span>
                  Largest absolute increase
                </span>

                <strong>
                  {topServiceByCostIncrease
                    ? `+${formatCurrency(
                        topServiceByCostIncrease.increase
                      )}`
                    : "$0.00"}
                </strong>

                <p>
                  {topServiceByCostIncrease
                    ? topServiceByCostIncrease.service
                    : "No increase detected"}
                </p>
              </div>

            </div>


            <div
              className="intelligence-item clickable-item"
              onClick={() =>
                navigate("analysis")
              }
            >

              <div className="intelligence-icon">
                <Activity size={17} />
              </div>

              <div>
                <span>
                  Largest percentage increase
                </span>

                <strong>
                  {topServiceByIncrease
                    ? formatPercentage(
                        topServiceByIncrease.change_percentage
                      )
                    : "0.0%"}
                </strong>

                <p>
                  {topServiceByIncrease
                    ? topServiceByIncrease.service
                    : "No increase detected"}
                </p>
              </div>

            </div>


            <div
              className="intelligence-item clickable-item"
              onClick={() =>
                navigate("anomalies")
              }
            >

              <div className="intelligence-icon warning">
                <AlertTriangle size={17} />
              </div>

              <div>
                <span>
                  Daily cost spikes
                </span>

                <strong>
                  {spikes.length}
                </strong>

                <p>
                  Unusual daily spending detected
                </p>
              </div>

            </div>

          </div>

        </div>

      </section>


      <section className="panel">

        <div className="panel-header">

          <div>
            <p className="panel-label">
              DAILY ACTIVITY
            </p>

            <h2>
              Recent cost spikes
            </h2>
          </div>

          <button
            className="panel-link"
            onClick={() =>
              navigate("anomalies")
            }
          >
            View anomalies
            <ChevronRight size={15} />
          </button>

        </div>


        {spikes.length === 0 ? (

          <div className="empty-state">
            <Activity size={26} />

            <p>
              No unusual daily cost spikes detected.
            </p>
          </div>

        ) : (

          <div className="spike-list">

            {spikes.map(
              (spike) => (
                <div
                  className="spike-item clickable-item"
                  key={spike.date}
                  onClick={() =>
                    navigate("anomalies")
                  }
                >

                  <div>
                    <strong>
                      {spike.date}
                    </strong>

                    <span>
                      Average daily cost:{" "}
                      {formatCurrency(
                        spike.average_cost
                      )}
                    </span>
                  </div>

                  <div className="spike-value">
                    <strong>
                      {formatCurrency(
                        spike.cost
                      )}
                    </strong>

                    <span>
                      +{spike.increase_percentage.toFixed(
                        1
                      )}%
                    </span>
                  </div>

                </div>
              )
            )}

          </div>

        )}

      </section>
    </>
  );
}


  function renderCostAnalysis() {
    const maximumDailyCost =
      dailyCosts.length
        ? Math.max(
            ...dailyCosts.map(
              (item) =>
                Number(item.cost || 0)
            )
          )
        : 0;


    const averageDailyCost =
      dailyCosts.length
        ? dailyCosts.reduce(
            (total, item) =>
              total +
              Number(item.cost || 0),
            0
          ) / dailyCosts.length
        : 0;


    return (
      <>
        <header className="topbar">

          <div>
            <p className="eyebrow">
              COST ANALYSIS
            </p>

            <h1>
              AWS Cost Analysis
            </h1>

            <p className="page-description">
              Compare service spending and identify
              unusual daily cost movements.
            </p>
          </div>

          <button
            className="refresh-button"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw
              size={16}
              className={
                refreshing
                  ? "spinning"
                  : ""
              }
            />

            {refreshing
              ? "Refreshing..."
              : "Refresh"}
          </button>

        </header>


        <section className="metric-grid">

          <div className="metric-card">

            <div className="metric-card-header">
              <span>
                Current Period
              </span>

              <div className="metric-icon">
                <DollarSign size={18} />
              </div>
            </div>

            <div className="metric-value">
              {formatCurrency(currentCost)}
            </div>

            <div className="metric-meta">
              Total AWS spending
            </div>

          </div>


          <div className="metric-card">

            <div className="metric-card-header">
              <span>
                Daily Average
              </span>

              <div className="metric-icon">
                <Activity size={18} />
              </div>
            </div>

            <div className="metric-value">
              {formatCurrency(
                averageDailyCost
              )}
            </div>

            <div className="metric-meta">
              Average daily spending
            </div>

          </div>


          <div className="metric-card">

            <div className="metric-card-header">
              <span>
                Highest Day
              </span>

              <div className="metric-icon warning">
                <TrendingUp size={18} />
              </div>
            </div>

            <div className="metric-value">
              {formatCurrency(
                maximumDailyCost
              )}
            </div>

            <div className="metric-meta">
              Highest observed daily cost
            </div>

          </div>


          <div className="metric-card">

            <div className="metric-card-header">
              <span>
                Period Change
              </span>

              <div className="metric-icon">
                <BarChart3 size={18} />
              </div>
            </div>

            <div className="metric-value">
              {formatPercentage(
                changePercentage
              )}
            </div>

            <div className="metric-meta">
              Compared with previous period
            </div>

          </div>

        </section>


        <section className="panel">

          <div className="panel-header">

            <div>
              <p className="panel-label">
                DAILY COST TREND
              </p>

              <h2>
                AWS spending by day
              </h2>
            </div>

            <Activity size={20} />

          </div>


          {dailyCosts.length === 0 ? (

            <div className="empty-state">
              <Activity size={28} />

              <p>
                No daily cost data available.
              </p>
            </div>

          ) : (

            <div className="daily-chart">

              {dailyCosts.map(
                (item) => {

                  const cost =
                    Number(item.cost || 0);

                  const height =
                    maximumDailyCost > 0
                      ? (
                          cost /
                          maximumDailyCost
                        ) * 100
                      : 0;

                  const isSpike =
                    spikes.some(
                      (spike) =>
                        spike.date ===
                        item.date
                    );


                  return (
                    <div
                      className="daily-bar-column"
                      key={item.date}
                      title={`${item.date}: ${formatCurrency(
                        cost
                      )}`}
                    >

                      <div className="daily-bar-value">
                        {formatCurrency(cost)}
                      </div>

                      <div className="daily-bar-track">

                        <div
                          className={`daily-bar-fill ${
                            isSpike
                              ? "daily-bar-spike"
                              : ""
                          }`}
                          style={{
                            height: `${Math.max(
                              height,
                              4
                            )}%`,
                          }}
                        />

                      </div>

                      <div className="daily-bar-date">
                        {item.date.slice(8)}
                      </div>

                    </div>
                  );
                }
              )}

            </div>

          )}

        </section>


        <section className="panel table-panel">

          <div className="panel-header">

            <div>
              <p className="panel-label">
                SERVICE COMPARISON
              </p>

              <h2>
                Current vs previous spending
              </h2>
            </div>

            <span className="table-count">
              {serviceData.length} services
            </span>

          </div>


          <div className="table-wrapper">

            <table>

              <thead>

                <tr>
                  <th>
                    Service
                  </th>

                  <th>
                    Current
                  </th>

                  <th>
                    Previous
                  </th>

                  <th>
                    Absolute Change
                  </th>

                  <th>
                    Percentage
                  </th>
                </tr>

              </thead>


              <tbody>

                {serviceData.map(
                  (item) => {

                    const difference =
                      item.cost -
                      item.previous_cost;


                    return (
                      <tr
                        key={item.service}
                        className="clickable-row"
                      >

                        <td>
                          <div className="service-name">

                            <span className="service-dot" />

                            {item.service}

                          </div>
                        </td>


                        <td>
                          {formatCurrency(
                            item.cost
                          )}
                        </td>


                        <td>
                          {formatCurrency(
                            item.previous_cost
                          )}
                        </td>


                        <td>
                          {difference >= 0
                            ? `+${formatCurrency(
                                difference
                              )}`
                            : formatCurrency(
                                difference
                              )}
                        </td>


                        <td>

                          <span
                            className={
                              item.change_percentage >
                              0
                                ? "change-positive"
                                : "change-neutral"
                            }
                          >
                            {formatPercentage(
                              item.change_percentage
                            )}
                          </span>

                        </td>

                      </tr>
                    );
                  }
                )}

              </tbody>

            </table>

          </div>

        </section>
      </>
    );
  }


  function renderAnomalies() {
    return (
      <>
        <header className="topbar">

          <div>
            <p className="eyebrow">
              ANOMALY DETECTION
            </p>

            <h1>
              Cost Anomalies
            </h1>

            <p className="page-description">
              Investigate services and daily spending
              that moved beyond expected thresholds.
            </p>
          </div>

          <button
            className="refresh-button"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw size={16} />
            Refresh
          </button>

        </header>


        <section className="metric-grid">

          <div className="metric-card">

            <div className="metric-card-header">
              <span>
                Service Anomalies
              </span>

              <div className="metric-icon warning">
                <AlertTriangle size={18} />
              </div>
            </div>

            <div className="metric-value">
              {anomalies.length}
            </div>

            <div className="metric-meta">
              Services above threshold
            </div>

          </div>


          <div className="metric-card">

            <div className="metric-card-header">
              <span>
                Daily Spikes
              </span>

              <div className="metric-icon warning">
                <TrendingUp size={18} />
              </div>
            </div>

            <div className="metric-value">
              {spikes.length}
            </div>

            <div className="metric-meta">
              Unusual daily movements
            </div>

          </div>

        </section>


        <section className="panel">

          <div className="panel-header">

            <div>
              <p className="panel-label">
                SERVICE ANOMALIES
              </p>

              <h2>
                Services requiring investigation
              </h2>
            </div>

            <AlertTriangle size={20} />

          </div>


          {anomalies.length === 0 ? (

            <div className="empty-state">
              <ShieldCheck size={28} />

              <p>
                No service anomalies detected.
              </p>
            </div>

          ) : (

            <div className="anomaly-list">

              {anomalies.map(
                (item) => (
                  <div
                    className="anomaly-card clickable-item"
                    key={item.service}
                  >

                    <div className="anomaly-card-main">

                      <div className="anomaly-icon">
                        <AlertTriangle size={18} />
                      </div>

                      <div>

                        <strong>
                          {item.service}
                        </strong>

                        <p>
                          Current:{" "}
                          {formatCurrency(
                            item.cost
                          )}{" "}
                          · Previous:{" "}
                          {formatCurrency(
                            item.previous_cost
                          )}
                        </p>

                      </div>

                    </div>


                    <div className="anomaly-change">
                      {formatPercentage(
                        item.change_percentage
                      )}
                    </div>

                  </div>
                )
              )}

            </div>

          )}

        </section>


        <section className="panel">

          <div className="panel-header">

            <div>
              <p className="panel-label">
                DAILY SPIKES
              </p>

              <h2>
                Unusual daily spending
              </h2>
            </div>

            <Activity size={20} />

          </div>


          {spikes.length === 0 ? (

            <div className="empty-state">
              <ShieldCheck size={28} />

              <p>
                No unusual daily spikes detected.
              </p>
            </div>

          ) : (

            <div className="spike-list">

              {spikes.map(
                (spike) => (
                  <div
                    className="spike-item"
                    key={spike.date}
                  >

                    <div>
                      <strong>
                        {spike.date}
                      </strong>

                      <span>
                        Average:{" "}
                        {formatCurrency(
                          spike.average_cost
                        )}
                      </span>
                    </div>

                    <div className="spike-value">

                      <strong>
                        {formatCurrency(
                          spike.cost
                        )}
                      </strong>

                      <span>
                        +
                        {spike.increase_percentage.toFixed(
                          1
                        )}
                        %
                      </span>

                    </div>

                  </div>
                )
              )}

            </div>

          )}

        </section>
      </>
    );
  }


 function renderAIInvestigation() {
  const analysis = aiResult;

  return (
    <>
      <header className="topbar">
        <div>
          <p className="eyebrow">
            AI INVESTIGATION
          </p>

          <h1>
            Investigate AWS Costs
          </h1>

          <p className="page-description">
            Ask questions about your AWS spending
            and receive structured analysis.
          </p>
        </div>

        <div className="ai-header-icon">
          <Bot size={22} />
        </div>
      </header>

      <section className="panel ai-panel">
        <div className="panel-header">
          <div>
            <p className="panel-label">
              COST INVESTIGATION
            </p>

            <h2>
              Ask the cost detective
            </h2>
          </div>

          <Bot size={20} />
        </div>

        <div className="ai-input-area">
          <textarea
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            placeholder="Ask a question about your AWS costs..."
            rows={4}
          />

          <button
            className="primary-button"
            onClick={runAIAnalysis}
            disabled={aiLoading}
          >
            <Bot size={16} />

            {aiLoading
              ? "Investigating..."
              : "Investigate"}
          </button>
        </div>
      </section>

      {analysis && (
        <section className="panel ai-results">
          <div className="panel-header">
            <div>
              <p className="panel-label">
                AI ANALYSIS
              </p>

              <h2>
                Investigation result
              </h2>
            </div>

            <span className="confidence-badge">
              {analysis.risk_level} risk
            </span>
          </div>

          <div className="ai-result-section">
            <h3>
              Summary
            </h3>

            <p>
              {analysis.summary}
            </p>
          </div>

          <div className="ai-result-section">
            <h3>
              Findings
            </h3>

            {analysis.findings?.length ? (
              <div className="ai-driver-list">
                {analysis.findings.map(
                  (finding, index) => (
                    <div
                      className="ai-driver"
                      key={`${finding.service}-${index}`}
                    >
                      <strong>
                        {finding.service}
                      </strong>

                      <span>
                        {finding.change_percentage !==
                        null
                          ? formatPercentage(
                              finding.change_percentage
                            )
                          : "No percentage change"}
                      </span>

                      <p>
                        {finding.issue}
                      </p>

                      <p>
                        {finding.evidence}
                      </p>
                    </div>
                  )
                )}
              </div>
            ) : (
              <p className="muted-text">
                No specific cost findings identified.
              </p>
            )}
          </div>

          <div className="ai-result-section">
            <h3>
              Recommended actions
            </h3>

            {analysis.recommendations?.length ? (
              <div className="recommendation-list">
                {analysis.recommendations.map(
                  (recommendation, index) => (
                    <div
                      className="recommendation-item"
                      key={index}
                    >
                      <strong>
                        {recommendation.action}
                      </strong>

                      <p>
                        {recommendation.reason}
                      </p>

                      <p>
                        Estimated savings:{" "}
                        {recommendation.estimated_savings}
                      </p>

                      <p>
                        Confidence:{" "}
                        {recommendation.confidence}
                      </p>
                    </div>
                  )
                )}
              </div>
            ) : (
              <p className="muted-text">
                No recommendations available.
              </p>
            )}
          </div>

          <div className="ai-result-section">
            <h3>
              Investigation details
            </h3>

            <div className="savings-card">
              <strong>
                {analysis.provider}
              </strong>

              <p>
                Analysis provider
              </p>
            </div>
          </div>
        </section>
      )}
    </>
  );
}


  function renderSecurity() {
    return (
      <>
        <header className="topbar">

          <div>
            <p className="eyebrow">
              SECURITY
            </p>

            <h1>
              Security & Access
            </h1>

            <p className="page-description">
              Review the security principles used by
              the cost intelligence platform.
            </p>
          </div>

          <ShieldCheck size={24} />

        </header>


        <section className="security-grid">

          <div className="panel">

            <div className="security-icon">
              <Lock size={22} />
            </div>

            <h2>
              Least-privilege IAM
            </h2>

            <p>
              The application is designed to use a
              dedicated AWS identity with read-only
              Cost Explorer permissions for cost
              analysis.
            </p>

          </div>


          <div className="panel">

            <div className="security-icon">
              <ShieldCheck size={22} />
            </div>

            <h2>
              Read-only cost access
            </h2>

            <p>
              Cost investigation does not require
              permission to modify AWS resources.
              Recommendations are presented for
              user approval rather than executed
              automatically.
            </p>

          </div>


          <div className="panel">

            <div className="security-icon">
              <Bot size={22} />
            </div>

            <h2>
              Controlled AI input
            </h2>

            <p>
              The AI layer receives structured cost
              investigation data instead of broad
              AWS account access.
            </p>

          </div>


          <div className="panel">

            <div className="security-icon">
              <Settings size={22} />
            </div>

            <h2>
              Configuration separation
            </h2>

            <p>
              AI provider and cost data provider
              configuration are controlled through
              environment variables.
            </p>

          </div>

        </section>
      </>
    );
  }


  function renderSettings() {
    return (
      <>
        <header className="topbar">

          <div>
            <p className="eyebrow">
              SETTINGS
            </p>

            <h1>
              Platform Settings
            </h1>

            <p className="page-description">
              Current application configuration and
              provider information.
            </p>
          </div>

          <Settings size={24} />

        </header>


        <section className="panel settings-panel">

          <div className="setting-row">

            <div>
              <span>
                Cost data provider
              </span>

              <p>
                Source used for AWS cost information.
              </p>
            </div>

            <strong>
              Mock / AWS
            </strong>

          </div>


          <div className="setting-row">

            <div>
              <span>
                AI provider
              </span>

              <p>
                Provider responsible for cost
                investigation responses.
              </p>
            </div>

            <strong>
              Mock
            </strong>

          </div>


          <div className="setting-row">

            <div>
              <span>
                AWS Region
              </span>

              <p>
                Default AWS region configured for
                the application.
              </p>
            </div>

            <strong>
              eu-north-1
            </strong>

          </div>


          <div className="setting-row">

            <div>
              <span>
                API status
              </span>

              <p>
                Current FastAPI backend connection.
              </p>
            </div>

            <strong className="status-online">
              Online
            </strong>

          </div>

        </section>
      </>
    );
  }


  function renderPage() {
    switch (activePage) {

      case "analysis":
        return renderCostAnalysis();

      case "anomalies":
        return renderAnomalies();

      case "ai":
        return renderAIInvestigation();

      case "security":
        return renderSecurity();

      case "settings":
        return renderSettings();

      case "dashboard":
      default:
        return renderDashboard();
    }
  }


  return (
    <div className="app-shell">


      <aside className="sidebar">

        <div className="brand">

          <div className="brand-mark">
            <Activity size={21} />
          </div>

          <div>
            <strong>
              Cost Detective
            </strong>

            <span>
              AWS FinOps
            </span>
          </div>

        </div>


        <nav className="sidebar-nav">

          <button
            className={`nav-item ${
              activePage === "dashboard"
                ? "active"
                : ""
            }`}
            onClick={() =>
              navigate("dashboard")
            }
          >
            <LayoutDashboard size={18} />

            <span>
              Dashboard
            </span>
          </button>


          <button
            className={`nav-item ${
              activePage === "analysis"
                ? "active"
                : ""
            }`}
            onClick={() =>
              navigate("analysis")
            }
          >
            <BarChart3 size={18} />

            <span>
              Cost Analysis
            </span>
          </button>


          <button
            className={`nav-item ${
              activePage === "anomalies"
                ? "active"
                : ""
            }`}
            onClick={() =>
              navigate("anomalies")
            }
          >
            <AlertTriangle size={18} />

            <span>
              Anomalies
            </span>

            {anomalies.length > 0 && (
              <span className="nav-badge">
                {anomalies.length}
              </span>
            )}
          </button>


          <button
            className={`nav-item ${
              activePage === "ai"
                ? "active"
                : ""
            }`}
            onClick={() =>
              navigate("ai")
            }
          >
            <Bot size={18} />

            <span>
              AI Investigation
            </span>
          </button>


          <div className="nav-divider" />


          <button
            className={`nav-item ${
              activePage === "security"
                ? "active"
                : ""
            }`}
            onClick={() =>
              navigate("security")
            }
          >
            <ShieldCheck size={18} />

            <span>
              Security
            </span>
          </button>


          <button
            className={`nav-item ${
              activePage === "settings"
                ? "active"
                : ""
            }`}
            onClick={() =>
              navigate("settings")
            }
          >
            <Settings size={18} />

            <span>
              Settings
            </span>
          </button>

        </nav>


        <div className="sidebar-footer">

          <div className="status-indicator">
            <span className="status-dot" />

            <span>
              API Connected
            </span>
          </div>

          <span className="version">
            v0.1.0
          </span>

        </div>

      </aside>


      <main className="main-content">

        {renderPage()}

      </main>

    </div>
  );
}


export default App;

