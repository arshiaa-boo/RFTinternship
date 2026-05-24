import matplotlib.pyplot as plt

# --- Dataset ------------------------------------------------------------------
DATES = ["MON", "TUE", "WED", "THU", "FRI"]
SALES = [200, 250, 300, 280, 350]

# --- Find Highest and Lowest Day (BONUS) --------------------------------------
max_sales = max(SALES)
min_sales = min(SALES)
max_day   = DATES[SALES.index(max_sales)]
min_day   = DATES[SALES.index(min_sales)]

print("=" * 40)
print("     SALES TREND ANALYSIS")
print("=" * 40)
for day, sale in zip(DATES, SALES):
    tag = ""
    if sale == max_sales:
        tag = " <-- HIGHEST"
    elif sale == min_sales:
        tag = " <-- LOWEST"
    print(f"   {day} : {sale}{tag}")

print(f"\nHighest Sales Day : {max_day} ({max_sales})")
print(f"Lowest  Sales Day : {min_day} ({min_sales})")
print(f"Average Sales     : {sum(SALES)/len(SALES):.1f}")

# --- Plot ---------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))

# Main line
ax.plot(DATES, SALES,
        color='steelblue',
        linewidth=2.5,
        marker='o',
        markersize=7,
        label='Daily Sales')

# Highlight highest day (green)
ax.scatter(max_day, max_sales,
           color='green', s=150, zorder=5,
           label=f'Highest: {max_day} ({max_sales})')

# Highlight lowest day (red)
ax.scatter(min_day, min_sales,
           color='red', s=150, zorder=5,
           label=f'Lowest: {min_day} ({min_sales})')

# Annotate highest point
ax.annotate(f'HIGH\n{max_sales}',
            xy=(max_day, max_sales),
            xytext=(max_day, max_sales + 15),
            ha='center', fontsize=9,
            color='green', fontweight='bold')

# Annotate lowest point
ax.annotate(f'LOW\n{min_sales}',
            xy=(min_day, min_sales),
            xytext=(min_day, min_sales - 25),
            ha='center', fontsize=9,
            color='red', fontweight='bold')

# Average line
avg = sum(SALES) / len(SALES)
ax.axhline(y=avg, color='orange', linestyle='--',
           linewidth=1.5, label=f'Average: {avg:.1f}')

# Data value labels on each point
for day, sale in zip(DATES, SALES):
    ax.text(day, sale + 8, str(sale),
            ha='center', fontsize=9, color='steelblue')

# Labels, title, grid
ax.set_title('Weekly Sales Trend', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Day of the Week', fontsize=11)
ax.set_ylabel('Sales (units)', fontsize=11)
ax.set_ylim(150, 400)
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(loc='upper left', fontsize=9)

plt.tight_layout()
plt.savefig('sales_trend.png', dpi=150)
plt.show()

print("\nChart saved as: sales_trend.png")