"""
weather_analysis.py
"""
import warnings
warnings.filterwarnings("ignore")
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------------------
# 1. Load data
# ------------------------------------------------------------------
CSV_PATH = sys.argv[1] if len(sys.argv) > 1 else "weather_data.csv"

if not os.path.exists(CSV_PATH):
    print(f"Could not find '{CSV_PATH}'.")
    print("Run 'python generate_sample_data.py' first, or pass your own CSV path.")
    sys.exit(1)

df = pd.read_csv(CSV_PATH)

# normalize column names (lowercase, stripped)
df.columns = [c.strip().lower() for c in df.columns]

required = {"date", "city", "temperature", "condition"}
missing = required - set(df.columns)
if missing:
    print(f"CSV is missing required columns: {missing}")
    print(f"Found columns: {list(df.columns)}")
    sys.exit(1)

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["city", "date"]).reset_index(drop=True)

OUTPUT_DIR = "weather_report_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ------------------------------------------------------------------
# 2. Average temperature per city
# ------------------------------------------------------------------
avg_temp_per_city = df.groupby("city")["temperature"].mean().sort_values(ascending=False)

# ------------------------------------------------------------------
# 3. Hottest & coldest city
# ------------------------------------------------------------------
hottest_city = avg_temp_per_city.idxmax()
hottest_temp = avg_temp_per_city.max()
coldest_city = avg_temp_per_city.idxmin()
coldest_temp = avg_temp_per_city.min()

# ------------------------------------------------------------------
# 4. Rainy / sunny day counts
# ------------------------------------------------------------------
cond_lower = df["condition"].astype(str).str.lower()
is_rainy = cond_lower.str.contains("rain")
is_sunny = cond_lower.str.contains("sun|clear")

rainy_days = int(is_rainy.sum())
sunny_days = int(is_sunny.sum())
other_days = int(len(df) - rainy_days - sunny_days)

condition_counts = df["condition"].value_counts()

# ------------------------------------------------------------------
# 5. Charts
# ------------------------------------------------------------------
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

# --- 5a. Temperature Trend (line chart per city) ---
plt.figure(figsize=(10, 6))
for city, group in df.groupby("city"):
    plt.plot(group["date"], group["temperature"], marker="o", markersize=3, label=city)
plt.title("Temperature Trend Over Time")
plt.xlabel("Date")
plt.ylabel("Temperature (°C)")
plt.legend(title="City", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.xticks(rotation=45)
plt.tight_layout()
trend_path = os.path.join(OUTPUT_DIR, "temperature_trend.png")
plt.savefig(trend_path, dpi=150)
plt.close()

# --- 5b. Weather Distribution (pie chart) ---
plt.figure(figsize=(7, 7))
condition_counts.plot.pie(autopct="%1.1f%%", startangle=90, ylabel="")
plt.title("Weather Condition Distribution")
plt.tight_layout()
dist_path = os.path.join(OUTPUT_DIR, "weather_distribution.png")
plt.savefig(dist_path, dpi=150)
plt.close()

# --- 5c. Average Temperature per City (bar chart) ---
plt.figure(figsize=(9, 6))
bars = plt.bar(avg_temp_per_city.index, avg_temp_per_city.values, color="tomato")
plt.title("Average Temperature per City")
plt.xlabel("City")
plt.ylabel("Avg Temperature (°C)")
plt.xticks(rotation=30)
for bar, val in zip(bars, avg_temp_per_city.values):
    plt.text(bar.get_x() + bar.get_width() / 2, val, f"{val:.1f}°C",
              ha="center", va="bottom", fontsize=9)
plt.tight_layout()
avg_path = os.path.join(OUTPUT_DIR, "avg_temperature_per_city.png")
plt.savefig(avg_path, dpi=150)
plt.close()

print("Charts saved to:", OUTPUT_DIR)

# ------------------------------------------------------------------
# 6. Bonus: predict tomorrow's temperature using moving average
# ------------------------------------------------------------------
WINDOW = 3  # 3-day moving average
predictions = {}
for city, group in df.groupby("city"):
    group = group.sort_values("date")
    last_n = group["temperature"].tail(WINDOW)
    predictions[city] = round(last_n.mean(), 2)

# ------------------------------------------------------------------
# 7. Export final report (text file)
# ------------------------------------------------------------------
report_path = os.path.join(OUTPUT_DIR, "weather_report.txt")
with open(report_path, "w", encoding="utf-8") as f:
    f.write("=" * 55 + "\n")
    f.write("            WEATHER DATA ANALYSIS REPORT\n")
    f.write("=" * 55 + "\n\n")

    f.write(f"Data source: {CSV_PATH}\n")
    f.write(f"Total records: {len(df)}\n")
    f.write(f"Cities covered: {', '.join(sorted(df['city'].unique()))}\n")
    f.write(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}\n\n")

    f.write("-" * 55 + "\n")
    f.write("AVERAGE TEMPERATURE PER CITY\n")
    f.write("-" * 55 + "\n")
    for city, temp in avg_temp_per_city.items():
        f.write(f"  {city:<15} {temp:6.2f} °C\n")
    f.write("\n")

    f.write("-" * 55 + "\n")
    f.write("HOTTEST & COLDEST CITY\n")
    f.write("-" * 55 + "\n")
    f.write(f"   Hottest: {hottest_city} ({hottest_temp:.2f} °C)\n")
    f.write(f"   Coldest: {coldest_city} ({coldest_temp:.2f} °C)\n\n")

    f.write("-" * 55 + "\n")
    f.write("WEATHER CONDITION COUNTS\n")
    f.write("-" * 55 + "\n")
    f.write(f"  Rainy days: {rainy_days}\n")
    f.write(f"  Sunny days: {sunny_days}\n")
    f.write(f"  Other:      {other_days}\n\n")
    for cond, count in condition_counts.items():
        f.write(f"    {cond:<15} {count}\n")
    f.write("\n")

    f.write("-" * 55 + "\n")
    f.write(f"BONUS: TOMORROW'S TEMPERATURE PREDICTION ({WINDOW}-day moving avg)\n")
    f.write("-" * 55 + "\n")
    for city, pred in predictions.items():
        f.write(f"  {city:<15} predicted ≈ {pred:6.2f} °C\n")
    f.write("\n")

    f.write("-" * 55 + "\n")
    f.write("CHARTS GENERATED\n")
    f.write("-" * 55 + "\n")
    f.write(f"  {trend_path}\n  {dist_path}\n  {avg_path}\n")

print("Report saved to:", report_path)

# ------------------------------------------------------------------
# 8. Console summary
# ------------------------------------------------------------------
print("\n=== SUMMARY ===")
print(avg_temp_per_city.round(2))
print(f"\nHottest city: {hottest_city} ({hottest_temp:.2f} °C)")
print(f"Coldest city: {coldest_city} ({coldest_temp:.2f} °C)")
print(f"Rainy days: {rainy_days} | Sunny days: {sunny_days} | Other: {other_days}")
print("\nTomorrow's predicted temperature (moving average):")
for city, pred in predictions.items():
    print(f"  {city}: {pred} °C")


import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

st.set_page_config(page_title=" Weather Dashboard", layout="wide")

st.title(" Interactive Weather Data Dashboard")
st.caption("Temperature trends, weather distribution, and next-day prediction")

# ------------------------------------------------------------------
# Load data
# ------------------------------------------------------------------
st.sidebar.header("Data")
uploaded = st.sidebar.file_uploader("Upload a weather CSV", type="csv")

DEFAULT_PATH = "weather_data.csv"

if uploaded is not None:
    df = pd.read_csv(uploaded)
elif os.path.exists(DEFAULT_PATH):
    df = pd.read_csv(DEFAULT_PATH)
else:
    st.warning("No data found. Upload a CSV or run generate_sample_data.py first.")
    st.stop()

df.columns = [c.strip().lower() for c in df.columns]
required = {"date", "city", "temperature", "condition"}
missing = required - set(df.columns)
if missing:
    st.error(f"CSV is missing required columns: {missing}")
    st.stop()

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["city", "date"])

