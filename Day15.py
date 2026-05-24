
#Day 15 - Project 15: Mini EDA Dashboard (Combined)


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D

# ─────────────────────────────────────────────
# 1. CREATE DATASET — Monthly Sales Data
# ─────────────────────────────────────────────

np.random.seed(42)

months      = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
sales       = [12000, 15000, 13500, 17000, 16000, 21000,
               19500, 22000, 18000, 25000, 27000, 31000]
units_sold  = [120, 145, 130, 165, 155, 200,
               188, 210, 172, 240, 258, 295]

# Add some noise + one outlier for visual detection
sales[4]    = 8000    # May outlier (sudden dip)
units_sold[4] = 75

df = pd.DataFrame({
    "Month":      months,
    "Sales":      sales,
    "Units":      units_sold,
    "Avg_Price":  [round(s / u, 2) for s, u in zip(sales, units_sold)],
})

# ─────────────────────────────────────────────
# 2. OUTLIER DETECTION (IQR method)
# ─────────────────────────────────────────────

def get_outlier_mask(series):
    Q1, Q3 = series.quantile(0.25), series.quantile(0.75)
    IQR    = Q3 - Q1
    return (series < Q1 - 1.5 * IQR) | (series > Q3 + 1.5 * IQR)

sales_outliers = get_outlier_mask(df["Sales"])
units_outliers = get_outlier_mask(df["Units"])

# ─────────────────────────────────────────────
# 3. FIGURE & GRIDSPEC LAYOUT
# ─────────────────────────────────────────────

fig = plt.figure(figsize=(16, 12), facecolor="#F0F2F5")
fig.suptitle(
    "Day 15 — Mini EDA Dashboard  |  Monthly Sales Analysis",
    fontsize=17, fontweight="bold", color="#1A1A2E", y=0.98
)

gs = gridspec.GridSpec(
    3, 2,
    figure=fig,
    hspace=0.45,
    wspace=0.35,
    left=0.07, right=0.97,
    top=0.93, bottom=0.06,
)

GRID_COLOR  = "#D0D3DA"
ACCENT      = "#E74C3C"
PRIMARY     = "#3498DB"
SUCCESS     = "#2ECC71"
WARN        = "#F39C12"
TEXT_DARK   = "#1A1A2E"

# ─────────────────────────────────────────────
# 4. PLOT 1 — LINE CHART (Sales Trend)
# ─────────────────────────────────────────────

ax1 = fig.add_subplot(gs[0, :])   # Full-width top row
ax1.set_facecolor("#FFFFFF")

ax1.plot(df["Month"], df["Sales"], color=PRIMARY, linewidth=2.5,
         marker="o", markersize=7, zorder=3, label="Monthly Sales")

# Shade area under line
ax1.fill_between(range(len(months)), df["Sales"],
                 alpha=0.12, color=PRIMARY)

# Highlight outliers on line chart
for i, is_out in enumerate(sales_outliers):
    if is_out:
        ax1.scatter(df["Month"][i], df["Sales"][i],
                    color=ACCENT, s=140, zorder=5,
                    label="Outlier detected")
        ax1.annotate(
            f"Outlier: {df['Sales'][i]:,}",
            xy=(df["Month"][i], df["Sales"][i]),
            xytext=(i + 0.4, df["Sales"][i] + 1200),
            fontsize=9, color=ACCENT, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.4),
        )

# Trend line (linear regression)
x_num  = np.arange(len(months))
z      = np.polyfit(x_num, df["Sales"], 1)
p      = np.poly1d(z)
ax1.plot(df["Month"], p(x_num), "--", color=WARN,
         linewidth=1.8, label=f"Trend (slope: +{z[0]:,.0f}/month)")

ax1.set_title("Sales Trend Over the Year (Line Chart)", fontsize=13,
              fontweight="bold", color=TEXT_DARK, pad=8)
