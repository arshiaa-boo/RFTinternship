
#Day 16 | Project 16: Complete Sales Data EDA


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────
# 1. GENERATE SAMPLE SALES DATASET
# ─────────────────────────────────────────
np.random.seed(42)

products = ["Laptop", "Phone", "Tablet", "Headphones", "Monitor", "Keyboard", "Mouse"]
regions  = ["North", "South", "East", "West"]

n = 300
dates = [datetime(2024, 1, 1) + timedelta(days=np.random.randint(0, 365))
         for _ in range(n)]

data = {
    "Date":    dates,
    "Product": np.random.choice(products, n),
    "Region":  np.random.choice(regions, n),
    "Sales":   np.random.randint(500, 10000, n).astype(float),
}

# Inject missing values (~5 %)
for col in ["Product", "Sales"]:
    idx = np.random.choice(n, size=15, replace=False)
    data[col] = pd.array(data[col])          # make mutable
    for i in idx:
        data[col][i] = np.nan

df = pd.DataFrame(data)
df["Date"] = pd.to_datetime(df["Date"])

print("=" * 55)
print("  GOW AI ACADEMY | Day 16 — Sales Data EDA")
print("=" * 55)

# ─────────────────────────────────────────
# 2. DATA CLEANING — Handle Missing Values
# ─────────────────────────────────────────
print("\nSTEP 1: RAW DATASET INFO")
print(f"   Shape  : {df.shape[0]} rows × {df.shape[1]} columns")
print(f"   Missing:\n{df.isnull().sum().to_string()}")

# Fill missing Sales with column median
df["Sales"].fillna(df["Sales"].median(), inplace=True)

# Fill missing Product with mode
df["Product"].fillna(df["Product"].mode()[0], inplace=True)

# Drop any remaining nulls (safety net)
df.dropna(inplace=True)
df.reset_index(drop=True, inplace=True)

print(f"\nAfter cleaning — missing values: {df.isnull().sum().sum()}")
print(f"   Final shape: {df.shape[0]} rows × {df.shape[1]} columns")

# ─────────────────────────────────────────
# 3. AGGREGATION
# ─────────────────────────────────────────
print("\nSTEP 2: AGGREGATION")

# 3a. Total Sales per Product
product_sales = (df.groupby("Product")["Sales"]
                   .sum()
                   .sort_values(ascending=False)
                   .reset_index())
product_sales.columns = ["Product", "Total_Sales"]
print("\n  Total Sales per Product:")
print(product_sales.to_string(index=False))

# 3b. Region-wise Performance
region_sales = (df.groupby("Region")["Sales"]
                  .agg(Total="sum", Average="mean", Count="count")
                  .sort_values("Total", ascending=False)
                  .reset_index())
print("\n  Region-wise Performance:")
print(region_sales.to_string(index=False))

# 3c. Monthly Sales (for trend chart)
df["Month"] = df["Date"].dt.to_period("M")
monthly_sales = (df.groupby("Month")["Sales"]
                   .sum()
                   .reset_index())
monthly_sales["Month_dt"] = monthly_sales["Month"].dt.to_timestamp()

# 3d. Monthly Growth (BONUS)
monthly_sales["Growth_%"] = monthly_sales["Sales"].pct_change() * 100
print("\n  Monthly Sales & Growth:")
print(monthly_sales[["Month", "Sales", "Growth_%"]].to_string(index=False))

# ─────────────────────────────────────────
# 4. VISUALIZATION
# ─────────────────────────────────────────
print("\nSTEP 3: GENERATING CHARTS ...")

PALETTE = ["#2563EB", "#7C3AED", "#DB2777", "#D97706", "#059669",
           "#DC2626", "#0891B2"]
BG      = "#0F172A"
TEXT    = "#F1F5F9"
ACCENT  = "#38BDF8"

fig = plt.figure(figsize=(18, 14), facecolor=BG)
fig.suptitle("Sales Data EDA  •  GOW AI Academy — Day 16",
             fontsize=17, color=ACCENT, fontweight="bold", y=0.98)

axes_positions = [
    (2, 2, 1),   # Line Chart — Sales Trend
    (2, 2, 2),   # Bar Chart  — Top Products
    (2, 2, 3),   # Bar Chart  — Region Performance
    (2, 2, 4),   # Bar Chart  — Monthly Growth
]

# ── 4a. Sales Trends — Line Chart ──────────────────────────────
ax1 = fig.add_subplot(*axes_positions[0])
ax1.set_facecolor(BG)
ax1.plot(monthly_sales["Month_dt"], monthly_sales["Sales"],
         color=ACCENT, linewidth=2.5, marker="o", markersize=5,
         markerfacecolor=PALETTE[2])
ax1.fill_between(monthly_sales["Month_dt"], monthly_sales["Sales"],
                 alpha=0.15, color=ACCENT)
ax1.set_title("Monthly Sales Trend", color=TEXT, fontsize=13, pad=10)
ax1.set_xlabel("Month", color=TEXT, fontsize=10)
ax1.set_ylabel("Total Sales (₹)", color=TEXT, fontsize=10)
ax1.tick_params(colors=TEXT, labelsize=8)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f"Rs.{x/1_000:.0f}K"))
for spine in ax1.spines.values():
    spine.set_edgecolor("#334155")
