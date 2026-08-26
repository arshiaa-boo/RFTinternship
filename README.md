# Weather Data Analysis Toolkit

## Files
- `generate_sample_data.py` — creates a sample `weather_data.csv` (5 cities, 30 days)
- `weather_analysis.py` — main script: reads CSV, computes stats, saves 3 charts + a text report
- `streamlit_dashboard.py` — bonus interactive dashboard
- `weather_data.csv` — sample dataset (already generated)
- `weather_report_output/` — sample output: charts (PNG) + report (TXT)

## How to run

1. Install dependencies:
   pip install pandas numpy matplotlib streamlit plotly

2. (Optional) Generate a fresh sample dataset:
   python generate_sample_data.py

3. Run the analysis (creates charts + report in weather_report_output/):
   python weather_analysis.py
   # or point it at your own CSV:
   python weather_analysis.py path/to/your_weather.csv

4. Launch the bonus interactive dashboard:
   streamlit run streamlit_dashboard.py

## Your own CSV format
Needs these columns (any order, case-insensitive):
date, city, temperature, condition

Example row: 2024-01-05,Delhi,28.4,Sunny
