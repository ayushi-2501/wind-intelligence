import { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import { getJanuaryAnalysis } from "./services/api";
import "./App.css";

function formatMW(value) {
  return `${Math.round(value).toLocaleString("en-GB")} MW`;
}

function MetricCard({ label, value, description }) {
  return (
    <div className="metric-card">
      <p className="metric-label">{label}</p>
      <h2>{value}</h2>
      <p className="metric-description">{description}</p>
    </div>
  );
}

export default function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getJanuaryAnalysis()
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
  return (
    <main className="page loading-page">
      <div className="loader-container">
        <div className="spinner"></div>
        <h2>Loading wind generation data</h2>
        <p>Fetching forecast and actual generation data…</p>
      </div>
    </main>
  );
}

  if (error) {
    return (
      <main className="page">
        <h1>Unable to load dashboard</h1>
        <p>{error}</p>
        <p>Check that the FastAPI backend is running on port 8000.</p>
      </main>
    );
  }

  const { summary, series, data_quality } = data;

  const chartData = series.map((point) => ({
    ...point,
    label: new Date(point.time).toLocaleString("en-GB", {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
      timeZone: "Europe/London",
    }),
  }));

  return (
    <main className="page">
      <header className="header">
        <div>
          <p className="eyebrow">ENERGY INTELLIGENCE</p>
          <h1>Wind Generation Monitor</h1>
          <p className="subtitle">
            Forecast performance against actual UK wind generation
          </p>
        </div>
        <div className="period-badge">January 2026</div>
      </header>

      <section className="metrics">
        <MetricCard
          label="Mean absolute error"
          value={formatMW(summary.mae_mw)}
          description="Average absolute forecast error"
        />
        <MetricCard
          label="Root mean squared error"
          value={formatMW(summary.rmse_mw)}
          description="Highlights larger misses"
        />
        <MetricCard
          label="Forecast bias"
          value={`${summary.bias_mw > 0 ? "+" : ""}${formatMW(summary.bias_mw)}`}
          description="Positive means overforecasting"
        />
        <MetricCard
          label="Matched intervals"
          value={`${summary.matched_hours}/744`}
          description="Hourly forecast and actual pairs"
        />
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Forecast vs actual generation</h2>
            <p>Hourly generation, MW · UK local time</p>
          </div>
          <span className="status">Historical analysis</span>
        </div>

        <div className="chart">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" minTickGap={45} tick={{ fontSize: 11 }} />
              <YAxis
                tickFormatter={(v) => `${Math.round(v / 1000)}k`}
                width={55}
              />
              <Tooltip
                formatter={(value) => formatMW(value)}
                labelFormatter={(label) => `Delivery: ${label}`}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="forecast_mw"
                name="Forecast"
                stroke="#2563eb"
                dot={false}
                strokeWidth={2}
              />
              <Line
                type="monotone"
                dataKey="actual_mw"
                name="Actual"
                stroke="#059669"
                dot={false}
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Forecast error details</h2>
            <p>Largest absolute errors first</p>
          </div>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Delivery time</th>
                <th>Forecast</th>
                <th>Actual</th>
                <th>Error</th>
              </tr>
            </thead>
            <tbody>
              {[...series]
                .sort((a, b) => Math.abs(b.error_mw) - Math.abs(a.error_mw))
                .slice(0, 15)
                .map((point) => (
                  <tr key={point.time}>
                    <td>
                      {new Date(point.time).toLocaleString("en-GB", {
                        day: "2-digit",
                        month: "short",
                        year: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                        hour12: false,
                        timeZone: "Europe/London",
                      })}
                    </td>
                    <td>{formatMW(point.forecast_mw)}</td>
                    <td>{formatMW(point.actual_mw)}</td>
                    <td
                      className={point.error_mw >= 0 ? "positive" : "negative"}
                    >
                      {point.error_mw > 0 ? "+" : ""}
                      {formatMW(point.error_mw)}
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </section>

      <footer>
        <p>Source: Elexon BMRS · {data_quality.matched_hours} matched hours</p>
        <p>
          Evaluation cutoff: {summary.decision_cutoff}. Forecast selection and
          cutoff assumptions should be validated before procurement use.
        </p>
        <br></br>
        <p>Methodology note: Day-ahead forecasts are selected using the latest forecast published by 10:00 UTC on the preceding day. This cutoff is a modelling assumption used for evaluation, not a confirmed operational purchasing deadline. Actual wind generation is calculated as the hourly mean of the two half-hourly actual records. Forecast accuracy metrics reflect this methodology.</p>
      </footer>
    </main>
  );
}
