# Wind Intelligence Dashboard

A data-driven dashboard for analysing day ahead wind generation forecasts against actual wind generation in Great Britain. The dashboard helps users understand forecast accuracy, identify periods with large deviations and assess the potential impact of forecast errors on energy purchasing decisions.

## Overview

Wind generation is variable, making accurate forecasting important for energy suppliers planning their electricity purchases. This project compares day ahead wind generation forecasts with actual generation using data from the Elexon BMRS API.

The dashboard focuses on January 2026 and presents forecast performance through summary metrics, a time-series chart, and a table of the largest forecast errors.

## Features

- **Forecast vs actual:** Compare hourly wind generation forecasts with actual generation.
- **Key performance metrics:** View Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and forecast bias.
- **Time-series visualisation:** Identify changes in forecast and actual generation throughout the month.
- **Largest forecast errors:** Inspect the 15 hours with the largest absolute forecast errors.
- **Data quality checks:** Track source records, complete hourly actuals, and matched forecast/actual observations.
- **Documented evaluation assumptions:** Make the forecast selection cutoff and hourly aggregation method explicit.

## Tech Stack

**Frontend**
- React
- Vite
- Recharts
- CSS

**Backend**
- Python
- FastAPI
- HTTPX
- Pandas

**Data source**
- Elexon BMRS API

## Data Source

The dashboard uses the Elexon BMRS API:

https://data.elexon.co.uk/bmrs/api/v1

The datasets used are:

- **WINDFOR:** Wind generation forecast data.
- **FUELHH:** Half-hourly generation data, filtered to records where `fuelType = WIND`.

The analysis covers 1–31 January 2026.

## Methodology

1. Retrieve wind forecast records from `WINDFOR` and actual generation records from `FUELHH`.
2. Filter actual generation to the wind fuel type.
3. Select the latest published actual record for each delivery interval.
4. Aggregate the two half-hourly actual generation records into an hourly average. Hours without both half-hourly records are excluded.
5. For each delivery hour, select the latest forecast published by **10:00 UTC on the preceding day**.
6. Match hourly forecasts with hourly actual generation and calculate forecast error metrics.

### Metrics

- **MAE (Mean Absolute Error):** Average absolute difference between forecast and actual generation. Lower is better.
- **RMSE (Root Mean Squared Error):** Square root of the mean squared error. Larger errors have a greater influence on this metric.
- **Bias:** Mean of forecast generation minus actual generation. A positive value indicates overforecasting on average; a negative value indicates underforecasting.

### Important assumption

The 10:00 UTC previous-day forecast cutoff is an evaluation assumption used for this analysis. It should not be interpreted as a verified operational purchasing deadline.

The results depend on the chosen cutoff, the hourly aggregation method and the completeness of the source data.

## Getting Started

### Prerequisites

- Python 3.10 or later
- Node.js compatible with the frontend dependencies
- npm

### 1. Clone the repository

```bash
git clone https://github.com/ayushi-2501/wind-intelligence.git
cd wind-intelligence
```

### 2. Run the backend

Open a terminal:

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Git Bash:**

```bash
source .venv/Scripts/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

Useful endpoints:

- Health check: `http://localhost:8000/api/health`
- January 2026 analysis: `http://localhost:8000/api/analysis/january-2026`
- Interactive API documentation: `http://localhost:8000/docs`

### 3. Run the frontend

Open a second terminal:

```bash
cd frontend
npm install
```

Create a `.env` file inside `frontend/` with:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Start the development server:

```bash
npm run dev
```

Open the local URL printed by Vite, usually `http://localhost:5173`.

Keep the backend running while using the dashboard.

## Project Structure

```text
wind-intelligence/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── services/
│   ├── tests/
│   ├── requirements.txt
│   └── .gitignore
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── .gitignore
├── README.md
└── gitignore
```

## Limitations

- Forecast accuracy is evaluated using a specific previous day publication cutoff.
- Incomplete half-hourly actual data can cause delivery hours to be excluded.
- Forecast errors alone do not quantify the actual financial cost of purchasing electricity that would require additional market price and purchasing data.
- Results represent the selected analysis period and should not automatically be generalised to other periods.

## Future Improvements

- Add selectable analysis periods.
- Compare forecast accuracy across days and weeks.
- Highlight underforecasting and overforecasting periods.
- Incorporate electricity market prices to estimate potential financial exposure.
- Add automated tests and data-refresh monitoring.

## License

This project was created as an assignment project. A license can be added if the repository is intended for reuse or distribution.
