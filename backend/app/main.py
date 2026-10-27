import httpx
from fastapi import FastAPI


from app.services.analysis import build_january_analysis

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Wind Intelligence API",
    description="UK wind generation forecast and accuracy analysis",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "https://wind-intelligence-khaki.vercel.app",
],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok"}


from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from app.services.elexon import (
    fetch_wind_actuals,
    fetch_wind_forecasts,
)


@app.get("/api/debug/elexon")
async def test_elexon():
    # A small, recent window to test connectivity and response shape.
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=6)

    publish_from = start.isoformat()
    publish_to = end.isoformat()

    try:
        actuals = await fetch_wind_actuals(publish_from, publish_to)
        forecasts = await fetch_wind_forecasts(
            publish_from, publish_to
        )

        # return {
        #     "actual_count": len(actuals),
        #     "forecast_count": len(forecasts),
        #     "actual_sample": actuals[:3],
        #     "forecast_sample": forecasts[:3],
        # }
        return {
            "actual_count": len(actuals),
            "forecast_count": len(forecasts),
            "actual_fields": list(actuals[0].keys()) if actuals else [],
            "forecast_fields": list(forecasts[0].keys()) if forecasts else [],
            "actual_sample": actuals[:2],
            "forecast_sample": forecasts[:2],
        }
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Elexon API request failed: {exc}",
        )


@app.get("/api/analysis/january-2026")
async def january_analysis():
    try:
        return await build_january_analysis()
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=str(exc))