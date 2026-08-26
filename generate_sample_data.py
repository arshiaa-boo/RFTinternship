"""
generate_sample_data.py
------------------------
Creates a sample weather_data.csv file so the analysis script has
something to work with out of the box. If you already have your own
CSV (with columns: date, city, temperature, condition), just skip this
and point weather_analysis.py at your file instead.
"""

import numpy as np
import pandas as pd

np.random.seed(42)

cities = {
    "Delhi": 32,
    "Mumbai": 29,
    "Bangalore": 24,
    "Chennai": 33,
    "Kolkata": 30,
}

conditions = ["Sunny", "Rainy", "Cloudy", "Sunny", "Sunny", "Rainy", "Cloudy"]

dates = pd.date_range(start="2024-01-01", periods=30, freq="D")

rows = []
for city, base_temp in cities.items():
    # give each city a slightly different trend + daily noise
    trend = np.linspace(0, np.random.uniform(-2, 3), len(dates))
    noise = np.random.normal(0, 1.5, len(dates))
    temps = base_temp + trend + noise

    for date, temp in zip(dates, temps):
        rows.append({
            "date": date.strftime("%Y-%m-%d"),
            "city": city,
            "temperature": round(temp, 1),
            "condition": np.random.choice(conditions),
        })

df = pd.DataFrame(rows)
df.to_csv("weather_data.csv", index=False)
print(f"Sample dataset created: weather_data.csv ({len(df)} rows)")
