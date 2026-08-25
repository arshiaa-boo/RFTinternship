"""
SALES DATA ANALYSIS
--------------------
Reads a CSV, cleans it, calculates key metrics, finds top customers,
generates Line/Bar/Pie charts, and prints business insights.

Expected CSV columns (rename in the CONFIG section below if yours differ):
    Date, Customer, Product, Category, Quantity, Price, Revenue
"""

import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------------------
# CONFIG — change these to match your actual CSV's column names
# ------------------------------------------------------------------
CSV_PATH = "sales_data.csv"
COL_DATE = "Date"
COL_CUSTOMER = "Customer"
COL_PRODUCT = "Product"
COL_CATEGORY = "Category"
COL_REVENUE = "Revenue"

OUTPUT_DIR = "."  # where chart images get saved

# ------------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------------
df = pd.read_csv(CSV_PATH)
print(f"Raw data shape: {df.shape}")

# ------------------------------------------------------------------
# 2. CLEAN DATA — missing values & duplicates
# ------------------------------------------------------------------
before = len(df)
df = df.drop_duplicates()
print(f"Removed {before - len(df)} duplicate rows")

# Drop rows with missing customer name (can't attribute the sale)
df = df.dropna(subset=[COL_CUSTOMER])

# Fill missing revenue with the column's median (safer than mean for skewed data)
missing_revenue = df[COL_REVENUE].isna().sum()
df[COL_REVENUE] = df[COL_REVENUE].fillna(df[COL_REVENUE].median())
print(f"Filled {missing_revenue} missing revenue values with median")

# Ensure correct data types
df[COL_DATE] = pd.to_datetime(df[COL_DATE])
df[COL_REVENUE] = pd.to_numeric(df[COL_REVENUE], errors="coerce")

print(f"Clean data shape: {df.shape}")

# ------------------------------------------------------------------
# 3. TOTAL SALES & AVERAGE REVENUE
# ------------------------------------------------------------------
total_sales = df[COL_REVENUE].sum()
average_revenue = df[COL_REVENUE].mean()

print(f"\nTotal Sales: ${total_sales:,.2f}")
print(f"Average Revenue per Transaction: ${average_revenue:,.2f}")

# ------------------------------------------------------------------
# 4. TOP 5 CUSTOMERS
# ------------------------------------------------------------------
top_customers = (
    df.groupby(COL_CUSTOMER)[COL_REVENUE]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)
print("\nTop 5 Customers by Revenue:")
print(top_customers.to_string())

# ------------------------------------------------------------------
# 5. CHARTS
# ------------------------------------------------------------------

# --- 5a. LINE CHART: Sales Trend over time (monthly) ---
monthly_sales = df.set_index(COL_DATE).resample("ME")[COL_REVENUE].sum()

plt.figure(figsize=(10, 5))
plt.plot(monthly_sales.index, monthly_sales.values, marker="o", linewidth=2, color="#2563eb")
plt.title("Sales Trend Over Time", fontsize=14, fontweight="bold")
plt.xlabel("Month")
plt.ylabel("Revenue ($)")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/1_line_chart_sales_trend.png", dpi=150)
plt.close()

# --- 5b. BAR CHART: Top Products by revenue ---
top_products = (
    df.groupby(COL_PRODUCT)[COL_REVENUE]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)

plt.figure(figsize=(10, 5))
plt.bar(top_products.index, top_products.values, color="#f97316")
plt.title("Top 5 Products by Revenue", fontsize=14, fontweight="bold")
plt.xlabel("Product")
plt.ylabel("Revenue ($)")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/2_bar_chart_top_products.png", dpi=150)
plt.close()

# --- 5c. PIE CHART: Category distribution ---
category_sales = df.groupby(COL_CATEGORY)[COL_REVENUE].sum()

plt.figure(figsize=(7, 7))
plt.pie(
    category_sales.values,
    labels=category_sales.index,
    autopct="%1.1f%%",
    startangle=90,
    colors=["#2563eb", "#f97316", "#16a34a", "#dc2626", "#9333ea"]
)
plt.title("Revenue Distribution by Category", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/3_pie_chart_category_distribution.png", dpi=150)
plt.close()

print("\nCharts saved: line chart, bar chart, pie chart (as PNG files)")

# ------------------------------------------------------------------
# 6. BUSINESS INSIGHTS (auto-generated from the numbers above)
# ------------------------------------------------------------------
best_month = monthly_sales.idxmax().strftime("%B %Y")
worst_month = monthly_sales.idxmin().strftime("%B %Y")
top_product_name = top_products.index[0]
top_category_name = category_sales.idxmax()
top_category_pct = (category_sales.max() / category_sales.sum()) * 100
top_customer_name = top_customers.index[0]
top5_share = (top_customers.sum() / total_sales) * 100

insights = [
    f"1. {best_month} was the strongest month for sales, while {worst_month} was the weakest — "
    f"worth investigating what drove the difference (promotions, seasonality, etc.).",

    f"2. '{top_product_name}' is the best-selling product by revenue, making it a strong candidate "
    f"for continued marketing investment and stock prioritization.",

    f"3. The '{top_category_name}' category dominates revenue at {top_category_pct:.1f}% of total sales, "
    f"indicating the business is heavily reliant on this single category.",

    f"4. The top 5 customers together contribute {top5_share:.1f}% of total revenue, led by "
    f"'{top_customer_name}' — a loyalty or account-management program could help retain them.",

    f"5. Average revenue per transaction is ${average_revenue:,.2f}, which can serve as a benchmark "
    f"for evaluating whether future promotions increase or dilute basket size.",
]

print("\n" + "=" * 60)
print("BUSINESS INSIGHTS")
print("=" * 60)
for insight in insights:
    print(insight)