ax1.set_ylabel("Sales (INR)", fontsize=10, color=TEXT_DARK)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/1000:.0f}K"))
ax1.grid(axis="y", color=GRID_COLOR, linestyle="--", alpha=0.7)
ax1.spines[["top", "right"]].set_visible(False)
ax1.legend(fontsize=9, loc="upper left")
ax1.tick_params(colors=TEXT_DARK, labelsize=10)

# ─────────────────────────────────────────────
# 5. PLOT 2 — BAR CHART (Units Sold Comparison)
# ─────────────────────────────────────────────

ax2 = fig.add_subplot(gs[1, 0])
ax2.set_facecolor("#FFFFFF")

bar_colors = [ACCENT if units_outliers[i] else SUCCESS
              for i in range(len(months))]

bars = ax2.bar(df["Month"], df["Units"], color=bar_colors,
               edgecolor="white", linewidth=0.8, width=0.65)

# Label bars
for bar, val in zip(bars, df["Units"]):
    ax2.text(bar.get_x() + bar.get_width() / 2,
             bar.get_height() + 3,
             str(val), ha="center", va="bottom",
             fontsize=7.5, color=TEXT_DARK, fontweight="bold")

ax2.set_title("Units Sold per Month (Bar Chart)", fontsize=12,
              fontweight="bold", color=TEXT_DARK, pad=8)
ax2.set_ylabel("Units Sold", fontsize=10, color=TEXT_DARK)
ax2.set_ylim(0, max(df["Units"]) * 1.18)
ax2.grid(axis="y", color=GRID_COLOR, linestyle="--", alpha=0.7)
ax2.spines[["top", "right"]].set_visible(False)
ax2.tick_params(axis="x", rotation=45, labelsize=8, colors=TEXT_DARK)
ax2.tick_params(axis="y", colors=TEXT_DARK)

legend_elements = [
    Line2D([0], [0], marker="s", color="w", markerfacecolor=SUCCESS,
           markersize=10, label="Normal"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor=ACCENT,
           markersize=10, label="Outlier"),
]
ax2.legend(handles=legend_elements, fontsize=8)

# ─────────────────────────────────────────────
# 6. PLOT 3 — HISTOGRAM (Sales Distribution)
# ─────────────────────────────────────────────

ax3 = fig.add_subplot(gs[1, 1])
ax3.set_facecolor("#FFFFFF")

n, bins, patches = ax3.hist(df["Sales"], bins=8,
                             color="#9B59B6", edgecolor="white",
                             linewidth=0.8, alpha=0.85)

# Color outlier bins differently
outlier_threshold_low = df["Sales"].quantile(0.25) - 1.5 * (
    df["Sales"].quantile(0.75) - df["Sales"].quantile(0.25))
for patch, left in zip(patches, bins[:-1]):
    if left < outlier_threshold_low:
        patch.set_facecolor(ACCENT)
        patch.set_alpha(0.9)

# Mean & median lines
ax3.axvline(df["Sales"].mean(),   color=PRIMARY,  linestyle="--",
            linewidth=2, label=f"Mean  = {df['Sales'].mean():,.0f}")
ax3.axvline(df["Sales"].median(), color=SUCCESS, linestyle=":",
            linewidth=2, label=f"Median = {df['Sales'].median():,.0f}")

ax3.set_title("Sales Distribution (Histogram)", fontsize=12,
              fontweight="bold", color=TEXT_DARK, pad=8)
ax3.set_xlabel("Sales (INR)", fontsize=10, color=TEXT_DARK)
ax3.set_ylabel("Frequency", fontsize=10, color=TEXT_DARK)
ax3.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/1000:.0f}K"))
ax3.grid(axis="y", color=GRID_COLOR, linestyle="--", alpha=0.7)
ax3.spines[["top", "right"]].set_visible(False)
ax3.legend(fontsize=8)
ax3.tick_params(colors=TEXT_DARK, labelsize=9)

