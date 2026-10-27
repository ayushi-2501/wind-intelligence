
## Methodology and assumptions

- **Analysis period:** 1–31 January 2026.
- **Forecast source:** Elexon WINDFOR dataset.
- **Actual generation source:** Elexon FUELHH dataset, filtered to WIND.
- **Forecast cutoff:** The latest forecast published by 10:00 UTC on the preceding day is selected for each delivery hour. This is an evaluation assumption, not a verified operational purchasing deadline.
- **Actual generation alignment:** The two half-hourly actual records are averaged to obtain hourly actual generation. Hours without both half-hourly records are excluded.
- **Evaluation metrics:**
  - MAE: Mean Absolute Error.
  - RMSE: Root Mean Squared Error, which penalises larger errors more heavily.
  - Bias: Mean forecast minus actual generation. Positive bias indicates overforecasting on average.

The results should be interpreted in the context of these assumptions.