# ------------------------------------------------------------------
# Sidebar filters
# ------------------------------------------------------------------
st.sidebar.header("Filters")
all_cities = sorted(df["city"].unique())
selected_cities = st.sidebar.multiselect("Cities", all_cities, default=all_cities)

date_min, date_max = df["date"].min(), df["date"].max()
date_range = st.sidebar.date_input("Date range", (date_min, date_max))

window = st.sidebar.slider("Moving average window (days) for prediction", 2, 7, 3)

filtered = df[df["city"].isin(selected_cities)]
if len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = filtered[(filtered["date"] >= start) & (filtered["date"] <= end)]

if filtered.empty:
    st.warning("No data for the selected filters.")
    st.stop()

# ------------------------------------------------------------------
# Key metrics
# ------------------------------------------------------------------
avg_temp_per_city = filtered.groupby("city")["temperature"].mean().sort_values(ascending=False)
hottest_city, hottest_temp = avg_temp_per_city.idxmax(), avg_temp_per_city.max()
coldest_city, coldest_temp = avg_temp_per_city.idxmin(), avg_temp_per_city.min()

cond_lower = filtered["condition"].astype(str).str.lower()
rainy_days = int(cond_lower.str.contains("rain").sum())
sunny_days = int(cond_lower.str.contains("sun|clear").sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric(" Hottest City", hottest_city, f"{hottest_temp:.1f} °C")
c2.metric(" Coldest City", coldest_city, f"{coldest_temp:.1f} °C")
c3.metric(" Rainy Days", rainy_days)
c4.metric(" Sunny Days", sunny_days)

st.divider()

# ------------------------------------------------------------------
# Charts
# ------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    " Temperature Trend", " Weather Distribution",
    "Avg Temp per City", " Prediction"
])

with tab1:
    fig = px.line(filtered, x="date", y="temperature", color="city", markers=True,
                   title="Temperature Trend Over Time")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    condition_counts = filtered["condition"].value_counts().reset_index()
    condition_counts.columns = ["condition", "count"]
    fig = px.pie(condition_counts, names="condition", values="count",
                 title="Weather Condition Distribution")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    fig = px.bar(avg_temp_per_city.reset_index(), x="city", y="temperature",
                 title="Average Temperature per City", text_auto=".1f",
                 color="temperature", color_continuous_scale="OrRd")
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader(f"Tomorrow's Predicted Temperature ({window}-day moving average)")
    preds = []
    for city, group in filtered.groupby("city"):
        group = group.sort_values("date")
        pred = group["temperature"].tail(window).mean()
        preds.append({"city": city, "predicted_temp": round(pred, 2)})
    pred_df = pd.DataFrame(preds).sort_values("predicted_temp", ascending=False)
    st.dataframe(pred_df, use_container_width=True, hide_index=True)
    fig = px.bar(pred_df, x="city", y="predicted_temp", text_auto=".1f",
                 title="Predicted Temperature for Tomorrow")
    st.plotly_chart(fig, use_container_width=True)

st.divider()
with st.expander(" View raw data"):
    st.dataframe(filtered, use_container_width=True)


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