# ─────────────────────────────────────────────
# 7. PLOT 4 — BOX PLOT (Outlier Visual — Bonus)
# ─────────────────────────────────────────────

ax4 = fig.add_subplot(gs[2, 0])
ax4.set_facecolor("#FFFFFF")

bp = ax4.boxplot(
    [df["Sales"], df["Units"] * 100],    # Scale units for same axis
    patch_artist=True,
    notch=False,
    labels=["Sales (INR)", "Units x100"],
    medianprops=dict(color=ACCENT, linewidth=2.5),
    whiskerprops=dict(color=TEXT_DARK, linewidth=1.5),
    capprops=dict(color=TEXT_DARK, linewidth=1.5),
    flierprops=dict(marker="o", color=ACCENT, markersize=8,
                    markerfacecolor=ACCENT, alpha=0.8),
)

box_colors = [PRIMARY, SUCCESS]
for patch, color in zip(bp["boxes"], box_colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.5)

ax4.set_title("Outlier Detection (Box Plot — Bonus)", fontsize=12,
              fontweight="bold", color=TEXT_DARK, pad=8)
ax4.set_ylabel("Value", fontsize=10, color=TEXT_DARK)
ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax4.grid(axis="y", color=GRID_COLOR, linestyle="--", alpha=0.7)
ax4.spines[["top", "right"]].set_visible(False)
ax4.tick_params(colors=TEXT_DARK, labelsize=10)

# ─────────────────────────────────────────────
# 8. PLOT 5 — INSIGHTS TEXT PANEL
# ─────────────────────────────────────────────

ax5 = fig.add_subplot(gs[2, 1])
ax5.set_facecolor("#1A1A2E")
ax5.axis("off")

insights = [
    "INSIGHTS & PATTERNS",
    "",
    "1. Strong upward sales trend across the year.",
    "   Slope: ~+{:.0f} INR/month.".format(z[0]),
    "",
    "2. May shows a clear outlier (dip to 8,000)",
    "   — possible data error or seasonal drop.",
    "",
    "3. Q4 (Oct-Dec) is the strongest quarter.",
    "   Dec sales peak at 31,000 INR.",
    "",
    "4. Sales distribution is right-skewed.",
    "   Mean ({:,.0f}) > Median ({:,.0f}).".format(
        df["Sales"].mean(), df["Sales"].median()),
    "",
    "5. Units sold follow the same trend,",
    "   confirming volume drives revenue.",
]

y_pos = 0.97
for line in insights:
    style  = "bold" if line == "INSIGHTS & PATTERNS" else "normal"
    size   = 11     if line == "INSIGHTS & PATTERNS" else 8.5
    color  = WARN   if line == "INSIGHTS & PATTERNS" else "#ECF0F1"
    ax5.text(0.05, y_pos, line, transform=ax5.transAxes,
             fontsize=size, color=color, fontweight=style,
             va="top", fontfamily="monospace")
    y_pos -= 0.062

# ─────────────────────────────────────────────
# 9. SAVE & SHOW
# ─────────────────────────────────────────────

plt.savefig("eda_dashboard.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.show()
print("Plot saved as eda_dashboard.png")

# ─────────────────────────────────────────────
# 10. CONSOLE SUMMARY
# ─────────────────────────────────────────────

print("\n" + "="*50)
print("         EDA DASHBOARD — DATA SUMMARY")
print("="*50)
print(df.to_string(index=False))
print("-"*50)
print(f"  Sales   — Mean: {df['Sales'].mean():>8,.0f}  |  Std: {df['Sales'].std():>8,.0f}")
print(f"  Units   — Mean: {df['Units'].mean():>8,.1f}  |  Std: {df['Units'].std():>8,.1f}")
print(f"  Outliers found in Sales : {sales_outliers.sum()} month(s)")
print(f"  Outliers found in Units : {units_outliers.sum()} month(s)")
print("="*50)