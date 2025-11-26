# Liverpool City Region Housing Dashboard

A Streamlit-based data analytics dashboard for the Liverpool City Region housing pipeline. It visualises the messy CSV supplied for the hackathon, surfaces KPIs for the Mayor, and prototypes an AI-assisted data entry workflow.

## Features
- **Interactive filters:** Multi-select by area, developer, status, timeline, land type, numeric sliders for units and cost, plus free-text search.
- **Visual analytics:** KPI cards, homes built vs target (6,600), units by area/developer, completion timelines, and site-size distribution.
- **Raw data explorer:** Paginated, sortable table with CSV export of the filtered view.
- **AI input mock:** Google Forms-style text input with mocked “AI-powered summarisation” and mapping preview.
- **Data prep script:** Load and normalise the CSV, flatten headers, convert numerics, and derive helper fields such as estimated capacity.

## Quickstart
1. Create and activate a virtual environment (optional but recommended).
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```
2. Install dependencies.
   ```bash
   pip install -r requirements.txt
   ```
3. Run the dashboard.
   ```bash
   streamlit run app.py
   ```
4. Open the provided local URL in your browser to explore the dashboard.

## Environment variables
- `DATA_PATH` (optional): Override the CSV location. Defaults to `data/Copy of Housing_Pipeline_Long_List_External_Hackathon(Longlist).csv`.
- `DATA_ENCODING` (optional): Force a specific CSV encoding if auto-detection fails (tries utf-8, cp1252, latin1 by default).

## Data preparation
Use the helper script to generate a cleaned CSV for analysis or sharing:
```bash
python scripts/prepare_data.py --input data/Copy\ of\ Housing_Pipeline_Long_List_External_Hackathon\(Longlist\).csv --output data/cleaned_housing_pipeline.csv
```

## Project structure
- `app.py` — Streamlit UI with filters, analytics, raw explorer, and AI mock.
- `utils/data_loader.py` — CSV loading, column normalisation, numeric conversions, derived capacity field.
- `utils/analytics.py` — KPI and chart-ready aggregations with 6,600 target and 4,500 built baseline.
- `scripts/prepare_data.py` — CLI to clean and save the dataset.
- `data/` — Input CSV (supplied).

## Notes
- The AI workflow is intentionally mocked for demonstration (no external calls).
- Numeric conversions are best-effort; messy fields are coerced to sensible values where possible.
- Charts and filters dynamically respect the current dataset slice so stakeholders always see context-aware insights.
