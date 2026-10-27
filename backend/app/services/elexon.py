
import httpx

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets"


async def fetch_dataset(
    dataset: str,
    publish_from: str,
    publish_to: str,
    extra_params: dict | None = None,
):
    """Fetch records published during the requested time window."""
    params = {
        "publishDateTimeFrom": publish_from,
        "publishDateTimeTo": publish_to,
    }

    if extra_params:
        params.update(extra_params)

    url = f"{BASE_URL}/{dataset}/stream"

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    if isinstance(data, dict):
        data = data.get("data", [])

    if not isinstance(data, list):
        raise ValueError(f"Unexpected response format from {dataset}")

    return data


async def fetch_wind_actuals(publish_from: str, publish_to: str):
    records = await fetch_dataset(
        "FUELHH",
        publish_from,
        publish_to,
        extra_params={"fuelType": "WIND"},
    )

    return [
        row for row in records
        if row.get("fuelType") == "WIND"
    ]

async def fetch_wind_forecasts(publish_from: str, publish_to: str):
    records = await fetch_dataset(
        "WINDFOR",
        publish_from,
        publish_to,
    )

    return [
        {
            "startTime": row.get("startTime"),
            "publishTime": row.get("publishTime"),
            "generation": row.get("generation"),
        }
        for row in records
    ]