ax1.grid(axis="y", color="#1E293B", linewidth=0.8)
fig.autofmt_xdate()

# ── 4b. Top Products — Bar Chart ───────────────────────────────
ax2 = fig.add_subplot(*axes_positions[1])
ax2.set_facecolor(BG)
bars = ax2.barh(product_sales["Product"], product_sales["Total_Sales"],
                color=PALETTE[:len(product_sales)], edgecolor="none",
                height=0.6)
ax2.set_title("Top Products by Sales", color=TEXT, fontsize=13, pad=10)
ax2.set_xlabel("Total Sales (₹)", color=TEXT, fontsize=10)
ax2.tick_params(colors=TEXT, labelsize=9)
ax2.xaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f"Rs.{x/1_000:.0f}K"))
for spine in ax2.spines.values():
    spine.set_edgecolor("#334155")
ax2.grid(axis="x", color="#1E293B", linewidth=0.8)
# Value labels
for bar in bars:
    w = bar.get_width()
    ax2.text(w + 100, bar.get_y() + bar.get_height() / 2,
             f"Rs.{w/1_000:.1f}K", va="center", color=TEXT, fontsize=8)

# ── 4c. Region-wise Performance ─────────────────────────────────
ax3 = fig.add_subplot(*axes_positions[2])
ax3.set_facecolor(BG)
colors_r = [PALETTE[i] for i in range(len(region_sales))]
bars3 = ax3.bar(region_sales["Region"], region_sales["Total"],
                color=colors_r, edgecolor="none", width=0.55)
ax3.set_title("Region-wise Total Sales", color=TEXT, fontsize=13, pad=10)
ax3.set_ylabel("Total Sales (₹)", color=TEXT, fontsize=10)
ax3.tick_params(colors=TEXT, labelsize=10)
ax3.yaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f"Rs.{x/1_000:.0f}K"))
for spine in ax3.spines.values():
    spine.set_edgecolor("#334155")
ax3.grid(axis="y", color="#1E293B", linewidth=0.8)
for bar in bars3:
    h = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width() / 2, h + 200,
             f"Rs.{h/1_000:.1f}K", ha="center", color=TEXT, fontsize=9)

# ── 4d. Monthly Growth % — BONUS ────────────────────────────────
ax4 = fig.add_subplot(*axes_positions[3])
ax4.set_facecolor(BG)
growth = monthly_sales.dropna(subset=["Growth_%"])
bar_colors = [PALETTE[4] if g >= 0 else PALETTE[6]
              for g in growth["Growth_%"]]
ax4.bar(growth["Month_dt"], growth["Growth_%"],
        color=bar_colors, edgecolor="none", width=20)
ax4.axhline(0, color="#475569", linewidth=1)
ax4.set_title("Monthly Growth % (BONUS)", color=TEXT, fontsize=13, pad=10)
ax4.set_ylabel("Growth (%)", color=TEXT, fontsize=10)
ax4.tick_params(colors=TEXT, labelsize=8)
for spine in ax4.spines.values():
    spine.set_edgecolor("#334155")
ax4.grid(axis="y", color="#1E293B", linewidth=0.8)
fig.autofmt_xdate()

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("sales_eda_charts.png", dpi=150, bbox_inches="tight",
            facecolor=BG)
plt.show()
print("   Charts saved as 'sales_eda_charts.png'")

# ─────────────────────────────────────────
# 5. KEY INSIGHTS
# ─────────────────────────────────────────
print("\n" + "=" * 55)
print("  KEY INSIGHTS")
print("=" * 55)

top_product  = product_sales.iloc[0]
low_product  = product_sales.iloc[-1]
best_region  = region_sales.iloc[0]
worst_region = region_sales.iloc[-1]
best_month   = monthly_sales.loc[monthly_sales["Sales"].idxmax()]
avg_growth   = monthly_sales["Growth_%"].mean()

insights = [
    f"1. Top product is '{top_product['Product']}' with Rs."
    f"{top_product['Total_Sales']:,.0f} in total sales.",

    f"2. Lowest selling product is '{low_product['Product']}' "
    f"(Rs.{low_product['Total_Sales']:,.0f}) — needs a marketing push.",

    f"3. Best performing region is '{best_region['Region']}' "
    f"with Rs.{best_region['Total']:,.0f} in sales "
    f"({best_region['Count']} transactions).",

    f"4. Peak sales month was {best_month['Month']} "
    f"with Rs.{best_month['Sales']:,.0f} revenue.",

    f"5. Average month-over-month growth: {avg_growth:.1f}% — "
    + ("positive trend overall!" if avg_growth > 0
       else "declining trend — review strategy."),

    # BONUS
    f"6. [BONUS] Best region '{best_region['Region']}' averages "
    f"Rs.{best_region['Average']:,.0f} per transaction vs "
    f"Rs.{worst_region['Average']:,.0f} for '{worst_region['Region']}'.",
]

for insight in insights:
    print(f"  {insight}")

print("\n" + "=" * 55)
print("  EDA Complete! Charts + 6 Key Insights generated.")
print("=" * 55)