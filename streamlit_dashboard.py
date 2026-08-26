

import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="🌤️ Weather Dashboard", layout="wide")

st.title("🌤️ Interactive Weather Data Dashboard")
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
c1.metric("🔥 Hottest City", hottest_city, f"{hottest_temp:.1f} °C")
c2.metric("❄️ Coldest City", coldest_city, f"{coldest_temp:.1f} °C")
c3.metric("🌧️ Rainy Days", rainy_days)
c4.metric("☀️ Sunny Days", sunny_days)

st.divider()

# ------------------------------------------------------------------
# Charts
# ------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🌡️ Temperature Trend", "🌧️ Weather Distribution",
    "📊 Avg Temp per City", "🔮 Prediction"
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
with st.expander("📄 View raw data"):
    st.dataframe(filtered, use_container_width=True)
