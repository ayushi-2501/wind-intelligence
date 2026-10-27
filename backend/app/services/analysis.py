
from datetime import datetime, timedelta, timezone

import pandas as pd

from app.services.elexon import (
    fetch_wind_actuals,
    fetch_wind_forecasts,
)

UTC = timezone.utc


async def build_january_analysis():
    delivery_start = pd.Timestamp("2026-01-01T00:00:00Z")
    delivery_end = pd.Timestamp("2026-02-01T00:00:00Z")

    publish_from = "2025-12-31T00:00:00Z"
    publish_to = "2026-02-02T00:00:00Z"

    actual_records = await fetch_wind_actuals(
        publish_from, publish_to
    )
    forecast_records = await fetch_wind_forecasts(
        publish_from, publish_to
    )

    actuals = pd.DataFrame(actual_records)
    forecasts = pd.DataFrame(forecast_records)

    if actuals.empty or forecasts.empty:
        raise ValueError("Elexon returned no actual or forecast records.")

    for frame, columns in [
        (actuals, ["startTime", "publishTime"]),
        (forecasts, ["startTime", "publishTime"]),
    ]:
        for column in columns:
            frame[column] = pd.to_datetime(
                frame[column], utc=True, errors="coerce"
            )

        frame["generation"] = pd.to_numeric(
            frame["generation"], errors="coerce"
        )

        frame.dropna(
            subset=["startTime", "publishTime", "generation"],
            inplace=True,
        )

    actuals = actuals[
        (actuals["startTime"] >= delivery_start)
        & (actuals["startTime"] < delivery_end)
        & (actuals["fuelType"] == "WIND")
    ].copy()

    forecasts = forecasts[
        (forecasts["startTime"] >= delivery_start)
        & (forecasts["startTime"] < delivery_end)
    ].copy()

    actuals = (
        actuals.sort_values("publishTime")
        .drop_duplicates("startTime", keep="last")
    )

    actuals["hour"] = actuals["startTime"].dt.floor("h")

    actual_hourly = (
        actuals.groupby("hour")["generation"]
        .agg(actual_mw="mean", actual_intervals="count")
        .reset_index()
    )

    actual_hourly = actual_hourly[
        actual_hourly["actual_intervals"] == 2
    ].copy()

    forecasts["cutoff"] = (
        forecasts["startTime"].dt.normalize()
        - pd.Timedelta(days=1)
        + pd.Timedelta(hours=10)
    )

    eligible = forecasts[
        forecasts["publishTime"] <= forecasts["cutoff"]
    ].copy()

    selected = (
        eligible.sort_values("publishTime")
        .drop_duplicates("startTime", keep="last")
        .rename(columns={"generation": "forecast_mw"})
    )

    comparison = actual_hourly.merge(
        selected[["startTime", "publishTime", "forecast_mw"]],
        left_on="hour",
        right_on="startTime",
        how="inner",
    )

    if comparison.empty:
        raise ValueError(
            "No matched forecast/actual intervals. "
            "Check publication history, time resolution and cutoff."
        )

    comparison["error_mw"] = (
        comparison["forecast_mw"] - comparison["actual_mw"]
    )
    comparison["absolute_error_mw"] = comparison["error_mw"].abs()
    comparison["squared_error"] = comparison["error_mw"] ** 2

    summary = {
        "period": "January 2026",
        "decision_cutoff": "10:00 UTC on the previous day",
        "forecast_resolution": "Hourly",
        "actual_resolution": "Hourly mean of two half-hour intervals",
        "matched_hours": int(len(comparison)),
        "mae_mw": round(
            float(comparison["absolute_error_mw"].mean()), 2
        ),
        "rmse_mw": round(
            float(comparison["squared_error"].mean() ** 0.5), 2
        ),
        "bias_mw": round(float(comparison["error_mw"].mean()), 2),
    }

    comparison = comparison.sort_values("hour")

    series = [
        {
            "time": row.hour.isoformat(),
            "forecast_mw": round(float(row.forecast_mw), 2),
            "actual_mw": round(float(row.actual_mw), 2),
            "error_mw": round(float(row.error_mw), 2),
            "forecast_published_at": row.publishTime.isoformat(),
        }
        for row in comparison.itertuples()
    ]

    return {
        "summary": summary,
        "series": series,
        "data_quality": {
            "actual_half_hour_records": int(len(actuals)),
            "complete_actual_hours": int(len(actual_hourly)),
            "forecast_records_in_delivery_period": int(len(forecasts)),
            "eligible_forecast_records": int(len(eligible)),
            "matched_hours": int(len(comparison)),
        },
    }
